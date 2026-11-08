# -*- coding: utf-8 -*-
"""用新 API Key 探测业务空间可用的 TTS 模型（含 SSRF 防护：https + 域名白名单 + 解析 IP 校验）。

用法: python probe_models.py
Key 从同目录 api_key_new.txt 读取（避免写入命令行历史）。
"""
import ipaddress
import json
import socket
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests

BASE = "https://llm-j4rrs2ypcn844o8j.cn-beijing.maas.aliyuncs.com"
ALLOWED_HOSTS = {"llm-j4rrs2ypcn844o8j.cn-beijing.maas.aliyuncs.com"}
KEY = Path(__file__).with_name("api_key_new.txt").read_text(encoding="utf-8").strip()
H = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}


def validate_url(url: str) -> str:
    """仅允许 https + 白名单域名 + 解析后 IP 必须为公网地址（防 SSRF/DNS rebinding）。"""
    p = urlparse(url)
    if p.scheme != "https" or p.hostname not in ALLOWED_HOSTS:
        raise ValueError(f"URL 被拒绝: {url}")
    for _f, _t, _p, _cn, sa in socket.getaddrinfo(p.hostname, 443):
        ip = ipaddress.ip_address(sa[0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            raise ValueError(f"域名解析到非公网地址 {ip}，拒绝请求")
    return url


def model_list():
    r = requests.get(validate_url(BASE + "/compatible-mode/v1/models"), headers=H, timeout=30,
                     allow_redirects=False)
    print("== models ==")
    try:
        d = r.json()
        ids = [m.get("id") for m in d.get("data", [])]
        tts = [i for i in ids if i and any(k in i.lower() for k in ("tts", "cosyvoice", "sambert", "audio"))]
        print(json.dumps({"total": len(ids), "tts_related": tts, "all_first20": ids[:20]}, ensure_ascii=False))
    except Exception:
        print(f"status={r.status_code} body={r.text[:200]}")


def speech_probe(model, voice, text="通路测试"):
    r = requests.post(validate_url(BASE + "/compatible-mode/v1/audio/speech"), headers=H,
                      json={"model": model, "input": text, "voice": voice,
                            "response_format": "wav"}, timeout=60,
                      allow_redirects=False)
    ct = r.headers.get("content-type", "")
    if r.status_code == 200 and "audio" in ct:
        return {"model": model, "ok": True, "bytes": len(r.content), "ct": ct}
    msg = ""
    try:
        msg = r.json().get("error", {}).get("message", "") or r.text[:150]
    except Exception:
        msg = r.text[:150]
    return {"model": model, "ok": False, "status": r.status_code, "msg": msg[:150]}


def main():
    model_list()
    print("== audio/speech probes ==")
    for model, voice in [
        ("qwen3-tts-flash", "Cherry"),
        ("qwen-audio-3.1-tts-flash", "longanhuan_v3.1"),
        ("qwen-audio-3.1-tts-plus", "longanhuan_v3.1"),
        ("qwen-audio-3.0-tts-flash", "longxiaochun_v2"),
        ("cosyvoice-v2", "longxiaochun_v2"),
        ("cosyvoice-v3-flash", "longxiaochun_v3"),
        ("cosyvoice-v3.5-flash", "longxiaochun_v3"),
    ]:
        print(json.dumps(speech_probe(model, voice), ensure_ascii=False))


if __name__ == "__main__":
    main()
