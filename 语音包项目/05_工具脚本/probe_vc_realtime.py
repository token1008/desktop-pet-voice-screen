# -*- coding: utf-8 -*-
"""qwen3-tts-vc-realtime 合成探针（WS SpeechSynthesizer + 复刻音色）。

用法: python probe_vc_realtime.py [model] [voice] [text]
"""
import json
import os
import sys
from pathlib import Path

PLUGIN_MCP_DIR = Path(r"C:\Users\a1575\.zcode\cli\plugins\cache\fufu-local\bailian-voice\0.6.1\mcp")
sys.path.insert(0, str(PLUGIN_MCP_DIR))
import server  # noqa: E402  workspace ws 端点
import dashscope
from dashscope.audio.tts_v2 import SpeechSynthesizer, AudioFormat

KEY = os.environ.get("BAILIAN_API_KEY") or Path(__file__).with_name("api_key_new.txt").read_text(encoding="utf-8").strip()
dashscope.api_key = KEY
dashscope.base_websocket_api_url = server.CFG["websocket_url"]
OUT = Path(r"D:\桌宠\语音包项目\03_合成音频\probe_vc.wav")


def probe(model, voice, text):
    collected = []
    err = []
    try:
        synth = SpeechSynthesizer(
            model=model, voice=voice,
            format=AudioFormat.WAV_24000HZ_MONO_16BIT,
            callback=__import__("types").SimpleNamespace(
                on_open=lambda: None,
                on_close=lambda: None,
                on_data=lambda data: collected.append(data),
                on_error=lambda e: err.append(str(e)),
                on_event=lambda e: None,
            ),
        )
        synth.call(text)
        if err:
            return {"model": model, "voice": voice[:40], "ok": False, "msg": err[0][:200]}
        blob = b"".join(collected)
        if not blob:
            return {"model": model, "voice": voice[:40], "ok": False, "msg": "无音频"}
        OUT.write_bytes(blob)
        return {"model": model, "voice": voice[:40], "ok": True, "bytes": len(blob), "saved": str(OUT)}
    except Exception as e:
        return {"model": model, "voice": voice[:40], "ok": False, "msg": str(e)[:200]}


if __name__ == "__main__":
    model = sys.argv[1] if len(sys.argv) > 1 else "qwen3-tts-vc-realtime"
    voice = sys.argv[2] if len(sys.argv) > 2 else "qwen-tts-vc-furinareal-voice-20261107212733988-d4a2"
    text = sys.argv[3] if len(sys.argv) > 3 else "看好了！优雅，永不过时！"
    print(json.dumps(probe(model, voice, text), ensure_ascii=False))
