"""
Модуль интервального повторения для Armenian Learning Bot.

Реализует алгоритм SuperMemo-2 для оптимального запоминания слов.
"""

"""Spaced repetition package."""

__all__ = ["register_srs_handlers", "SRSStates"]

def __getattr__(name):
    if name == "register_srs_handlers":
        from .handlers import register_srs_handlers
        return register_srs_handlers
    if name == "SRSStates":
        from .states import SRSStates
        return SRSStates
    raise AttributeError(name)
