# -*- coding: utf-8 -*-
"""调用百炼端点的文生图模型，生成两人全身像素画（纯白背景）。
Key 从语音包项目 api_key_new.txt 读取，不打印密钥。
所有动态 URL 均经 SSRF 校验（https + 解析公网 IP + 禁止重定向）。
输出保存到 表情替换项目/01_素材下载/生成/。
"""
import base64
import ipaddress
import json
import socket
import time
from pathlib import Path
from urllib.parse import urlparse

import requests

BASE = "https://llm-j4rrs2ypcn844o8j.cn-beijing.maas.aliyuncs.com"
ALLOWED_HOSTS = {"llm-j4rrs2ypcn844o8j.cn-beijing.maas.aliyuncs.com"}
KEY_PATH = Path(r"D:\桌宠\语音包项目\05_工具脚本\api_key_new.txt")
OUT_DIR = Path(r"D:\桌宠\表情替换项目\01_素材下载\生成")

KEY = KEY_PATH.read_text(encoding="utf-8").strip()
H = {"Authorization": "Bearer " + KEY, "Content-Type": "application/json"}

TASKS = [
    ("furina_lying2", "qwen-image-3.0-pro",
     "原神角色芙宁娜的Q版大头贴像素画，趴姿：脸部超大占满画面大部分，"
     "下巴枕在两只交叠的小手上，两只小手放在画面最下边缘，头微微倾斜看向观众。"
     "经典像素艺术风格，平涂上色，色块分明，只有两三个色调，粗黑轮廓线，高对比度，"
     "纯白色背景，无任何背景装饰：白色卷发带浅蓝色挑染，头顶一个大卷曲呆毛，"
     "头戴深蓝色高顶礼帽，帽子上有金色皇冠装饰和蓝色蝴蝶结宝石，"
     "左眼睁开是超大的蓝色眼睛，右眼眨眼wink，张开嘴巴开心地笑，脸颊粉红腮红，"
     "构图极简干净"),
    ("firefly_stare", "qwen-image-3.0-pro",
     "崩坏星穹铁道角色流萤的Q版大头贴像素画，只有头部和肩部的正面大特写，头部占满画面，"
     "经典像素艺术风格，平涂上色，色块分明，只有两三个色调，粗黑轮廓线，高对比度，"
     "纯白色背景，无任何背景装饰：银灰色头发齐刘海，深灰色发箍，发箍上有青绿色X形装饰，"
     "脸部超大，瞪大双眼非常惊讶，眼睛又大又圆，瞳孔纯黑色带大白色高光，嘴巴张开成小圆形O型嘴，"
     "脸颊两侧粉红腮红，脖子围绿色围巾，肩部深青色外套，构图极简干净"),
    ("furina_excited", "qwen-image-3.0-pro",
     "原神角色芙宁娜的Q版大头贴像素画，只有头部和肩部的正面大特写，头部占满画面，"
     "经典像素艺术风格，平涂上色，色块分明，只有两三个色调，粗黑轮廓线，高对比度，"
     "纯白色背景，无任何背景装饰：白色卷发带浅蓝色挑染，头戴深蓝色高顶礼帽，"
     "帽子上有金色小皇冠装饰，脸部超大，超大蓝色眼睛亮闪闪，张开嘴巴超级兴奋地大笑，"
     "表情疯狂开心，脸颊红晕，深蓝色衣服白色领子，构图极简干净"),
    ("firefly_hello", "qwen-image-3.0-pro",
     "崩坏星穹铁道角色流萤的Q版大头贴像素画，头部和举起的小手占满画面，"
     "经典像素艺术风格，平涂上色，色块分明，只有两三个色调，粗黑轮廓线，高对比度，"
     "纯白色背景，无任何背景装饰：银灰色头发齐刘海，深灰色发箍，发箍上有青绿色X形装饰，"
     "脸部超大，超大紫色眼睛带白色高光点，开心灿烂的笑容，一只小手举起来挥手打招呼，"
     "脸颊两侧粉红腮红，脖子围绿色围巾，肩部深青色外套，构图极简干净"),
]


def validate_url(url):
    """仅允许 https + 白名单端点或解析为公网 IP 的地址（防 SSRF/DNS rebinding），禁止重定向。"""
    p = urlparse(url)
    if p.scheme != "https":
        raise ValueError("URL 必须为 https: %s" % url)
    if p.hostname not in ALLOWED_HOSTS:
        infos = socket.getaddrinfo(p.hostname, 443)
        for _f, _t, _p, _cn, sa in infos:
            ip = ipaddress.ip_address(sa[0])
            if (ip.is_private or ip.is_loopback or ip.is_link_local
                    or ip.is_reserved or ip.is_multicast or ip.is_unspecified):
                raise ValueError("域名解析到非公网地址 %s，拒绝: %s" % (ip, url))
    return url


def post_json(url, body, timeout=180):
    r = requests.post(validate_url(url), headers=H, data=json.dumps(body),
                      timeout=timeout, allow_redirects=False)
    r.raise_for_status()
    return r.json()


def get_json(url, timeout=30):
    r = requests.get(validate_url(url), headers=H, timeout=timeout, allow_redirects=False)
    r.raise_for_status()
    return r.json()


def gen_one(name, model, prompt):
    body = {"model": model, "prompt": prompt, "n": 1,
            "size": "1024x1024", "response_format": "url"}
    d = post_json(BASE + "/compatible-mode/v1/images/generations", body)
    if isinstance(d, dict) and d.get("task_id"):
        print("  异步任务:", d.get("task_status"), d["task_id"])
        return ("task", d["task_id"])
    items = d.get("data") or (d.get("output") or {}).get("results") or []
    if items:
        it = items[0]
        url = it.get("url") or (it.get("image") or {}).get("url")
        b64 = it.get("b64_json") or (it.get("image") or {}).get("b64_json")
        print("  同步返回:", "url" if url else ("b64" if b64 else str(d)[:200]))
        return ("sync", url, b64)
    print("  未知结构:", json.dumps(d, ensure_ascii=False)[:500])
    return None


def poll_task(task_id):
    for _ in range(80):
        time.sleep(3)
        d = get_json(BASE + "/compatible-mode/v1/tasks/" + task_id)
        st = d.get("task_status") or d.get("status")
        print("  轮询:", st)
        if st in ("SUCCEEDED", "success", "succeed"):
            out = d.get("output", {})
            items = out.get("results") or out.get("task_results") or out.get("image_url") and [{"url": out["image_url"]}] or []
            if items:
                it = items[0] if isinstance(items, list) else items
                return it.get("url") if isinstance(it, dict) else it
            return None
        if st in ("FAILED", "fail", "failed", "CANCELED"):
            print("  失败:", json.dumps(d, ensure_ascii=False)[:400])
            return None
    return None


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, model, prompt in TASKS:
        try:
            res = gen_one(name, model, prompt)
        except Exception as e:
            print("  [%s] 请求失败: %s" % (name, e))
            continue
        if not res:
            continue
        url = None
        b64 = None
        if res[0] == "task":
            try:
                url = poll_task(res[1])
            except Exception as e:
                print("  [%s] 轮询失败: %s" % (name, e))
                continue
        else:
            url, b64 = res[1], res[2]
        try:
            if b64:
                out = OUT_DIR / (name + ".png")
                out.write_bytes(base64.b64decode(b64))
                print("  已保存:", out)
            elif url:
                p = urlparse(url)
                if p.scheme != "https":
                    raise ValueError("图片 URL 非 https")
                img = requests.get(validate_url(url), timeout=120, allow_redirects=False)
                img.raise_for_status()
                out = OUT_DIR / (name + ".png")
                out.write_bytes(img.content)
                print("  已保存:", out, len(img.content), "bytes")
            else:
                print("  [%s] 未拿到图片" % name)
        except Exception as e:
            print("  [%s] 下载失败: %s" % (name, e))


if __name__ == "__main__":
    main()
