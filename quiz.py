class Quiz:
    def __init__(
        self,
        question: str,
        choices: list[str],
        answer: int,
        hint: str = "",
    ) -> None:
        self.question = question
        self.choices  = choices
        self.answer   = answer
        self.hint     = hint

    # 출력

    def display(self, number: int) -> None:
        #문제 번호와 함께 퀴즈 전체를 출력한다.
        print(f"\n  [문제 {number}]")
        print(f"  {self.question}")
        print()
        for i, choice in enumerate(self.choices, 1):
            print(f"    {i}. {choice}")

    def show_hint(self) -> None:
        #힌트를 출력한다.
        if self.hint:
            print(f"\n  💡 힌트: {self.hint}")
        else:
            print("\n  💡 이 문제에는 힌트가 없습니다.")

    # 정답 확인
    def check_answer(self, user_answer: int) -> bool:
        return user_answer == self.answer

    #직렬화

    def to_dict(self) -> dict:
        return {
            "question": self.question,
            "choices":  self.choices,
            "answer":   self.answer,
            "hint":     self.hint,
        }


