import re

from helpers import SKILLS, skill_dirs

CORE_REFS = SKILLS / "academy-core" / "references"
REPORT = SKILLS / "academy-report"


def _write_safety() -> str:
    return (CORE_REFS / "write-safety.md").read_text(encoding="utf-8")


def test_attaching_a_file_needs_approval():
    text = _write_safety()
    assert "파일 붙이기" in text
    assert re.search(r"파일 붙이기.{0,100}승인", text), (
        "페이지에 파일을 붙이는 것이 승인 조건으로 적혀 있지 않다"
    )
    assert re.search(r"파일 붙이기\s*\|.*write-gate\.md.*4단계", text), (
        "파일 붙이기가 write-gate.md 4단계(승인 판정의 단일 출처)를 가리키지 않는다"
    )


def test_attaching_a_file_states_parents_can_see_it():
    text = _write_safety()
    assert re.search(r"파일 붙이기.{0,200}학부모", text, re.S), (
        "붙인 파일을 학부모가 볼 수 있다는 것이 경계 근거로 적혀 있지 않다"
    )


def test_deleting_a_file_block_is_not_done():
    text = _write_safety()
    assert re.search(r"파일 블록 삭제.{0,120}(하지 않는다|금지)", text), (
        "파일 블록을 지우지 않는다는 경계가 없다"
    )


def test_form_ships_with_the_skill():
    form = REPORT / "references" / "form.html"
    assert form.exists(), "배포용 양식이 스킬 폴더에 없다"
    text = form.read_text(encoding="utf-8")
    assert "@page" in text and "A4" in text, "인쇄용 A4 규격이 없다"
    assert "--brand" in text, "학원 대표색을 고칠 자리(CSS 변수)가 없다"


def _skill() -> str:
    return (REPORT / "SKILL.md").read_text(encoding="utf-8")


def test_report_skill_exists_and_is_listed():
    """skill_dirs() 는 SKILL.md 가 있는 폴더만 돌려주므로, 이 확인 하나로 둘 다 잡힌다."""
    assert "academy-report" in [d.name for d in skill_dirs()]


def test_form_is_read_from_a_fixed_path():
    text = _skill()
    assert "~/.academy/report-form.html" in text, "양식 자리가 고정 경로로 적혀 있지 않다"
    assert re.search(r"없으면.{0,120}(기본 양식|references/form\.html)", text), (
        "원장 양식이 없을 때 기본 양식을 쓴다는 서술이 없다"
    )


def test_default_form_use_is_disclosed():
    text = _skill()
    assert re.search(r"(기본 양식|샘플).{0,160}(미리보기|밝힌다|알린다)", text, re.S), (
        "기본 양식을 쓰고 있다는 것을 미리보기에 밝힌다는 서술이 없다"
    )


def test_data_collection_points_at_message_skill():
    text = _skill()
    assert "academy-message" in text
    assert re.search(r"academy-message.{0,200}(3단계|근거 수집)", text, re.S), (
        "한 달치 데이터 수집을 academy-message 로 넘긴다는 서술이 없다"
    )


def test_existing_month_is_not_overwritten():
    text = _skill()
    assert re.search(r"같은 달.{0,160}(덮어쓰지 않는다|묻는다)", text, re.S), (
        "같은 달 리포트가 이미 있을 때의 처리가 없다"
    )


def test_missing_data_is_written_as_missing():
    text = _skill()
    assert re.search(r"(없으면|비어).{0,120}(그렇게 적는다|기록 없음)", text, re.S), (
        "데이터가 없을 때 빈 칸으로 두지 않는다는 서술이 없다"
    )


def test_existing_month_is_checked_before_the_preview():
    """같은 달 파일이 있는지를 승인 뒤에 읽으면 미리보기가 승인 요청이 못 된다.

    5단계 미리보기는 「누구를 왜 빼는지」를 담는데, 뺄 학생은 페이지 본문을
    읽어야 드러난다. 그 걸음이 6단계(승인 뒤)에만 있으면 원장이 승인한 대상과
    실제로 붙인 대상이 갈린다.
    """
    text = _skill()
    before = text[: text.index("### 5. 미리보기")]
    assert "notion-fetch" in before, (
        "페이지 본문을 승인(5단계) 앞에서 읽는 걸음이 절차에 없다"
    )
    assert re.search(r"본문.{0,300}같은 달", before, re.S), (
        "승인 앞에서 같은 달 파일이 이미 있는지 보는 서술이 없다"
    )
