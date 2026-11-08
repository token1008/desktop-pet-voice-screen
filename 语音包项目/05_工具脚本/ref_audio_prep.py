# -*- coding: utf-8 -*-
"""从 18s 候选样本中截取 GPT-SoVITS 参考音频：找最长连续语音段(4~9s)，转 32k/24k 单声道 wav。

用法: python ref_audio_prep.py <样本wav> <输出wav>
"""
import json
import re
import subprocess
import sys


def main():
    src, dst = sys.argv[1], sys.argv[2]
    # 1) silencedetect 找语音区间
    r = subprocess.run(
        ["ffmpeg", "-i", src, "-af", "silencedetect=noise=-32dB:d=0.4", "-f", "null", "-"],
        capture_output=True, text=True, errors="ignore",
    )
    silences, cur = [], None
    for m in re.finditer(r"silence_(start|end):\s*([-\d.]+)", r.stderr):
        kind, t = m.group(1), float(m.group(2))
        if kind == "start":
            cur = t
        elif cur is not None:
            silences.append((cur, t))
            cur = None
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", src], capture_output=True, text=True)
    total = float(p.stdout.strip())
    speech, pos = [], 0.0
    for s, e in silences:
        if s - pos > 0.3:
            speech.append((pos, s))
        pos = e
    if total - pos > 0.3:
        speech.append((pos, total))

    # 2) 选最长语音段，截到 8s 以内
    speech.sort(key=lambda x: x[1] - x[0], reverse=True)
    s, e = speech[0]
    dur = min(e - s, 8.0)
    out = {
        "segments": [[round(a, 2), round(b, 2)] for a, b in speech],
        "picked": {"start": round(s, 2), "dur": round(dur, 2)},
    }
    # 3) 提取（24k 单声道，与权重训练采样无关，GPT-SoVITS 会自动重采样）
    subprocess.run(
        ["ffmpeg", "-y", "-ss", f"{s:.2f}", "-t", f"{dur:.2f}", "-i", src,
         "-vn", "-ac", "1", "-ar", "32000", "-c:a", "pcm_s16le", dst],
        capture_output=True, text=True, check=True,
    )
    out["output"] = dst
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
