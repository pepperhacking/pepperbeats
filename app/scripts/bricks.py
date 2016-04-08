# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 22:05:41 2016

@author: ekroeger
"""

import random
import time

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

    def brick_done(self, fut):
        print "brick done", self.bricktype
        self.brick = None

    def get_brick(self):
        if self.word:
            self.bricktype = random.choice(["POEM", "SING", "MUSIC", "SILENCE"])
        else:
            self.bricktype = random.choice(["GIMMEWORD", "SING", "MUSIC"])
        #bricktype = random.choice(BRICKTYPES)
        print "doing", self.bricktype
        self.events.set("PepperBeats/Brick", self.bricktype)
        return getattr(self, "get_" + self.bricktype)().then(self.brick_done)

    def get_POEM(self):
        phrase = random.choice([
            "I heard about %s",
            "There was word of %s",
            "The word of the street is %s",
            "I dreamt of %s",
            ]) % self.word
        self.word = None
        return qi.async(self.say, phrase)

    def get_SING(self):
        phrase = random.choice([
            "Shabadabada",
            "Yo",
            "jhfjvryjdtrcfgyjbujkybdfvgjkoljkdghfdr",
            "qseifhbqsdklnh",
            "dfgjkloiuytghjk",
            ])
        return qi.async(self.say, phrase)
        
    def get_SILENCE(self):
        print 'silence'
        return qi.async(time.sleep, 2)
        
    def get_MUSIC(self):
        sound = random.choice(["A", "B"])
        return qi.async(self.play_sound, sound)

    SOUNDPATH = "/home/nao/.local/share/PackageManager/apps/{0}/sounds/{1}.ogg"
    package_id = "pepperbeats"
    def play_sound(self, sound_name):
        filepath = self.SOUNDPATH.format(self.package_id, sound_name)
        self.s.ALAudioPlayer.playFile(filepath)

        
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
