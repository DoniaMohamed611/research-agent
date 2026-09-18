from ddgs import DDGS


def search_web(query, max_results=5):
    try:
        results = DDGS().text(query, max_results=max_results)
        return results
    except Exception as e:
        print(f"Warning: search failed for query '{query}': {e}")
        return []


def format_new_results(results, start_index, source_map):
    formatted = ""
    already_seen_urls = set(source_map.values())
    current_index = start_index

    for r in results:
        url = r['href']
        if url in already_seen_urls:
            continue

        tag = f"S{current_index}"
        formatted += f"[{tag}] (source: {url})\n"
        formatted += f"{r['body']}\n\n"
        source_map[tag] = url
        already_seen_urls.add(url)
        current_index += 1

    return formatted