# 表情替换项目

把桌宠小狗 **128×64 单色 OLED** 的 7 个默认表情替换成 **芙宁娜 / 流萤** 的角色像素画。

## 原理

原厂固件 `Project.hex` 中有 7 个 `1024` 字节的表情位图槽位。本项目只原位替换这 7×1024 字节，不改任何逻辑代码：

| 槽位 | 触发场景 | 替换为 |
|---|---|---|
| `Face_sleep` | 睡觉 | `Face_Furina_Lying_X` |
| `Face_stare` | 蹲下 | `Face_Firefly_Stare_X` |
| `Face_happy` | 前进 / 后退 / 转向 | `Face_Firefly_X` |
| `Face_mania` | 摇摆 | `Face_Furina_Excited_X` |
| `Face_very_happy` | 非常快乐 | `Face_Firefly_Laugh_X` |
| `Face_eyes` | 站立 + 开机画面 | `Face_Furina_X` |
| `Face_hello` | 打招呼 | `Face_Firefly_Hello_X` |

取模格式：**128×64、页式（每字节 8 个纵点）、阴码、低位在上（bit0 = 顶部）**，与江协科技 `OLED_ShowImage` 兼容。

## 目录说明

```text
表情替换项目/
├─ 01_素材下载/        # 官方立绘、Enka 图标、参考图、Qwen-Image 生成图
├─ 02_脚本/
│  ├─ convert_to_oled.py   # 立绘 → 128×64 单色候选（输出 stdout）
│  ├─ pixel_art.py         # 手绘 Q 版像素画（输出 stdout）
│  ├─ gen_images.py        # 百炼 Qwen-Image 3.0 Pro 文生图
│  ├─ patch_hex_2026.py    # 原厂 HEX 原位替换 7 个表情位
│  ├─ verify_face2026.py   # 取模 / HEX 校验
│  └─ analyze_oct17.py     # 原固件表情槽位分析
├─ 03_预览/            # 1bit、6x 放大预览、C 数组 dump
└─ 04_固件数据/         # Chibi / Dither / Lum / Silhouette 四种风格 C 数组
```

- `03_预览/Face_Data_2026_content.txt`：最终用于打补丁的 **7 个 `_X` 数组**。
- `03_预览/final_*.txt`：各表情的 Smart 分区转换候选。
- `04_固件数据/*.c`：每个角色的 4 种风格备选（Chibi / Dither / Lum / Silhouette）。

## 生成可烧录的 HEX

由于原项目采用 **GPL-3.0**，本仓库**不直接分发**原版 `Project.hex` 或其修改版 `Project_Face2026.hex`。请在本机生成：

1. 从原作者项目获取完整资料包（含 `Project.hex` 和 `Face_Data_2026.c` 所在工程）：
   - <https://oshwhub.com/sngelswyh/stm32-smart-desktop-pet>
2. 把 `03_预览/Face_Data_2026_content.txt` 复制为工程中的 `Face_Data_2026.c`。
3. 修改 `02_脚本/patch_hex_2026.py` 顶部的 `SRC_C`、`HEX_IN`、`HEX_OUT` 为本机实际路径。
4. 运行：

```bash
python -I 02_脚本/patch_hex_2026.py
```

5. 用 `FlyMcu` 烧录生成的 `Project_Face2026.hex` 到 STM32F103C8T6。

补丁脚本会校验：

- 输出 HEX 的地址集合与原固件完全一致；
- 所有差异字节都落在 7 个表情区内；
- 逐字节回读比对。

## 重新生成表情

```bash
# 立绘 → OLED 候选（stdout 重定向保存）
python -I 02_脚本/convert_to_oled.py png furina_dit > 03_预览/out_furina.txt

# 手绘像素画（sim = 模拟预览；blue / white = 配色）
python -I 02_脚本/pixel_art.py sim furina blue > 03_预览/out_sim.txt

# 校验
python -I 02_脚本/verify_face2026.py
```

依赖：`pip install Pillow`。

## 版权说明

- 芙宁娜 / 流萤角色立绘、图标版权归米哈游 / HoYoverse 及相关权利人所有。
- 本目录素材仅限个人学习与个人桌宠使用，**禁止商用、禁止单独再分发**。
- 原作固件与硬件工程采用 GPL-3.0，使用 `patch_hex_2026.py` 时请遵守原项目许可证。

## 来源与参考

- 原始桌宠项目（Sngels_wyh，GPL-3.0）：<https://oshwhub.com/sngelswyh/stm32-smart-desktop-pet>
- 江协科技 OLED 教程：<https://jiangxiekeji.com/tutorial/oled.html>
- 江协科技 OLED 视频：<https://www.bilibili.com/video/BV1EN41177Pc/>
- Enka.Network：<https://enka.network/>
- 阿里云百炼 Qwen-Image：<https://bailian.console.aliyun.com/>
- 米哈游 / HoYoverse：<https://www.mihoyo.com/>
