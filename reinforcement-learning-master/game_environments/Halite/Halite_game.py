import numpy as np
import datetime
import os
import sys
import random
import json


class HaliteGame:
    # initialize the class
    def __int__(self, player_id, replay_id):
        self.replay_id = replay_id
        self.frame = 0

    # Todo: step function return s, s1, a, r, t, score,
    def step(self):
        self.frame += 1
        return

    # Todo: reset the env when a game ends
    def reset(self):
        return

