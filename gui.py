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
    
    # Color scheme
    COLORS = {
        'bg_dark': '#1a1a2e',
        'bg_medium': '#16213e',
        'bg_light': '#0f3460',
        'card_bg': '#667eea',
        'card_bg_hover': '#764ba2',
        'card_disabled': '#4a5568',
        'text_light': '#ffffff',
        'text_dark': '#2d3748',
        'hp_high': '#48bb78',
        'hp_medium': '#ed8936',
        'hp_low': '#f56565',
        'block': '#4ecdc4',
        'energy': '#ffe66d',
        'enemy_bg': '#dc3545',
        'enemy_border': '#c82333',
        'log_bg': '#2d3748',
        'log_text': '#e2e8f0',
    }
    
    def __init__(self, root):
        """Initialize the GUI."""
        self.root = root
        self.root.title("⚔️ Card Battler - Slay the Spire Lite")
        self.root.geometry("1400x900")
        self.root.configure(bg=self.COLORS['bg_dark'])
        
        # Configure style
        self.setup_styles()
        
        self.game = Game()
        self.current_combat = None
        
        self.setup_ui()
        self.start_new_combat()
    
    def setup_styles(self):
        """Configure custom styles for widgets."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure frame styles
        style.configure('Dark.TFrame', background=self.COLORS['bg_dark'])
        style.configure('Medium.TFrame', background=self.COLORS['bg_medium'])
        style.configure('Card.TFrame', background=self.COLORS['card_bg'], relief='raised', borderwidth=2)
        
        # Configure label frame styles
        style.configure('Title.TLabelframe', background=self.COLORS['bg_medium'], 
                       foreground=self.COLORS['text_light'], borderwidth=2, relief='raised')
        style.configure('Title.TLabelframe.Label', background=self.COLORS['bg_medium'],
                       foreground=self.COLORS['text_light'], font=('Arial', 14, 'bold'))
        
        # Configure button styles
        style.configure('Action.TButton', font=('Arial', 11, 'bold'), padding=10)
        style.configure('Card.TButton', font=('Arial', 10), padding=8)
    
    def setup_ui(self):
        """Set up the user interface."""
        # Main container with dark background
        main_frame = tk.Frame(self.root, bg=self.COLORS['bg_dark'], padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="⚔️ CARD BATTLER ⚔️",
            font=('Arial', 24, 'bold'),
            bg=self.COLORS['bg_dark'],
            fg=self.COLORS['text_light']
        )
        title_label.pack(pady=(0, 15))
        
        # Content area
        content_frame = tk.Frame(main_frame, bg=self.COLORS['bg_dark'])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Player info and cards
        left_panel = tk.Frame(content_frame, bg=self.COLORS['bg_medium'], relief='raised', borderwidth=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Player stats frame
        player_frame = tk.LabelFrame(
            left_panel,
            text=" 👤 PLAYER ",
            font=('Arial', 14, 'bold'),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text_light'],
            padx=15,
            pady=15,
            relief='raised',
            borderwidth=2
        )
        player_frame.pack(fill=tk.X, pady=(10, 10), padx=10)
        
        # Player stats with visual bars
        stats_container = tk.Frame(player_frame, bg=self.COLORS['bg_medium'])
        stats_container.pack(fill=tk.X)
        
        # HP with bar
        hp_container = tk.Frame(stats_container, bg=self.COLORS['bg_medium'])
        hp_container.pack(fill=tk.X, pady=5)
        self.player_hp_label = tk.Label(
            hp_container,
            text="❤️ HP: 80/80",
            font=('Arial', 12, 'bold'),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['hp_high'],
            anchor='w'
        )
        self.player_hp_label.pack(fill=tk.X)
        self.player_hp_bar = tk.Canvas(hp_container, height=20, width=300, bg=self.COLORS['bg_dark'], highlightthickness=0)
        self.player_hp_bar.pack(fill=tk.X, pady=(5, 0))
        
        # Block
        self.player_block_label = tk.Label(
            stats_container,
            text="🛡️ Block: 0",
            font=('Arial', 11, 'bold'),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['block'],
            anchor='w'
        )
        self.player_block_label.pack(fill=tk.X, pady=5)
        
        # Energy
        self.player_energy_label = tk.Label(
            stats_container,
            text="⚡ Energy: 3/3",
            font=('Arial', 11, 'bold'),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['energy'],
            anchor='w'
        )
        self.player_energy_label.pack(fill=tk.X, pady=5)
        
        # Hand cards frame
        hand_frame = tk.LabelFrame(
            left_panel,
            text=" 🃏 YOUR HAND ",
            font=('Arial', 14, 'bold'),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text_light'],
            padx=10,
            pady=10,
            relief='raised',
            borderwidth=2
        )
        hand_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Scrollable frame for cards
        canvas = tk.Canvas(hand_frame, bg=self.COLORS['bg_medium'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(hand_frame, orient="vertical", command=canvas.yview)
        self.cards_container = tk.Frame(canvas, bg=self.COLORS['bg_medium'])
        
        self.cards_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.cards_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        self.card_buttons = []
        
        # Right panel - Enemies and combat log
        right_panel = tk.Frame(content_frame, bg=self.COLORS['bg_medium'], relief='raised', borderwidth=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Enemies frame
        enemies_frame = tk.LabelFrame(
            right_panel,
            text=" 👹 ENEMIES ",
            font=('Arial', 14, 'bold'),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text_light'],
            padx=15,
            pady=15,
            relief='raised',
            borderwidth=2
        )
        enemies_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 10))
        
        # Scrollable enemies container
        enemies_canvas = tk.Canvas(enemies_frame, bg=self.COLORS['bg_medium'], highlightthickness=0)
        enemies_scrollbar = ttk.Scrollbar(enemies_frame, orient="vertical", command=enemies_canvas.yview)
        self.enemies_container = tk.Frame(enemies_canvas, bg=self.COLORS['bg_medium'])
        
        self.enemies_container.bind(
            "<Configure>",
            lambda e: enemies_canvas.configure(scrollregion=enemies_canvas.bbox("all"))
        )
        
        enemies_canvas.create_window((0, 0), window=self.enemies_container, anchor="nw")
        enemies_canvas.configure(yscrollcommand=enemies_scrollbar.set)
        
        enemies_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        enemies_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.enemy_labels = []
        
        # Combat log frame
        log_frame = tk.LabelFrame(
            right_panel,
            text=" 📜 COMBAT LOG ",
            font=('Arial', 14, 'bold'),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text_light'],
            padx=10,
            pady=10,
            relief='raised',
            borderwidth=2
        )
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.combat_log = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            wrap=tk.WORD,
            bg=self.COLORS['log_bg'],
            fg=self.COLORS['log_text'],
            font=('Courier New', 10),
            insertbackground=self.COLORS['text_light'],
            selectbackground=self.COLORS['card_bg']
        )
        self.combat_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.combat_log.config(state=tk.DISABLED)
        
        # Configure text tags for colored log messages
        self.combat_log.tag_config("damage", foreground="#ff6b6b")
        self.combat_log.tag_config("block", foreground="#4ecdc4")
        self.combat_log.tag_config("energy", foreground="#ffe66d")
        self.combat_log.tag_config("played", foreground="#667eea", font=('Courier New', 10, 'bold'))
        
        # Bottom panel - Controls
        controls_frame = tk.Frame(main_frame, bg=self.COLORS['bg_dark'])
        controls_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.end_turn_btn = tk.Button(
            controls_frame,
            text="⏭️ END TURN",
            command=self.end_turn,
            font=('Arial', 12, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text_light'],
            activebackground=self.COLORS['card_bg_hover'],
            activeforeground=self.COLORS['text_light'],
            relief='raised',
            borderwidth=3,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        self.end_turn_btn.pack(side=tk.LEFT, padx=10)
        
        self.new_combat_btn = tk.Button(
            controls_frame,
            text="🔄 NEW COMBAT",
            command=self.start_new_combat,
            font=('Arial', 12, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text_light'],
            activebackground=self.COLORS['card_bg_hover'],
            activeforeground=self.COLORS['text_light'],
            relief='raised',
            borderwidth=3,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        self.new_combat_btn.pack(side=tk.LEFT, padx=10)
        
        self.quit_btn = tk.Button(
            controls_frame,
            text="❌ QUIT",
            command=self.root.quit,
            font=('Arial', 12, 'bold'),
            bg='#c82333',
            fg=self.COLORS['text_light'],
            activebackground='#bd2130',
            activeforeground=self.COLORS['text_light'],
            relief='raised',
            borderwidth=3,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        self.quit_btn.pack(side=tk.LEFT, padx=10)
    
    def log_message(self, message):
        """Add a message to the combat log."""
        self.combat_log.config(state=tk.NORMAL)
        # Add color tags for different message types
        if "damage" in message.lower():
            self.combat_log.insert(tk.END, message + "\n", "damage")
        elif "block" in message.lower():
            self.combat_log.insert(tk.END, message + "\n", "block")
        elif "energy" in message.lower():
            self.combat_log.insert(tk.END, message + "\n", "energy")
        elif "played" in message.lower():
            self.combat_log.insert(tk.END, message + "\n", "played")
        else:
            self.combat_log.insert(tk.END, message + "\n")
        
        self.combat_log.see(tk.END)
        self.combat_log.config(state=tk.DISABLED)
    
    def update_ui(self):
        """Update the UI with current game state."""
        if not self.current_combat:
            return
        
        # Update player stats
        player = self.game.player
        hp_percent = player.current_hp / player.max_hp
        
        # Update HP label with color
        hp_color = self.COLORS['hp_high'] if hp_percent > 0.5 else self.COLORS['hp_medium'] if hp_percent > 0.25 else self.COLORS['hp_low']
        self.player_hp_label.config(
            text=f"❤️ HP: {player.current_hp}/{player.max_hp}",
            fg=hp_color
        )
        
        # Update HP bar
        self.player_hp_bar.delete("all")
        self.player_hp_bar.update_idletasks()  # Ensure widget is rendered
        bar_width = max(self.player_hp_bar.winfo_width(), 200)
        bar_fill_width = int(bar_width * hp_percent)
        self.player_hp_bar.create_rectangle(0, 0, bar_width, 20, fill=self.COLORS['bg_dark'], outline='')
        if bar_fill_width > 0:
            self.player_hp_bar.create_rectangle(0, 0, bar_fill_width, 20, fill=hp_color, outline='')
        self.player_hp_bar.create_text(bar_width//2, 10, text=f"{player.current_hp}/{player.max_hp}", 
                                       fill=self.COLORS['text_light'], font=('Arial', 9, 'bold'))
        
        self.player_block_label.config(text=f"🛡️ Block: {player.block}")
        self.player_energy_label.config(text=f"⚡ Energy: {player.energy}/{player.max_energy}")
        
        # Update hand
        self.update_hand()
        
        # Update enemies
        self.update_enemies()
        
        # Check victory/defeat
        if self.current_combat.is_victory():
            messagebox.showinfo("🎉 Victory!", "You defeated all enemies!")
            self.start_new_combat()
        elif self.current_combat.is_defeat():
            messagebox.showerror("💀 Defeat", "You have been defeated!")
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
            # Check if can afford
            can_play = player.energy >= card.get_cost()
            
            # Create card frame with visual styling
            card_frame = tk.Frame(
                self.cards_container,
                bg=self.COLORS['card_bg'] if can_play else self.COLORS['card_disabled'],
                relief='raised',
                borderwidth=3,
                padx=12,
                pady=10
            )
            card_frame.pack(fill=tk.X, pady=8, padx=5)
            
            # Card header with cost and name
            header_frame = tk.Frame(card_frame, bg=card_frame['bg'])
            header_frame.pack(fill=tk.X, pady=(0, 5))
            
            # Cost badge
            cost_badge = tk.Label(
                header_frame,
                text=f" {card.get_cost()} ",
                font=('Arial', 12, 'bold'),
                bg=self.COLORS['text_light'],
                fg=self.COLORS['card_bg'],
                relief='raised',
                borderwidth=2
            )
            cost_badge.pack(side=tk.LEFT, padx=(0, 10))
            
            # Card name
            name_label = tk.Label(
                header_frame,
                text=card.name,
                font=('Arial', 13, 'bold'),
                bg=card_frame['bg'],
                fg=self.COLORS['text_light'],
                anchor='w'
            )
            name_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Card description
            desc_label = tk.Label(
                card_frame,
                text=card.description,
                font=('Arial', 10),
                bg=card_frame['bg'],
                fg=self.COLORS['text_light'],
                anchor='w',
                wraplength=400,
                justify='left'
            )
            desc_label.pack(fill=tk.X, pady=(0, 5))
            
            # Card stats
            stats_frame = tk.Frame(card_frame, bg=card_frame['bg'])
            stats_frame.pack(fill=tk.X)
            
            stats_parts = []
            if card.get_damage() > 0:
                stats_parts.append(f"⚔️ {card.get_damage()}")
            if card.get_block() > 0:
                stats_parts.append(f"🛡️ {card.get_block()}")
            if card.card_draw > 0:
                stats_parts.append(f"📖 +{card.card_draw}")
            if card.energy_gain > 0:
                stats_parts.append(f"⚡ +{card.energy_gain}")
            
            if stats_parts:
                stats_label = tk.Label(
                    stats_frame,
                    text="  |  ".join(stats_parts),
                    font=('Arial', 10, 'bold'),
                    bg=card_frame['bg'],
                    fg=self.COLORS['text_light']
                )
                stats_label.pack(anchor='w')
            
            # Make card clickable
            if can_play:
                def make_play_func(c, idx):
                    def play_func(event=None):
                        self.play_card(c, idx)
                    return play_func
                
                play_func = make_play_func(card, i)
                card_frame.bind('<Button-1>', play_func)
                card_frame.bind('<Enter>', lambda e, f=card_frame: f.config(bg=self.COLORS['card_bg_hover']))
                card_frame.bind('<Leave>', lambda e, f=card_frame: f.config(bg=self.COLORS['card_bg']))
                card_frame.config(cursor='hand2')
                
                # Make all child widgets clickable too
                for widget in [header_frame, name_label, desc_label, stats_frame, cost_badge]:
                    if widget:
                        widget.bind('<Button-1>', play_func)
                        widget.config(cursor='hand2')
                        if isinstance(widget, tk.Frame):
                            widget.config(bg=card_frame['bg'])
            
            self.card_buttons.append(card_frame)
    
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
            
            # Enemy frame with visual styling
            enemy_frame = tk.Frame(
                self.enemies_container,
                bg=self.COLORS['enemy_bg'],
                relief='raised',
                borderwidth=3,
                padx=15,
                pady=12
            )
            enemy_frame.pack(fill=tk.X, pady=8, padx=5)
            
            # Enemy name
            hp_percent = enemy.current_hp / enemy.max_hp
            hp_color = self.COLORS['hp_high'] if hp_percent > 0.5 else self.COLORS['hp_medium'] if hp_percent > 0.25 else self.COLORS['hp_low']
            
            name_label = tk.Label(
                enemy_frame,
                text=f"👹 {enemy.name}",
                font=('Arial', 14, 'bold'),
                bg=self.COLORS['enemy_bg'],
                fg=self.COLORS['text_light'],
                anchor='w'
            )
            name_label.pack(fill=tk.X, pady=(0, 8))
            
            # HP with visual bar
            hp_label = tk.Label(
                enemy_frame,
                text=f"❤️ HP: {enemy.current_hp}/{enemy.max_hp}",
                font=('Arial', 11, 'bold'),
                bg=self.COLORS['enemy_bg'],
                fg=hp_color,
                anchor='w'
            )
            hp_label.pack(fill=tk.X, pady=(0, 5))
            
            # HP bar
            hp_bar_canvas = tk.Canvas(enemy_frame, height=18, bg=self.COLORS['bg_dark'], highlightthickness=0)
            hp_bar_canvas.pack(fill=tk.X, pady=(0, 8))
            bar_width = 300  # Fixed width for enemy HP bars
            bar_fill_width = int(bar_width * hp_percent)
            hp_bar_canvas.create_rectangle(0, 0, bar_width, 18, fill=self.COLORS['bg_dark'], outline='')
            hp_bar_canvas.create_rectangle(0, 0, bar_fill_width, 18, fill=hp_color, outline='')
            hp_bar_canvas.create_text(bar_width//2, 9, text=f"{enemy.current_hp}/{enemy.max_hp}", 
                                     fill=self.COLORS['text_light'], font=('Arial', 9, 'bold'))
            
            # Block
            if enemy.block > 0:
                block_label = tk.Label(
                    enemy_frame,
                    text=f"🛡️ Block: {enemy.block}",
                    font=('Arial', 10, 'bold'),
                    bg=self.COLORS['enemy_bg'],
                    fg=self.COLORS['block'],
                    anchor='w'
                )
                block_label.pack(fill=tk.X, pady=(0, 5))
            
            # Intent
            if enemy.intent_description:
                intent_label = tk.Label(
                    enemy_frame,
                    text=f"🎯 {enemy.intent_description}",
                    font=('Arial', 10, 'italic'),
                    bg=self.COLORS['enemy_bg'],
                    fg=self.COLORS['text_light'],
                    anchor='w'
                )
                intent_label.pack(fill=tk.X, pady=(0, 5))
            
            # Status effects
            statuses = enemy.status_manager.get_all()
            if statuses:
                status_text = "✨ " + "  |  ".join([
                    f"{name} ({effect.amount})" 
                    for name, effect in statuses.items()
                ])
                status_label = tk.Label(
                    enemy_frame,
                    text=status_text,
                    font=('Arial', 9),
                    bg=self.COLORS['enemy_bg'],
                    fg='#d4a5ff',
                    anchor='w'
                )
                status_label.pack(fill=tk.X)
            
            self.enemy_labels.append(enemy_frame)
    
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

