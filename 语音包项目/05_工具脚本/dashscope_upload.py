# -*- coding: utf-8 -*-
"""DashScope 文件上传 API：本地文件 → 阿里云临时 URL（百炼服务端可达，不公开）。

用法: python dashscope_upload.py <文件>
打印 JSON（含 url）。
"""
import json
import sys
from pathlib import Path

PLUGIN_MCP_DIR = Path(r"C:\Users\a1575\.zcode\cli\plugins\cache\fufu-local\bailian-voice\0.6.1\mcp")
sys.path.insert(0, str(PLUGIN_MCP_DIR))
import server  # noqa: E402  CFG 含 api_key
import requests


def main():
    src = Path(sys.argv[1])
    # DashScope 文件上传：先申请上传凭证，再 PUT 到 OSS
    r = requests.get(
        server.CFG["http_base_url"] + "/uploads",
        headers={"Authorization": f"Bearer {server.CFG['api_key']}"},
        params={"action": "getPolicy", "model": "qwen-audio-asr"},
        timeout=60,
    )
    print(json.dumps({"step": "getPolicy", "status": r.status_code,
                      "body_head": r.text[:400]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
