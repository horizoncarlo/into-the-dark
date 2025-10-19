class StartRendering(Exception):
    """Exception raised when a blocking overlay or other process is complete to start rendering the game loop"""


class StopRendering(Exception):
    """Exception raised when a blocking overlay or other process should stop rendering the game loop"""


class ImpossibleAction(Exception):
    """Exception raised when an action is impossible to be performed

    The reason is given in the exception message
    """
