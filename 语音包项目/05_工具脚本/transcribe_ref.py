# -*- coding: utf-8 -*-
"""faster-whisper 转录参考音频文字（GPT-SoVITS 零样本合成的 prompt_text）。

用法: python transcribe_ref.py <wav...>
"""
import json
import sys

from faster_whisper import WhisperModel

MODEL_DIR = r"D:\GPT-SoVITS\whisper_models\faster-whisper-base"

model = WhisperModel(MODEL_DIR, device="cpu", compute_type="int8")
out = {}
for path in sys.argv[1:]:
    segments, info = model.transcribe(path, language="zh", vad_filter=True)
    text = "".join(s.text for s in segments).strip()
    out[path] = text
    print(f"{path} -> {text}", flush=True)
print(json.dumps(out, ensure_ascii=False))
