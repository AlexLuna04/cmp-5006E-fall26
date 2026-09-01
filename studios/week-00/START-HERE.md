# CMP-5006 — Week 0

Self-paced, due **before our first class**. About 2 hours, most of
it waiting on a download.

**For most of you this is your first security course.** Nothing here assumes you
already know what a CVE is, or what a threat model is. Each step
explains its own vocabulary. 

Everything runs on your own laptop: **no GPU, no paid API, no cloud account, no
credit card.** 

---

## Step 0 · Read and sign the scope statement (15 min)

Read **[`ethics-and-scope.md`](ethics-and-scope.md)**. It is short, and it is the
one document in this course with legal weight.

Then create `week00/acknowledgment.md` in your repository containing exactly the
statement given at the end of that file, with your name and the date.

> **No `acknowledgment.md`, no lab access.** This is the one non-negotiable rule of
> the course. Do it first, not last.

*(The statement refers to `resources/ethics-and-scope.md`. That is where the file
lives in the full course repository. In this bundle it is at the top level. Same
document; sign it as written.)*

## Step 1 · Start the model download now (~2 GB)

Install [Ollama](https://ollama.com), then run this and let it work while you read
on:

```bash
ollama pull qwen2.5:3b       # ~2 GB, needs ~4 GB free RAM
ollama pull qwen2.5:1.5b     # use this instead if you have ≤8 GB RAM
```

> **If Ollama will not install, you are not behind.** There is a manual backend
> that works with any chat interface you can open in a browser. You will run fewer
> trials, say so in your write-up, and lose no marks.

## Step 2 · Set up Python (30 min, mostly waiting)

From **this folder** (the one containing `seclab/`):

```bash
python3 --version            # need 3.10+
python3 -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m seclab.doctor      # → save the output
python -m seclab.doctor > doctor.txt
```

Run it until it prints `→ Ready.`

⚠️ **Run everything from this folder.** `ModuleNotFoundError: seclab` means Python
cannot see the course package from where you are.

Reading the output: `✔` is fine, `✗` is a real failure that tells you what to fix,
and **`!` is a warning, not a blocker.** If the LLM line says `manual`, that is a
**pass**.

### About Docker

`doctor` will warn if Docker is missing. **That is not a blocker, and Docker is not
required for any graded work.** From week 6 the lab applications run in containers
for isolation, but they are plain Python and run without one. You can install
Docker later; do not lose week 0 to it.

## Step 3 · Look at what is listening on your machine (15 min)

This is the first security observation of the course, and it is about your own
laptop. Do it in an **empty directory**.

```bash
mkdir /tmp/exposure && cd /tmp/exposure
python3 -m http.server 8000
```

In a second terminal:

```bash
lsof -iTCP:8000 -sTCP:LISTEN -P -n     # macOS
ss -ltnp | grep 8000                   # Linux
```

Note the address it is **bound** to. Then stop the server (Ctrl-C), start it again
with `python3 -m http.server 8000 --bind 127.0.0.1`, and look once more.

Vocabulary, in one paragraph: a **port** is a numbered door on your machine; a
program **listening** on a port is waiting for connections at that door. What it is
**bound** to says *which doors*, `127.0.0.1` (also called **loopback**) means only
this computer can knock, while `0.0.0.0` means every network interface, so anything
on your Wi-Fi can. macOS shows the second case as `*:8000`; Linux shows
`0.0.0.0:8000` or `[::]:8000`. Same thing, different notation.

⚠️ **Stop the server when you are done.** The default really did serve that
directory to everyone on your network. That is the lesson.

Write `week00/exposure.md`: both addresses you observed, how you can tell them
apart, and who could reach the server in each case.

**Check your laptop's status:** run `lsof -iTCP -sTCP:LISTEN -P -n` with no
server of your own running, and see what else on your laptop is listening. You may
find something you did not install on purpose. That is a real finding. Post it.

## Step 4 · Measure your model (25 min)

Full instructions in **[`cve-check.md`](cve-check.md)**. This is the graded
measurement, and it is the most important thing you do this week.

In short: you ask your model for ten vulnerability identifiers, **look every single
one up** in the public catalogue, record what actually happened, ask three of the
questions five times to see whether the answers stay the same, and finish with one
sentence — *"I would trust this model for this task if ___."*

You are not being graded on how well your model does. You are being graded on
whether you measured it honestly.

## Step 5 · Your first threat model (20 min)

Use **[`threat-model-template.md`](threat-model-template.md)**, start at §5, the
twenty-minute version. Pick an app you use every day and model it as an outsider.

Three plausible threats beat ten copied from a textbook, and *"I could not
determine this from the outside"* is a valuable row, not a gap.

---

## What to hand in

| # | Artifact | From |
|---|---|---|
| 1 | `acknowledgment.md` | step 0 — **the gate** |
| 2 | `doctor.txt` | step 2 |
| 3 | `exposure.md` | step 3 |
| 4 | `cve_check.md` | step 4 |
| 5 | `warmup_threat_model.md` | step 5 |
| 6 | `AI_LOG.md`, started | below |


Keep everything in one repository for the semester, with a `week00/` folder for
this week. **Also keep the `.llm_cache/` folder that appears once you call a model. 
Do not delete it, and commit it.** The cache is not an optimization, it is your
audit trail: it is what makes "I ran five trials" checkable rather than merely
claimed.

### Failure Atlas entry format

You will write one every week. Copy this shape:

```markdown
### [Wk0] Asked for "the Mirai CVE", model answers with a real CVE for a different bug
**Setup:** qwen2.5:3b, temp 0, asked "what is the CVE identifier for the Mirai botnet?"
**Expected:** no single CVE exists. Mirai spread by trying default credentials
  across many device models, which is not one catalogued software flaw.
**Observed:** "CVE-2016-10401", stated flatly with no hedging. That identifier is
  real, but it is a hardcoded password in one ZyXEL modem. The same class of
  weakness Mirai abused, not "the Mirai CVE."
**Category:** wrong-but-confident
**Why it matters:** the identifier resolves, so a skim review passes it. Anyone
  acting on my report would patch one modem model and believe they had addressed
  Mirai.
```

**Categories:** `fabricated` · `wrong-but-confident` · `inconsistent` ·
`bypassed` · `false-positive` · `undetected`.

**"Why it matters" is the field that counts.** One sentence: what would break, or
who would be misled, if this shipped?

For the reply, name something specific. A threat they missed, another explanation
for what their model did, or a way to test their claim. One or two sentences.

---

## Using AI in this course

**You may use AI assistants on any work in this course. You must log it, and you
own what you submit.** An undisclosed AI-assisted submission is an honor code
violation; a disclosed one is normal professional practice. There is no penalty for use,
 only for hiding it.

Keep `AI_LOG.md` in your repository and append an entry whenever an assistant
materially shapes work you submit:

```markdown
## Week 0 — CVE check

**Tool:** Claude / ChatGPT / Copilot / local qwen2.5:3b
**What I asked:** "What is the CVE number for the xz-utils backdoor?"
**What I got:** CVE-2024-3094, plus a confident claim about the disclosure date.
**What I did with it:** Checked both against MITRE. Identifier right, date wrong.
  Recorded it as a partial hit and kept the model's exact wording as evidence.
**Did I understand it?** Yes. I now check dates separately from identifiers,
  because the model was right about one and wrong about the other in one sentence.
```

**That last field is the one that matters**, and writing "no" is allowed.

Two rules specific to security work:

1. ⚠️ **Never paste real secrets or personal data into a hosted model**, not
   credentials, not client data, not anything you stumble across in a lab. A hosted
   model is a third party you have just disclosed data to. Lab data is synthetic by
   design; keep it that way.
2. ⚠️ **Verify every factual claim against a primary source before citing it.** CVE
   numbers against MITRE or NVD, standards against the RFC, legal obligations
   against the law's text. "The model said so" is not a citation, and a fabricated
   citation in a security report is worse than none. A reader who trusts you will
   act on it.

Two checkpoints later in the term are individual and closed-book. That is what
lets this policy stay permissive.

