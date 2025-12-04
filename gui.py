"""
GUI version of the Card Battler game using tkinter.
Provides a visual interface for playing the game.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from game import Game
from card import Card
from character import Character


class CardBattlerGUI:
    """GUI application for the Card Battler game."""
    
    def __init__(self, root):
        """Initialize the GUI."""
        self.root = root
        self.root.title("Card Battler - Slay the Spire Lite")
        self.root.geometry("1200x800")
        
        self.game = Game()
        self.current_combat = None
        
        self.setup_ui()
        self.start_new_combat()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Left panel - Player info and cards
        left_panel = ttk.Frame(main_frame)
        left_panel.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Player stats
        player_frame = ttk.LabelFrame(left_panel, text="Player", padding="10")
        player_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.player_hp_label = ttk.Label(player_frame, text="HP: 80/80", font=("Arial", 12, "bold"))
        self.player_hp_label.pack(anchor=tk.W)
        
        self.player_block_label = ttk.Label(player_frame, text="Block: 0", font=("Arial", 11))
        self.player_block_label.pack(anchor=tk.W)
        
        self.player_energy_label = ttk.Label(player_frame, text="Energy: 3/3", font=("Arial", 11))
        self.player_energy_label.pack(anchor=tk.W)
        
        # Hand cards
        hand_frame = ttk.LabelFrame(left_panel, text="Your Hand", padding="10")
        hand_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollable frame for cards
        canvas = tk.Canvas(hand_frame, height=400)
        scrollbar = ttk.Scrollbar(hand_frame, orient="vertical", command=canvas.yview)
        self.cards_container = ttk.Frame(canvas)
        
        self.cards_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.cards_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.card_buttons = []
        
        # Right panel - Enemies and combat log
        right_panel = ttk.Frame(main_frame)
        right_panel.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)
        
        # Enemies frame
        enemies_frame = ttk.LabelFrame(right_panel, text="Enemies", padding="10")
        enemies_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        enemies_frame.columnconfigure(0, weight=1)
        
        self.enemies_container = ttk.Frame(enemies_frame)
        self.enemies_container.pack(fill=tk.BOTH, expand=True)
        
        self.enemy_labels = []
        
        # Combat log
        log_frame = ttk.LabelFrame(right_panel, text="Combat Log", padding="10")
        log_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.combat_log = scrolledtext.ScrolledText(log_frame, height=15, width=50, wrap=tk.WORD)
        self.combat_log.pack(fill=tk.BOTH, expand=True)
        self.combat_log.config(state=tk.DISABLED)
        
        # Bottom panel - Controls
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.end_turn_btn = ttk.Button(controls_frame, text="End Turn", command=self.end_turn)
        self.end_turn_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.new_combat_btn = ttk.Button(controls_frame, text="New Combat", command=self.start_new_combat)
        self.new_combat_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.quit_btn = ttk.Button(controls_frame, text="Quit", command=self.root.quit)
        self.quit_btn.pack(side=tk.LEFT)
    
    def log_message(self, message):
        """Add a message to the combat log."""
        self.combat_log.config(state=tk.NORMAL)
        self.combat_log.insert(tk.END, message + "\n")
        self.combat_log.see(tk.END)
        self.combat_log.config(state=tk.DISABLED)
    
    def update_ui(self):
        """Update the UI with current game state."""
        if not self.current_combat:
            return
        
        # Update player stats
        player = self.game.player
        self.player_hp_label.config(text=f"HP: {player.current_hp}/{player.max_hp}")
        self.player_block_label.config(text=f"Block: {player.block}")
        self.player_energy_label.config(text=f"Energy: {player.energy}/{player.max_energy}")
        
        # Update hand
        self.update_hand()
        
        # Update enemies
        self.update_enemies()
        
        # Check victory/defeat
        if self.current_combat.is_victory():
            messagebox.showinfo("Victory!", "You defeated all enemies!")
            self.start_new_combat()
        elif self.current_combat.is_defeat():
            messagebox.showerror("Defeat", "You have been defeated!")
            self.start_new_combat()
    
    def update_hand(self):
        """Update the hand display."""
        # Clear existing buttons
        for widget in self.cards_container.winfo_children():
            widget.destroy()
        self.card_buttons.clear()
        
        if not self.current_combat:
            return
        
        hand = self.current_combat.get_available_cards()
        player = self.game.player
        
        for i, card in enumerate(hand):
            card_frame = ttk.Frame(self.cards_container)
            card_frame.pack(fill=tk.X, pady=5)
            
            # Card info
            cost_symbol = "●" * card.get_cost()
            card_text = f"{card.name} [{cost_symbol}] - {card.description}"
            
            # Check if can afford
            can_play = player.energy >= card.get_cost()
            btn_state = tk.NORMAL if can_play else tk.DISABLED
            
            card_btn = ttk.Button(
                card_frame,
                text=card_text,
                command=lambda c=card, idx=i: self.play_card(c, idx),
                state=btn_state,
                width=50
            )
            card_btn.pack(side=tk.LEFT, padx=5)
            
            # Show card stats
            stats_text = ""
            if card.get_damage() > 0:
                stats_text += f"⚔ {card.get_damage()} "
            if card.get_block() > 0:
                stats_text += f"🛡 {card.get_block()} "
            if card.card_draw > 0:
                stats_text += f"📖 +{card.card_draw} "
            if card.energy_gain > 0:
                stats_text += f"⚡ +{card.energy_gain} "
            
            if stats_text:
                stats_label = ttk.Label(card_frame, text=stats_text, font=("Arial", 9))
                stats_label.pack(side=tk.LEFT, padx=5)
            
            self.card_buttons.append(card_btn)
    
    def update_enemies(self):
        """Update the enemies display."""
        # Clear existing labels
        for widget in self.enemies_container.winfo_children():
            widget.destroy()
        self.enemy_labels.clear()
        
        if not self.current_combat:
            return
        
        for i, enemy in enumerate(self.current_combat.enemies):
            if not enemy.is_alive():
                continue
            
            enemy_frame = ttk.Frame(self.enemies_container)
            enemy_frame.pack(fill=tk.X, pady=5)
            
            # Enemy info
            hp_percent = enemy.current_hp / enemy.max_hp
            hp_color = "green" if hp_percent > 0.5 else "orange" if hp_percent > 0.25 else "red"
            
            enemy_text = f"{enemy.name} - HP: {enemy.current_hp}/{enemy.max_hp}"
            if enemy.block > 0:
                enemy_text += f" | Block: {enemy.block}"
            
            enemy_label = ttk.Label(
                enemy_frame,
                text=enemy_text,
                font=("Arial", 11, "bold"),
                foreground=hp_color
            )
            enemy_label.pack(anchor=tk.W)
            
            # Intent
            if enemy.intent_description:
                intent_label = ttk.Label(
                    enemy_frame,
                    text=f"  → {enemy.intent_description}",
                    font=("Arial", 9),
                    foreground="gray"
                )
                intent_label.pack(anchor=tk.W)
            
            # Status effects
            statuses = enemy.status_manager.get_all()
            if statuses:
                status_text = "  Status: " + ", ".join([
                    f"{name} ({effect.amount})" 
                    for name, effect in statuses.items()
                ])
                status_label = ttk.Label(
                    enemy_frame,
                    text=status_text,
                    font=("Arial", 8),
                    foreground="purple"
                )
                status_label.pack(anchor=tk.W)
            
            self.enemy_labels.append(enemy_label)
    
    def play_card(self, card: Card, card_index: int):
        """Play a card."""
        if not self.current_combat or not self.current_combat.is_combat_active():
            return
        
        # Select target if multiple enemies
        target_index = 0
        alive_enemies = [e for e in self.current_combat.enemies if e.is_alive()]
        if len(alive_enemies) > 1:
            # Simple: target first alive enemy
            target_index = self.current_combat.enemies.index(alive_enemies[0])
        
        result = self.current_combat.play_card(card, target_index)
        
        if result['success']:
            self.log_message(f"Played {card.name}!")
            for effect in result.get('effects', []):
                if effect['type'] == 'damage':
                    self.log_message(f"  → {effect['target']} takes {effect['amount']} damage!")
                elif effect['type'] == 'block':
                    self.log_message(f"  → Gained {effect['amount']} block")
                elif effect['type'] == 'energy':
                    self.log_message(f"  → Gained {effect['amount']} energy")
                elif effect['type'] == 'draw':
                    self.log_message(f"  → Drew {len(effect['cards'])} card(s)")
                elif effect['type'] == 'status':
                    self.log_message(f"  → {effect['target']} gained {effect['amount']} {effect['status']}")
        else:
            messagebox.showwarning("Cannot Play Card", result.get('message', 'Unknown error'))
        
        self.update_ui()
    
    def end_turn(self):
        """End the player's turn."""
        if not self.current_combat:
            return
        
        self.log_message("\n--- Ending Turn ---")
        self.current_combat.end_player_turn()
        self.update_ui()
    
    def start_new_combat(self):
        """Start a new combat."""
        self.log_message("=" * 50)
        self.log_message("Starting new combat...")
        self.current_combat = self.game.start_new_combat()
        self.log_message(f"Floor {self.game.floor}")
        self.update_ui()


def main():
    """Run the GUI application."""
    root = tk.Tk()
    app = CardBattlerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

