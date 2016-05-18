import time

from slackclient import SlackClient

"""
balbla
>>>truc()
1

blabla
"""

def truc():
    return 2

TOKEN="xoxb-"

bot = SlackClient(TOKEN)
if bot.rtm_connect():
    try:
        while True:
            messages = bot.rtm_read()
            if messages:
                print(messages)
            else:
                time.sleep(1)
    except KeyboardInterrupt:
        pass
