import pygame


pygame.init()

clock = pygame.time.Clock()
fps = 30

HEIGHT = 600
WIDTH = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Breakout')

PADDLE_WIDTH = 80
PADDLE_HEIGHT = 5
PADDLE_COLOR = (255,255,255)

paddle_x = WIDTH//2
paddle_y = 9*HEIGHT//10
paddle_x_vel = 0

user_impulse = 0
user_impulse_per_millisecond = 10
paddle_max_speed_per_millisecond = 0.25
air_resistance_coefficient = user_impulse_per_millisecond/paddle_max_speed_per_millisecond

last_movement_key_pressed = None

game_exit = False   # This should definitely be in the GameLoop but then "global game_exit" doesn't work


def draw_paddle(paddle_x, paddle_y, paddle_width = PADDLE_WIDTH, paddle_height = PADDLE_HEIGHT, paddle_color = PADDLE_COLOR):
    pygame.draw.rect(screen, paddle_color, [paddle_x, paddle_y, paddle_width, paddle_height])

def render():
    global paddle_x, paddle_y #Is this a good idea? Or should they be passed into the render function?
    screen.fill((0,0,0))
    draw_paddle(paddle_x, paddle_y)
    pygame.display.update()
    
    # Right now this isn't unit-agnostic, but later all the "matching-to-actual-pixels" should be here in the render()

def update(delta_t):
    global paddle_x, paddle_y, paddle_x_vel, user_impulse_per_millisecond, last_movement_key_pressed, air_resistance_coefficient
    if last_movement_key_pressed == 'A':
        impulse_sign = 1
    elif last_movement_key_pressed == 'D':
        impulse_sign = -1
    else:
        impulse_sign = 0
    
    paddle_x_vel += delta_t*(impulse_sign*user_impulse_per_millisecond - air_resistance_coefficient*paddle_x_vel)
    paddle_x += delta_t * paddle_x_vel

def handle_input():
    global game_exit, last_movement_key_pressed
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_exit = True
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


def GameLoop():

    clock.tick()
    
    while not game_exit:


        render()
        handle_input()

        update(clock.get_time())

        clock.tick(fps)



GameLoop()
pygame.quit()
