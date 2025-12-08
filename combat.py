"""
Turn-based combat engine for the card battler game.
Handles combat flow, turns, and victory/defeat conditions.

This module contains the Combat class which manages a single combat encounter.
It handles turn flow, card playing, enemy AI, and victory/defeat conditions.
"""

from typing import List, Optional, Dict, Callable
from enum import Enum
from character import Player, Enemy, Character
from card import Card


class CombatState(Enum):
    """
    Enumeration of combat states.
    
    Tracks the current phase of combat:
    - WAITING_FOR_INPUT: Waiting for player action
    - PLAYER_TURN: Player's turn (can play cards)
    - ENEMY_TURN: Enemy's turn (enemies act)
    - VICTORY: Player won
    - DEFEAT: Player lost
    - ENDED: Combat finished
    """
    WAITING_FOR_INPUT = "waiting_for_input"  # Waiting for player
    PLAYER_TURN = "player_turn"  # Player can act
    ENEMY_TURN = "enemy_turn"  # Enemies act
    VICTORY = "victory"  # Player won
    DEFEAT = "defeat"  # Player lost
    ENDED = "ended"  # Combat finished


class Combat:
    """
    Manages a single combat encounter.
    
    This class orchestrates the entire combat flow:
    - Manages turn order (player -> enemies -> player...)
    - Handles card playing
    - Executes enemy AI
    - Tracks combat state and victory/defeat
    - Maintains combat log for debugging/display
    """
    
    def __init__(self, player: Player, enemies: List[Enemy]):
        """
        Initialize combat with player and enemies.
        
        Args:
            player: The Player character
            enemies: List of Enemy characters to fight
        """
        self.player = player  # Player character
        self.enemies = enemies  # List of enemy characters
        self.state = CombatState.WAITING_FOR_INPUT  # Current combat state
        self.turn_number = 0  # Current turn number (starts at 0, increments)
        self.combat_log: List[str] = []  # Log of combat events
        
        # Initialize combat - prepare player's deck
        self.player.start_combat()
        self._log(f"Combat started! Facing {len(enemies)} enemy(ies).")
    
    def _log(self, message: str):
        """
        Add a message to the combat log.
        
        Internal method for logging combat events. Logs are stored in
        combat_log list and also printed to console for debugging.
        
        Args:
            message: Message to log
        """
        self.combat_log.append(message)
        print(f"[Combat] {message}")
    
    def start_player_turn(self):
        """
        Start the player's turn.
        
        This method:
        1. Increments turn number
        2. Sets state to PLAYER_TURN
        3. Calls player.start_turn() (draws cards, gains energy)
        4. Logs current status of player and enemies
        """
        self.turn_number += 1  # Increment turn counter
        self.state = CombatState.PLAYER_TURN  # Set state to player's turn
        self._log(f"\n=== Turn {self.turn_number} ===")
        self._log("Player's turn begins.")
        
        # Start player's turn (draws cards, gains energy, applies start-of-turn effects)
        self.player.start_turn()
        
        # Log player status for visibility
        self._log(f"Player HP: {self.player.current_hp}/{self.player.max_hp}, "
                 f"Block: {self.player.block}, Energy: {self.player.energy}/{self.player.max_energy}")
        self._log(f"Hand size: {self.player.deck.get_hand_size()}")
        
        # Log enemy statuses (HP, block, intent)
        for enemy in self.enemies:
            if enemy.is_alive():
                self._log(f"{enemy.name} HP: {enemy.current_hp}/{enemy.max_hp}, Block: {enemy.block}")
                if enemy.intent_description:
                    self._log(f"{enemy.name} intent: {enemy.intent_description}")
    
    def play_card(self, card: Card, target_index: int = 0) -> Dict:
        """
        Play a card from player's hand.
        
        Validates that it's the player's turn, the target is valid, and
        then plays the card. Logs all effects and checks for enemy defeat.
        
        Args:
            card: The Card object to play
            target_index: Index of enemy in enemies list to target (default: 0)
            
        Returns:
            Dictionary with 'success' (bool) and 'effects' (list) or error message
        """
        # Validation: Must be player's turn
        if self.state != CombatState.PLAYER_TURN:
            return {'success': False, 'message': 'Not player turn'}
        
        # Validation: Target must exist
        if not self.enemies or target_index >= len(self.enemies):
            return {'success': False, 'message': 'Invalid target'}
        
        target = self.enemies[target_index]
        # Validation: Target must be alive
        if not target.is_alive():
            return {'success': False, 'message': 'Target is dead'}
        
        # Play the card (delegates to player.play_card())
        result = self.player.play_card(card, target)
        
        # Log card play and effects if successful
        if result['success']:
            self._log(f"Player plays {card.name}!")
            # Log each effect that occurred
            for effect in result.get('effects', []):
                if effect['type'] == 'damage':
                    self._log(f"  → {effect['target']} takes {effect['amount']} damage!")
                elif effect['type'] == 'block':
                    self._log(f"  → Player gains {effect['amount']} block (total: {effect['actual_block']})")
                elif effect['type'] == 'energy':
                    self._log(f"  → Player gains {effect['amount']} energy")
                elif effect['type'] == 'draw':
                    self._log(f"  → Player draws {len(effect['cards'])} card(s)")
                elif effect['type'] == 'status':
                    self._log(f"  → {effect['target']} gains {effect['amount']} {effect['status']}")
            
            # Check if enemy was defeated
            if not target.is_alive():
                self._log(f"{target.name} is defeated!")
        
        return result
    
    def end_player_turn(self):
        """
        End the player's turn and start enemy turns.
        
        This method:
        1. Ends player's turn (applies end-of-turn effects, discards hand)
        2. Checks victory condition (all enemies dead)
        3. Starts enemy turns if combat continues
        """
        # Validation: Must be player's turn
        if self.state != CombatState.PLAYER_TURN:
            return
        
        # End player's turn (applies end-of-turn effects, discards hand)
        self.player.end_turn()
        self._log("\nPlayer's turn ends.")
        
        # Check victory condition: Are all enemies dead?
        if all(not enemy.is_alive() for enemy in self.enemies):
            self.state = CombatState.VICTORY
            self._log("\n=== VICTORY! ===")
            return
        
        # Start enemy turns (they act, then next player turn begins)
        self._start_enemy_turns()
    
    def _start_enemy_turns(self):
        """Start all enemy turns."""
        self.state = CombatState.ENEMY_TURN
        
        for enemy in self.enemies:
            if not enemy.is_alive():
                continue
            
            enemy.start_turn()
            
            # Simple AI: determine intent
            self._determine_enemy_intent(enemy)
            
            if enemy.intent_description:
                self._log(f"\n{enemy.name}'s turn: {enemy.intent_description}")
            
            # Execute intent
            result = enemy.execute_intent(self.player)
            
            for effect in result.get('effects', []):
                if effect['type'] == 'damage':
                    self._log(f"  → {effect['target']} takes {effect['amount']} damage!")
                elif effect['type'] == 'block':
                    self._log(f"  → {enemy.name} gains {effect['amount']} block")
                elif effect['type'] == 'status':
                    self._log(f"  → {effect['target']} gains {effect['amount']} {effect['status']}")
            
            enemy.end_turn()
            
            # Check defeat condition
            if not self.player.is_alive():
                self.state = CombatState.DEFEAT
                self._log("\n=== DEFEAT! ===")
                return
        
        # Enemy turns complete, start next player turn
        self.start_player_turn()
    
    def _determine_enemy_intent(self, enemy: Enemy):
        """
        Determine what the enemy will do this turn (simple AI).
        
        This is a simple pattern-based AI system. In a full game, this would
        be more sophisticated with behavior trees, state machines, or complex
        decision-making logic.
        
        Current AI patterns:
        - Every 3 turns when low HP: Defend
        - Every 4 turns: Buff (gain Strength)
        - Default: Attack (damage scales with turn number)
        
        Args:
            enemy: The Enemy whose intent to determine
        """
        # Simple pattern-based AI
        # In a full game, this would be more sophisticated
        
        hp_percent = enemy.get_hp_percentage()  # Get HP as percentage (0.0 to 1.0)
        
        # Pattern 1: Defend when low on HP (every 3 turns)
        if self.turn_number % 3 == 0 and hp_percent < 0.5:
            # Every 3 turns when low on HP, defend
            block_amount = 8 + (self.turn_number // 3)  # Scaling block
            enemy.set_intent("defend", block=block_amount, 
                           description=f"Preparing to defend (will gain {block_amount} block)")
        # Pattern 2: Buff periodically (every 4 turns)
        elif self.turn_number % 4 == 0:
            # Every 4 turns, buff (gain strength)
            strength_gain = 2
            enemy.set_intent("buff", damage=strength_gain,
                           description=f"Gathering strength (will gain {strength_gain} Strength)")
        # Pattern 3: Default attack (scales with turn number)
        else:
            # Default: attack (damage increases over time)
            base_damage = 6 + (self.turn_number // 2)  # Damage scales with turns
            enemy.set_intent("attack", damage=base_damage,
                           description=f"Attacking (will deal {base_damage} damage)")
    
    def get_available_cards(self) -> List[Card]:
        """Get cards the player can play."""
        if self.player.deck:
            return self.player.deck.get_hand()
        return []
    
    def get_state(self) -> Dict:
        """Get current combat state for serialization."""
        return {
            'state': self.state.value,
            'turn_number': self.turn_number,
            'player': self.player.to_dict(),
            'enemies': [enemy.to_dict() for enemy in self.enemies],
            'player_hand': [card.to_dict() for card in self.get_available_cards()],
            'combat_log': self.combat_log[-10:]  # Last 10 log entries
        }
    
    def is_victory(self) -> bool:
        """Check if player won."""
        return self.state == CombatState.VICTORY
    
    def is_defeat(self) -> bool:
        """Check if player lost."""
        return self.state == CombatState.DEFEAT
    
    def is_combat_active(self) -> bool:
        """Check if combat is still active."""
        return self.state in [CombatState.PLAYER_TURN, CombatState.ENEMY_TURN, CombatState.WAITING_FOR_INPUT]


class EncounterGenerator:
    """Generates procedural encounters (stretch feature)."""
    
    @staticmethod
    def generate_easy_encounter() -> List[Enemy]:
        """Generate an easy encounter."""
        import random
        enemies = []
        
        # 1-2 basic enemies
        num_enemies = random.randint(1, 2)
        for i in range(num_enemies):
            enemy = Enemy(
                name=f"Goblin {i+1}",
                max_hp=random.randint(20, 30),
                intent="attack",
                damage=random.randint(5, 8)
            )
            enemies.append(enemy)
        
        return enemies
    
    @staticmethod
    def generate_medium_encounter() -> List[Enemy]:
        """Generate a medium encounter."""
        import random
        enemies = []
        
        # 1-3 enemies, mix of types
        num_enemies = random.randint(1, 3)
        for i in range(num_enemies):
            enemy_type = random.choice(["goblin", "orc", "skeleton"])
            if enemy_type == "goblin":
                enemy = Enemy(
                    name=f"Goblin {i+1}",
                    max_hp=random.randint(25, 35),
                    intent="attack",
                    damage=random.randint(6, 9)
                )
            elif enemy_type == "orc":
                enemy = Enemy(
                    name=f"Orc {i+1}",
                    max_hp=random.randint(40, 50),
                    intent="attack",
                    damage=random.randint(8, 12)
                )
            else:  # skeleton
                enemy = Enemy(
                    name=f"Skeleton {i+1}",
                    max_hp=random.randint(30, 40),
                    intent="attack",
                    damage=random.randint(7, 10)
                )
            enemies.append(enemy)
        
        return enemies
    
    @staticmethod
    def generate_boss_encounter() -> List[Enemy]:
        """Generate a boss encounter."""
        boss = Enemy(
            name="Dragon",
            max_hp=100,
            intent="attack",
            damage=15
        )
        return [boss]

