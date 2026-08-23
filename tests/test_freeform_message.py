"""academy-message 의 두 번째 입력 경로(원장이 준 예시로 형태를 얻는 경로) 회귀 테스트.

경로 1(노션 `문자 양식`)은 이미 있던 것이고, 경로 2는 형태 출처만 다르고
3~6단계를 경로 1과 공유한다. 이 파일은 경로 2가 문서에서 사라지거나
핵심 규칙(숫자는 모양이다 / 저장은 노션이 아니라 설정 파일)이 빠지는 것을 막는다.
"""

import re

import pytest

from helpers import SKILLS

MESSAGE = SKILLS / "academy-message"
SKILL_MD = MESSAGE / "SKILL.md"
EXAMPLES_MD = MESSAGE / "references" / "examples.md"


@pytest.fixture(scope="module")
def skill_text() -> str:
    return SKILL_MD.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def examples_text() -> str:
    return EXAMPLES_MD.read_text(encoding="utf-8")


def _section(text: str, n: int) -> str:
    """examples.md 의 `## <n>.` 절 본문을 잘라낸다."""
    match = re.search(rf"^## {n}\. .*?(?=^## )", text, re.M | re.S)
    assert match, f"예시 {n} 절을 찾지 못했다"
    return match.group(0)


def test_procedure_still_has_exactly_six_steps(skill_text):
    """경로가 둘로 늘어도 절은 여섯이다 — 새 절을 만들어 갈래를 벌리지 않았는지 본다."""
    steps = re.findall(r"^### (\d)\. ", skill_text, re.M)
    assert steps == ["1", "2", "3", "4", "5", "6"], f"절차 절이 여섯이 아니다: {steps}"


def test_step_two_names_both_form_sources(skill_text):
    """2단계가 형태 출처 두 갈래를 모두 이름 붙여 갖고 있는지."""
    step_two = re.search(r"^### 2\. .*?(?=^### 3\. )", skill_text, re.M | re.S)
    assert step_two, "2단계 절을 찾지 못했다"
    body = step_two.group(0)

    for anchor in [
        "경로 1",
        "경로 2",
        "노션 `문자 양식`",
        "원장이 준 예시",
    ]:
        assert anchor in body, f"2단계에 없는 형태 출처 표기: {anchor}"

    assert "사용" in body and "켜진" in body, (
        "경로 1의 선택 기준(`사용` 이 켜진 행)이 2단계에서 사라졌다"
    )


def test_step_two_states_later_steps_are_shared(skill_text):
    """경로 2가 3~6단계를 복제하지 않고 공유한다는 서술이 있는지."""
    step_two = re.search(r"^### 2\. .*?(?=^### 3\. )", skill_text, re.M | re.S)
    body = step_two.group(0)
    assert re.search(r"3~6단계.*공유한다", body), (
        "3~6단계를 두 경로가 공유한다는 서술이 2단계에 없다"
    )


ROUTE_DECISION_ANCHORS = [
    # 1. 붙여넣으면 경로 2
    r"완성된 문자 텍스트를 붙여넣으면.*경로 2",
    # 2. 저장된 이름을 부르면 경로 2 (설정 파일에서 꺼낸다)
    r"저장된 이름을 부르면.*경로 2",
    # 3. 아무 말 없으면 경로 1
    r"아무 말이 없으면.*경로 1",
    # 4. 둘 다면 방금 준 것이 이긴다
    r"둘 다 해당하면.*방금 준 것이 이긴다",
]


def test_route_decision_has_four_rules(skill_text):
    missing = [p for p in ROUTE_DECISION_ANCHORS if not re.search(p, skill_text)]
    assert not missing, f"경로 판정 규칙이 빠졌다: {missing}"


def test_pasted_numbers_are_shape_not_value(skill_text):
    """이 경로에서 가장 틀리기 쉬운 지점 — 예시의 숫자를 전원에게 복사하지 않는다."""
    assert "모양이지 값이 아니다" in skill_text, (
        "예시의 숫자·이름이 모양이지 값이 아니라는 규칙이 SKILL.md 에 없다"
    )
    assert re.search(r"각 학생의 실제 조회 결과", skill_text), (
        "예시 자리에 각 학생의 실제 데이터를 넣는다는 서술이 없다"
    )
    # 파일 아무 데나 "55%" 가 있는지가 아니라, 금지 사례 문장 안에 있는지를 본다.
    assert re.search(r"55%.?를 예시로 줬다고 전원에게 55%를 쓰면 안 된다", skill_text), (
        "전원에게 같은 숫자를 쓰면 안 된다는 것을 보여주는 구체 사례 문장이 없다"
    )
    assert re.search(r"쓰기 직전에 한 번 더", skill_text), (
        "잔류 확인이 쓰기 직전에도 걸린다는 서술이 2단계에 없다"
    )


def test_items_absent_from_pasted_example_are_not_added(skill_text):
    assert "예시에 없는 항목은 넣지 않는다" in skill_text, (
        "예시에 없는 항목을 끼워 넣지 않는다는 규칙이 없다"
    )
    assert re.search(r"예시에 있는데.*데이터가 없으면", skill_text), (
        "예시에 있으나 데이터가 없는 항목을 비우고 보고한다는 규칙이 없다"
    )


def test_saving_goes_to_config_file_not_notion(skill_text):
    assert "~/.academy/config.json" in skill_text, (
        "저장 위치(`~/.academy/config.json`)가 SKILL.md 에 없다"
    )
    assert "message_formats" in skill_text, (
        "설정 파일의 저장 키(`message_formats`)가 SKILL.md 에 없다"
    )
    assert re.search(r"노션 `문자 양식` DB ?에 저장하지 않는다", skill_text), (
        "자유 양식을 노션 `문자 양식` DB 에 넣지 않는다는 금지가 없다"
    )


def test_saving_explains_why_notion_template_db_would_break(skill_text):
    """이유까지 적혀 있어야 한다 — 토큰을 치환하는 수식 경로가 깨지기 때문이다."""
    reason = re.search(r"노션 `문자 양식` DB ?에 저장하지 않는다.*?\n", skill_text, re.S)
    assert reason, "금지 문장을 찾지 못했다"
    block = reason.group(0)
    for anchor in ["#{최근성적}", "수식", "깨진다"]:
        assert anchor in block, f"저장 금지의 이유에 빠진 말: {anchor}"


def test_saving_is_opt_in_and_names_the_local_only_caveat(skill_text):
    assert "저장해 달라고 할 때만 저장한다" in skill_text, (
        "원장이 요청할 때만 저장한다는 규칙이 없다"
    )
    assert "어떤 이름으로 저장할지 묻는다" in skill_text, (
        "저장 전에 이름을 묻는다는 규칙이 없다"
    )
    assert "다른 컴퓨터에서는 다시 붙여넣으셔야 합니다" in skill_text, (
        "노션에 들어가지 않는다는 안내 문구가 없다"
    )
    assert "같은 이름이 이미 있으면 덮어쓸지 묻는다" in skill_text, (
        "같은 이름 덮어쓰기 확인 규칙이 없다"
    )


def test_examples_cover_three_route_two_situations(examples_text):
    headings = re.findall(r"^## (\d)\. (.+)$", examples_text, re.M)
    numbers = [n for n, _ in headings]
    assert numbers == [str(i) for i in range(1, 9)], (
        f"예시 번호가 1~8로 이어지지 않는다: {numbers}"
    )

    titles = " / ".join(t for _, t in headings)
    for anchor in ["예시 붙여넣기", "저장 요청", "저장된 이름 호출"]:
        assert anchor in titles, f"경로 2 예시가 빠졌다: {anchor}"


def test_examples_declare_independence_of_new_cases(examples_text):
    """새 예시가 독립인지 이어지는지 밝혔는지."""
    ex7 = re.search(r"^## 7\. .*?(?=^## 8\. )", examples_text, re.M | re.S).group(0)
    assert "예시 6에 이어진다" in ex7, "예시 7이 예시 6에 이어진다는 표시가 없다"

    ex6 = re.search(r"^## 6\. .*?(?=^## 7\. )", examples_text, re.M | re.S).group(0)
    assert "독립 상황이다" in ex6, "예시 6의 독립 여부 표시가 없다"

    ex8 = re.search(r"^## 8\. .*?(?=^## 참고)", examples_text, re.M | re.S).group(0)
    assert "대화 자체는 새로 시작한다" in ex8, "예시 8의 독립 여부 표시가 없다"


def test_paste_example_shows_numbers_are_not_copied(examples_text):
    """예시 6의 완성본 네 통에 예시의 숫자가 복사되지 않았음이 눈에 보여야 한다."""
    ex6 = re.search(r"^## 6\. .*?(?=^## 7\. )", examples_text, re.M | re.S).group(0)
    preview = re.search(r"```\n원장님이 주신 예시.*?```", ex6, re.S)
    assert preview, "예시 6의 미리보기 블록을 찾지 못했다"
    body = preview.group(0)

    assert body.count("55%") == 1, (
        f"예시의 숫자(55%)가 미리보기에 {body.count('55%')}번 나온다 — 한 학생 몫이어야 한다"
    )
    for pct in ["97.5%", "87.5%", "77.5%"]:
        assert pct in body, f"다른 학생의 실제 값이 미리보기에 없다: {pct}"

    assert "재시험 일정을 조율하고" in body
    assert body.count("재시험 일정을 조율하고") == 1, (
        "예시에 적힌 피드백 문장이 다른 학생에게도 복사됐다"
    )


def test_saved_format_example_reports_empty_item(examples_text):
    """예시 8 — 저장된 양식에 있는 항목의 데이터가 없으면 비우고 보고한다."""
    ex8 = _section(examples_text, 8)
    assert "message_formats" in ex8, "저장된 이름을 어디서 꺼내는지 예시 8에 없다"
    assert re.search(r"채점이 아직 비어 있어.*비웠습니다", ex8), (
        "데이터가 없는 항목을 비우고 결과 보고에 밝히는 흐름이 예시 8에 없다"
    )


def test_saved_format_example_shows_number_substitution(examples_text):
    """저장본 안에 남의 실제 점수가 남아 있다 — 그것이 갈아 끼워지는 장면이 있어야 한다."""
    ex8 = _section(examples_text, 8)
    assert "저장본 안에는" in ex8 and "그대로 남아 있다" in ex8, (
        "저장본에 남의 점수가 남아 있다는 경고가 예시 8에 없다"
    )

    preview = re.search(r"```\n저장해 두신.*?```", ex8, re.S)
    assert preview, "예시 8의 미리보기 블록을 찾지 못했다"
    body = preview.group(0)

    assert "55%" not in body, "저장본에 있던 박시우의 55%가 완성본에 남아 있다"
    assert "재시험 일정을 조율" not in body, (
        "저장본에 있던 박시우의 피드백 문장이 완성본에 남아 있다"
    )
    for pct in ["60%", "83.3%", "90%", "96.7%", "93.3%"]:
        assert pct in body, f"학생별 실제 값이 완성본에 없다: {pct}"


def test_saved_format_example_flags_coincidental_number(examples_text):
    """우연히 같은 숫자가 나왔을 때 잔류와 구별하라는 서술."""
    ex8 = _section(examples_text, 8)
    assert "우연히 같다" in ex8 and "저장본의 잔류인지 구별" in ex8, (
        "같은 숫자가 조회 결과인지 저장본 잔류인지 구별하라는 서술이 예시 8에 없다"
    )


HOMEWORK_GRADE_BAD = re.compile(r"과제는 8/\d\d 분까지 제출했고 평가는")


def test_new_examples_attribute_homework_grade_to_prior_row(examples_text):
    """「저번 과제 방향」 — 과제 행의 `평가` 는 직전 행 과제의 채점이다."""
    for n in (6, 8):
        section = _section(examples_text, n)
        assert not HOMEWORK_GRADE_BAD.search(section), (
            f"예시 {n} 이 이번 주 과제에 그 주의 평가를 붙였다 — 「저번 과제 방향」 위반"
        )
        assert "저번 과제 방향" in section, (
            f"예시 {n} 이 「저번 과제 방향」을 근거로 대지 않았다"
        )
        assert re.search(r"직전 8/\d\d 과제 채점", section), (
            f"예시 {n} 의 과제 문장이 채점 대상 날짜를 명시하지 않았다"
        )


def test_examples_do_not_claim_submission_status(examples_text):
    """`과제` DB 에는 제출 여부 속성이 없다 — 학부모 문자에 단정하지 않는다."""
    assert "제출 기록이 없" not in examples_text, (
        "조회할 수 없는 제출 여부를 문자 본문에서 단정하고 있다"
    )
    ex8 = _section(examples_text, 8)
    assert "제출 여부를 담는 속성이 없다" in ex8, (
        "`과제` DB 에 제출 여부 속성이 없다는 근거가 예시 8에 없다"
    )


# ---------------------------------------------------------------------------
# 다리가 실제로 닿는지 — 경로 2가 경로 1 전용 서술에 걸려 넘어지지 않아야 한다
# ---------------------------------------------------------------------------


def test_bridge_covers_notes_section_too(skill_text):
    assert re.search(r"3~6단계와 「주의」", skill_text), (
        "다리 문장이 「주의」까지 덮지 않는다 — 경로 1 전용 규칙이 경로 2에 새어 들어간다"
    )


def test_active_template_wording_after_step_two_is_qualified(skill_text):
    """3단계 이후에 남은 "활성 양식" 은 전부 경로가 명시돼 있어야 한다."""
    tail = skill_text[skill_text.index("### 3. ") :]
    lines = [ln for ln in tail.split("\n") if "활성 양식" in ln]
    assert len(lines) <= 3, (
        f"3단계 이후 '활성 양식' 표현이 {len(lines)}줄로 늘었다 — 경로 2에서 읽히지 않는 서술이다"
    )
    unqualified = [
        ln for ln in lines if "경로 1" not in ln and "활성 양식이든" not in ln
    ]
    assert not unqualified, (
        "경로를 밝히지 않은 '활성 양식' 서술: " + " / ".join(ln[:50] for ln in unqualified)
    )


def test_route_two_does_not_query_template_db(skill_text, examples_text):
    assert "경로 2에서는 노션 `문자 양식` DB 를 조회하지 않는다" in skill_text, (
        "경로 2가 `문자 양식` DB 를 조회하지 않는다는 규칙이 SKILL.md 에 없다"
    )
    assert "노션 `문자 양식` DB 는 조회하지 않는다" in _section(examples_text, 8), (
        "예시 8이 `문자 양식` DB 를 조회하지 않는다는 것을 보이지 않는다"
    )


def test_pasted_tokens_fall_back_to_route_one_handling(skill_text):
    assert re.search(r"토큰이 들어 있으면.*경로 1과 똑같이 다룬다", skill_text, re.S), (
        "노션 양식 본문을 복사해 붙여넣어 `#{}` 토큰이 섞인 경우의 지침이 없다"
    )


def test_unknown_name_falls_through_to_route_one_rules(skill_text):
    assert "거기서 찾았으면 그때부터는 경로 1이고" in skill_text, (
        "부른 이름을 노션 양식에서 찾은 뒤 경로 1 규칙이 이어진다는 서술이 없다"
    )
    assert "조용히 꺼진 양식을 쓰지 않는다" in skill_text, (
        "`사용` 이 꺼진 양식을 조용히 쓰지 않는다는 규칙이 없다"
    )


def test_counsel_rule_is_conditional_not_absolute(skill_text):
    assert "형태 출처에 상담 항목이 없으면" in skill_text, (
        "상담 규칙이 무조건 단정으로 남아 있다 — 원장 예시가 상담을 담는 경우가 있다"
    )


def test_write_step_has_a_route_two_gate(skill_text):
    step_six = skill_text[skill_text.index("### 6. ") : skill_text.index("## 주의")]
    assert "경로 1이었으면" in step_six and "경로 2였으면" in step_six, (
        "6단계의 쓰기 직전 점검이 경로별로 갈리지 않는다"
    )
    assert re.search(r"숫자·이름·피드백 문장이 다른 학생의 완성본에 남아 있지 않은지", step_six), (
        "경로 2의 쓰기 직전 잔류 확인이 6단계에 없다 — 경로 2에서 마지막 관문이 비어 있다"
    )


def test_config_write_preserves_existing_keys_and_points_at_write_safety(skill_text):
    assert "`databases`·`root_page` 등 기존 키는 그대로 둔다" in skill_text, (
        "설정 파일의 기존 키를 보존한다는 규칙이 없다"
    )
    assert "write-safety.md" in skill_text, (
        "로컬 설정 파일 쓰기의 경계로 write-safety.md 를 가리키지 않는다"
    )


def test_homework_grade_rule_lives_in_the_skill_not_only_examples(skill_text):
    assert "과제 평가는 채점 대상을 명시해 쓴다" in skill_text, (
        "채점 대상을 명시하라는 규칙이 SKILL.md 경로 2에 없다"
    )
    assert "저번 과제 방향" in skill_text, (
        "SKILL.md 경로 2가 「저번 과제 방향」을 근거로 대지 않는다"
    )
