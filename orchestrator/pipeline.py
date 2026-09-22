import json
from llm.client import ask_llm, ask_llm_cloud, load_rules


def get_llm_function(backend):
    if backend == "cloud":
        return ask_llm_cloud
    return ask_llm


def analyze_query(question, backend="local"):
    rules = load_rules("query_analysis.md")
    llm = get_llm_function(backend)

    prompt = f"""{rules}

## Research question
{question}

Now output the search queries as JSON, following the format above.
"""

    raw_reply = llm(prompt, temperature=0.1)

    if raw_reply is None:
        print("LLM call failed. Using original question instead.")
        return [question]

    try:
        result = json.loads(raw_reply)
        queries = result.get("queries", [])
        if queries:
            return queries
        else:
            return [question]
    except json.JSONDecodeError:
        print("Warning: LLM did not return valid JSON for query analysis. Using original question instead.")
        return [question]


def make_decision(question, evidence_text, backend="local"):
    rules = load_rules("decision.md")
    llm = get_llm_function(backend)

    prompt = f"""{rules}

## Research question
{question}

## Evidence
{evidence_text}

Now output your decision as JSON, following the format above.
"""

    raw_reply = llm(prompt, temperature=0.1)

    if raw_reply is None:
        print("LLM call failed. Finalizing with current evidence.")
        return {"decision": "FINALIZE", "reason": "Fallback due to LLM server error."}

    try:
        decision = json.loads(raw_reply)
        return decision
    except json.JSONDecodeError:
        print("Warning: LLM did not return valid JSON. Raw reply was:")
        print(raw_reply)
        return {"decision": "FINALIZE", "reason": "Fallback due to invalid JSON."}


def generate_report(question, evidence_text, source_map, backend="local"):
    rules = load_rules("report.md")
    llm = get_llm_function(backend)

    prompt = f"""{rules}

## Research question
{question}

## Evidence
{evidence_text}

Now write the full report, following the structure above exactly.
"""

    report_text = llm(prompt, temperature=0.3)

    if report_text is None:
        report_text = "*(Report generation failed due to an LLM server error. Raw evidence is available below.)*\n\n" + evidence_text

    sources_section = "\n\n### Sources\n"
    for tag in sorted(source_map.keys(), key=lambda t: int(t[1:])):
        sources_section += f"- [{tag}]: {source_map[tag]}\n"

    return report_text + sources_section