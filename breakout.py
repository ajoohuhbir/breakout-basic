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

def draw_paddle(paddle_x, paddle_y, paddle_width = PADDLE_WIDTH, paddle_height = PADDLE_HEIGHT, paddle_color = PADDLE_COLOR):
    pygame.draw.rect(screen, paddle_color, [paddle_x, paddle_y, paddle_width, paddle_height])

def GameLoop():
    paddle_x = WIDTH//2
    paddle_y = 9*HEIGHT//10
    paddle_max_speed = 10
    moving_right = False
    moving_left = False

    game_exit = False
    
    while not game_exit:
        screen.fill((0,0,0))
        draw_paddle(paddle_x, paddle_y)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_exit = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    moving_left = True
                if event.key == pygame.K_d:
                    moving_right = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    moving_left = False
                if event.key == pygame.K_d:
                    moving_right = False
            

        if moving_right:
            paddle_x += paddle_max_speed
        elif moving_left:
            paddle_x -= paddle_max_speed




        pygame.display.update()
        clock.tick(fps)

GameLoop()
pygame.quit()
