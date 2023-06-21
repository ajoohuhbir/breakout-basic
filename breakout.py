import pygame
import random

user_impulse = 0
user_impulse_per_millisecond = 0.01

last_movement_key_pressed = None
game_exit = False


class Constants:
    def __init__(self):
        self.game_width = 800
        self.game_height = 600
        self.gravity = 0.0002
        self.air_resistance_coefficient = 0.01


class Settings:
    def __init__(self):
        self.fps = 60
        self.resolution = [800, 600]


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
        self.player = pygame.mixer.music
        self.player.load(self.music.menu)

    def change_music(self, music):
        self.player.unload()
        self.player.load(music)
        self.player.play()

    def run(self, instructions: AudioInstructions):
        for sound in instructions.sound_queue:
            sound.play()

        if instructions.new_music != None:
            self.change_music(self.music_instruction)


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

    def msg_screen(self):
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

    def msg_screen(self, msg: Message):
        self.messages_to_display.append(msg)

    def render_object(self, obj):
        self.objects_to_render.append(obj)


class Graphics:  # Does not yet support different resolutions
    def __init__(self, resolution_width, resolution_height):
        self.screen = pygame.display.set_mode((resolution_width, resolution_height))
        self.paddle_color = (255, 255, 255)

    def render_paddle(self, paddle):
        pygame.draw.rect(
            self.screen,
            self.paddle_color,
            [paddle.x, paddle.y, paddle.width, paddle.height],
        )

    def render_block(self, block):
        pygame.draw.rect(
            self.screen,
            block,
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

        for obj in instructions.objects_to_render:
            self.render_object(obj)

        for msg in instructions.messages_to_display:
            msg.msg_screen()

        pygame.display.update()


class Paddle:
    def __init__(self, x, y, height, width):
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
        self.y_vel = -0.28
        self.radius = 5
        self.color = (255, 255, 255)

    def update(self, delta_t):
        global game_screen
        self.y_vel += gravity * delta_t
        if self.x_vel > 0.1:
            self.x_vel = 0.1
        elif self.x_vel < -0.1:
            self.x_vel = -0.1

        self.y += self.y_vel
        self.x += self.x_vel
        self.paddle_collision()
        self.wall_collision()
        for block in blocks:
            self.block_collision(block)

        if self.y > GAME_HEIGHT + 2 * self.radius:
            music_player.unload()
            music_player.load("game over.mp3")
            music_player.play()

            game_screen = "game over"

    def paddle_collision(self):
        if self.y >= paddle_y and self.y <= paddle_y + PADDLE_HEIGHT:
            if self.x > paddle_x and self.x < paddle_x + PADDLE_WIDTH:
                self.y_vel *= -1
                self.x_vel += paddle_x_vel / 20
                hit_sound.play()

    def wall_collision(self):
        if self.x < self.radius and self.x_vel < 0:
            self.x_vel *= -1
        elif self.x > GAME_WIDTH - self.radius and self.x_vel > 0:
            self.x_vel *= -1
        if self.y < self.radius and self.y_vel < 0:
            self.y_vel *= -1

    def block_collision(self, block):
        if (
            block.x - self.radius < self.x < block.x + block.width + self.radius
            and block.y - self.radius < self.y < block.y + block.height + self.radius
        ):
            if self.y > block.y + block.height and self.y_vel < 0:
                self.y_vel *= -1
                blocks.remove(block)
                block_sound.play()
            elif self.y < block.y and self.y_vel > 0:
                self.y_vel *= -1
                blocks.remove(block)
                block_sound.play()
            elif self.x > block.x + block.width and self.x_vel < 0:
                self.x_vel *= -1
                blocks.remove(block)
                block_sound.play()
            elif self.x < block.x and self.x_vel > 0:
                self.x_vel *= -1
                blocks.remove(block)
                block_sound.play()


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
                    self.new_keys_pressed.remove(event.key)
            elif event.type == pygame.QUIT:
                self.quit = True

    def get_keys(self):
        return self.currently_pressed_keys.extend(self.new_keys_pressed)


def update(delta_t):
    global paddle_x, paddle_y, paddle_x_vel, user_impulse_per_millisecond, last_movement_key_pressed, air_resistance_coefficient, balls
    if last_movement_key_pressed == "A":
        impulse_sign = -1
    elif last_movement_key_pressed == "D":
        impulse_sign = +1
    else:
        impulse_sign = 0

    paddle_x_vel += delta_t * (
        impulse_sign * user_impulse_per_millisecond
        - air_resistance_coefficient * paddle_x_vel
    )
    paddle_x += delta_t * paddle_x_vel

    if paddle_x > GAME_WIDTH - PADDLE_WIDTH:
        paddle_x = GAME_WIDTH - PADDLE_WIDTH
    elif paddle_x < 0:
        paddle_x = 0

    for ball in balls:
        ball.update(delta_t)


def handle_input():
    global game_exit, last_movement_key_pressed, game_screen
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_exit = True
        if game_screen == "play":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    last_movement_key_pressed = "A"
                if event.key == pygame.K_d:
                    last_movement_key_pressed = "D"
                if event.key == pygame.K_p:
                    game_screen = "pause"
                    msg_screen("PAUSED", RESOLUTION_WIDTH / 2, RESOLUTION_HEIGHT / 2)
                    msg_screen(
                        "Press P to unpause",
                        RESOLUTION_WIDTH / 2,
                        0.6 * RESOLUTION_HEIGHT,
                    )
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a and last_movement_key_pressed == "A":
                    last_movement_key_pressed = None
                if event.key == pygame.K_d and last_movement_key_pressed == "D":
                    last_movement_key_pressed = None
        elif game_screen == "game over" or game_screen == "game win":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    restart()
                if event.key == pygame.K_q:
                    game_exit = True
        elif game_screen == "menu":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    restart()
                if event.key == pygame.K_q:
                    game_exit = True
                if event.key == pygame.K_i:
                    game_screen = "instructions"
        elif game_screen == "instructions":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    game_screen = "menu"
        elif game_screen == "pause":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    clock.tick()
                    game_screen = "play"


def restart():
    global game_screen, paddle_x, balls, paddle_x_vel, blocks, last_movement_key_pressed
    balls = [Ball(GAME_WIDTH / 2, paddle_y - 20)]
    paddle_x = GAME_WIDTH / 2 - PADDLE_WIDTH / 2
    paddle_x_vel = 0
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
    last_movement_key_pressed = None

    music_player.unload()
    music_player.load("music.mp3")
    music_player.play()
    start_sound.play()
    clock.tick()
    game_screen = "play"


def OldGameLoop():
    global game_screen
    clock = pygame.time.clock()

    clock.tick()

    while not game_exit:
        while game_screen == "instructions" and not game_exit:
            screen.fill((0, 0, 0))
            msg_screen("Instructions: ", RESOLUTION_WIDTH / 2, 0.1 * RESOLUTION_HEIGHT)
            msg_screen(
                "Press A and D to move your paddle and P to pause",
                RESOLUTION_WIDTH / 2,
                0.3 * RESOLUTION_HEIGHT,
            )
            msg_screen(
                "Hit the ball and try to break all the blocks",
                RESOLUTION_WIDTH / 2,
                0.5 * RESOLUTION_HEIGHT,
            )
            msg_screen(
                "If the ball falls, you lose",
                RESOLUTION_WIDTH / 2,
                0.7 * RESOLUTION_HEIGHT,
            )
            msg_screen(
                "Press M to return to the Menu",
                RESOLUTION_WIDTH / 2,
                0.9 * RESOLUTION_HEIGHT,
            )
            handle_input()
            pygame.display.update()
            clock.tick(fps)

        while game_screen == "menu" and not game_exit:
            screen.fill((0, 0, 0))
            msg_screen(
                "Welcome to Breakout!", RESOLUTION_WIDTH / 2, RESOLUTION_HEIGHT / 2
            )
            msg_screen("Press P to Play", RESOLUTION_WIDTH / 2, 0.6 * RESOLUTION_HEIGHT)
            msg_screen(
                "Press I for Instructions",
                RESOLUTION_WIDTH / 2,
                0.7 * RESOLUTION_HEIGHT,
            )
            msg_screen("Press Q to Exit", RESOLUTION_WIDTH / 2, 0.8 * RESOLUTION_HEIGHT)
            handle_input()
            pygame.display.update()
            clock.tick(fps)

        while game_screen == "game over" and not game_exit:
            screen.fill((0, 0, 0))
            msg_screen("GAME OVER", RESOLUTION_WIDTH / 2, RESOLUTION_HEIGHT / 2)
            msg_screen(
                "Press R to restart", RESOLUTION_WIDTH / 2, 0.6 * RESOLUTION_HEIGHT
            )
            msg_screen("Press Q to Exit", RESOLUTION_WIDTH / 2, 0.7 * RESOLUTION_HEIGHT)
            handle_input()
            pygame.display.update()
            clock.tick(fps)

        while game_screen == "game win" and not game_exit:
            screen.fill((0, 0, 0))
            msg_screen("YOU WIN!", RESOLUTION_WIDTH / 2, RESOLUTION_HEIGHT / 2)
            msg_screen(
                "Press R to restart", RESOLUTION_WIDTH / 2, 0.6 * RESOLUTION_HEIGHT
            )
            msg_screen("Press Q to Exit", RESOLUTION_WIDTH / 2, 0.7 * RESOLUTION_HEIGHT)
            handle_input()
            pygame.display.update()
            clock.tick(fps)

        while game_screen == "play" and not game_exit:
            render()
            handle_input()

            total_delta_t = clock.get_time()
            N = 50
            for i in range(N):
                update(total_delta_t / N)

            if len(blocks) == 0:
                win_sound.play()
                music_player.unload()
                music_player.load("win music.mp3")
                music_player.play()
                game_screen = "game win"

            clock.tick(fps)

        while game_screen == "pause" and not game_exit:
            handle_input()
            pygame.display.update()
            clock.tick(fps)


def GameLoop():
    game_screen = "menu"

    while not game_exit:
        pass


def main():
    pygame.init()
    pygame.display.set_caption("Breakout")
    GameLoop()
    pygame.quit()


if __name__ == "__main__":
    main()
