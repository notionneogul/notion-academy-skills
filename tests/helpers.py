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
    "academy-tuition",
]

# academy-template 은 행을 만들지 않고 데이터베이스 스키마(속성)만 바꾼다 — WRITE_SKILLS 가 아니다.
SCHEMA_SKILLS = ["academy-template"]

# academy-report 는 행도 속성도 만들지 않고 페이지 본문에 파일을 붙인다.
CONTENT_SKILLS = ["academy-report"]
