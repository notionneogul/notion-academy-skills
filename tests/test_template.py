import re

from helpers import SCHEMA_SKILLS, SKILLS, WRITE_SKILLS, skill_dirs

CORE_REFS = SKILLS / "academy-core" / "references"


def _write_safety() -> str:
    return (CORE_REFS / "write-safety.md").read_text(encoding="utf-8")


def test_schema_add_is_allowed_with_approval():
    text = _write_safety()
    assert "속성 추가" in text
    assert re.search(r"속성 추가.{0,80}승인", text), (
        "속성 추가가 승인 조건으로 적혀 있지 않다"
    )


def test_schema_delete_and_rename_stay_forbidden():
    text = _write_safety()
    assert re.search(r"속성 삭제.{0,120}(하지 않는다|금지)", text), (
        "속성 삭제를 하지 않는다는 경계가 없다"
    )
    assert re.search(r"이름 변경.{0,160}(하지 않는다|금지)", text), (
        "속성 이름 변경을 하지 않는다는 경계가 없다"
    )


def test_schema_delete_states_why_it_is_worse_than_sending():
    text = _write_safety()
    assert re.search(r"속성 삭제.{0,200}되돌릴", text, re.S), (
        "속성 삭제가 왜 되돌릴 수 없는지가 적혀 있지 않다"
    )


def test_db_map_excludes_alimtalk_properties_from_fingerprint():
    text = (CORE_REFS / "db-map.md").read_text(encoding="utf-8")
    section = text.split("### 지문표에 넣지 않는 속성", 1)[1].split("\n## ", 1)[0]
    assert "클로드출결" in section, (
        "알림톡 변수 속성군이 「지문표에 넣지 않는 속성」에 없다"
    )
    fingerprint = text.split("## 스키마 지문표", 1)[1].split("\n## ", 1)[0]
    assert "클로드출결" not in fingerprint, (
        "알림톡 변수 속성이 지문표에 들어갔다 — 구매자 사본이 전부 멈춘다"
    )


SCHEMA_STATEMENT = re.compile(r"ADD COLUMN|DROP COLUMN|RENAME COLUMN|notion-update-data-source")


def test_only_schema_skills_touch_the_schema():
    """스키마를 바꾸는 도구·구문이 `SCHEMA_SKILLS` 밖에서 나오면 빨간불이다.

    `helpers.SCHEMA_SKILLS` 가 값만 있고 아무 데서도 안 쓰이면 목록이 낡아도
    아무도 모른다. 여기서 강제한다 — 다른 스킬이 스키마 변경 구문을 쓰기
    시작하면 `write-safety.md` 「스키마 변경 — 속성 추가」 경계(「`academy-template`
    만 한다」)가 깨진 것이므로 그 자리에서 걸린다. 부정문("쓰지 않는다")도
    함께 걸리는 것은 `test_property_creation_shows_preview_and_asks_approval`
    과 같은 알려진 대가다 — 스키마 구문을 입에 올리는 스킬 자체를 하나로 묶어
    둔다.
    """
    offenders = {}
    for directory in skill_dirs():
        if directory.name in SCHEMA_SKILLS:
            continue
        docs = [directory / "SKILL.md", *sorted((directory / "references").glob("*.md"))]
        hits = sorted(
            {m.group(0) for doc in docs if doc.exists()
             for m in SCHEMA_STATEMENT.finditer(doc.read_text(encoding="utf-8"))}
        )
        if hits:
            offenders[directory.name] = hits
    assert not offenders, (
        f"SCHEMA_SKILLS({SCHEMA_SKILLS}) 밖에서 스키마 변경 구문이 나온다: {offenders}"
    )


def test_schema_skills_are_not_row_writing_skills():
    assert not set(SCHEMA_SKILLS) & set(WRITE_SKILLS), (
        "같은 스킬이 SCHEMA_SKILLS 와 WRITE_SKILLS 양쪽에 있다 — 경계가 갈리지 않는다"
    )
    for name in SCHEMA_SKILLS:
        assert (SKILLS / name / "SKILL.md").exists(), f"SCHEMA_SKILLS 의 {name} 이 없다"


def _template_skill() -> str:
    return (SKILLS / "academy-template" / "SKILL.md").read_text(encoding="utf-8")


def test_template_skill_exists_and_is_listed():
    assert (SKILLS / "academy-template" / "SKILL.md").exists()
    assert "academy-template" in [d.name for d in skill_dirs()]


def test_template_skill_never_drops_or_renames():
    text = _template_skill()
    assert "DROP COLUMN" in text, "지우지 않는다는 것을 무엇으로 안 지우는지 적어야 한다"
    assert re.search(r"DROP COLUMN.{0,200}(하지 않는다|쓰지 않는다)", text, re.S), (
        "DROP COLUMN 을 쓰지 않는다는 서술이 없다"
    )
    assert re.search(r"RENAME COLUMN.{0,200}(하지 않는다|쓰지 않는다)", text, re.S), (
        "RENAME COLUMN 을 쓰지 않는다는 서술이 없다"
    )


def test_template_skill_forbids_spaces_in_property_names():
    text = _template_skill()
    assert re.search(r"공백.{0,80}(쓰지 않는다|넣지 않는다|금지)", text), (
        "속성명에 공백을 쓰지 않는다는 규칙이 없다"
    )


def test_template_skill_checks_data_exists_before_proposing_item():
    text = _template_skill()
    assert re.search(r"데이터가.{0,60}(있는지|없으면)", text), (
        "항목을 제안하기 전에 데이터가 있는지 확인한다는 서술이 없다"
    )


def test_template_skill_does_not_register_to_solapi():
    text = _template_skill()
    assert re.search(r"등록하지 않는다|원장이 콘솔에서 등록", text), (
        "Solapi 등록을 스킬이 하지 않는다는 서술이 없다"
    )


def test_template_skill_records_fixed_length():
    text = _template_skill()
    assert "fixed_length" in text, "고정 본문 길이를 어디에 저장하는지가 없다"
    assert "1,000" in text or "1000" in text, "상한 1,000자가 적혀 있지 않다"


EXAMPLES = SKILLS / "academy-template" / "references" / "examples.md"
# 속성을 만드는 절인지만 가른다. 도구 이름 둘이면 충분하다 — 산문 동사 목록은
# 늘려도 새 표현에 뚫리기만 한다.
TOOL_CREATE = re.compile(r"ADD COLUMN|notion-update-data-source")
PREVIEW_TABLE = re.compile(r"\|\s*속성명\s*\|\s*타입\s*\|")
# 「만들까요?」·「만들어 드릴까요?」 둘 다 승인 요청이다.
APPROVAL = re.compile(r"만들[^\n]{0,10}(?:까요|할까요)")
PREVIEW_STEP = re.compile(r"^### \d+\. 미리보기 \+ 승인", re.M)
CREATE_STEP = re.compile(r"^### \d+\. 속성을 만든다", re.M)
NEXT_HEADING = re.compile(r"^#{2,4} ", re.M)


def test_property_creation_shows_preview_and_asks_approval():
    """속성을 만드는 절마다 미리보기 표와 승인 요청이 **있는지**를 본다.

    **순서를 기계로 보지 않는다.** 마크다운 산문에 정규식을 걸어 「승인이 생성보다
    앞선다」를 증명하려다 세 라운드 동안 우회 5건과 거짓 차단 3건이 났다 — 부정어
    한 마디로 탐지가 꺼지고, 재시도·결과 보고 같은 정상 서술이 막혔다. 순서는 사람
    리뷰가 본다. 여기서 보는 것은 존재뿐이고, 뚫으려면 표와 승인 요청을 지워야
    하는데 그것은 곧 문서가 실제로 나빠진 것이다. 첫 판 예시 2 가 정확히 그 상태로
    Critical 을 받았다 — 표도 승인 요청도 둘 다 없었다.

    `SKILL.md` 쪽은 셋을 본다 — 「미리보기 + 승인」 단계가 「속성을 만든다」 단계보다
    앞에 있는지(제목으로), 그 사이에 승인을 받는다고 적혀 있는지, 그리고 **생성 도구
    이름이 「속성을 만든다」 단계 안에만 나오는지.** 마지막 것이 절차 문서 쪽 우회를
    막는다 — 「급하면 바로 만든다」 같은 단계를 새로 달아 거기서 도구를 쏘면 걸린다.
    `examples.md` 처럼 단계마다 표를 요구하지는 않는다. 절차 문서에는 미리보기 표가
    한 번만 나오므로 그렇게 하면 정상 문서가 막힌다.

    **이 게이트는 제목·표 머리·승인 문구의 표면 표현에 매여 있다.** 단계 제목의
    `+` 기호, 「승인을 받는다」라는 문구, 표의 `속성명`·`타입` 머리, 승인 어간 「만들」
    이 그렇다. 그 표현을 바꾸면 이 테스트도 함께 고쳐야 한다 — 빨간불이 곧 문서가
    나빠졌다는 뜻은 아니다. 존재 검사 기법의 알려진 대가이고, 정상 산문을 막던 앞선
    라운드의 거짓 차단보다 낫다고 판단해 이 자리에 둔다.

    남은 구멍 둘도 같은 성격이다. **생성을 도구 이름으로만 알아본다 — 도구 이름 없이
    산문으로만 쓴 우회 단계는 통과한다.** 그리고 **도구로 한다와 도구로 하지 마라를
    구별하지 못한다 — 생성 단계 밖에서 그 도구 이름을 부정문으로 써도 빨간불이
    켜진다.**
    """
    text = EXAMPLES.read_text(encoding="utf-8")
    chunks = re.split(r"^## ", text, flags=re.M)
    creating = 0
    for index, chunk in enumerate(chunks):
        if not TOOL_CREATE.search(chunk):
            continue
        creating += 1
        title = "서문" if index == 0 else chunk.splitlines()[0]
        assert PREVIEW_TABLE.search(chunk), (
            f"「{title}」: 속성을 만드는데 만들 속성 표가 없다"
        )
        assert APPROVAL.search(chunk), (
            f"「{title}」: 속성을 만드는데 승인을 요청하는 문구가 없다"
        )
    assert creating >= 2, (
        f"속성을 만드는 예시가 {creating}개뿐이다. 둘 중 하나다 — 문서에서 미리보기·승인이 "
        f"빠졌거나, 생성 표현이 바뀌어 탐지({TOOL_CREATE.pattern})에서 빠졌다. 둘 다 확인해라"
    )

    skill = _template_skill()
    preview = PREVIEW_STEP.search(skill)
    create = CREATE_STEP.search(skill)
    assert preview, "SKILL.md 에 「미리보기 + 승인」 단계가 없다"
    assert create, "SKILL.md 에 「속성을 만든다」 단계가 없다"
    assert preview.start() < create.start(), (
        "SKILL.md 절차가 속성을 만든 뒤에 미리보기·승인을 둔다"
    )
    assert "승인을 받는다" in skill[preview.start() : create.start()], (
        "SKILL.md 「미리보기 + 승인」 단계가 승인을 받는다고 적지 않는다"
    )

    after = NEXT_HEADING.search(skill, create.end())
    step_end = after.start() if after else len(skill)
    outside = [
        skill[max(0, m.start() - 40) : m.start() + 40].replace("\n", " ")
        for m in TOOL_CREATE.finditer(skill)
        if not create.start() <= m.start() < step_end
    ]
    assert not outside, (
        "SKILL.md 가 「속성을 만든다」 단계 밖에서 생성 도구를 부른다 — "
        f"생성은 그 단계에서만 한다: {outside}"
    )


def _message_skill() -> str:
    return (SKILLS / "academy-message" / "SKILL.md").read_text(encoding="utf-8")


def test_message_mode_defaults_to_sms():
    text = _message_skill()
    assert re.search(r"알림톡.{0,120}(모드|경로)", text), "알림톡 모드 서술이 없다"
    assert re.search(r"애매하면.{0,80}문자", text), (
        "발화가 애매하면 문자 모드로 간다는 기본값이 없다"
    )


def test_alimtalk_mode_omits_headers():
    text = _message_skill()
    assert re.search(r"머리(글|표).{0,120}넣지 않는다", text), (
        "알림톡 모드에서 머리글을 넣지 않는다는 서술이 없다"
    )


def test_alimtalk_mode_stops_when_properties_missing():
    text = _message_skill()
    assert re.search(r"academy-template", text), (
        "속성이 없을 때 academy-template 을 안내한다는 서술이 없다"
    )
    assert re.search(r"속성이 없으면.{0,120}(만들지 않고|멈춘다)", text), (
        "속성이 없으면 만들지 않고 멈춘다는 서술이 없다"
    )


def test_alimtalk_mode_counts_assembled_length():
    text = _message_skill()
    assert "1,000" in text or "1000" in text
    # 브리핑 원안 `(조립|치환).{0,120}(글자|자)` 는 무관한 기존 문장(「토큰을 템플릿
    # 수식이 **치환**하는 **자**리다」)에 걸려 편집 전에도 통과했다 — 5단계의 조립
    # 서술이 통째로 지워져도 빨간불이 켜지지 않았다. 「조립」이 글자수를 세는 맥락에
    # 있는지로 좁힌다.
    assert re.search(r"조립[^\n]{0,80}글자수[^\n]{0,80}합계가 아니", text), (
        "조립한 본문 전체의 글자수를 센다(칸별 합계가 아니다)는 서술이 없다"
    )
    assert re.search(r"넘.{0,80}(줄이지 않는다|원장)", text), (
        "상한을 넘었을 때 임의로 줄이지 않는다는 서술이 없다"
    )
