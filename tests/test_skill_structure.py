import re

import pytest
import yaml

from helpers import REPO, WRITE_SKILLS, skill_dirs

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


def test_readme_states_write_skills_need_approval():
    text = (REPO / "README.md").read_text(encoding="utf-8")
    assert "승인 없이" in text and "쓰지 않는다" in text, (
        "README 가 승인 없이 쓰지 않는다는 것을 명시하지 않았다"
    )


def test_readme_separates_read_setup_and_write_skills():
    """'쓰기' 라는 낱말이 어딘가 있는지가 아니라, 네 표가 실제로 나뉘어 있는지를 본다.

    `academy-setup` 은 샘플 정리에서 **행을 옮긴다.** 값만 고치는 `academy-doctor` 와
    성격이 달라 「읽기 전용」에 둘 수 없고, 행을 만들지 않으니 「쓰기」도 아니다.

    `academy-send` 는 반대쪽 끝이다 — 노션에 아무것도 쓰지 않지만 **되돌릴 수 없다.**
    노션에 쓴 것은 보관 페이지로 되돌아오지만 학부모에게 나간 문자는 회수할 수 없어,
    「쓰기」와 같은 표에 두면 위험도가 같아 보인다. 그래서 「발송」이 따로 있어야 한다.
    """
    text = (REPO / "README.md").read_text(encoding="utf-8")
    headings = ["### 읽기 전용", "### 연결·정리", "### 쓰기", "### 발송"]
    for heading in headings:
        assert re.search(rf"^{re.escape(heading)}\s*$", text, re.M), (
            f"README 에 「{heading}」 표 제목이 없다 — 네 분류가 표로 나뉘어 있어야 한다"
        )
    positions = [text.index(h) for h in headings]
    assert positions == sorted(positions), (
        f"README 의 네 분류 순서가 읽기 전용 → 연결·정리 → 쓰기 → 발송 이 아니다: {positions}"
    )
    read_section = text.split("### 읽기 전용", 1)[1].split("### 연결·정리", 1)[0]
    setup_section = text.split("### 연결·정리", 1)[1].split("### 쓰기", 1)[0]
    write_section = text.split("### 쓰기", 1)[1].split("### 발송", 1)[0]
    send_section = text.split("### 발송", 1)[1]

    assert "| `academy-setup` |" in setup_section, (
        "README 「연결·정리」 표에 academy-setup 행이 없다"
    )
    assert "| `academy-send` |" in send_section, (
        "README 「발송」 표에 academy-send 행이 없다"
    )
    assert "| `academy-send` |" not in write_section, (
        "README 「쓰기」 표에 academy-send 가 들어가 있다 — 되돌릴 수 없어 분류가 다르다"
    )
    for section, name in [(read_section, "읽기 전용"), (write_section, "쓰기")]:
        assert "| `academy-setup` |" not in section, (
            f"README 「{name}」 표에 academy-setup 이 들어가 있다 — 행을 옮기는 스킬이다"
        )
    for skill in ["academy-insight", "academy-doctor"]:
        assert f"| `{skill}` |" in read_section, f"README 「읽기 전용」 표에 {skill} 이 없다"
        assert f"| `{skill}` |" not in write_section, (
            f"README 「쓰기」 표에 읽기 전용 스킬 {skill} 이 들어가 있다"
        )
    for skill in WRITE_SKILLS:
        assert f"| `{skill}` |" in write_section, f"README 「쓰기」 표에 {skill} 이 없다"


def test_readme_states_message_does_not_send():
    """'발송' 이라는 낱말만 보면 '자동 발송합니다' 도 통과한다 — 부정문을 확인한다."""
    text = (REPO / "README.md").read_text(encoding="utf-8")
    assert "발송하지 않는다" in text, (
        "README 가 '발송하지 않는다' 를 명시하지 않았다"
    )
    assert "자동 발송합니다" not in text and "자동으로 발송한다" not in text


def test_readme_no_longer_claims_it_never_sends():
    text = (REPO / "README.md").read_text(encoding="utf-8")
    assert "자동으로 발송하지 않습니다" not in text, (
        "academy-send 가 생겼는데 README 가 아직 발송하지 않는다고 적는다"
    )
    assert "승인" in text and "발송" in text, (
        "README 가 발송에 승인이 필요하다는 것을 밝히지 않는다"
    )


def test_install_lists_thirteen_skill_folders():
    text = (REPO / "INSTALL.md").read_text(encoding="utf-8")
    assert "13개" in text, "INSTALL 의 스킬 개수가 갱신되지 않았다"
    assert "12개" not in text, "INSTALL 에 옛 개수가 남아 있다"


def test_readme_places_template_in_setup_group():
    text = (REPO / "README.md").read_text(encoding="utf-8")
    setup_section = text.split("### 연결·정리", 1)[1].split("### 쓰기", 1)[0]
    assert "| `academy-template` |" in setup_section, (
        "README 「연결·정리」 표에 academy-template 행이 없다"
    )


def test_install_matches_skill_folder_list():
    """INSTALL 이 안내하는 폴더 수·목록이 실제 스킬 폴더와 일치해야 한다.

    3단계에서 스킬이 4개에서 11개로 늘었을 때 INSTALL 만 4개로 남아 있었다.
    """
    text = (REPO / "INSTALL.md").read_text(encoding="utf-8")
    names = [d.name for d in skill_dirs()]
    missing = [n for n in names if n not in text]
    assert not missing, f"INSTALL.md 에 언급되지 않은 스킬 폴더: {missing}"
    assert f"총 {len(names)}개" in text, (
        f"INSTALL.md 가 폴더 수를 '총 {len(names)}개' 로 적지 않았다 (현재 스킬 {len(names)}개)"
    )


def test_install_offers_both_zip_and_terminal_paths():
    """초보자용 ZIP 경로가 먼저 나오고, 터미널 경로는 접혀서 뒤에 있어야 한다."""
    text = (REPO / "INSTALL.md").read_text(encoding="utf-8")
    assert "Download ZIP" in text, "INSTALL 에 ZIP 내려받기 경로가 없다"
    assert "git clone https://github.com/notionneogul/notion-academy-skills.git" in text, (
        "INSTALL 에 터미널(git clone) 경로가 없다"
    )
    assert "<details>" in text, "INSTALL 의 터미널 경로가 <details> 로 접혀 있지 않다"
    assert text.index("Download ZIP") < text.index("git clone"), (
        "INSTALL 이 터미널 경로를 ZIP 경로보다 먼저 보여준다 — 기본은 ZIP 이다"
    )


def test_install_covers_mac_and_windows_paths():
    """맥·윈도우 각각의 스킬 폴더 위치와 여는 법이 둘 다 있어야 한다."""
    text = (REPO / "INSTALL.md").read_text(encoding="utf-8")
    for anchor, why in [
        ("~/.claude/skills", "맥 스킬 폴더 경로"),
        (r"C:\Users\<사용자이름>\.claude\skills", "윈도우 스킬 폴더 경로"),
        ("Command + Shift + G", "맥에서 숨김 폴더로 이동하는 법"),
        (r"%USERPROFILE%\.claude", "윈도우 탐색기 주소창 경로"),
    ]:
        assert anchor in text, f"INSTALL 에 {why}({anchor}) 가 없다"


def test_readme_install_shows_zip_before_terminal():
    """README 의 설치 절도 INSTALL 과 같은 순서여야 한다 — ZIP 먼저, 터미널은 접어서."""
    text = (REPO / "README.md").read_text(encoding="utf-8")
    assert "INSTALL.md" in text, "README 가 INSTALL.md 로 안내하지 않는다"
    assert "Download ZIP" in text, "README 설치 절에 ZIP 경로가 없다"
    assert "<details>" in text, "README 의 터미널 경로가 <details> 로 접혀 있지 않다"
    assert text.index("Download ZIP") < text.index("git clone"), (
        "README 가 터미널 경로를 ZIP 경로보다 먼저 보여준다"
    )
