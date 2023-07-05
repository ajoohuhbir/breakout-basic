import pygame


from GameState import GameState
from Graphics import Graphics
from Audio import Audio
from Inputs import KeyboardState


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
