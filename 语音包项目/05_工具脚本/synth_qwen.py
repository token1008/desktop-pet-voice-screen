# -*- coding: utf-8 -*-
"""qwen3-tts-flash 正式合成脚本（支持音色 + 指令控制 + 输出路径）。

用法: python synth_qwen.py --text "台词" --out "x.wav" [--voice Cherry] [--instruction "语气指令"]
Key 从同目录 api_key_new.txt 读取；BAILIAN_API_KEY 环境变量优先。
"""
import argparse
import base64
import ipaddress
import json
import os
import socket
import sys
from pathlib import Path
from urllib.parse import urlparse

PLUGIN_MCP_DIR = Path(r"C:\Users\a1575\.zcode\cli\plugins\cache\fufu-local\bailian-voice\0.6.1\mcp")
sys.path.insert(0, str(PLUGIN_MCP_DIR))
import server  # noqa: E402  workspace 端点
import dashscope
from dashscope.audio.qwen_tts import SpeechSynthesizer as QwenSynth

KEY = os.environ.get("BAILIAN_API_KEY") or Path(__file__).with_name("api_key_new.txt").read_text(encoding="utf-8").strip()
MODEL = "qwen3-tts-flash"
WORKSPACE = "llm-j4rrs2ypcn844o8j"


def validate_url(url: str) -> str:
    """下载结果音频前校验：仅 aliyuncs 域 + 公网解析 IP。"""
    p = urlparse(url)
    host = p.hostname or ""
    if p.scheme not in ("http", "https") or not host.endswith(".aliyuncs.com"):
        raise ValueError(f"URL 被拒绝: {url[:80]}")
    for _f, _t, _p, _cn, sa in socket.getaddrinfo(host, 443):
        ip = ipaddress.ip_address(sa[0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            raise ValueError(f"域名解析到非公网地址 {ip}，拒绝请求")
    return url


def synth(text, out_path, voice, instruction):
    kwargs = {"voice": voice}
    if instruction:
        kwargs["instructions"] = instruction
    resp = QwenSynth.call(model=MODEL, text=text, api_key=KEY, workspace=WORKSPACE, **kwargs)
    if resp.status_code != 200:
        return {"ok": False, "status": resp.status_code, "code": getattr(resp, "code", None),
                "msg": str(resp.message)[:200]}
    audio = (resp.output or {}).get("audio", {}) if isinstance(resp.output, dict) else {}
    data, url = audio.get("data"), audio.get("url")
    if data:
        blob = base64.b64decode(data)
    elif url:
        import urllib.request
        with urllib.request.urlopen(validate_url(url), timeout=120) as r:
            blob = r.read()
    else:
        return {"ok": False, "msg": "无音频内容"}
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(blob)
    return {"ok": True, "file": str(out), "bytes": len(blob), "voice": voice,
            "instruction": bool(instruction)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--voice", default="Cherry")
    ap.add_argument("--instruction", default="")
    a = ap.parse_args()
    print(json.dumps(synth(a.text, a.out, a.voice, a.instruction), ensure_ascii=False))
