# Week 5 Studio Report: Diffie-Hellman, MITM & the Trust Anchor

## 1. DH + Man-in-the-Middle

**Implementation.** `dh_public(x) = g^x mod p`, `dh_shared(their_pub, my_priv) = their_pub^my_priv mod p`, using the RFC 2409 group-2 1024-bit MODP prime.

**Honest DH.** Alice and Bob each compute `g^(ab) mod p` and agree.

**MITM.** Mallory sends her public value `M = g^m` to *both* sides. Result:

| Pair | Share a key? |
|---|---|
| Alice <-> Mallory | Yes |
| Bob <-> Mallory | Yes |
| Alice <-> Bob | **No** |

**What DH guarantees:** a shared secret against a *passive* eavesdropper, **provided the endpoints are authenticated**. It gives secrecy on each leg and zero authentication of the endpoints. Secrecy without authentication is a private conversation with an impostor.

## 2. Certificate-chain validation

| Chain | Result | Reason |
|---|---|---|
| leaf <- ACME Intermediate <- ACME Root (trusted) | Accepted | Terminates in a trusted anchor |
| Self-signed forgery | Rejected | Anchor is not a trusted root |
| Rogue leaf <- Rogue CA | Rejected | Anchor is not a trusted root |

Both forgeries fail at the **same** check. Mallory can sign anything, but she cannot make the browser trust her signing key. PKI relocates the whole problem to one question: *is the trust store correct?*

## 3. Trust-store attack

`poison_trust_store` returns a **new** set containing the original anchors plus the rogue root's public key (the caller's store is not mutated).

| Store | Rogue chain |
|---|---|
| Clean | Rejected |
| Poisoned | **Accepted** |

The signatures never broke; the trust anchor did. Real-world analogues:

- **DigiNotar (2011):** a compromised CA mis-issued valid certificates, used to MITM Gmail for Iranian users.
- **Negligent CA:** signs a certificate it should not have.
- **Malware-installed root:** any forged chain now validates cleanly.

Certificate Transparency does not prevent mis-issuance; it makes it public and detectable (a detective control).

## 4. Control Scorecard

### Quick view (axis 2 conditional form)

| Mechanism | Guarantee (axis 2) | Condition / failure |
|---|---|---|
| Diffie-Hellman | Shared secret vs. a passive eavesdropper | **No authentication:** MITM defeats it |
| Certificate chain | Binds a key to a name | Only as trustworthy as the **root trust store** |
| TLS 1.3 | Confidential, authenticated channel | Every underlying condition (nonce, key, trust) must hold |

TLS 1.3 = authenticated DH + certificate chain + AEAD (AES-GCM). Nonce reuse (wk3), a weak key (wk4), MITM on unauthenticated DH (section 1), and a bad trust anchor (section 3) all live somewhere in that stack.

### Full table: certificate-chain validation as the control

| Axis | Before | After control | Evidence |
|---|---|---|---|
| Threat model | Active network attacker (Mallory) who can intercept, inject and relay; can sign with her own keys; cannot modify the trust store | Unchanged | `starter.py` MITM |
| Guarantee | None: DH endpoints unauthenticated | Binds key to name **if** the root trust store contains only honest anchors and CAs never mis-issue | `validate()` |
| Coverage | 0/2 forgeries rejected (no validation) | 2/2 forgery types rejected (self-signed, rogue CA); sample of 2, not the space of all attacks | `test_dh_pki.py` |
| **Bypass** | n/a | **Found:** poisoning the trust store with the rogue root makes the rogue chain validate | `test_trust_store_poisoning_accepts_forgery` |
| FP cost | n/a | 0/1 legitimate chains rejected (only one benign chain tested) | `test_legitimate_chain_validates` |
| Op cost | n/a | Negligible in the toy model; real PKI costs CA operations, revocation and rotation | not measured |
| Observability | None | `validate()` returns a reason string; real-world equivalent is Certificate Transparency logs | `validate()` output |
| Failure mode | n/a | **Fails open** once a rogue root is trusted: the validator cannot tell | poisoning test |

## 5. Where we may have been unfair, and what we did not test

- Only **one** legitimate chain was tested, so the false-positive estimate is weak.
- Only **two** forgery types were tried. We did not test expired certificates, revocation, name mismatch, path-length constraints, or intermediates with CA flags.
- The signature scheme is **64-bit toy RSA**: textbook RSA over a SHA-256 digest reduced mod n. It is trivially factorable, so a real attacker would forge signatures without any trust-store attack. The tests show the *structure* of the failure, not real-world strength.
- The attacker in the poisoning test is *given* write access to the trust store. We did not model how hard that is to obtain.
- Certificate Transparency and pinning were discussed but not implemented, so their effectiveness is unmeasured.
