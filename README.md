# Card Battler - Slay the Spire Lite

A Python-based deck-building card battler game inspired by Slay the Spire. The game features turn-based combat, deck management, status effects, and procedural encounters. Designed to integrate with Godot for visual presentation.

## Features

### Core Features ✅
- **Data-driven card system** - Cards are defined as data structures with effects, costs, and metadata
- **Deck management** - Draw pile, discard pile, hand, and exhaust mechanics
- **Turn-based combat engine** - Full combat flow with player and enemy turns
- **Status effect system** - Buffs, debuffs, and persistent effects (Strength, Vulnerable, Weak, etc.)
- **Character system** - Player and enemy entities with HP, block, energy, and status effects

### Stretch Features ✅
- **Procedural encounters** - Randomly generated enemy encounters based on floor level
- **Multiple character classes** - Extensible character system (ready for multiple classes)
- **Relics/Passives** - Framework in place for relics and passive abilities

## Project Structure

```
.
├── card.py              # Card definitions and card library
├── deck.py              # Deck management (draw, discard, hand)
├── character.py         # Player and enemy character classes
├── status_effects.py    # Status effect system
├── combat.py            # Turn-based combat engine
├── game.py              # Main game loop and entry point (terminal)
├── gui.py               # Desktop GUI (tkinter)
├── web_gui.py           # Web browser interface (Flask)
├── run_gui.py           # Quick launcher for GUI
├── godot_integration.py # Godot integration bridge
├── __init__.py          # Package initialization
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Installation

### Basic Setup (Python Only)

The game runs on pure Python 3.7+ with no external dependencies required!

## Running the Game

### 🎮 Visual GUI (Recommended)

**Option 1: Desktop GUI (tkinter - Built-in)**
```bash
python3 gui.py
# or
python3 run_gui.py
```
Opens a windowed GUI with clickable cards, visual stats, and combat log.

**Option 2: Web Browser Interface**
```bash
# First install Flask (one-time setup)
pip install flask

# Then run the web server
python3 web_gui.py

# Open your browser to: http://localhost:5000
```
Play in your web browser with a modern, responsive interface!

### 📟 Terminal/Command Line

```bash
# Run the text-based version
python3 game.py
```
Commands: `play <card_number> [target]`, `end`, `quit`

### Godot Integration Setup

For HTTP API integration with Godot:

```bash
# Install Flask for HTTP API
pip install flask

# Run the HTTP API server
python godot_integration.py

# The API will be available at http://localhost:5000
```

## Usage

### Running the Game

#### Command Line (Text-Based)

```bash
python game.py
```

The game runs in the terminal with a simple text interface. Commands:
- `play <card_number> [target]` - Play a card from your hand
- `end` - End your turn
- `state` - Show full game state (JSON)
- `quit` - Quit the game

#### Python API

```python
from game import Game

# Create game instance
game = Game()

# Start combat
combat = game.start_new_combat()

# Play a card
result = game.play_card("Strike", target_index=0)

# End turn
game.end_turn()

# Get game state
state = game.get_game_state()
```

#### Godot Integration

**Option 1: Direct Python Calls (Godot Python Plugin)**

```python
from godot_integration import get_game_bridge

bridge = get_game_bridge()
bridge.start_new_game()
bridge.start_combat()

# Play a card
result = bridge.play_card("Strike", target_index=0)

# Get state
state = bridge.get_combat_state()
```

**Option 2: HTTP API**

```bash
# Start the HTTP server
python godot_integration.py

# Then from Godot, make HTTP requests:
# POST http://localhost:5000/api/start_game
# POST http://localhost:5000/api/play_card
# GET  http://localhost:5000/api/combat_state
```

## Game Mechanics

### Cards

Cards have:
- **Name** - Card identifier
- **Type** - Attack, Skill, or Power
- **Cost** - Energy cost to play
- **Effects** - Damage, block, card draw, energy gain, status effects
- **Rarity** - Common, Uncommon, or Rare
- **Upgrades** - Cards can be upgraded for better effects

### Combat Flow

1. **Player Turn**
   - Draw cards (default: 5)
   - Gain energy (default: 3)
   - Play cards from hand
   - End turn

2. **Enemy Turn**
   - Each enemy executes their intent (attack, defend, buff, debuff)
   - Status effects tick

3. **Status Effects**
   - Applied at start/end of turn
   - Can stack
   - Some expire after duration

### Status Effects

**Buffs:**
- **Strength** - Increases damage dealt
- **Dexterity** - Increases block gained
- **Metallicize** - Gain block at end of turn
- **Barricade** - Block doesn't expire
- **Demon Form** - Gain strength each turn

**Debuffs:**
- **Vulnerable** - Take 50% more damage
- **Weak** - Deal 25% less damage
- **Frail** - Gain 25% less block

**Damage Over Time:**
- **Poison** - Damage at start of turn
- **Burn** - Damage at end of turn

## Example Cards

- **Strike** (Attack, 1 cost) - Deal 6 damage
- **Defend** (Skill, 1 cost) - Gain 5 block
- **Bash** (Attack, 2 cost) - Deal 8 damage, apply Vulnerable
- **Metallicize** (Power, 1 cost) - Gain 3 block at end of turn
- **Demon Form** (Power, 3 cost) - Gain 2 Strength each turn

## Extending the Game

### Adding New Cards

Edit `card.py` and add to `CardLibrary.get_all_cards()`:

```python
Card(
    name="New Card",
    card_type=CardType.ATTACK,
    cost=2,
    damage=10,
    description="Deal 10 damage.",
    rarity=CardRarity.COMMON
)
```

### Adding New Status Effects

Edit `status_effects.py` and add to `CommonStatuses` class, then handle in `Character.start_turn()` or `Character.end_turn()`.

### Adding New Enemies

Create enemy instances in `combat.py`:

```python
enemy = Enemy(
    name="New Enemy",
    max_hp=50,
    intent="attack",
    damage=10
)
```

## Godot Integration Guide

### Method 1: Godot Python Plugin

1. Install the Godot Python plugin
2. Import the Python module in GDScript:
   ```gdscript
   var bridge = PythonBridge.get_game_bridge()
   bridge.start_new_game()
   ```

### Method 2: HTTP API

1. Run `python godot_integration.py` to start the HTTP server
2. Use Godot's HTTPRequest node to communicate:
   ```gdscript
   var http_request = HTTPRequest.new()
   http_request.request("http://localhost:5000/api/play_card", 
                        ["Content-Type: application/json"], 
                        HTTPClient.METHOD_POST, 
                        JSON.stringify({"card_name": "Strike", "target_index": 0}))
   ```

### Method 3: GDNative/Extension

Create a C++ extension that wraps the Python code using Python C API or pybind11.

## License

This project is provided as-is for educational purposes.

## Credits

Inspired by Slay the Spire by MegaCrit Games.

