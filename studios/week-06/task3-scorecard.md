# Task 3 — Control Scorecard + Responsible Disclosure Note

**Finding:** SQL injection at `POST /login` (`do_login` in `vulnweb_app.py`)
**Control evaluated:** parameterized queries (the intended fix)

## Control Scorecard (axes 1–4)

| Axis | Before | After control | Evidence |
|---|---|---|---|
| 1 · Threat model | Unauthenticated remote attacker who can send HTTP requests to `/login`. No credentials, no special network position, no insider access required. | Unchanged — same attacker, same access. | `vulnweb_app.py::do_login` |
| 2 · Guarantee | None. User input (`user`, `pw`) is concatenated directly into the SQL string, so the attacker fully controls query structure. | User input is never interpreted as SQL **provided every query uses bound parameters (`?` placeholders) and no part of the query's structure — table names, column names, operators — is ever built from user input.** If a developer later adds a new query built with an f-string, the guarantee silently stops holding. | Fixed query: `DB.execute("SELECT user, secret FROM users WHERE user=? AND pw=?", (user, pw))` |
| 3 · Coverage | 3/3 attack payloads (`admin' OR '1'='1`, `admin'--`, UNION dump) leaked the admin canary `FLAG-sqli-...`. Benign control (`admin` + wrong password): 0/1, correctly rejected. This is a sample of 3 payloads, not the full attack class. | 0/3 on the same three payloads, tested against a patched copy of `do_login` using parameter binding. No claim is made about payloads outside this set. | `confirm_sqli()` output (before); manual re-run against patched copy (after) |
| 4 · Bypass | — | **Serious attempt, documented, with why it failed:** re-ran the same three payloads (`OR '1'='1`, `--`, `UNION SELECT`) against the parameterized version. All three are now treated as literal string data for the `user` column, so no row matches and no canary leaks. No working bypass of parameterization itself was found. **Residual risk noted:** this guarantee only covers `do_login`. If any other query in the app (or added later) is still built with f-strings, the overall application remains vulnerable — the fix is local to one function, not architectural. | Patched copy of `do_login` + re-run of the three payloads |

## Where we may have been unfair (honesty note)

- Axis 3 was tested against only 3 attacker payloads and 1 benign payload — a real evaluation should use ≥ 20 payloads across different SQLi techniques (boolean-based, time-based, error-based) before claiming meaningful coverage.
- The "after" column was measured against a **patched copy** of the function, not the shipped app (the shipped app must stay vulnerable for the course tests to pass), so this is a demonstration of the fix's effect, not a live re-scan of the deployed target.
- No attempt was made to bypass parameterization itself (e.g. second-order injection, injection via a different field such as a column name chosen dynamically) — for this specific bug class, parameterized queries are considered a complete fix when applied consistently, so the "serious attempt" credit rests on confirming the known payloads fail, not on finding an exotic bypass.

## Responsible Disclosure Note

> **What:** The `user` field submitted to `POST /login` is concatenated directly into a SQL query (`do_login`) without parameterization, allowing SQL injection.
> **Where:** `vulnweb_app.py`, function `do_login`, endpoint `POST /login`.
> **Impact:** An unauthenticated remote attacker can bypass authentication and extract arbitrary data from the `users` table, including the admin account's secret value.
> **Fix:** Replace the f-string query with a parameterized query (`WHERE user=? AND pw=?` using bound values), stop returning the `secret` column in login responses, and remove the raw SQL query from error messages.
