from helpers import SKILLS

MSG = SKILLS / "academy-message"


def _text():
    return (MSG / "SKILL.md").read_text(encoding="utf-8")


def test_writes_only_the_claude_summary_property():
    text = _text()
    section = text.split("## 쓰는 속성", 1)[1].split("\n## ", 1)[0]
    assert "클로드총평" in section, "쓰는 속성 절에 `클로드총평` 이 없다"
    for old in ["클로드 문자", "클로드출결", "클로드시험", "클로드과제", "클로드다음과제"]:
        assert old not in text, f"academy-message 에 없어진 속성 `{old}` 이 남아 있다"


def test_has_no_alimtalk_mode_or_saved_formats():
    text = _text() + (MSG / "references" / "examples.md").read_text(encoding="utf-8")
    for old in ["알림톡 모드", "message_formats", "경로 2", "fixed_length", "oopy_domain", "은퇴한 발송 스킬"]:
        assert old not in text, f"academy-message 에 없어진 `{old}` 이 남아 있다"


def test_never_sends_and_points_at_core_rule():
    text = _text()
    assert "domain-rules.md" in text and "발송" in text, (
        "academy-message 가 발송 규칙을 core 로 가리키지 않는다"
    )


def test_warns_summary_must_precede_scheduled_send():
    text = _text()
    assert "발송 시각" in text or "보내기 전" in text, (
        "총평은 Make 의 정해진 발송 시각 전에 써야 실린다는 안내가 없다"
    )


def test_checks_template_actually_uses_the_variable():
    text = _text()
    assert "#{클로드총평}" in text, (
        "문자 양식에 #{클로드총평} 이 들어 있는지 확인하는 절차가 없다"
    )


def test_summary_is_grounded_in_read_data():
    text = _text()
    for src in ["출석부", "시험", "과제"]:
        assert src in text, f"총평의 근거로 `{src}` 를 읽는다는 절차가 없다"


def test_scores_are_compared_as_percent_of_total():
    text = _text()
    assert "총점" in text and "100" in text, (
        "총점이 시험마다 달라 백분율로 환산해야 한다는 규칙이 없다"
    )


def test_homework_grade_is_read_as_the_rows_own():
    text = _text()
    assert "과제 평가 대상" in text, "과제 평가를 그 행 자기 과제의 평가로 읽는다는 근거가 없다"
    assert "직전" not in text and "저번 과제" not in text, "옛 「직전 과제」 해석이 남아 있다"
