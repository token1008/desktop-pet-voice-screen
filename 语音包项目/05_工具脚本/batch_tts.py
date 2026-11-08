# -*- coding: utf-8 -*-
"""GPT-SoVITS 批量合成：读台词清单 JSON，逐句合成 wav。

用法: python batch_tts.py --lines <台词.json> --t2s <ckpt> --vits <pth> \
        --ref <参考wav> --ref-text "参考音频文字" --out-dir <dir> \
        [--speed 1.0] [--seed -1] [--version auto]
"""
import argparse
import json
import os
import sys
import wave
from pathlib import Path

GPT_ROOT = r"D:\GPT-SoVITS"
sys.path.insert(0, os.path.join(GPT_ROOT, "_shims"))  # jieba_fast 垫片优先于 site-packages
sys.path.insert(0, os.path.join(GPT_ROOT, "GPT_SoVITS"))
sys.path.insert(0, GPT_ROOT)
os.chdir(GPT_ROOT)  # 让相对路径的 pretrained_models 生效

from TTS_infer_pack import TTS  # noqa: E402
from process_ckpt import get_sovits_version_from_path_fast  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lines", required=True)
    ap.add_argument("--t2s", required=True)
    ap.add_argument("--vits", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--ref-text", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=-1)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--top-p", type=float, default=1.0)
    ap.add_argument("--top-k", type=int, default=15)
    a = ap.parse_args()

    # 自动探测 SoVITS 版本：返回兼容列表（如 ['v2','v2ProPlus',False] / ['v2','v4',True]），
    # 最后一个字符串是最具体/实际的训练版本
    det = get_sovits_version_from_path_fast(a.vits)
    version = None
    if isinstance(det, (list, tuple)):
        strs = [x for x in det if isinstance(x, str) and x.lower().startswith("v")]
        version = strs[-1] if strs else None
    elif isinstance(det, str):
        version = det
    print(f"[batch] SoVITS version 检测: {version}", flush=True)

    cfg = {"custom": {
        "device": "cpu",
        "is_half": False,
        "version": version or "v2",
        "t2s_weights_path": a.t2s,
        "vits_weights_path": a.vits,
        "cnhuhbert_base_path": "GPT_SoVITS/pretrained_models/chinese-hubert-base",
        "bert_base_path": "GPT_SoVITS/pretrained_models/chinese-roberta-wwm-ext-large",
    }}
    pipeline = TTS.TTS(cfg)

    data = json.loads(Path(a.lines).read_text(encoding="utf-8"))
    out_dir = Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for line in data["lines"]:
        params = {
            "text": line["text"],
            "text_lang": "zh",
            "ref_audio_path": a.ref,
            "prompt_text": a.ref_text,
            "prompt_lang": "zh",
            "top_k": a.top_k,
            "top_p": a.top_p,
            "temperature": a.temperature,
            "text_split_method": "cut0",
            "speed_factor": a.speed,
            "seed": a.seed,
        }
        try:
            chunks = []
            sr = None
            for chunk_sr, chunk in pipeline.run(params):
                sr = chunk_sr
                chunks.append(chunk)
            blob = b"".join(chunks)
            out_path = out_dir / f"{line['id']}_{line['name']}.wav"
            with wave.open(str(out_path), "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(sr)
                w.writeframes(blob)
            results.append({"id": line["id"], "ok": True, "file": str(out_path),
                            "bytes": len(blob), "sr": sr})
            print(f"[batch] OK {line['id']} {line['name']} {len(blob)}B @{sr}", flush=True)
        except Exception as e:
            results.append({"id": line["id"], "ok": False, "err": str(e)[:200]})
            print(f"[batch] FAIL {line['id']} {str(e)[:120]}", flush=True)

    (out_dir / "_results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = sum(1 for r in results if r["ok"])
    print(f"[batch] 完成 {ok}/{len(results)}", flush=True)


if __name__ == "__main__":
    main()
