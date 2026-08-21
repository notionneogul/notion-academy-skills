import re

from helpers import REPO

CORE = REPO / "skills" / "academy-core" / "references"

DB_NAMES = [
    "학생", "학생 과목별 페이지", "클래스", "출석부", "과제",
    "시험", "시험 카테고리", "수강료 납부", "납부 월", "재원생 상담",
    "신입생", "학교", "클래스 공지사항", "문자 양식", "과제 M",
]

CONFIG_KEYS = ["template_version", "root_page", "connected_at", "databases"]


TABLE_ROW_HEAD = re.compile(r"^\|\s*([^|]+?)\s*\|", re.M)


def test_db_map_lists_all_fifteen_databases():
    """부분 문자열이 아니라 표 행의 첫 칸으로 매칭한다.

    부분 문자열이면 "과제" 가 "과제 안내" 에도 걸려, 정작 `| 과제 |` 행이
    없어도 통과해 버린다.
    """
    text = (CORE / "db-map.md").read_text(encoding="utf-8")
    row_heads = {m.group(1) for m in TABLE_ROW_HEAD.finditer(text)}
    missing = [name for name in DB_NAMES if name not in row_heads]
    assert not missing, f"db-map.md 지문표에 빠진 데이터베이스: {missing}"


def test_db_map_documents_config_schema():
    text = (CORE / "db-map.md").read_text(encoding="utf-8")
    missing = [key for key in CONFIG_KEYS if key not in text]
    assert not missing, f"db-map.md 에 빠진 config.json 키: {missing}"
    assert "~/.academy/config.json" in text, "config.json 경로가 명시되지 않았다"


RULE_KEYS = [
    "클래스 요일 정합", "저번 과제 방향", "보강 자동화", "점수 상한",
    "과목 페이지 필수", "퇴원 정합", "쓰기 불가 속성",
]

CHECK_CATEGORIES = ["필수", "되물음", "공란 허용"]

BOUNDARY_KEYS = [
    "행 추가", "자기가 만든 행 수정", "기존 행 수정", "보관 페이지로 이동",
    "스키마 변경", "발송", "휴지통",
]


def test_domain_rules_covers_all_seven():
    text = (CORE / "domain-rules.md").read_text(encoding="utf-8")
    missing = [key for key in RULE_KEYS if key not in text]
    assert not missing, f"domain-rules.md 에 빠진 규칙: {missing}"


def test_completeness_checks_has_three_categories():
    text = (CORE / "completeness-checks.md").read_text(encoding="utf-8")
    missing = [cat for cat in CHECK_CATEGORIES if cat not in text]
    assert not missing, f"completeness-checks.md 에 빠진 분류: {missing}"


def test_write_safety_covers_all_boundaries():
    text = (CORE / "write-safety.md").read_text(encoding="utf-8")
    missing = [key for key in BOUNDARY_KEYS if key not in text]
    assert not missing, f"write-safety.md 에 빠진 경계: {missing}"
