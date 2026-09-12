import re

from helpers import REPO

CORE = REPO / "skills" / "academy-core" / "references"

DB_NAMES = [
    "학생", "학생 과목별 페이지", "클래스", "출석부", "과제",
    "시험", "시험 카테고리", "수강료 납부", "납부 월", "재원생 상담",
    "신입생", "학교", "클래스 공지사항", "문자 양식",
]

REMOVED_NAMES = [
    "과제 M", "보강 날짜", "클로드 문자", "클로드출결", "클로드시험",
    "클로드과제", "클로드다음과제", "가변 문자", "비가변 문자", "문자 필터",
    "저번 과제", "문자 전송",
]

CONFIG_KEYS = ["template_version", "root_page", "connected_at", "databases"]


TABLE_ROW_HEAD = re.compile(r"^\|\s*([^|]+?)\s*\|", re.M)


def test_db_map_lists_all_fourteen_databases():
    """부분 문자열이 아니라 표 행의 첫 칸으로 매칭한다."""
    text = (CORE / "db-map.md").read_text(encoding="utf-8")
    row_heads = {m.group(1) for m in TABLE_ROW_HEAD.finditer(text)}
    missing = [name for name in DB_NAMES if name not in row_heads]
    assert not missing, f"db-map.md 지문표에 빠진 데이터베이스: {missing}"
    assert "14개" in text, "db-map.md 가 데이터베이스 개수를 14개로 적지 않는다"
    assert "15개" not in text, "db-map.md 에 옛 개수 15개가 남아 있다"


def test_db_map_has_no_removed_names():
    text = (CORE / "db-map.md").read_text(encoding="utf-8")
    left = [n for n in REMOVED_NAMES if n in text]
    assert not left, f"db-map.md 에 개편으로 없어진 이름이 남아 있다: {left}"


def test_db_map_documents_new_structure():
    text = (CORE / "db-map.md").read_text(encoding="utf-8")
    for needle in ["보강 예정일", "클로드총평", "## 문자 양식 변수", "띄어쓰기", "학생 1명"]:
        assert needle in text, f"db-map.md 에 `{needle}` 이 없다"
    assert "send" not in text and "solapi" not in text.lower(), (
        "db-map.md 설정 규격에 발송(send) 키가 남아 있다"
    )


def test_db_map_documents_config_schema():
    text = (CORE / "db-map.md").read_text(encoding="utf-8")
    missing = [key for key in CONFIG_KEYS if key not in text]
    assert not missing, f"db-map.md 에 빠진 config.json 키: {missing}"
    assert "~/.academy/config.json" in text, "config.json 경로가 명시되지 않았다"


RULE_KEYS = [
    "클래스 요일 정합", "과제 평가 대상", "보강", "점수 상한",
    "과목 페이지 필수", "퇴원 정합", "쓰기 불가 속성", "발송",
]

CHECK_CATEGORIES = ["필수", "되물음", "공란 허용"]

BOUNDARY_KEYS = [
    "행 추가", "자기가 만든 행 수정", "기존 행 수정", "보관 페이지로 이동",
    "스키마 변경", "발송", "휴지통",
]


def test_domain_rules_covers_all_rules():
    text = (CORE / "domain-rules.md").read_text(encoding="utf-8")
    missing = [key for key in RULE_KEYS if key not in text]
    assert not missing, f"domain-rules.md 에 빠진 규칙: {missing}"
    assert "저번 과제" not in text and "직전 과제" not in text, (
        "domain-rules.md 에 없어진 「저번 과제 방향」 규칙이 남아 있다"
    )


def test_makeup_rule_creates_row_then_checks():
    text = (CORE / "domain-rules.md").read_text(encoding="utf-8")
    for needle in ["보강 예정일", "새 행", "보강완료", "출결상태", "Make"]:
        assert needle in text, f"domain-rules.md 보강 규칙에 `{needle}` 이 없다"
    seg = text[text.index("새 행"):]
    assert "보강완료" in seg, "보강 규칙이 「새 행 생성 → 원래 행 보강완료 체크」 순서로 적혀 있지 않다"


def test_no_skill_sends():
    text = (CORE / "domain-rules.md").read_text(encoding="utf-8")
    assert "발송하지 않는다" in text, "domain-rules.md 가 「스킬은 발송하지 않는다」를 적지 않는다"


def test_completeness_checks_has_three_categories():
    text = (CORE / "completeness-checks.md").read_text(encoding="utf-8")
    missing = [cat for cat in CHECK_CATEGORIES if cat not in text]
    assert not missing, f"completeness-checks.md 에 빠진 분류: {missing}"


def test_write_safety_covers_all_boundaries():
    text = (CORE / "write-safety.md").read_text(encoding="utf-8")
    missing = [key for key in BOUNDARY_KEYS if key not in text]
    assert not missing, f"write-safety.md 에 빠진 경계: {missing}"
