def build_ass_subtitles(words, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write("""
[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Style: Default,Arial,64,&H00FFFFFF,&H000000FF,0,0,0,0,100,100,0,0,1,3,0,2,30,30,30,1

[Events]
""")

        for w in words:
            start = format_time(w["start"])
            end = format_time(w["end"])
            word = w["word"]

            f.write(
                f"Dialogue: 0,{start},{end},Default,,0,0,0,,{{\\c&H00FF00&}}{word}\n"
            )


def format_time(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"
