# -*- coding: utf-8 -*-
"""funasr Paraformer 转录参考音频（中文 ASR 专用，比 whisper-base 准）。

用法: python transcribe_funasr.py <wav...>
"""
import json
import sys

from funasr import AutoModel

model = AutoModel(
    model="paraformer-zh",
    vad_model="fsmn-vad",
    disable_update=True,
)
out = {}
for path in sys.argv[1:]:
    res = model.generate(input=path, batch_size_s=60)
    text = (res[0].get("text") or "").strip() if res else ""
    out[path] = text
    print(f"{path} -> {text}", flush=True)
print(json.dumps(out, ensure_ascii=False))
