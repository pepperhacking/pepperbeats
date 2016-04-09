# -*- coding: utf-8 -*-
"""
Created on Sat Apr  9 14:00:25 2016

@author: ekroeger
"""

import random
import time

import qi

import stk.logging

class AnimEngine(object):
    def __init__(self, context):
        self.s = context.s
        self.logger = context.logger
        self.events = context.events
        self.left = None
        self.right = None
        self.head = None
        self.description = None
        self.queue = []

    @stk.logging.log_exceptions
    def run_anim(self, name):
        #self.s.ALBehaviorManager.runBehavior("haklux/" + name)
        self.s.ALAnimationPlayer.run("haklux/" + name)

    def update(self, beat):
        if (beat % 4) == 2:
            if (beat % 16 == 2):
                self.left   = qi.async(self.run_anim, "Arm_L")
            elif (beat % 16 == 10):
                self.left   = qi.async(self.run_anim, "Arm_R")
            else:
                self.left   = qi.async(self.run_anim, "Arm_L")
                self.right  = qi.async(self.run_anim, "Arm_R")
        elif (beat % 4) == 0:
            self.head   = qi.async(self.run_anim, "Head")
        #print "TODO ANIM", beat
