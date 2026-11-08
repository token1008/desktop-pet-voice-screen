# -*- coding: utf-8 -*-
"""qwen3-tts-vc-realtime 合成探针（WS SpeechSynthesizer + 复刻音色）。

用法: python probe_vc_realtime.py [model] [voice] [text]
可选: 设置 BAILIAN_WS_URL 覆盖 WebSocket 端点。
"""
import ipaddress
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import dashscope
from dashscope.audio.tts_v2 import SpeechSynthesizer, AudioFormat

KEY = os.environ.get("BAILIAN_API_KEY") or Path(__file__).with_name("api_key_new.txt").read_text(encoding="utf-8").strip()
dashscope.api_key = KEY

WS_URL = os.environ.get("BAILIAN_WS_URL", "wss://dashscope.aliyuncs.com/api-ws/v1/inference")


def _safe_ws_url(url):
    """仅允许 ws/wss，拒绝 localhost、环回、私有和保留地址。"""
    p = urlparse(url)
    if p.scheme not in ("ws", "wss"):
        raise SystemExit("仅允许 ws/wss WebSocket URL")
    host = (p.hostname or "").strip().lower()
    if not host:
        raise SystemExit("URL 缺少 host")
    if host in ("localhost", "localhost.localdomain"):
        raise SystemExit("拒绝 localhost")
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        ip = None
    if ip is not None and (
        ip.is_loopback or ip.is_private or ip.is_reserved
        or ip.is_link_local or ip.is_multicast or ip.is_unspecified
    ):
        raise SystemExit("拒绝环回/私有/保留地址")
    return url


dashscope.base_websocket_api_url = _safe_ws_url(WS_URL)
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
    def _clean_arg(value, name, max_len=300):
        value = value.strip()
        if not value or len(value) > max_len:
            raise SystemExit(f"{name} 参数为空或过长")
        if name in ("model", "voice"):
            if not re.fullmatch(r"[A-Za-z0-9._-]+", value):
                raise SystemExit(f"{name} 仅允许字母、数字、点、下划线、连字符")
        elif any(ord(c) < 32 for c in value):
            raise SystemExit("text 含控制字符")
        return value

    model = _clean_arg(sys.argv[1] if len(sys.argv) > 1 else "qwen3-tts-vc-realtime", "model")
    voice = _clean_arg(sys.argv[2] if len(sys.argv) > 2 else "qwen-tts-vc-furinareal-voice-20261107212733988-d4a2", "voice")
    text = _clean_arg(sys.argv[3] if len(sys.argv) > 3 else "看好了！优雅，永不过时！", "text", max_len=500)
    print(json.dumps(probe(model, voice, text), ensure_ascii=False))
