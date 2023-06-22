import pygame
import random
from enum import Enum
from dataclasses import dataclass


class Constants:
    def __init__(self):
        self.game_width = 800
        self.game_height = 600
        self.gravity = 0.0002
        self.air_resistance_coefficient = 0.01
        self.user_impulse_per_millisecond = 0.01
        self.update_repetitions = 50


class Settings:
    def __init__(self):
        self.fps = 60
        self.resolution_width = 800
        self.resolution_height = 600


class SoundReprs(Enum):
    START_SOUND = "start_sound"
    HIT_SOUND = "hit_sound"
    BLOCK_SOUND = "block_sound"
    WIN_SOUND = "win_sound"


class Music(Enum):
    MENU = "menu.mp3"
    GAME_OVER = "game over.mp3"
    GAME_PLAY = "music.mp3"
    VICTORY = "win music.mp3"


class AudioInstructions:
    def __init__(self):
        self.sound_queue = []
        self.new_music = None

    def queue_sound(self, sound):
        self.sound_queue.append(sound)

    def queue_music_change(self, music):
        self.new_music = music


class Audio:
    def __init__(self):
        self.start_sound = pygame.mixer.Sound("start effect.mp3")
        self.hit_sound = pygame.mixer.Sound("paddle hit.mp3")
        self.block_sound = pygame.mixer.Sound("block hit.mp3")
        self.win_sound = pygame.mixer.Sound("win sound.wav")
        self.to_sounds = {
            SoundReprs.START_SOUND: self.start_sound,
            SoundReprs.HIT_SOUND: self.hit_sound,
            SoundReprs.BLOCK_SOUND: self.block_sound,
            SoundReprs.WIN_SOUND: self.win_sound,
        }
        self.to_music = {
            Music.MENU: "menu.mp3",
            Music.GAME_OVER: "game over.mp3",
            Music.GAME_PLAY: "music.mp3",
            Music.VICTORY: "win music.mp3",
        }
        self.player = pygame.mixer.music
        self.player.load(self.to_music[Music.MENU])
        self.player.play()

    def __change_music(self, music):
        self.player.unload()
        self.player.load(music)
        self.player.play()

    def run(self, instructions: AudioInstructions):
        for sound_repr in instructions.sound_queue:
            self.to_sounds[sound_repr].play()

        if instructions.new_music != None:
            self.__change_music(self.to_music[instructions.new_music])


class Message:
    def __init__(
        self, msg, size, x, y, font="arial", color=(255, 255, 255)
    ):  # This DOES mean that the game state has to "know" about colors and fonts
        self.msg = msg
        self.size = size
        self.x = x
        self.y = y
        self.font = font
        self.color = color

    def display(self, screen: pygame.Surface):
        surf = pygame.font.SysFont(self.font, self.size).render(
            self.msg, True, self.color
        )
        trect = surf.get_rect()
        trect.center = self.x, self.y
        screen.blit(surf, trect)


class Paddle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.x_vel = 0


class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.x_vel = random.uniform(-0.05, 0.05)
        self.y_vel = -0.28  # This doesn't seem to be the right place to hardcode this
        self.radius = 5


class Block:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.color = color


GameObject = Block | Paddle | Ball


@dataclass
class GraphicsInstructions:
    objects: list[GameObject]
    messages: list[Message]


class Graphics:  # Does not yet support different resolutions
    def __init__(self, resolution_width, resolution_height):
        self.screen = pygame.display.set_mode((resolution_width, resolution_height))
        self.paddle_color = (255, 255, 255)
        self.ball_color = (255, 255, 255)

    def render_paddle(self, paddle):
        pygame.draw.rect(
            self.screen,
            self.paddle_color,
            [paddle.x, paddle.y, paddle.width, paddle.height],
        )

    def render_block(self, block):
        pygame.draw.rect(
            self.screen,
            block.color,
            [block.x, block.y, block.width, block.height],
        )

    def render_ball(self, ball):
        pygame.draw.circle(self.screen, self.ball_color, (ball.x, ball.y), ball.radius)

    def render_object(self, obj):
        if type(obj) == Block:
            self.render_block(obj)
        elif type(obj) == Ball:
            self.render_ball(obj)
        elif type(obj) == Paddle:
            self.render_paddle(obj)

    def render(self, instructions: GraphicsInstructions):
        self.screen.fill((0, 0, 0))

        for obj in instructions.objects:
            self.render_object(obj)

        for msg in instructions.messages:
            msg.display(self.screen)

        pygame.display.update()


class InputHandler:
    def __init__(self):
        self.new_keys_pressed = []
        self.currently_pressed_keys = []
        self.quit = False

    def handle_input(self):
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


class GameState:
    def __init__(self):
        self.game_screen = "menu"
        self.game_exit = False
        self.settings = Settings()
        self.constants = Constants()

    def initialize_game(self):
        self.paddle = Paddle(
            self.constants.game_width / 2 - 50,
            0.9 * self.constants.game_height,
            100,
            10,
        )
        self.balls = [Ball(self.constants.game_width / 2, self.paddle.y - 50)]
        self.blocks = self.generate_blocks()
        self.game_screen = "play"

    def collision_check_ball_block(self, ball: Ball, block: Block):
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

    def collision_check_ball_wall(self, ball: Ball):
        if ball.x < ball.radius and ball.x_vel < 0:
            ball.x_vel *= -1
        elif ball.x > self.constants.game_width - ball.radius and ball.x_vel > 0:
            ball.x_vel *= -1
        if ball.y < ball.radius and ball.y_vel < 0:
            ball.y_vel *= -1

    def collision_check_ball_paddle(self, ball: Ball, paddle: Paddle):
        if ball.y >= paddle.y and ball.y <= paddle.y + paddle.height:
            if ball.x > paddle.x and ball.x < paddle.x + paddle.width:
                ball.y_vel *= -1
                ball.x_vel += paddle.x_vel / 20
                return True  # This should flag the paddle sound to be played

    def update_ball(self, ball: Ball, delta_t, audio_instructions: AudioInstructions):
        ball.y_vel += self.constants.gravity * delta_t
        if ball.x_vel > 0.1:
            ball.x_vel = 0.1
        elif ball.x_vel < -0.1:
            ball.x_vel = -0.1

        if ball.y > self.constants.game_height + ball.radius:
            self.balls.remove(ball)

        ball.y += ball.y_vel
        ball.x += ball.x_vel
        if self.collision_check_ball_paddle(ball, self.paddle):
            audio_instructions.queue_sound(SoundReprs.HIT_SOUND)
        self.collision_check_ball_wall(ball)
        for block in self.blocks:
            if self.collision_check_ball_block(ball, block):
                audio_instructions.queue_sound(SoundReprs.BLOCK_SOUND)

    def update_game(self, delta_t, keys, audio_instructions: AudioInstructions):
        if pygame.K_a in keys:
            impulse_sign = -1
        elif pygame.K_d in keys:
            impulse_sign = +1
        else:
            impulse_sign = 0

        self.paddle.x_vel += delta_t * (
            impulse_sign * self.constants.user_impulse_per_millisecond
            - self.constants.air_resistance_coefficient * self.paddle.x_vel
        )
        self.paddle.x += delta_t * self.paddle.x_vel

        if self.paddle.x > self.constants.game_width - self.paddle.width:
            self.paddle.x = self.constants.game_width - self.paddle.width
        elif self.paddle.x < 0:
            self.paddle.x = 0

        for ball in self.balls:
            self.update_ball(ball, delta_t, audio_instructions)

    def generate_blocks(self):
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

    def update(self, total_delta_t, input_handler: InputHandler, update_reps):
        audio_instructions = AudioInstructions()
        keys = input_handler.get_keys()

        messages = self.manage_screens(input_handler, audio_instructions)
        if self.game_screen == "play" or self.game_screen == "pause":
            if self.game_screen == "play":
                delta_t = total_delta_t / update_reps
                for i in range(update_reps):
                    self.update_game(delta_t, keys, audio_instructions)
            objects = self.game_objects_to_render()
        else:
            objects = []

        return audio_instructions, GraphicsInstructions(objects, messages)

    def game_objects_to_render(self) -> list[GameObject]:
        return [self.paddle] + self.balls + self.blocks

    def manage_screens(
        self,
        input_handler: InputHandler,
        audio_instructions: AudioInstructions,
    ) -> list[Message]:
        keys = input_handler.get_keys()
        answer = []

        if self.game_screen == "play":
            if pygame.K_p in input_handler.new_keys_pressed:
                self.game_screen = "pause"
            if len(self.balls) == 0:
                self.game_screen = "game over"
                audio_instructions.queue_music_change(Music.GAME_OVER)
            if len(self.blocks) == 0:
                self.game_screen = "game win"
                audio_instructions.queue_sound(SoundReprs.WIN_SOUND)
                audio_instructions.queue_music_change(Music.VICTORY)

        elif self.game_screen == "pause":
            if pygame.K_p in input_handler.new_keys_pressed:
                self.game_screen = "play"
            answer.append(
                Message(
                    "PAUSED",
                    50,
                    self.constants.game_width / 2,
                    self.constants.game_height / 2,
                )
            )
            answer.append(
                Message(
                    "Press P to continue",
                    25,
                    self.constants.game_width / 2,
                    0.75 * self.constants.game_height,
                )
            )

        elif self.game_screen == "game win" or self.game_screen == "game over":
            if pygame.K_r in keys:
                audio_instructions.queue_music_change(Music.GAME_PLAY)
                self.initialize_game()
            if pygame.K_q in keys:
                self.game_exit = True
            if self.game_screen == "game over":
                answer.append(
                    Message(
                        "GAME OVER",
                        50,
                        self.constants.game_width / 2,
                        self.constants.game_height / 2,
                    )
                )
                answer.append(
                    Message(
                        "Press R to restart",
                        25,
                        self.constants.game_width / 2,
                        0.7 * self.constants.game_height,
                    )
                )
                answer.append(
                    Message(
                        "Press Q to quit",
                        25,
                        self.constants.game_width / 2,
                        0.8 * self.constants.game_height,
                    )
                )
            else:
                answer.append(
                    Message(
                        "YOU WIN",
                        50,
                        self.constants.game_width / 2,
                        self.constants.game_height / 2,
                    )
                )
                answer.append(
                    Message(
                        "Press R to restart",
                        25,
                        self.constants.game_width / 2,
                        0.7 * self.constants.game_height,
                    )
                )
                answer.append(
                    Message(
                        "Press Q to quit",
                        25,
                        self.constants.game_width / 2,
                        0.8 * self.constants.game_height,
                    )
                )
        elif self.game_screen == "menu":
            if pygame.K_p in keys:
                audio_instructions.queue_music_change(Music.GAME_PLAY)
                self.initialize_game()
            if pygame.K_q in keys:
                self.game_exit = True
            answer.append(
                Message(
                    "Welcome to Breakout!",
                    50,
                    self.constants.game_width / 2,
                    self.constants.game_height / 2,
                )
            )
            answer.append(
                Message(
                    "Press P to play",
                    25,
                    self.constants.game_width / 2,
                    0.7 * self.constants.game_height,
                )
            )
            answer.append(
                Message(
                    "Press Q to quit",
                    25,
                    self.constants.game_width / 2,
                    0.8 * self.constants.game_height,
                )
            )
        return answer

    def check_quit(self, quit):
        if quit:
            self.game_exit = True


def GameLoop():
    game = GameState()
    clock = pygame.time.Clock()
    audio = Audio()
    graphics = Graphics(game.settings.resolution_width, game.settings.resolution_height)
    input_handler = InputHandler()

    while not game.game_exit:
        clock.tick(game.settings.fps)

        total_delta_t = clock.get_time()

        audio_instructions, graphics_instructions = game.update(
            total_delta_t, input_handler, game.constants.update_repetitions
        )

        game.check_quit(input_handler.quit)

        audio.run(audio_instructions)
        graphics.render(graphics_instructions)

        input_handler.handle_input()
        # print(total_delta_t)


def main():
    pygame.init()
    pygame.display.set_caption("Breakout")
    GameLoop()
    pygame.quit()


if __name__ == "__main__":
    main()
