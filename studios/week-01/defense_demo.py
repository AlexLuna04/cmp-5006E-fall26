import random

from cipher import ALPHABET, apply_guess
from starter import frequency_guess_key


def otp_encrypt(plaintext, key):
    """Encrypt letters with a one-time pad."""
    result = []

    for p, k in zip(plaintext, key):
        p_value = ALPHABET.index(p)
        k_value = ALPHABET.index(k)
        c_value = (p_value + k_value) % 26
        result.append(ALPHABET[c_value])

    return "".join(result)


def otp_decrypt(ciphertext, key):
    """Decrypt letters with a one-time pad."""
    result = []

    for c, k in zip(ciphertext, key):
        c_value = ALPHABET.index(c)
        k_value = ALPHABET.index(k)
        p_value = (c_value - k_value) % 26
        result.append(ALPHABET[p_value])

    return "".join(result)


def random_key(length, seed=123):
    """Generate a random key with the same length as the message."""
    rng = random.Random(seed)
    return "".join(rng.choice(ALPHABET) for _ in range(length))


def main():
    plaintext = (
        "SECURITY THROUGH OBSCURITY IS THE RELIANCE ON SECRECY "
        "OF DESIGN AS THE MAIN METHOD OF PROVIDING SECURITY"
    )

    # Keep only letters because this demonstration uses A-Z.
    plaintext = "".join(
        ch for ch in plaintext.upper()
        if ch in ALPHABET
    )

    # OTP requirement: key is truly random and exactly as long as plaintext.
    key = random_key(len(plaintext))

    ciphertext = otp_encrypt(plaintext, key)

    # Attack using the same frequency-analysis technique from the lab.
    guess = frequency_guess_key(ciphertext)
    recovered = apply_guess(ciphertext, guess)

    correct = sum(
        a == b
        for a, b in zip(recovered, plaintext)
    )
    accuracy = correct / len(plaintext)

    # Verify that the real key decrypts correctly.
    decrypted = otp_decrypt(ciphertext, key)

    print("PLAINTEXT:")
    print(plaintext)
    print()

    print("CIPHERTEXT:")
    print(ciphertext)
    print()

    print("FREQUENCY-ANALYSIS RECOVERY:")
    print(recovered)
    print()

    print(f"Frequency-analysis accuracy: {accuracy:.1%}")
    print(f"Correct decryption with OTP key: {decrypted == plaintext}")
    print(f"Key length: {len(key)}")
    print(f"Message length: {len(plaintext)}")


if __name__ == "__main__":
    main()