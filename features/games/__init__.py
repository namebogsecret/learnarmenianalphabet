"""
Модуль игр для Armenian Learning Bot.
"""
"""Game module package."""

__all__ = ["GameStates", "cmd_games", "register_games_handlers"]

def __getattr__(name):
    if name == "GameStates":
        from .states import GameStates
        return GameStates
    if name == "cmd_games":
        from .handlers import cmd_games
        return cmd_games
    if name == "register_games_handlers":
        from .handlers import register_games_handlers
        return register_games_handlers
    raise AttributeError(name)
