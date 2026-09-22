# Local Research Agent

A research agent that searches the web, reasons over the evidence using an LLM (either a locally-run Qwen3 8B via LM Studio, or a cloud-hosted free model via OpenRouter), 
and produces a cited research report with no required API costs and no data leaving your machine unless you choose the cloud option.

## How It Works

1. You ask a research question.
2. The LLM breaks it down into effective search queries.
3. Python searches the web and collects real sources.
4. The LLM evaluates the evidence and decides: is this enough, or do we need to search more?
5. If more evidence is needed, the LLM proposes new search queries, and the cycle repeats.
6. Once enough evidence is gathered, the LLM writes a structured report citing real sources, which Python attaches automatically to guarantee accuracy.

The loop is bounded by several safety limits, so it never runs forever:
- A maximum number of search rounds
- A total time limit
- An early stop if new searches stop turning up meaningfully new information

## Web Interface (Hubble)

In addition to the command-line version (`main.py`), this project includes **Hubble** a web-based interface with live progress updates and a choice between two LLM backends:

- 🖥️ **Local**  runs fully offline (aside from web search), using your own LM Studio instance. Private, no cost, but slower on modest hardware.
- ⚡ **Cloud**  routes LLM calls through [OpenRouter](https://openrouter.ai)'s free tier for much faster responses, at the cost of your queries leaving your machine and being subject to OpenRouter's free-tier rate limits.


Run it with: 

python app.py 

Then open `http://127.0.0.1:5000` in your browser.

## Project Structure
```
research-agent/
├── main.py # Command-line entry point — runs the full research loop
├── app.py # Flask server powering the Hubble web interface
├── templates/
│ └── index.html # Hubble's front end (search bar, live progress, report view)
├── config/
│ ├── query_analysis.md # Instructions for breaking down the question
│ ├── decision.md # Instructions for judging evidence sufficiency
│ └── report.md # Instructions for writing the final report
├── llm/
│ └── client.py # Communication with both the local LLM and the cloud (OpenRouter) LLM
├── search/
│ └── search_engine.py # Web search + source tagging/deduplication
├── orchestrator/
│ └── pipeline.py # Query analysis, decision-making, report generation
└── requirements.txt 
```

## Setup

### Prerequisites
- Python 3.10+
- [LM Studio](https://lmstudio.ai/) with the Qwen3 8B model downloaded (for the local backend)
- a free [OpenRouter](https://openrouter.ai) account and API key (for the cloud backend)

### Installation

1. Clone this repository:
```
git clone https://github.com/DoniaMohamed611/research-agent.git
cd research-agent
```
2. Create and activate a virtual environment:
```
python -m venv venv
venv\Scripts\Activate.ps1
```

3. Install dependencies:
```   
pip install -r requirements.txt
```

4. **For the local backend:** start LM Studio, load the Qwen3 8B model, and start the local server (default: `http://127.0.0.1:1234`).

5. **For the cloud backend:** create a `.env` file in the project root with:
```
OPENROUTER_API_KEY=your_key_here
```
6. Run the command-line version:
``` 
python main.py
```
When prompted, type your research question. The final report will be saved as `research_report.md`.
Or run the web interface:
```
python app.py
```
Then open `http://127.0.0.1:5000` and choose Local or Cloud before searching.

## Example

**Input:** best cybersecurity certifications for beginners

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

- **Python controls the loop; the LLM only reasons.** The LLM never directly executes searches or controls how many rounds happen  it can only recommend, and Python enforces hard limits regardless of what the LLM wants. This makes the system predictable and debuggable.
- **Source citations are built by Python, not the LLM.** Early testing showed the LLM would sometimes hallucinate or misremember source URLs when asked to write them itself. The fix: Python tracks every source's real URL directly and appends an accurate Sources section after the LLM's analysis the LLM never touches citation URLs.
- **Low temperature for decision-making.** Using a high temperature caused the LLM to give inconsistent SEARCH_MORE/FINALIZE decisions on identical evidence. Lowering it to 0.1 made decisions consistent across repeated runs.
- **Instructions are split into focused files, not one large prompt.** Each stage (query analysis, evidence evaluation, report writing) has its own dedicated instruction file, since smaller, focused prompts get followed more reliably by a local 8B model than one long combined instruction set.
- **The LLM backend is swappable, not hardcoded.** `llm/client.py` exposes both a local (`ask_llm`) and cloud (`ask_llm_cloud`) function behind the same interface, so the rest of the pipeline doesn't need to know or care which one is actually running.

## Known Limitations

- Local LLM inference speed depends heavily on hardware a full research session can take 10-15+  minutes on a laptop GPU.
- The cloud backend depends on OpenRouter's free-tier availability and rate limits, which can vary.
- Search results come from DuckDuckGo (no API key required); result quality varies by topic.
- No per-source reliability scoring yet (planned future improvement).






