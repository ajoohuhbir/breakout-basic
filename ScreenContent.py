from Context import GameFsmState
from Graphics import Message
from Settings import SettingsState, Constants


def screen_content(
    game_fsm_state: GameFsmState, settings_state: SettingsState = None
) -> list[Message]:
    answer = []
    if game_fsm_state == GameFsmState.MENU:
        answer.append(
            Message(
                "Welcome to Breakout!",
                50,
                Constants.game_width / 2,
                0.3 * Constants.game_height,
            )
        )
        answer.append(
            Message(
                "Press P to play",
                25,
                Constants.game_width / 2,
                0.5 * Constants.game_height,
            )
        )
        answer.append(
            Message(
                "Press I for instructions",
                25,
                Constants.game_width / 2,
                0.6 * Constants.game_height,
            )
        )
        answer.append(
            Message(
                "Press S for settings",
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
                    SettingsState.possible_resolutions[settings_state.temp_resolution][
                        0
                    ],
                    SettingsState.possible_resolutions[settings_state.temp_resolution][
                        1
                    ],
                ),
                25,
                Constants.game_width / 2,
                0.4 * Constants.game_height,
            )
        )
        answer.append(
            Message(
                "FPS              :             {}".format(settings_state.temp_fps),
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
    elif game_fsm_state == GameFsmState.PRE_PLAY:
        answer.append(
            Message(
                "Press L to launch",
                25,
                Constants.game_width / 2,
                0.8 * Constants.game_height,
            )
        )

    return answer
