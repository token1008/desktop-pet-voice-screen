# -*- coding: utf-8 -*-
"""用 dashscope 新式 client.audio.tts.connect 接口探测 TTS 模型可用性。

用法: python probe_client_tts.py [model] [voice]
Key 从同目录 api_key_new.txt 读取；BAILIAN_API_KEY 环境变量优先。
"""
import json
import os
import sys
from pathlib import Path

PLUGIN_MCP_DIR = Path(r"C:\Users\a1575\.zcode\cli\plugins\cache\fufu-local\bailian-voice\0.6.1\mcp")
sys.path.insert(0, str(PLUGIN_MCP_DIR))
import server  # noqa: E402  加载 CFG（含 workspace http/ws 端点）
import dashscope
from dashscope.audio.tts_v2 import SpeechSynthesizer, AudioFormat  # noqa: F401

KEY = os.environ.get("BAILIAN_API_KEY") or Path(__file__).with_name("api_key_new.txt").read_text(encoding="utf-8").strip()
dashscope.api_key = KEY
dashscope.base_http_api_url = server.CFG["http_base_url"]
dashscope.base_websocket_api_url = server.CFG["websocket_url"]

OUT = Path(r"D:\桌宠\语音包项目\03_合成音频\probe_client.wav")


def probe(model, voice, text="通路测试，一句即可"):
    try:
        client = dashscope.Client(api_key=KEY, workspace="llm-j4rrs2ypcn844o8j", region="cn-beijing")
        audio = b""
        with client.audio.tts.connect(model=model, voice=voice, format="wav", sample_rate=24000) as session:
            session.send_text(text)
            session.flush()
            session.stop()
            for chunk in session.audio_chunks():
                audio += chunk
        if audio:
            OUT.write_bytes(audio)
            return {"model": model, "ok": True, "bytes": len(audio), "saved": str(OUT)}
        return {"model": model, "ok": False, "msg": "无音频返回"}
    except Exception as e:
        return {"model": model, "ok": False, "msg": str(e)[:200]}


if __name__ == "__main__":
    pairs = [
        ("qwen3-tts-flash", "Cherry"),
        ("qwen-audio-3.1-realtime-flash", "longanhuan_v3.1"),
        ("qwen-audio-3.1-tts-flash", "longanhuan_v3.1"),
        ("cosyvoice-v2", "longxiaochun_v2"),
    ]
    if len(sys.argv) > 2:
        pairs = [(sys.argv[1], sys.argv[2])]
    for m, v in pairs:
        print(json.dumps(probe(m, v), ensure_ascii=False))
