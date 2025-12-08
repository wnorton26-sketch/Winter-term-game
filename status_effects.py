"""
Status effect system for the card battler game.
Handles buffs, debuffs, and persistent effects.

Status effects are temporary or permanent modifiers that affect characters
during combat. Examples include Strength (increases damage), Vulnerable
(increases damage taken), Poison (damage over time), etc.
"""

from enum import Enum
from typing import Dict, Optional
from dataclasses import dataclass, field


class StatusType(Enum):
    """
    Enumeration of status effect types.
    
    Used to categorize status effects:
    - BUFF: Positive effects (Strength, Dexterity, etc.)
    - DEBUFF: Negative effects (Vulnerable, Weak, Poison, etc.)
    - NEUTRAL: Effects that are neither clearly positive nor negative
    """
    BUFF = "buff"      # Positive effects
    DEBUFF = "debuff"  # Negative effects
    NEUTRAL = "neutral"  # Neutral effects


@dataclass
class StatusEffect:
    """
    Represents a single status effect applied to a character.
    
    Status effects modify character behavior and stats. They can have
    a duration (temporary) or be permanent until removed. The amount
    field typically represents the intensity of the effect (e.g., amount
    of Strength, stacks of Poison, etc.).
    
    Attributes:
        name: Unique identifier for the status effect
        amount: Intensity/value of the effect (can stack)
        status_type: Whether it's a buff, debuff, or neutral
        duration: Number of turns remaining (-1 = permanent)
        description: Human-readable description of the effect
    """
    name: str  # Unique identifier (e.g., "strength", "vulnerable")
    amount: int  # Intensity/value (can be stacked)
    status_type: StatusType  # BUFF, DEBUFF, or NEUTRAL
    duration: int = -1  # -1 means permanent until removed, >0 means temporary
    description: str = ""  # Human-readable description
    
    def tick(self) -> bool:
        """
        Reduce duration by 1 turn. Called at end of each turn.
        
        If duration is positive, decrements it. Returns True if the
        effect should be removed (duration reached 0). Permanent effects
        (duration = -1) never expire.
        
        Returns:
            True if effect should be removed, False otherwise
        """
        if self.duration > 0:
            self.duration -= 1
            return self.duration <= 0  # Remove if duration reached 0
        return False  # Permanent effects (duration = -1) never expire
    
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
    """
    Manages status effects for a character (player or enemy).
    
    Each character has a StatusManager that tracks all active status effects.
    Status effects can stack (additive) and have durations. The manager
    handles adding, removing, querying, and ticking status effects.
    """
    
    def __init__(self):
        """
        Initialize an empty status manager.
        
        Creates a dictionary to store status effects by name. Each character
        (player or enemy) has its own StatusManager instance.
        """
        # Dictionary mapping status name to StatusEffect object
        self.effects: Dict[str, StatusEffect] = {}
    
    def add_status(self, name: str, amount: int, duration: int = -1, 
                   status_type: StatusType = StatusType.NEUTRAL, description: str = ""):
        """
        Add or stack a status effect.
        
        If the status already exists, stacks the amount (additive). If it's
        a new status, creates a new StatusEffect. Duration is updated if the
        new duration is shorter (for temporary effects).
        
        Args:
            name: Status effect name (e.g., "strength", "vulnerable")
            amount: Amount to add (stacks with existing)
            duration: Duration in turns (-1 = permanent)
            status_type: Type of status (BUFF, DEBUFF, NEUTRAL)
            description: Human-readable description
        """
        if name in self.effects:
            # Status already exists - stack the amount
            self.effects[name].amount += amount
            # Update duration if new duration is shorter (for temporary effects)
            if duration > 0 and (self.effects[name].duration < 0 or duration < self.effects[name].duration):
                self.effects[name].duration = duration
        else:
            # New status effect - create it
            self.effects[name] = StatusEffect(
                name=name,
                amount=amount,
                status_type=status_type,
                duration=duration,
                description=description
            )
    
    def remove_status(self, name: str):
        """
        Remove a status effect completely.
        
        Args:
            name: Name of the status effect to remove
        """
        if name in self.effects:
            del self.effects[name]
    
    def get_status(self, name: str) -> Optional[StatusEffect]:
        """
        Get a status effect object by name.
        
        Args:
            name: Name of the status effect
            
        Returns:
            StatusEffect object if found, None otherwise
        """
        return self.effects.get(name)
    
    def get_status_amount(self, name: str) -> int:
        """
        Get the amount/value of a status effect, or 0 if not present.
        
        This is the most commonly used method - it returns the numeric
        value of a status (e.g., how much Strength, how many stacks of
        Poison, etc.). Returns 0 if the status doesn't exist.
        
        Args:
            name: Name of the status effect
            
        Returns:
            Amount/value of the status, or 0 if not present
        """
        if name in self.effects:
            return self.effects[name].amount
        return 0
    
    def has_status(self, name: str) -> bool:
        """
        Check if the entity has a specific status effect (regardless of amount).
        
        Args:
            name: Name of the status effect to check
            
        Returns:
            True if status exists, False otherwise
        """
        return name in self.effects
    
    def tick_all(self):
        """
        Tick all status effects, removing expired ones.
        
        Called at the end of each turn. Reduces duration of all temporary
        effects and removes those that have expired (duration reached 0).
        Permanent effects (duration = -1) are not affected.
        """
        to_remove = []
        # Check all effects and mark expired ones for removal
        for name, effect in self.effects.items():
            if effect.tick():  # Returns True if expired
                to_remove.append(name)
        # Remove expired effects
        for name in to_remove:
            del self.effects[name]
    
    def clear_all(self):
        """
        Clear all status effects immediately.
        
        Used when combat ends or for special effects that remove all statuses.
        """
        self.effects.clear()
    
    def get_all(self) -> Dict[str, StatusEffect]:
        """
        Get all status effects as a dictionary.
        
        Returns a copy so modifications don't affect the internal state.
        
        Returns:
            Dictionary mapping status names to StatusEffect objects
        """
        return self.effects.copy()
    
    def to_dict(self) -> Dict:
        """
        Convert all status effects to dictionary for serialization.
        
        Used for saving game state or sending data to frontends.
        
        Returns:
            Dictionary containing all status effects as nested dicts
        """
        return {name: effect.to_dict() for name, effect in self.effects.items()}


# Common status effect definitions
class CommonStatuses:
    """
    Constants for common status effect names used throughout the game.
    
    This class provides string constants for status effect names to avoid
    typos and make code more maintainable. These are the actual status names
    used in the game logic.
    
    Usage:
        status_manager.add_status(CommonStatuses.STRENGTH, 2)
        strength_amount = status_manager.get_status_amount(CommonStatuses.STRENGTH)
    """
    
    # Buffs - Positive status effects
    STRENGTH = "strength"  # Increases damage dealt by the character
    DEXTERITY = "dexterity"  # Increases block gained by the character
    METALLICIZE = "metallicize"  # Gain block at end of turn (passive defense)
    BARRICADE = "barricade"  # Block doesn't expire at start of turn (persistent block)
    DEMON_FORM = "demon_form"  # Gain strength each turn (scaling power)
    
    # Debuffs - Negative status effects
    VULNERABLE = "vulnerable"  # Take 50% more damage from attacks
    WEAK = "weak"  # Deal 25% less damage with attacks
    FRAIL = "frail"  # Gain 25% less block from cards
    
    # Damage over time effects
    POISON = "poison"  # Take damage at start of turn (damage over time)
    BURN = "burn"  # Take damage at end of turn (damage over time)

