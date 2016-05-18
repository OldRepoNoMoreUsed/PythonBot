import time

from slackclient import SlackClient

def truc():
    """
    blablabla

    >>> truc()
    1

    :return:
    """
    return 1

TOKEN="xoxb-"

bot = SlackClient(TOKEN)
if bot.rtm_connect():
    try:
        while True:
            messages = bot.rtm_read()
            if messages:
                print(messages)
                print("Coucou")
            else:
                time.sleep(1)
    except KeyboardInterrupt:
        pass
