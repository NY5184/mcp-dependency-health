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


def convert_npm_range_to_specifier(npm_range: str) -> str | None:
    """
    Converts npm-style version ranges to Python packaging specifier format.
    
    npm ranges:
    - ^18.0.0 → >=18.0.0,<19.0.0 (allows any compatible 18.x.x)
    - ~18.0.0 → >=18.0.0,<18.1.0 (allows patch updates only)
    - >=18.0.0 → >=18.0.0
    - <=18.0.0 → <=18.0.0
    
    Returns None if the range cannot be converted.
    """
    npm_range = npm_range.strip()
    
    # Handle caret (^) ranges: ^18.0.0 → >=18.0.0,<19.0.0
    if npm_range.startswith("^"):
        base_version = npm_range[1:].strip()
        try:
            v = Version(base_version)
            # For ^x.y.z, allow >=x.y.z <(x+1).0.0
            next_major = f"{v.major + 1}.0.0"
            return f">={base_version},<{next_major}"
        except InvalidVersion:
            return None
    
    # Handle tilde (~) ranges: ~18.0.0 → >=18.0.0,<18.1.0
    if npm_range.startswith("~"):
        base_version = npm_range[1:].strip()
        try:
            v = Version(base_version)
            # For ~x.y.z, allow >=x.y.z <x.(y+1).0
            if len(v.release) >= 2:
                next_minor = f"{v.major}.{v.minor + 1}.0"
            else:
                next_minor = f"{v.major + 1}.0.0"
            return f">={base_version},<{next_minor}"
        except InvalidVersion:
            return None
    
    # Handle standalone >= or <= (npm style, not Python style)
    # These are already compatible with Python specifiers, but we need to ensure
    # they're not being treated as Python-style (which would have been caught earlier)
    if npm_range.startswith((">=", "<=", ">", "<")):
        # Already in Python specifier format, return as-is
        return npm_range
    
    return None


def is_up_to_date(current_spec: str, latest: str) -> tuple[bool, str | None]:
    """
    current_spec can be "17.0.2" or "^17.0.2" or "==1.2.3" or ">=1.0".
    We try:
      - if spec is exact version => compare versions
      - else if it's a Python-style specifier => check if latest satisfies it
      - else if it's an npm-style range => convert and check if latest satisfies it
      - else fallback to extracted x.y.z compare
    """
    cs = current_spec.strip()

    # exact numeric like 1.2.3
    if re.fullmatch(r"\d+\.\d+\.\d+", cs):
        return (Version(cs) >= Version(latest), None)

    # Python requirements style: ==1.2.3 / >=1.0 / ~=1.0
    if cs.startswith(("==", ">=", "<=", "~=", "!=", ">", "<")):
        try:
            spec = SpecifierSet(cs)
            ok = spec.contains(latest, prereleases=True)
            return (ok, None)
        except (InvalidSpecifier, InvalidVersion):
            pass

    # npm-style ranges: ^18.0.0, ~18.0.0, >=18.0.0 (standalone)
    npm_spec = convert_npm_range_to_specifier(cs)
    if npm_spec:
        try:
            spec = SpecifierSet(npm_spec)
            ok = spec.contains(latest, prereleases=True)
            return (ok, "npm range detected; checked if latest satisfies range")
        except (InvalidSpecifier, InvalidVersion):
            pass

    # fallback: try extract version and compare (legacy behavior)
    cur_v = normalize_possible_version(cs)
    try:
        return (Version(cur_v) >= Version(latest), "range detected; compared by extracted version")
    except InvalidVersion:
        return (False, "could not parse current version; marking unknown")
