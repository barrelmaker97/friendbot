from behave import when
from friendbot import corpus


@when('we load {quality} {category} data from {location}')
def load_data(context, quality, category, location):
    passed = True
    try:
        if category == "channel":
            corpus.getChannelDict(location)
        elif category == "user":
            corpus.getUserDict(location)
    except Exception:
        if quality == "good":
            passed = False
    assert passed
