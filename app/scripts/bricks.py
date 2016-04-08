# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 22:05:41 2016

@author: ekroeger
"""

import random

import qi

import stk.logging

BRICKTYPES = [
    "SING",
    "POEM",
]

class BrickEngine(object):
    def __init__(self, context):
        self.s = context.s
        self.logger = context.logger
        self.events = context.events
        self.brick = None
    
    def update(self):
        if not self.brick:
            self.brick = self.get_brick()

    def get_brick(self):
        bricktype = random.choice(BRICKTYPES)
        self.events.set("PepperBrats/Brick", bricktype)
        return getattr(self, "get_" + bricktype)()

    def get_POEM(self):
        phrase = random.choice([
            "J'ai vu des ordinateurs",
            "J'ai vu des geeks",
            "J'ai vu des filles",
            "Je suis le robot du futur les gars",
            ])
        return qi.async(self.say, phrase)

    def get_SING(self):
        phrase = random.choice([
            "Shabadabada",
            "Yo",
            "Blip",
            ])
        return qi.async(self.say, phrase)

    @stk.logging.log_exceptions
    def say(self, phrase):
        self.s.ALTextToSpeech.say(phrase)
        self.brick = None
