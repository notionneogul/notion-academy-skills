import re

from helpers import REPO, SKILLS, skill_dirs

CORE_REFS = SKILLS / "academy-core" / "references"
TPL = SKILLS / "academy-template"


def _write_safety() -> str:
    return (CORE_REFS / "write-safety.md").read_text(encoding="utf-8")


def _skill() -> str:
    return (TPL / "SKILL.md").read_text(encoding="utf-8")


def _all_text() -> str:
    return "\n".join(p.read_text(encoding="utf-8") for p in TPL.rglob("*.md"))


def test_schema_add_is_no_longer_done_by_any_skill():
    row = next(l for l in _write_safety().splitlines() if "속성 추가" in l)
    assert "하지 않는다" in row, "write-safety.md 가 아직 속성 추가를 허용한다"


def test_schema_delete_and_rename_stay_forbidden():
    text = _write_safety()
    assert re.search(r"속성 삭제.{0,120}(하지 않는다|금지)", text), (
        "속성 삭제를 하지 않는다는 경계가 없다"
    )
    assert re.search(r"이름 변경.{0,160}(하지 않는다|금지)", text), (
        "속성 이름 변경을 하지 않는다는 경계가 없다"
    )


def test_schema_delete_states_why_it_cannot_be_undone():
    text = _write_safety()
    assert re.search(r"속성 삭제.{0,200}되돌릴", text, re.S), (
        "속성 삭제가 왜 되돌릴 수 없는지가 적혀 있지 않다"
    )


def test_template_writes_message_template_rows_only():
    text = _skill()
    section = text.split("## 쓰는 속성", 1)[1].split("\n## ", 1)[0]
    assert "문자 양식" in section, "쓰는 속성 절이 `문자 양식` DB 를 적지 않는다"
    for forbidden in ["ADD COLUMN", "notion-update-data-source"]:
        assert forbidden not in text, f"academy-template 이 아직 스키마를 바꾼다: `{forbidden}`"


def test_template_validates_variables_by_space_stripped_property_names():
    text = _skill()
    assert "띄어쓰기" in text, "변수 대조 규칙(속성 이름에서 띄어쓰기를 뺀 것)이 없다"
    assert "db-map.md" in text and "문자 양식 변수" in text, (
        "변수 규칙을 db-map.md 「문자 양식 변수」로 가리키지 않는다"
    )


def test_template_stops_on_unknown_variable_before_writing():
    text = _all_text()
    assert "#{출결문자}" in text, "없는 변수를 걸러내는 예시(#{출결문자})가 없다"
    assert "멈춘다" in text, "없는 변수가 있으면 쓰기 전에 멈춘다는 절차가 없다"


def test_template_has_no_solapi_or_old_properties():
    text = _all_text()
    for old in ["솔라피", "Solapi", "solapi", "fixed_length", "클로드출결", "가변 문자", "알림톡 모드", "은퇴한 발송 스킬"]:
        assert old not in text, f"academy-template 에 옛 구조 `{old}` 이 남아 있다"


def test_no_skill_changes_the_schema():
    pattern = re.compile(r"ADD COLUMN|DROP COLUMN|RENAME COLUMN|notion-update-data-source")
    offenders = []
    for d in skill_dirs():
        t = "\n".join(p.read_text(encoding="utf-8") for p in d.rglob("*.md"))
        if pattern.search(t):
            offenders.append(d.name)
    assert not offenders, f"스키마를 바꾸는 스킬이 남아 있다: {offenders}"


def test_template_skill_exists_and_is_listed():
    assert (TPL / "SKILL.md").exists()
    assert "academy-template" in (REPO / "README.md").read_text(encoding="utf-8")
