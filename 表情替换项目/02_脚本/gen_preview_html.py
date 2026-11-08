# -*- coding: utf-8 -*-
# gen_preview_html.py - 从固件 Face_Data_2026.c 生成实机蓝屏预览页(内嵌字节数据, canvas逐点渲染)
# 并自校验: 写出的 HTML 中的 hex 必须与固件数组逐字节一致
import re
import os
from pathlib import Path

SRC = r"D:/桌宠/桌宠代码/适配1.2.0版本电路板的代码/桌面宠物代码(更新于26年3月23日)适配国产芯片/HardWare/Face_Data_2026.c"
OUT = r"C:/Users/a1575/.zcode/v2/visualizations/fbc358da0e8375daee510d41504f890908566720f9eb4e810f14dd775618f128/face-preview-2026.html"

# 路径安全: 规范化并限制输出在允许目录内, 禁止 ../ 越界
OUT = os.path.normpath(OUT)
_ALLOWED_ROOT = os.path.normpath(r"C:/Users/a1575/.zcode/v2/visualizations")
assert ".." not in OUT.split(os.sep), "输出路径含 .."
assert os.path.commonpath([OUT, _ALLOWED_ROOT]) == _ALLOWED_ROOT, "输出路径越界"

with open(SRC, "r", encoding="utf-8") as f:
    text = f.read()

arrays = {}
for m in re.finditer(r"uint8_t\s+(\w+)\s*\[\s*\]\s*=\s*\{(.*?)\};", text, re.S):
    body = re.sub(r"//[^\n]*", "", m.group(2))
    vals = [int(v, 16) for v in re.findall(r"0[xX][0-9a-fA-F]+", body)]
    assert len(vals) == 1024, "%s len=%d" % (m.group(1), len(vals))
    arrays[m.group(1)] = "".join("%02X" % v for v in vals)
assert len(arrays) == 7

# 显示顺序与 Face_Config.c case 0..6 一致
ITEMS = [
    ("Face_Furina_Lying_X",    "芙宁娜 · 趴姿枕手", "睡觉 · 模式0"),
    ("Face_Firefly_Stare_X",   "流萤 · 瞪眼惊讶",   "蹲下 · 模式1"),
    ("Face_Firefly_X",         "流萤 · 微笑",       "前进/后退/转向 · 模式2"),
    ("Face_Furina_Excited_X",  "芙宁娜 · 兴奋",     "摇摆 · 模式3"),
    ("Face_Firefly_Laugh_X",   "流萤 · 开心大笑",   "非常快乐 · 模式4"),
    ("Face_Furina_X",          "芙宁娜 · 眨眼笑",   "站立 · 模式5 · 开机画面"),
    ("Face_Firefly_Hello_X",   "流萤 · 打招呼",     "打招呼 · 模式6"),
]

items_js = ",\n".join(
    '    {name:"%s", mode:"%s", hex:"%s"}' % (cn, mode, arrays[key])
    for key, cn, mode in ITEMS
)

html = '''<div id="furi-firefly-oled-preview">
  <div style="display:flex;align-items:baseline;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-bottom:12px;">
    <h3 style="margin:0;">128×64 蓝屏实机效果预览</h3>
    <span class="text-small text-muted">逐点渲染自固件 Face_Data_2026.c · 页式取模 · 阴码 · 低位在上</span>
  </div>
  <div id="fp-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(264px,1fr));gap:14px;"></div>
</div>
<script>
(function(){
  var FACES=[
''' + items_js + '''
  ];
  var grid=document.getElementById('fp-grid');
  FACES.forEach(function(f){
    var fig=document.createElement('figure');
    fig.style.margin='0';
    var bez=document.createElement('div');
    bez.style.cssText='background:#111418;border:1px solid #2a2e35;border-radius:10px;padding:9px;';
    var cv=document.createElement('canvas');
    cv.width=256;cv.height=128;
    cv.style.cssText='display:block;width:100%;height:auto;image-rendering:pixelated;background:#04070d;border-radius:3px;';
    bez.appendChild(cv);
    var cap=document.createElement('figcaption');
    cap.style.cssText='margin-top:7px;font-size:12px;line-height:1.5;';
    var n1=document.createElement('span');
    n1.style.cssText='color:var(--foreground);font-weight:500;';
    n1.textContent=f.name;
    var n2=document.createElement('span');
    n2.style.cssText='color:var(--muted-foreground);';
    n2.textContent='　'+f.mode;
    cap.appendChild(n1);cap.appendChild(n2);
    fig.appendChild(bez);fig.appendChild(cap);
    grid.appendChild(fig);
    var ctx=cv.getContext('2d');
    ctx.fillStyle='#04070d';ctx.fillRect(0,0,256,128);
    ctx.fillStyle='#3fa9ff';
    for(var p=0;p<8;p++){
      for(var x=0;x<128;x++){
        var b=parseInt(f.hex.substr((p*128+x)*2,2),16);
        if(!b)continue;
        for(var bit=0;bit<8;bit++){
          if((b>>bit)&1){ctx.fillRect(x*2,(p*8+bit)*2,2,2);}
        }
      }
    }
  });
})();
</script>'''

# OUT 已在上方限制在 _ALLOWED_ROOT 内，使用 pathlib 写入
Path(OUT).write_text(html, encoding="utf-8")

# 自校验: 重新读出 HTML, 提取 hex 与固件比对
back = Path(OUT).read_text(encoding="utf-8")
embedded = set(re.findall(r'hex:"([0-9A-F]{2048})"', back))
expected = set(arrays.values())
assert embedded == expected and len(embedded) == 7, "HTML内嵌数据与固件不一致!"
print("PASS: HTML 中 7 组 hex 与固件 Face_Data_2026.c 逐字节一致")
print("OUT :", OUT)
print("SIZE:", len(html.encode("utf-8")), "bytes")
