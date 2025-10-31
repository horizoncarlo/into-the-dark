class ImpossibleAction(Exception):
    """Exception raised when an action is impossible to be performed

    The reason is given in the exception message
    """


class QuitWithoutSaving(SystemExit):
    """Can be raised to exit the game without automatically saving"""


class StartAttackHandler(Exception):
    """Disrupt our normal game loop to do the hero weapon attack process"""