"""
A sample showing how to have a NAOqi service as a Python app.
"""

__version__ = "0.0.3"

__copyright__ = "Copyright 2015, Aldebaran Robotics"
__author__ = 'ekroeger'
__email__ = 'ekroeger@aldebaran.com'

import time
import random

import qi

import stk.runner
import stk.events
import stk.services
import stk.logging

import bricks

TENTH_OF_SECOND = 100000
ONE_SECOND = 1000000

class ALPepperBeats(object):
    "NAOqi service example (set/get on a simple value)."
    APP_ID = "com.aldebaran.ALPepperBeats"
    def __init__(self, qiapp):
        # generic activity boilerplate
        self.qiapp = qiapp
        self.events = stk.events.EventHelper(qiapp.session)
        self.s = stk.services.ServiceCache(qiapp.session)
        self.logger = stk.logging.get_logger(qiapp.session, self.APP_ID)
        # Internal variables
        self.level = 0
        self.running = True
        self.brickengine = bricks.BrickEngine(self)
        
    @qi.bind(returnType=qi.Void, paramsType=[qi.Int8])
    def set(self, level):
        "Set level"
        self.level = level

    @qi.bind(returnType=qi.Int8, paramsType=[])
    def get(self):
        "Get level"
        return self.level

    @qi.bind(returnType=qi.Void, paramsType=[])
    def reset(self):
        "Reset level to default value"
        return self.set(0)

    @qi.bind(returnType=qi.Void, paramsType=[])
    def stop(self):
        "Stop the service."
        self.logger.info("ALPepperBeats stopped by user request.")
        self.qiapp.stop()

    @qi.nobind
    def on_start(self):
        "Cleanup (add yours if needed)"
        #self.s.ALTextToSpeech.say("blip")
        self.start_loop()

    @stk.logging.log_exceptions
    def loop_update(self):
        self.beat += 1
        if self.beat % 2:
            print "bip_gentle"
            self.s.ALAudioPlayer.playFile("/usr/share/naoqi/wav/bip_gentle.wav")
        else:
            #self.s.ALTextToSpeech.say("tcha")
            self.s.ALAudioPlayer.playFile("/usr/share/naoqi/wav/begin_reco.wav")
        self.brickengine.update()

    def start_loop(self):
        self.beat = 0
        self.loop = qi.PeriodicTask()
        self.loop.setCallback(self.loop_update)
        self.loop.setUsPeriod(5 * TENTH_OF_SECOND)
        self.loop.start(True)
        print dir(self.loop)
        time.sleep(10)
        self.stop()

    @qi.nobind
    def on_stop(self):
        "Cleanup (add yours if needed)"
        if self.loop:
            self.loop.stop()
        self.logger.info("ALPepperBeats finished.")

####################
# Setup and Run
####################

if __name__ == "__main__":
    stk.runner.run_service(ALPepperBeats)

