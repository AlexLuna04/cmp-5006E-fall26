# Control Scorecard — Week 2: One-Time Pad

| Axis | Before | After control | Evidence |
|------|--------|---------------|----------|
| 1. Threat model | attacker sees ciphertext, unbounded compute, no key | unchanged | `test_otp.py` |
| 2. Guarantee | none | perfect secrecy — ciphertext statistically independent of plaintext, **against unbounded compute**, **provided** the key is random, ≥ message length, and used **exactly once** | `test_otp_perfect_secrecy_when_key_used_once` |
| 3. Coverage | N/A (not a payload-blocking control) | 1/1 — any plaintext of matching length is equally consistent with the ciphertext | Task 2 demo: two keys, two meaningful decryptions of one ciphertext |
| 4. Bypass | — | **found: key reuse.** Reusing the key across two messages collapses the guarantee completely: `c1 ⊕ c2 = p1 ⊕ p2`, no key needed | `test_two_time_pad_leaks_and_crib_drag_recovers`, crib-drag on `please`/`target` |
| 5. FP cost | — | N/A — a cipher has no "false positive" analog; correctness is guaranteed by construction (`otp_decrypt(otp_encrypt(m,k),k) == m`) | `test_otp.py` |
| 6. Op cost | — | key must be truly random and as long as the message; generating/storing/transporting that much secret key is the real cost | `resources/ai-policy.md` n/a — reasoning only |
| 7. Observability | — | none needed while the condition holds; if reused, the leak is silent — nothing in the ciphertext signals reuse to a defender | reasoning |
| 8. Failure mode | — | **fails silently, not closed or open** — reuse doesn't throw an error or refuse to encrypt; it just quietly destroys the guarantee and lets an attacker crib-drag both plaintexts out | `test_two_time_pad_leaks_and_crib_drag_recovers` |

## Why almost no one uses the OTP

Its only condition, a random key, as long as the message, used only once, turns the problem of distributing the key into a problem just as difficult as distributing the secret message itself. If you already have a secure channel to share a key the size of the message, you could simply send the message through that channel. That is why real cryptography (weeks 3–4: AES, RSA) trades perfect secrecy for computational security: breakable in principle, infeasible in practice, but usable — and with its own conditions, which must be named just like here.
