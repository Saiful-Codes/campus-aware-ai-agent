import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.api.chat import _rank_urls


def test_rank_urls_prefers_latrobe_over_other_domains():
    urls = [
        "https://example.com/policies",
        "https://www.latrobe.edu.au/students",
    ]
    ranked = _rank_urls(urls)
    assert ranked[0] == "https://www.latrobe.edu.au/students"


def test_rank_urls_prefers_longer_path_among_latrobe_urls():
    urls = [
        "https://www.latrobe.edu.au/",
        "https://www.latrobe.edu.au/students/colleges/glenn",
        "https://www.latrobe.edu.au/students",
    ]
    ranked = _rank_urls(urls)
    assert ranked[0] == "https://www.latrobe.edu.au/students/colleges/glenn"


def test_rank_urls_prefers_longer_path_among_non_latrobe_urls():
    urls = [
        "https://example.com/",
        "https://example.com/some/deep/path",
    ]
    ranked = _rank_urls(urls)
    assert ranked[0] == "https://example.com/some/deep/path"


def test_rank_urls_stable_on_ties():
    urls = [
        "https://a.example.com/x",
        "https://b.example.com/x",
        "https://c.example.com/x",
    ]
    ranked = _rank_urls(urls)
    # Same domain class (non-latrobe) and same path length — original order preserved.
    assert ranked == urls


def test_rank_urls_empty_input_returns_empty_list():
    assert _rank_urls([]) == []
