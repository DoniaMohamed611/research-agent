# Local Research Agent
A research agent that searches the web, reasons over the evidence using a locally-run LLM (Qwen3 8B via LM Studio), 
and produces a cited research report  with no external API costs and no data leaving your machine except the search queries themselves.

## How It Works
1. You ask a research question.
2. The LLM breaks it down into effective search queries.
3. Python searches the web and collects real sources.
4. The LLM evaluates the evidence and decides: is this enough, or do we need to search more?
5. If more evidence is needed, the LLM proposes new search queries, and the cycle repeats.
6. Once enough evidence is gathered, the LLM writes a structured report citing real sources,
 which Python attaches automatically to guarantee accuracy.

The loop is bounded by several safety limits, so it never runs forever:
- A maximum number of search rounds
- A total time limit
- An early stop if new searches stop turning up  meaningfully new information

## Setup

### Prerequisites
- Python 3.10+
- [LM Studio](https://lmstudio.ai/) with the Qwen3 8B model downloaded
- No paid API keys required everything runs locally except the web search itself

### Installation

1. Clone this repository:

git clone https://github.com/DoniaMohamed611/research-agent.git
cd research-agent

2. Create and activate a virtual environment:

python -m venv venv
venv\Scripts\Activate.ps1

3. Install dependencies:

pip install -r requirements.txt

4. Start LM Studio, load the Qwen3 8B model, and start the local server (default: `http://127.0.0.1:1234`).

5. Run the agent:

python main.py

6. When prompted, type your research question. The final report will be saved as `research_report.md`.


## Example

**Input:**  best cybersecurity certifications for beginners


**Output (research_report.md):**
```markdown
# Research Report
## Topic: best cybersecurity certifications for beginners

### Executive Summary
The most recommended cybersecurity certifications for beginners include CompTIA
Security+, the Google Cybersecurity Certificate, and CompTIA Network+...

### Key Findings
1. CompTIA Security+ is consistently cited as the top certification for
   beginners due to its broad applicability and industry recognition [S1][S2][S3].
...

### Sources
- [S1]: https://www.snhu.edu/about-us/newsroom/stem/best-cybersecurity-certifications-for-beginners
- [S2]: https://www.coursera.org/articles/popular-cybersecurity-certifications
...
```

## Design Decisions

- **Python controls the loop; the LLM only reasons.** The LLM never directly executes searches or controls how many rounds happen it can only recommend, and Python enforces hard limits regardless of what the LLM wants. This makes the system predictable and debuggable.
- **Source citations are built by Python, not the LLM.** Early testing showed the LLM would sometimes hallucinate or misremember source URLs when asked to write them itself. The fix: Python tracks every source's real URL directly and appends an accurate Sources section after the LLM's analysis the LLM never touches citation URLs.
- **Low temperature for decision-making.** Using a high temperature caused the LLM to give inconsistent SEARCH_MORE/FINALIZE decisions on identical evidence. Lowering it to 0.1 made decisions consistent across repeated runs.
- **Instructions are split into focused files, not one large prompt.** Each stage (query analysis, evidence evaluation, report writing) has its own dedicated instruction file, since smaller, focused prompts get followed more reliably by a local 8B model than one long combined instruction set.

## Known Limitations
- Local LLM inference speed depends heavily on hardware a full research session can take 10-20+ minutes on a laptop GPU.
- Search results come from DuckDuckGo (no API key required); result quality varies by topic.
- No per-source reliability scoring yet (planned future improvement).

## Future Improvements
- A graphical interface (in progress)
- Per-source evidence scoring before the decision step
- Support for swapping in different local or hosted LLMs

