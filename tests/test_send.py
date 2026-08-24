import re

from helpers import SKILLS

SEND = SKILLS / "academy-send"
SETUP = SEND / "references" / "setup.md"


def _skill():
    return (SEND / "SKILL.md").read_text(encoding="utf-8")


def test_skill_has_exactly_six_sections():
    heads = re.findall(r"^## (.+)$", _skill(), re.M)
    assert heads == ["시작 전에 읽는다", "언제 쓰나", "쓰는 속성", "절차", "주의", "예시"], heads


def test_never_sends_without_approval():
    text = _skill()
    assert "승인 없이" in text and "보내지 않는다" in text, (
        "승인 없이 보내지 않는다는 서술이 없다"
    )


def test_never_handles_the_api_key():
    text = _skill() + SETUP.read_text(encoding="utf-8")
    assert "직접 넣" in text, "원장이 키를 직접 넣는다는 안내가 없다"
    assert "출력하지 않는다" in text, "키를 화면에 출력하지 않는다는 서술이 없다"


def test_setup_covers_six_steps():
    text = SETUP.read_text(encoding="utf-8")
    for kw in ["API 키", "발신 프로필", "우피 도메인", "템플릿", "변수", "시험 발송"]:
        assert kw in text, f"세팅에 빠진 단계: {kw}"


def test_setup_test_send_goes_to_the_director_first():
    text = SETUP.read_text(encoding="utf-8")
    assert "원장 자신의 번호" in text, (
        "시험 발송을 원장 번호로 먼저 보낸다는 서술이 없다 — 학부모에게 먼저 보내면 안 된다"
    )


def test_config_spec_documents_send_key():
    text = (SKILLS / "academy-core" / "references" / "db-map.md").read_text(encoding="utf-8")
    assert "oopy_domain" in text and "sender_key" in text, "config 규격에 send 키가 없다"
    assert "선택 키" in text, "send 가 선택 키라는 서술이 없다"


def test_blocks_freeform_text_on_alimtalk():
    text = _skill()
    assert "클로드 문자" in text and "알림톡" in text
    assert "막는다" in text, (
        "클로드 문자를 알림톡으로 보내달라는 요청을 막는다는 서술이 없다"
    )


def test_never_falls_back_to_student_phone():
    text = _skill()
    assert "학생 전화번호" in text
    assert re.search(r"학생 전화번호.{0,40}(대체하지 않는다|쓰지 않는다)", text), (
        "학부모 번호가 비었을 때 학생 번호로 대체하지 않는다는 서술이 없다"
    )


def test_preview_shows_count_channel_sender_balance():
    text = _skill()
    for kw in ["건수", "채널", "발신번호", "잔액"]:
        assert kw in text, f"미리보기에 빠진 항목: {kw}"


def test_stops_when_balance_is_short():
    text = _skill()
    assert re.search(r"잔액.{0,60}보내지 않는다", text), (
        "잔액이 모자라면 보내지 않는다는 서술이 없다"
    )


def test_partial_failure_is_read_from_response():
    text = _skill()
    assert "registeredFailed" in text or "registered" in text, (
        "부분 실패를 응답의 어느 값으로 아는지 적혀 있지 않다"
    )


def test_incomplete_preview_is_not_an_approval_request():
    text = _skill()
    assert re.search(r"건수·채널·발신번호·잔액.{0,80}승인 요청이 아니다", text), (
        "네 줄 중 하나라도 못 채운 미리보기가 승인 요청이 아니라는 규칙이 없다"
    )
    assert "미리보기를 처음부터 다시 낸다" in text, (
        "빠진 값을 채운 뒤 미리보기를 처음부터 다시 낸다는 서술이 없다"
    )
    assert "승인은 완성된 미리보기 뒤에만 성립한다" in text, (
        "값을 채우는 과정에서 나온 긍정이 승인이 아니라는 판정이 없다"
    )


def test_schedule_is_the_same_call_with_a_date():
    text = _skill()
    assert "scheduledDate" in text, "예약 파라미터 이름이 없다"
    assert re.search(r"scheduledDate.{0,120}(넣지 않는다|생략)", text, re.S), (
        "즉시 발송일 때 scheduledDate 를 넣지 않는다는 서술이 없다"
    )


def test_cancel_uses_group_schedule_endpoint():
    text = _skill()
    assert "/schedule" in text and "DELETE" in text, "예약 취소 엔드포인트가 없다"


def test_past_time_is_refused():
    text = _skill()
    assert re.search(r"과거.{0,40}(막는다|보내지 않는다|거부)", text), (
        "과거 시각 예약을 막는다는 서술이 없다"
    )


def test_cancel_list_does_not_invent_the_target():
    text = _skill()
    assert re.search(r"(반 이름|학생 이름).{0,120}(Solapi|목록).{0,60}(나오지 않는다|모르는)", text, re.S), (
        "반 이름·학생 이름이 예약 목록에서 나오지 않는다는 서술이 없다"
    )
    assert "대상 정보 없음" in text, (
        "취소 목록에서 모르는 대상 자리를 무엇으로 남기는지가 없다"
    )
    assert re.search(r"학부모 전화번호.{0,40}대조", text), (
        "구별이 안 될 때 수신번호를 학부모 전화번호와 대조해 이름을 얻는 갈래가 없다"
    )
    assert re.search(r"(대상은|대상).{0,60}(실제로 얻었을 때만|얻었을 때만)", text), (
        "확인 문구의 대상 줄이 실제로 얻었을 때만 적는 것이라는 한정이 없다"
    )


def test_report_reads_group_messages():
    text = _skill()
    assert "그룹 안의 메시지" in text, (
        "건별 결과를 어느 경로로 읽는지가 setup.md 「호출 형식」 표 참조로 적혀 있지 않다"
    )
    assert re.search(r"건별|메시지별", text), "건별 결과를 읽는다는 서술이 없다"
    assert "/messages/v4/groups/" not in text, (
        "경로 리터럴이 SKILL.md 에 있다 — 경로는 setup.md 「호출 형식」 표에만 산다"
    )


def test_resend_targets_failures_only():
    text = _skill()
    assert re.search(r"성공한 건.{0,40}다시 보내지 않는다", text), (
        "성공분을 중복 발송하지 않는다는 서술이 없다"
    )


def _report_section():
    """SKILL.md 「절차」의 `### 결과 확인` 절만 잘라낸다."""
    parts = _skill().split("### 결과 확인", 1)
    assert len(parts) == 2, "SKILL.md 에 「결과 확인」 절이 없다"
    return parts[1].split("\n## ", 1)[0]


def test_sms_resend_checks_auto_fallback_first():
    text = _report_section()
    assert "disableSms" in text, (
        "실패분을 다시 보내기 전에 자동 문자 대체(disableSms) 를 보는 규칙이 없다"
    )
    assert re.search(r"어느 채널로 다시 보내든", text), (
        "중복 검사가 다시 보낼 채널이 아니라 앞 발송 설정에 걸려 있지 않다 — "
        "알림톡으로 다시 보내면 자동 대체가 또 나간다"
    )
    assert re.search(r"채널이 아니라 앞 발송의 `disableSms` 값", text), (
        "조건을 채널이 아니라 앞 발송의 disableSms 값에 건다는 서술이 없다"
    )
    assert re.search(r"`disableSms: true`.{0,60}자동 대체가 없", text), (
        "disableSms 가 true 였으면 자동 대체가 없었다는 갈래가 없다"
    )
    assert re.search(r"`disableSms: true`.{0,200}5단계 미리보기를 낸 뒤", text, re.S), (
        "true 갈래가 미리보기 없이 승인을 받는 것처럼 읽힌다"
    )
    assert re.search(r"`disableSms: false`.{0,80}이미 문자가 나갔을 수 있다", text), (
        "disableSms 가 false 였으면 이미 문자가 나갔을 수 있다는 갈래가 없다"
    )
    assert "확인받기 전에는 다시 보내지 않는다" in text, (
        "자동 대체가 이미 나갔는지 확인받기 전에는 다시 보내지 않는다는 판정이 없다"
    )
    assert re.search(r"「이미 갔다」고 하면 다시 보내지 않는다", text), (
        "원장이 이미 갔다고 답했을 때 멈춘다는 판정이 없다"
    )
    assert re.search(r"기본값이 `false` 라는 것을 근거로.{0,40}단정하지 않는다", text), (
        "disableSms 값을 모를 때 기본값으로 단정하지 않는다는 서술이 없다"
    )
    assert re.search(r"수신거부.{0,40}같은 채널로 다시 보내면 또 막힌다", text), (
        "사유마다 재발송이 말이 되는지 다르다는 서술이 없다"
    )


def test_example_walks_the_unknown_fallback_branch():
    """예시 8 은 대화가 바뀐 갈래다 — disableSms 값을 모르는 채로 물어야 한다."""
    text = (SEND / "references" / "examples.md").read_text(encoding="utf-8")
    body = text.split("## 8. ", 1)
    assert len(body) == 2, "examples.md 에 예시 8 이 없다"
    body = body[1]
    assert re.search(r"이 대화는 어제의 `disableSms` 값을 모른다", body), (
        "예시 8 이 대화가 바뀐 전제를 세워 놓고 disableSms 값을 아는 것처럼 진행한다"
    )
    assert re.search(r"머리글의 `false` 는 세팅의 기본값이지", body), (
        "예시 8 이 문서 머리글의 기본값을 그 발송의 값으로 단정하지 않는다는 못이 없다"
    )
    assert "그 설정이었는지를 제가 확정하지 못합니다" in body, (
        "예시 8 의 확인 물음이 모름 갈래(확정하지 못한다)를 밟지 않는다"
    )
    assert re.search(r"문자 왔대.{0,40}거기서 끝난다", body), (
        "예시 8 에 「이미 왔다」쪽에서 멈추는 갈래가 없다"
    )
