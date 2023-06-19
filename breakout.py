import pygame
import random


pygame.init() # Random comment

clock = pygame.time.Clock()
fps = 60

RESOLUTION_HEIGHT = 600
RESOLUTION_WIDTH = 800
screen = pygame.display.set_mode((RESOLUTION_WIDTH, RESOLUTION_HEIGHT))
pygame.display.set_caption('Breakout')

GAME_HEIGHT = 600
GAME_WIDTH = 800

PADDLE_WIDTH = 100
PADDLE_HEIGHT = 10
PADDLE_COLOR = (255,255,255)

paddle_x = GAME_WIDTH/2 - PADDLE_WIDTH/2
paddle_y = 0.9*GAME_HEIGHT
paddle_x_vel = 0

user_impulse = 0
user_impulse_per_millisecond = 0.01
paddle_max_speed_per_millisecond = 1
air_resistance_coefficient = user_impulse_per_millisecond/paddle_max_speed_per_millisecond

gravity = 0.0002

last_movement_key_pressed = None

game_exit = False   # This should definitely be in the GameLoop but then "global game_exit" doesn't work


def draw_paddle(paddle_x, paddle_y, paddle_width = PADDLE_WIDTH, paddle_height = PADDLE_HEIGHT, paddle_color = PADDLE_COLOR):
    pygame.draw.rect(screen, paddle_color, [paddle_x, paddle_y, paddle_width, paddle_height])

class Ball:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.x_vel = random.uniform(-0.05, 0.05)
        self.y_vel = -0.28
        self.radius = 5
        self.color = (255,255,255)
    
    def update(self, delta_t):
        global game_state
        self.y_vel += gravity*delta_t
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
        
        if self.y > GAME_HEIGHT + 2*self.radius:
            game_state = "game over"
    
    def render(self): # It is somewhat clunky to deal with scaling here, instead of in render, but I don't have a cleaner solution
        pygame.draw.circle(screen, self.color, (scale_x(self.x), scale_y(self.y)), scale_y(self.radius))   
        # print("render got called!")

    def paddle_collision(self):
        if self.y >= paddle_y and self.y <= paddle_y + PADDLE_HEIGHT:
            if self.x > paddle_x and self.x < paddle_x + PADDLE_WIDTH:
                self.y_vel *= -1
                self.x_vel += paddle_x_vel/20
            
            # if self.x > paddle_x + 3*self.radius and self.x < paddle_x + PADDLE_WIDTH - 3*self.radius:
            #     self.y_vel *= -1
            # elif self.x < paddle_x + 3*self.radius and self.x > paddle_x - self.radius:
            #     self.y_vel *= -1
            #     self.x_vel += paddle_x_vel/4 if paddle_x_vel < 0 else 0
            # elif self.x > paddle_x + PADDLE_WIDTH - 3*self.radius and self.x < paddle_x + PADDLE_WIDTH + self.radius:
            #     self.y_vel *= -1
            #     self.x_vel += paddle_x_vel/4 if paddle_x_vel > 0 else 0

    def wall_collision(self):
        if self.x < self.radius and self.x_vel < 0:
            self.x_vel *= -1
        elif self.x > GAME_WIDTH - self.radius and self.x_vel > 0:
            self.x_vel *= -1
        if self.y < self.radius and self.y_vel < 0:
            self.y_vel *= -1
    
    def block_collision(self, block):
        if block.x - self.radius < self.x < block.x + block.width + self.radius and block.y - self.radius < self.y < block.y + block.height + self.radius:
            if self.y > block.y + block.height and self.y_vel < 0:
                self.y_vel *= -1
                blocks.remove(block)
            elif self.y < block.y and self.y_vel > 0:
                self.y_vel *= -1
                blocks.remove(block)
            elif self.x > block.x + block.width and self.x_vel < 0:
                self.x_vel *= -1
                blocks.remove(block)
            elif self.x < block.x and self.x_vel > 0:
                self.x_vel *= -1
                blocks.remove(block)


class Block:

    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.color = color
    
    def render(self):
        pygame.draw.rect(screen, self.color ,[scale_x(self.x), scale_y(self.y), scale_x(self.width), scale_y(self.height)])


def scale_x(x_coord):
    return (x_coord/GAME_WIDTH)*RESOLUTION_WIDTH

def scale_y(y_coord):
    return (y_coord/GAME_HEIGHT)*RESOLUTION_HEIGHT

def render():
    global paddle_x, paddle_y, balls #Is this a good idea? Or should they be passed into the render function?
    screen.fill((0,0,0))
    draw_paddle(scale_x(paddle_x), scale_y(paddle_y), scale_x(PADDLE_WIDTH), scale_y(PADDLE_HEIGHT))
    for ball in balls:
        ball.render()
    for block in blocks:
        block.render()
    pygame.display.update()

def update(delta_t):
    global paddle_x, paddle_y, paddle_x_vel, user_impulse_per_millisecond, last_movement_key_pressed, air_resistance_coefficient, balls
    if last_movement_key_pressed == 'A':
        impulse_sign = -1
    elif last_movement_key_pressed == 'D':
        impulse_sign = +1
    else:
        impulse_sign = 0
    
    paddle_x_vel += delta_t*(impulse_sign*user_impulse_per_millisecond - air_resistance_coefficient*paddle_x_vel)
    paddle_x += delta_t * paddle_x_vel

    if paddle_x > GAME_WIDTH - PADDLE_WIDTH:
        paddle_x = GAME_WIDTH - PADDLE_WIDTH
    elif paddle_x < 0:
        paddle_x = 0

    for ball in balls:
        ball.update(delta_t)

def handle_input():
    global game_exit, last_movement_key_pressed, game_state
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_exit = True
        if game_state == "play": 
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    last_movement_key_pressed = 'A'
                if event.key == pygame.K_d:
                    last_movement_key_pressed = 'D'
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a and last_movement_key_pressed == 'A':
                    last_movement_key_pressed = None
                if event.key == pygame.K_d and last_movement_key_pressed == 'D':
                    last_movement_key_pressed = None
        elif game_state == "game over":
             if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    restart()
        elif game_state == "game win":
             if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    restart()                   

def msg_screen(msg, x, y, color = (255,255,255), size = 25, font = "arial"):
    surf = pygame.font.SysFont(font, size).render(msg, True, color)
    trect = surf.get_rect()
    trect.center = x,y
    screen.blit(surf, trect)

def restart():
    global game_state, paddle_x, balls, paddle_x_vel, blocks, last_movement_key_pressed
    balls = [Ball(GAME_WIDTH/2, paddle_y - 20)]
    paddle_x = GAME_WIDTH/2 - PADDLE_WIDTH/2
    paddle_x_vel = 0
    blocks = []
    for i in range(8):
        for j in range(4):
            blocks.append(Block(100*i + 2, 50*j +2, 95, 45, tuple((random.randint(0, 255) for i in range(3)))))
    last_movement_key_pressed = None
    game_state = "play"


balls = [Ball(GAME_WIDTH/2, paddle_y - 20)]  # this should DEFINITELY not be global
blocks = []
for i in range(8):
    for j in range(4):
        blocks.append(Block(100*i + 2, 50*j +2, 95, 45, tuple((random.randint(0, 255) for i in range(3)))))

game_state = "play"

def GameLoop():

    global game_state

    while not game_exit:
        while game_state == "game over" and not game_exit:
            screen.fill((0,0,0))
            msg_screen("GAME OVER", RESOLUTION_WIDTH/2, RESOLUTION_HEIGHT/2)
            msg_screen("Press R to restart", RESOLUTION_WIDTH/2, 0.6*RESOLUTION_HEIGHT)
            handle_input()
            pygame.display.update()
            clock.tick(fps)
        
        while game_state == "game win" and not game_exit:
            screen.fill((0,0,0))
            msg_screen("YOU WIN!", RESOLUTION_WIDTH/2, RESOLUTION_HEIGHT/2)
            msg_screen("Press R to restart", RESOLUTION_WIDTH/2, 0.6*RESOLUTION_HEIGHT)
            handle_input()
            pygame.display.update()
            clock.tick(fps)        

        render()
        handle_input()

        total_delta_t = clock.get_time()
        N = 50
        for i in range(N):
            update(total_delta_t/N)
        
        if len(blocks) == 0:
            game_state = "game win"
        
        clock.tick(fps)



GameLoop()
pygame.quit()
