import pygame
import random
from enum import Enum
from dataclasses import dataclass
from typing import Tuple
import copy
import math

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


@dataclass
class Message:
    text: str
    size: int
    x: float
    y: float
    font: str = "arial"
    color: Color = (255, 255, 255)


@dataclass
class SettingsSelector:
    x: float
    y: float
    width: int


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


GameObject = Block | Paddle | Ball | Powerup
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


class Graphics:  # Does not yet support different resolutions
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


class KeyboardState:
    def __init__(self):
        self.new_keys_pressed = set()
        self.currently_pressed_keys = set()
        self.quit = False

    def handle_pygame_events(self):
        self.currently_pressed_keys = self.currently_pressed_keys.union(
            self.new_keys_pressed
        )
        self.new_keys_pressed = set()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key not in self.currently_pressed_keys:
                    self.new_keys_pressed.add(event.key)
            elif event.type == pygame.KEYUP:
                if (
                    event.key in self.currently_pressed_keys
                ):  # Technically it should always be, but just in case
                    self.currently_pressed_keys.remove(event.key)
            elif event.type == pygame.QUIT:
                self.quit = True

    def get_keys(self):
        return self.currently_pressed_keys.union(self.new_keys_pressed)


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


class CoreGameState:
    def __init__(self):
        self.lives = Constants.initial_lives
        self.paddle = Paddle(
            Constants.game_width / 2 - 50,
            0.9 * Constants.game_height,
            100,
            10,
            0,
            self.lives,
        )
        self.ball = Ball(
            Constants.game_width / 2,
            self.paddle.y - Constants.ball_radius,
            random.uniform(
                -1 * Constants.init_max_x_vel_ball,
                Constants.init_max_x_vel_ball,
            ),
            0,
            Constants.ball_radius,
        )

        self.blocks = self.__generate_blocks(9, 5)
        self.__set_special_blocks()
        self.__update_block_effects()
        self.powerups = []
        self.new_life = False

    def update(
        self, total_delta_t: float, keys: list[int], game_fsm_state
    ) -> Tuple[list[Sound], list[GameObject]]:
        delta_t = total_delta_t / Constants.update_repetitions
        output_sounds = []

        if game_fsm_state == GameFsmState.PLAY:
            for _ in range(Constants.update_repetitions):
                self.__update_game_physics(delta_t, keys, output_sounds)

        return output_sounds, self.__game_objects_to_render()

    def game_over(self) -> bool:
        condition = self.lives == 0
        return True if condition else False

    def game_win(self) -> bool:
        condition = len(self.blocks) == 0
        return True if condition else False

    def start_new_life(self) -> bool:
        if self.new_life == True:
            self.new_life = False
            return True
        else:
            return False

    def make_new_ball(self):
        self.ball = Ball(
            self.paddle.x + self.paddle.width / 2,
            self.paddle.y - Constants.ball_radius,
            random.uniform(
                -1 * Constants.init_max_x_vel_ball,
                Constants.init_max_x_vel_ball,
            ),
            0,
            Constants.ball_radius,
        )

    def __update_game_physics(
        self, delta_t: float, keys: list[int], output_sounds: list[Sound]
    ):
        if pygame.K_a in keys:
            impulse_sign = -1
        elif pygame.K_d in keys:
            impulse_sign = +1
        else:
            impulse_sign = 0

        self.paddle.x_vel += delta_t * (
            impulse_sign * Constants.user_impulse_per_millisecond
            - Constants.air_resistance_coefficient * self.paddle.x_vel
        )
        self.paddle.x += delta_t * self.paddle.x_vel

        if self.paddle.x > Constants.game_width - self.paddle.width:
            self.paddle.x = Constants.game_width - self.paddle.width
        elif self.paddle.x < 0:
            self.paddle.x = 0

        if self.ball != None:
            self.__update_ball(self.ball, delta_t, output_sounds)

        for powerup in self.powerups:
            self.__update_powerup(powerup, delta_t, output_sounds)

    def __game_objects_to_render(self) -> list[GameObject]:
        return [self.paddle] + [self.ball] + self.blocks + self.powerups

    def __get_block_from_id(self, id: Tuple[int, int]) -> Block | None:
        for block in self.blocks:
            if block.block_id == id:
                return block

        return None

    def __generate_blocks(self, num_cols, num_rows) -> list[Block]:
        blocks = []
        gap = 2
        for i in range(num_cols):
            for j in range(num_rows):
                blocks.append(
                    Block(
                        (Constants.game_width / num_cols) * i + gap,
                        (Constants.game_height / (3 * num_rows)) * j + gap,
                        (Constants.game_width / num_cols) - 2 * gap,
                        (Constants.game_height / (3 * num_rows)) - 2 * gap,
                        (i, j),
                        BlockType.NORMAL,
                        1,
                        0,
                        Colors.generate_random_block_color(),
                    )
                )

        return blocks

    def __set_special_blocks(self):
        for block in self.blocks:
            block.block_type = BlockType.normal_or_powerup(
                Constants.powerup_probability
            )

            if block.block_id[1] in [0, 2]:
                block.health += 1
            if block.block_id in [(4, 2)]:
                block.block_type = BlockType.PROTECTOR

    def __collision_check_ball_block(self, ball: Ball, block: Block) -> bool:
        collision_type = None
        if (
            block.x - ball.radius < ball.x < block.x + block.width + ball.radius
            and block.y - ball.radius < ball.y < block.y + block.height + ball.radius
        ):
            if ball.y > block.y + block.height and ball.y_vel < 0:
                collision_type = "vertical"
            elif ball.y < block.y and ball.y_vel > 0:
                collision_type = "vertical"
            elif ball.x > block.x + block.width and ball.x_vel < 0:
                collision_type = "horizontal"
            elif ball.x < block.x and ball.x_vel > 0:
                collision_type = "horizontal"

        if collision_type != None:
            if ball.modifier == BallModifier.PIERCING:
                if (ball.blocks_pierced < ball.max_blocks_can_pierce) and (
                    block.health <= 1 or block.protection <= 0
                ):
                    ball.blocks_pierced += 1
                else:
                    ball.blocks_pierced = 0
                    if collision_type == "vertical":
                        ball.y_vel *= -1
                    elif collision_type == "horizontal":
                        ball.x_vel *= -1

            else:
                if collision_type == "vertical":
                    ball.y_vel *= -1
                elif collision_type == "horizontal":
                    ball.x_vel *= -1

            return True  # This should flag the block sound to be played

    def __collision_check_ball_wall(self, ball: Ball):
        if ball.x < ball.radius and ball.x_vel < 0:
            ball.x_vel *= -1
        elif ball.x > Constants.game_width - ball.radius and ball.x_vel > 0:
            ball.x_vel *= -1
        if ball.y < ball.radius and ball.y_vel < 0:
            ball.y_vel *= -1

    def __collision_check_ball_paddle(self, ball: Ball, paddle: Paddle) -> bool:
        collision_occurred = False
        if ball.y_vel <= 0:
            return False

        if (
            paddle.y - ball.radius <= ball.y <= paddle.y + paddle.height
            and paddle.x - ball.radius
            <= ball.x
            <= paddle.x + paddle.width + ball.radius
        ):
            if ball.y <= paddle.y:
                ball.y_vel *= -1
                ball.x_vel += paddle.x_vel / 5
                collision_occurred = True
            elif ball.y >= paddle.y and (
                ball.x < paddle.x or ball.x > paddle.x + paddle.width
            ):
                ball.y_vel *= -1
                ball.x_vel += paddle.x_vel
                collision_occurred = True
        return collision_occurred  # This should flag the paddle sound to be played

    def __collision_check_powerup_paddle(self, powerup: Powerup, paddle: Paddle):
        if (
            paddle.y - powerup.hitbox_radius
            <= powerup.y
            <= paddle.y + paddle.height + powerup.hitbox_radius
            and paddle.x - powerup.hitbox_radius
            <= powerup.x
            <= paddle.x + paddle.width + powerup.hitbox_radius
        ):
            self.powerups.remove(powerup)
            return True

    def __update_block_from_collision(self, block: Block, output_sounds: list[Sound]):
        if block.protection == 0:
            block.health -= 1

        if block.health <= 0:
            self.__break_block(block)
            output_sounds.append(Sound.BLOCK)
            self.__update_block_effects()

    def __update_block_effects(self):  # Awkward?
        for block in self.blocks:
            block.protection = 0

        for block in self.blocks:
            if block.block_type == BlockType.PROTECTOR:
                i, j = block.block_id
                self.__get_block_from_id((i, j + 1)).protection += 1
                self.__get_block_from_id((i - 1, j + 1)).protection += 1
                self.__get_block_from_id((i + 1, j + 1)).protection += 1

    def __break_block(self, block: Block):
        if block.block_type == BlockType.POWERUP:
            self.__spawn_powerup(
                block.x + block.width / 2,
                block.y + block.height / 2,
                block.height / 2,
            )
        self.blocks.remove(block)

    def __update_ball(self, ball: Ball, delta_t: float, output_sounds: list[Sound]):
        ball.y_vel += Constants.gravity * delta_t
        if ball.x_vel > 0.1:
            ball.x_vel = 0.1
        elif ball.x_vel < -0.1:
            ball.x_vel = -0.1

        if ball.y > Constants.game_height + ball.radius:
            self.lives -= 1
            self.__new_life()

        else:
            ball.y += ball.y_vel * delta_t
            ball.x += ball.x_vel * delta_t
            if self.__collision_check_ball_paddle(ball, self.paddle):
                output_sounds.append(Sound.HIT)
            self.__collision_check_ball_wall(ball)
            for block in self.blocks:
                if self.__collision_check_ball_block(ball, block):
                    self.__update_block_from_collision(block, output_sounds)

            if ball.modifier == BallModifier.PIERCING:
                ball.modifier_active_for -= delta_t
                if ball.modifier_active_for <= 0:
                    ball.modifier_active_for = 0
                    ball.modifier = None

    def __spawn_powerup(self, x, y, hitbox_radius):
        ptype = random.choices(list(PowerupType), Constants.powerup_type_probabilities)[
            0
        ]
        self.powerups.append(Powerup(ptype, x, y, hitbox_radius))

    def __update_powerup(
        self, powerup: Powerup, delta_t: float, output_sounds: list[Sound]
    ):
        powerup.y += delta_t * Constants.powerup_fall_speed
        if self.__collision_check_powerup_paddle(powerup, self.paddle):
            output_sounds.append(Sound.POWERUP)
            if powerup.powerup_type == PowerupType.PIERCING:
                self.ball.make_piercing(3000, 1)
            elif powerup.powerup_type == PowerupType.LIFE:
                self.lives += 1
                self.paddle.lives += 1

    def __new_life(self):
        self.paddle.lives = self.lives
        self.ball = None
        self.new_life = True


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


class GameState:
    def __init__(self):
        self.game_fsm_state = GameFsmState.MENU
        self.game_exit = False
        self.settings = copy.deepcopy(Constants.default_settings)
        self.settings_state = None

    def update(
        self, total_delta_t: float, keyboard_state: KeyboardState
    ) -> Tuple[AudioInstructions, GraphicsInstructions]:
        keys = keyboard_state.get_keys()
        graphics_instructions = GraphicsInstructions([], [], None)

        next_fsm_state = self.__next_fsm_state(keyboard_state)

        transition_audio_instructions = AudioInstructions([], None)
        collision_sounds = AudioInstructions([], None)

        if next_fsm_state != None:
            transition_audio_instructions = state_transition_audio(
                self.game_fsm_state, next_fsm_state
            )
            self.__on_transition(next_fsm_state)

        objects = []
        ui_elements = []
        if self.game_fsm_state in [
            GameFsmState.PLAY,
            GameFsmState.PAUSE,
            GameFsmState.PRE_PLAY,
        ]:  # Should this be a set?
            sounds, objects = self.core_game_state.update(
                total_delta_t, keys, self.game_fsm_state
            )
            collision_sounds = AudioInstructions(sounds, None)
        elif self.game_fsm_state == GameFsmState.SETTINGS:
            new_settings, ui_elements = self.settings_state.update(keyboard_state)
            if new_settings != None:
                self.settings = copy.deepcopy(new_settings)
                graphics_instructions += GraphicsInstructions(
                    [], [], new_settings.graphics_settings
                )

        screen_ui = (
            screen_content(self.game_fsm_state)
            if self.game_fsm_state != GameFsmState.SETTINGS
            else screen_content(GameFsmState.SETTINGS, self.settings_state)
        )
        screen_graphics = GraphicsInstructions(
            objects,
            screen_ui,
        )
        ui_graphics = GraphicsInstructions([], ui_elements)

        audio_instructions = transition_audio_instructions.merge(collision_sounds)
        graphics_instructions += screen_graphics + ui_graphics

        return audio_instructions, graphics_instructions

    def __initialize_game(self):
        self.core_game_state = CoreGameState()

    def __next_fsm_state(self, keyboard_state: KeyboardState) -> GameFsmState | None:
        keys = keyboard_state.get_keys()

        if self.game_fsm_state == GameFsmState.MENU:
            if pygame.K_p in keyboard_state.new_keys_pressed:
                return GameFsmState.PRE_PLAY
            elif pygame.K_q in keys:
                return GameFsmState.QUIT
            elif pygame.K_i in keys:
                return GameFsmState.INSTRUCTIONS
            elif pygame.K_s in keys:
                return GameFsmState.SETTINGS

        elif self.game_fsm_state == GameFsmState.INSTRUCTIONS:
            if pygame.K_m in keys:
                return GameFsmState.MENU

        elif self.game_fsm_state == GameFsmState.SETTINGS:
            if pygame.K_m in keys:
                return GameFsmState.MENU

        elif self.game_fsm_state in [
            GameFsmState.GAME_OVER,
            GameFsmState.GAME_WIN,
        ]:
            if pygame.K_r in keys:
                return GameFsmState.PRE_PLAY
            elif pygame.K_q in keys:
                return GameFsmState.QUIT

        elif self.game_fsm_state == GameFsmState.PLAY:
            if self.core_game_state.game_over():
                return GameFsmState.GAME_OVER
            elif self.core_game_state.game_win():
                return GameFsmState.GAME_WIN
            elif self.core_game_state.start_new_life():
                return GameFsmState.PRE_PLAY
            elif pygame.K_p in keyboard_state.new_keys_pressed:
                return GameFsmState.PAUSE

        elif self.game_fsm_state == GameFsmState.PAUSE:
            if pygame.K_p in keyboard_state.new_keys_pressed:
                return GameFsmState.PLAY

        elif self.game_fsm_state == GameFsmState.PRE_PLAY:
            if pygame.K_l in keys:
                return GameFsmState.PLAY

        if keyboard_state.quit:
            self.game_exit = True

    def __on_transition(self, next_state: GameFsmState):
        if next_state == GameFsmState.PRE_PLAY:
            if self.game_fsm_state in [
                GameFsmState.MENU,
                GameFsmState.GAME_OVER,
                GameFsmState.GAME_WIN,
            ]:
                self.__initialize_game()
            elif self.game_fsm_state == GameFsmState.PLAY:
                self.core_game_state.make_new_ball()

        elif (
            next_state == GameFsmState.PLAY
            and self.game_fsm_state == GameFsmState.PRE_PLAY
        ):
            self.core_game_state.ball.y_vel = Constants.init_y_vel_ball

        elif next_state == GameFsmState.GAME_OVER:
            self.core_game_state = None

        elif next_state == GameFsmState.SETTINGS:
            self.settings_state = SettingsState(self.settings)

        if next_state == GameFsmState.QUIT:
            self.game_exit = True

        self.game_fsm_state = next_state


def state_transition_audio(
    current_state: GameFsmState,
    target_state: GameFsmState,
) -> AudioInstructions:
    sounds = []
    new_music = None
    if target_state == GameFsmState.GAME_WIN:
        sounds.append(Sound.WIN)
        new_music = Music.VICTORY
    elif target_state == GameFsmState.GAME_OVER:
        new_music = Music.GAME_OVER
    elif target_state == GameFsmState.PRE_PLAY and current_state != GameFsmState.PLAY:
        new_music = Music.GAME_PLAY
    return AudioInstructions(sounds, new_music)


def screen_content(
    game_fsm_state: GameFsmState, settings_state: SettingsState = None
) -> list[Message]:
    answer = []
    if game_fsm_state == GameFsmState.MENU:
        answer.append(
            Message(
                "Welcome to Breakout!",
                50,
                Constants.game_width / 2,
                0.3 * Constants.game_height,
            )
        )
        answer.append(
            Message(
                "Press P to play",
                25,
                Constants.game_width / 2,
                0.5 * Constants.game_height,
            )
        )
        answer.append(
            Message(
                "Press I for instructions",
                25,
                Constants.game_width / 2,
                0.6 * Constants.game_height,
            )
        )
        answer.append(
            Message(
                "Press S for settings",
                25,
                Constants.game_width / 2,
                0.7 * Constants.game_height,
            )
        )
        answer.append(
            Message(
                "Press Q to quit",
                25,
                Constants.game_width / 2,
                0.8 * Constants.game_height,
            )
        )

    elif game_fsm_state == GameFsmState.PAUSE:
        answer.append(
            Message(
                "PAUSED",
                50,
                Constants.game_width / 2,
                Constants.game_height / 2,
            )
        )
        answer.append(
            Message(
                "Press P to continue",
                25,
                Constants.game_width / 2,
                0.75 * Constants.game_height,
            )
        )

    elif game_fsm_state == GameFsmState.GAME_OVER:
        answer.append(
            Message(
                "GAME OVER",
                50,
                Constants.game_width / 2,
                Constants.game_height / 2,
            )
        )
        answer.append(
            Message(
                "Press R to restart",
                25,
                Constants.game_width / 2,
                0.7 * Constants.game_height,
            )
        )
        answer.append(
            Message(
                "Press Q to quit",
                25,
                Constants.game_width / 2,
                0.8 * Constants.game_height,
            )
        )

    elif game_fsm_state == GameFsmState.GAME_WIN:
        answer.append(
            Message(
                "YOU WIN",
                50,
                Constants.game_width / 2,
                Constants.game_height / 2,
            )
        )
        answer.append(
            Message(
                "Press R to restart",
                25,
                Constants.game_width / 2,
                0.7 * Constants.game_height,
            )
        )
        answer.append(
            Message(
                "Press Q to quit",
                25,
                Constants.game_width / 2,
                0.8 * Constants.game_height,
            )
        )

    elif game_fsm_state == GameFsmState.INSTRUCTIONS:
        answer.append(
            Message(
                "INSTRUCTIONS",
                50,
                Constants.game_width / 2,
                0.05 * Constants.game_height,
            )
        )
        answer.append(
            Message(
                "Press A and D to move the paddle and P to pause",
                25,
                Constants.game_width / 2,
                0.3 * Constants.game_height,
            )
        )
        answer.append(
            Message(
                "Try to break all the blocks",
                25,
                Constants.game_width / 2,
                0.5 * Constants.game_height,
            )
        )
        answer.append(
            Message(
                "If your ball falls off the screen, you lose",
                25,
                Constants.game_width / 2,
                0.7 * Constants.game_height,
            )
        )
        answer.append(
            Message(
                "Press M to return to the menu",
                25,
                Constants.game_width / 2,
                0.9 * Constants.game_height,
            )
        )

    elif game_fsm_state == GameFsmState.SETTINGS:
        answer.append(
            Message(
                "SETTINGS",
                50,
                Constants.game_width / 2,
                0.05 * Constants.game_height,
            )
        )
        answer.append(
            Message(
                "Resolution              :             {} x {}".format(
                    SettingsState.possible_resolutions[settings_state.temp_resolution][
                        0
                    ],
                    SettingsState.possible_resolutions[settings_state.temp_resolution][
                        1
                    ],
                ),
                25,
                Constants.game_width / 2,
                0.4 * Constants.game_height,
            )
        )
        answer.append(
            Message(
                "FPS              :             {}".format(settings_state.temp_fps),
                25,
                Constants.game_width / 2,
                0.7 * Constants.game_height,
            )
        )
        answer.append(
            Message(
                "Press M to return to the menu",
                25,
                Constants.game_width / 2,
                0.9 * Constants.game_height,
            )
        )
    elif game_fsm_state == GameFsmState.PRE_PLAY:
        answer.append(
            Message(
                "Press L to launch",
                25,
                Constants.game_width / 2,
                0.8 * Constants.game_height,
            )
        )

    return answer


def check_invariants(game: GameState, graphics: Graphics):
    assert game.settings.graphics_settings == graphics.graphics_settings
    if game.settings_state != None:
        assert game.settings == game.settings_state.settings


def GameLoop():
    game = GameState()
    clock = pygame.time.Clock()
    audio = Audio()
    graphics = Graphics(game.settings.graphics_settings)
    keyboard_state = KeyboardState()

    while not game.game_exit:
        clock.tick(game.settings.fps)

        total_delta_t = clock.get_time()

        audio_instructions, graphics_instructions = game.update(
            total_delta_t, keyboard_state
        )

        audio.run(audio_instructions)
        graphics.render(graphics_instructions)

        keyboard_state.handle_pygame_events()
        check_invariants(game, graphics)


def main():
    pygame.init()
    pygame.display.set_caption("Breakout")
    GameLoop()
    pygame.quit()


if __name__ == "__main__":
    main()
