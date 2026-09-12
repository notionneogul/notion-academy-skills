from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILLS = REPO / "skills"


def skill_dirs() -> list[Path]:
    if not SKILLS.is_dir():
        return []
    return sorted(p for p in SKILLS.iterdir() if p.is_dir() and (p / "SKILL.md").exists())


WRITE_SKILLS = [
    "academy-attendance",
    "academy-counsel",
    "academy-enroll",
    "academy-exam",
    "academy-homework",
    "academy-message",
    "academy-template",
    "academy-tuition",
]

# 데이터베이스 스키마(속성)를 바꾸는 스킬은 이제 없다. 문자 양식은 노션 템플릿이 가진다.
SCHEMA_SKILLS: list[str] = []

# academy-report 는 행도 속성도 만들지 않고 페이지 본문에 파일을 붙인다.
CONTENT_SKILLS = ["academy-report"]
