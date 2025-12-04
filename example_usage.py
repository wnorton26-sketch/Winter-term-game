"""
Example usage of the Card Battler game.
Demonstrates how to use the game programmatically.
"""

from game import Game
from card import CardLibrary, CardType


def example_basic_combat():
    """Example of running a basic combat."""
    print("=" * 60)
    print("Example: Basic Combat")
    print("=" * 60)
    
    # Create game
    game = Game()
    
    # Start combat
    combat = game.start_new_combat()
    
    # Show initial state
    print(f"\nPlayer HP: {game.player.current_hp}/{game.player.max_hp}")
    print(f"Energy: {game.player.energy}/{game.player.max_energy}")
    
    hand = combat.get_available_cards()
    print(f"\nHand ({len(hand)} cards):")
    for i, card in enumerate(hand):
        print(f"  {i+1}. {card.name} (Cost: {card.get_cost()}) - {card.description}")
    
    print("\nEnemies:")
    for i, enemy in enumerate(combat.enemies):
        print(f"  {i+1}. {enemy.name} - HP: {enemy.current_hp}/{enemy.max_hp}")
    
    # Play a card
    if hand:
        print(f"\nPlaying {hand[0].name}...")
        result = combat.play_card(hand[0], target_index=0)
        if result['success']:
            print("Card played successfully!")
            for effect in result.get('effects', []):
                print(f"  Effect: {effect}")
    
    # End turn
    print("\nEnding turn...")
    combat.end_player_turn()
    
    print("\nCombat state:", "Victory" if combat.is_victory() else 
          "Defeat" if combat.is_defeat() else "Active")


def example_card_library():
    """Example of using the card library."""
    print("\n" + "=" * 60)
    print("Example: Card Library")
    print("=" * 60)
    
    # Get all cards
    all_cards = CardLibrary.get_all_cards()
    print(f"\nTotal cards in library: {len(all_cards)}")
    
    # Get cards by type
    attacks = CardLibrary.get_cards_by_type(CardType.ATTACK)
    print(f"Attack cards: {len(attacks)}")
    
    # Get specific card
    strike = CardLibrary.get_card_by_name("Strike")
    if strike:
        print(f"\nFound card: {strike.name}")
        print(f"  Type: {strike.card_type.value}")
        print(f"  Cost: {strike.get_cost()}")
        print(f"  Damage: {strike.get_damage()}")
        print(f"  Description: {strike.description}")


def example_godot_integration():
    """Example of using the Godot integration bridge."""
    print("\n" + "=" * 60)
    print("Example: Godot Integration")
    print("=" * 60)
    
    from godot_integration import get_game_bridge
    
    bridge = get_game_bridge()
    
    # Start game
    result = bridge.start_new_game()
    print(f"Game started: {result['success']}")
    
    # Start combat
    result = bridge.start_combat()
    print(f"Combat started: {result['success']}")
    
    # Get available cards
    cards = bridge.get_available_cards()
    print(f"\nAvailable cards: {len(cards)}")
    for card in cards[:3]:  # Show first 3
        print(f"  - {card['name']} (Cost: {card['cost']})")
    
    # Get enemies
    enemies = bridge.get_enemies()
    print(f"\nEnemies: {len(enemies)}")
    for enemy in enemies:
        print(f"  - {enemy['name']} (HP: {enemy['current_hp']}/{enemy['max_hp']})")
    
    # Play a card
    if cards:
        result = bridge.play_card(cards[0]['name'], target_index=0)
        print(f"\nPlayed {cards[0]['name']}: {result['success']}")
    
    # Get combat state
    state = bridge.get_combat_state()
    print(f"\nCombat active: {bridge.is_combat_active()}")


if __name__ == "__main__":
    print("Card Battler - Usage Examples")
    print("=" * 60)
    
    # Run examples
    example_basic_combat()
    example_card_library()
    example_godot_integration()
    
    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)

