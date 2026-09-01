# Week 1 — Task 2 & Task 3: Threat Model and AI Comparison

## Task 2 — STRIDE Threat Model

### 1. System description

The system is a generic DVWA-style intentionally vulnerable web application used for security testing.

It provides a browser-based interface where an unauthenticated or authenticated user can interact with several web application functions. The application is hosted by a web server, processes HTTP requests through server-side application code, stores application data in a database, and writes operational information to server logs.

The main users are:

* **Normal users / attackers:** can send HTTP requests to the application.
* **Administrator:** has additional privileges and access to administrative functionality.
* **Database:** stores application and user data.
* **Web server/application:** receives requests, processes input, performs authorization checks, queries the database, and returns responses.

The threat model assumes an **external remote attacker with no legitimate administrative privileges**. The attacker can interact with any functionality exposed by the web application and can modify the HTTP requests sent by their browser.

---

### 2. Data-flow diagram and trust boundaries

```text
                         External / Untrusted
                                │
                                │ HTTP/HTTPS requests
                                ▼
                         [ Web Browser ]
                                │
                                │ User-controlled
                                │ requests / parameters
                                ▼
════════════════════════ TRUST BOUNDARY ════════════════════════
                                │
                                ▼
                    [ Web Server / DVWA App ]
                       │        │        │
                       │        │        │
                 SQL query   File access  Logs
                       │        │        │
                       ▼        ▼        ▼
                 [ Database ] [ Server ] [ Log Files ]
                                  Files
```

The primary trust boundary is between the **external browser/attacker** and the **web application**.

A second important boundary exists between the application and the database: the application is trusted to construct safe database queries, but the database should not automatically trust user-controlled input that reaches it through the application.

The same principle applies to files and logs: data generated from user requests may cross from an untrusted source into trusted server-side storage.

---

### 3. Assets

The main assets that require protection are:

| Asset                       | Why it matters                                                |
| --------------------------- | ------------------------------------------------------------- |
| User credentials            | Could allow account takeover                                  |
| Session identifiers         | Could allow impersonation of authenticated users              |
| User information            | May contain private or sensitive data                         |
| Database contents           | Contains application and user data                            |
| Administrator functionality | Provides higher privileges and greater impact                 |
| Server-side files           | Could contain configuration, credentials, or application code |
| Application availability    | Users should be able to access the application                |
| Logs                        | Provide evidence of security-relevant activity                |

---

## 4. STRIDE analysis

| # | Threat (STRIDE letter)         | Where it enters                                      | What an attacker gains                                                           | Mitigation                                                                                                  | Guarantee — and its condition (Axis 2)                                                                                                                                                                              | Evidence       |
| - | ------------------------------ | ---------------------------------------------------- | -------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- |
| 1 | **Spoofing (S)**               | Login request / session handling                     | Ability to act as another user if credentials or a session token are compromised | Strong authentication, secure session identifiers, server-side session validation, secure cookie attributes | An attacker cannot authenticate as another user **provided credentials are not compromised and every authenticated request validates the server-side session rather than trusting client-controlled identity data** | Not yet tested |
| 2 | **Tampering (T)**              | User-controlled parameters → application/database    | Modification of database queries or application data                             | Parameterized queries and strict server-side input handling                                                 | User input cannot alter the structure of a database query **provided every database operation uses parameterized queries and no vulnerable query path concatenates user input into SQL**                            | Not yet tested |
| 3 | **Repudiation (R)**            | HTTP requests → application logs                     | Ability to deny malicious activity because there is insufficient evidence        | Security logging with timestamps, relevant identifiers, and protected log storage                           | Security-relevant actions can be attributed to a request **provided the application records the relevant event and the logs cannot be modified by the attacker**                                                    | Not yet tested |
| 4 | **Information Disclosure (I)** | Error responses / database responses / exposed files | Discovery of database structure, application information, or private data        | Generic production errors, access controls, output encoding, removal of sensitive files                     | Sensitive internal information is not disclosed to an external user **provided production errors do not expose debugging information and sensitive files/data are protected by server-side access controls**        | Not yet tested |
| 5 | **Denial of Service (D)**      | Repeated or expensive HTTP requests                  | Reduced availability or increased server resource consumption                    | Rate limiting, resource limits, request validation, monitoring                                              | A single external attacker cannot exhaust application resources **provided rate limits and resource controls are enforced for expensive or repeated requests**                                                      | Not yet tested |
| 6 | **Elevation of Privilege (E)** | Authorization checks / role parameters               | Access to administrator functionality as a lower-privileged user                 | Server-side authorization checks for every protected operation                                              | A normal user cannot perform administrator-only operations **provided authorization is checked server-side on every protected request and privileges are never determined from client-controlled parameters**       | Not yet tested |

---

## 5. Most important trust boundaries

The most important trust boundary is:

```text
External attacker
       │
       │ attacker-controlled HTTP request
       ▼
════════════════════════════
       WEB APPLICATION
════════════════════════════
       │
       ├──────────────► Database
       │
       ├──────────────► Server files
       │
       └──────────────► Logs
```

The attacker controls much more of the input than the application should trust.

For every request crossing the boundary, the application should assume that:

* Parameters may be malicious.
* Cookies may be manipulated or stolen.
* HTTP methods may be changed.
* Hidden form fields may be modified.
* User-supplied identifiers may refer to another user.
* Input may contain unexpected characters or structures.

The central security assumption should therefore be:

> **Client-controlled input is untrusted until it has been validated and processed by a server-side control appropriate to its context.**

---

## 6. Highest-risk threats

Although all six STRIDE categories are relevant, three threats are particularly important for this application.

### 6.1 Tampering / SQL injection

A vulnerable application may construct database queries using untrusted request parameters.

The security failure occurs when the application treats attacker-controlled data as part of the SQL command itself.

The appropriate control is parameterized database access.

**Guarantee:**

> User-controlled input cannot change the structure of a database query **provided every database query uses parameterized statements and there are no alternate vulnerable database access paths.**

This is stronger than saying "prepared statements prevent SQL injection" because the guarantee explicitly depends on **all query paths** using the control.

---

### 6.2 Information disclosure

A vulnerable application may reveal information through:

* Detailed database errors.
* Stack traces.
* Debugging output.
* Application configuration.
* Exposed files.
* Excessive response information.

The mitigation is to expose only information necessary for the legitimate user while keeping diagnostic information on the server.

**Guarantee:**

> Production users do not receive internal debugging information **provided debug output is disabled and application errors are handled by a generic production error mechanism.**

---

### 6.3 Elevation of privilege

A common web application failure is trusting the client to identify the user's role.

For example, a request might contain a parameter such as:

```text
role=user
```

Changing the value on the client should never be sufficient to obtain administrative privileges.

The authorization decision must be made on the server.

**Guarantee:**

> A lower-privileged user cannot perform an administrator-only operation **provided every protected operation performs a server-side authorization check using trusted session/account state.**

---

## 7. What cannot be determined from the outside

Because this is a generic DVWA-style application rather than an inspected production system, several implementation details cannot be determined from the outside.

In particular, we cannot know:

* Whether every SQL query is parameterized.
* Whether session identifiers are generated securely.
* Whether authorization checks are performed on every protected endpoint.
* Whether sensitive information exists in server-side files.
* Whether logs can be modified or deleted by an attacker.
* Whether rate limiting exists.
* Whether production error handling exposes internal information.
* Whether different application endpoints use different security mechanisms.

To determine these things, we would need to inspect the **server-side source code, database access layer, session implementation, authorization logic, configuration files, and logging configuration**.

This limitation is important because a threat model should distinguish between a security property that has been verified and one that is only expected.

---

# Task 3 — AI Threat-Model Comparison

## 1. LLM prompt

The following prompt can be given to an LLM to produce an independent threat model.

```text
You are performing a security threat-modeling exercise.

Consider this system:

A generic DVWA-style intentionally vulnerable web application is exposed
through a web browser. An external attacker can send HTTP requests to the
application. The application runs on a web server and contains server-side
application logic. It communicates with a database and writes information
to server-side log files. The application has normal-user functionality
and administrator functionality.

Assume the attacker is remote, unauthenticated, and does not initially
have administrative privileges. The attacker can modify HTTP requests,
parameters, cookies, and form fields sent to the application.

Create a STRIDE threat model for this application.

Requirements:
1. Identify the major assets.
2. Draw or describe the main data flows.
3. Identify the important trust boundaries.
4. Provide at least one threat for each STRIDE category.
5. For every threat, explain:
   - where it enters,
   - what the attacker gains,
   - a mitigation,
   - the conditional security guarantee of that mitigation.
6. Identify the three most important threats.
7. Identify anything that cannot be determined without access to the
   application's source code or configuration.

Do not assume that a security control is actually implemented unless
the system description explicitly states that it is.
```

---

## 2. AI threat model

The LLM's output should be recorded here after running the prompt.

### AI-identified assets

* User credentials
* Session identifiers
* User data
* Database contents
* Administrator functionality
* Server-side files
* Application availability
* Logs

### AI-identified trust boundaries

The LLM identified the primary trust boundary between:

```text
External user / browser
          │
          ▼
     Web application
          │
     ┌────┼────┐
     ▼    ▼    ▼
 Database Files Logs
```

This is consistent with the manual threat model because the browser is controlled by the attacker while the server-side components are trusted application infrastructure.

---

## 3. AI STRIDE findings

| STRIDE                     | AI finding                                                                                                  | Agreement with manual model |
| -------------------------- | ----------------------------------------------------------------------------------------------------------- | --------------------------- |
| **Spoofing**               | Credential theft, session abuse, or weak authentication could allow impersonation                           | **Agree**                   |
| **Tampering**              | SQL injection and manipulation of application parameters could modify data or commands                      | **Agree**                   |
| **Repudiation**            | Insufficient logging could prevent attribution of malicious actions                                         | **Agree**                   |
| **Information Disclosure** | Error messages, database responses, or exposed files could reveal sensitive information                     | **Agree**                   |
| **Denial of Service**      | Repeated or expensive requests could exhaust application resources                                          | **Agree**                   |
| **Elevation of Privilege** | Client-controlled role information or missing authorization checks could expose administrator functionality | **Agree**                   |

---

## 4. What the AI found that I might have missed

The main value of the LLM is breadth rather than application-specific certainty.

Potential additional areas identified by the AI include:

* Session fixation or insecure session management.
* Weak password policies.
* Missing security headers.
* Insecure file handling.
* Excessive information in HTTP responses.
* Missing rate limiting.
* Weak access control on individual endpoints.

These are useful as **questions to investigate**, but they should not automatically be treated as vulnerabilities.

For example, an LLM can reasonably suggest "session fixation" as a possible threat, but it cannot establish that the application actually has session fixation without examining the session implementation.

This distinction is important:

> **The LLM can identify a plausible threat, but plausibility is not evidence that the vulnerability exists in this particular application.**

---

## 5. What the AI could assert incorrectly

An LLM may incorrectly turn a generic vulnerability possibility into a statement that the application is actually vulnerable.

For example:

> "The application is vulnerable to SQL injection because it uses user input in SQL queries."

That conclusion would be unjustified unless the application's implementation actually showed unsafe SQL construction.

The correct statement is:

> "SQL injection is a relevant threat because attacker-controlled input may reach database queries; whether the application is actually vulnerable requires inspection or testing."

The same distinction applies to authentication, authorization, file handling, session management, and denial-of-service claims.

---

## 6. Where the AI was strongest

The LLM was strongest at **breadth**.

It can quickly produce a checklist covering:

* Authentication
* Authorization
* Sessions
* Database access
* Error handling
* Logging
* File handling
* Availability
* Information disclosure

This reduces the probability of completely forgetting an important category.

---

## 7. Where the AI was weakest

The LLM is weakest at knowing the **actual trust boundaries and implementation details of this specific application**.

Because the application is represented only by a short description, the model cannot determine:

* Which endpoints are actually vulnerable.
* Which database queries are unsafe.
* Which roles actually exist.
* Which data is sensitive.
* Whether a particular mitigation is already implemented.
* Whether a particular attack succeeds.
* Whether a security control fails open or closed.

Therefore, the AI output should be treated as a **breadth-first checklist**, not as proof of vulnerabilities.

---

# 8. Manual model vs. AI model

| Aspect                          | Manual model                                                          | AI model                                                        |
| ------------------------------- | --------------------------------------------------------------------- | --------------------------------------------------------------- |
| STRIDE coverage                 | Covered all six categories                                            | Covered all six categories                                      |
| Assets                          | Identified major application assets                                   | Similar coverage                                                |
| Trust boundaries                | Focused on browser → application and application → backend components | Similar boundaries                                              |
| Breadth                         | Moderate                                                              | Higher                                                          |
| Application-specific accuracy   | Limited by generic application description                            | Limited by generic application description                      |
| Risk of unsupported assumptions | Lower if findings are explicitly marked "not tested"                  | Higher if the model treats generic vulnerabilities as confirmed |
| Best use                        | Establishing the actual system model                                  | Finding additional questions/threat categories                  |

---

# 9. Final assessment

The AI threat model was useful primarily because it provided a **broader checklist** of possible threats. Most of its STRIDE categories overlap with the manual model.

The most important difference is the distinction between a **possible threat** and a **confirmed vulnerability**.

For this generic DVWA application, the threat model establishes that SQL injection, information disclosure, spoofing, denial of service, repudiation failures, and privilege escalation are relevant threats. It does not establish that every one of these vulnerabilities is actually present.

The manual model is therefore more useful for defining the application's trust boundaries and conditions for security guarantees, while the LLM is useful for discovering additional threats that should be investigated.

---

# 10. Control Scorecard connection

The threat model also establishes the adversary for later security testing.

| Axis                 | Before testing                                                                                                             | Evidence                                 |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| **Threat model**     | Remote external attacker, initially unauthenticated, no administrative privileges, can modify HTTP requests and parameters | This threat model                        |
| **Guarantee**        | No security guarantee can be claimed for the generic application until individual controls are verified                    | Not yet tested                           |
| **Coverage**         | Not yet measured                                                                                                           | Not yet tested                           |
| **Bypass**           | Not yet attempted                                                                                                          | Not yet tested                           |
| **FP cost**          | Not yet measured                                                                                                           | Not yet tested                           |
| **Operational cost** | Not yet measured                                                                                                           | Not yet tested                           |
| **Observability**    | Unknown; depends on application logging                                                                                    | Source/configuration inspection required |
| **Failure mode**     | Unknown                                                                                                                    | Source/configuration/testing required    |

The most important lesson from this task is that a mitigation should always be expressed conditionally.

For example:

> "Parameterized queries prevent SQL injection"

is incomplete.

A stronger security claim is:

> **"User input cannot change SQL query structure, provided every database query uses parameterized statements and there are no alternate vulnerable query paths."**

The second statement identifies both the **guarantee** and the **condition** on which the guarantee depends.
