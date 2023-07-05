from dataclasses import dataclass
from enum import Enum
import random
from typing import Tuple
import pygame

from Context import Color, Colors, GameFsmState
from Settings import Constants
from Audio import Sound


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
