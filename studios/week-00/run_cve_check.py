from seclab import LLM

llm = LLM()

questions = [
    "What is the CVE identifier for the Heartbleed vulnerability in OpenSSL? Also give the year it was published.",
    "What is the CVE identifier for the Shellshock vulnerability in GNU Bash? Also give the year it was published.",
    "What is the CVE identifier for the Dirty COW vulnerability in the Linux kernel? Also give the year it was published.",
    "What is the CVE identifier for the Apache Struts vulnerability used in the 2017 Equifax breach? Also give the year it was published.",
    "What is the CVE identifier for EternalBlue, the Windows SMBv1 vulnerability used by WannaCry? Also give the year it was published.",
    "What is the CVE identifier for the Meltdown CPU vulnerability? Also give the year it was published.",
    "What is the CVE identifier for Spectre variant 1 (bounds check bypass)? Also give the year it was published.",
    "What is the CVE identifier for the Log4Shell vulnerability in Apache Log4j 2? Also give the year it was published.",
    "What is the CVE identifier for the xz-utils backdoor? Also give the year it was published.",
    "What is the CVE identifier for the Mirai botnet? Also give the year it was published.",
]

for i, question in enumerate(questions, 1):
    print(f"\n{'=' * 70}")
    print(f"QUESTION {i}")
    print(f"{'=' * 70}")
    print(question)
    
    r = llm.complete(question)
    
    print("\nMODEL ANSWER:")
    print(r.text)