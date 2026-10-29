# Week 8 — Control Scorecard: Trust the Artifact, Not the Name

**Studio:** Week 8 — Systems, Auth & Supply Chain
**Evidence:** `starter.py`, `test_supplychain.py`, `bonus_bruteforce.py`

> **The question the scorecard forces:** What does this control guarantee, against which adversary, and how do you know?

**Shared guarantee (axis 2):** *Only the exact vetted artifact is trusted — under a key or list **we** control.* A name-based lookup can never make this promise.

---

## 1. Name → Artifact → Pin (one row per attack)

| Attack | Trusted name | Substituted artifact | The pin that closes it |
|---|---|---|---|
| Dependency confusion | The package name `acme-auth` | Attacker's public `acme-auth` 9.9.9 | Lockfile + sha256 + source scope |
| Transitive backdoor (XZ) | "It's just a dependency" | Compromised upstream code (`xz-utils`, two levels deep) | SBOM + provenance + pinning |
| `alg=none` JWT | The token's own `alg` header | An unsigned token claiming `role: admin` | Server-side algorithm pinning |

---

## 2. Full scorecard (8 axes)

### Attack 1 — Dependency confusion

| Axis | Before | After control | Evidence |
|---|---|---|---|
| Threat model | Remote attacker who can publish to the public registry. No credentials, no access to our network. | Unchanged | `data.py` (public_registry) |
| Guarantee | None. The resolver trusts the name and picks the highest version. | Only the artifact with the pinned **source AND sha256** installs, **provided** the lockfile is reviewed and not tampered with. | `resolve_pinned()` |
| Coverage | 0/1 — attacker's 9.9.9 wins | 1/1 attacker artifact refused (sample of one; no claim about other attacks) | `test_dependency_confusion_public_wins_until_pinned` |
| **Bypass** | Not needed — the attack works by default. | **Attempted:** same name from the public registry with any hash → rejected on source mismatch. A package with the right hash but wrong source → rejected. Remaining bypass: a compromised lockfile or a malicious but legitimately vetted release. | `resolve_pinned()` |
| FP cost | 0% | Vetted internal build accepted (1/1). Every legitimate version bump requires a lockfile update. | test output |
| Op cost | None | Maintaining hashes in the lockfile; scoped internal registry config. | — |
| Observability | Silent — the install looks normal. | The pinned resolver returns an explicit reason string; it should be wired to a CI log/alert. | `resolve_pinned()` return value |
| Failure mode | **Fails open** (attacker accepted) | **Fails closed** (unknown package, wrong source or wrong hash → refuse) | `resolve_pinned()` |

### Attack 2 — Transitive backdoor / SBOM

| Axis | Before | After control | Evidence |
|---|---|---|---|
| Threat model | Attacker compromises an upstream package we never chose directly. | Unchanged | `dep_graph` in `data.py` |
| Guarantee | None — we cannot even list what we depend on. | We can enumerate every transitive dependency and answer "are we affected by CVE-X?" instantly, **provided** the SBOM is complete and regenerated on every build. | `build_sbom()`, `cve_affected()` |
| Coverage | Unknown | 6/6 transitive dependencies listed; `xz-utils` found. (Toy graph of 7 nodes.) | `test_sbom_finds_transitive_cve` |
| **Bypass** | — | An SBOM only **detects and inventories**; it does not prevent a backdoor. A dependency missing from the graph (dynamic loading, vendored code) is invisible to it. | — |
| FP cost | 0% | None — it is a read-only inventory. | — |
| Op cost | — | Generating and storing an SBOM per build (real tools: syft, cyclonedx). | — |
| Observability | Days of grepping build logs | One set-intersection query | `cve_affected()` |
| Failure mode | Fails silently (we don't know we're exposed) | Degrades silently if the SBOM is stale or incomplete. | — |

### Attack 3 — `alg=none` JWT forgery

| Axis | Before | After control | Evidence |
|---|---|---|---|
| Threat model | Attacker can read and craft tokens. Holds **no** signing key. | Unchanged | `forge_alg_none_admin()` |
| Guarantee | "Only tokens signed under our key are valid" — **false**, the verifier obeys the token's own `alg`. | Only HS256 tokens signed under `SECRET` are accepted, **provided** `SECRET` is long, random and never leaked. | `verify_secure()` |
| Coverage | 0/1 — forged admin token accepted | 1/1 forgery rejected; legitimate token still accepted (sample of one; case variants like `"None"` untested) | `test_algorithm_pinning_rejects_forgery` |
| **Bypass** | Not needed. | **Found:** if `SECRET` is a short dictionary word, it is brute-forced offline and valid admin tokens can be minted (demo key `admin` cracked from a 5-word list). Pinning the algorithm does **not** protect a weak key. | `bonus_bruteforce.py` |
| FP cost | 0% | Legitimate HS256 token accepted (1/1). | test output |
| Op cost | — | Negligible (one string comparison and one HMAC). | — |
| Observability | No log line when a forged token is accepted. | `verify_secure` returns `None` but does not log; rejections should be logged. | — |
| Failure mode | **Fails open** (accepts unsigned token) | **Fails closed** (wrong alg, bad signature or malformed token → `None`) | `verify_secure()` |

---

## 3. Where we may have been unfair, and what we did not test

- We used **one attack per category** on a toy dataset (2 registries, 7-node graph). The coverage numbers describe this sample, not the attack class.
- The attacker and defender were not given equal effort: the attacks are the textbook versions, and the defences were written knowing exactly what the attack does.
- We did not test hash collisions, a tampered lockfile, a malicious release that is legitimately signed, or `alg` case variants (`"None"`, `"NONE"`) that real libraries once accepted.
- The weak-secret brute force used a **demo key** (`admin`), not the lab's `SECRET`; the lab's real `SECRET` (`server-signing-key`) was not attacked.
- We did not measure false positives on realistic traffic; only one legitimate artifact per control was checked.
- Algorithm pinning and lockfile pinning do not fix a weak signing key or a compromised vetting process — the guarantees are conditional on those.
