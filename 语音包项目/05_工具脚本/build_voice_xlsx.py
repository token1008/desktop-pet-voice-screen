# -*- coding: utf-8 -*-
"""基于平台导出的语音词 Excel 模板，生成芙宁娜/流萤两份配置。

回复语文本必须与 03_合成音频 中已合成音频的台词逐字一致（作为个性化音频的词条键）。
"""
import openpyxl

TEMPLATE = r"D:\桌宠\语音包项目\01_研究笔记\语音词导出_0.xlsx"

# 与台词清单_*.json 一致（id → 台词）
FURINA = {
    "wake": "芙宁娜大人",
    "wake_reply": "哼哼~芙宁娜大人，听候你的差遣！|嗯哼~有何吩咐？|叫我做什么呀？",
    "boot": "有|请说芙宁娜大人来唤醒我",
    "reply_AA": "啊……观众都散场了，本大人也要休息了",
    "reply_BB": "好吧好吧，坐下来看你一眼",
    "reply_CC": "看好了！优雅，永不过时！",
    "reply_DD": "呜……趴下了，可不许笑我",
    "reply_EE": "跟我来，舞台中央就是这里！",
    "reply_FF": "退场，也是演出的一部分",
    "reply_GG": "向左~注意仪态，看我演示",
    "reply_HH": "向右~仪态万方！",
    "reply_II": "一起摇摆吧，嘿嘿~",
    "reply_JJ": "再快一点！掌声在哪里！",
    "reply_KK": "气氛还不够热烈！",
    "reply_LL": "尾巴听我号令~摇！",
    "reply_MM": "看本大人的华丽一跳！",
    "reply_NN": "华丽的退场，跃！",
    "reply_OO": "很高兴见到你，请多关照啦！",
    "reply_PP": "灯光亮起，舞台属于我！",
    "reply_QQ": "谢幕~灯灭。",
    "reply_RR": "氛围感，懂不懂呀？",
    "reply_SS": "哼，安分一点啦~",
    "reply_TT": "呼啊……再睡五百年",
    "reply_UU": "演出前要热身的！",
    "reply_VV": "让本大人看看你的状态",
    "reply_WW": "芙宁娜大人，任务完成",
    "timeout": "哼，本大人先休息了，想我就喊我",
    "exit": "好吧好吧，本大人先退场了",
}

FIREFLY = {
    "wake": "流萤大人",
    "wake_reply": "嗯，收到~我在哦！|随时待命，交给我吧|今天想去哪里玩呀？",
    "boot": "有|请说流萤大人来唤醒我",
    "reply_AA": "那……我休息一会儿，晚安",
    "reply_BB": "蹲下来啦，像只小机甲",
    "reply_CC": "站好了，随时可以出发",
    "reply_DD": "趴下休息……别看我哦",
    "reply_EE": "收到，出发！",
    "reply_FF": "战术后撤~",
    "reply_GG": "向左转，跟上我",
    "reply_HH": "向右转，目标确认",
    "reply_II": "摇摆模式，启动！",
    "reply_JJ": "引擎功率，提升！",
    "reply_KK": "再快一点也没问题",
    "reply_LL": "尾巴系统，切换",
    "reply_MM": "跃迁——！",
    "reply_NN": "战术后跳！",
    "reply_OO": "你好呀，很高兴见到你",
    "reply_PP": "照明系统，开启",
    "reply_QQ": "灯光关闭，晚上好",
    "reply_RR": "呼吸灯，启动~",
    "reply_SS": "呼吸灯，关闭",
    "reply_TT": "呼……活动一下关节",
    "reply_UU": "关节校准中，请稍等",
    "reply_VV": "电量信息，已显示",
    "reply_WW": "流萤大人，任务完成",
    "timeout": "那我先待机啦，需要时随时叫我",
    "exit": "好的，那我先走啦",
}


def build(character: dict, out_path: str):
    wb = openpyxl.load_workbook(TEMPLATE)
    ws_cmd = wb["命令词"]
    # 行10起为数据：A=行为名称, D=命令词, G=回复语
    for row in range(10, ws_cmd.max_row + 1):
        action = ws_cmd.cell(row=row, column=1).value
        if not action:
            continue
        if action == "WW":
            # 彩蛋命令：触发词改为「和我说句话」
            ws_cmd.cell(row=row, column=4).value = "和我说句话"
        key = f"reply_{action}"
        if key in character:
            ws_cmd.cell(row=row, column=7).value = character[key]
    ws_voice = wb["语音词"]
    # 行13=唤醒词, 14=唤醒回复, 17=开机播报, 18=超时退出回复, 20=退出回复（B列=内容）
    ws_voice.cell(row=13, column=2).value = character["wake"]
    ws_voice.cell(row=14, column=2).value = character["wake_reply"]
    ws_voice.cell(row=17, column=2).value = character["boot"]
    ws_voice.cell(row=18, column=2).value = character["timeout"]
    ws_voice.cell(row=20, column=2).value = character["exit"]
    wb.save(out_path)
    print("saved:", out_path)


if __name__ == "__main__":
    build(FURINA, r"D:\桌宠\语音包项目\04_固件\语音词_芙宁娜.xlsx")
    build(FIREFLY, r"D:\桌宠\语音包项目\04_固件\语音词_流萤.xlsx")
