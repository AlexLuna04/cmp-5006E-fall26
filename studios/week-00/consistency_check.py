from seclab import LLM

llm = LLM()

questions = {
    "Heartbleed": "What is the CVE identifier for the Heartbleed vulnerability? Also give the year it was published.",
    "xz-utils": "What is the CVE identifier for the xz-utils backdoor? Also give the year it was published.",
    "Mirai": "What is the CVE identifier for the Mirai botnet? Also give the year it was published.",
}

for name, question in questions.items():
    print(f"\n{'=' * 70}")
    print(name)
    print(f"{'=' * 70}")

    for i in range(5):
        r = llm.complete(question, seed=i)
        print(f"\nTRIAL {i}:")
        print(r.text.strip())