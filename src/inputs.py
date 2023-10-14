import pygame

# This module deals with user input
# Will be expanded upon when more input methods are added
# Right now it supports only keyboard input

# Holds which keys have been pressed
class KeyboardState:
    def __init__(self):
        # To distnguish between a key being pressed and a key remaining pressed
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
                # Technically a KEYUP key must always be in currently pressed keys, but just in case it is not, I added this check
                if (
                    event.key in self.currently_pressed_keys
                ):
                    self.currently_pressed_keys.remove(event.key)
            # Quits the game when the 'cross' button in pressed on the window
            # Technically this should not be handled by keyboard state
            # But right now it is the only class in inputs
            # This will later probably be the responsibility of an Inputs class that handles multiple kinds of inputs
            elif event.type == pygame.QUIT:
                self.quit = True

    # Keys that are currently down
    def get_keys(self):
        return self.currently_pressed_keys.union(self.new_keys_pressed)
