# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 22:05:41 2016

@author: ekroeger
"""

import random

import qi

import stk.logging

BRICKTYPES = [
    #"SING",
    #"POEM",
    "GIMMEWORD",
]

class BrickEngine(object):
    def __init__(self, context):
        self.s = context.s
        self.logger = context.logger
        self.events = context.events
        self.brick = None
        self.word = None
    
    def update(self):
        if not self.brick:
            self.brick = self.get_brick()

    def get_brick(self):
        if self.word:
            bricktype = random.choice(["POEM", "SING"])
        else:
            bricktype = random.choice(["GIMMEWORD", "SING"])
        #bricktype = random.choice(BRICKTYPES)
        self.events.set("PepperBeats/Brick", bricktype)
        return getattr(self, "get_" + bricktype)()

    def get_POEM(self):
        phrase = random.choice([
            "On m'a parlé de %s",
            "J'ai revé de %s",
            ]) % self.word
        self.word = None
        return qi.async(self.say, phrase)

    def get_SING(self):
        phrase = random.choice([
            "Shabadabada",
            "Yo",
            "Blip",
            ])
        return qi.async(self.say, phrase)
        
    def get_GIMMEWORD(self):
        phrase = "Give me a word!"
        return qi.async(self.ask_for_word, phrase)

    def stop(self):
        if self.brick:
            #print "dir", dir(self.brick)
            self.brick.stop()

    @stk.logging.log_exceptions
    def ask_for_word(self, phrase):
        self.s.ALTextToSpeech.say(phrase)
        asr = self.s.ALSpeechRecognition
        for subscriber, a, b in asr.getSubscribersInfo():
            asr.unsubscribe(subscriber)
        asr.setVisualExpression(True)
        asr.pushContexts()
        if asr._isFreeSpeechToTextAvailable():
            print "Free Speech!"
            asr._enableFreeSpeechToText()
        else:
            print "No free speech, sorry :("
            words = "computer bottle girl keyboard screen guy programmer".split()
            asr.setVocabulary(words, False)
        asr.subscribe("PepperBeats")
        self.word, conf = self.events.wait_for("WordRecognized")
        asr.unsubscribe("PepperBeats")
        print "Got", self.word, conf
        if True:
            self.brick = None

    @stk.logging.log_exceptions
    def say(self, phrase):
        self.s.ALTextToSpeech.say(phrase)
        self.brick = None
