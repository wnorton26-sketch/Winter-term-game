"""
Character system for the card battler game.
Handles player and enemy entities with health, energy, and status effects.
"""

from typing import List, Optional
from deck import Deck
from card import Card
from status_effects import StatusManager, CommonStatuses, StatusType


class Character:
    """Base class for characters (player and enemies)."""
    
    def __init__(self, name: str, max_hp: int, starting_block: int = 0):
        """Initialize a character."""
        self.name = name
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.block = starting_block
        self.status_manager = StatusManager()
        
        # Combat stats
        self.energy = 0
        self.max_energy = 3
        
        # Track damage dealt this turn (for effects like Flame Barrier)
        self.damage_dealt_this_turn = 0
    
    def take_damage(self, amount: int, ignore_block: bool = False) -> int:
        """Take damage, accounting for block. Returns actual damage taken."""
        if ignore_block:
            actual_damage = amount
        else:
            # Apply vulnerable modifier (50% more damage)
            vulnerable = self.status_manager.get_status_amount(CommonStatuses.VULNERABLE)
            if vulnerable > 0:
                amount = int(amount * 1.5)
            
            # Block reduces damage
            if self.block >= amount:
                self.block -= amount
                actual_damage = 0
            else:
                actual_damage = amount - self.block
                self.block = 0
        
        self.current_hp -= actual_damage
        if self.current_hp < 0:
            self.current_hp = 0
        
        return actual_damage
    
    def gain_block(self, amount: int):
        """Gain block."""
        # Apply frail modifier (25% less block)
        frail = self.status_manager.get_status_amount(CommonStatuses.FRAIL)
        if frail > 0:
            amount = int(amount * 0.75)
        
        # Apply dexterity modifier
        dexterity = self.status_manager.get_status_amount(CommonStatuses.DEXTERITY)
        amount += dexterity
        
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
        """Apply damage modifiers to base damage."""
        damage = base_damage
        
        # Apply strength
        strength = self.get_damage_modifier()
        damage += strength
        
        # Apply weak modifier (25% less damage)
        weak = self.status_manager.get_status_amount(CommonStatuses.WEAK)
        if weak > 0:
            damage = int(damage * 0.75)
        
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
    """Player character with deck management."""
    
    def __init__(self, name: str = "Player", max_hp: int = 80, max_energy: int = 3):
        """Initialize player."""
        super().__init__(name, max_hp)
        self.max_energy = max_energy
        self.energy = max_energy
        self.deck: Optional[Deck] = None
        self.starting_hand_size = 5
        
        # Relics/passives (stretch feature)
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
        """Play a card. Returns result dictionary."""
        if not self.deck or card not in self.deck.hand:
            return {'success': False, 'message': 'Card not in hand'}
        
        if self.energy < card.get_cost():
            return {'success': False, 'message': 'Not enough energy'}
        
        result = {'success': True, 'effects': []}
        
        # Spend energy
        self.energy -= card.get_cost()
        
        # Apply card effects
        damage = card.get_damage()
        block = card.get_block()
        
        if damage > 0:
            # Apply damage modifiers
            actual_damage = self.apply_damage_modifier(damage)
            if target:
                damage_taken = target.take_damage(actual_damage)
                result['effects'].append({
                    'type': 'damage',
                    'target': target.name,
                    'amount': damage_taken
                })
                self.damage_dealt_this_turn += actual_damage
        
        if block > 0:
            self.gain_block(block)
            result['effects'].append({
                'type': 'block',
                'amount': block,
                'actual_block': self.block
            })
        
        if card.energy_gain > 0:
            self.energy += card.energy_gain
            result['effects'].append({
                'type': 'energy',
                'amount': card.energy_gain
            })
        
        if card.card_draw > 0:
            drawn = self.deck.draw(card.card_draw)
            result['effects'].append({
                'type': 'draw',
                'cards': [c.name for c in drawn]
            })
        
        # Apply status effects from card
        for status_name, amount in card.status_effects.items():
            if target:
                target.status_manager.add_status(status_name, amount)
                result['effects'].append({
                    'type': 'status',
                    'target': target.name,
                    'status': status_name,
                    'amount': amount
                })
            else:
                # Apply to self (for powers)
                self.status_manager.add_status(status_name, amount)
                result['effects'].append({
                    'type': 'status',
                    'target': self.name,
                    'status': status_name,
                    'amount': amount
                })
        
        # Move card to discard pile
        self.deck.discard_card(card)
        
        return result


class Enemy(Character):
    """Enemy character with AI behavior."""
    
    def __init__(self, name: str, max_hp: int, intent: str = "attack", 
                 damage: int = 0, block: int = 0):
        """Initialize enemy."""
        super().__init__(name, max_hp)
        self.intent = intent  # "attack", "defend", "buff", "debuff"
        self.intent_damage = damage
        self.intent_block = block
        self.intent_description = ""
    
    def set_intent(self, intent: str, damage: int = 0, block: int = 0, description: str = ""):
        """Set the enemy's intent for this turn."""
        self.intent = intent
        self.intent_damage = damage
        self.intent_block = block
        self.intent_description = description
    
    def execute_intent(self, target: Character) -> dict:
        """Execute the enemy's intent."""
        result = {'effects': []}
        
        if self.intent == "attack":
            damage = self.apply_damage_modifier(self.intent_damage)
            actual_damage = target.take_damage(damage)
            result['effects'].append({
                'type': 'damage',
                'target': target.name,
                'amount': actual_damage
            })
        elif self.intent == "defend":
            self.gain_block(self.intent_block)
            result['effects'].append({
                'type': 'block',
                'amount': self.intent_block,
                'actual_block': self.block
            })
        elif self.intent == "buff":
            # Example: gain strength
            self.status_manager.add_status(CommonStatuses.STRENGTH, self.intent_damage)
            result['effects'].append({
                'type': 'status',
                'target': self.name,
                'status': CommonStatuses.STRENGTH,
                'amount': self.intent_damage
            })
        elif self.intent == "debuff":
            # Example: apply vulnerable
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

