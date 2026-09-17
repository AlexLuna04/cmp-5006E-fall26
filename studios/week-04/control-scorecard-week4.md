# Control Scorecard — Week 4: Breaking RSA Without Factoring

**The question the scorecard forces:** what does this control guarantee,
against which adversary, and how do you know?

Two controls evaluated in this studio:

1. **RSA-2048** (the "factoring n is hard" guarantee)
2. **Secret comparison** (`insecure_equal` vs. `constant_time_equal`)

Both share the same pattern: **the algorithm's guarantee depends on
conditions the algorithm itself cannot enforce.**

---

## Summary table (README Task 4 format)

| Control | Guarantee | Its condition (what the algorithm can't enforce) |
|---|---|---|
| RSA-2048 | infeasible to factor `n` | `p, q` generated with good entropy and independently of one another |
| Any secret comparison | none intrinsic — depends on the implementation | constant-time comparison, or it leaks |

---

## 1 · RSA-2048 — the no-factoring guarantee

| Axis | Evaluation | Evidence |
|---|---|---|
| **1 · Threat model** | Passive attacker with access only to the **public** keys (moduli `n`) of a device population; no access to any private key; needs no factoring hardware — just `math.gcd`. | 8 public keys in `keys.json` |
| **2 · Guarantee** | "Factoring `n` is infeasible" — **if and only if** `p` and `q` were generated with good entropy and independently across devices. | "The one idea" section of the notebook / README |
| **3 · Coverage** | Across the 8-key corpus, the pairwise-GCD scan detected **2/2** vulnerable keys (the one pair sharing a factor) and left all **6/6** safe keys untouched. | `test_shared_factor_recovers_both_keys`, `test_safe_keys_not_recovered` — both passing |
| **4 · Bypass** | **Bypass found and documented**: no strong modulus was factored; `gcd(n_i, n_j)` revealed the shared prime instantly, and `d` was derived for both keys from it via `factor_from_shared`. | `starter.py` output: `batch-GCD recovered private keys for indices: [0, 4]` |
| **5 · Cost — false positives** | 0 %. No safe key was ever flagged as vulnerable (`gcd == 1` against every other key). | `test_safe_keys_not_recovered` |
| **6 · Cost — operational** | Pairwise scan is **O(k²)**. Empirical measurement on a synthetic corpus: ~0.00087 ms per GCD pair, constant regardless of `k` (k=50 → 1,225 pairs / 1.15 ms; k=100 → 4,950 pairs / 4.32 ms; k=200 → 19,900 pairs / 17.31 ms — time scales ~4× when `k` doubles, exactly as O(k²) predicts). At internet scale (millions of keys) naive pairwise becomes infeasible; the real attack (Heninger et al. 2012) uses a **product/remainder tree** to make this near-linear. | Own measurement using `gen_prime` + `math.gcd` over 400 primes |
| **7 · Observability** | High **if the scan is run**: `gcd != 1` is a clean, binary, trivially loggable/alertable signal. But nobody knows until someone actually runs the scan across the population. | — |
| **8 · Failure mode** | **Fails open, silently**: every key individually passes any "is this key safe?" check — the flaw is only visible at the *population* level. Without a periodic scan, a compromised key stays "apparently safe" indefinitely. | Heninger et al. (2012) — ~0.2 % of real TLS keys fell this way in production |

**Honesty clause:** we did not test what happens with mixed corpora of
different modulus sizes (2048-bit real keys vs. the 64-bit keys used here for
speed), nor with more than one sharing pair present simultaneously.

---

## 2 · Secret comparison — `insecure_equal` (before) vs. `constant_time_equal` (after)

| Axis | Before (`insecure_equal`) | After (`constant_time_equal`) | Evidence |
|---|---|---|---|
| **1 · Threat model** | Remote attacker who can only **call** the comparison oracle and measure how long it takes; cannot read the secret. | (same threat model) | `make_oracle` in `rsa_lab.py` |
| **2 · Guarantee** | **None** — the algorithm makes no promise about timing; in fact it actively leaks how many prefix bytes matched. | "Duration does not depend on the secret" — **if and only if** every byte is examined with no *early exit*. | Notebook, section 3 |
| **3 · Coverage** | The timing attack recovered **2/2 bytes** of the secret (`0xA5, 0x3C`) without ever reading it. | The same attack, same number of rounds (41), recovered **0/2** correct bytes. | `test_timing_attack_recovers_secret`, `test_constant_time_defeats_timing_attack` |
| **4 · Bypass** | Bypass = the attack itself (this is already the break). | **Serious bypass attempt documented**: the exact same `timing_attack` was run against `constant_time_equal` and failed to recover the secret — no bypass found. | Output: `constant-time compare leaked nothing: same attack recovered 0000 != a53c` |
| **5 · Cost — false positives** | N/A (not a defense) | **0 %** — equality semantics are identical to `==`; no correct/incorrect result changes, only timing. | `test_constant_time_equal_is_correct` |
| **6 · Cost — operational** | Cheap (early exit saves work). | Slightly more expensive: always walks every byte instead of exiting early — negligible cost for short secrets (tokens, MACs, hashes). | Code comparison |
| **7 · Observability** | **None**: a timing leak leaves no distinctive log line; only detectable through active side-channel testing (exactly what this studio does). | Still none — but there is no longer any signal to leak. | — |
| **8 · Failure mode** | Actively fails on every call (it *is* the vulnerability). | **Silently degrades** if someone "optimizes" the code back into an early `break`/`return` (e.g. the length check, or an early cutoff) — nothing warns that the constant-time property broke. | README note: "A lingering early-exit ... is a live debugging moment" |

**Production recommendation:** don't use either hand-rolled version — always
call `hmac.compare_digest`, which the standard library already solves this
with.

---

## The pattern connecting both controls

> The algorithm's guarantee is conditional on things the algorithm **cannot
> enforce on its own**: quality and independence of entropy (RSA), or
> constant-time execution (secret comparison). The attacker doesn't break the
> math — they break the conditions around it. Name the condition, and you've
> found the attack surface.
