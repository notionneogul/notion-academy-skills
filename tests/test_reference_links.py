import re

from helpers import REPO, skill_dirs

CROSS_LINK = re.compile(r"(?<![\w./])(?:\.\./)+[A-Za-z0-9_-]+/references/[A-Za-z0-9_.-]+\.md")
OWN_LINK = re.compile(r"(?<![\w./])references/[A-Za-z0-9_.-]+\.md")


def test_cross_skill_reference_links_resolve():
    broken = []
    for skill_dir in skill_dirs():
        for md in skill_dir.rglob("*.md"):
            text = md.read_text(encoding="utf-8")
            for match in CROSS_LINK.finditer(text):
                target = (md.parent / match.group(0)).resolve()
                if not target.exists():
                    broken.append(f"{md.relative_to(REPO)} → {match.group(0)}")
    assert not broken, "끊어진 스킬 간 참조:\n" + "\n".join(broken)


def test_own_reference_links_resolve():
    broken = []
    for skill_dir in skill_dirs():
        skill_md = skill_dir / "SKILL.md"
        text = skill_md.read_text(encoding="utf-8")
        for match in OWN_LINK.finditer(text):
            target = (skill_dir / match.group(0)).resolve()
            if not target.exists():
                broken.append(f"{skill_md.relative_to(REPO)} → {match.group(0)}")
    assert not broken, "끊어진 자기 참조:\n" + "\n".join(broken)


def test_action_skills_reference_core():
    offenders = []
    for skill_dir in skill_dirs():
        if skill_dir.name == "academy-core":
            continue
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        if "../academy-core/references/" not in text:
            offenders.append(skill_dir.name)
    assert not offenders, f"academy-core 를 참조하지 않는 스킬: {offenders}"


def test_cross_link_pattern_handles_nested_paths():
    from test_reference_links import CROSS_LINK
    text = "규칙은 `../../academy-core/references/domain-rules.md` 에 있다"
    match = CROSS_LINK.search(text)
    assert match, "두 단계 상위 경로를 잡지 못한다"
    assert match.group(0) == "../../academy-core/references/domain-rules.md", (
        f"경로를 온전히 잡지 못했다: {match.group(0)}"
    )
