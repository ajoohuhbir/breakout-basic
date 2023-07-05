import pygame


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
