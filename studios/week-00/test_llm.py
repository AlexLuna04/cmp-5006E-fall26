from seclab import LLM

llm = LLM()

r = llm.complete(
    "What is the CVE identifier for the Heartbleed vulnerability? "
    "Also give the year it was published."
)

print(r.text)