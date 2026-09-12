from helpers import SKILLS

HW = SKILLS / "academy-homework"


def _skill():
    return (HW / "SKILL.md").read_text(encoding="utf-8")


def _all():
    return "\n".join(p.read_text(encoding="utf-8") for p in HW.rglob("*.md"))


def test_no_master_table():
    assert "과제 M" not in _all(), "academy-homework 에 없어진 `과제 M` 이 남아 있다"


def test_title_is_filled_with_assignment_name():
    section = _skill().split("## 쓰는 속성", 1)[1].split("\n## ", 1)[0]
    assert "제목" in section and "과제 안내" in section, (
        "쓰는 속성 절이 제목(\"\")에 과제 이름을 넣는다고 적지 않는다"
    )


def test_grade_is_for_the_row_itself():
    text = _all()
    for old in ["저번 과제", "직전 과제", "가장 최근 행의", "저번과제"]:
        assert old not in text, f"없어진 「직전 과제 평가」 규칙 흔적 `{old}` 이 남아 있다"
    assert "과제 평가 대상" in _skill(), "domain-rules.md 「과제 평가 대상」을 가리키지 않는다"


def test_duplicate_key_includes_title():
    text = _skill()
    # 「(가)·(나)·(다)·(라) 를 전부 한다」 같은 목차 줄이 먼저 나오므로 굵은 글머리로 찾는다
    dup = text.split("**(나)", 1)[1].split("**(다)", 1)[0]
    assert "과제 안내" in dup, "중복 판정 (나) 가 과제 이름까지 보지 않는다 — 같은 날 두 번째 과제를 막는다"


def test_same_day_multiple_is_allowed_and_ambiguous_grade_asks():
    text = _all()
    assert "같은 날" in text, "같은 날 과제가 여럿일 수 있다는 서술이 없다"
    assert "되묻" in text or "골라" in text or "묻는다" in text, (
        "그날 과제가 여럿인데 어느 과제인지 안 밝힌 평가 발화를 되묻는 절차가 없다"
    )


def test_examples_walk_two_assignments_same_day():
    ex = (HW / "references" / "examples.md").read_text(encoding="utf-8")
    assert ex.count("같은 날") >= 1 and "어느 과제" in ex, (
        "examples.md 에 같은 날 과제 둘·어느 과제인지 되묻는 예시가 없다"
    )
