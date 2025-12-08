"""
Character system for the card battler game.
Handles player and enemy entities with health, energy, and status effects.

This module defines the base Character class and specialized Player and Enemy
classes. Characters have HP, block, energy, and status effects that modify
their behavior during combat.
"""

from typing import List, Optional
from deck import Deck
from card import Card
from status_effects import StatusManager, CommonStatuses, StatusType


class Character:
    """
    Base class for characters (player and enemies).
    
    This class provides common functionality for all characters in combat:
    - Health points (HP) management
    - Block (temporary damage reduction)
    - Status effects (buffs/debuffs)
    - Damage calculation with modifiers
    - Turn lifecycle (start_turn, end_turn)
    
    Both Player and Enemy inherit from this class.
    """
    
    def __init__(self, name: str, max_hp: int, starting_block: int = 0):
        """
        Initialize a character with basic stats.
        
        Args:
            name: Display name of the character
            max_hp: Maximum health points
            starting_block: Initial block value (usually 0)
        """
        self.name = name  # Character's display name
        self.max_hp = max_hp  # Maximum health points
        self.current_hp = max_hp  # Current health points (starts at max)
        self.block = starting_block  # Current block (damage reduction)
        self.status_manager = StatusManager()  # Manages all status effects
        
        # Combat stats
        self.energy = 0  # Current energy (used to play cards)
        self.max_energy = 3  # Maximum energy per turn
        
        # Track damage dealt this turn (for effects like Flame Barrier that
        # trigger based on damage dealt)
        self.damage_dealt_this_turn = 0
    
    def take_damage(self, amount: int, ignore_block: bool = False) -> int:
        """
        Apply damage to this character, accounting for block and status effects.
        
        This method handles the damage calculation pipeline:
        1. Apply Vulnerable modifier (50% more damage if vulnerable)
        2. Reduce damage by current block
        3. Apply remaining damage to HP
        4. Update block (reduced by damage amount)
        
        Args:
            amount: Base damage amount to apply
            ignore_block: If True, bypass block entirely (for poison, etc.)
            
        Returns:
            Actual damage taken (after block reduction)
        """
        if ignore_block:
            # Bypass block (used for damage-over-time effects like poison)
            actual_damage = amount
        else:
            # Apply vulnerable modifier (50% more damage)
            vulnerable = self.status_manager.get_status_amount(CommonStatuses.VULNERABLE)
            if vulnerable > 0:
                amount = int(amount * 1.5)  # 50% increase
            
            # Block reduces damage
            if self.block >= amount:
                # Block completely absorbs damage
                self.block -= amount
                actual_damage = 0
            else:
                # Block partially absorbs damage
                actual_damage = amount - self.block
                self.block = 0  # Block is consumed
        
        # Apply damage to HP
        self.current_hp -= actual_damage
        # Ensure HP doesn't go below 0
        if self.current_hp < 0:
            self.current_hp = 0
        
        return actual_damage
    
    def gain_block(self, amount: int):
        """
        Gain block (temporary damage reduction).
        
        Block reduces incoming damage. It's modified by:
        - Frail status: Reduces block gained by 25%
        - Dexterity status: Adds flat block bonus
        
        Args:
            amount: Base block amount to gain
        """
        # Apply frail modifier (25% less block)
        frail = self.status_manager.get_status_amount(CommonStatuses.FRAIL)
        if frail > 0:
            amount = int(amount * 0.75)  # 25% reduction
        
        # Apply dexterity modifier (flat bonus)
        dexterity = self.status_manager.get_status_amount(CommonStatuses.DEXTERITY)
        amount += dexterity  # Add dexterity as flat bonus
        
        # Add block
        self.block += amount
    
    def heal(self, amount: int):
        """Heal the character."""
        self.current_hp = min(self.current_hp + amount, self.max_hp)
    
    def is_alive(self) -> bool:
        """Check if character is alive."""
        return self.current_hp > 0
    
    def get_hp_percentage(self) -> float:
        """Get HP as a percentage."""
        return self.current_hp / self.max_hp if self.max_hp > 0 else 0.0
    
    def start_turn(self):
        """Called at the start of a turn."""
        self.damage_dealt_this_turn = 0
        
        # Apply status effects that trigger at start of turn
        poison = self.status_manager.get_status_amount(CommonStatuses.POISON)
        if poison > 0:
            self.take_damage(poison, ignore_block=True)
            self.status_manager.add_status(CommonStatuses.POISON, -1)
    
    def end_turn(self):
        """Called at the end of a turn."""
        # Apply status effects that trigger at end of turn
        burn = self.status_manager.get_status_amount(CommonStatuses.BURN)
        if burn > 0:
            self.take_damage(burn, ignore_block=True)
            self.status_manager.add_status(CommonStatuses.BURN, -1)
        
        metallicize = self.status_manager.get_status_amount(CommonStatuses.METALLICIZE)
        if metallicize > 0:
            self.gain_block(metallicize)
        
        demon_form = self.status_manager.get_status_amount(CommonStatuses.DEMON_FORM)
        if demon_form > 0:
            self.status_manager.add_status(CommonStatuses.STRENGTH, 2)
        
        # Tick all status effects
        self.status_manager.tick_all()
        
        # Remove block unless barricade is active
        if not self.status_manager.has_status(CommonStatuses.BARRICADE):
            self.block = 0
    
    def get_damage_modifier(self) -> int:
        """Get damage modifier from strength."""
        return self.status_manager.get_status_amount(CommonStatuses.STRENGTH)
    
    def apply_damage_modifier(self, base_damage: int) -> int:
        """
        Apply damage modifiers to base damage.
        
        This method calculates the final damage after applying all modifiers:
        1. Add Strength (flat bonus)
        2. Apply Weak (25% reduction)
        
        Used when calculating damage dealt by attacks.
        
        Args:
            base_damage: Base damage before modifiers
            
        Returns:
            Final damage after all modifiers (never negative)
        """
        damage = base_damage
        
        # Apply strength (flat damage bonus)
        strength = self.get_damage_modifier()
        damage += strength
        
        # Apply weak modifier (25% less damage)
        weak = self.status_manager.get_status_amount(CommonStatuses.WEAK)
        if weak > 0:
            damage = int(damage * 0.75)  # 25% reduction
        
        # Ensure damage is never negative
        return max(0, damage)
    
    def to_dict(self) -> dict:
        """Convert character to dictionary for serialization."""
        return {
            'name': self.name,
            'max_hp': self.max_hp,
            'current_hp': self.current_hp,
            'block': self.block,
            'energy': self.energy,
            'max_energy': self.max_energy,
            'status_effects': self.status_manager.to_dict()
        }


class Player(Character):
    """
    Player character with deck management.
    
    Extends Character with player-specific functionality:
    - Deck management (drawing, playing cards)
    - Energy management (spending energy to play cards)
    - Card playing logic
    - Relics/passives (framework for future features)
    """
    
    def __init__(self, name: str = "Player", max_hp: int = 80, max_energy: int = 3):
        """
        Initialize player character.
        
        Args:
            name: Player's name (default: "Player")
            max_hp: Maximum health points (default: 80)
            max_energy: Maximum energy per turn (default: 3)
        """
        super().__init__(name, max_hp)
        self.max_energy = max_energy  # Maximum energy per turn
        self.energy = max_energy  # Current energy (starts at max)
        self.deck: Optional[Deck] = None  # Player's deck (set separately)
        self.starting_hand_size = 5  # Cards drawn at start of turn
        
        # Relics/passives (stretch feature - framework for passive abilities)
        self.relics: List[str] = []
    
    def set_deck(self, deck: Deck):
        """Set the player's deck."""
        self.deck = deck
    
    def start_combat(self):
        """Initialize for a new combat."""
        if self.deck:
            self.deck.reset_for_combat()
            self.deck.draw(self.starting_hand_size)
        self.energy = self.max_energy
        self.block = 0
    
    def start_turn(self):
        """Called at the start of player's turn."""
        super().start_turn()
        self.energy = self.max_energy
        
        # Draw cards
        if self.deck:
            cards_to_draw = 5  # Base draw
            # Could add card draw modifiers here
            self.deck.draw(cards_to_draw)
    
    def end_turn(self):
        """Called at the end of player's turn."""
        super().end_turn()
        if self.deck:
            self.deck.discard_hand()
    
    def play_card(self, card: Card, target: Optional[Character] = None) -> dict:
        """
        Play a card from the player's hand.
        
        This is the core method for playing cards. It:
        1. Validates the card can be played (in hand, enough energy)
        2. Spends energy
        3. Applies all card effects (damage, block, card draw, status effects)
        4. Moves card to discard pile
        5. Returns a result dictionary with all effects that occurred
        
        Args:
            card: The Card object to play
            target: Target character (for attacks/debuffs). If None, effects apply to self.
            
        Returns:
            Dictionary with 'success' (bool) and 'effects' (list of effect dicts)
        """
        # Validation: Check card is in hand
        if not self.deck or card not in self.deck.hand:
            return {'success': False, 'message': 'Card not in hand'}
        
        # Validation: Check enough energy
        if self.energy < card.get_cost():
            return {'success': False, 'message': 'Not enough energy'}
        
        result = {'success': True, 'effects': []}
        
        # Spend energy to play the card
        self.energy -= card.get_cost()
        
        # Get card effect values (these account for upgrades)
        damage = card.get_damage()
        block = card.get_block()
        
        # Apply damage if card deals damage
        if damage > 0:
            # Apply damage modifiers (strength, weak, etc.)
            actual_damage = self.apply_damage_modifier(damage)
            if target:
                # Deal damage to target
                damage_taken = target.take_damage(actual_damage)
                result['effects'].append({
                    'type': 'damage',
                    'target': target.name,
                    'amount': damage_taken
                })
                # Track damage dealt (for effects like Flame Barrier)
                self.damage_dealt_this_turn += actual_damage
        
        # Apply block if card provides block
        if block > 0:
            self.gain_block(block)
            result['effects'].append({
                'type': 'block',
                'amount': block,
                'actual_block': self.block  # Total block after gaining
            })
        
        # Apply energy gain if card provides energy
        if card.energy_gain > 0:
            self.energy += card.energy_gain
            result['effects'].append({
                'type': 'energy',
                'amount': card.energy_gain
            })
        
        # Apply card draw if card draws cards
        if card.card_draw > 0:
            drawn = self.deck.draw(card.card_draw)
            result['effects'].append({
                'type': 'draw',
                'cards': [c.name for c in drawn]
            })
        
        # Apply status effects from card
        for status_name, amount in card.status_effects.items():
            if target:
                # Apply status to target (for debuffs on attacks)
                target.status_manager.add_status(status_name, amount)
                result['effects'].append({
                    'type': 'status',
                    'target': target.name,
                    'status': status_name,
                    'amount': amount
                })
            else:
                # Apply to self (for powers and self-buffs)
                self.status_manager.add_status(status_name, amount)
                result['effects'].append({
                    'type': 'status',
                    'target': self.name,
                    'status': status_name,
                    'amount': amount
                })
        
        # Move card from hand to discard pile
        self.deck.discard_card(card)
        
        return result


class Enemy(Character):
    """
    Enemy character with AI behavior.
    
    Extends Character with enemy-specific functionality:
    - Intent system (what the enemy plans to do)
    - AI-driven actions
    - Intent execution
    
    Enemies use an "intent" system where they declare what they'll do,
    then execute it during their turn.
    """
    
    def __init__(self, name: str, max_hp: int, intent: str = "attack", 
                 damage: int = 0, block: int = 0):
        """
        Initialize enemy character.
        
        Args:
            name: Enemy's display name
            max_hp: Maximum health points
            intent: Initial intent type ("attack", "defend", "buff", "debuff")
            damage: Damage value for attack intents
            block: Block value for defend intents
        """
        super().__init__(name, max_hp)
        self.intent = intent  # Current intent: "attack", "defend", "buff", "debuff"
        self.intent_damage = damage  # Damage value for attack/buff/debuff intents
        self.intent_block = block  # Block value for defend intents
        self.intent_description = ""  # Human-readable description of intent
    
    def set_intent(self, intent: str, damage: int = 0, block: int = 0, description: str = ""):
        """Set the enemy's intent for this turn."""
        self.intent = intent
        self.intent_damage = damage
        self.intent_block = block
        self.intent_description = description
    
    def execute_intent(self, target: Character) -> dict:
        """
        Execute the enemy's declared intent.
        
        This method performs the action the enemy declared (via set_intent).
        Different intents do different things:
        - attack: Deal damage to target
        - defend: Gain block
        - buff: Apply buff to self (e.g., gain Strength)
        - debuff: Apply debuff to target (e.g., apply Vulnerable)
        
        Args:
            target: Target character (usually the player)
            
        Returns:
            Dictionary with 'effects' list describing what happened
        """
        result = {'effects': []}
        
        if self.intent == "attack":
            # Deal damage to target
            damage = self.apply_damage_modifier(self.intent_damage)
            actual_damage = target.take_damage(damage)
            result['effects'].append({
                'type': 'damage',
                'target': target.name,
                'amount': actual_damage
            })
        elif self.intent == "defend":
            # Gain block
            self.gain_block(self.intent_block)
            result['effects'].append({
                'type': 'block',
                'amount': self.intent_block,
                'actual_block': self.block
            })
        elif self.intent == "buff":
            # Apply buff to self (e.g., gain strength)
            self.status_manager.add_status(CommonStatuses.STRENGTH, self.intent_damage)
            result['effects'].append({
                'type': 'status',
                'target': self.name,
                'status': CommonStatuses.STRENGTH,
                'amount': self.intent_damage
            })
        elif self.intent == "debuff":
            # Apply debuff to target (e.g., apply vulnerable)
            target.status_manager.add_status(CommonStatuses.VULNERABLE, self.intent_damage)
            result['effects'].append({
                'type': 'status',
                'target': target.name,
                'status': CommonStatuses.VULNERABLE,
                'amount': self.intent_damage
            })
        
        return result
    
    def start_turn(self):
        """Called at the start of enemy's turn."""
        super().start_turn()
        # AI would determine intent here
        # For now, we'll use simple patterns
    
    def end_turn(self):
        """Called at the end of enemy's turn."""
        super().end_turn()

