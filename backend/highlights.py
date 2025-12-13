def pick_highlights(segments, max_highlights):
    scored = []

    for s in segments:
        score = 0

        text = s["text"].lower()

        if len(text) > 40:
            score += 1

        if "!" in text or "?" in text:
            score += 1

        duration = s["end"] - s["start"]
        if duration > 5:
            score += 1

        scored.append((score, s))

    scored.sort(key=lambda x: x[0], reverse=True)

    return [s for _, s in scored[:max_highlights]]
