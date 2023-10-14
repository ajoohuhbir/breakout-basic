from dataclasses import dataclass
import pygame
import copy
import math
from typing import Tuple

from settings import SettingsSelector
from common import (
    Color,
    Colors,
    Constants,
    GameObject,
    Paddle,
    Ball,
    Block,
    Powerup,
    BlockType,
    PowerupType,
    GraphicsSettings,
)


@dataclass
class Message:
    text: str
    size: int
    x: float
    y: float
    font: str = "arial"
    color: Color = (255, 255, 255)


UIElement = SettingsSelector | Message


@dataclass
class GraphicsInstructions:
    objects: list[GameObject]
    ui_elements: list[UIElement]
    graphics_settings_change: None | GraphicsSettings = None

    def __add__(self, other: "GraphicsInstructions"):
        """If both have new settings, the ones in the caller are preserved"""
        new_settings = (
            self.graphics_settings_change
            if self.graphics_settings_change != None
            else other.graphics_settings_change
        )
        return GraphicsInstructions(
            self.objects + other.objects,
            self.ui_elements + other.ui_elements,
            new_settings,
        )


class Graphics: 
    def __init__(self, graphics_settings: GraphicsSettings):
        self.__screen = pygame.display.set_mode(
            (graphics_settings.resolution_width, graphics_settings.resolution_height)
        )
        self.resolution = (
            graphics_settings.resolution_width,
            graphics_settings.resolution_height,
        )
        self.__paddle_color = Colors.white
        self.__ball_color = Colors.white
        self.graphics_settings = copy.deepcopy(graphics_settings)
        self.__set_game_screen()

    def render(self, instructions: GraphicsInstructions):
        if instructions.graphics_settings_change != None:
            self.graphics_settings = copy.deepcopy(
                instructions.graphics_settings_change
            )
            self.__reset_resolution()

        self.__screen.fill(Colors.black)

        pygame.draw.rect(
            self.__screen,
            Colors.dark_gray,
            [
                self.game_screen_origin_x,
                self.game_screen_origin_y,
                self.game_screen_width,
                self.game_screen_height,
            ],
        )

        for obj in instructions.objects:
            self.__render_object(obj)

        for ui_element in instructions.ui_elements:
            self.__render_ui_element(ui_element)

        pygame.display.update()

    def __reset_resolution(self):
        self.__screen = pygame.display.set_mode(
            (
                self.graphics_settings.resolution_width,
                self.graphics_settings.resolution_height,
            )
        )
        self.resolution = (
            self.graphics_settings.resolution_width,
            self.graphics_settings.resolution_height,
        )
        self.__set_game_screen()

    def __render_paddle(self, paddle: Paddle):
        self.__res_draw_rect(
            paddle.x, paddle.y, paddle.width, paddle.height, self.__paddle_color
        )
        self.__render_lives(paddle)

    def __render_lives(self, paddle: Paddle):
        num = paddle.lives
        life_width = Constants.life_width

        if num == 1:
            mids = [0.5]
        elif num % 2 == 1:
            each_side = int((num - 1) / 2)
            mids = [
                0.5 + (0.25 / each_side) * i
                for i in range(-1 * each_side, each_side + 1)
            ]
        else:
            mids = [0.5 + i * (0.25 / num) for i in range(-(num - 1), (num - 1) + 1, 2)]

        actual_mids = [paddle.x + paddle.width * i for i in mids]

        for mid in actual_mids:
            self.__res_draw_rect(
                mid - life_width / 2, paddle.y, life_width, paddle.height, Colors.red
            )

    def __render_block(self, block: Block):
        self.__res_draw_rect(block.x, block.y, block.width, block.height, block.color)
        if block.block_type == BlockType.POWERUP:
            self.__res_draw_circle(
                block.x + block.width / 2,
                block.y + block.height / 2,
                block.height / 2,
                Colors.negative(block.color),
            )
        elif block.block_type == BlockType.PROTECTOR:
            self.__res_draw_rect(
                block.x, block.y, block.width, block.height, Colors.white
            )
        if block.health > 1:
            self.__res_draw_rect(
                block.x,
                block.y,
                block.width,
                block.height,
                Colors.red,
                int((block.health - 1) * block.height / 10),
            )

        if block.protection > 0:
            self.__res_draw_rect(
                block.x,
                block.y,
                block.width,
                block.height,
                Colors.white,
                int(block.height / 5),
            )

    def __render_ball(self, ball: Ball):
        self.__res_draw_circle(
            ball.x,
            ball.y,
            ball.radius,
            self.__ball_color if ball.modifier == None else Colors.red,
        )

    def __render_powerup(self, powerup: Powerup):
        if powerup.powerup_type == PowerupType.PIERCING:
            self.__render_piercing_powerup(powerup)
        elif powerup.powerup_type == PowerupType.LIFE:
            self.__render_life_powerup(powerup)

    def __render_piercing_powerup(self, powerup: Powerup):
        self.__res_draw_circle(
            powerup.x,
            powerup.y,
            powerup.hitbox_radius,
            Colors.red,
            powerup.hitbox_radius / 4,
        )
        self.__res_draw_circle(
            powerup.x,
            powerup.y,
            powerup.hitbox_radius / 4,
            Colors.red,
        )

    def __render_life_powerup(self, powerup: Powerup):
        get_circle_point = lambda theta_deg: (
            powerup.x + powerup.hitbox_radius / 2 * math.cos(math.radians(theta_deg)),
            powerup.y - powerup.hitbox_radius / 2 * math.sin(math.radians(theta_deg)),
        )

        heart_points = [
            get_circle_point(45),
            get_circle_point(0),
            get_circle_point(270),
            get_circle_point(180),
            get_circle_point(135),
            (powerup.x, powerup.y),
        ]

        self.__res_draw_circle(
            powerup.x,
            powerup.y,
            powerup.hitbox_radius,
            Colors.red,
            powerup.hitbox_radius / 4,
        )

        self.__res_draw_polygon(heart_points, Colors.red)

    def __render_object(self, obj: GameObject):
        if type(obj) == Block:
            self.__render_block(obj)
        elif type(obj) == Ball:
            self.__render_ball(obj)
        elif type(obj) == Paddle:
            self.__render_paddle(obj)
        elif type(obj) == Powerup:
            self.__render_powerup(obj)

    def __render_message(self, msg: Message):
        surf = pygame.font.SysFont(msg.font, round(self.scaling * msg.size)).render(
            msg.text, True, msg.color
        )
        trect = surf.get_rect()
        trect.center = self.__game_x_to_resolution_x(
            msg.x
        ), self.__game_y_to_resolution_y(msg.y)
        self.__screen.blit(surf, trect)

    def __render_settings_selector(self, selector: SettingsSelector):
        triangle_base = 50
        triangle_height = 50

        first_triangle_tip = (selector.x - selector.width / 2, selector.y)
        first_triangle_foot_perp = (
            first_triangle_tip[0] - triangle_height,
            first_triangle_tip[1],
        )
        second_triangle_tip = (selector.x + selector.width / 2, selector.y)
        second_triangle_foot_perp = (
            second_triangle_tip[0] + triangle_height,
            second_triangle_tip[1],
        )

        first_triangle_point_a = (
            first_triangle_foot_perp[0],
            first_triangle_foot_perp[1] - triangle_base / 2,
        )
        first_triangle_point_b = (
            first_triangle_foot_perp[0],
            first_triangle_foot_perp[1] + triangle_base / 2,
        )

        second_triangle_point_a = (
            second_triangle_foot_perp[0],
            second_triangle_foot_perp[1] - triangle_base / 2,
        )
        second_triangle_point_b = (
            second_triangle_foot_perp[0],
            second_triangle_foot_perp[1] + triangle_base / 2,
        )

        first_triangle = [
            first_triangle_tip,
            first_triangle_point_a,
            first_triangle_point_b,
        ]
        second_triangle = [
            second_triangle_tip,
            second_triangle_point_a,
            second_triangle_point_b,
        ]

        self.__res_draw_polygon(first_triangle, Colors.white)
        self.__res_draw_polygon(second_triangle, Colors.white)

    def __render_ui_element(self, ui_element: UIElement):
        if type(ui_element) == Message:
            self.__render_message(ui_element)
        elif type(ui_element) == SettingsSelector:
            self.__render_settings_selector(ui_element)

    def __set_game_screen(self):
        ratio = Constants.game_width / Constants.game_height
        res_ratio = (
            self.graphics_settings.resolution_width
            / self.graphics_settings.resolution_height
        )
        if res_ratio < ratio:
            self.game_screen_width = self.graphics_settings.resolution_width
            self.game_screen_height = self.game_screen_width / ratio
            self.black_bars = "horizontal"
            self.scaling = self.game_screen_width / Constants.game_width
        elif res_ratio > ratio:
            self.game_screen_height = self.graphics_settings.resolution_height
            self.game_screen_width = self.game_screen_height * ratio
            self.black_bars = "vertical"
            self.scaling = self.game_screen_height / Constants.game_height
        else:
            self.game_screen_height = self.graphics_settings.resolution_height
            self.game_screen_width = self.graphics_settings.resolution_width
            self.black_bars = "none"
            self.scaling = self.game_screen_height / Constants.game_height

        if self.black_bars == "none":
            self.game_screen_origin_x = 0
            self.game_screen_origin_y = 0
        elif self.black_bars == "horizontal":
            self.game_screen_origin_x = 0
            self.game_screen_origin_y = (
                self.graphics_settings.resolution_height / 2
            ) - (self.game_screen_height / 2)
        elif self.black_bars == "vertical":
            self.game_screen_origin_y = 0
            self.game_screen_origin_x = (
                self.graphics_settings.resolution_width / 2
            ) - (self.game_screen_width / 2)

    def __game_x_to_resolution_x(self, x: float) -> float:
        return x * self.scaling + self.game_screen_origin_x

    def __game_y_to_resolution_y(self, y: float) -> float:
        return y * self.scaling + self.game_screen_origin_y

    def __game_coords_to_resolution_coords(
        self, coord: Tuple[float, float]
    ) -> Tuple[float, float]:
        x = coord[0]
        y = coord[1]
        return (self.__game_x_to_resolution_x(x), self.__game_y_to_resolution_y(y))

    def __res_draw_rect(self, x, y, width, height, color, border_width=0):
        pygame.draw.rect(
            self.__screen,
            color,
            [
                self.__game_x_to_resolution_x(x),
                self.__game_y_to_resolution_y(y),
                self.scaling * width,
                self.scaling * height,
            ],
            int(self.scaling * border_width),
        )

    def __res_draw_circle(self, x, y, radius, color, border_width=0):
        pygame.draw.circle(
            self.__screen,
            color,
            self.__game_coords_to_resolution_coords((x, y)),
            self.scaling * radius,
            int(self.scaling * border_width),
        )

    def __res_draw_polygon(self, points, color):
        points = [self.__game_coords_to_resolution_coords(i) for i in points]
        pygame.draw.polygon(self.__screen, color, points)
