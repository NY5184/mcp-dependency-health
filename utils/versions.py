from __future__ import annotations
import re
from packaging.version import Version, InvalidVersion
from packaging.specifiers import SpecifierSet, InvalidSpecifier


def is_prerelease(ver: str) -> bool:
    """
    Checks if a version string represents a prerelease version.
    
    Uses Python's packaging library for PEP 440 versions, and falls back to
    checking for hyphens (e.g., "1.2.3-beta.1") for npm-style prereleases.
    """
    try:
        return Version(ver).is_prerelease
    except InvalidVersion:
        # npm-like prerelease: 1.2.3-beta.1
        return "-" in ver


def normalize_possible_version(raw: str) -> str:
    """
    Try to extract a "x.y.z" from strings like "^17.0.2" or "~4.1.0".
    If not found, return raw.
    """
    raw = raw.strip()
    m = re.search(r"\d+\.\d+\.\d+", raw)
    return m.group(0) if m else raw


def is_up_to_date(current_spec: str, latest: str) -> tuple[bool, str | None]:
    """
    current_spec can be "17.0.2" or "^17.0.2" or "==1.2.3" or ">=1.0".
    We try:
      - if spec is exact version => compare versions
      - else if it's a specifier => check if latest satisfies it
      - else fallback to extracted x.y.z compare
    """
    cs = current_spec.strip()

    # exact numeric like 1.2.3
    if re.fullmatch(r"\d+\.\d+\.\d+", cs):
        return (Version(cs) >= Version(latest), None)

    # requirements style: ==1.2.3 / >=1.0
    if cs.startswith(("==", ">=", "<=", "~=", "!=", ">", "<")):
        try:
            spec = SpecifierSet(cs)
            ok = spec.contains(latest, prereleases=True)
            return (ok, None)
        except (InvalidSpecifier, InvalidVersion):
            pass

    # npm-ish: try extract
    cur_v = normalize_possible_version(cs)
    try:
        return (Version(cur_v) >= Version(latest), "range detected; compared by extracted version")
    except InvalidVersion:
        return (False, "could not parse current version; marking unknown")
