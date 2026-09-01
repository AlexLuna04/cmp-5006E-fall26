# Week 1 Studio — Break a Cipher: The Assumption Is the Attack

## Task 1 — Break It Yourself

### 1. Recovered plaintext and pre-correction accuracy

The recovered plaintext was:

> SECURITY THROUGH OBSCURITY IS THE RELIANCE ON SECRECY OF DESIGN AS THE MAIN METHOD OF PROVIDING SECURITY FOR A SYSTEM. A SYSTEM RELYING ON OBSCURITY MAY HAVE REAL SECURITY VULNERABILITIES, BUT ITS OWNERS OR DESIGNERS BELIEVE THAT IF THE FLAWS ARE NOT KNOWN THEN ATTACKERS WILL BE UNLIKELY TO FIND THEM. KERCKHOFFS ARGUED THE OPPOSITE: A SYSTEM SHOULD BE SECURE EVEN IF EVERYTHING ABOUT IT EXCEPT THE KEY IS PUBLIC KNOWLEDGE. THE LESSON FOR THIS COURSE IS THAT WE CAN PUBLISH EXACTLY HOW AN ATTACK WORKS, BECAUSE A SYSTEM WHOSE SECURITY DEPENDED ON YOUR IGNORANCE WAS ALREADY BROKEN.

**Pre-correction accuracy:** 100%

No manual corrections were made before measuring the recovery rate.

### 2. Named assumption

**Assumption:** The plaintext is English and therefore has exploitable letter-frequency and bigram structure that survives the substitution cipher.

### 3. Defeating the attack

To defeat the frequency-analysis attack, I used a one-time pad (OTP) with a randomly generated key of the same length as the plaintext.

The experiment encrypted an English message using the OTP and then applied the same frequency-analysis attack used in the studio.

**Observed result:**

* Frequency-analysis accuracy: **6.8%**
* Correct decryption using the actual OTP key: **True**
* Key length: **88**
* Message length: **88**

The ciphertext produced by the OTP was:

> IHEUERDMBTLTEWHUAFHRTGIAOYHIONPLDSPEMUNNEAEDNOSOJGVTBVOAGKDACLMCTFYFYLECCSASRISWRTWNIKPO

The frequency-analysis attack recovered only **6.8%** of the plaintext characters, compared with **100%** recovery against the English substitution-cipher ciphertext. However, decryption using the actual OTP key recovered the plaintext correctly. This shows that the frequency and bigram structure exploited by the substitution-cipher attack is no longer useful against the OTP ciphertext.

#### Control Scorecard — Axis 2: Guarantee

**Guarantee:** A one-time pad provides perfect secrecy, meaning the ciphertext reveals no information about the plaintext, provided that the key is truly random, is at least as long as the message, is kept secret, and is never reused.

**Cost:** The key must be as long as the message and must be securely distributed, stored, and used only once.



### 4. Failure Atlas

**Failure:** Frequency-only analysis can assign incorrect plaintext letters when the ciphertext is short.

**Why:** Frequency analysis assumes that the observed sample has frequencies similar to population-level English frequencies. A short message may not have that distribution, especially for rare letters such as J, X, Q, and Z. Therefore, the frequency ranking can produce incorrect letter assignments even when the plaintext is English.

The bigram hill-climbing stage provides additional signal by evaluating pairs of letters rather than relying only on individual letter frequencies.

---

## Where we may have been unfair, and what we did not test

The attack was evaluated using the public English frequency prior and bigram score provided by the course. The provided English ciphertexts were generated from the same plaintext structure used by the public language model, so the attack benefits from having a language model that closely matches the plaintext domain.

The experiment also used a fixed random seed for reproducibility.

The defense demonstration tested the frequency-analysis attack against an OTP ciphertext, but it does not by itself constitute a proof of perfect secrecy. The guarantee of the OTP depends on its stated conditions: a truly random key, sufficient key length, secrecy of the key, and no key reuse.

### Test results

The provided test suite passed all four tests:

- `test_cipher_roundtrip`
- `test_frequency_guess_is_a_valid_mapping`
- `test_english_assumption_collapses_confidentiality`
- `test_cipher_holds_on_non_english_plaintext`

**Result:** All 4 tests passed.