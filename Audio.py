from enum import Enum
from dataclasses import dataclass
import pygame


class Sound(Enum):
    START = "start_sound"
    HIT = "hit_sound"
    BLOCK = "block_sound"
    WIN = "win_sound"
    POWERUP = "powerup_sound"


class Music(Enum):
    MENU = "menu.mp3"
    GAME_OVER = "game over.mp3"
    GAME_PLAY = "music.mp3"
    VICTORY = "win music.mp3"
    PRE_LAUNCH_UNIMPLEMENTED = "pre-launch.mp3"


@dataclass
class AudioInstructions:
    sound_queue: list[Sound]
    new_music: Music

    def merge(self, other: "AudioInstructions") -> "AudioInstructions":
        """If both have new music, the one in the caller is preserved"""
        new_queue = self.sound_queue + other.sound_queue
        if self.new_music == None:
            new_music = other.new_music
        else:
            new_music = self.new_music

        return AudioInstructions(new_queue, new_music)


class Audio:
    def __init__(self):
        start_sound = pygame.mixer.Sound("start effect.mp3")
        hit_sound = pygame.mixer.Sound("paddle hit.mp3")
        block_sound = pygame.mixer.Sound("block hit.mp3")
        win_sound = pygame.mixer.Sound("win sound.wav")
        powerup_sound = pygame.mixer.Sound("powerup sound.mp3")
        self.__to_sounds = {
            Sound.START: start_sound,
            Sound.HIT: hit_sound,
            Sound.BLOCK: block_sound,
            Sound.WIN: win_sound,
            Sound.POWERUP: powerup_sound,
        }
        self.__to_music = {
            Music.MENU: "menu.mp3",
            Music.GAME_OVER: "game over.mp3",
            Music.GAME_PLAY: "music.mp3",
            Music.VICTORY: "win music.mp3",
            Music.PRE_LAUNCH_UNIMPLEMENTED: "pre-launch.mp3",
        }
        self.__player = pygame.mixer.music
        self.__player.load(self.__to_music[Music.MENU])
        self.__player.play()

    def __change_music(self, music: str):
        self.__player.unload()
        self.__player.load(music)
        self.__player.play(-1)

    def run(self, instructions: AudioInstructions):
        for sound_repr in instructions.sound_queue:
            self.__to_sounds[sound_repr].play()

        if instructions.new_music != None:
            self.__change_music(self.__to_music[instructions.new_music])
