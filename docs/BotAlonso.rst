BotAlonso package
=================

Submodules
----------

BotAlonso.api
-------------

Cette partie décrit la fonctionnalité du module api de notre bot.

Ce module ne contient qu une seul méthode

.. py:function:: api_call(method, data=None, token=TOKEN):
cette méthode permet la communication avec slack

BotAlonso.config
----------------

Ce module contient deux variables.
La variable TOKEN qui est le token pour se connecter a Slack.
Et une variable DEBUG.

BotAlonso.MainAlonso
--------------------

Cette partie décrit la fonctionnalité du module MainAlonso de notre bot.

Ce module contient une classe EventHandler qui permet de créer et de traiter un event provoquer par une modification d'un fichier.

Ce module contient une seconde classe BotAlonso. Cette classe est la classe principal de notre programme.
Elle possede 8 fonctions:

.. py:function:: __init__(self, token=TOKEN):$
Initialise le bot

.. py:function:: sendText(self, reponse, id_chan, id_team):
Envoie la reponse du bot

.. py:function:: add(self, argument, id_utilisateur, id_chan, id_team):
Ajoute un fichier a la liste des fichiers à controler de l'utilisateur

.. py:function:: check(self, id_chan, id_utilisateur, id_team):
Controle la modification du fichier

.. py:function:: remove(self, argument, id_utilisateur, id_chan, id_team):
Permet la suppression d'un fichier a suivre

.. py:function:: help(self, id_chan, id_utilisateur, id_team):
Envoie le manuel utilisateur du bot

.. py:function:: error(self, id_chan,id_utilisateur, id_team):
Envoie un message d'erreur lorsqu'une commande erroné est entrée

.. py:function:: execute(self, message):
Lis et execute la commande passé dans le message

.. py:function:: connect(self):
Fonction de connection de notre bot a slack
