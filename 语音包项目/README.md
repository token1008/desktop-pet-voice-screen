# 语音包项目

给桌宠小狗 V1.2.0 的 **SU-03T1** 语音模块制作两套角色语音固件：**芙宁娜** 与 **流萤**。

## 快速入口

| 想做什么 | 看这里 |
|---|---|
| 直接烧录现成固件 | [`烧录手册.md`](烧录手册.md) |
| 了解架构与命令字节映射 | [`00_设计方案.md`](00_设计方案.md) |
| 重新合成台词 | [`05_工具脚本/`](05_工具脚本/) |
| 改语音词后重新生成固件 | [`04_固件/语音词_*.xlsx`](04_固件/) → 智能公元平台 |
| 查看台词与音频 | [`03_合成音频/`](03_合成音频/) |

## 两套固件

| 角色 | 唤醒词 | 烧录文件 |
|---|---|---|
| 芙宁娜 | 芙宁娜大人 | `04_固件/芙宁娜/jx_firm/jx_su_03t_release_update.bin` |
| 流萤 | 流萤大人 | `04_固件/流萤/jx_firm/jx_su_03t_release_update.bin` |

- 每个固件包含：3 条唤醒回复 + 22 个命令词回复 + 30 条个性化音频。
- 开机播报、300 秒超时、退出回复也都使用角色音色。
- UART 9600 的 `0x29~0x50` 单字节动作协议与原版一致，**STM32 固件无需改动**。

> ⚠️ 烧录时必须选择带 `_update` 后缀的 bin，否则烧完无法开机。

## 目录说明

```text
语音包项目/
├─ 00_设计方案.md          # 目标、架构、命令字节、音色管线、风险
├─ 烧录手册.md              # 接线、烧录、验证、换角色、FAQ
├─ 01_研究笔记/             # 5 个 B 站教程的字幕 + 参考视频音轨
├─ 02_声音样本/             # 角色原声 m4a + 复刻参考 wav
├─ 03_合成音频/             # 芙宁娜包 / 流萤包 / 试听
├─ 04_固件/                 # bin、tar.gz、语音词 xlsx、平台配置 json
├─ 05_工具脚本/             # 百炼 / GPT-SoVITS / 转写 / 词表生成
└─ 06_模型权重/             # GPT-SoVITS .ckpt / .pth（Git LFS）
```

## 重新合成语音

### 阿里云百炼

```bash
cp 05_工具脚本/api_key_new.txt.example 05_工具脚本/api_key_new.txt
# 编辑 api_key_new.txt，填入自己的百炼 API Key

python -I 05_工具脚本/bailian_cli.py clone 02_声音样本/furina_ref.wav --name furina
python -I 05_工具脚本/synth_qwen.py
```

### 本地 GPT-SoVITS

```bash
# 先安装 GPT-SoVITS，并修改 batch_tts.py 里的 GPT_ROOT
python -I 05_工具脚本/batch_tts.py \
  --lines 05_工具脚本/台词清单_芙宁娜.json \
  --t2s 06_模型权重/芙宁娜/Funina-e15.ckpt \
  --vits 06_模型权重/芙宁娜/Funina_e8_s464.pth \
  --ref 02_声音样本/furina_ref.wav \
  --ref-text "参考音频对应的文字" \
  --out-dir 03_合成音频/芙宁娜包/batch
```

> 脚本内的 `D:\桌宠\...`、`D:\GPT-SoVITS` 是作者本机路径，使用前请替换。
> 台词文本必须与合成音频逐字一致，因为它是智能公元平台「个性化音频」的词条键。

## 版权说明

- 角色语音、原声样本、角色立绘版权归米哈游 / HoYoverse 及相关权利人所有。
- 本目录内容仅限个人学习与个人桌宠使用，**禁止商用**。
- 语音复刻与合成请遵守阿里云百炼服务条款及声音权利人的授权范围。

## 来源与参考

- 原始桌宠项目（Sngels_wyh，GPL-3.0）：<https://oshwhub.com/sngelswyh/stm32-smart-desktop-pet>
- 机芯智能 SU-03T 文档：<https://docs.aimachip.com/zh-cn/latest/file/offlineVoice/SU03T.html>
- 智能公元平台：<http://www.smartpi.cn/>
- 阿里云百炼：<https://bailian.console.aliyun.com/>
- GPT-SoVITS：<https://github.com/RVC-Boss/GPT-SoVITS>
- 教程参考（科技手造局）：[BV1nuJAzkEs7](https://www.bilibili.com/video/BV1nuJAzkEs7/) · [BV1tPJrz8EFz](https://www.bilibili.com/video/BV1tPJrz8EFz/) · [BV1KaEfz3EPJ](https://www.bilibili.com/video/BV1KaEfz3EPJ/) · [BV1bwE2zVEv2](https://www.bilibili.com/video/BV1bwE2zVEv2/) · [BV1DNjmzGE4y](https://www.bilibili.com/video/BV1DNjmzGE4y/)
