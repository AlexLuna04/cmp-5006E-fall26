"""Week 8 studio — solution (three attacks, three pins).

Every exploit substitutes an artifact behind a name the victim trusted;
every fix pins the artifact instead of trusting the name.
"""
import hashlib
import hmac
import json

from data import (internal_registry, public_registry, LOCKFILE,
                  dep_graph, KNOWN_BAD, SECRET)
from supplychain import b64, b64d, make_token


# ---- Task 1a: dependency confusion — the naive resolver (the bug) -----------

def resolve_highest_version(pkg: str):
    """Consider BOTH registries and pick the highest version, ignoring source."""
    candidates = []
    if pkg in internal_registry:
        candidates.append(("internal", internal_registry[pkg]))
    if pkg in public_registry:
        candidates.append(("public", public_registry[pkg]))
    # Compare versions as tuples of ints so "9.9.9" > "1.4.2" (and "1.10" > "1.9").
    # Note what is NOT in the key: the source. That omission is the vulnerability.
    return max(candidates, key=lambda c: tuple(int(x) for x in c[1].split(".")))


# ---- Task 1b: the pin — resolve against the lockfile (the fix) --------------

def resolve_pinned(pkg: str, candidate_hash: str, candidate_source: str):
    """Accept only the exact vetted artifact: right source AND right hash."""
    want = LOCKFILE.get(pkg)
    if not want:
        return False, "package not in lockfile — refuse to install"
    if candidate_source != want["source"]:
        return False, f"source mismatch: got {candidate_source!r}, pinned {want['source']!r}"
    if candidate_hash != want["sha256"]:
        return False, "hash mismatch — artifact is not the one we vetted"
    return True, "ok — exact artifact matches the lockfile"


# ---- Task 2: SBOM — build the transitive list, then query it for a CVE ------

def build_sbom(root: str, graph: dict) -> list:
    """Sorted list of ALL transitive dependencies of root (root excluded)."""
    seen = set()
    stack = list(graph.get(root, []))
    while stack:
        dep = stack.pop()
        if dep not in seen:
            seen.add(dep)
            stack.extend(graph.get(dep, []))
    seen.discard(root)  # guards against cycles pointing back to the root
    return sorted(seen)


def cve_affected(sbom: list, known_bad: set) -> list:
    """Sorted intersection of the SBOM with the advisory's known-bad names."""
    return sorted(set(sbom) & set(known_bad))


# ---- Task 3a: forge an alg=none admin token (the attack) --------------------

def forge_alg_none_admin() -> str:
    """Header alg=none, payload role=admin, EMPTY signature (trailing dot)."""
    header = b64(json.dumps({"alg": "none", "typ": "JWT"}).encode())
    payload = b64(json.dumps({"user": "alice", "role": "admin"}).encode())
    return f"{header}.{payload}."


# ---- Task 3b: the pin — verify with a server-side algorithm (the fix) -------

def verify_secure(token: str, expected_alg: str = "HS256"):
    """Pin the algorithm server-side; never trust the token's own header."""
    try:
        h, p, sig = token.split(".")
        if json.loads(b64d(h)).get("alg") != expected_alg:
            return None                      # kills alg=none immediately
        expected = b64(hmac.new(SECRET, f"{h}.{p}".encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(sig, expected):
            return None
        return json.loads(b64d(p))
    except (ValueError, KeyError, TypeError):
        return None                          # malformed token -> fail closed


if __name__ == "__main__":
    src, ver = resolve_highest_version("acme-auth")
    print(f"naive resolve('acme-auth') -> {src} v{ver} (attacker won: {src == 'public'})")
    print("pinned, attacker's public:", resolve_pinned("acme-auth", "evil99ff", "public"))
    print("pinned, vetted internal  :", resolve_pinned("acme-auth", "aa11bb22cc", "internal"))

    sbom = build_sbom("our-app", dep_graph)
    print("SBOM:", sbom)
    print("affected by xz-utils CVE:", cve_affected(sbom, KNOWN_BAD))

    from supplychain import verify_insecure
    legit = make_token({"user": "alice", "role": "user"})
    forged = forge_alg_none_admin()
    print("naive verifier accepts forgery as:", verify_insecure(forged))
    print("pinned verifier, forgery:", verify_secure(forged))
    print("pinned verifier, legit  :", verify_secure(legit))
