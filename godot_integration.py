"""
Godot integration module for the card battler game.
This module provides a bridge between Python game logic and Godot.
"""

import json
from typing import Dict, Optional, List
from game import Game
from card import Card
from character import Character


class GodotGameBridge:
    """
    Bridge class for integrating Python game logic with Godot.
    This class provides a clean API that Godot can call via Python plugin or HTTP.
    """
    
    def __init__(self):
        """Initialize the game bridge."""
        self.game = Game()
        self.current_combat = None
    
    def start_new_game(self) -> Dict:
        """Start a new game session."""
        self.game = Game()
        return {
            'success': True,
            'game_state': self.game.get_game_state()
        }
    
    def start_combat(self, floor: int = None) -> Dict:
        """Start a new combat encounter."""
        if floor:
            self.game.floor = floor
        
        self.current_combat = self.game.start_new_combat()
        return {
            'success': True,
            'combat_state': self.current_combat.get_state()
        }
    
    def get_game_state(self) -> Dict:
        """Get the current game state."""
        return self.game.get_game_state()
    
    def get_combat_state(self) -> Optional[Dict]:
        """Get the current combat state."""
        if self.current_combat:
            return self.current_combat.get_state()
        return None
    
    def play_card(self, card_name: str, target_index: int = 0) -> Dict:
        """Play a card from the player's hand."""
        if not self.current_combat:
            return {'success': False, 'message': 'No active combat'}
        
        result = self.game.play_card(card_name, target_index)
        
        # Return updated combat state
        if result['success']:
            result['combat_state'] = self.current_combat.get_state()
        
        return result
    
    def end_turn(self) -> Dict:
        """End the player's turn."""
        if not self.current_combat:
            return {'success': False, 'message': 'No active combat'}
        
        self.game.end_turn()
        
        return {
            'success': True,
            'combat_state': self.current_combat.get_state()
        }
    
    def get_available_cards(self) -> List[Dict]:
        """Get cards currently in the player's hand."""
        if not self.current_combat:
            return []
        
        return [card.to_dict() for card in self.current_combat.get_available_cards()]
    
    def get_enemies(self) -> List[Dict]:
        """Get current enemies in combat."""
        if not self.current_combat:
            return []
        
        return [enemy.to_dict() for enemy in self.current_combat.enemies if enemy.is_alive()]
    
    def is_combat_active(self) -> bool:
        """Check if combat is currently active."""
        return self.current_combat and self.current_combat.is_combat_active()
    
    def is_victory(self) -> bool:
        """Check if player won the combat."""
        return self.current_combat and self.current_combat.is_victory()
    
    def is_defeat(self) -> bool:
        """Check if player lost the combat."""
        return self.current_combat and self.current_combat.is_defeat()


# HTTP API for Godot integration (if using HTTP requests)
def create_http_api():
    """
    Create an HTTP API server for Godot to communicate with Python.
    This uses Flask or similar. Install with: pip install flask
    """
    try:
        from flask import Flask, request, jsonify
    except ImportError:
        print("Flask not installed. Install with: pip install flask")
        return None
    
    app = Flask(__name__)
    bridge = GodotGameBridge()
    
    @app.route('/api/start_game', methods=['POST'])
    def start_game():
        result = bridge.start_new_game()
        return jsonify(result)
    
    @app.route('/api/start_combat', methods=['POST'])
    def start_combat():
        data = request.get_json() or {}
        floor = data.get('floor')
        result = bridge.start_combat(floor)
        return jsonify(result)
    
    @app.route('/api/game_state', methods=['GET'])
    def get_game_state():
        return jsonify(bridge.get_game_state())
    
    @app.route('/api/combat_state', methods=['GET'])
    def get_combat_state():
        state = bridge.get_combat_state()
        if state:
            return jsonify(state)
        return jsonify({'error': 'No active combat'}), 404
    
    @app.route('/api/play_card', methods=['POST'])
    def play_card():
        data = request.get_json() or {}
        card_name = data.get('card_name')
        target_index = data.get('target_index', 0)
        result = bridge.play_card(card_name, target_index)
        return jsonify(result)
    
    @app.route('/api/end_turn', methods=['POST'])
    def end_turn():
        result = bridge.end_turn()
        return jsonify(result)
    
    @app.route('/api/available_cards', methods=['GET'])
    def get_available_cards():
        return jsonify(bridge.get_available_cards())
    
    @app.route('/api/enemies', methods=['GET'])
    def get_enemies():
        return jsonify(bridge.get_enemies())
    
    return app


# Direct Python API (for Godot Python plugin)
def get_game_bridge() -> GodotGameBridge:
    """Get a game bridge instance for direct Python calls."""
    return GodotGameBridge()


if __name__ == "__main__":
    # Example: Run HTTP server for Godot integration
    print("Starting HTTP API server for Godot integration...")
    print("Install Flask with: pip install flask")
    print("Then access API at http://localhost:5000")
    
    app = create_http_api()
    if app:
        app.run(host='0.0.0.0', port=5000, debug=True)

