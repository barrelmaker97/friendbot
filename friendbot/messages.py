import json


def errorMessage():
    payload = {
        "response_type": "ephemeral",
        "replace_original": False,
        "text": "Sorry, that didn't work. Please try again.",
    }
    return json.dumps(payload)


def cancelMessage():
    payload = {"delete_original": True}
    return json.dumps(payload)


def sendMessage(sentence, real_name):
    context_msg = f"Sent by {real_name}"
    payload = {
        "delete_original": True,
        "response_type": "in_channel",
        "blocks": [
            {"type": "section", "text": {"type": "plain_text", "text": sentence}},
            {
                "type": "context",
                "elements": [{"type": "plain_text", "text": context_msg}],
            },
        ],
    }
    return json.dumps(payload)


def promptMessage(sentence, user, channel):
    payload = {
        "replace_original": True,
        "response_type": "ephemeral",
        "blocks": [
            {"type": "section", "text": {"type": "plain_text", "text": sentence}},
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "emoji": True, "text": "Send"},
                        "style": "primary",
                        "value": sentence,
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "emoji": True,
                            "text": "Shuffle",
                        },
                        "value": f"{user} {channel}",
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "emoji": True, "text": "Cancel"},
                        "style": "danger",
                        "value": "cancel",
                    },
                ],
            },
        ],
    }
    return json.dumps(payload)
