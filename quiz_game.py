
# 게임 전체를 관리하는 QuizGame 클래스.

import json
import os
import random
import sys
from datetime import datetime

from quiz import Quiz

# 상수

STATE_FILE    = "state.json"
HINT_PENALTY  = 10          # 힌트 사용 1회당 최종 점수 차감량
MAX_HISTORY   = 10          # 히스토리 최대 표시 개수

LINE_WIDE = "=" * 46
LINE_THIN = "-" * 46

# 기본 퀴즈 데이터 (한국 역사)
DEFAULT_QUIZZES: list[Quiz] = [
    Quiz("한글을 만든 조선의 왕은 누구인가요?",
         ["태조", "세종대왕", "태종", "영조"], 2,
         "백성이 글을 쉽게 읽고 쓸 수 있도록 문자를 만들었습니다."),
    Quiz("우리나라의 수도는 어디인가요?",
         ["부산", "인천", "서울", "대전"], 3,
         "조선 시대부터 지금까지 수도 역할을 하고 있는 도시입니다."),
    Quiz("대한민국의 국기는 무엇인가요?",
         ["성조기", "태극기", "유니언잭", "오성홍기"], 2,
         "흰 바탕에 빨강과 파랑, 그리고 네 개의 검은 괘가 있습니다."),
    Quiz("대한민국의 화폐 단위는 무엇인가요?",
         ["달러", "엔", "위안", "원"], 4,
         "지폐와 동전에 쓰이는 단위입니다."),
    Quiz("한반도에서 가장 높은 산으로 유명한 산은 무엇인가요?",
         ["지리산", "설악산", "북한산", "한라산"], 4,
         "제주도에 있는 산입니다."),
    Quiz("우리나라를 대표하는 글자는 무엇인가요?",
         ["가나", "한글", "한자", "로마자"], 2,
         "세종대왕이 만든 문자입니다."),
    Quiz("대한민국의 수도 서울에 있는 큰 강은 무엇인가요?",
         ["낙동강", "한강", "금강", "영산강"], 2,
         "서울을 가로질러 흐르는 강입니다."),
    Quiz("태극기 가운데 원은 몇 가지 색으로 이루어져 있나요?",
         ["1가지", "2가지", "3가지", "4가지"], 2,
         "빨간색과 파란색으로 이루어져 있습니다."),
    Quiz("대한민국의 국화로 알려진 꽃은 무엇인가요?",
         ["무궁화", "장미", "튤립", "해바라기"], 1,
         "애국가 가사에도 나오는 꽃입니다."),
    Quiz("제주도는 대한민국의 어느 쪽에 있나요?",
         ["북쪽", "동쪽", "남쪽", "서쪽"], 3,
         "한반도 아래쪽 바다에 있는 섬입니다."),
]

# 퀴즈 게임 전체를 관리하는 클래스
class QuizGame:
    def __init__(self) -> None:
        self.quizzes:    list[Quiz]  = []
        self.best_score: int         = 0
        self.history:    list[dict]  = []
        self._load_data()
    

    # 파일 저장/불러오기
    def _load_data(self) -> None:
        # state.json 을 읽어 quizzes / best_score / history 를 초기화한다.
        if not os.path.exists(STATE_FILE):
            self.quizzes = DEFAULT_QUIZZES[:]
            print("  📂 기본 퀴즈 데이터를 불러왔습니다.")
            return

        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            quizzes_data = data.get("quizzes", [])
            for quiz_data in quizzes_data:
                choices = quiz_data["choices"]
                if len(choices) != 4:
                    raise ValueError("모든 퀴즈의 choices 개수는 4개여야 합니다.")

            self.quizzes    = [Quiz.from_dict(q) for q in quizzes_data]
            self.best_score = data.get("best_score", 0)
            self.history    = data.get("history", [])
            print(f"  📂 저장된 데이터를 불러왔습니다."
                  f" (퀴즈 {len(self.quizzes)}개, 최고점수 {self.best_score}점)")
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"  ⚠️  데이터 파일이 손상되었습니다. 기본 데이터로 초기화합니다. ({e})")
            self.quizzes = DEFAULT_QUIZZES[:]
        except IOError as e:
            print(f"  ⚠️  파일을 읽을 수 없습니다. 기본 데이터를 사용합니다. ({e})")
            self.quizzes = DEFAULT_QUIZZES[:]

    def _save_data(self) -> None:
        #현재 상태를 state.json 에 저장한다.
        data = {
            "quizzes":    [q.to_dict() for q in self.quizzes],
            "best_score": self.best_score,
            "history":    self.history,
        }
        try:
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"  ⚠️  저장에 실패했습니다: {e}")

    # 입력 헬퍼
    def _input_int(self, prompt: str, min_val: int, max_val: int) -> int | None:
        # [min_val, max_val] 범위의 정수를 입력받는다. EOFError 시 None 반환. 빈 입력 / 문자 / 범위 초과에 대해 안내 메시지 후 재입력.
        while True:
            try:
                raw = input(prompt)
            except EOFError:
                return None

            raw = raw.strip()

            if not raw:
                print(f"입력이 없습니다. {min_val}~{max_val} 사이의 숫자를 입력하세요.")
                continue
            try:
                value = int(raw)
            except ValueError:
                print(f"숫자만 입력하세요. (입력값: {raw!r})")
                continue
            if not (min_val <= value <= max_val):
                print(f"{min_val}~{max_val} 사이의 숫자를 입력하세요.")
                continue

            return value

    def _input_str(self, prompt: str) -> str | None:
        # 비어 있지 않은 문자열을 입력받는다. EOFError 시 None 반환.
        while True:
            try:
                raw = input(prompt)
            except EOFError:
                return None

            raw = raw.strip()
            if not raw:
                print("  ⚠️  내용을 입력하세요.")
                continue
            return raw


    # 화면 출력
    def _show_menu(self) -> None:
        print(LINE_WIDE)
        print("         🎯  나만의 퀴즈 게임  🎯")
        print(LINE_WIDE)
        print("  1. 퀴즈 풀기")
        print("  2. 퀴즈 추가")
        print("  3. 퀴즈 목록")
        print("  4. 점수 확인")
        print("  5. 퀴즈 삭제")
        print("  6. 종료")
        print(LINE_WIDE)

    # 기능 1: 퀴즈 풀기
    def _play(self) -> None:
        total_available = len(self.quizzes)
        if total_available == 0:
            print("\n  퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요.")
            return

        # 문제 수 선택
        print(f"\n  총 {total_available}개의 퀴즈가 있습니다.")
        count = self._input_int(f"  몇 문제를 풀까요? (1~{total_available}): ",
                                1, total_available)
        if count is None:
            return

        # 랜덤 섞기
        quizzes = random.sample(self.quizzes, count)

        print(f"\n  퀴즈를 시작합니다! (총 {count}문제)")
        print(f"  ※ 풀이 중 H 를 입력하면 힌트를 볼 수 있습니다.")
        print(f"    (힌트 사용 후 맞혀도 {HINT_PENALTY}점이 차감됩니다.)")

        correct_count      = 0
        hint_correct_count = 0  # 힌트를 쓰고 맞힌 문제 수

        for i, quiz in enumerate(quizzes, 1):
            print(f"\n  {LINE_THIN}")
            quiz.display(i)
            hint_used = False

            # 답 입력 루프
            while True:
                try:
                    raw = input("\n  정답 입력 (H: 힌트): ").strip()
                except EOFError:
                    print("\n  입력이 종료되었습니다. 데이터를 저장합니다.")
                    self._save_data()
                    return

                # 힌트 요청
                if raw.upper() == "H":
                    if hint_used:
                        print("  이미 힌트를 사용했습니다.")
                    else:
                        quiz.show_hint()
                        hint_used = True
                    continue

                if not raw:
                    print("  ⚠️  1~4 중 숫자를 입력하세요.")
                    continue
                try:
                    answer = int(raw)
                except ValueError:
                    print("  ⚠️  숫자만 입력하세요.")
                    continue
                if not (1 <= answer <= 4):
                    print("  ⚠️  1~4 사이의 숫자를 입력하세요.")
                    continue
                break

            # 정답 판정
            if quiz.check_answer(answer):
                correct_count += 1
                if hint_used:
                    hint_correct_count += 1
                print("  정답입니다!")
            else:
                print(f"  오답입니다. 정답은 {quiz.answer}번입니다.")

        # 점수 계산
        base_score  = round(correct_count / count * 100)
        final_score = max(0, base_score - hint_correct_count * HINT_PENALTY)

        print(f"\n  {LINE_WIDE}")
        print(f"  🏆 결과: {count}문제 중 {correct_count}문제 정답!  ({final_score}점)")
        if hint_correct_count > 0:
            print(f"      (힌트 차감: -{hint_correct_count * HINT_PENALTY}점)")

        # 최고 점수 갱신
        if final_score > self.best_score:
            self.best_score = final_score
            print("  🎉 새로운 최고 점수입니다!")

        # 히스토리 기록 
        self.history.append({
            "date":    datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total":   count,
            "correct": correct_count,
            "score":   final_score,
        })
        print(f"  {LINE_WIDE}")

        self._save_data()

    # 기능 2: 퀴즈 추가
    def _add_quiz(self) -> None:
        print("\n  📌 새로운 퀴즈를 추가합니다.")
        print("  (취소하려면 'q' 를 입력하세요.)\n")

        question = self._input_str("  문제: ")
        if question is None or question.lower() == "q":
            print("  취소되었습니다.")
            return

        choices = []
        for i in range(1, 5):
            choice = self._input_str(f"  선택지 {i}: ")
            if choice is None or choice.lower() == "q":
                print("  취소되었습니다.")
                return
            choices.append(choice)

        answer = self._input_int("  정답 번호 (1~4): ", 1, 4)
        if answer is None:
            return

        hint = ""
        try:
            hint = input("  힌트 (없으면 Enter): ").strip()
        except EOFError:
            pass

        self.quizzes.append(Quiz(question, choices, answer, hint))
        self._save_data()
        print("\n  ✅ 퀴즈가 추가되었습니다!")



    # 기능 4: 점수 확인

    def _show_score(self) -> None:
        print()
        if not self.history:
            print("  아직 퀴즈를 풀지 않았습니다.")
            return

        best_rec = max(self.history, key=lambda r: r["score"])
        print(f"  🏆 최고 점수: {self.best_score}점"
              f"  ({best_rec['total']}문제 중 {best_rec['correct']}개 정답)")

        recent = self.history[-MAX_HISTORY:]
        print(f"\n  📊 최근 게임 기록 (총 {len(self.history)}회 중 최근 {len(recent)}회)")
        print("  " + "-" * 54)
        print(f"  {'번호':>3}  {'날짜':<16}  {'문제':>4}  {'정답':>4}  {'점수':>5}")
        print("  " + "-" * 54)
        for i, rec in enumerate(recent, 1):
            print(f"  {i:>3}.  {rec['date']:<16}  "
                  f"{rec['total']:>4}문제  {rec['correct']:>4}개  {rec['score']:>4}점")
        print("  " + "-" * 54)

    # 기능 5: 퀴즈 삭제 (보너스 5.4)
    def _delete_quiz(self) -> None:
        self._list_quizzes()
        if not self.quizzes:
            return

        total = len(self.quizzes)
        index = self._input_int(f"\n  삭제할 퀴즈 번호 (1~{total}, 취소: 0): ", 0, total)
        if index is None or index == 0:
            print("  취소되었습니다.")
            return

        removed = self.quizzes.pop(index - 1)
        self._save_data()
        print(f"\n  🗑️  삭제되었습니다: {removed.question}")

    # 메인 루프
    def run(self) -> None:
        #게임 메인 루프
        print()

        while True:
            self._show_menu()

            try:
                choice = self._input_int("  선택: ", 1, 6)
            except KeyboardInterrupt:
                self._safe_exit()
                return

            if choice is None:
                print("\n  입력 스트림이 종료되었습니다. 데이터를 저장하고 종료합니다.")
                self._save_data()
                return

            try:
                if   choice == 1: self._play()
                elif choice == 2: self._add_quiz()
                elif choice == 3: self._list_quizzes()
                elif choice == 4: self._show_score()
                elif choice == 5: self._delete_quiz()
                elif choice == 6:
                    print("\n  👋 프로그램을 종료합니다. 감사합니다!")
                    self._save_data()
                    return
            except KeyboardInterrupt:
                self._safe_exit()
                return

            print()  # 다음 메뉴 출력 전 여백

    def _safe_exit(self) -> None:
        #Ctrl+C 시 데이터를 저장하고 안전하게 종료한다.
        print("\n\n  프로그램이 중단되었습니다. 데이터를 저장합니다...")
        self._save_data()
        print("  저장 완료. 종료합니다.")
        sys.exit(0)
