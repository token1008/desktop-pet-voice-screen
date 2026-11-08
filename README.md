# 桌宠语音包 & OLED 屏幕表情替换

<p align="center">
  <img src="https://img.shields.io/badge/MCU-STM32F103C8T6-0b7285?style=flat-square" alt="STM32F103C8T6">
  <img src="https://img.shields.io/badge/Voice-SU--03T1-2b8a3e?style=flat-square" alt="SU-03T1">
  <img src="https://img.shields.io/badge/OLED-128%C3%9764%20SSD1306-e8590c?style=flat-square" alt="128x64 OLED">
  <img src="https://img.shields.io/badge/Code-License%3A%20MIT-1971c2?style=flat-square" alt="MIT">
  <img src="https://img.shields.io/badge/Assets-Personal%20Use%20Only-c92a2a?style=flat-square" alt="Personal Use Only">
</p>

> 基于 **Sngels_wyh** 开源「STM32 智能桌面宠物」V1.2.0 电路板的二次创作：
> 给桌宠小狗换上 **芙宁娜 / 流萤** 两套角色语音包，并把 128×64 单色 OLED 的默认表情替换成角色像素表情。
>
> 本仓库只包含 **语音** 与 **屏幕** 两部分的新增内容，**不是**原作者的完整硬件 / 固件工程。

---

## 目录

- [项目简介](#项目简介)
- [内容概览](#内容概览)
- [功能特性](#功能特性)
- [目录结构](#目录结构)
- [环境与依赖](#环境与依赖)
- [快速开始](#快速开始)
  - [1. 克隆仓库](#1-克隆仓库)
  - [2. 烧录语音固件](#2-烧录语音固件)
  - [3. 烧录屏幕表情固件](#3-烧录屏幕表情固件)
- [语音包制作流程](#语音包制作流程)
- [屏幕表情制作流程](#屏幕表情制作流程)
- [信息与资源来源](#信息与资源来源)
- [参考资料链接](#参考资料链接)
- [版权与使用限制](#版权与使用限制)
- [常见问题](#常见问题)
- [许可证](#许可证)
- [致谢](#致谢)

---

## 项目简介

本项目围绕一只基于 **STM32F103C8T6** 的桌面宠物小狗展开，硬件为 **Sngels_wyh 开源的 V1.2.0 电路板**，语音模块为 **机芯智能 SU-03T1**，屏幕为 **128×64 单色 OLED（SSD1306 / SSD1315）**。

原作者已经完成了硬件、STM32 固件、蓝牙控制、舵机动作和基础语音固件。本仓库在其基础上新增了两部分：

| 部分 | 做了什么 | 关键产物 |
|---|---|---|
| **语音包** | 用角色音色重新制作两套 SU-03T1 语音固件：唤醒词、唤醒回复、22 个命令词回复、开机 / 超时 / 退出播报全部换成角色音色 | `语音包项目/04_固件/*/jx_firm/jx_su_03t_release_update.bin` |
| **屏幕表情** | 把官方 7 个表情位替换成芙宁娜 / 流萤的 128×64 单色像素画；只改位图数据，不改 STM32 代码 | `表情替换项目/04_固件数据/*.c`、`表情替换项目/03_预览/Face_Data_2026_content.txt` |

核心兼容性结论：

- SU-03T1 与 STM32 之间的 **UART 9600 单字节协议（0x29~0x50）保持不变**。
- 语音包只重烧 SU-03T1，**STM32 固件不需要重新烧录**，蓝牙控制不受影响。
- 屏幕表情只替换 OLED 的 7×1024 字节位图，**不改动任何逻辑代码**。

---

## 内容概览

### 语音包（两套）

| 角色 | 唤醒词 | 内容 | 烧录文件 |
|---|---|---|---|
| 芙宁娜（原神） | 「芙宁娜大人」 | 3 条唤醒回复 + 22 个命令词回复 + 30 条个性化音频；开机、300 秒超时、退出也使用角色音色 | `语音包项目/04_固件/芙宁娜/jx_firm/jx_su_03t_release_update.bin` |
| 流萤（崩坏：星穹铁道） | 「流萤大人」 | 3 条唤醒回复 + 22 个命令词回复 + 30 条个性化音频；开机、300 秒超时、退出也使用角色音色 | `语音包项目/04_固件/流萤/jx_firm/jx_su_03t_release_update.bin` |

固件版本：芙宁娜 `20261108003`、流萤 `20261108002`（详见 [`语音包项目/烧录手册.md`](语音包项目/烧录手册.md)）。

### 屏幕表情（7 个表情位）

`patch_hex_2026.py` 将原固件中的 7 个表情位原位替换为：

| 表情位 | 触发场景 | 替换为 |
|---|---|---|
| `Face_sleep` | 睡觉 | 芙宁娜趴姿 |
| `Face_stare` | 蹲下 | 流萤凝视 |
| `Face_happy` | 前进 / 后退 / 转向 | 流萤 |
| `Face_mania` | 摇摆 | 芙宁娜兴奋 |
| `Face_very_happy` | 非常快乐 | 流萤大笑 |
| `Face_eyes` | 站立 + 开机画面 | 芙宁娜 |
| `Face_hello` | 打招呼 | 流萤打招呼 |

每个表情为 **128×64、页式、阴码、低位在上（bit0 = 顶部）** 的 1024 字节数组，与江协科技 `OLED_ShowImage` 的取模格式兼容。

---

## 功能特性

### 语音

- **全机角色音**：开机播报、唤醒回复、22 个命令词回复、超时退出、退出回复都由角色音色合成，不再混用平台机械 TTS。
- **两套独立固件**：换角色 = 重烧一次 SU-03T1，约 2 分钟；STM32 与蓝牙无需任何操作。
- **协议零改动**：仍通过 UART 9600 发送 `0x29~0x50` 单字节动作指令，原 STM32 固件完全兼容。
- **可复现管线**：阿里云百炼声音复刻 + Qwen-TTS，以及本地 GPT-SoVITS 批量合成两套方案都保留了脚本。
- **台词可维护**：`04_固件/语音词_*.xlsx` 可直接导入智能公元平台修改词条；`05_工具脚本/build_voice_xlsx.py` 可从台词 JSON 重新生成配置表。

### 屏幕

- **7 个表情位全覆盖**：睡觉、蹲下、移动、摇摆、非常快乐、站立/开机、打招呼。
- **只改位图，不改代码**：通过 `patch_hex_2026.py` 在原厂 `Project.hex` 中定位 7 个 1024 字节槽位并原位写入，附带三层校验（地址集合、差异范围、逐字节回读）。
- **多种美术方案**：`04_固件数据/` 提供 Chibi / Dither / Lum / Silhouette 四种风格，`03_预览/` 提供 1bit 与 6 倍放大预览，方便替换或继续调参。
- **可复现工具链**：Qwen-Image 3.0 Pro 生成 Q 版像素画 → Pillow 裁剪/抖动/取模 → C 数组 → HEX 补丁。

---

## 目录结构

```text
desktop-pet-voice-screen/
├─ README.md
├─ LICENSE                     # MIT（仅覆盖代码，不覆盖角色素材）
├─ .gitignore
├─ .gitattributes              # Git LFS：*.pth / *.ckpt
├─ requirements.txt
│
├─ 语音包项目/
│  ├─ README.md                # 语音包索引与使用说明
│  ├─ 00_设计方案.md            # 架构、命令字节映射、音色管线、风险
│  ├─ 烧录手册.md              # SU-03T1 接线、烧录、验证、换角色
│  ├─ 01_研究笔记/
│  │  ├─ BV*_字幕.txt          # 5 个 B 站教程的视频字幕
│  │  └─ 音频/                 # 参考视频音轨（m4a）
│  ├─ 02_声音样本/
│  │  ├─ *.m4a                 # B 站角色原声样本
│  │  └─ *_ref*.wav            # 声音复刻 / GPT-SoVITS 参考音频
│  ├─ 03_合成音频/
│  │  ├─ 芙宁娜包/、流萤包/     # 逐条台词 wav + 批量结果
│  │  └─ 试听/、试听2/          # 平台音色试听对比
│  ├─ 04_固件/
│  │  ├─ 芙宁娜/、流萤/         # jx_firm（bin + readme + 平台配置 json）
│  │  ├─ *.tar.gz              # 智能公元平台导出的固件包
│  │  └─ 语音词_*.xlsx          # 可重新导入平台的词条配置
│  ├─ 05_工具脚本/
│  │  ├─ bailian_cli.py        # 百炼声音复刻 / TTS CLI
│  │  ├─ batch_tts.py          # GPT-SoVITS 批量合成
│  │  ├─ build_voice_xlsx.py   # 台词 JSON → 语音词 xlsx
│  │  ├─ probe_*.py            # 平台接口 / 模型探测
│  │  ├─ transcribe_*.py       # 字幕 / 参考音频转写
│  │  ├─ 台词清单_*.json        # 逐条台词与 id
│  │  └─ api_key_new.txt.example
│  └─ 06_模型权重/
│     ├─ 芙宁娜/               # GPT-SoVITS .ckpt / .pth（Git LFS）
│     └─ 流萤/
│
└─ 表情替换项目/
   ├─ README.md                # 屏幕表情索引与 HEX 补丁说明
   ├─ 01_素材下载/              # 官方立绘、参考图、Qwen-Image 生成图
   ├─ 02_脚本/
   │  ├─ convert_to_oled.py    # 立绘 → 128×64 单色候选
   │  ├─ pixel_art.py          # 手绘 Q 版像素画
   │  ├─ gen_images.py         # 百炼 Qwen-Image 文生图
   │  ├─ patch_hex_2026.py     # 原厂 HEX 原位替换 7 个表情位
   │  ├─ verify_*.py           # 取模 / HEX 校验
   │  └─ analyze_*.py          # 原固件表情槽位分析
   ├─ 03_预览/                 # 1bit、6x 放大预览、C 数组 dump
   └─ 04_固件数据/              # 8 个风格化表情 C 数组
```

> 说明：`语音包项目/06_模型权重/` 中的 `.pth` / `.ckpt` 由 **Git LFS** 管理；克隆时请先执行 `git lfs install`，否则只会得到指针文件。

---

## 环境与依赖

### 必需

- **Python 3.10+**
- Python 包：`Pillow`、`openpyxl`、`requests`、`dashscope`
- **Git LFS**（模型权重）
- 烧录工具：
  - 语音：`UniOneUpdateTool.exe`（SU-03T1 串口升级）
  - STM32：`FlyMcu`（原项目资料包内）
  - USB 转串口：CH340 / CP2102

```bash
pip install -r requirements.txt
git lfs install
```

### 可选

- **GPT-SoVITS**：本地批量 TTS。脚本默认 `GPT_ROOT = D:\GPT-SoVITS`，使用前请按本机路径修改。
- **阿里云百炼 API Key**：声音复刻 / Qwen-TTS / Qwen-Image。把 `语音包项目/05_工具脚本/api_key_new.txt.example` 复制为 `api_key_new.txt` 并填入自己的 Key；也可使用环境变量 `BAILIAN_API_KEY`。
- **faster-whisper / FunASR**：字幕与参考音频转写（仅 `transcribe_*.py` 需要）。

> 真实 API Key 不入库。仓库里只有 `.example` 占位文件。

---

## 快速开始

### 1. 克隆仓库

```bash
git lfs install
git clone https://github.com/token1008/desktop-pet-voice-screen.git
cd desktop-pet-voice-screen
```

如果已经克隆但模型权重是几百字节的指针文件：

```bash
git lfs pull
```

### 2. 烧录语音固件

适用硬件：**桌宠小狗 V1.2.0 电路板 + SU-03T1**。

接线（升级模式）：

| SU-03T1 引脚 | USB-TTL |
|---|---|
| **B7** | RXD |
| **B6** | TXD |
| **GND** | GND |

步骤：

1. 打开 `UniOneUpdateTool.exe`。
2. 选择对应角色的 **`jx_su_03t_release_update.bin`**。
   - 芙宁娜：`语音包项目/04_固件/芙宁娜/jx_firm/jx_su_03t_release_update.bin`
   - 流萤：`语音包项目/04_固件/流萤/jx_firm/jx_su_03t_release_update.bin`
   - ⚠️ **必须选带 `_update` 后缀的 bin**；选错会导致烧完无法开机。
3. 点「烧录」，此时模块**不要上电**。
4. 给模块上电，等待进度条到 100%。
5. 显示「下载完成」后模块自动重启，装回小狗测试。

完整验证清单与常见问题见 [`语音包项目/烧录手册.md`](语音包项目/烧录手册.md)。

### 3. 烧录屏幕表情固件

屏幕表情的最终产物是一个修改过 7 个表情位的 STM32 HEX。由于原固件采用 **GPL-3.0**，本仓库**不直接分发**原版或修改版 HEX，只提供补丁脚本与表情数据。生成方法：

1. 从原作者项目获取完整资料包（含 `Project.hex` 与 `Face_Data_2026.c` 所在工程）：
   - 立创开源硬件平台：<https://oshwhub.com/sngelswyh/stm32-smart-desktop-pet>
2. 把 `表情替换项目/03_预览/Face_Data_2026_content.txt` 复制为工程中的 `Face_Data_2026.c`（或按脚本里的 `SRC_C` 路径放置）。
3. 按本机实际路径修改 `表情替换项目/02_脚本/patch_hex_2026.py` 顶部的 `SRC_C`、`HEX_IN`、`HEX_OUT`。
4. 运行：

```bash
python -I 表情替换项目/02_脚本/patch_hex_2026.py
```

5. 用 `FlyMcu` 把生成的 `Project_Face2026.hex` 烧录到 STM32F103C8T6。

> 补丁脚本会做三层校验：地址集合不变、差异全部落在 7 个表情区、逐字节回读比对。若校验失败会直接报错，不会静默写出错误固件。

---

## 语音包制作流程

整体管线（详见 [`语音包项目/00_设计方案.md`](语音包项目/00_设计方案.md)）：

```text
B 站原声视频
   │  yt-dlp 下载 + ffmpeg 截取 10~20s 干净独白
   ▼
02_声音样本/*.wav
   │  百炼声音复刻（qwen-voice-enrollment / qwen3-tts-vc）
   ▼
角色音色
   │  台词清单 JSON → 批量合成
   ▼
03_合成音频/芙宁娜包、流萤包/*.wav
   │  ffmpeg 转 16kHz 单声道
   ▼
智能公元平台「个性化音频」上传 + 语音词配置
   ▼
04_固件/*/jx_firm/jx_su_03t_release_update.bin
```

### 方案 A：阿里云百炼（声音复刻 + Qwen-TTS）

```bash
# 1) 准备 Key
cp 语音包项目/05_工具脚本/api_key_new.txt.example 语音包项目/05_工具脚本/api_key_new.txt
# 编辑 api_key_new.txt 填入自己的百炼 Key

# 2) 声音复刻（示例）
python -I 语音包项目/05_工具脚本/bailian_cli.py clone 语音包项目/02_声音样本/furina_ref.wav --name furina

# 3) 批量合成（按脚本内参数/台词 JSON 调整）
python -I 语音包项目/05_工具脚本/synth_qwen.py
```

### 方案 B：本地 GPT-SoVITS

```bash
# 先安装 GPT-SoVITS，并修改 batch_tts.py 里的 GPT_ROOT
python -I 语音包项目/05_工具脚本/batch_tts.py \
  --lines 语音包项目/05_工具脚本/台词清单_芙宁娜.json \
  --t2s 语音包项目/06_模型权重/芙宁娜/Funina-e15.ckpt \
  --vits 语音包项目/06_模型权重/芙宁娜/Funina_e8_s464.pth \
  --ref 语音包项目/02_声音样本/furina_ref.wav \
  --ref-text "参考音频对应的文字" \
  --out-dir 语音包项目/03_合成音频/芙宁娜包/batch
```

> 脚本里的 `D:\桌宠\...`、`D:\GPT-SoVITS` 都是作者本机路径，使用前请替换成自己的路径。台词必须与合成音频逐字一致，因为它是平台「个性化音频」的词条键。

---

## 屏幕表情制作流程

```text
官方立绘 / Enka.Network 图标 / Qwen-Image 生成图
   │  convert_to_oled.py（裁剪、缩放、阈值/抖动）
   ▼
128×64 1bit 候选（03_预览/*.png）
   │  pixel_art.py（手绘 Q 版）/ gen_convert.py
   ▼
C 数组（04_固件数据/*.c 或 03_预览/Face_Data_2026_content.txt）
   │  patch_hex_2026.py（定位 7×1024 字节槽位）
   ▼
Project_Face2026.hex（FlyMcu 烧录）
```

常用命令：

```bash
# 立绘 → OLED 候选（输出到 stdout，重定向保存）
python -I 表情替换项目/02_脚本/convert_to_oled.py png furina_dit > 表情替换项目/03_预览/out_furina.txt

# 手绘像素画（sim 为模拟预览，blue/white 为配色）
python -I 表情替换项目/02_脚本/pixel_art.py sim furina blue > 表情替换项目/03_预览/out_sim.txt

# 校验取模 / HEX
python -I 表情替换项目/02_脚本/verify_face2026.py
```

> 这些脚本依赖 Pillow；`convert_to_oled.py` / `pixel_art.py` 只输出到 stdout，不直接写文件。

---

## 信息与资源来源

本项目是二次创作，所有原始来源如下。**角色 IP、立绘、原声样本的版权归原权利人所有**，本仓库仅作个人学习与非商业用途的记录。

| 类别 | 来源 | 用途 / 说明 | 链接 |
|---|---|---|---|
| **原始桌宠项目** | **Sngels_wyh（森卓洛斯·WYH）** | 硬件设计、V1.2.0 电路板、STM32 固件、舵机动作、UART 协议、模型与资料包；原项目采用 **GPL-3.0** | [立创开源](https://oshwhub.com/sngelswyh/stm32-smart-desktop-pet) · [B 站 v1.0](https://www.bilibili.com/video/BV1xD6MYGEzD/) · [v1.1](https://www.bilibili.com/video/BV17hAaeXEY4/) · [v1.2/v1.2.1](https://www.bilibili.com/video/BV1XRhyzGE2E/) |
| **教程参考** | **科技手造局**（B 站） | 5 个视频的字幕与流程参考：焊接、代码写入、SU-03T1 语音模块改词/烧录、蓝牙连接 | [BV1nuJAzkEs7](https://www.bilibili.com/video/BV1nuJAzkEs7/) · [BV1tPJrz8EFz](https://www.bilibili.com/video/BV1tPJrz8EFz/) · [BV1KaEfz3EPJ](https://www.bilibili.com/video/BV1KaEfz3EPJ/) · [BV1bwE2zVEv2](https://www.bilibili.com/video/BV1bwE2zVEv2/) · [BV1DNjmzGE4y](https://www.bilibili.com/video/BV1DNjmzGE4y/) |
| **语音模块** | **机芯智能（AIMachip）** | SU-03T / SU-03T1 离线语音模组规格、串口协议、固件说明 | [官网](http://www.aimachip.com/) · [SU-03T 文档](https://docs.aimachip.com/zh-cn/latest/file/offlineVoice/SU03T.html) |
| **语音固件平台** | **智能公元（SmartPi）** | 零代码配置唤醒词、命令词、回复语、个性化音频，生成 SU-03T1 固件 | [平台](http://www.smartpi.cn/) |
| **OLED 驱动 / 取模** | **江协科技** | `OLED_ShowImage` 驱动与 128×64 页式取模格式；本项目表情数据与其兼容 | [OLED 教程](https://jiangxiekeji.com/tutorial/oled.html) · [B 站视频](https://www.bilibili.com/video/BV1EN41177Pc/) |
| **声音复刻 / TTS** | **阿里云百炼（Model Studio）** | 角色音色复刻（qwen-voice-enrollment / qwen3-tts-vc）、Qwen-TTS 批量合成 | [百炼控制台](https://bailian.console.aliyun.com/) · [文档](https://help.aliyun.com/zh/model-studio/) |
| **本地 TTS** | **GPT-SoVITS** | 本地批量合成角色语音；`06_模型权重/` 为训练/微调得到的 `.ckpt` / `.pth` | [GitHub](https://github.com/RVC-Boss/GPT-SoVITS) |
| **文生图** | **阿里云百炼 Qwen-Image 3.0 Pro** | 生成 Q 版像素画素材（趴姿、凝视、兴奋、打招呼等） | [百炼控制台](https://bailian.console.aliyun.com/) |
| **角色立绘 / 图标** | **米哈游 / HoYoverse 官方** 与 **Enka.Network** | 芙宁娜、流萤立绘与图标；文件名带 `_enka` 后缀的素材取自 Enka.Network | [米哈游](https://www.mihoyo.com/) · [原神](https://ys.mihoyo.com/) · [星穹铁道](https://sr.mihoyo.com/) · [Enka.Network](https://enka.network/) |
| **原声样本** | **Bilibili 角色语音视频** | `02_声音样本/*.m4a` 用于声音复刻的参考样本；m4a 元数据标记为 “Packed by Bilibili XCoder”，具体 BV 号未在项目中记录 | [Bilibili](https://www.bilibili.com/) |
| **蓝牙调试器（未包含）** | **XLazyDog** | 原桌宠蓝牙控制 App，作者资料包内整理，本仓库未收录 | — |
| **灵感来源** | **有出息的男孩** | 原作者 Sngels_wyh 在项目页提到的桌宠灵感来源 | — |

---

## 参考资料链接

### 原始项目与教程

- Sngels_wyh · STM32 智能桌面宠物（立创开源，GPL-3.0）：<https://oshwhub.com/sngelswyh/stm32-smart-desktop-pet>
- Sngels_wyh · v1.0 总教程：<https://www.bilibili.com/video/BV1xD6MYGEzD/>
- Sngels_wyh · v1.1 总教程：<https://www.bilibili.com/video/BV17hAaeXEY4/>
- Sngels_wyh · v1.2 / v1.2.1 总教程：<https://www.bilibili.com/video/BV1XRhyzGE2E/>
- Sngels_wyh · 项目展示：<https://www.bilibili.com/video/BV1TLsmevEBp/>
- 科技手造局 ·（一）V1.2 焊接 + 测试：<https://www.bilibili.com/video/BV1nuJAzkEs7/>
- 科技手造局 ·（二）代码 + SU-03T1 烧录：<https://www.bilibili.com/video/BV1tPJrz8EFz/>
- 科技手造局 ·（三）蓝牙连接：<https://www.bilibili.com/video/BV1KaEfz3EPJ/>
- 科技手造局 ·（四）SU-03T1 改名字/指令/回复语：<https://www.bilibili.com/video/BV1DNjmzGE4y/>
- 科技手造局 · V1.1 焊接/代码/组装：<https://www.bilibili.com/video/BV1bwE2zVEv2/>

### 语音模块与固件平台

- 机芯智能官网：<http://www.aimachip.com/>
- SU-03T 文档中心：<https://docs.aimachip.com/zh-cn/latest/file/offlineVoice/SU03T.html>
- 智能公元零代码平台：<http://www.smartpi.cn/>

### OLED 与取模

- 江协科技 · 0.96 寸 OLED 教程：<https://jiangxiekeji.com/tutorial/oled.html>
- 江协科技 · OLED 视频教程：<https://www.bilibili.com/video/BV1EN41177Pc/>
- 江协科技资料下载：<https://jiangxiekeji.com/download.html>

### 语音 / 图像生成

- 阿里云百炼控制台：<https://bailian.console.aliyun.com/>
- 阿里云百炼文档：<https://help.aliyun.com/zh/model-studio/>
- GPT-SoVITS：<https://github.com/RVC-Boss/GPT-SoVITS>

### 角色素材

- 米哈游官网：<https://www.mihoyo.com/>
- 原神官网：<https://ys.mihoyo.com/>
- 崩坏：星穹铁道官网：<https://sr.mihoyo.com/>
- Enka.Network：<https://enka.network/>
- Enka.Network API 文档：<https://github.com/EnkaNetwork/API-docs>

---

## 版权与使用限制

本仓库采用 **代码与素材分离** 的授权方式：

| 内容 | 授权 / 状态 |
|---|---|
| 本项目新增的脚本、文档、配置 | **MIT**（见 [`LICENSE`](LICENSE)） |
| 芙宁娜 / 流萤角色立绘、图标、原声样本、角色语音合成音频 | **版权归米哈游 / HoYoverse 及相关权利人**；**不适用 MIT**；仅限个人学习、研究与个人桌宠使用，**禁止商用、禁止单独再分发、禁止冒充官方** |
| 声音复刻产生的音色与音频 | 仅限个人非商业使用；不得用于冒充真人、诈骗、商业配音或其他侵权场景；使用百炼服务时需遵守阿里云服务条款 |
| 原作者的 STM32 固件 / 硬件工程 | **GPL-3.0**；本仓库不包含原版 `Project.hex` 及其修改版 `Project_Face2026.hex`，仅提供补丁脚本 |
| 机芯智能 SU-03T1 固件 / SDK | 受机芯智能与智能公元平台条款约束；固件仅供个人烧录使用 |

补充说明：

- 本仓库是**非官方粉丝二创**，与米哈游 / HoYoverse、机芯智能、阿里云均无隶属或授权关系。
- 如果你要公开发布、商用或制作衍生商品，请自行取得角色 IP、声音权利与固件/平台方的授权。
- 若权利人认为本仓库中的素材侵犯其权益，请通过 GitHub Issue 联系，我会尽快删除相关素材。

---

## 常见问题

### Q1：为什么仓库里没有 `Project_Face2026.hex`？

因为它是原项目 `Project.hex` 的衍生作品，而原项目采用 **GPL-3.0**。本仓库代码采用 MIT，直接分发 GPL 衍生的 HEX 会产生许可证冲突。仓库改为提供 `patch_hex_2026.py` + 表情数据，你从原作者项目获取原版 HEX 后在本机生成即可。

### Q2：为什么模型权重用 Git LFS？

`06_模型权重/` 里的 4 个文件均超过 GitHub 100MB 单文件上限（最大约 173MB）。仓库用 `.gitattributes` 将 `*.pth`、`*.ckpt` 交给 Git LFS 管理。

### Q3：克隆后模型文件只有几百字节？

说明没有拉取 LFS 对象。执行：

```bash
git lfs install
git lfs pull
```

### Q4：脚本报 `FileNotFoundError` 或路径错误？

脚本里保留了作者本机的绝对路径（如 `D:\桌宠\...`、`D:\GPT-SoVITS`）。请按你的实际目录修改脚本顶部的路径常量。

### Q5：提示缺少 `api_key_new.txt`？

复制示例文件并填入自己的百炼 Key：

```bash
cp 语音包项目/05_工具脚本/api_key_new.txt.example 语音包项目/05_工具脚本/api_key_new.txt
```

### Q6：语音固件烧完无法开机？

大概率选错了不带 `_update` 的 bin。重新选择 `jx_su_03t_release_update.bin` 烧录一次即可恢复。

### Q7：唤醒不灵敏？

在智能公元平台配置页调高「唤醒灵敏度」，重新发布版本并重烧；或检查麦克风/喇叭接线与供电。

### Q8：可以商用吗？

**不可以。** 代码是 MIT，但角色立绘、原声、角色语音等素材版权归原权利人，仅限个人非商业使用。商用需自行取得授权。

---

## 许可证

本项目新增的**代码与文档**采用 [MIT License](LICENSE) 开源。

**角色素材、原声样本、角色语音合成音频不适用 MIT**，其版权归米哈游 / HoYoverse 及相关权利人所有，仅限个人非商业使用。原作者的固件与硬件工程采用 GPL-3.0，本仓库未直接分发其衍生 HEX。完整的素材版权与使用限制见 [NOTICE.md](NOTICE.md)。

---

## 致谢

- **Sngels_wyh（森卓洛斯·WYH）**：开源桌宠硬件、STM32 固件、协议与完整资料包。
- **科技手造局**：SU-03T1 语音模块改词、烧录与蓝牙教程。
- **江协科技**：STM32 与 OLED 驱动/取模教程。
- **机芯智能 / 智能公元**：SU-03T1 模组与零代码语音固件平台。
- **阿里云百炼**：声音复刻、Qwen-TTS、Qwen-Image。
- **GPT-SoVITS**：本地语音合成管线。
- **Enka.Network**：角色图标与数据服务。
- **米哈游 / HoYoverse**：芙宁娜、流萤角色与世界观。

---

<p align="center">
  <sub>本项目仅用于个人学习与桌宠爱好，非官方作品。角色版权归原权利人所有。</sub>
</p>
