"""샘플 데이터 정리 절차가 `academy-setup` 안에 온전히 있는지 본다.

구매자가 첫날 가장 먼저 부딪히는 절차라, 순서 한 칸이 어긋나면 고아 행이 남고
남기는 2종 하나가 빠지면 이후 스킬이 가리킬 곳을 잃는다. 낱말이 있는지가 아니라
순서와 항목이 실제로 갖춰져 있는지를 검사한다.
"""

import re

import pytest

from helpers import REPO, SKILLS

SETUP = SKILLS / "academy-setup"
SETUP_MD = SETUP / "SKILL.md"


@pytest.fixture(scope="module")
def setup_text() -> str:
    return SETUP_MD.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def cleanup_section(setup_text: str) -> str:
    """「샘플 데이터 정리」 절 본문. 다음 `## ` 헤더 전까지."""
    m = re.search(r"^## 샘플 데이터 정리\s*$", setup_text, re.M)
    assert m, "academy-setup/SKILL.md 에 「## 샘플 데이터 정리」 절이 없다"
    rest = setup_text[m.end():]
    nxt = re.search(r"^## ", rest, re.M)
    return rest[: nxt.start()] if nxt else rest


def test_setup_owns_sample_cleanup(setup_text):
    """새 스킬이 아니라 academy-setup 이 맡아야 한다 — 연결 다음에 오는 절차다."""
    assert re.search(r"^## 샘플 데이터 정리\s*$", setup_text, re.M), (
        "academy-setup/SKILL.md 에 「## 샘플 데이터 정리」 절이 없다"
    )
    others = [
        d.name
        for d in SKILLS.iterdir()
        if d.is_dir() and d.name.startswith("academy-") and "sample" in d.name
    ]
    assert not others, f"샘플 정리용 별도 스킬 폴더가 생겼다: {others}"


def test_setup_description_triggers_on_sample_cleanup(setup_text):
    """frontmatter 에 없으면 '샘플 지워줘' 발화에서 이 스킬이 뜨지 않는다."""
    front = setup_text.split("---", 2)[1]
    assert "샘플" in front, (
        "academy-setup frontmatter description 에 샘플 정리 트리거가 없다"
    )


# 잎(가리키는 쪽) → 뿌리(가리켜지는 쪽). 표의 각 행 첫 칸이 단계 번호다.
MOVE_STAGES = [
    (1, ["출석부", "과제", "시험", "수강료 납부", "재원생 상담", "클래스 공지사항"]),
    (2, ["시험 카테고리", "신입생"]),
    (3, ["학생 과목별 페이지"]),
    (4, ["학생"]),
    (5, ["클래스", "학교"]),
]


def _subsection(section: str, heading: str, exact: bool = False) -> str:
    """`### <heading>` 소절 본문. exact=True 면 제목이 정확히 그 글자여야 한다.

    「되돌리기」와 「되돌리기 목록」처럼 한쪽이 다른 쪽의 접두사인 제목이 있어
    (뒤엣것은 보관 페이지에 써 넣을 예시 안에 있다) 정확 일치가 필요하다.
    """
    tail = r"\s*$" if exact else r"[^\n]*$"
    m = re.search(rf"^### {heading}{tail}", section, re.M)
    assert m, f"「### {heading}」 절이 없다"
    rest = section[m.end():]
    nxt = re.search(r"^### ", rest, re.M)
    return rest[: nxt.start()] if nxt else rest


def _stage_rows(section: str) -> dict[int, str]:
    """「옮기는 순서」 표의 단계 번호 → 그 행의 나머지.

    미리보기 예시에도 같은 모양의 표가 있으므로 절을 좁혀서 읽는다.
    """
    order = _subsection(section, "옮기는 순서")
    rows = {}
    for m in re.finditer(r"^\|\s*([1-5])\s*\|([^\n]*)$", order, re.M):
        rows[int(m.group(1))] = m.group(2)
    return rows


def test_move_order_has_five_stages(cleanup_section):
    rows = _stage_rows(cleanup_section)
    missing = [n for n, _ in MOVE_STAGES if n not in rows]
    assert not missing, f"이동 순서 표에 없는 단계: {missing}"


@pytest.mark.parametrize("stage,dbs", MOVE_STAGES, ids=lambda v: str(v))
def test_each_stage_lists_its_databases(stage, dbs, cleanup_section):
    if not isinstance(stage, int):
        pytest.skip("parametrize id helper")
    row = _stage_rows(cleanup_section).get(stage, "")
    missing = [db for db in dbs if f"`{db}`" not in row]
    assert not missing, f"이동 순서 {stage}단계 행에 빠진 DB: {missing} (행: {row.strip()})"


def test_move_order_is_leaf_to_root(cleanup_section):
    """과목 페이지가 학생보다 **먼저** 나와야 한다.

    뒤집히면 학생을 먼저 치우게 되어 과목 페이지가 고아가 된다. 표의 단계 번호로
    본다 — 본문 어딘가에 낱말이 먼저 나오는 것만으로는 순서가 보장되지 않는다.
    """
    rows = _stage_rows(cleanup_section)
    stage_of = {}
    for stage, row in rows.items():
        for db in ["출석부", "학생 과목별 페이지", "학생", "클래스", "학교", "신입생"]:
            if f"`{db}`" in row:
                stage_of[db] = stage
    for leaf, root in [
        ("출석부", "학생 과목별 페이지"),
        ("학생 과목별 페이지", "학생"),
        ("학생", "학교"),
        ("학생 과목별 페이지", "클래스"),
        ("신입생", "학교"),
    ]:
        assert leaf in stage_of and root in stage_of, (
            f"이동 순서 표에서 {leaf} 또는 {root} 를 찾지 못했다: {stage_of}"
        )
        assert stage_of[leaf] < stage_of[root], (
            f"이동 순서가 잎에서 뿌리로가 아니다 — {leaf}({stage_of[leaf]}단계)가 "
            f"{root}({stage_of[root]}단계)보다 뒤에 있다"
        )


KEEP = {
    "문자 양식": "원장이 그대로 쓸 양식이라 남긴다",
    "납부 월": "연월이라 학원이 달라도 재사용된다",
}


@pytest.mark.parametrize("db", sorted(KEEP), ids=sorted(KEEP))
def test_kept_databases_are_named_with_a_reason(db, cleanup_section):
    """둘 중 하나라도 빠지면 그 DB 가 통째로 치워진다."""
    keep_section = _subsection(cleanup_section, "남기는 것")
    row = re.search(rf"^\|\s*`{re.escape(db)}`\s*\|([^\n]*)$", keep_section, re.M)
    assert row, f"「남기는 것」 표에 `{db}` 행이 없다 ({KEEP[db]})"
    assert len(row.group(1).replace("|", "").strip()) >= 10, (
        f"「남기는 것」 표의 `{db}` 행에 왜 남기는지가 없다"
    )


def test_kept_databases_never_moved(cleanup_section):
    rows = _stage_rows(cleanup_section)
    for stage, row in rows.items():
        for db in KEEP:
            assert f"`{db}`" not in row, (
                f"남겨야 할 `{db}` 가 이동 순서 {stage}단계에 들어가 있다"
            )


def test_warns_message_template_student_relation_empties(setup_text):
    """과목 페이지를 치우면 `문자 양식` 의 `학생` relation 이 전부 빈다.

    이 경고가 없으면 원장은 문자가 안 나가는 이유를 몇 주 뒤에 알게 된다.
    """
    assert re.search(r"문자 양식[^\n]*`학생`[^\n]*(빈다|빕니다|비었습니다|전부 빈)", setup_text), (
        "문자 양식의 `학생` 연결이 빈다는 경고가 없다"
    )
    assert "academy-message" in setup_text, (
        "문자 양식 부작용이 academy-message 에 어떻게 나타나는지 적혀 있지 않다"
    )
    assert "각 양식의 `학생` 속성에 연결" in setup_text, (
        "결과 보고에 원장이 무엇을 해야 하는지(각 양식의 `학생` 속성 연결)가 없다"
    )


def test_result_report_hands_off_to_enroll(setup_text):
    assert "academy-enroll" in setup_text, (
        "샘플 정리 이후 academy-enroll 로 넘어가는 안내가 없다"
    )


def test_undo_is_documented_in_reverse_order(cleanup_section):
    m = re.search(r"^### 되돌리기\s*$", cleanup_section, re.M)
    assert m, "「되돌리기」 절이 없다"
    undo = cleanup_section[m.end():]
    # 백틱까지 포함해 찾는다. 백틱 없이 "클래스" 를 찾으면 `클래스 공지사항` 의
    # 부분 문자열에 걸려, 문장을 손대는 것만으로 순서 판정이 뒤집힌다.
    order = ["`클래스`", "`학생 과목별 페이지`", "`시험 카테고리`"]
    positions = []
    for name in order:
        i = undo.find(name)
        assert i >= 0, f"되돌리기 절에 {name} 이 없다"
        positions.append(i)
    assert positions == sorted(positions), (
        f"되돌리기 순서가 뿌리에서 잎으로가 아니다: {dict(zip(order, positions))}"
    )
    assert "반대" in undo, "되돌리기가 이동과 반대 순서임을 밝히지 않았다"
    assert "write-safety.md" in undo, (
        "되돌리기 호출 형식의 출처(write-safety.md 「되돌리기 절차」)를 가리키지 않는다"
    )


def test_gate_is_strong_and_incremental(cleanup_section):
    assert "되돌릴 수 있지만 규모가 큽니다" in cleanup_section, (
        "승인 문구가 규모를 알리지 않는다"
    )
    assert re.search(r"DB 하나가 끝날 때마다[^\n]*몇 행을 옮겼는지와 `COUNT\(\*\)` 재확인 결과를 말하고", cleanup_section), (
        "DB 하나가 끝날 때마다 옮긴 행 수와 COUNT 재확인 결과를 보고하라는 규칙이 없다"
    )
    assert re.search(r"어디까지 갔는지[^\n]*멈춘다", cleanup_section), (
        "중간 실패 시 어디까지 갔는지 말하고 멈춘다는 규칙이 없다"
    )
    assert "조용히 다음 DB 로 넘어가지 않는다" in cleanup_section, (
        "실패 후 조용히 다음 DB 로 넘어가지 않는다는 규칙이 없다"
    )


def test_preview_is_per_database_row_counts(cleanup_section):
    assert "행을 한 줄씩 보여주지 않는다" in cleanup_section, (
        "미리보기를 DB별 행 수 표로 한다는 규칙이 없다 — 수백 행을 나열하면 검토가 안 된다"
    )
    assert "COUNT(*)" in cleanup_section, (
        "미리보기의 행 수를 COUNT(*) 로 센다는 지시가 없다"
    )


def test_batch_cap_is_delegated_not_restated(cleanup_section):
    assert "notion-move-pages" in cleanup_section
    assert "100건" in cleanup_section, "배치 상한(100건)이 적혀 있지 않다"
    assert "write-gate.md` 6단계" in cleanup_section, (
        "notion-move-pages 배치 상한의 출처인 write-gate.md 6단계를 가리키지 않는다"
    )
    assert not re.search(r"배치 상한\(100건[^\n)]*5단계", cleanup_section), (
        "배치 상한의 출처를 write-gate.md 5단계로 적고 있다 — 5단계는 notion-create-pages 상한이고 "
        "이 스킬은 행을 만들지 않는다"
    )
    assert "notion-create-pages" in cleanup_section, (
        "5단계 상한이 이 스킬과 무관하다는 것을 밝히지 않았다"
    )


def test_archive_page_procedure_points_at_write_gate(cleanup_section):
    assert "../academy-core/references/write-gate.md" in cleanup_section, (
        "보관 페이지 절차의 출처(write-gate.md)를 가리키지 않는다"
    )
    assert "6단계 「보관 페이지 절차」" in cleanup_section, (
        "보관 페이지를 찾고 없으면 만드는 절차가 있는 write-gate.md 6단계를 가리키지 않는다"
    )
    assert "여기서 다시 적지 않는다" in cleanup_section, (
        "core 문서의 보관 페이지 절차를 재진술하지 않는다는 것이 명시되지 않았다"
    )


ARCHIVE_PAGE_ID = "3c3596e032e08191a01dee9e4724466f"


def test_archive_page_id_is_not_hardcoded_anywhere():
    """보관 페이지 id 는 구매자 사본마다 다르다. 박아 두면 남의 페이지로 옮긴다."""
    offenders = [
        str(md.relative_to(REPO))
        for md in REPO.rglob("*.md")
        if ARCHIVE_PAGE_ID in md.read_text(encoding="utf-8")
    ]
    assert not offenders, f"보관 페이지 id 가 문서에 박혀 있다: {offenders}"
    text = SETUP_MD.read_text(encoding="utf-8")
    assert "이름으로 찾" in text, (
        "보관 페이지를 이름으로 찾는다는 지시가 없다"
    )


def test_row_counts_are_not_hardcoded():
    """행 수는 실측값이고 구매자마다 다르다 (`query-limits.md`).

    세 자리 이상의 숫자에 '행' 이 붙어 있으면 제작자 사본의 실측값을 그대로
    옮겨 적은 것이다.
    """
    for md in [SETUP_MD, SETUP / "references" / "examples.md"]:
        text = md.read_text(encoding="utf-8")
        hits = re.findall(r"[0-9]{3,}\s*행", text)
        assert not hits, f"{md.name} 에 고정 행 수가 적혀 있다: {hits}"


def test_only_one_cleanup_mode(setup_text):
    """「이름만 바꾸기」 모드는 만들지 않기로 확정됐다."""
    assert "「통째로 비우기」 한 가지 방식뿐이다" in setup_text, (
        "통째로 비우기 한 가지 방식이라는 것이 명시되지 않았다"
    )


def test_setup_no_longer_claims_it_never_writes():
    """README 가 academy-setup 을 '아무것도 쓰지 않는다' 로 남겨 두면 거짓이 된다."""
    text = (REPO / "README.md").read_text(encoding="utf-8")
    assert "`academy-setup`, `academy-insight` 는 노션에 아무것도 쓰지 않습니다" not in text, (
        "README 가 academy-setup 이 노션에 아무것도 쓰지 않는다고 적고 있다 — "
        "샘플 정리는 행을 옮긴다"
    )
    assert "샘플 보관" in text, "README 에 샘플 정리의 이동 대상 페이지 안내가 없다"


# --- 되돌리기 목록 -------------------------------------------------------
#
# 실측: 보관 페이지로 옮긴 행을 notion-fetch 로 열면 title 하나만 나온다.
# 원래 어느 DB 것이었는지 알아낼 방법이 없으므로, 목록을 보관 페이지 본문에
# 남기지 않으면 되돌리기가 문서상으로만 존재하게 된다.


def test_documents_that_moved_rows_lose_their_properties(cleanup_section):
    assert re.search(r"`title` 하나만", cleanup_section), (
        "옮긴 행에 title 밖에 남지 않는다는 실측 사실이 적혀 있지 않다"
    )
    assert re.search(r"어느 DB 것이었는지[^\n]*(알려 주지 않는다|알 수 없다|알아낼 방법이 없다)", cleanup_section), (
        "옮긴 행만 보고는 원래 DB 를 알 수 없다는 것이 적혀 있지 않다"
    )


def test_undo_list_is_written_into_the_archive_page(cleanup_section):
    assert "### 되돌리기 목록" in cleanup_section, (
        "보관 페이지 본문에 넣을 「되돌리기 목록」 형식 예시가 없다"
    )
    for token in ["옮긴 날:", "collection://<uuid>", "<id>"]:
        assert token in cleanup_section, f"되돌리기 목록 형식에 {token} 이 없다"
    assert "insert_content" in cleanup_section, (
        "목록을 쓰는 호출(notion-update-page + insert_content)이 적혀 있지 않다"
    )
    assert '{"type": "end"}' in cleanup_section, (
        "insert_content 의 position 이 본문 끝({\"type\": \"end\"})으로 지정되어 있지 않다"
    )


def test_undo_list_is_written_before_the_move_not_after(cleanup_section):
    """이동 뒤에 쓰면 마지막 move 와 insert_content 사이가 기록 없는 창이 된다.

    그 창에서 실패하면 옮겨진 행은 title 만 남은 채 어느 DB 것인지 알 수 없다.
    """
    assert "기록이 이동보다 먼저다" in cleanup_section, (
        "목록 기록이 이동보다 먼저라는 규칙이 없다"
    )
    loop = _subsection(cleanup_section, "DB 하나를 옮기는 루프")
    record = loop.find("insert_content")
    move = loop.find("notion-move-pages")
    assert record >= 0 and move >= 0, "루프에 기록·이동 호출이 둘 다 나오지 않는다"
    assert record < move, (
        "루프의 걸음 순서가 기록보다 이동을 먼저 둔다 — 기록되지 않은 이동이 생긴다"
    )
    assert "순서를 바꾸지 않는다" in loop, "기록·이동 순서를 고정한다는 못이 없다"
    assert re.search(r"옮기지 못한 id[^\n]*무해", cleanup_section), (
        "미리 적은 뒤 옮기지 못한 id 가 무해하다는 근거(대조가 걸러낸다)가 없다"
    )


def test_move_loop_is_per_database_with_count_verification(cleanup_section):
    """전량 SELECT 는 잘려도 신호가 없다 — COUNT 재확인이 유일한 완료 증거다."""
    loop = _subsection(cleanup_section, "DB 하나를 옮기는 루프")
    assert "페이지네이션이 없" in loop, (
        "SQL 모드에 페이지네이션이 없다는 제약이 적혀 있지 않다"
    )
    assert re.search(r"잘려도[^\n]*신호를 주지 않", loop), (
        "조회가 잘려도 신호가 없다는 것이 적혀 있지 않다"
    )
    assert "LIMIT 100" in loop, "배치 상한만큼만 조회한다는 지시가 없다"
    assert "행이 많은 DB 는 통째로 읽지 않는다" in loop, (
        "query-limits.md 의 전량 SELECT 금지를 가리키지 않는다"
    )
    assert re.search(r"`COUNT\(\*\)` 를 다시 센다", loop), (
        "이동 뒤 COUNT 재확인 걸음이 없다"
    )
    assert re.search(r"마지막 `COUNT\(\*\)` 가 0 인 것이[^\n]*유일한 증거", cleanup_section), (
        "COUNT 0 이 완료의 유일한 증거라는 서술이 없다"
    )
    assert re.search(r"SELECT url FROM", cleanup_section) is None, (
        "url 을 따로 조회하는 지시가 남아 있다 — notion-move-pages 는 uuid 배열을 받는다"
    )


def test_move_loop_matches_database_names_exactly(cleanup_section):
    """부분 일치로 풀면 `학생` 이 `학생 과목별 페이지` 에, `시험` 이 `시험 카테고리` 에 딸려간다."""
    loop = _subsection(cleanup_section, "DB 하나를 옮기는 루프")
    assert "정확히 일치" in loop, "config 키와 정확히 일치로 찾는다는 지시가 없다"
    assert "접두" in loop, "접두·부분 일치로 풀지 않는다는 금지가 없다"
    assert re.search(r"남기는 2종이 그 안에 없는지", loop), (
        "이동 직전에 남기는 2종이 대상에 없는지 확인하는 절차가 없다"
    )


def test_partial_cleanup_also_records_the_list(cleanup_section):
    """단독 정리는 '단계' 가 없어서 단계 단위 규칙에 안 걸렸다."""
    assert re.search(r"부분 정리도 이 루프를 그대로 탄다", cleanup_section), (
        "「출석부만 비워줘」 같은 부분 정리가 같은 루프를 탄다는 것이 명시되지 않았다"
    )
    assert re.search(r"단계가 없다고 목록 기록을 건너뛰지 않는다", cleanup_section), (
        "부분 정리에서도 목록 기록을 건너뛰지 않는다는 못이 없다"
    )


def test_undo_starts_by_reading_the_list_and_stops_without_it(cleanup_section):
    undo = _subsection(cleanup_section, "되돌리기", exact=True)
    assert "되돌리기 목록" in undo, "되돌리기 절이 목록을 읽는 것부터 시작하지 않는다"
    assert "notion-fetch" in undo, "목록을 무엇으로 읽는지(notion-fetch)가 없다"
    assert "목록이 없으면 되돌릴 수 없다고" in undo, (
        "목록이 없을 때 되돌릴 수 없다고 말하고 멈춘다는 서술이 없다"
    )
    assert re.search(r"추측으로[^\n]*(넣지 않는다|하지 않는다)", undo), (
        "목록이 없을 때 추측으로 되돌리지 않는다는 금지가 없다"
    )


def test_result_report_warns_deleting_archive_page_loses_undo(setup_text):
    """지금까지는 '지우세요' 만 있어서 되돌리기를 스스로 막는 안내였다."""
    assert "되돌리기 목록을 보관 페이지에 적어 두었습니다" in setup_text, (
        "결과 보고에 되돌리기 목록을 남겼다는 안내가 없다"
    )
    assert re.search(r"지우면 되돌리기 목록도 함께 사라져 되돌릴 수 없습니다", setup_text), (
        "결과 보고에 보관 페이지를 지우면 되돌릴 수 없다는 경고가 없다"
    )
    assert re.search(r"지우라는 안내는 샘플 정리 직후에만 한다", setup_text), (
        "보관 페이지를 지우라는 안내에 시점 조건이 없다 — 이 페이지는 공용 보관소다"
    )
    assert "공용 보관소" in setup_text, (
        "보관 페이지가 일곱 쓰기 스킬과 공용이라는 것이 적혀 있지 않다"
    )
    assert "지우기 전에 안에 샘플 말고 다른 것이 들어 있지 않은지" in setup_text, (
        "지우기 전에 내용을 확인하라는 안내가 없다"
    )


def test_routing_covers_cleanup_then_enroll():
    text = (REPO / "skills" / "academy-core" / "references" / "routing.md").read_text(
        encoding="utf-8"
    )
    assert "샘플 정리 + 신규 등록" in text, (
        "routing.md 에 「샘플 정리 + 신규 등록」 조합이 없다"
    )


def test_doctor_placeholder_checks_point_at_cleanup():
    """샘플이 통째로 남아 있으면 한 건씩 고치는 것보다 정리 절차가 맞다."""
    text = (
        REPO / "skills" / "academy-doctor" / "references" / "checks.md"
    ).read_text(encoding="utf-8")
    section = text.split("## 플레이스홀더 잔존", 1)
    assert len(section) == 2, "checks.md 에 「플레이스홀더 잔존」 절이 없다"
    body = section[1]
    assert "academy-setup" in body and "샘플 데이터 정리" in body, (
        "「플레이스홀더 잔존」 절이 academy-setup 의 샘플 데이터 정리를 가리키지 않는다"
    )


# --- 목록 압축 · 실제 상태 대조 -----------------------------------------
#
# id 를 한 줄에 하나씩 적으면 로그가 수천 행인 학원에서 본문이 감당이 안 된다.
# 그리고 `insert_content` 는 덧붙이기라 되돌린 항목을 목록에서 지울 수 없다 —
# 목록을 고치는 대신 되돌리기 직전에 보관 페이지의 실제 자식과 대조한다.


def test_undo_list_packs_ids_on_one_line_per_database(cleanup_section):
    """DB 한 줄에 id 를 공백으로 이어 붙여야 줄 수가 DB 개수로 고정된다."""
    m = re.search(r"^### 되돌리기 목록\n(.*?)^```", cleanup_section, re.M | re.S)
    assert m, "되돌리기 목록 형식 예시(코드 블록)를 찾지 못했다"
    example = m.group(1)
    assert re.search(r"`<id>`\s+`<id>`", example), (
        f"목록 예시가 id 를 한 줄에 공백으로 이어 붙이지 않는다:\n{example}"
    )
    assert not re.search(r"^\s*-\s*`<(?:page )?id>`", example, re.M), (
        f"목록 예시에 id 를 한 줄에 하나씩 적는 글머리가 남아 있다:\n{example}"
    )
    assert re.search(r"줄 수가[^\n]*(DB 개수|데이터베이스 개수)", cleanup_section), (
        "압축 형식의 이유(줄 수가 DB 개수로 고정된다)가 적혀 있지 않다"
    )


def test_undo_parses_ids_by_whitespace(cleanup_section):
    undo = _subsection(cleanup_section, "되돌리기", exact=True)
    assert re.search(r"공백 기준으로 잘라", undo), (
        "되돌리기 절에 id 를 공백 기준으로 잘라 읽는다는 파싱 방법이 없다"
    )


def test_undo_declares_target_state_without_reading_it(cleanup_section):
    """실측: 이미 제자리인 행을 다시 옮기면 오류가 아니라 no-op 이고,
    도구가 몇 건이 그랬는지 직접 알려준다. 그래서 상태를 읽을 이유가 없다.

    자식 목록을 읽지 않으면 잘림·정규화·fail-open 세 문제가 한꺼번에 사라진다.
    """
    undo = _subsection(cleanup_section, "되돌리기", exact=True)
    assert "보관 페이지의 상태를 읽지 않는다" in undo, (
        "되돌리기가 보관 페이지 상태를 읽지 않는다는 것을 밝히지 않았다"
    )
    assert "already in the target location" in undo, (
        "도구가 돌려주는 no-op 응답(already in the target location)이 근거로 적혀 있지 않다"
    )
    assert re.search(r"추론하지 않는다[^\n]*틀릴 수도 없다", undo), (
        "「이미 되돌아갔는지」를 추론하지 않는다는 근거가 없다"
    )
    assert re.search(r"목적 상태를 선언", undo), (
        "상태를 읽지 않고 목적 상태를 선언하는 방식이라는 성격이 적혀 있지 않다"
    )


def test_undo_no_longer_reads_children_or_normalizes(cleanup_section):
    """없앤 절차가 되살아나면 잘림·정규화 문제도 함께 돌아온다."""
    undo = _subsection(cleanup_section, "되돌리기", exact=True)
    for gone, why in [
        ("겹치는 것만 되돌린다", "목록과 자식의 대조"),
        ("총수", "자식 수와 목록 건수 대조"),
        ("이미 되돌아간 것으로 본다", "되돌아갔는지를 추론하는 판정"),
    ]:
        assert gone not in undo, (
            f"되돌리기 절에 없앤 절차({why})가 남아 있다: {gone!r}"
        )
    assert "자식 목록을 조회하지도" in undo, (
        "자식 목록을 조회하지 않는다는 부정문이 없다 — 낱말만 사라지면 절차가 되살아난 것을 못 잡는다"
    )


def test_undo_reports_both_counts_from_the_tool_response(cleanup_section):
    undo = _subsection(cleanup_section, "되돌리기", exact=True)
    assert "이미 제자리에 있었습니다" in undo, (
        "결과 보고에 이미 제자리였던 건수를 적는다는 지시가 없다"
    )
    assert re.search(r"도구가 돌려주는 결과를 그대로 읽는다", undo), (
        "건수의 출처가 도구 응답이라는 것이 적혀 있지 않다 — 추론으로 세면 안 된다"
    )
    assert re.search(r"미리보기는 목록 기준", undo), (
        "미리보기를 목록 기준으로 한다는 규칙이 없다 — 실제 건수를 미리 알려면 상태를 읽어야 한다"
    )


def test_button_databases_are_flagged_without_overclaiming(cleanup_section):
    """버튼 동작은 미확인이다 — 단정하지 않고 확인 안내만 남긴다."""
    caution = _subsection(cleanup_section, "주의")
    assert "`퇴원`" in caution and "`재원생 등록`" in caution, (
        "「주의」에 버튼이 있는 DB(학생·신입생)가 적혀 있지 않다"
    )
    assert "확인되지 않았다" in caution, (
        "버튼의 실제 동작이 미확인이라는 것을 밝히지 않았다 — 단정하면 안 된다"
    )


def test_undo_states_its_own_batch_cap(cleanup_section):
    undo = _subsection(cleanup_section, "되돌리기", exact=True)
    assert "100건" in undo, "되돌리기에 배치 상한 안내가 없다"
    assert re.search(r"배치마다 도구 응답을 읽어", undo), (
        "되돌리기 배치마다 도구 응답을 읽어 건수를 누적하라는 지시가 없다"
    )


def test_move_order_rationale_is_about_stopping_midway():
    """전량 비우기에서는 고아가 안 생긴다 — 근거는 중간 실패와 부분 정리다."""
    text = SETUP_MD.read_text(encoding="utf-8")
    order = re.search(r"^### 옮기는 순서[^\n]*$", text, re.M)
    assert order, "「옮기는 순서」 절이 없다"
    head = text[order.end(): text.index("|", order.end())]
    assert "중간에 멈췄을 때" in head and "부분 정리" in head, (
        "순서의 근거가 중간 실패·부분 정리로 적혀 있지 않다"
    )
    assert "고아" not in head, (
        "순서의 근거가 아직 '고아 행' 이다 — 전량 비우기에서는 고아가 생기지 않아 "
        "'어차피 다 비우는데 왜' 로 뒤집힌다"
    )


def test_install_classification_matches_readme():
    """README 만 고치고 INSTALL 을 두면 같은 배포물이 앞뒤로 어긋난다."""
    text = (REPO / "INSTALL.md").read_text(encoding="utf-8")
    assert re.search(r"\| 연결·정리 \(1\) \| `academy-setup` \|", text), (
        "INSTALL.md 에 「연결·정리」 구분과 academy-setup 행이 없다"
    )
    read_row = re.search(r"^\| 읽기 전용 \((\d+)\) \|([^\n]*)$", text, re.M)
    assert read_row, "INSTALL.md 에 「읽기 전용」 행이 없다"
    assert "academy-setup" not in read_row.group(2), (
        "INSTALL.md 가 academy-setup 을 아직 「읽기 전용」에 두고 있다 — 행을 옮기는 스킬이다"
    )
    assert read_row.group(1) == "2", (
        f"INSTALL.md 「읽기 전용」 개수가 2 가 아니다: {read_row.group(1)}"
    )


def test_move_loop_reports_one_line_per_database(cleanup_section):
    """`LIMIT 100` 배치가 수십 번 도는 DB 도 있다 — 배치마다 보고하면 안 읽힌다."""
    assert "보고는 DB 하나당 한 줄로 묶는다" in cleanup_section, (
        "DB 하나당 한 줄로 묶어 보고하라는 규칙이 없다"
    )
    assert re.search(r"배치마다 보고하면[^\n]*읽지 않는다", cleanup_section), (
        "배치마다 보고하지 않는 이유가 적혀 있지 않다"
    )
    assert re.search(r"^> 출석부 <N>행 →", cleanup_section, re.M), (
        "DB 한 줄 보고의 예시가 없다"
    )


def test_setup_expects_fourteen_databases_without_master_table():
    text = "\n".join(
        p.read_text(encoding="utf-8") for p in (SKILLS / "academy-setup").rglob("*.md")
    )
    assert "과제 M" not in text, "academy-setup 에 없어진 `과제 M` 이 남아 있다"
    assert "15개" not in text, "academy-setup 이 아직 데이터베이스 15개를 찾는다"
    assert "14개" in text, "academy-setup 이 데이터베이스 14개를 찾는다고 적지 않는다"
