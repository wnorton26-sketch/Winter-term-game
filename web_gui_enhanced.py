"""
Enhanced Web-based GUI with advanced graphics and animations.
Run this and open http://localhost:5000 in your browser.
"""

from flask import Flask, render_template_string, jsonify, request, send_from_directory
from game import Game
from godot_integration import GodotGameBridge
import json
import os

app = Flask(__name__)
bridge = GodotGameBridge()

# Enhanced HTML template with advanced graphics
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Card Battler - Enhanced</title>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600&family=Roboto:wght@300;400;500;700&display=swap');
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Roboto', sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            padding: 20px;
            min-height: 100vh;
            color: #fff;
            overflow-x: hidden;
        }
        
        /* Animated background particles */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 40% 20%, rgba(119, 198, 255, 0.3) 0%, transparent 50%);
            animation: pulse 15s ease-in-out infinite;
            z-index: -1;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 0.5; transform: scale(1); }
            50% { opacity: 0.8; transform: scale(1.1); }
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        h1 {
            text-align: center;
            font-family: 'Cinzel', serif;
            font-size: 3.5em;
            margin-bottom: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 30px rgba(102, 126, 234, 0.5);
            animation: glow 2s ease-in-out infinite alternate;
        }
        
        @keyframes glow {
            from { filter: drop-shadow(0 0 10px rgba(102, 126, 234, 0.5)); }
            to { filter: drop-shadow(0 0 20px rgba(118, 75, 162, 0.8)); }
        }
        
        .game-area {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .panel {
            background: rgba(255, 255, 255, 0.08);
            border-radius: 15px;
            padding: 25px;
            border: 2px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(5px);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }
        
        .panel h2 {
            font-family: 'Cinzel', serif;
            color: #fff;
            margin-bottom: 20px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            font-size: 1.8em;
        }
        
        .player-stats {
            display: flex;
            gap: 15px;
            margin-bottom: 25px;
            flex-wrap: wrap;
        }
        
        .stat {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
            padding: 20px;
            border-radius: 12px;
            min-width: 140px;
            border: 2px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .stat:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
        }
        
        .stat-label {
            font-size: 0.9em;
            color: rgba(255, 255, 255, 0.7);
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #fff;
        }
        
        .hp .stat-value { color: #ff6b6b; }
        .block .stat-value { color: #4ecdc4; }
        .energy .stat-value { color: #ffe66d; }
        
        /* Card Styles */
        .card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 15px;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }
        
        .card::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255, 255, 255, 0.3) 0%, transparent 70%);
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .card:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
            border-color: rgba(255, 255, 255, 0.6);
        }
        
        .card:hover::before {
            opacity: 1;
        }
        
        .card.disabled {
            opacity: 0.4;
            cursor: not-allowed;
            filter: grayscale(100%);
        }
        
        .card.disabled:hover {
            transform: none;
        }
        
        .card-name {
            font-weight: bold;
            font-size: 1.3em;
            color: #fff;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }
        
        .card-cost {
            display: inline-block;
            background: rgba(255, 255, 255, 0.9);
            color: #667eea;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 1em;
            font-weight: bold;
            margin-right: 10px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }
        
        .card-description {
            color: rgba(255, 255, 255, 0.9);
            font-size: 0.95em;
            margin-top: 8px;
            line-height: 1.4;
        }
        
        .card-stats {
            display: flex;
            gap: 10px;
            margin-top: 10px;
            flex-wrap: wrap;
        }
        
        .card-stat {
            background: rgba(255, 255, 255, 0.2);
            padding: 5px 10px;
            border-radius: 8px;
            font-size: 0.85em;
        }
        
        /* Enemy Styles */
        .enemy {
            background: linear-gradient(135deg, rgba(220, 53, 69, 0.3) 0%, rgba(139, 0, 0, 0.3) 100%);
            border: 3px solid rgba(220, 53, 69, 0.5);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 15px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(220, 53, 69, 0.3);
            animation: enemyPulse 3s ease-in-out infinite;
        }
        
        @keyframes enemyPulse {
            0%, 100% { border-color: rgba(220, 53, 69, 0.5); }
            50% { border-color: rgba(220, 53, 69, 0.8); }
        }
        
        .enemy-name {
            font-weight: bold;
            font-size: 1.4em;
            color: #ff6b6b;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }
        
        .enemy-hp {
            color: #fff;
            margin-bottom: 8px;
            font-size: 1.1em;
        }
        
        .hp-bar-container {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            height: 20px;
            margin: 10px 0;
            overflow: hidden;
        }
        
        .hp-bar {
            height: 100%;
            background: linear-gradient(90deg, #ff6b6b 0%, #ee5a6f 100%);
            border-radius: 10px;
            transition: width 0.5s ease;
            box-shadow: 0 0 10px rgba(255, 107, 107, 0.5);
        }
        
        .enemy-intent {
            color: rgba(255, 255, 255, 0.8);
            font-style: italic;
            font-size: 0.95em;
            margin-top: 10px;
            padding: 8px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 8px;
        }
        
        .controls {
            display: flex;
            gap: 15px;
            margin-top: 30px;
            justify-content: center;
        }
        
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 12px;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        button:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        button:disabled {
            background: rgba(255, 255, 255, 0.2);
            cursor: not-allowed;
            opacity: 0.5;
        }
        
        .log {
            background: rgba(0, 0, 0, 0.3);
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 15px;
            max-height: 300px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        
        .log-entry {
            margin-bottom: 8px;
            color: rgba(255, 255, 255, 0.9);
            padding: 5px;
            border-radius: 5px;
            animation: fadeIn 0.3s;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateX(-10px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        .message {
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 25px;
            text-align: center;
            font-weight: bold;
            font-size: 1.3em;
            animation: slideDown 0.5s;
        }
        
        @keyframes slideDown {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .victory {
            background: linear-gradient(135deg, rgba(40, 167, 69, 0.3) 0%, rgba(25, 135, 84, 0.3) 100%);
            color: #90ee90;
            border: 3px solid rgba(40, 167, 69, 0.5);
            box-shadow: 0 0 30px rgba(40, 167, 69, 0.5);
        }
        
        .defeat {
            background: linear-gradient(135deg, rgba(220, 53, 69, 0.3) 0%, rgba(139, 0, 0, 0.3) 100%);
            color: #ff6b6b;
            border: 3px solid rgba(220, 53, 69, 0.5);
            box-shadow: 0 0 30px rgba(220, 53, 69, 0.5);
        }
        
        /* Scrollbar styling */
        .log::-webkit-scrollbar {
            width: 8px;
        }
        
        .log::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
        }
        
        .log::-webkit-scrollbar-thumb {
            background: rgba(102, 126, 234, 0.5);
            border-radius: 10px;
        }
        
        .log::-webkit-scrollbar-thumb:hover {
            background: rgba(102, 126, 234, 0.7);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚔️ Card Battler ⚔️</h1>
        
        <div id="message"></div>
        
        <div class="game-area">
            <div class="panel">
                <h2>👤 Player</h2>
                <div class="player-stats">
                    <div class="stat hp">
                        <div class="stat-label">❤️ Health</div>
                        <div class="stat-value" id="player-hp">80/80</div>
                    </div>
                    <div class="stat block">
                        <div class="stat-label">🛡️ Block</div>
                        <div class="stat-value" id="player-block">0</div>
                    </div>
                    <div class="stat energy">
                        <div class="stat-label">⚡ Energy</div>
                        <div class="stat-value" id="player-energy">3/3</div>
                    </div>
                </div>
                
                <h3 style="margin-top: 25px; margin-bottom: 15px; color: rgba(255,255,255,0.9);">🃏 Your Hand</h3>
                <div id="hand"></div>
            </div>
            
            <div class="panel">
                <h2>👹 Enemies</h2>
                <div id="enemies"></div>
                
                <h3 style="margin-top: 25px; margin-bottom: 15px; color: rgba(255,255,255,0.9);">📜 Combat Log</h3>
                <div class="log" id="log"></div>
            </div>
        </div>
        
        <div class="controls">
            <button onclick="endTurn()">⏭️ End Turn</button>
            <button onclick="newCombat()">🔄 New Combat</button>
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
                
                // Build stats display
                let statsHTML = '';
                if (card.damage > 0) statsHTML += `<span class="card-stat">⚔️ ${card.damage}</span>`;
                if (card.block > 0) statsHTML += `<span class="card-stat">🛡️ ${card.block}</span>`;
                if (card.card_draw > 0) statsHTML += `<span class="card-stat">📖 +${card.card_draw}</span>`;
                if (card.energy_gain > 0) statsHTML += `<span class="card-stat">⚡ +${card.energy_gain}</span>`;
                
                cardDiv.innerHTML = `
                    <div class="card-name">
                        <span class="card-cost">${card.cost}</span>
                        ${card.name}
                    </div>
                    <div class="card-description">${card.description}</div>
                    ${statsHTML ? `<div class="card-stats">${statsHTML}</div>` : ''}
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
                
                const hpPercent = (enemy.current_hp / enemy.max_hp) * 100;
                
                const enemyDiv = document.createElement('div');
                enemyDiv.className = 'enemy';
                enemyDiv.innerHTML = `
                    <div class="enemy-name">${enemy.name}</div>
                    <div class="enemy-hp">HP: ${enemy.current_hp}/${enemy.max_hp}</div>
                    <div class="hp-bar-container">
                        <div class="hp-bar" style="width: ${hpPercent}%"></div>
                    </div>
                    ${enemy.block > 0 ? `<div style="color: #4ecdc4; margin-top: 5px;">🛡️ Block: ${enemy.block}</div>` : ''}
                    ${enemy.intent_description ? `<div class="enemy-intent">🎯 ${enemy.intent_description}</div>` : ''}
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
                    addLog(`✨ Played ${cardName}!`);
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
                    addLog('🎮 Starting new combat...');
                    updateUI();
                });
        }
        
        function checkGameState(state) {
            const msgDiv = document.getElementById('message');
            if (state.state === 'victory') {
                msgDiv.className = 'message victory';
                msgDiv.textContent = '🎉 VICTORY! You defeated all enemies! 🎉';
            } else if (state.state === 'defeat') {
                msgDiv.className = 'message defeat';
                msgDiv.textContent = '💀 DEFEAT! You have been defeated! 💀';
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
                addLog('🎮 Game started!');
                updateUI();
                setInterval(updateUI, 2000);
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
    print("Card Battler - Enhanced Web Interface")
    print("=" * 60)
    print("\n🎮 Starting enhanced web server...")
    print("🌐 Open your browser and go to: http://localhost:8080")
    print("\n✨ Features:")
    print("   - Advanced graphics and animations")
    print("   - Beautiful card designs")
    print("   - Animated enemy displays")
    print("   - Smooth transitions and effects")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    bridge.start_new_game()
    bridge.start_combat()
    
    app.run(host='127.0.0.1', port=8080, debug=True)

