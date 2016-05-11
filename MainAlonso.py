import time

from slackclient import SlackClient

TOKEN="xoxb-38203543493-XFvbmk66Z1bTg4ru7iorArpS"

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
