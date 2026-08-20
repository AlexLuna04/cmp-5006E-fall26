# Ethics and Scope

This is a security course. Students will learn to break real classes of system.
That knowledge is dual-use, and this document is the boundary that keeps it
defensive.

**Read this before Week 1. You will sign it (a PR acknowledging it) as part of the
Week 0 deliverable.**

---

## The one rule

> ## You attack only targets you own or have written authorization to test.

Every lab in this course is built so that following this rule is the *easy* path:
the targets ship as Docker containers that run on your own machine, on an isolated
network. You never need an external target, so you never have an excuse to touch
one.

**Attacking any system you do not own or lack written authorization for is grounds
for failing the course**. Independent of, and in addition to, any legal
consequence under Ecuadorian law (COIP arts. on unauthorized access) or the law of
wherever the target sits.

This is not a formality. It has ended security careers before they started.

---

## Why we sandbox everything

| | |
|---|---|
| **Targets** | Docker containers, pinned by digest, on a dedicated Docker network |
| **Network** | labs bind to `127.0.0.1` only; no lab target is exposed to your LAN |
| **Data** | every dataset is synthetic or public-domain; no real personal data, ever |
| **LLM targets** | the vulnerable AI app runs a *local* model or a mock. Your attacks never leave the machine |
| **Teardown** | `python -m seclab.targets --down` removes containers and networks |

If a lab ever asks you to point a tool at a hostname you do not recognize, **stop
and ask.** That is a bug in the lab, not an instruction.

---

## Why Week 14 exists

Week 14 covers **offensive AI capability**. Phishing generated at scale, deepfake
voice for vishing, automated vulnerability discovery.

We teach it for one reason: **a defender who does not understand the offense builds
defenses against the threat they imagine rather than the one they face.** A
phishing filter tuned against 2015-era grammar mistakes is useless against a model
that writes flawless, context-aware lures.

The rules for that week are stricter, not looser:

- **The deliverable is always the defense.** You may analyze an offensive
  technique; you submit the detection or mitigation.
- **No live targets, no real people.** Social-engineering exercises use role-play
  within the class, with consent, never a real third party.
- **No functional malware.** You may explain how AI lowers the cost of malware
  authorship; you do not submit a working sample.

If you are unsure whether something crosses the line, it does. Ask first.

---

## Responsible disclosure: practised, not just discussed

Several labs will have you find a real bug in an *intentionally* vulnerable app.
That is safe. But the **habit** you build is the one you will use when you
accidentally find a real bug in a real system, which will happen in your career,
probably by accident, probably soon.

So we practise the ritual on the safe targets:

1. **Stop.** Do not pivot, do not escalate beyond proof, do not exfiltrate real
   data.
2. **Document** minimally: what, where, and a single proof-of-concept.
3. **Report** to the owner through a private channel, with a reasonable remediation
   window before any disclosure.
4. **Never** publish a working exploit against a live system before it is fixed.

Weeks 6–10 each include a "you found it, now what?" beat that rehearses this.

---

## Using AI in this course

AI use is **allowed and encouraged** — this is a course about, among other things,
using AI as a security instrument. But:

- Every AI-assisted deliverable carries an `AI_LOG.md` entry (see
  [`START-HERE.md`](START-HERE.md), § *Using AI in this course*): what you asked, which model, what you kept, what
  you rejected.
- **You are responsible for what you submit.** An LLM that hallucinates a CVE
  number, invents a `mysql_real_escape_string` bypass that does not work, or
  fabricates a legal citation for the LOPDP section is *your* error once you paste
  it. The checkpoints are closed-book precisely so that this responsibility is
  real.
- ⚠️ **Do not paste real secrets, real client data, or the class's private lab
  details into a hosted model.** This is itself one of the privacy lessons of the
  course. Practise it on yourself.

---

## The disclosure you sign

Your Week 0 submission includes `week00/acknowledgment.md` containing exactly:

```markdown
I have read resources/ethics-and-scope.md. I understand that I will attack only
targets I own or am authorized to test, that doing otherwise is grounds for
failing this course and may be a crime, and that the deliverable for any
offensive technique in this course is a defense.

Signed: <name>, <date>
```

No acknowledgment, no lab access. It is the one hard gate in the course.
