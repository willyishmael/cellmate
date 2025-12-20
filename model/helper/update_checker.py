from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Optional, Tuple

DEFAULT_REPO = "willyishmael/cellmate"
USER_AGENT = "CellmateUpdateChecker/1.0"


def _normalize_version(tag: str) -> str:
    """Strip a leading 'v'/'V' and whitespace from a tag."""
    return tag.strip().lstrip("vV")


def compare_versions(current: str, latest: str) -> int:
    """Compare semantic-ish versions without extra dependencies.

    Returns: -1 if current < latest, 0 if equal, 1 if current > latest.
    Non-numeric segments are compared lexicographically as fallback.
    """

    def to_tuple(v: str):
        parts = _normalize_version(v).split(".")
        normalized = []
        for p in parts:
            if p.isdigit():
                normalized.append(int(p))
            else:
                # Extract leading digits if present; keep remainder as string
                m = re.match(r"(\d+)(.*)", p)
                if m:
                    normalized.append(int(m.group(1)))
                    if m.group(2):
                        normalized.append(m.group(2))
                else:
                    normalized.append(p)
        return tuple(normalized)

    c = to_tuple(current)
    l = to_tuple(latest)
    return (c > l) - (c < l)


def fetch_latest_release(repo_full_name: Optional[str] = None) -> Tuple[str, str]:
    """Fetch the latest release tag and html_url from GitHub API.

    repo_full_name: "owner/repo". Uses env GITHUB_REPO or DEFAULT_REPO if not provided.
    Returns (tag_name, html_url).
    Raises RuntimeError on failure.
    """

    repo = repo_full_name or os.environ.get("GITHUB_REPO") or DEFAULT_REPO
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            if resp.status != 200:
                raise RuntimeError(f"GitHub API returned status {resp.status}")
            data = json.loads(resp.read().decode("utf-8"))
            tag = data.get("tag_name") or ""
            html_url = data.get("html_url") or data.get("url") or url
            if not tag:
                raise RuntimeError("No tag_name in latest release response")
            return _normalize_version(tag), html_url
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise RuntimeError(f"No releases found for repo '{repo}'. Create a GitHub release.") from e
        raise RuntimeError(f"GitHub API error {e.code}: {e.reason}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error: {e}") from e
    except (json.JSONDecodeError, KeyError) as e:
        raise RuntimeError("Failed to parse GitHub response") from e
