import subprocess
from bs4 import BeautifulSoup
import pytest
import requests

SITE_URL = "https://loic.lescoat.me/linedance-tracker/"

response = requests.get(SITE_URL)
assert response.status_code == 200

soup = BeautifulSoup(response.text, "html.parser")
links = soup.find_all("a", href=True)
youtube_link_expected_tuples = [
    (a["href"], a.get_text(strip=True))
    for a in links
    if "youtube.com/watch" in a["href"]
]


def get_video_title(url):
    """
    Returns title of youtube video
    """
    result = subprocess.run(
        ["uvx", "yt-dlp", "--get-title", url],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )
    return result.stdout.strip()


@pytest.mark.parametrize("link, expected", youtube_link_expected_tuples)
def test_link_valid(link: str, expected: str) -> None:
    title = get_video_title(link)
    print(title, link)
    assert expected in title
