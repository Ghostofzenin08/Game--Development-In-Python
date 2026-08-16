"""Procedural game sounds; no external files are required."""

import math
from array import array
import pygame


class SoundEffects:
    def __init__(self):
        self._sounds = {name: self._tone(freq, duration) for name, freq, duration in (
            ("hit", 620, .07), ("wall", 300, .05), ("score", 180, .18), ("power", 900, .12)
        )}

    @staticmethod
    def _tone(frequency, duration):
        if not pygame.mixer.get_init():
            return None
        rate = 22050
        data = array("h", (int(9000 * math.sin(2 * math.pi * frequency * i / rate)) for i in range(int(rate * duration))))
        return pygame.mixer.Sound(buffer=data)

    def play(self, name):
        if sound := self._sounds.get(name):
            sound.play()
