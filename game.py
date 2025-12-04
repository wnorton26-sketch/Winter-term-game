"""
Main game loop and entry point for the card battler game.
"""

from typing import Optional
from character import Player
from deck import Deck
from card import CardLibrary
from combat import Combat, EncounterGenerator


class Game:
    """Main game class managing the overall game state."""
    
    def __init__(self):
        """Initialize the game."""
        self.player = Player(name="Player", max_hp=80, max_energy=3)
        self.current_combat: Optional[Combat] = None
        self.floor = 1
        self.gold = 0
        
        # Initialize player deck
        starter_deck = CardLibrary.get_starter_deck()
        self.player.set_deck(Deck(starter_deck))
    
    def start_new_combat(self, enemies=None):
        """Start a new combat encounter."""
        if enemies is None:
            # Generate procedural encounter based on floor
            if self.floor <= 3:
                enemies = EncounterGenerator.generate_easy_encounter()
            elif self.floor <= 6:
                enemies = EncounterGenerator.generate_medium_encounter()
            else:
                enemies = EncounterGenerator.generate_boss_encounter()
        
        self.current_combat = Combat(self.player, enemies)
        self.current_combat.start_player_turn()
        return self.current_combat
    
    def play_card(self, card_name: str, target_index: int = 0) -> dict:
        """Play a card by name."""
        if not self.current_combat:
            return {'success': False, 'message': 'No active combat'}
        
        # Find card in hand
        hand = self.current_combat.get_available_cards()
        card = None
        for c in hand:
            if c.name.lower() == card_name.lower():
                card = c
                break
        
        if not card:
            return {'success': False, 'message': f'Card "{card_name}" not in hand'}
        
        return self.current_combat.play_card(card, target_index)
    
    def end_turn(self):
        """End the current turn."""
        if self.current_combat:
            self.current_combat.end_player_turn()
    
    def get_game_state(self) -> dict:
        """Get current game state."""
        state = {
            'floor': self.floor,
            'gold': self.gold,
            'player': self.player.to_dict(),
            'combat': None
        }
        
        if self.current_combat:
            state['combat'] = self.current_combat.get_state()
        
        return state
    
    def advance_floor(self):
        """Advance to the next floor."""
        self.floor += 1
        # Could add rewards, shop, etc. here


def main():
    """Main entry point for the game."""
    print("=" * 50)
    print("Card Battler - Slay the Spire Lite")
    print("=" * 50)
    print("\nWelcome to the card battler!")
    print("This is a Python-based card battler that can be integrated with Godot.")
    print("\nGame features:")
    print("- Turn-based combat")
    print("- Deck building")
    print("- Status effects")
    print("- Procedural encounters")
    print("\n" + "=" * 50)
    
    # Create game instance
    game = Game()
    
    # Start first combat
    print(f"\nStarting Floor {game.floor}...")
    combat = game.start_new_combat()
    
    # Simple text-based game loop
    while combat.is_combat_active():
        print("\n" + "-" * 50)
        print("Your turn!")
        print(f"HP: {game.player.current_hp}/{game.player.max_hp}")
        print(f"Block: {game.player.block}")
        print(f"Energy: {game.player.energy}/{game.player.max_energy}")
        
        # Show hand
        hand = combat.get_available_cards()
        print(f"\nHand ({len(hand)} cards):")
        for i, card in enumerate(hand):
            cost_symbol = "●" * card.get_cost()
            print(f"  {i+1}. {card.name} [{cost_symbol}] - {card.description}")
        
        # Show enemies
        print("\nEnemies:")
        for i, enemy in enumerate(combat.enemies):
            if enemy.is_alive():
                print(f"  {i+1}. {enemy.name} - HP: {enemy.current_hp}/{enemy.max_hp}, "
                     f"Block: {enemy.block}")
                if enemy.intent_description:
                    print(f"      Intent: {enemy.intent_description}")
        
        # Get player input
        print("\nCommands:")
        print("  play <card_number> [target] - Play a card")
        print("  end - End your turn")
        print("  state - Show game state")
        print("  quit - Quit game")
        
        try:
            command = input("\n> ").strip().lower()
            
            if command == "quit":
                print("Thanks for playing!")
                break
            elif command == "end":
                combat.end_player_turn()
            elif command == "state":
                import json
                print(json.dumps(game.get_game_state(), indent=2))
            elif command.startswith("play"):
                parts = command.split()
                if len(parts) < 2:
                    print("Usage: play <card_number> [target]")
                    continue
                
                try:
                    card_index = int(parts[1]) - 1
                    target_index = int(parts[2]) - 1 if len(parts) > 2 else 0
                    
                    if 0 <= card_index < len(hand):
                        card = hand[card_index]
                        result = combat.play_card(card, target_index)
                        if not result['success']:
                            print(f"Error: {result.get('message', 'Unknown error')}")
                    else:
                        print("Invalid card number")
                except ValueError:
                    print("Invalid number")
            else:
                print("Unknown command")
        
        except KeyboardInterrupt:
            print("\n\nGame interrupted. Thanks for playing!")
            break
        except EOFError:
            print("\n\nGame ended. Thanks for playing!")
            break
    
    # Combat ended
    if combat.is_victory():
        print("\n🎉 Victory! You defeated all enemies!")
        game.advance_floor()
        print(f"Advancing to Floor {game.floor}...")
    elif combat.is_defeat():
        print("\n💀 Defeat! You have been defeated.")
        print("Game Over.")


if __name__ == "__main__":
    main()

