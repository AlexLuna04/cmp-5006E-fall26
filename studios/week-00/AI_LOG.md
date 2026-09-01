# AI Log

## Week 0 — CVE check

**Tool:** ChatGPT

**What I asked:** Helped me run the Week 0 CVE measurement with my local `qwen2.5:3b` model.

**What I got:** Guidance for running the ten CVE questions and three repeated questions. The model correctly identified 7 of 10 cases, gave one partial answer, one wrong answer, and one refusal.

**What I did with it:** I ran the prompts through my local Qwen model using `seclab.llm`, preserved the model's answers in `.llm_cache/`, and independently checked the CVE identifiers and publication dates against MITRE/NVD before recording the results.

**Did I understand it?** Yes. I learned that a CVE identifier can look plausible and still be associated with the wrong vulnerability, so I need to verify the identifier itself rather than trusting the model's explanation.

## Week 0 — Threat model

**Tool:** ChatGPT

**What I asked:** Helped me structure a short outsider threat model for WhatsApp using STRIDE.

**What I got:** Suggestions for possible threats, mitigations, conditions for those mitigations, and a simple system diagram.

**What I did with it:** I used the suggestions to create `warmup_threat_model.md` and focused the model on threats that can reasonably be considered from an outsider's perspective.

**Did I understand it?** Yes. I understood that a threat model should distinguish between a possible threat, its mitigation, the condition under which the mitigation works, and evidence that the control has actually been tested.

## Week 0 — Document review

**Tool:** ChatGPT

**What I asked:** I provided all of my Week 0 deliverables and asked ChatGPT to identify spelling, grammatical and format errors and improve the grammar and structure while preserving the original content and meaning.

**What I got:** Suggestions for spelling, grammar, clarity, and document structure. The content and technical conclusions were kept unchanged.

**What I did with it:** I reviewed the suggestions and used them to correct and polish my Week 0 deliverables without changing the underlying information or results.

**Did I understand it?** Yes. I understood the changes made to the documents and kept responsibility for the final content of my submission.
