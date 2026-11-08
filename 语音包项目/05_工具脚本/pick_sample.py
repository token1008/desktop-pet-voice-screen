# -*- coding: utf-8 -*-
"""从纯享语音合集中挑选干净样本窗口：silencedetect 找语音区间，滑窗取语音占比最高的候选。"""
import json
import re
import subprocess
import sys


def speech_intervals(path):
    r = subprocess.run(
        ["ffmpeg", "-i", path, "-af", "silencedetect=noise=-32dB:d=0.7",
         "-f", "null", "-"],
        capture_output=True, text=True, errors="ignore",
    )
    text = r.stderr
    silences = []
    cur = None
    for m in re.finditer(r"silence_(start|end):\s*([-\d.]+)", text):
        kind, t = m.group(1), float(m.group(2))
        if kind == "start":
            cur = t
        elif cur is not None:
            silences.append((cur, t))
            cur = None
    # 音频总时长
    p = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path], capture_output=True, text=True)
    total = float(p.stdout.strip())
    # 反推语音区间
    speech, pos = [], 0.0
    for s, e in silences:
        if s - pos > 0.5:
            speech.append((pos, s))
        pos = e
    if total - pos > 0.5:
        speech.append((pos, total))
    return total, speech


def best_windows(total, speech, win=18.0, n=3, lo_frac=0.08, hi_frac=0.9):
    """在 [lo,hi] 区间滑窗，返回语音总时长最大的 n 个窗口（互相隔开）。"""
    lo, hi = total * lo_frac, total * hi_frac
    step = 0.5
    cands = []
    t = lo
    while t + win <= hi:
        dur = sum(max(0.0, min(e, t + win) - max(s, t)) for s, e in speech)
        cands.append((dur, t))
        t += step
    cands.sort(reverse=True)
    picked = []
    for dur, t in cands:
        if all(abs(t - pt) > 25 for _, pt in picked):
            picked.append((dur, t))
        if len(picked) == n:
            break
    return picked


def main():
    path = sys.argv[1]
    tag = sys.argv[2] if len(sys.argv) > 2 else "sample"
    total, speech = speech_intervals(path)
    picks = best_windows(total, speech)
    out = []
    for i, (dur, t) in enumerate(picks, 1):
        dst = f"{tag}_cand{i}.wav"
        subprocess.run(
            ["ffmpeg", "-y", "-ss", f"{t:.2f}", "-t", "18", "-i", path,
             "-vn", "-ac", "1", "-ar", "24000", "-c:a", "pcm_s16le", dst],
            capture_output=True, text=True,
        )
        out.append({"file": dst, "start": round(t, 1), "speech_sec": round(dur, 1)})
    print(json.dumps({"total": round(total, 1), "speech_segments": len(speech),
                      "candidates": out}, ensure_ascii=False))


if __name__ == "__main__":
    main()
