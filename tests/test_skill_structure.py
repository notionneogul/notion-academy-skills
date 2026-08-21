import re

import pytest
import yaml

from helpers import REPO, skill_dirs

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def test_at_least_one_skill_exists():
    assert skill_dirs(), "skills/ 아래에 SKILL.md 를 가진 폴더가 하나도 없다"


@pytest.mark.parametrize("skill_dir", skill_dirs(), ids=lambda p: p.name)
def test_frontmatter_is_valid(skill_dir):
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    match = FRONTMATTER.match(text)
    assert match, f"{skill_dir.name}: SKILL.md 가 YAML frontmatter 로 시작하지 않는다"

    meta = yaml.safe_load(match.group(1))
    assert isinstance(meta, dict), f"{skill_dir.name}: frontmatter 가 매핑이 아니다"
    assert set(meta) == {"name", "description"}, (
        f"{skill_dir.name}: frontmatter 필드는 name, description 둘뿐이어야 한다 (현재 {sorted(meta)})"
    )
    assert meta["name"] == skill_dir.name, (
        f"{skill_dir.name}: name({meta['name']}) 이 폴더명과 다르다"
    )
    assert isinstance(meta["description"], str) and len(meta["description"]) >= 40, (
        f"{skill_dir.name}: description 이 40자 미만이다"
    )

    body = text[match.end():].strip()
    assert body, f"{skill_dir.name}: SKILL.md 본문이 비어 있다"


REQUIRED_DOCS = ["README.md", "INSTALL.md", "TROUBLESHOOTING.md"]


def test_distribution_docs_exist():
    missing = [name for name in REQUIRED_DOCS if not (REPO / name).exists()]
    assert not missing, f"배포 문서 누락: {missing}"


def test_readme_lists_every_skill():
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    missing = [d.name for d in skill_dirs() if d.name not in readme]
    assert not missing, f"README.md 에 언급되지 않은 스킬: {missing}"
