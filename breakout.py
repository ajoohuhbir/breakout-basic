import pygame
import random


class Constants:
    def __init__(self):
        self.game_width = 800
        self.game_height = 600
        self.gravity = 0.0002
        self.air_resistance_coefficient = 0.01
        self.user_impulse_per_millisecond = 0.01


class Settings:
    def __init__(self):
        self.fps = 60
        self.resolution_width = 800
        self.resolution_height = 600


class Sounds:
    def __init__(self):
        self.start_sound = pygame.mixer.Sound("start effect.mp3")
        self.hit_sound = pygame.mixer.Sound("paddle hit.mp3")
        self.block_sound = pygame.mixer.Sound("block hit.mp3")
        self.win_sound = pygame.mixer.Sound("win sound.wav")


class Music:
    def __init__(self):
        self.menu = "menu.mp3"
        self.game_over = "game over.mp3"
        self.game_play = "music.mp3"
        self.victory = "win music.mp3"


class AudioInstructions:
    def __init__(self):
        self.music = Music()
        self.sounds = Sounds()
        self.sound_queue = []
        self.new_music = None

    def queue_sound(self, sound):
        self.sound_queue.append(sound)

    def queue_music_change(self, music):
        self.new_music = music


class Audio:
    def __init__(self):
        self.music = Music()
        self.player = pygame.mixer.music
        self.player.load(self.music.menu)
        self.player.play()

    def change_music(self, music):
        self.player.unload()
        self.player.load(music)
        self.player.play()

    def run(self, instructions: AudioInstructions):
        for sound in instructions.sound_queue:
            sound.play()

        if instructions.new_music != None:
            self.change_music(instructions.new_music)


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

    def msg_screen(self, screen):
        surf = pygame.font.SysFont(self.font, self.size).render(
            self.msg, True, self.color
        )
        trect = surf.get_rect()
        trect.center = self.x, self.y
        screen.blit(surf, trect)


class GraphicsInstructions:
    def __init__(self):
        self.objects_to_render = []
        self.messages_to_display = []
        self.pause_rendering = False

    def msg_screen(self, msg: Message):
        self.messages_to_display.append(msg)

    def render_object(self, obj):
        self.objects_to_render.append(obj)


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
        if not instructions.pause_rendering:
            self.screen.fill((0, 0, 0))

        for obj in instructions.objects_to_render:
            self.render_object(obj)

        for msg in instructions.messages_to_display:
            msg.msg_screen(self.screen)

        pygame.display.update()


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

    def collision_check_ball_block(self, ball, block):
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

    def collision_check_ball_wall(self, ball):
        if ball.x < ball.radius and ball.x_vel < 0:
            ball.x_vel *= -1
        elif ball.x > self.constants.game_width - ball.radius and ball.x_vel > 0:
            ball.x_vel *= -1
        if ball.y < ball.radius and ball.y_vel < 0:
            ball.y_vel *= -1

    def collision_check_ball_paddle(self, ball, paddle):
        if ball.y >= paddle.y and ball.y <= paddle.y + paddle.height:
            if ball.x > paddle.x and ball.x < paddle.x + paddle.width:
                ball.y_vel *= -1
                ball.x_vel += paddle.x_vel / 20
                return True  # This should flag the paddle sound to be played

    def update_ball(self, ball, delta_t, audio_instructions):
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
            audio_instructions.queue_sound(audio_instructions.sounds.hit_sound)
        self.collision_check_ball_wall(ball)
        for block in self.blocks:
            if self.collision_check_ball_block(ball, block):
                audio_instructions.queue_sound(audio_instructions.sounds.block_sound)

    def update_game(self, delta_t, keys, audio_instructions):
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

    def update(self, delta_t, keys):
        audio_instructions = AudioInstructions()
        graphics_instructions = GraphicsInstructions()

        self.manage_screens(keys, audio_instructions, graphics_instructions)
        if self.game_screen == "play" or self.game_screen == "pause":
            if self.game_screen == "play":
                self.update_game(delta_t, keys, audio_instructions)
            self.game_objects_to_render(graphics_instructions)

        # Note: Win and lose checks in manage_screen_transitions

        return audio_instructions, graphics_instructions

    def game_objects_to_render(self, graphics_instructions: GraphicsInstructions):
        graphics_instructions.render_object(self.paddle)
        for ball in self.balls:
            graphics_instructions.render_object(ball)
        for block in self.blocks:
            graphics_instructions.render_object(block)

    def manage_screens(
        self,
        keys,
        audio_instructions: AudioInstructions,
        graphics_instructions: GraphicsInstructions,
    ):
        if self.game_screen == "play":
            if pygame.K_p in keys:
                self.game_screen == "pause"
            if len(self.balls) == 0:
                self.game_screen == "game over"
                audio_instructions.queue_music_change(
                    audio_instructions.music.game_over
                )
            if len(self.blocks) == 0:
                self.game_screen == "game win"
                audio_instructions.queue_sound(audio_instructions.sounds.win_sound)
                audio_instructions.queue_music_change(audio_instructions.music.victory)

        elif self.game_screen == "pause":
            if pygame.K_p in keys:
                self.game_screen == "play"
            graphics_instructions.msg_screen(
                Message(
                    "PAUSED",
                    50,
                    self.constants.game_width / 2,
                    self.constants.game_height / 2,
                )
            )
            graphics_instructions.msg_screen(
                Message(
                    "Press P to continue",
                    25,
                    self.constants.game_width / 2,
                    0.75 * self.constants.game_height,
                )
            )

        elif self.game_screen == "game win" or self.game_screen == "game over":
            if pygame.K_r in keys:
                audio_instructions.queue_music_change(
                    audio_instructions.music.game_play
                )
                self.initialize_game()
            if pygame.K_q in keys:
                self.game_exit = True
            if self.game_screen == "game over":
                graphics_instructions.msg_screen(
                    Message(
                        "GAME OVER",
                        50,
                        self.constants.game_width / 2,
                        self.constants.game_height / 2,
                    )
                )
                graphics_instructions.msg_screen(
                    Message(
                        "Press R to restart",
                        25,
                        self.constants.game_width / 2,
                        0.7 * self.constants.game_height,
                    )
                )
                graphics_instructions.msg_screen(
                    Message(
                        "Press Q to quit",
                        25,
                        self.constants.game_width / 2,
                        0.8 * self.constants.game_height,
                    )
                )
            else:
                graphics_instructions.msg_screen(
                    Message(
                        "YOU WIN",
                        50,
                        self.constants.game_width / 2,
                        self.constants.game_height / 2,
                    )
                )
                graphics_instructions.msg_screen(
                    Message(
                        "Press R to restart",
                        25,
                        self.constants.game_width / 2,
                        0.7 * self.constants.game_height,
                    )
                )
                graphics_instructions.msg_screen(
                    Message(
                        "Press Q to quit",
                        25,
                        self.constants.game_width / 2,
                        0.8 * self.constants.game_height,
                    )
                )
        elif self.game_screen == "menu":
            if pygame.K_p in keys:
                audio_instructions.queue_music_change(
                    audio_instructions.music.game_play
                )
                self.initialize_game()
            if pygame.K_q in keys:
                self.game_exit = True
            graphics_instructions.msg_screen(
                Message(
                    "Welcome to Breakout!",
                    50,
                    self.constants.game_width / 2,
                    self.constants.game_height / 2,
                )
            )
            graphics_instructions.msg_screen(
                Message(
                    "Press P to play",
                    25,
                    self.constants.game_width / 2,
                    0.7 * self.constants.game_height,
                )
            )
            graphics_instructions.msg_screen(
                Message(
                    "Press Q to quit",
                    25,
                    self.constants.game_width / 2,
                    0.8 * self.constants.game_height,
                )
            )

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
        keys = input_handler.get_keys()

        # N = 50
        # delta_t = total_delta_t / N
        # for i in range(N - 1):
        #     game.update(delta_t, keys)
        #
        # audio_instructions, graphics_instructions = game.update(total_delta_t, keys)

        # For some reason, doing the above completely kills the fps

        audio_instructions, graphics_instructions = game.update(total_delta_t, keys)
        game.check_quit(input_handler.quit)

        audio.run(audio_instructions)
        graphics.render(graphics_instructions)

        input_handler.handle_input()
        print(total_delta_t)


def main():
    pygame.init()
    pygame.display.set_caption("Breakout")
    GameLoop()
    pygame.quit()


if __name__ == "__main__":
    main()
