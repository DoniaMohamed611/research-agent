import time
from search.search_engine import search_web, format_new_results
from orchestrator.pipeline import analyze_query, make_decision, generate_report

MAX_ROUNDS = 4


if __name__ == "__main__":
    original_query = input("What do you want to research? ")
    all_evidence = ""
    source_map = {}
    next_index = 1
    round_number = 1

    print("Analyzing the question...")
    queries_to_run = analyze_query(original_query)
    print(f"Initial search queries: {queries_to_run}")

    already_searched_queries = set()

    start_time = time.time()
    MAX_TIME_SECONDS = 1500

    while round_number <= MAX_ROUNDS:
        elapsed = time.time() - start_time
        if elapsed > MAX_TIME_SECONDS:
            print(f"\nTime limit reached ({elapsed:.0f}s elapsed). Stopping and generating report now.")
            break

        print(f"\n--- ROUND {round_number} ---")

        fresh_queries = []
        for q in queries_to_run:
            if q in already_searched_queries:
                print(f"Skipping already-searched query: '{q}'")
            else:
                fresh_queries.append(q)

        if not fresh_queries:
            print("No new queries to search this round. Stopping.")
            break

        print(f"Searching for: {fresh_queries}")

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

        if total_results_this_round > 0:
            new_ratio = new_tags_this_round / total_results_this_round
        else:
            new_ratio = 0

        print(f"New information this round: {new_tags_this_round}/{total_results_this_round} results ({new_ratio:.0%})")

        if new_ratio < 0.2 and round_number > 1:
            print("Very little new information found. Stopping early.")
            break

        print("Asking the LLM to decide...")
        decision = make_decision(original_query, all_evidence)
        print("Decision:", decision)

        if decision["decision"] == "FINALIZE":
            print("\nLLM decided we have enough evidence. Stopping.")
            break

        queries_to_run = decision.get("next_queries", [])
        if not queries_to_run:
            print("\nSEARCH_MORE but no next_queries given. Stopping to be safe.")
            break

        round_number += 1

    else:
        print(f"\nHit MAX_ROUNDS ({MAX_ROUNDS}). Stopping regardless of LLM's opinion.")

    print("\nGenerating final report...")
    report = generate_report(original_query, all_evidence, source_map)
    with open("research_report.md", "w", encoding="utf-8") as f:
        f.write(report)

    print("\nReport saved to research_report.md")