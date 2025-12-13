def build_ass_subtitles(words, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write("""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Style: Default,Arial,72,&H00FFFFFF,&H00000000,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,3,0,2,30,30,60,1

[Events]
""")

        for w in words:
            start = ass_time(w["start"])
            end = ass_time(w["end"])
            word = w["word"].replace("{", "").replace("}", "")

            f.write(
                f"Dialogue: 0,{start},{end},Default,,0,0,0,,"
                f"{{\\fad(50,50)\\bord3\\shad1\\c&H00FFFF&}}{word}\n"
            )


def ass_time(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"
