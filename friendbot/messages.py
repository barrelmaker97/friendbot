import ujson


def health_message(sentence):
    return ujson.dumps({"status": "running", "sentence_generation": isinstance(sentence, str)})


def error_message():
    return ujson.dumps(
        {
            "response_type": "ephemeral",
            "replace_original": False,
            "text": "Sorry, that didn't work. Please try again.",
        }
    )


def cancel_message():
    return ujson.dumps({"delete_original": True})


def send_message(sentence, real_name):
    context_msg = f"Sent by {real_name}"
    return ujson.dumps(
        {
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
    )


def prompt_message(sentence, user, channel):
    return ujson.dumps(
        {
            "replace_original": True,
            "response_type": "ephemeral",
            "blocks": [
                {"type": "section", "text": {"type": "plain_text", "text": sentence}},
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "emoji": True,
                                "text": "Send",
                            },
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
                            "text": {
                                "type": "plain_text",
                                "emoji": True,
                                "text": "Cancel",
                            },
                            "style": "danger",
                            "value": "cancel",
                        },
                    ],
                },
            ],
        }
    )
