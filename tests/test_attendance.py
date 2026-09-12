from helpers import SKILLS

AT = SKILLS / "academy-attendance"


def _skill():
    return (AT / "SKILL.md").read_text(encoding="utf-8")


def _all():
    return "\n".join(p.read_text(encoding="utf-8") for p in AT.rglob("*.md"))


def test_uses_new_makeup_date_name():
    text = _all()
    assert "보강 날짜" not in text, "없어진 `보강 날짜` 가 남아 있다"
    assert "date:보강 예정일:start" in _skill(), "쓰는 속성에 `date:보강 예정일:start` 가 없다"


def test_makeup_completion_creates_row_then_checks_original():
    text = _skill()
    section = text.split("### 보강", 1)[1].split("\n### ", 1)[0]
    assert "새 행" in section and "보강완료" in section, (
        "보강 완료가 「새 행 생성 → 원래 행 보강완료 체크」로 적혀 있지 않다"
    )
    seg = section[section.index("새 행"):]
    assert "보강완료" in seg, "보강 완료 순서가 거꾸로다"
    assert "domain-rules.md" in section, "보강 규칙을 core 로 가리키지 않는다"


def test_makeup_completion_explains_why_row_is_needed():
    section = _skill().split("### 보강", 1)[1].split("\n### ", 1)[0]
    assert "Make" in section, "체크박스만 켜면 Make 가 알림톡을 안 보낸다는 이유가 없다"


def test_examples_walk_makeup_completion():
    ex = (AT / "references" / "examples.md").read_text(encoding="utf-8")
    assert "보강 예정일" in ex and "보강완료" in ex and "새 행" in ex, (
        "examples.md 에 보강 완료(새 행 생성 + 원래 행 체크) 예시가 없다"
    )
