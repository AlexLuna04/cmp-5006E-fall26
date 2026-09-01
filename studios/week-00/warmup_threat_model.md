# Week 0 — Warmup Threat Model: WhatsApp

## 1. System

WhatsApp is a messaging app used by individuals to exchange messages, calls, images, files, and other information. Its users access the service through mobile devices and can also use linked devices such as computers.

## 2. System sketch

```text
                             Untrusted 
                              network
                                  │
                                  │ messages, login/
                                  │ registration attempts
                                  ▼
                         ╔════════════════╗
                         ║   WhatsApp     ║
                         ║    service     ║
                         ╚════════════════╝
                                  │
                    ══════════════╪══════════════
                         TRUST BOUNDARY
                                  │
                    messages / account data
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
             [ User's phone ]            [ Linked device ]
                    │                           │
                    └────── User-controlled ────┘
```

## 3. Threats

| # | Threat (STRIDE letter)     | Where it enters                                         | What an attacker gains                                                       | Mitigation                                                                                                                   | Guarantee, and its condition (axis 2)                                                                                                                                                                                                | Evidence                                                                                                                                                                          |
| - | -------------------------- | ------------------------------------------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | Spoofing (S)               | Account registration, verification, or account recovery | Control of the victim's WhatsApp account and the ability to act as that user | Account verification mechanisms and protection of the user's phone and verification credentials                              | An attacker cannot impersonate the account owner through the normal registration process, **provided the attacker cannot obtain or control the credentials and verification mechanisms required to register or recover the account** | The registration process requires account verification. The exact server-side checks and recovery controls cannot be determined from outside.                                     |
| 2 | Information disclosure (I) | User device or linked device                            | Access to private messages, files, contacts, or other account information    | Device security, screen lock, account security, and limiting access to linked devices                                        | Private messages remain inaccessible to an unauthorized person, **provided the attacker cannot unlock a trusted device or gain authorized access to a linked device/account**                                                        | Device and linked-device access can be observed as security boundaries. The internal storage and server-side handling of message data cannot be determined from the outside.      |
| 3 | Tampering (T)              | Compromised account or linked device                    | Ability to send messages or other content while appearing to be the victim   | Protecting the account and reviewing/removing unfamiliar linked devices                                                      | An attacker cannot send messages as the user, **provided the attacker has not obtained control of an authenticated account session or linked device**                                                                                | A user can observe messages sent from their account and can manage linked devices. The complete server-side authorization mechanism cannot be determined externally.              |
| 4 | Denial of service (D)      | Account registration/recovery or access to the service  | Prevents the legitimate user from accessing or using the account             | Account recovery and registration protections; maintaining access to the registered phone number and verification mechanisms | The user can regain account access after an unauthorized registration attempt, **provided the user still controls the required account recovery and verification mechanisms**                                                        | Account registration and verification behavior can be observed, but the exact recovery protections and their effectiveness against all attacks cannot be determined from outside. |

## 4. What I could not determine from the outside

I could not determine the exact server-side authentication, authorization, storage, recovery, and abuse-prevention mechanisms used by WhatsApp. To evaluate those controls more thoroughly, I would need access to the application's security architecture and the server-side implementation or documentation.
