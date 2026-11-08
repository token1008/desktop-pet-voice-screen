# -*- coding: utf-8 -*-
"""用 dashscope.audio.qwen_tts.SpeechSynthesizer（Qwen-TTS 专用协议）探测模型。

用法: python probe_qwen_tts.py [model] [voice]
Key 从同目录 api_key_new.txt 读取；BAILIAN_API_KEY 环境变量优先。
"""
import base64
import ipaddress
import json
import os
import socket
import sys
from pathlib import Path
from urllib.parse import urlparse

import dashscope
from dashscope.audio.qwen_tts import SpeechSynthesizer as QwenSynth

PLUGIN_MCP_DIR = Path(r"C:\Users\a1575\.zcode\cli\plugins\cache\fufu-local\bailian-voice\0.6.1\mcp")
sys.path.insert(0, str(PLUGIN_MCP_DIR))
import server  # noqa: E402  加载 CFG（workspace http/ws 端点）

KEY = os.environ.get("BAILIAN_API_KEY") or Path(__file__).with_name("api_key_new.txt").read_text(encoding="utf-8").strip()
dashscope.api_key = KEY
dashscope.base_http_api_url = server.CFG["http_base_url"]
OUT = Path(r"D:\桌宠\语音包项目\03_合成音频\probe_qwen_tts.wav")


def validate_url(url: str) -> str:
    """仅允许 https + 阿里云/百炼域名白名单 + 解析后 IP 必须为公网地址。"""
    p = urlparse(url)
    host = p.hostname or ""
    if p.scheme not in ("http", "https") or not (host.endswith(".aliyuncs.com") or host.endswith(".aliyun.com")):
        raise ValueError(f"URL 被拒绝: {url[:80]}")
    for _f, _t, _p, _cn, sa in socket.getaddrinfo(host, 443):
        ip = ipaddress.ip_address(sa[0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            raise ValueError(f"域名解析到非公网地址 {ip}，拒绝请求")
    return url


def probe(model, voice, text="通路测试，一句即可"):
    try:
        resp = QwenSynth.call(model=model, text=text, voice=voice)
        if resp.status_code != 200:
            return {"model": model, "ok": False, "status": resp.status_code,
                    "code": getattr(resp, "code", None), "msg": str(resp.message)[:200]}
        out = resp.output or {}
        audio = out.get("audio", {}) if isinstance(out, dict) else {}
        data = audio.get("data")
        url = audio.get("url")
        if data:
            OUT.write_bytes(base64.b64decode(data))
            return {"model": model, "ok": True, "src": "base64", "bytes": OUT.stat().st_size}
        if url:
            import urllib.request
            with urllib.request.urlopen(validate_url(url), timeout=120) as r:
                blob = r.read()
            OUT.write_bytes(blob)
            return {"model": model, "ok": True, "src": "url", "bytes": len(blob), "saved": str(OUT)}
        return {"model": model, "ok": False, "msg": f"无音频: {str(out)[:200]}"}
    except ValueError as e:
        return {"model": model, "ok": False, "msg": str(e)[:200]}
    except Exception as e:
        return {"model": model, "ok": False, "msg": str(e)[:200]}


if __name__ == "__main__":
    pairs = [
        ("qwen3-tts-flash", "Cherry"),
        ("qwen3-tts-flash", "Serena"),
    ]
    if len(sys.argv) > 2:
        pairs = [(sys.argv[1], sys.argv[2])]
    for m, v in pairs:
        print(json.dumps(probe(m, v), ensure_ascii=False))
