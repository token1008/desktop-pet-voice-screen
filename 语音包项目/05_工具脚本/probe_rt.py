# -*- coding: utf-8 -*-
"""qwen3-tts-vc-realtime realtime 协议合成探针（QwenTtsRealtime + 复刻音色）。

用法: python probe_rt.py [voice_id] [text]
Key 从同目录 api_key_new.txt 读取；BAILIAN_API_KEY 环境变量优先。
"""
import base64
import json
import os
import struct
import sys
import threading
import wave
from pathlib import Path

PLUGIN_MCP_DIR = Path(r"C:\Users\a1575\.zcode\cli\plugins\cache\fufu-local\bailian-voice\0.6.1\mcp")
sys.path.insert(0, str(PLUGIN_MCP_DIR))
import server  # noqa: E402  workspace ws 端点
import dashscope
from dashscope.audio.qwen_tts_realtime import QwenTtsRealtime, QwenTtsRealtimeCallback

# realtime 协议走官方默认端点（业务空间网关不路由 realtime），workspace 用参数区分
KEY = os.environ.get("BAILIAN_API_KEY") or Path(__file__).with_name("api_key_new.txt").read_text(encoding="utf-8").strip()
dashscope.api_key = KEY
dashscope.base_websocket_api_url = "wss://dashscope.aliyuncs.com/api-ws/v1/inference"
MODEL = "qwen3-tts-vc-realtime"
WORKSPACE = "NONE"
OUT = Path(r"D:\桌宠\语音包项目\03_合成音频\probe_rt.wav")
SAMPLE_RATE = 24000


class CB(QwenTtsRealtimeCallback):
    def __init__(self):
        self.chunks = []
        self.errors = []
        self.events = []
        self.session_ready = threading.Event()
        self.done = threading.Event()

    def on_open(self):
        pass

    def on_event(self, message):
        ev = message if isinstance(message, dict) else json.loads(message)
        t = ev.get("type", "")
        self.events.append(json.dumps(ev, ensure_ascii=False)[:400])
        if "audio" in t and ev.get("delta"):
            self.chunks.append(base64.b64decode(ev["delta"]))
        if t == "session.created":
            self.session_ready.set()
        if t.startswith("response.") and ("done" in t or "fail" in t):
            self.done.set()
        if t == "error" or "fail" in t.lower():
            self.errors.append(str(ev)[:300])
            self.done.set()

    def on_close(self, code, msg):
        self.events.append(f"CLOSE code={code} msg={msg}")
        self.done.set()


def synth(text, voice_id):
    cb = CB()
    tts = QwenTtsRealtime(model=MODEL, callback=cb, workspace=None if WORKSPACE == "NONE" else WORKSPACE)
    tts.connect()
    if not cb.session_ready.wait(timeout=15):
        return {"ok": False, "msg": "session.created 未到达", "events": cb.events[:10]}
    import time as _t
    _t.sleep(2)
    if voice_id != "DEFAULT":
        tts.update_session(voice=voice_id)
        _t.sleep(1)
    tts.append_text(text)
    if len(sys.argv) > 3 and sys.argv[3] == "nofinish":
        pass
    else:
        tts.finish()
    cb.done.wait(timeout=60)
    try:
        tts.close()
    except Exception:
        pass
    pcm = b"".join(cb.chunks)
    if not pcm:
        return {"ok": False, "errors": cb.errors[:3], "events": cb.events[:15]}
    with wave.open(str(OUT), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(pcm)
    return {"ok": True, "bytes": OUT.stat().st_size, "pcm": len(pcm),
            "errors": cb.errors[:2], "last_events": cb.events[-5:]}


if __name__ == "__main__":
    voice = sys.argv[1] if len(sys.argv) > 1 else "qwen-tts-vc-furinareal-voice-20261107212733988-d4a2"
    text = sys.argv[2] if len(sys.argv) > 2 else "看好了！优雅，永不过时！"
    print(json.dumps(synth(text, voice), ensure_ascii=False))
