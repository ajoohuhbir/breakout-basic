from dataclasses import dataclass
import pygame
import copy
from typing import Tuple

from Inputs import KeyboardState


@dataclass
class GraphicsSettings:
    resolution_width: int
    resolution_height: int


@dataclass
class Settings:
    fps: int
    graphics_settings: GraphicsSettings


@dataclass
class SettingsSelector:
    x: float
    y: float
    width: int


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


class SettingsState:
    possible_settings = ["Resolution", "FPS"]
    possible_resolutions = [(800, 600), (1080, 720), (400, 300)]

    def __init__(self, settings: Settings):
        self.changed = False
        self.selector_at = 1
        self.selector = SettingsSelector(
            Constants.game_width / 2, 0.4 * Constants.game_height, 400
        )
        self.temp_fps = settings.fps
        self.temp_resolution = SettingsState.possible_resolutions.index(
            (
                settings.graphics_settings.resolution_width,
                settings.graphics_settings.resolution_height,
            )
        )
        self.settings = settings

    def update(
        self, keyboard_state: KeyboardState
    ) -> Tuple[Settings, list[SettingsSelector]]:
        keys = keyboard_state.new_keys_pressed

        new_settings = copy.deepcopy(self.settings)
        if pygame.K_s in keys and not self.changed:
            self.selector_at += 1
            self.selector_at %= len(SettingsState.possible_settings)
        elif pygame.K_w in keys and not self.changed:
            self.selector_at -= 1
            self.selector_at %= len(SettingsState.possible_settings)
        elif pygame.K_d in keys:
            if self.selector_at == 0:
                self.temp_resolution += 1
                self.temp_resolution %= len(SettingsState.possible_resolutions)
                self.changed = True
            elif self.selector_at == 1:
                self.temp_fps += 1
                self.changed = True
        elif pygame.K_a in keys:
            if self.selector_at == 0:
                self.temp_resolution -= 1
                self.temp_resolution %= len(SettingsState.possible_resolutions)
                self.changed = True
            elif self.selector_at == 1:
                self.temp_fps -= 1
                self.changed = True
        elif pygame.K_RETURN in keys:
            new_settings.fps = self.temp_fps
            (
                new_settings.graphics_settings.resolution_width,
                new_settings.graphics_settings.resolution_height,
            ) = SettingsState.possible_resolutions[self.temp_resolution]
            self.changed = False

        if self.selector_at == 0:
            self.selector.y = 0.4 * Constants.game_height
        elif self.selector_at == 1:
            self.selector.y = 0.7 * Constants.game_height

        if new_settings == self.settings:
            new_settings = None
        else:
            self.settings = copy.deepcopy(new_settings)

        return new_settings, [self.selector]
