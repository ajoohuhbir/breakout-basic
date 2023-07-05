from typing import Tuple
import random
from enum import Enum

Color = Tuple[float, float, float]


class Colors:
    white = (255, 255, 255)
    black = (0, 0, 0)
    dark_gray = (10, 10, 10)
    red = (255, 0, 0)

    @staticmethod
    def generate_random_block_color() -> Color:
        color = tuple([random.randint(0, 255) for i in range(3)])
        return (
            color if Colors.is_bright(color) else Colors.generate_random_block_color()
        )

    @staticmethod
    def is_bright(color: Color, brightness: int = 20) -> bool:
        return not [i < brightness for i in color] == [True, True, True]

    @staticmethod
    def negative(color: Color) -> Color:
        return tuple([255 - i for i in color])


class GameFsmState(Enum):
    MENU = "menu"
    PLAY = "play"
    PAUSE = "pause"
    GAME_WIN = "game win"
    GAME_OVER = "game over"
    QUIT = "quit"
    INSTRUCTIONS = "instructions"
    SETTINGS = "settings"
    PRE_PLAY = "pre play"
