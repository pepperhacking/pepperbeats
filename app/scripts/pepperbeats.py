"""
A sample showing how to have a NAOqi service as a Python app.
"""

__version__ = "0.0.3"

__copyright__ = "Copyright 2015, Aldebaran Robotics"
__author__ = 'ekroeger'
__email__ = 'ekroeger@aldebaran.com'

import time

import qi

import stk.runner
import stk.events
import stk.services
import stk.logging

import bricks
import anims

TENTH_OF_SECOND = 100000
ONE_SECOND = 1000000

DBGOBJ = False
#DBGOBJ = True

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
        self.running = True
        self.brickengine = bricks.BrickEngine(self)
        self.animengine = anims.AnimEngine(self)

    @qi.bind(returnType=qi.Void, paramsType=[])
    def stop(self):
        "Stop the service."
        self.logger.info("ALPepperBeats stopped by user request.")
        self.qiapp.stop()

    @qi.nobind
    def on_start(self):
        "Cleanup (add yours if needed)"
        #self.s.ALTextToSpeech.say("blip")
        self.animengine.init()
        self.animengine.run_anim("WarmUp_2")
        self.ask_for_inspiration()
        if DBGOBJ:
            self.s.ALTextToSpeech.say(self.brickengine.description)
            self.ask_for_inspiration()
            self.s.ALTextToSpeech.say(self.brickengine.description)
            self.ask_for_inspiration()
            self.s.ALTextToSpeech.say(self.brickengine.description)
            self.s.ALTextToSpeech.say("Finished")
            self.stop()
            return
        self.record_multiple()
        self.start_loop()
        self.stop()

    RECORDHOME = "/home/nao/"

    def record_multiple(self):
        self.events.set("PepperBeats/Brick", "SILENCE")
        self.s.ALTextToSpeech.say("Now touch my head and gimme some sounds!")
        by_durations = []
        for i in range(4):
            print "start", self.events.wait_for("FrontTactilTouched")
            self.events.set("PepperBeats/Brick", "RECORDING")
            self.s.ALAudioPlayer.playFile("/usr/share/naoqi/wav/begin_reco.wav")
            start = time.time()
            try:
                filename = self.RECORDHOME + "yoursound_{}.ogg".format(i)
                self.s.ALAudioDevice.startMicrophonesRecording(filename)
                print "end", self.events.wait_for("FrontTactilTouched")
                duration = time.time() - start
                by_durations.append((duration, filename))
                self.events.set("PepperBeats/Brick", "SILENCE")
                self.s.ALAudioDevice.stopMicrophonesRecording()
            except RuntimeError as e:
                print "error recording:", e
            self.s.ALAudioPlayer.playFile("/usr/share/naoqi/wav/end_reco.wav")
            time.sleep(0.5)
            by_durations.sort()
            if i <= 2:
                if i == 2:
                    tosay = "and a last one?"
                else:
                    tosay = "okay, another one?"
                # Now check if we have something to add
                if by_durations:
                    if by_durations[0][0] > 0.5:
                        tosay += " shorter please?"
                    elif by_durations[-1][0] < 0.5:
                        tosay += " shorter please?"
                self.s.ALTextToSpeech.say(tosay)
        self.beatA = by_durations[0][0]
        self.beatB = by_durations[1][0]
        sounds = [filepath for (dur, filepath) in by_durations]
        print "sounds by_durations:", by_durations
        self.beatA, self.beatB = sounds[:2]
        self.brickengine.set_sounds(sounds[2:])
        self.s.ALTextToSpeech.say("This is about what i see. I know my perception is lame.  But when you dare trust me, you can be part of the game !")
        self.animengine.run_anim("WarmUp_1")
        
    def record_simple(self):
        self.events.set("PepperBeats/Brick", "SILENCE")
        self.s.ALTextToSpeech.say("Now touch my head and gimme some sound!")
        print "start", self.events.wait_for("FrontTactilTouched")
        self.events.set("PepperBeats/Brick", "RECORDING")
        self.s.ALAudioPlayer.playFile("/usr/share/naoqi/wav/begin_reco.wav")
        try:
            self.s.ALAudioDevice.startMicrophonesRecording(self.RECORDHOME + "yoursound.ogg")
            print "end", self.events.wait_for("FrontTactilTouched")
            self.events.set("PepperBeats/Brick", "SILENCE")
            self.s.ALAudioDevice.stopMicrophonesRecording()
        except RuntimeError as e:
            print "error recording:", e
        self.s.ALAudioPlayer.playFile("/usr/share/naoqi/wav/end_reco.wav")
        time.sleep(1)
        #self.s.ALTextToSpeech.say("And now!")
        #self.s.ALAudioPlayer.playFile(self.RECORDHOME + "yoursound.ogg")
        self.animengine.run_anim("WarmUp_1")

    def ask_for_inspiration(self):
        self.s.ALTextToSpeech.say("Give me some inspiration!")
        time.sleep(2)
        qi.async(self.s.ALTextToSpeech.say, "I see something!")
        self.brickengine.inspiration()
        

    SOUNDPATH = "/home/nao/.local/share/PackageManager/apps/{0}/sounds/{1}.ogg"
    package_id = "pepperbeats"

    def play_sound(self, sound_name):
        filepath = self.SOUNDPATH.format(self.package_id, sound_name)
        self.s.ALAudioPlayer.playFile(filepath)

    @stk.logging.log_exceptions
    def loop_update(self):
        self.beat += 1
        if self.beat % 2:
            print "bip_gentle"
            #qi.async(self.play_sound, "C")
            try:
                self.s.ALAudioPlayer.playFile(self.beatA)
            except Exception as e:
                self.s.ALAudioPlayer.playFile(self.beatB)
            #qi.async(self.s.ALAudioPlayer.playFile, self.beatA)
            #self.s.ALAudioPlayer.playFile("/usr/share/naoqi/wav/bip_gentle.wav")
        else:
            #self.s.ALTextToSpeech.say("tcha")
            #qi.async(self.play_sound, "D")
            self.s.ALAudioPlayer.playFile(self.beatB)
            #qi.async(self.s.ALAudioPlayer.playFile, self.beatB)
            #self.play_sound("D")
            #self.s.ALAudioPlayer.playFile("/usr/share/naoqi/wav/begin_reco.wav")
        self.brickengine.update()
        if self.brickengine.allow_anim:
            self.animengine.update(self.beat)

    def start_loop(self):
        self.beat = 0
        self.loop = qi.PeriodicTask()
        self.loop.setCallback(self.loop_update)
        self.loop.setUsPeriod(5 * TENTH_OF_SECOND)
        self.loop.start(True)
        #print dir(self.loop)
        time.sleep(40)
        print "Finished"

    @qi.nobind
    def on_stop(self):
        "Cleanup (add yours if needed)"
        self.events.clear()
        if self.loop:
            self.loop.stop()
        self.brickengine.stop()
        self.s.ALAudioPlayer.stopAll()
        self.logger.info("ALPepperBeats finished.")

####################
# Setup and Run
####################

if __name__ == "__main__":
    stk.runner.run_service(ALPepperBeats)
