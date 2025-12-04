"""
Web-based GUI for the Card Battler game.
Run this and open http://localhost:5000 in your browser.
"""

from flask import Flask, render_template_string, jsonify, request
from game import Game
from godot_integration import GodotGameBridge
import json

app = Flask(__name__)
bridge = GodotGameBridge()

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Card Battler - Slay the Spire Lite</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        .game-area {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        .panel {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            border: 2px solid #e9ecef;
        }
        .panel h2 {
            color: #495057;
            margin-bottom: 15px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .player-stats {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .stat {
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            min-width: 120px;
        }
        .stat-label {
            font-size: 0.9em;
            color: #6c757d;
            margin-bottom: 5px;
        }
        .stat-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
        }
        .hp { color: #dc3545; }
        .block { color: #007bff; }
        .energy { color: #28a745; }
        .card {
            background: white;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            border-color: #667eea;
        }
        .card.disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .card-name {
            font-weight: bold;
            font-size: 1.1em;
            color: #333;
            margin-bottom: 5px;
        }
        .card-cost {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 3px 8px;
            border-radius: 5px;
            font-size: 0.9em;
            margin-right: 10px;
        }
        .card-description {
            color: #6c757d;
            font-size: 0.9em;
            margin-top: 5px;
        }
        .enemy {
            background: white;
            border: 2px solid #dc3545;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
        }
        .enemy-name {
            font-weight: bold;
            font-size: 1.2em;
            color: #dc3545;
            margin-bottom: 5px;
        }
        .enemy-hp {
            color: #333;
            margin-bottom: 5px;
        }
        .enemy-intent {
            color: #6c757d;
            font-style: italic;
            font-size: 0.9em;
        }
        .controls {
            display: flex;
            gap: 10px;
            margin-top: 20px;
            justify-content: center;
        }
        button {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            transition: background 0.3s;
        }
        button:hover {
            background: #5568d3;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .log {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            max-height: 300px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        .log-entry {
            margin-bottom: 5px;
            color: #495057;
        }
        .message {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
            font-weight: bold;
        }
        .victory {
            background: #d4edda;
            color: #155724;
            border: 2px solid #c3e6cb;
        }
        .defeat {
            background: #f8d7da;
            color: #721c24;
            border: 2px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🃏 Card Battler</h1>
        
        <div id="message"></div>
        
        <div class="game-area">
            <div class="panel">
                <h2>Player</h2>
                <div class="player-stats">
                    <div class="stat">
                        <div class="stat-label">HP</div>
                        <div class="stat-value hp" id="player-hp">80/80</div>
                    </div>
                    <div class="stat">
                        <div class="stat-label">Block</div>
                        <div class="stat-value block" id="player-block">0</div>
                    </div>
                    <div class="stat">
                        <div class="stat-label">Energy</div>
                        <div class="stat-value energy" id="player-energy">3/3</div>
                    </div>
                </div>
                
                <h3 style="margin-top: 20px; margin-bottom: 10px;">Your Hand</h3>
                <div id="hand"></div>
            </div>
            
            <div class="panel">
                <h2>Enemies</h2>
                <div id="enemies"></div>
                
                <h3 style="margin-top: 20px; margin-bottom: 10px;">Combat Log</h3>
                <div class="log" id="log"></div>
            </div>
        </div>
        
        <div class="controls">
            <button onclick="endTurn()">End Turn</button>
            <button onclick="newCombat()">New Combat</button>
        </div>
    </div>
    
    <script>
        let combatState = null;
        
        function updateUI() {
            fetch('/api/combat_state')
                .then(r => r.json())
                .then(data => {
                    combatState = data;
                    updatePlayer(data.player);
                    updateHand(data.player_hand || []);
                    updateEnemies(data.enemies || []);
                    checkGameState(data);
                })
                .catch(err => console.error('Error:', err));
        }
        
        function updatePlayer(player) {
            document.getElementById('player-hp').textContent = `${player.current_hp}/${player.max_hp}`;
            document.getElementById('player-block').textContent = player.block;
            document.getElementById('player-energy').textContent = `${player.energy}/${player.max_energy}`;
        }
        
        function updateHand(hand) {
            const container = document.getElementById('hand');
            container.innerHTML = '';
            
            hand.forEach((card, index) => {
                const cardDiv = document.createElement('div');
                cardDiv.className = 'card';
                if (combatState && combatState.player.energy < card.cost) {
                    cardDiv.className += ' disabled';
                }
                
                cardDiv.innerHTML = `
                    <div class="card-name">
                        <span class="card-cost">${card.cost}</span>
                        ${card.name}
                    </div>
                    <div class="card-description">${card.description}</div>
                `;
                
                if (combatState && combatState.player.energy >= card.cost) {
                    cardDiv.onclick = () => playCard(card.name);
                }
                
                container.appendChild(cardDiv);
            });
        }
        
        function updateEnemies(enemies) {
            const container = document.getElementById('enemies');
            container.innerHTML = '';
            
            enemies.forEach(enemy => {
                if (enemy.current_hp <= 0) return;
                
                const enemyDiv = document.createElement('div');
                enemyDiv.className = 'enemy';
                enemyDiv.innerHTML = `
                    <div class="enemy-name">${enemy.name}</div>
                    <div class="enemy-hp">HP: ${enemy.current_hp}/${enemy.max_hp}</div>
                    ${enemy.block > 0 ? `<div>Block: ${enemy.block}</div>` : ''}
                `;
                container.appendChild(enemyDiv);
            });
        }
        
        function playCard(cardName) {
            fetch('/api/play_card', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({card_name: cardName, target_index: 0})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    addLog(`Played ${cardName}!`);
                    updateUI();
                } else {
                    alert(data.message || 'Cannot play card');
                }
            });
        }
        
        function endTurn() {
            fetch('/api/end_turn', {method: 'POST'})
                .then(r => r.json())
                .then(data => {
                    addLog('--- Turn Ended ---');
                    updateUI();
                });
        }
        
        function newCombat() {
            fetch('/api/start_combat', {method: 'POST'})
                .then(r => r.json())
                .then(data => {
                    document.getElementById('log').innerHTML = '';
                    addLog('Starting new combat...');
                    updateUI();
                });
        }
        
        function checkGameState(state) {
            const msgDiv = document.getElementById('message');
            if (state.state === 'victory') {
                msgDiv.className = 'message victory';
                msgDiv.textContent = '🎉 Victory! You defeated all enemies!';
            } else if (state.state === 'defeat') {
                msgDiv.className = 'message defeat';
                msgDiv.textContent = '💀 Defeat! You have been defeated!';
            } else {
                msgDiv.className = '';
                msgDiv.textContent = '';
            }
        }
        
        function addLog(message) {
            const log = document.getElementById('log');
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            entry.textContent = message;
            log.appendChild(entry);
            log.scrollTop = log.scrollHeight;
        }
        
        // Initialize
        fetch('/api/start_game', {method: 'POST'})
            .then(() => fetch('/api/start_combat', {method: 'POST'}))
            .then(() => {
                addLog('Game started!');
                updateUI();
                setInterval(updateUI, 2000); // Auto-refresh every 2 seconds
            });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the main game page."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/start_game', methods=['POST'])
def start_game():
    """Start a new game."""
    result = bridge.start_new_game()
    return jsonify(result)

@app.route('/api/start_combat', methods=['POST'])
def start_combat():
    """Start a new combat."""
    result = bridge.start_combat()
    return jsonify(result)

@app.route('/api/combat_state', methods=['GET'])
def get_combat_state():
    """Get current combat state."""
    state = bridge.get_combat_state()
    if state:
        return jsonify(state)
    return jsonify({'error': 'No active combat'}), 404

@app.route('/api/play_card', methods=['POST'])
def play_card():
    """Play a card."""
    data = request.get_json() or {}
    card_name = data.get('card_name')
    target_index = data.get('target_index', 0)
    result = bridge.play_card(card_name, target_index)
    return jsonify(result)

@app.route('/api/end_turn', methods=['POST'])
def end_turn():
    """End the player's turn."""
    result = bridge.end_turn()
    return jsonify(result)

if __name__ == '__main__':
    print("=" * 60)
    print("Card Battler - Web Interface")
    print("=" * 60)
    print("\nStarting web server...")
    print("Open your browser and go to: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    bridge.start_new_game()
    bridge.start_combat()
    
    app.run(host='0.0.0.0', port=5000, debug=True)

