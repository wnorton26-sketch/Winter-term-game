"""
Status effect system for the card battler game.
Handles buffs, debuffs, and persistent effects.
"""

from enum import Enum
from typing import Dict, Optional
from dataclasses import dataclass, field


class StatusType(Enum):
    """Types of status effects."""
    BUFF = "buff"
    DEBUFF = "debuff"
    NEUTRAL = "neutral"


@dataclass
class StatusEffect:
    """Represents a status effect."""
    name: str
    amount: int
    status_type: StatusType
    duration: int = -1  # -1 means permanent until removed
    description: str = ""
    
    def tick(self) -> bool:
        """Reduce duration by 1. Returns True if effect should be removed."""
        if self.duration > 0:
            self.duration -= 1
            return self.duration <= 0
        return False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'name': self.name,
            'amount': self.amount,
            'status_type': self.status_type.value,
            'duration': self.duration,
            'description': self.description
        }


class StatusManager:
    """Manages status effects for entities."""
    
    def __init__(self):
        self.effects: Dict[str, StatusEffect] = {}
    
    def add_status(self, name: str, amount: int, duration: int = -1, 
                   status_type: StatusType = StatusType.NEUTRAL, description: str = ""):
        """Add or stack a status effect."""
        if name in self.effects:
            # Stack the effect
            self.effects[name].amount += amount
            if duration > 0 and (self.effects[name].duration < 0 or duration < self.effects[name].duration):
                self.effects[name].duration = duration
        else:
            self.effects[name] = StatusEffect(
                name=name,
                amount=amount,
                status_type=status_type,
                duration=duration,
                description=description
            )
    
    def remove_status(self, name: str):
        """Remove a status effect."""
        if name in self.effects:
            del self.effects[name]
    
    def get_status(self, name: str) -> Optional[StatusEffect]:
        """Get a status effect by name."""
        return self.effects.get(name)
    
    def get_status_amount(self, name: str) -> int:
        """Get the amount of a status effect, or 0 if not present."""
        if name in self.effects:
            return self.effects[name].amount
        return 0
    
    def has_status(self, name: str) -> bool:
        """Check if entity has a status effect."""
        return name in self.effects
    
    def tick_all(self):
        """Tick all status effects, removing expired ones."""
        to_remove = []
        for name, effect in self.effects.items():
            if effect.tick():
                to_remove.append(name)
        for name in to_remove:
            del self.effects[name]
    
    def clear_all(self):
        """Clear all status effects."""
        self.effects.clear()
    
    def get_all(self) -> Dict[str, StatusEffect]:
        """Get all status effects."""
        return self.effects.copy()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {name: effect.to_dict() for name, effect in self.effects.items()}


# Common status effect definitions
class CommonStatuses:
    """Common status effects used in the game."""
    
    # Buffs
    STRENGTH = "strength"  # Increases damage dealt
    DEXTERITY = "dexterity"  # Increases block gained
    METALLICIZE = "metallicize"  # Gain block at end of turn
    BARRICADE = "barricade"  # Block doesn't expire
    DEMON_FORM = "demon_form"  # Gain strength each turn
    
    # Debuffs
    VULNERABLE = "vulnerable"  # Take 50% more damage
    WEAK = "weak"  # Deal 25% less damage
    FRAIL = "frail"  # Gain 25% less block
    
    # Enemy-specific
    POISON = "poison"  # Take damage at start of turn
    BURN = "burn"  # Take damage at end of turn

