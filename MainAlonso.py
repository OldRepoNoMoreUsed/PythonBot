"""Slack bot pour checker les modification d'un fichier"""

import asyncio
import json
import aiohttp
import os
from os import stat
from stat import ST_MTIME
from time import localtime, asctime

from api import api_call
from config import DEBUG, TOKEN


class BotAlonso:
    def __init__(self, token = TOKEN):
        self.token = TOKEN
        self.rtm = None

        self.commandeDic = {
            "add": self.add,
            "check": self.check,
            "help": self.help
        }

    async def connect(self):
        """Fonction de connection de notre bot a slack"""

        self.rtm = await api_call('rtm.start')
        assert self.rtm['ok'], self.rtm['error']

        with aiohttp.ClientSession() as client:
            async with client.ws_connect(self.rtm["url"]) as ws:
                print("debug")
                async for msg in ws:
                    print(msg)
                    assert msg.tp == aiohttp.MsgType.text
                    message = json.loads(msg.data)
                    asyncio.ensure_future(self.execute(message))

    async def execute(self, message):
        """Lis et execute la commande passé dans le message"""
        if message.get('type') == 'message':
            id_chan = message.get('channel')

            id_utilisateur = message.get('user')

            id_team = self.rtm['team']['id']

            id_bot = self.rtm['self']['id']

            texte = message.get('text')

            if isinstance(texte, str):
                texte_split = texte.split(':', 1)
                recipient = texte_split[0].strip()

                if len(texte_split) > 0 and recipient == '<@{0}>'.format(id_bot):
                    core_texte = texte_split[1].strip()

                    core_texte_split = core_texte.split(" ", 1)
                    action = self.commandeDic.get(core_texte_split[0].strip()) or self.error

                    if len(core_texte_split) > 1:
                        if core_texte_split[0].strip() == "add" and core_texte_split[1] is not None:
                            print(await action(core_texte_split[1].strip(), id_utilisateur, id_chan, id_team))
                        else:
                            return await self.error(id_chan, id_utilisateur, id_team)
                    elif core_texte_split[0] == "add":
                        return await self.sendText("Erreur: La commande add prend en argument le chemin du fichier à contrôler", id_chan, id_team)
                    else:
                        print(await action(id_chan, id_utilisateur, id_team))

    async def sendText(self, reponse, id_chan, id_team):
        """Envoie la reponse du bot"""
        return await api_call('chat.postMessage',  {"type": "message",
                                                    "channel": id_chan,
                                                    "text": reponse,
                                                    "team": id_team})

    async def add(self, argument, id_utilisateur, id_chan, id_team):
        """Ajoute un fihcier a la liste des fichiers à controler de l'utilisateur"""
        if os.path.isfile(argument):
            infos = stat(argument)
            print(asctime(localtime(infos[ST_MTIME])))
            if os.path.exists("File/" + id_utilisateur + ".txt"):
                with open("File/" + id_utilisateur + ".txt", "a") as file:
                    file.write(argument + " " + str(infos[ST_MTIME]) + "\n")
            else:
                with open("File/" + id_utilisateur + ".txt", "w") as file:
                    file.write(argument + " " + str(infos[ST_MTIME]) + "\n")
            reponse = "Fichier ajouté avec succès"
        else:
            reponse = "Erreur: L'argument passé n'est pas un fichier !"
        return await self.sendText(reponse, id_chan, id_team)

    async def check(self, id_chan, id_utilisateur, id_team):
        """Controle la modification du fichier"""
        path = "File/" + id_utilisateur + ".txt"
        reponse = "Fichier contrôler: \n"
        if os.path.exists(path):
            with open(path) as file:
                for line in file:
                    lines = line.split(' ', 1)
                    reponse += lines[0]
                    infos = stat(lines[0])
                    last_modif = infos[ST_MTIME]
                    if str(last_modif) == lines[1].strip():
                        reponse += ": n'a pas été modifié !\n"
                    else:
                        #http://stackoverflow.com/questions/39086/search-and-replace-a-line-in-a-file-in-python
                        line.replace(line, "poil")
                        reponse += ": a subi des modifications !\n"
        else:
            reponse = "Aucun fichier à contrôler"
        return await self.sendText(reponse, id_chan, id_team)

    async def help(self, id_chan, id_utilisateur, id_team):
        """Envoie le manuel utilisateur du bot"""
        print("Help")
        reponse = "Manuel du bot\n" \
                  "Ce bot sert a contrôler si un  fichier a été modifié.\n" \
                  "La commande add permet d'ajouter un fichier à une liste de fichier a controler. Chaque utilisateur a une liste personnelle\n" \
                  "Format de la commande add => @alonso: add chemin/fichier\n" \
                  "La commande check demande au bot de parcourir la liste assignée à l'utilisateur et a contrôler si des fichiers ont été modifiés\n" \
                  "Format de la commande check => @alonso: check\n" \
                  "Enjoy our bot and Allons-y Alonso !!!"
        return await self.sendText(reponse, id_chan, id_team)

    async def error(self, id_chan,id_utilisateur, id_team):
        """Envoie un message d'erreur lorsqu'une commande erroné est entrée"""
        error = "La commande que vous avez entré n'existe pas. Taper 'help' pour recevoir de l'aide !"
        return await self.sendText(error, id_chan, id_team)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.set_debug(DEBUG)
    bot = BotAlonso(TOKEN)
    loop.run_until_complete(bot.connect())
    loop.close()