import pygame
import random
from enum import Enum
from dataclasses import dataclass
from typing import Tuple

Color = Tuple[float, float, float]


class Constants:
    game_width = 800
    game_height = 600
    gravity = 0.0002
    air_resistance_coefficient = 0.01
    user_impulse_per_millisecond = 0.01
    update_repetitions = 50
    init_y_vel_ball = -0.28
    init_max_x_vel_ball = 0.05
    max_x_vel_ball = 0.1
    ball_radius = 5


class Settings:
    fps = 60
    resolution_width = 800
    resolution_height = 800


class Sound(Enum):
    START_SOUND = "start_sound"
    HIT_SOUND = "hit_sound"
    BLOCK_SOUND = "block_sound"
    WIN_SOUND = "win_sound"


class Music(Enum):
    MENU = "menu.mp3"
    GAME_OVER = "game over.mp3"
    GAME_PLAY = "music.mp3"
    VICTORY = "win music.mp3"


@dataclass
class AudioInstructions:
    sound_queue: list[Sound]
    new_music: Music

    def merge(self, other: "AudioInstructions") -> "AudioInstructions":
        """This will discard the new_music in the other file if both have new_music"""
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
        self.__to_sounds = {
            Sound.START_SOUND: start_sound,
            Sound.HIT_SOUND: hit_sound,
            Sound.BLOCK_SOUND: block_sound,
            Sound.WIN_SOUND: win_sound,
        }
        self.__to_music = {
            Music.MENU: "menu.mp3",
            Music.GAME_OVER: "game over.mp3",
            Music.GAME_PLAY: "music.mp3",
            Music.VICTORY: "win music.mp3",
        }
        self.__player = pygame.mixer.music
        self.__player.load(self.__to_music[Music.MENU])
        self.__player.play()

    def __change_music(self, music: str):
        self.__player.unload()
        self.__player.load(music)
        self.__player.play()

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
class Paddle:
    x: float
    y: float
    width: float
    height: float
    x_vel: float


@dataclass
class Ball:
    x: float
    y: float
    x_vel: float
    y_vel: float
    radius: float


@dataclass
class Block:
    x: float
    y: float
    width: float
    height: float
    color: Color


GameObject = Block | Paddle | Ball


@dataclass
class GraphicsInstructions:
    objects: list[GameObject]
    messages: list[Message]


class Graphics:  # Does not yet support different resolutions
    def __init__(self):
        self.__screen = pygame.display.set_mode(
            (Settings.resolution_width, Settings.resolution_height)
        )
        self.__paddle_color = (255, 255, 255)
        self.__ball_color = (255, 255, 255)
        self.__set_game_screen()

    def render(self, instructions: GraphicsInstructions):
        self.__screen.fill((0, 0, 0))

        pygame.draw.rect(
            self.__screen,
            (15, 15, 15),
            [
                self.game_screen_origin_x,
                self.game_screen_origin_y,
                self.game_screen_width,
                self.game_screen_height,
            ],
        )

        for obj in instructions.objects:
            self.__render_object(obj)

        for msg in instructions.messages:
            self.__render_message(msg)

        pygame.display.update()

    def __reset_resolution(self):
        self.__screen = pygame.display.set_mode(
            (Settings.resolution_width, Settings.resolution_height)
        )
        self.__set_game_screen()

    def __render_paddle(self, paddle: Paddle):
        pygame.draw.rect(
            self.__screen,
            (self.__paddle_color),
            [
                self.__game_x_to_resolution_x(paddle.x),
                self.__game_y_to_resolution_y(paddle.y),
                self.scaling * paddle.width,
                self.scaling * paddle.height,
            ],
        )

    def __render_block(self, block: Block):
        pygame.draw.rect(
            self.__screen,
            block.color,
            [
                self.__game_x_to_resolution_x(block.x),
                self.__game_y_to_resolution_y(block.y),
                self.scaling * block.width,
                self.scaling * block.height,
            ],
        )

    def __render_ball(self, ball: Ball):
        pygame.draw.circle(
            self.__screen,
            self.__ball_color,
            (
                self.__game_x_to_resolution_x(ball.x),
                self.__game_y_to_resolution_y(ball.y),
            ),
            self.scaling * ball.radius,
        )

    def __render_object(self, obj: GameObject):
        if type(obj) == Block:
            self.__render_block(obj)
        elif type(obj) == Ball:
            self.__render_ball(obj)
        elif type(obj) == Paddle:
            self.__render_paddle(obj)

    def __render_message(self, msg: Message):
        surf = pygame.font.SysFont(msg.font, round(self.scaling * msg.size)).render(
            msg.text, True, msg.color
        )
        trect = surf.get_rect()
        trect.center = self.__game_x_to_resolution_x(
            msg.x
        ), self.__game_y_to_resolution_y(msg.y)
        self.__screen.blit(surf, trect)

    def __set_game_screen(self):
        ratio = Constants.game_width / Constants.game_height
        res_ratio = Settings.resolution_width / Settings.resolution_height
        if res_ratio < ratio:
            self.game_screen_width = Settings.resolution_width
            self.game_screen_height = self.game_screen_width / ratio
            self.black_bars = "horizontal"
            self.scaling = self.game_screen_width / Constants.game_width
        elif res_ratio > ratio:
            self.game_screen_height = Settings.resolution_height
            self.game_screen_width = self.game_screen_height * ratio
            self.black_bars = "vertical"
            self.scaling = self.game_screen_height / Constants.game_height
        else:
            self.game_screen_height = Settings.resolution_height
            self.game_screen_width = Settings.resolution_width
            self.black_bars = "none"
            self.scaling = self.game_screen_height / Constants.game_height

        if self.black_bars == "none":
            self.game_screen_origin_x = 0
            self.game_screen_origin_y = 0
        elif self.black_bars == "horizontal":
            self.game_screen_origin_x = 0
            self.game_screen_origin_y = (Settings.resolution_height / 2) - (
                self.game_screen_height / 2
            )
        elif self.black_bars == "vertical":
            self.game_screen_origin_y = 0
            self.game_screen_origin_x = (Settings.resolution_width / 2) - (
                self.game_screen_width / 2
            )

    def __game_x_to_resolution_x(self, x: float) -> float:
        return x * self.scaling + self.game_screen_origin_x

    def __game_y_to_resolution_y(self, y: float) -> float:
        return y * self.scaling + self.game_screen_origin_y


class KeyboardState:
    def __init__(self):
        self.new_keys_pressed = []
        self.currently_pressed_keys = []
        self.quit = False

    def handle_pygame_events(self):
        self.currently_pressed_keys.extend(self.new_keys_pressed)
        self.new_keys_pressed = []

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key not in self.currently_pressed_keys:
                    self.new_keys_pressed.append(event.key)
            elif event.type == pygame.KEYUP:
                if (
                    event.key in self.currently_pressed_keys
                ):  # Technically it should always be, but just in case
                    self.currently_pressed_keys.remove(event.key)
            elif event.type == pygame.QUIT:
                self.quit = True

    def get_keys(self):
        return self.currently_pressed_keys + self.new_keys_pressed


class GameFsmState(Enum):
    MENU = "menu"
    PLAY = "play"
    PAUSE = "pause"
    GAME_WIN = "game win"
    GAME_OVER = "game over"
    QUIT = "quit"
    INSTRUCTIONS = "instructions"
    SETTINGS = "settings"


class CoreGameState:
    def __init__(self):
        self.paddle = Paddle(
            Constants.game_width / 2 - 50,
            0.9 * Constants.game_height,
            100,
            10,
            0,
        )
        self.balls = [
            Ball(
                Constants.game_width / 2,
                self.paddle.y - 50,
                random.uniform(
                    -1 * Constants.init_max_x_vel_ball,
                    Constants.init_max_x_vel_ball,
                ),
                Constants.init_y_vel_ball,
                Constants.ball_radius,
            )
        ]
        self.blocks = self.__generate_blocks()

    def update(
        self, total_delta_t: float, keys: list[int]
    ) -> Tuple[list[Sound], list[GameObject]]:
        delta_t = total_delta_t / Constants.update_repetitions
        output_sounds = []

        for _ in range(Constants.update_repetitions):
            self.__update_game_physics(delta_t, keys, output_sounds)

        return output_sounds, self.__game_objects_to_render()

    def game_over(self) -> bool:
        condition = len(self.balls) == 0
        return True if condition else False

    def game_win(self) -> bool:
        condition = len(self.blocks) == 0
        return True if condition else False

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

        for ball in self.balls:
            self.__update_ball(ball, delta_t, output_sounds)

    def __game_objects_to_render(self) -> list[GameObject]:
        return [self.paddle] + self.balls + self.blocks

    def __generate_blocks(self) -> list[Block]:
        blocks = []
        for i in range(8):
            for j in range(4):
                blocks.append(
                    Block(
                        100 * i + 2,
                        50 * j + 2,
                        95,
                        45,
                        tuple((random.randint(0, 255) for i in range(3))),
                    )
                )
        return blocks

    def __collision_check_ball_block(self, ball: Ball, block: Block) -> bool:
        if (
            block.x - ball.radius < ball.x < block.x + block.width + ball.radius
            and block.y - ball.radius < ball.y < block.y + block.height + ball.radius
        ):
            if ball.y > block.y + block.height and ball.y_vel < 0:
                ball.y_vel *= -1
                self.blocks.remove(block)
            elif ball.y < block.y and ball.y_vel > 0:
                ball.y_vel *= -1
                self.blocks.remove(block)
            elif ball.x > block.x + block.width and ball.x_vel < 0:
                ball.x_vel *= -1
                self.blocks.remove(block)
            elif ball.x < block.x and ball.x_vel > 0:
                ball.x_vel *= -1
                self.blocks.remove(block)
            return True  # This should flag the block sound to be played

    def __collision_check_ball_wall(self, ball: Ball):
        if ball.x < ball.radius and ball.x_vel < 0:
            ball.x_vel *= -1
        elif ball.x > Constants.game_width - ball.radius and ball.x_vel > 0:
            ball.x_vel *= -1
        if ball.y < ball.radius and ball.y_vel < 0:
            ball.y_vel *= -1

    def __collision_check_ball_paddle(self, ball: Ball, paddle: Paddle) -> bool:
        if ball.y >= paddle.y and ball.y <= paddle.y + paddle.height:
            if ball.x > paddle.x and ball.x < paddle.x + paddle.width:
                ball.y_vel *= -1
                ball.x_vel += paddle.x_vel / 20
                return True  # This should flag the paddle sound to be played

    def __update_ball(self, ball: Ball, delta_t: float, output_sounds: list[Sound]):
        ball.y_vel += Constants.gravity * delta_t
        if ball.x_vel > 0.1:
            ball.x_vel = 0.1
        elif ball.x_vel < -0.1:
            ball.x_vel = -0.1

        if ball.y > Constants.game_height + ball.radius:
            self.balls.remove(ball)

        ball.y += ball.y_vel
        ball.x += ball.x_vel
        if self.__collision_check_ball_paddle(ball, self.paddle):
            output_sounds.append(Sound.HIT_SOUND)
        self.__collision_check_ball_wall(ball)
        for block in self.blocks:
            if self.__collision_check_ball_block(ball, block):
                output_sounds.append(Sound.BLOCK_SOUND)


class GameState:
    def __init__(self):
        self.game_fsm_state = GameFsmState.MENU
        self.game_exit = False
        self.settings = Settings()

    def update(
        self, total_delta_t: float, keyboard_state: KeyboardState
    ) -> Tuple[AudioInstructions, GraphicsInstructions]:
        keys = keyboard_state.get_keys()

        next_fsm_state = self.__next_fsm_state(keyboard_state)

        transition_audio_instructions = AudioInstructions([], None)
        collision_sounds = AudioInstructions([], None)

        if next_fsm_state != None:
            transition_audio_instructions = state_transition_audio(
                self.game_fsm_state, next_fsm_state
            )
            self.__on_transition(next_fsm_state)

        if (
            self.game_fsm_state == GameFsmState.PLAY
            or self.game_fsm_state == GameFsmState.PAUSE
        ):
            if self.game_fsm_state == GameFsmState.PLAY:
                sounds, objects = self.core_game_state.update(total_delta_t, keys)

                collision_sounds = AudioInstructions(sounds, None)
        else:
            objects = []

        return transition_audio_instructions.merge(
            collision_sounds
        ), GraphicsInstructions(objects, screen_content(self.game_fsm_state))

    def __initialize_game(self):
        self.core_game_state = CoreGameState()

    def __next_fsm_state(self, keyboard_state: KeyboardState) -> GameFsmState | None:
        keys = keyboard_state.get_keys()

        if self.game_fsm_state == GameFsmState.MENU:
            if pygame.K_p in keyboard_state.new_keys_pressed:
                return GameFsmState.PLAY
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
                return GameFsmState.PLAY
            elif pygame.K_q in keys:
                return GameFsmState.QUIT

        elif self.game_fsm_state == GameFsmState.PLAY:
            if self.core_game_state.game_over():
                return GameFsmState.GAME_OVER
            elif self.core_game_state.game_win():
                return GameFsmState.GAME_WIN
            elif pygame.K_p in keyboard_state.new_keys_pressed:
                return GameFsmState.PAUSE

        elif self.game_fsm_state == GameFsmState.PAUSE:
            if pygame.K_p in keyboard_state.new_keys_pressed:
                return GameFsmState.PLAY

        if keyboard_state.quit:
            self.game_exit = True

    def __on_transition(self, next_state: GameFsmState):
        if (
            next_state == GameFsmState.PLAY
            and self.game_fsm_state != GameFsmState.PAUSE
        ):
            self.__initialize_game()
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
        sounds.append(Sound.WIN_SOUND)
        new_music = Music.VICTORY
    elif target_state == GameFsmState.GAME_OVER:
        new_music = Music.GAME_OVER
    elif target_state == GameFsmState.PLAY:
        if current_state in [
            GameFsmState.GAME_OVER,
            GameFsmState.GAME_WIN,
            GameFsmState.MENU,
        ]:
            new_music = Music.GAME_PLAY
    return AudioInstructions(sounds, new_music)


def screen_content(game_fsm_state: GameFsmState) -> list[Message]:
    answer = []
    if game_fsm_state == GameFsmState.MENU:
        answer.append(
            Message(
                "Welcome to Breakout!",
                50,
                Constants.game_width / 2,
                Constants.game_height / 2,
            )
        )
        answer.append(
            Message(
                "Press P to play",
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
                    Settings.resolution_width, Settings.resolution_height
                ),
                25,
                Constants.game_width / 2,
                0.4 * Constants.game_height,
            )
        )
        answer.append(
            Message(
                "FPS              :             {}".format(Settings.fps),
                25,
                Constants.game_width / 2,
                0.7 * Constants.game_height,
            )
        )

    return answer


def GameLoop():
    game = GameState()
    clock = pygame.time.Clock()
    audio = Audio()
    graphics = Graphics()
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


def main():
    pygame.init()
    pygame.display.set_caption("Breakout")
    GameLoop()
    pygame.quit()


if __name__ == "__main__":
    main()
