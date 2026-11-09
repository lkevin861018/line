"""LINE 聊天室內的功能選單與圖片瀏覽控制。"""

import json

from linebot.models import (
    CameraRollAction,
    FlexSendMessage,
    MessageAction,
    PostbackAction,
    QuickReply,
    QuickReplyButton,
)


PROMPT_COMMANDS = {
    "chat": ("AI 聊天", "@GG人 ", "請輸入想問的內容，例如：@GG人 你好"),
    "draw": ("AI 畫圖", "@GG人畫圖 ", "請輸入想畫的內容，例如：@GG人畫圖 海邊的貓"),
    "edit": (
        "AI 改圖", "@GG人改圖 ",
        "請先輸入改圖指令，例如：@GG人改圖 把背景改成海邊，再依提示傳送圖片",
    ),
    "rolltest": ("指定抽圖", "rolltest ", "請輸入圖片編號，例如：rolltest 1"),
}


def postback_action(label, **data):
    return PostbackAction(
        label=label,
        data=json.dumps(data, ensure_ascii=False, separators=(",", ":")),
        display_text=label,
    )


def prompt_action(command):
    label, prefix, _ = PROMPT_COMMANDS[command]
    action = postback_action(label, action="prompt", command=command)
    action.input_option = "openKeyboard"
    action.fill_in_text = prefix
    return action


def feature_actions(upload_command):
    return [
        MessageAction(label="隨機抽圖", text="抽"),
        MessageAction(label="銀河圖片", text="銀河"),
        prompt_action("rolltest"),
        MessageAction(label="上傳圖片", text=upload_command),
        prompt_action("chat"),
        prompt_action("draw"),
        prompt_action("edit"),
    ]


def feature_quick_reply(upload_command, *, choose_image=False):
    actions = feature_actions(upload_command)
    if choose_image:
        actions.insert(0, CameraRollAction(label="選擇圖片"))
    actions.append(MessageAction(label="功能選單", text="選單"))
    return QuickReply(items=[QuickReplyButton(action=action) for action in actions])


def button(action, style="secondary"):
    return {"type": "button", "style": style, "height": "sm", "action": action.as_json_dict()}


def feature_menu(upload_command):
    return FlexSendMessage(
        alt_text="功能選單：抽、銀河、rolltest、上傳圖片、@GG人、@GG人畫圖、@GG人改圖",
        contents={
            "type": "bubble",
            "body": {
                "type": "box", "layout": "vertical", "spacing": "md",
                "contents": [
                    {"type": "text", "text": "GG 聊天室", "weight": "bold", "size": "xl"},
                    {
                        "type": "text", "text": "點選功能開始，也可以直接輸入原本的指令。",
                        "wrap": True, "size": "sm", "color": "#666666",
                    },
                ],
            },
            "footer": {
                "type": "box", "layout": "vertical", "spacing": "sm",
                "contents": [button(action) for action in feature_actions(upload_command)],
            },
        },
    )


def image_controls(category, filename, position, total):
    label = "抽圖" if category == "roll" else "銀河"

    def browse(direction, title):
        return postback_action(
            title, action="browse", category=category, file=filename, direction=direction,
        )

    return FlexSendMessage(
        alt_text=f"{label}：第 {position}／{total} 張，可選上一張、下一張或重新抽圖",
        contents={
            "type": "bubble",
            "body": {
                "type": "box", "layout": "vertical", "spacing": "md",
                "contents": [
                    {
                        "type": "text", "text": f"{label} · {position} / {total}",
                        "weight": "bold", "align": "center",
                    },
                    {
                        "type": "box", "layout": "horizontal", "spacing": "sm",
                        "contents": [
                            button(browse("previous", "上一張")),
                            button(browse("next", "下一張")),
                        ],
                    },
                    {
                        "type": "box", "layout": "horizontal", "spacing": "sm",
                        "contents": [
                            button(browse("random", "重新抽圖"), "primary"),
                            button(MessageAction(label="功能選單", text="選單")),
                        ],
                    },
                ],
            },
        },
    )
