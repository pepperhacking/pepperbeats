# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 22:05:41 2016

@author: ekroeger
"""

import random
import time
import urllib2
import json
import re

import qi

import stk.logging

I_SEE_SOME_X_re= re.compile("i see some (.*?) and")


VERSES1 = [
    "maybe, maybe,",
    "I see a WORD0",
    "Maybe a WORD1",
    "And also a WORD2",
]

VERSES2 = [
    "If you show me WORD0",
    "Maybe you like WORD0",
    "If you like WORD0",
    "WORD0 is my inspiration",
]

VERSES = [VERSES1, VERSES2]

class BrickEngine(object):
    def __init__(self, context):
        self.s = context.s
        self.logger = context.logger
        self.events = context.events
        self.brick = None
        self.word = None
        self.description = None
        self.queue = []
        self.verses = []
        self.allow_anim = True

    def update(self):
        if not self.brick:
            self.brick = self.get_brick()

    def brick_done(self, fut):
        print "brick done", self.bricktype
        self.brick = None
        
    def fill_queue(self):
        self.queue = [
            #"MUSIC", "INSPIRATION", 
            #"MUSIC",
            "POEM",
            "BEAT",
            "POEM",
            "YOURSOUND", 
            "POEM",
            "SING", 
            "POEM",
            "YOURSOUND",  
            "YOURSOUND",
            #"MUSIC",
        ]

    def get_brick(self):
        """"
        if self.word or self.description:
            self.bricktype = random.choice([
                "POEM", "POEM", "SING", "MUSIC", "YOURSOUND",
                ])
            #self.bricktype = "YOURSOUND"
        else:
            #self.bricktype = random.choice(["GIMMEWORD", "SING", "MUSIC", "SILENCE"])
            self.bricktype = random.choice([
                "INSPIRATION", "INSPIRATION", "SING", "MUSIC", "BEAT",
                "YOURSOUND",
                ])
        #bricktype = random.choice(BRICKTYPES)
        """
        if not self.queue:
            self.fill_queue()
        self.bricktype = self.queue.pop(0)
        print "doing", self.bricktype
        self.events.set("PepperBeats/Brick", self.bricktype)
        return getattr(self, "get_" + self.bricktype)().then(self.brick_done)

    def get_verses(self):
        self.verses = list(random.choice(VERSES))
        #print "FILLED VERSES:"
        #print "\n".join(self.verses)

    def get_POEM(self):
        #if self.word:
        #    image_url = get_pixabay(self.word)
        #    self.events.set("PepperBeats/ImageUrl", image_url)
        #if self.description:
        #    phrase = self.description
        #    self.description = None
        #else:
        #    phrase = random.choice([
        #        "I heard about %s",
        #        "There was word of %s",
        #        "The word of the street is %s",
        #        "I dreamt of %s",
        #        ]) % self.word
        #    if random.random() < 0.5:
        #        self.word = None
        if not self.verses:
            self.get_verses()
        phrase = self.verses.pop(0)
        for i, word in enumerate(self.words):
            keyword = "WORD" + str(i)
            if keyword in phrase:
                image_url = get_pixabay(word)
                phrase = phrase.replace(keyword, word)
                self.events.set("PepperBeats/ImageUrl", image_url)
        print "Saying", phrase
        return qi.async(self.say, phrase)

    #def get_PICTURE(self):
    #    image_url = get_pixabay(self.word)
    #    if random.random() < 0.5:
    #        self.word = None
    #    self.events.set("PepperBeats/ImageUrl", image_url)
    #    qi.async(time.sleep, 2)

    def get_INSPIRATION(self):
        return qi.async(self.inspiration)

    @stk.logging.log_exceptions
    def inspiration(self):
        if self.s.ALBehaviorManager.isBehaviorInstalled("picturedesc/."):
            self.s.ALBehaviorManager.runBehavior("picturedesc/.")
            self.description = self.events.get("PepperBeats/PictureDesc")
        else:
            self.description = "I see some people and some computers and maybe some design"
        self.words = get_words(self.description)
        #lower = self.description.lower()
        #match = I_SEE_SOME_X_re.match(lower)
        #if match:
        #    self.word = match.group(1)
        print "finished inspiration or something, todo", self.description

    def get_SING(self):
        if False: # Hard coded
            phrase = random.choice([
                "Shabadabada",
                "Yo",
                "jhfjvryjdtrcfgyjbujkybdfvgjkoljkdghfdr",
                "qseifhbqsdklnh",
                "dfgjkloiuytghjk",
                ])
            #phrase = "pep pep pepper sdjkfhsdkljhgjklmjhcfgbhjn,kl dfhjsdklfjsdbjfsdnilfgn fodkfosdkfostjirtri dzoup dzoup Peppar is in da house"
            return qi.async(self.say, phrase)
        else:
            return qi.async(self.s.ALBehaviorManager.runBehavior, "randomstring/behavior_long")
        
    def get_BEAT(self):
        return qi.async(time.sleep, 1.9)
        
    def get_MUSIC(self):
        sound = random.choice(["A", "B"])
        return qi.async(self.play_sound, sound)
    
    def set_sounds(self, sounds):
        self.yoursounds = sounds
        self.toplay = []

    def get_YOURSOUND(self):
        if True:
            print "swirl?"
            return qi.async(self.run_danse_twirling)
        if not self.toplay:
            self.toplay = list(self.yoursounds)
        #sfilepath = "/home/nao/yoursound.ogg"
        return qi.async(self.s.ALAudioPlayer.playFile, self.toplay.pop(0))

    @stk.logging.log_exceptions
    def run_danse_twirling(self):
        #qi.async(self.s.ALAudioPlayer.playFile, self.yoursounds[-1])
        #self.s.ALBehaviorManager.runBehavior("haxlux/Turn")
        longest_sound = self.yoursounds[-1]
        print "dancing", longest_sound
        try:
            time.sleep(0.5)
            self.allow_anim = False
            self.s.ALAudioPlayer.stopAll()
            self.s.ALAudioPlayer.playFile(longest_sound)
            qi.async(self.s.ALBehaviorManager.runBehavior, "haklux/Turn")
        except Exception as e:
            print "Weird twirling error:", e
            self.s.ALBehaviorManager.runBehavior("haklux/Turn")
        time.sleep(1.0)
        self.allow_anim = True
        print "danced"

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

    @stk.logging.log_exceptions
    def say(self, phrase):
        self.s.ALTextToSpeech.say(phrase)

def get_pixabay(keyword):
    url="https://pixabay.com/api/?key=2007282-2872cc698022c3e8b724e53a6&q=%s&image_type=photo" \
        % keyword
    try:
        request = urllib2.Request(url, None, {'Referer': 'testing'})
        response = urllib2.urlopen(request)
        results = json.load(response)
        hits = results["hits"]
        if hits:
            return hits[0]["webformatURL"]
        else:
            return None
    except Exception as e:
        print "Got pixabay error:", e
        return None

def get_gyphy(keyword):
    url="http://api.giphy.com/v1/gifs/search?q=%s&limit=1&api_key=dc6zaTOxFJmzC" % keyword
    request = urllib2.Request(url, None, {'Referer': 'testing'})
    response = urllib2.urlopen(request)
    results = json.load(response)
    result = random.choice(results["data"])
    return result["images"]["original"]["url"]


def test_image():
    search_term = "guitar"
    print get_pixabay(search_term)

I_SEE_SOME_X_123_re= re.compile("i see some (.*?) and some (.*?) and maybe some (.*)")

def get_words(phrase):
    lower = phrase.lower()
    m = I_SEE_SOME_X_123_re.match(lower)
    if m:
        return m.groups()
    else:
        m = I_SEE_SOME_X_re.match(lower)
        return m.groups()

def test_grep():
    description = "I see some people and some computers and maybe some design"
    lower = description.lower()
    m = I_SEE_SOME_X_re.match(lower)
    print m.group(1)
    
def test_grep2():
    description = "I see some people and some computers and maybe some design"
    lower = description.lower()
    m = I_SEE_SOME_X_123_re.match(lower)
    print m.groups()
    
def test_grep3():
    description = "I see some people and some computers and maybe some design"
    print get_words(description)
    
if __name__ == "__main__":
    #test_image()
    test_grep3()
