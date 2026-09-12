"""PRO X 개편으로 없어진 이름이 저장소 문서 어디에도 남지 않게 못 박는다.

개편 전 구조를 가리키는 문장 하나가 남으면, 그 문장을 읽은 스킬이 없는 속성에 쓰려 하거나
없는 DB 를 찾다 멈춘다. 스킬별 테스트가 놓친 자리를 여기서 한 번에 잡는다.
"""

from helpers import REPO

REMOVED = [
    "과제 M", "보강 날짜", "클로드 문자", "클로드출결", "클로드시험",
    "클로드과제", "클로드다음과제", "가변 문자", "비가변 문자", "문자 필터",
    "저번과제", "최근과제안내", "academy-send", "솔라피", "Solapi",
    "은퇴한 발송 스킬", "15개", "저번 과제", "직전 과제", "직전 행 과제", "한 행 앞의 과제",
]


def _docs():
    for p in sorted(REPO.rglob("*.md")):
        yield p, p.read_text(encoding="utf-8")


def test_no_removed_names_anywhere():
    hits = {}
    for p, text in _docs():
        found = [n for n in REMOVED if n in text]
        if found:
            hits[str(p.relative_to(REPO))] = found
    assert not hits, f"개편으로 없어진 이름이 남아 있다: {hits}"


def test_doctor_checks_makeup_completed_without_makeup_row():
    text = (REPO / "skills" / "academy-doctor" / "references" / "checks.md").read_text(encoding="utf-8")
    assert "보강 예정일" in text, "doctor 검사가 `보강 예정일` 을 쓰지 않는다"
    assert "보강 행" in text, (
        "「보강 행 없이 보강완료만 켜진 결석 행」 검사가 없다 — 알림톡이 안 나갔을 행이다"
    )


def test_insight_uses_new_makeup_date():
    text = (REPO / "skills" / "academy-insight" / "SKILL.md").read_text(encoding="utf-8")
    assert "date:보강 예정일:start" in text, "insight 보강 조회가 `보강 예정일` 을 쓰지 않는다"


def test_report_attaches_to_monthly_report_callout():
    text = (REPO / "skills" / "academy-report" / "SKILL.md").read_text(encoding="utf-8")
    assert "월말 리포트" in text, "report 가 「월말 리포트」 콜아웃을 가리키지 않는다"
