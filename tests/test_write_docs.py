import re

import pytest

from helpers import CONTENT_SKILLS, SKILLS, WRITE_SKILLS

CORE_REFS = SKILLS / "academy-core" / "references"

GATE_STEPS = [
    "되물음",
    "사전 검증",
    "미리보기",
    "승인",
    "쓰기",
    "결과 보고",
    "남은 항목",
]

GATE_CHECK_PATTERNS = [
    r"\(가\).*수업일",
    r"\(나\).*중복",
    r"\(다\).*직전 과제",
    r"\(라\).*퇴원",
]

# write-gate.md 2단계 (라)는 domain-rules.md 「퇴원 정합」의 대상 DB 에 쓰는 스킬 전부의
# 공통 단계다. 출결·과제·시험은 (라)가 빠진 채로 릴리스된 적이 있어 회귀 테스트를 건다.
DROPOUT_CHECK_SKILLS = [
    "academy-attendance",
    "academy-homework",
    "academy-exam",
    "academy-tuition",
]

ROUTING_COMBOS = [
    "출결 + 진도·과제",
    "출결 + 시험 점수",
    "신규 등록 + 수강료",
    "상담 + 문자",
]

NAME_PATHS = [
    "학생 이름으로 지정",
    "클래스 전체 지정",
    "클래스 전체에서 일부만 예외",
]


def test_write_gate_covers_seven_steps():
    text = (CORE_REFS / "write-gate.md").read_text(encoding="utf-8")
    missing = [
        s for s in GATE_STEPS if not re.search(rf"^## .*{re.escape(s)}", text, re.M)
    ]
    assert not missing, f"write-gate.md 에 헤더로 없는 단계: {missing}"


def test_write_gate_covers_four_pre_checks():
    text = (CORE_REFS / "write-gate.md").read_text(encoding="utf-8")
    missing = [p for p in GATE_CHECK_PATTERNS if not re.search(p, text)]
    assert not missing, f"write-gate.md 에 빠진 사전 검증: {missing}"


def test_write_gate_pre_check_heading_counts_four():
    """제목이 '3종'이면 스킬들이 (라)를 목록 밖으로 읽는다 — 실제로 그렇게 빠진 적이 있다."""
    text = (CORE_REFS / "write-gate.md").read_text(encoding="utf-8")
    assert re.search(r"^## 2단계 — 사전 검증 4종", text, re.M), (
        "write-gate.md 2단계 제목이 '사전 검증 4종'이 아니다 — 항목 수와 제목이 어긋나면 안 된다"
    )


def test_write_gate_pre_checks_are_in_order():
    """(가)(나)(다)(라) 순서. 라벨 순서가 뒤섞이면 목록의 끝이 어디인지 읽히지 않는다."""
    text = (CORE_REFS / "write-gate.md").read_text(encoding="utf-8")
    positions = []
    for label in ["가", "나", "다", "라"]:
        m = re.search(rf"^\*\*\({label}\) ", text, re.M)
        assert m, f"write-gate.md 에 ({label}) 항목이 굵은 글머리로 없다"
        positions.append(m.start())
    assert positions == sorted(positions), (
        f"write-gate.md 의 사전 검증 항목이 (가)(나)(다)(라) 순이 아니다: {positions}"
    )


@pytest.mark.parametrize("skill", DROPOUT_CHECK_SKILLS)
def test_dropout_check_reaches_target_skills(skill):
    """퇴원 정합 대상 DB 에 쓰는 스킬은 (라)를 자기 「사전 검증」에 적어야 한다.

    열거형 서술이라 적혀 있지 않으면 '하지 않는다'로 읽힌다.
    """
    skill_md = SKILLS / skill / "SKILL.md"
    if not skill_md.exists():
        pytest.skip(f"{skill} 아직 구현 전")
    text = skill_md.read_text(encoding="utf-8")
    assert re.search(r"\(라\)", text), f"{skill} 이 사전 검증 (라)를 언급하지 않는다"
    assert "퇴원" in text, f"{skill} 에 '퇴원' 이라는 단어가 한 번도 나오지 않는다"
    assert "write-gate.md` 2단계 (라)" in text, (
        f"{skill} 이 (라)의 판정 기준으로 write-gate.md 2단계 (라)를 가리키지 않는다"
    )


def test_write_gate_states_approval_is_mandatory():
    text = (CORE_REFS / "write-gate.md").read_text(encoding="utf-8")
    assert "승인 없이" in text and "쓰지 않는다" in text, (
        "write-gate.md 가 승인 없이 쓰지 않는다는 것을 명시하지 않았다"
    )


def test_write_gate_covers_undo_scope():
    text = (CORE_REFS / "write-gate.md").read_text(encoding="utf-8")
    assert "이번 실행에서 자기가 만든" in text, (
        "write-gate.md 에 되돌리기 범위(이번 실행에서 자기가 만든 행) 서술이 없다"
    )
    assert "보관" in text, "write-gate.md 에 보관 페이지 절차가 없다"


def test_write_gate_defines_undo_split():
    """되돌리기 생성분/수정분 두 갈래가 core 규칙으로 있는지."""
    text = (CORE_REFS / "write-gate.md").read_text(encoding="utf-8")
    assert "생성분" in text and "수정분" in text, (
        "write-gate.md 6단계에 생성분/수정분 두 갈래가 없다"
    )
    assert re.search(r"빈 값으로.*되돌리지 않는다", text), (
        "write-gate.md 가 '원래 값이 있었으면 그 값으로 되돌린다' 는 규칙을 명시하지 않았다"
    )
    assert "그 원래 값으로" in text, (
        "write-gate.md 가 수정분을 원래 값으로 복원한다고 적지 않았다"
    )


def test_name_resolution_student_query_selects_withdrawal_date():
    """이름 해석의 학생 DB 조회가 퇴원 날짜를 SELECT 해야 (라) 판정 근거가 생긴다."""
    text = (CORE_REFS / "name-resolution.md").read_text(encoding="utf-8")
    m = re.search(r"SELECT[^\n]*FROM \"collection://<학생>\" WHERE \"이름\"", text)
    assert m, "name-resolution.md 에 학생 이름 조회 쿼리가 없다"
    assert '"date:퇴원 날짜:start"' in m.group(0), (
        f"학생 이름 조회의 SELECT 목록에 date:퇴원 날짜:start 가 없다: {m.group(0)}"
    )


def test_db_map_lists_write_blocked_properties_per_database():
    """쓰기 불가 속성의 권위 목록이 db-map.md 에 DB별로 한 번 있어야 한다."""
    text = (CORE_REFS / "db-map.md").read_text(encoding="utf-8")
    assert re.search(r"^## DB별 쓰기 불가 속성", text, re.M), (
        "db-map.md 에 「DB별 쓰기 불가 속성」 절이 없다"
    )
    section = text.split("## DB별 쓰기 불가 속성", 1)[1]
    databases = [
        "학생", "학생 과목별 페이지", "클래스", "출석부", "과제", "시험",
        "시험 카테고리", "수강료 납부", "납부 월", "재원생 상담", "신입생",
        "학교", "클래스 공지사항", "문자 양식", "과제 M",
    ]
    missing = [d for d in databases if f"| {d} |" not in section]
    assert not missing, f"「DB별 쓰기 불가 속성」 표에 빠진 DB: {missing}"
    # 실측(schema-map.md)에서 확인된 대표 항목이 실제로 실려 있는지.
    for prop in ["성적(%)", "평균", "미납 알림", "저번 과제", "평가 점수", "인원 수", "재원생 등록"]:
        assert prop in section, f"「DB별 쓰기 불가 속성」 표에 {prop} 이 없다"


def test_db_map_fingerprint_excludes_optional_claude_message_property():
    """`클로드 문자` 는 최초 스캔 이후 추가된 속성이라 지문표에 들어가면 안 된다.

    지문표에 있으면 구버전 복제본에서 12개 스킬 전부가 연결 단계에서 멈춘다.
    """
    text = (CORE_REFS / "db-map.md").read_text(encoding="utf-8")
    fingerprint = text.split("## 스키마 지문표", 1)[1].split("## ", 1)[0]
    assert "클로드 문자" not in fingerprint, (
        "db-map.md 지문표에 `클로드 문자` 가 남아 있다 — 구버전 사본이 전부 멈춘다"
    )
    message_md = SKILLS / "academy-message" / "SKILL.md"
    if message_md.exists():
        assert "클로드 문자" in message_md.read_text(encoding="utf-8"), (
            "academy-message 가 `클로드 문자` 확인을 자기 시작 시점으로 가져가지 않았다"
        )


def test_query_limits_documents_status_comparison():
    """status 를 표시 문자열로 비교하는 근거가 query-limits.md 에 있어야 한다."""
    text = (CORE_REFS / "query-limits.md").read_text(encoding="utf-8")
    assert "status" in text and "미납" in text, (
        "query-limits.md 가 status 속성의 비교 형태를 서술하지 않았다"
    )


def test_write_gate_forbids_uuid_in_preview():
    text = (CORE_REFS / "write-gate.md").read_text(encoding="utf-8")
    assert "uuid는 넣지 않는다" in text, (
        "write-gate.md 가 미리보기 표에 uuid를 넣지 않는다는 규칙을 명시하지 않았다"
    )


def test_write_gate_states_create_pages_batch_cap():
    text = (CORE_REFS / "write-gate.md").read_text(encoding="utf-8")
    assert "notion-create-pages" in text and "100건" in text
    assert re.search(r"notion-create-pages`?\s*도\s*한\s*번에\s*100건까지다", text), (
        "write-gate.md 가 notion-create-pages 의 배치 상한(100건)을 명시하지 않았다"
    )


def test_write_gate_preview_example_respects_thirty_row_rule():
    text = (CORE_REFS / "write-gate.md").read_text(encoding="utf-8")
    assert "30개를 넘으면" in text
    # 요약+예외 예시의 총 행수는 규칙이 말하는 상한(30)을 실제로 넘어야 한다.
    m = re.search(r"출석부에 (\d+)행을 만듭니다\. \d+명 출석", text)
    assert m, "write-gate.md 의 요약+예외 예시 행을 찾지 못했다"
    assert int(m.group(1)) > 30, (
        f"write-gate.md 의 요약+예외 예시가 30행 규칙 자체를 어긴다: {m.group(1)}행"
    )


def test_routing_lists_all_combinations():
    text = (CORE_REFS / "routing.md").read_text(encoding="utf-8")
    missing = [c for c in ROUTING_COMBOS if c not in text]
    assert not missing, f"routing.md 에 빠진 조합: {missing}"


def test_name_resolution_covers_three_paths():
    text = (CORE_REFS / "name-resolution.md").read_text(encoding="utf-8")
    missing = [
        p for p in NAME_PATHS if not re.search(rf"^## {re.escape(p)}", text, re.M)
    ]
    assert not missing, f"name-resolution.md 에 헤더로 없는 갈래: {missing}"


def test_name_resolution_warns_relation_target():
    text = (CORE_REFS / "name-resolution.md").read_text(encoding="utf-8")
    assert "학생 과목별 페이지" in text and "가장 자주 틀리는 지점" in text, (
        "name-resolution.md 가 relation 대상이 학생 과목별 페이지임을 밝히지 않았다"
    )


def test_name_resolution_uses_withdrawal_date_column():
    text = (CORE_REFS / "name-resolution.md").read_text(encoding="utf-8")
    assert "date:퇴원 날짜:start" in text, (
        "name-resolution.md 가 퇴원생 제외에 date:퇴원 날짜:start 컬럼명을 쓰지 않았다"
    )


def test_name_resolution_dropout_query_direction_is_correct():
    text = (CORE_REFS / "name-resolution.md").read_text(encoding="utf-8")
    assert "IS NOT NULL" in text, (
        "name-resolution.md 가 퇴원자를 학생 DB 에서 먼저 뽑는 쿼리를 쓰지 않았다"
    )
    assert "id IN (...)" not in text, (
        "name-resolution.md 에 방향이 틀린 relation 대조 쿼리(id IN (...))가 남아 있다"
    )


def test_name_resolution_describes_partial_class_match():
    text = (CORE_REFS / "name-resolution.md").read_text(encoding="utf-8")
    assert "부분 일치" in text, (
        "name-resolution.md 가 클래스명 부분 일치를 서술하지 않았다"
    )


def test_name_resolution_resolves_school_name_via_separate_query():
    text = (CORE_REFS / "name-resolution.md").read_text(encoding="utf-8")
    assert "collection://<학교>" in text and "학교명" in text, (
        "name-resolution.md 가 학교 uuid를 학교명으로 바꾸는 별도 조회를 서술하지 않았다"
    )


def test_write_safety_gates_row_creation_on_approval():
    text = (CORE_REFS / "write-safety.md").read_text(encoding="utf-8")
    assert not re.search(r"행 추가\s*\|\s*자율\s*\|", text), (
        "write-safety.md 의 '행 추가' 가 여전히 자율로 적혀 있다 — write-gate.md 의 승인 규칙과 충돌한다"
    )
    assert re.search(r"행 추가\s*\|.*write-gate\.md.*4단계", text), (
        "write-safety.md 의 '행 추가' 행이 write-gate.md 4단계(승인)를 가리키지 않는다"
    )


@pytest.mark.parametrize("skill", WRITE_SKILLS + CONTENT_SKILLS)
def test_write_skill_references_gate(skill):
    skill_md = SKILLS / skill / "SKILL.md"
    if not skill_md.exists():
        pytest.skip(f"{skill} 아직 구현 전")
    text = skill_md.read_text(encoding="utf-8")
    assert "../academy-core/references/write-gate.md" in text, (
        f"{skill} 이 write-gate.md 를 참조하지 않는다"
    )


@pytest.mark.parametrize("skill", WRITE_SKILLS + CONTENT_SKILLS)
def test_write_skill_has_examples(skill):
    skill_dir = SKILLS / skill
    if not (skill_dir / "SKILL.md").exists():
        pytest.skip(f"{skill} 아직 구현 전")
    assert (skill_dir / "references" / "examples.md").exists(), (
        f"{skill}/references/examples.md 가 없다"
    )


@pytest.mark.parametrize("skill", WRITE_SKILLS + CONTENT_SKILLS)
def test_write_skill_states_no_write_without_approval(skill):
    """'승인' 이라는 글자가 있는지가 아니라, 승인 규칙의 단일 소스를 가리키는지를 본다.

    승인의 판정 기준("명시적 긍정만 승인, 침묵은 승인 아님")은 write-gate.md 4단계
    한 곳에만 있다. 스킬이 그 단계를 가리키지 않으면 자기 나름의 기준을 쓰게 된다.
    """
    skill_md = SKILLS / skill / "SKILL.md"
    if not skill_md.exists():
        pytest.skip(f"{skill} 아직 구현 전")
    text = skill_md.read_text(encoding="utf-8")
    assert re.search(r"write-gate\.md`?\s*4(?:~\d)?단계", text), (
        f"{skill} 이 승인 규칙의 출처인 write-gate.md 4단계를 가리키지 않는다"
    )


@pytest.mark.parametrize("skill", WRITE_SKILLS)
def test_write_skill_points_at_core_undo_split(skill):
    """되돌리기의 생성분/수정분 두 갈래는 write-gate.md 6단계 한 곳에만 있다.

    스킬마다 다르게 답하면 같은 "방금 거 취소해줘" 에 결과가 갈린다.
    """
    skill_md = SKILLS / skill / "SKILL.md"
    if not skill_md.exists():
        pytest.skip(f"{skill} 아직 구현 전")
    text = skill_md.read_text(encoding="utf-8")
    assert "생성분" in text and "수정분" in text, (
        f"{skill} 이 되돌리기의 생성분·수정분 구분을 언급하지 않는다"
    )
    assert re.search(r"write-gate\.md`?\s*(?:4~)?6단계", text), (
        f"{skill} 이 되돌리기 규칙의 출처인 write-gate.md 6단계를 가리키지 않는다"
    )


def test_write_safety_allows_send_with_approval():
    text = (CORE_REFS / "write-safety.md").read_text(encoding="utf-8")
    assert "알림톡·문자 발송" in text, "write-safety.md 에 발송 경계 행이 없다"
    send_row = [ln for ln in text.splitlines() if "알림톡·문자 발송" in ln][0]
    assert "금지" not in send_row, (
        "발송이 아직 금지로 적혀 있다 — academy-send 가 생겼으므로 승인 경계로 바뀌어야 한다"
    )
    assert "승인" in send_row, "발송 경계에 승인 조건이 없다"


def test_message_link_tokens_are_composable_with_domain():
    text = (SKILLS / "academy-message" / "SKILL.md").read_text(encoding="utf-8")
    assert "구조적으로 채울 수 없다" not in text, (
        "링크를 구조적으로 불가능하다고 단정한 서술이 남아 있다 — 우피 도메인이 있으면 조립된다"
    )
    assert "oopy_domain" in text, (
        "academy-message 가 send.oopy_domain 을 언급하지 않는다"
    )


def test_message_examples_do_not_contradict_link_token_fix():
    """examples.md 가 SKILL.md 와 어긋나는 옛 "구조적으로 채울 수 없다" 서술을 남기지 않았는지 본다."""
    text = (SKILLS / "academy-message" / "references" / "examples.md").read_text(
        encoding="utf-8"
    )
    assert "구조적으로 채울 수 없다" not in text, (
        "examples.md 에 링크를 구조적으로 불가능하다고 단정한 옛 서술이 남아 있다 — "
        "SKILL.md 와 모순된다"
    )


def _content_skill_text(skill: str) -> str:
    return (SKILLS / skill / "SKILL.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("skill", CONTENT_SKILLS)
def test_content_skill_never_uses_replace_content(skill):
    """replace_content 로 페이지 본문을 통째로 바꾸면 학부모가 우피로 보는 다섯 콜아웃이 사라진다."""
    text = _content_skill_text(skill)
    assert re.search(r"`replace_content`\s*를\s*쓰지 않는다", text), (
        f"{skill} 이 replace_content 를 쓰지 않는다고 명시하지 않았다"
    )


@pytest.mark.parametrize("skill", CONTENT_SKILLS)
def test_content_skill_attach_command_is_fixed(skill):
    """붙이는 명령이 update_content/insert_content 로 고정돼 있는지 — command 를 짐작해 고르지 않는다."""
    text = _content_skill_text(skill)
    assert 'command: "update_content"' in text, (
        f"{skill} 이 update_content 갈래를 command 로 고정하지 않았다"
    )
    assert 'command: "insert_content"' in text, (
        f"{skill} 이 insert_content 갈래를 command 로 고정하지 않았다"
    )


@pytest.mark.parametrize("skill", CONTENT_SKILLS)
def test_content_skill_never_creates_pages(skill):
    """행을 만들지도 속성을 건드리지도 않는다 — notion-create-pages 가 SKILL.md 에 없어야 한다."""
    text = _content_skill_text(skill)
    assert "notion-create-pages" not in text, (
        f"{skill} SKILL.md 에 notion-create-pages 가 나온다 — 이 스킬은 행을 만들지 않는다"
    )


@pytest.mark.parametrize("skill", CONTENT_SKILLS)
def test_content_skill_does_not_send(skill):
    """붙이는 데까지만 하고, 발송은 다른 스킬(academy-send)의 일이다."""
    text = _content_skill_text(skill)
    assert re.search(r"\*\*보내지 않는다\.?\*\*", text), (
        f"{skill} 이 보내지 않는다는 것을 명시하지 않았다"
    )
