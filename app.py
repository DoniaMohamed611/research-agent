import threading
import time
from flask import Flask, render_template, request, jsonify

from search.search_engine import search_web, format_new_results
from orchestrator.pipeline import analyze_query, make_decision, generate_report

app = Flask(__name__)

MAX_ROUNDS = 4
MAX_TIME_SECONDS = 1500

# This holds the current research's live progress.
# Only one research runs at a time in this simple version.
state = {
    "running": False,
    "round": 0,
    "log": [],
    "done": False,
    "report": None,
    "waiting_for_llm": False,
    "start_time": None
}


def run_research(question, backend):
    state["running"] = True
    state["round"] = 0
    state["log"] = []
    state["done"] = False
    state["report"] = None
    state["waiting_for_llm"] = False
    state["start_time"] = time.time()

    all_evidence = ""
    source_map = {}
    next_index = 1
    round_number = 1
    already_searched_queries = set()

    state["log"].append("Analyzing the question...")
    state["waiting_for_llm"] = True
    queries_to_run = analyze_query(question, backend=backend)
    state["waiting_for_llm"] = False
    state["log"].append(f"Initial search queries: {queries_to_run}")

    start_time = time.time()

    while round_number <= MAX_ROUNDS:
        elapsed = time.time() - start_time
        if elapsed > MAX_TIME_SECONDS:
            state["log"].append(f"Time limit reached ({elapsed:.0f}s). Stopping.")
            break

        state["round"] = round_number
        state["log"].append(f"--- Round {round_number} ---")

        fresh_queries = []
        for q in queries_to_run:
            if q in already_searched_queries:
                state["log"].append(f"Skipping already-searched query: '{q}'")
            else:
                fresh_queries.append(q)

        if not fresh_queries:
            state["log"].append("No new queries to search this round. Stopping.")
            break

        state["log"].append(f"Searching for: {fresh_queries}")

        total_results_this_round = 0
        new_tags_this_round = 0

        for q in fresh_queries:
            already_searched_queries.add(q)
            results = search_web(q)
            total_results_this_round += len(results)

            tags_before = len(source_map)
            new_evidence = format_new_results(results, next_index, source_map)
            tags_after = len(source_map)

            all_evidence += new_evidence
            next_index += (tags_after - tags_before)
            new_tags_this_round += (tags_after - tags_before)

        new_ratio = (new_tags_this_round / total_results_this_round) if total_results_this_round > 0 else 0
        state["log"].append(f"New information this round: {new_tags_this_round}/{total_results_this_round} ({new_ratio:.0%})")

        if new_ratio < 0.2 and round_number > 1:
            state["log"].append("Very little new information found. Stopping early.")
            break

        state["log"].append("Asking the LLM to decide...")
        state["waiting_for_llm"] = True
        decision = make_decision(question, all_evidence, backend=backend)
        state["waiting_for_llm"] = False
        state["log"].append(f"Decision: {decision.get('decision')} — {decision.get('reason')}")

        if decision["decision"] == "FINALIZE":
            state["log"].append("Enough evidence gathered. Stopping.")
            break

        queries_to_run = decision.get("next_queries", [])
        if not queries_to_run:
            state["log"].append("SEARCH_MORE but no next_queries given. Stopping.")
            break

        round_number += 1
    else:
        state["log"].append(f"Hit MAX_ROUNDS ({MAX_ROUNDS}). Stopping.")

        state["log"].append("Generating final report...")
    state["waiting_for_llm"] = True
    report = generate_report(question, all_evidence, source_map, backend=backend)
    state["waiting_for_llm"] = False

    state["report"] = report
    state["done"] = True
    state["running"] = False


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/start", methods=["POST"])
def start():
    if state["running"]:
        return jsonify({"error": "A research is already running. Please wait for it to finish.", "already_running": True}), 409

    question = request.json.get("question", "").strip()
    if not question:
        return jsonify({"error": "Please type a question first."}), 400

    backend = request.json.get("backend", "local")

    thread = threading.Thread(target=run_research, args=(question, backend))
    thread.start()

    return jsonify({"started": True})


@app.route("/status")
def status():
    return jsonify(state)


if __name__ == "__main__":
    app.run(debug=True)