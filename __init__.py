"""
Card Battler - Slay the Spire Lite
A Python-based card battler game that can be integrated with Godot.
"""

from game import Game
from card import Card, CardLibrary, CardType, CardRarity
from deck import Deck
from character import Player, Enemy, Character
from combat import Combat, CombatState, EncounterGenerator
from status_effects import StatusManager, StatusEffect, CommonStatuses, StatusType
from godot_integration import GodotGameBridge, get_game_bridge, create_http_api

__version__ = "1.0.0"
__all__ = [
    'Game',
    'Card',
    'CardLibrary',
    'CardType',
    'CardRarity',
    'Deck',
    'Player',
    'Enemy',
    'Character',
    'Combat',
    'CombatState',
    'EncounterGenerator',
    'StatusManager',
    'StatusEffect',
    'CommonStatuses',
    'StatusType',
    'GodotGameBridge',
    'get_game_bridge',
    'create_http_api'
]

