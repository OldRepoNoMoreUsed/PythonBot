"""Slack bot pour vérifier les modification d'un fichier"""

import asyncio
import json
import os
from os import stat
from stat import ST_MTIME

import aiohttp
import pyinotify
from Bot.config import DEBUG, TOKEN

from Bot.api import api_call


class EventHandler(pyinotify.ProcessEvent):
    """Permet de recupérer un event lié a la modification d'un fichier"""

    def process_IN_CLOSE_WRITE(self, event):
        print("**********/ Fichier modifié: ", event.pathname + "  \**********")

    def add_bot(self, BotAlonso):
        self.bot = BotAlonso


class BotAlonso:
    """Bot a proprement parlé. Ce dernier permet de vérifier l'état des fichiers que nous avons ajouté a sa liste"""
    helpmsg = """
    Manuel du bot
    Ce bot sert a contrôler si un fichier a été modifié.
    La commande add permet d'ajouter un fichier à une liste de fichier à contrôler.
    Chaque utilisateur a une liste personnelle.
    Format de la commande add => @alonso: add chemin/fichier
    La commande check demande au bot de parcourir la liste assignée à l'utilisateur et
    a contrôler si des fichiers ont été modifiés
    Format de la commande check => @alonso: check
    La commande remove permet de supprimer un fichier de la liste des fichiers à contrôler.
    Elle fonctionne sur le meme format que la commande add.
    Enjoy our bot and Allons-y Alonso !!!
    """

    def __init__(self, token=TOKEN):
        """Initialise le bot """
        self.token = token
        self.rtm = None
        self.commandeDic = {
            "add": self.add,
            "check": self.check,
            "remove": self.remove,
            "help": self.help
        }

        self.listeUser = {}
        self.listeFile = {}
        self.liste = []

        self.wm = pyinotify.WatchManager()
        self.mask = pyinotify.IN_CLOSE_WRITE

        self.handler = EventHandler()
        self.handler.add_bot(self)

        self.notifier = pyinotify.ThreadedNotifier(self.wm, self.handler)
        self.notifier.start()

    async def connect(self):
        """Fonction de connection de notre bot a slack"""

        self.rtm = await api_call('rtm.start')
        assert self.rtm['ok'], self.rtm['error']

        with aiohttp.ClientSession() as client:
            async with client.ws_connect(self.rtm["url"]) as ws:
                async for msg in ws:
                    #print(msg)
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
                        if (core_texte_split[0].strip() == "add" or core_texte_split[0].strip() == "remove") and core_texte_split[1] is not None:
                            print(await action(core_texte_split[1].strip(), id_utilisateur, id_chan, id_team))
                        else:
                            return await self.error(id_chan, id_utilisateur, id_team)
                    elif core_texte_split[0] == "add" or core_texte_split[0] == "remove":
                        return await self.sendText("Erreur: La commande que vous avez entrée prend en argument le chemin du fichier", id_chan, id_team)
                    else:
                        print(await action(id_chan, id_utilisateur, id_team))

    async def sendText(self, reponse, id_chan, id_team):
        """Envoie la reponse du bot"""
        return await api_call('chat.postMessage',  {"type": "message",
                                                    "channel": id_chan,
                                                    "text": reponse,
                                                    "team": id_team})

    async def add(self, argument, id_utilisateur, id_chan, id_team):
        """Ajoute un fichier a la liste des fichiers à controler de l'utilisateur"""
        if os.path.isfile(argument):
            infos = stat(argument)

            if id_utilisateur not in self.listeUser:
                self.listeUser[id_utilisateur] = []

            if argument not in self.listeUser[id_utilisateur]:
                self.listeUser[id_utilisateur].append(argument)

            if argument not in self.listeFile:
                self.listeFile[argument] = infos[ST_MTIME]
                self.wdd = self.wm.add_watch(argument, self.mask, rec=True)
            reponse = "Fichier ajouté avec succès"

        else:
            reponse = "L'argument n'est pas un fichier !"
        return await self.sendText(reponse, id_chan, id_team)

    async def check(self, id_chan, id_utilisateur, id_team):
        """Controle la modification du fichier"""
        reponse = "Fichier contrôlé: \n"
        liste = self.listeUser[id_utilisateur]

        if not liste:
            reponse = "Aucun fichier à contrôler"
        else:
            for element in liste:
                value = self.listeFile[element]
                infos = stat(element)
                last_modif = infos[ST_MTIME]
                if str(last_modif) == str(value):
                    reponse += element + ": n'a pas été modifié !\n"
                else:
                    self.listeFile[element] = infos[ST_MTIME]
                    reponse += element + ": a subi des modifications !\n"
        return await self.sendText(reponse, id_chan, id_team)

    async def remove(self, argument, id_utilisateur, id_chan, id_team):
        """Permet la suppression d'un fichier a suivre"""
        if id_utilisateur in self.listeUser:
            if argument in self.listeUser[id_utilisateur]:
                self.listeUser[id_utilisateur].remove(argument)
                reponse = argument + " supprimé de la liste avec succès"
            else:
                reponse = "Le fichier spécifier n'existe pas dans votre liste de fichier a suivre."
        else:
            reponse = "Il n'y a pas de fichier a supprimer pour vous !"

        return await self.sendText(reponse, id_chan, id_team)

    async def help(self, id_chan, id_utilisateur, id_team):
        """Envoie le manuel utilisateur du bot"""
        return await self.sendText(self.helpmsg, id_chan, id_team)

    async def error(self, id_chan,id_utilisateur, id_team):
        """Envoie un message d'erreur lorsqu'une commande erroné est entrée"""
        error = "La commande que vous avez entré n'existe pas. Taper 'help' pour recevoir de l'aide !"
        return await self.sendText(error, id_chan, id_team)

    def fonction_pour_prouver_que_je_peux_faire_des_test(self):
        return 1


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.set_debug(DEBUG)
    bot = BotAlonso(TOKEN)
    loop.run_until_complete(bot.connect())
    loop.close()