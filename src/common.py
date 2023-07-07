from typing import Tuple
import random
from enum import Enum
from dataclasses import dataclass

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


@dataclass
class GraphicsSettings:
    resolution_width: int
    resolution_height: int


@dataclass
class Settings:
    fps: int
    graphics_settings: GraphicsSettings


class Constants:
    default_graphics_settings = GraphicsSettings(800, 600)
    default_settings = Settings(60, default_graphics_settings)

    game_width = 800
    game_height = 600
    gravity = 0.0004
    air_resistance_coefficient = 0.01
    user_impulse_per_millisecond = 0.01
    update_repetitions = 50
    init_y_vel_ball = -0.8
    init_max_x_vel_ball = 0.4
    max_x_vel_ball = 0.8
    ball_radius = 5
    initial_lives = 3
    life_width = 5

    powerup_probability = 0.4
    powerup_type_probabilities = [0.8, 0.2]
    assert round(sum(powerup_type_probabilities), 3) == 1.0
    powerup_fall_speed = 0.4


@dataclass
class Paddle:
    x: float
    y: float
    width: float
    height: float
    x_vel: float
    lives: float


class BallModifier(Enum):
    PIERCING = "piercing"


@dataclass
class Ball:
    x: float
    y: float
    x_vel: float
    y_vel: float
    radius: float
    has_fallen: bool = False
    modifier: None | BallModifier = None  # This will later probably be a list
    modifier_active_for: float = 0  # This will later probably be a list
    max_blocks_can_pierce: int = 0
    blocks_pierced: int = 0

    def make_piercing(self, milliseconds, count):
        self.modifier = BallModifier.PIERCING
        self.modifier_active_for = milliseconds
        self.max_blocks_can_pierce = count
        self.blocks_pierced = 0


class BlockType(Enum):
    NORMAL = "normal"
    POWERUP = "powerup"
    PROTECTOR = "protector"

    @classmethod
    def normal_or_powerup(cls, probability_powerup):
        return (
            BlockType.POWERUP
            if random.random() < probability_powerup
            else BlockType.NORMAL
        )


@dataclass
class Block:
    x: float
    y: float
    width: float
    height: float
    block_id: Tuple[int, int]
    block_type: BlockType
    health: int
    protection: int

    color: Color


class PowerupType(Enum):
    PIERCING = "piercing"
    LIFE = "life"


@dataclass
class Powerup:
    powerup_type: PowerupType
    x: float
    y: float
    hitbox_radius: float


GameObject = Block | Paddle | Powerup | Ball
