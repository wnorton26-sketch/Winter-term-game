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
    
    # Pixel-art card game color scheme - improved for better readability
    COLORS = {
        'bg_dark': '#1a3a1a',  # Dark green background
        'bg_medium': '#2d4d2d',  # Medium green
        'bg_light': '#3d5d3d',  # Light green
        'panel_bg': '#2a3a2a',  # Dark brown/green panel
        'card_bg': '#ffffff',  # White card background
        'card_border': '#000000',  # Black card border
        'card_hover': '#ffff88',  # Brighter yellow hover
        'card_disabled': '#888888',  # Gray disabled
        'text_light': '#ffffff',
        'text_dark': '#000000',
        'text_accent': '#ffff00',  # Yellow accent
        'hp_high': '#00ff00',  # Green
        'hp_medium': '#ffaa00',  # Orange
        'hp_low': '#ff0000',  # Red
        'block': '#00aaff',  # Blue
        'energy': '#ffff00',  # Yellow
        'enemy_bg': '#4a2a2a',  # Dark red/brown
        'enemy_border': '#8a4a4a',  # Red border
        'log_bg': '#1a2a1a',  # Very dark green
        'log_text': '#aaffaa',  # Light green text
        'button_bg': '#ff6600',  # Bright orange for visibility
        'button_text': '#000000',  # Black text for contrast
        'button_hover': '#ff8833',  # Lighter orange on hover
        'button_end_turn': '#00ff00',  # Bright green for END TURN
        'button_end_turn_hover': '#33ff33',  # Lighter green
        'button_new': '#0066ff',  # Bright blue for NEW COMBAT
        'button_new_hover': '#3388ff',  # Lighter blue
    }
    
    def __init__(self, root):
        """Initialize the GUI."""
        self.root = root
        self.root.title("Card Battler")
        self.root.geometry("1600x1000")
        self.root.configure(bg=self.COLORS['bg_dark'])
        
        # Use pixelated font if available, otherwise use monospace
        self.font_family = 'Courier New'  # Pixel-art style font
        self.font_size_normal = 11
        self.font_size_large = 13
        self.font_size_title = 15
        
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
        """Set up the user interface in pixel-art card game style."""
        # Main container with dark green background
        main_frame = tk.Frame(self.root, bg=self.COLORS['bg_dark'], padx=0, pady=0)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Content area - horizontal layout
        content_frame = tk.Frame(main_frame, bg=self.COLORS['bg_dark'])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Game state and player info (like the image) - improved
        left_panel = tk.Frame(content_frame, bg=self.COLORS['panel_bg'], width=320, relief='sunken', borderwidth=4)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=8)
        left_panel.pack_propagate(False)
        
        # Enemy/Combat title (like "Big Blind" in the image) - improved
        enemy_title_frame = tk.Frame(left_panel, bg=self.COLORS['bg_light'], relief='raised', borderwidth=2)
        enemy_title_frame.pack(fill=tk.X, padx=8, pady=8)
        
        enemy_title_label = tk.Label(
            enemy_title_frame,
            text="ENEMY",
            font=(self.font_family, self.font_size_title, 'bold'),
            bg=self.COLORS['bg_light'],
            fg=self.COLORS['text_light']
        )
        enemy_title_label.pack(pady=8)
        
        # Round/Floor info - improved
        round_frame = tk.Frame(left_panel, bg=self.COLORS['panel_bg'])
        round_frame.pack(fill=tk.X, padx=8, pady=5)
        
        self.round_label = tk.Label(
            round_frame,
            text="Floor: 1",
            font=(self.font_family, self.font_size_normal, 'bold'),
            bg=self.COLORS['panel_bg'],
            fg=self.COLORS['text_accent'],
            anchor='w'
        )
        self.round_label.pack(fill=tk.X)
        
        # Player stats - compact display - improved
        stats_frame = tk.Frame(left_panel, bg=self.COLORS['bg_light'], relief='sunken', borderwidth=2)
        stats_frame.pack(fill=tk.X, padx=8, pady=8)
        
        self.player_hp_label = tk.Label(
            stats_frame,
            text="HP: 80/80",
            font=(self.font_family, self.font_size_normal, 'bold'),
            bg=self.COLORS['bg_light'],
            fg=self.COLORS['hp_high'],
            anchor='w'
        )
        self.player_hp_label.pack(fill=tk.X, padx=8, pady=4)
        
        self.player_block_label = tk.Label(
            stats_frame,
            text="Block: 0",
            font=(self.font_family, self.font_size_normal, 'bold'),
            bg=self.COLORS['bg_light'],
            fg=self.COLORS['block'],
            anchor='w'
        )
        self.player_block_label.pack(fill=tk.X, padx=8, pady=4)
        
        self.player_energy_label = tk.Label(
            stats_frame,
            text="Energy: 3/3",
            font=(self.font_family, self.font_size_normal, 'bold'),
            bg=self.COLORS['bg_light'],
            fg=self.COLORS['energy'],
            anchor='w'
        )
        self.player_energy_label.pack(fill=tk.X, padx=8, pady=4)
        
        # Hand count - improved
        hand_info_frame = tk.Frame(left_panel, bg=self.COLORS['panel_bg'])
        hand_info_frame.pack(fill=tk.X, padx=8, pady=5)
        
        self.hand_count_label = tk.Label(
            hand_info_frame,
            text="Hand: 5",
            font=(self.font_family, self.font_size_normal, 'bold'),
            bg=self.COLORS['panel_bg'],
            fg=self.COLORS['text_accent'],
            anchor='w'
        )
        self.hand_count_label.pack(fill=tk.X)
        
        # Controls at bottom of left panel - improved visibility
        controls_left_frame = tk.Frame(left_panel, bg=self.COLORS['panel_bg'])
        controls_left_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=10)
        
        self.end_turn_btn = tk.Button(
            controls_left_frame,
            text="END TURN",
            command=self.end_turn,
            font=(self.font_family, self.font_size_large, 'bold'),
            bg=self.COLORS['button_end_turn'],
            fg=self.COLORS['text_dark'],
            activebackground=self.COLORS['button_end_turn_hover'],
            activeforeground=self.COLORS['text_dark'],
            relief='raised',
            borderwidth=3,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        self.end_turn_btn.pack(fill=tk.X, pady=3)
        # Add hover effect
        self.end_turn_btn.bind('<Enter>', lambda e: self.end_turn_btn.config(bg=self.COLORS['button_end_turn_hover']))
        self.end_turn_btn.bind('<Leave>', lambda e: self.end_turn_btn.config(bg=self.COLORS['button_end_turn']))
        
        self.new_combat_btn = tk.Button(
            controls_left_frame,
            text="NEW COMBAT",
            command=self.start_new_combat,
            font=(self.font_family, self.font_size_large, 'bold'),
            bg=self.COLORS['button_new'],
            fg=self.COLORS['text_light'],
            activebackground=self.COLORS['button_new_hover'],
            activeforeground=self.COLORS['text_light'],
            relief='raised',
            borderwidth=3,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        self.new_combat_btn.pack(fill=tk.X, pady=3)
        # Add hover effect
        self.new_combat_btn.bind('<Enter>', lambda e: self.new_combat_btn.config(bg=self.COLORS['button_new_hover']))
        self.new_combat_btn.bind('<Leave>', lambda e: self.new_combat_btn.config(bg=self.COLORS['button_new']))
        
        # Right panel - Main play area with cards
        right_panel = tk.Frame(content_frame, bg=self.COLORS['bg_dark'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Card play area - cards displayed in rows
        card_area = tk.Frame(right_panel, bg=self.COLORS['bg_dark'])
        card_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Enemies row (top)
        enemies_row_frame = tk.Frame(card_area, bg=self.COLORS['bg_dark'])
        enemies_row_frame.pack(fill=tk.X, pady=(0, 10))
        
        enemies_label = tk.Label(
            enemies_row_frame,
            text="ENEMIES",
            font=(self.font_family, self.font_size_large, 'bold'),
            bg=self.COLORS['bg_dark'],
            fg=self.COLORS['text_light']
        )
        enemies_label.pack(anchor='w', pady=(0, 5))
        
        self.enemies_container = tk.Frame(enemies_row_frame, bg=self.COLORS['bg_dark'])
        self.enemies_container.pack(fill=tk.X)
        
        self.enemy_labels = []
        
        # Player hand row (bottom) - cards displayed horizontally
        hand_row_frame = tk.Frame(card_area, bg=self.COLORS['bg_dark'])
        hand_row_frame.pack(fill=tk.X, pady=(10, 0))
        
        hand_label = tk.Label(
            hand_row_frame,
            text="YOUR HAND",
            font=(self.font_family, self.font_size_large, 'bold'),
            bg=self.COLORS['bg_dark'],
            fg=self.COLORS['text_light']
        )
        hand_label.pack(anchor='w', pady=(0, 5))
        
        # Scrollable horizontal container for hand cards
        hand_canvas = tk.Canvas(hand_row_frame, bg=self.COLORS['bg_dark'], highlightthickness=0, height=200)
        hand_scrollbar = ttk.Scrollbar(hand_row_frame, orient="horizontal", command=hand_canvas.xview)
        self.cards_container = tk.Frame(hand_canvas, bg=self.COLORS['bg_dark'])
        
        self.cards_container.bind(
            "<Configure>",
            lambda e: hand_canvas.configure(scrollregion=hand_canvas.bbox("all"))
        )
        
        hand_canvas.create_window((0, 0), window=self.cards_container, anchor="nw")
        hand_canvas.configure(xscrollcommand=hand_scrollbar.set)
        
        hand_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        hand_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.card_buttons = []
        
        # Combat log at bottom
        log_frame = tk.Frame(right_panel, bg=self.COLORS['bg_dark'], relief='sunken', borderwidth=2)
        log_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=5, ipady=5)
        
        log_label = tk.Label(
            log_frame,
            text="COMBAT LOG",
            font=(self.font_family, self.font_size_normal, 'bold'),
            bg=self.COLORS['bg_dark'],
            fg=self.COLORS['text_light']
        )
        log_label.pack(anchor='w', padx=5, pady=2)
        
        self.combat_log = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            wrap=tk.WORD,
            bg=self.COLORS['log_bg'],
            fg=self.COLORS['log_text'],
            font=(self.font_family, 9),
            insertbackground=self.COLORS['text_light'],
            selectbackground=self.COLORS['card_bg'],
            relief='flat',
            borderwidth=0
        )
        self.combat_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.combat_log.config(state=tk.DISABLED)
        
        # Configure text tags for colored log messages
        self.combat_log.tag_config("damage", foreground="#ff0000")
        self.combat_log.tag_config("block", foreground="#00aaff")
        self.combat_log.tag_config("energy", foreground="#ffff00")
        self.combat_log.tag_config("played", foreground="#ffff00", font=(self.font_family, 9, 'bold'))
        
    
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
            text=f"HP: {player.current_hp}/{player.max_hp}",
            fg=hp_color
        )
        
        self.player_block_label.config(text=f"Block: {player.block}")
        self.player_energy_label.config(text=f"Energy: {player.energy}/{player.max_energy}")
        
        # Update round/floor
        self.round_label.config(text=f"Floor: {self.game.floor}")
        
        # Update hand count
        hand = self.current_combat.get_available_cards()
        self.hand_count_label.config(text=f"Hand: {len(hand)}")
        
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
        """Update the hand display in pixel-art card style."""
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
            
            # Create card frame - pixel-art style card (horizontal layout) - improved design
            card_frame = tk.Frame(
                self.cards_container,
                bg=self.COLORS['card_bg'] if can_play else self.COLORS['card_disabled'],
                relief='raised',
                borderwidth=3,
                width=150,
                height=200
            )
            card_frame.pack(side=tk.LEFT, padx=8, pady=8)
            card_frame.pack_propagate(False)
            
            # Card content - pixel-art style - improved
            # Cost badge in top-left corner (more prominent)
            cost_bg = '#ffaa00' if can_play else '#666666'
            cost_label = tk.Label(
                card_frame,
                text=f" {card.get_cost()} ",
                font=(self.font_family, self.font_size_large, 'bold'),
                bg=cost_bg,
                fg=self.COLORS['text_dark'],
                relief='raised',
                borderwidth=2
            )
            cost_label.place(x=8, y=8)
            
            # Card name (centered, bold) - improved spacing
            name_label = tk.Label(
                card_frame,
                text=card.name.upper(),
                font=(self.font_family, self.font_size_normal, 'bold'),
                bg=card_frame['bg'],
                fg=self.COLORS['text_dark'],
                wraplength=130,
                justify='center'
            )
            name_label.place(relx=0.5, rely=0.35, anchor='center')
            
            # Card stats/icons in center
            stats_text = ""
            if card.get_damage() > 0:
                stats_text += f"{card.get_damage()}\n"
            if card.get_block() > 0:
                stats_text += f"+{card.get_block()}\n"
            if card.card_draw > 0:
                stats_text += f"Draw {card.card_draw}\n"
            if card.energy_gain > 0:
                stats_text += f"+{card.energy_gain} Energy"
            
            if stats_text:
                stats_label = tk.Label(
                    card_frame,
                    text=stats_text.strip(),
                    font=(self.font_family, self.font_size_normal),
                    bg=card_frame['bg'],
                    fg=self.COLORS['text_dark'],
                    justify='center'
                )
                stats_label.place(relx=0.5, rely=0.6, anchor='center')
            
            # Make card clickable
            if can_play:
                def make_play_func(c, idx):
                    def play_func(event=None):
                        self.play_card(c, idx)
                    return play_func
                
                play_func = make_play_func(card, i)
                card_frame.bind('<Button-1>', play_func)
                # Improved hover effect
                def on_enter(e):
                    card_frame.config(bg=self.COLORS['card_hover'], relief='sunken', borderwidth=4)
                    cost_label.config(bg='#ffcc00')
                def on_leave(e):
                    card_frame.config(bg=self.COLORS['card_bg'], relief='raised', borderwidth=3)
                    cost_label.config(bg='#ffaa00')
                card_frame.bind('<Enter>', on_enter)
                card_frame.bind('<Leave>', on_leave)
                card_frame.config(cursor='hand2')
                
                # Make all child widgets clickable too
                for widget in [cost_label, name_label]:
                    if widget:
                        widget.bind('<Button-1>', play_func)
                        widget.config(cursor='hand2')
                if stats_text:
                    stats_label.bind('<Button-1>', play_func)
                    stats_label.config(cursor='hand2')
            else:
                # Gray out disabled cards
                card_frame.config(bg=self.COLORS['card_disabled'])
                cost_label.config(bg=self.COLORS['card_disabled'], fg='#666666')
                name_label.config(bg=self.COLORS['card_disabled'], fg='#666666')
                if stats_text:
                    stats_label.config(bg=self.COLORS['card_disabled'], fg='#666666')
            
            self.card_buttons.append(card_frame)
    
    def update_enemies(self):
        """Update the enemies display in pixel-art card style."""
        # Clear existing labels
        for widget in self.enemies_container.winfo_children():
            widget.destroy()
        self.enemy_labels.clear()
        
        if not self.current_combat:
            return
        
        for i, enemy in enumerate(self.current_combat.enemies):
            if not enemy.is_alive():
                continue
            
            # Enemy card - pixel-art style (displayed horizontally)
            hp_percent = enemy.current_hp / enemy.max_hp
            hp_color = self.COLORS['hp_high'] if hp_percent > 0.5 else self.COLORS['hp_medium'] if hp_percent > 0.25 else self.COLORS['hp_low']
            
            enemy_frame = tk.Frame(
                self.enemies_container,
                bg=self.COLORS['enemy_bg'],
                relief='raised',
                borderwidth=3,
                width=170,
                height=210
            )
            enemy_frame.pack(side=tk.LEFT, padx=8, pady=8)
            enemy_frame.pack_propagate(False)
            
            # Enemy name
            name_label = tk.Label(
                enemy_frame,
                text=enemy.name.upper(),
                font=(self.font_family, self.font_size_normal, 'bold'),
                bg=self.COLORS['enemy_bg'],
                fg=self.COLORS['text_light'],
                wraplength=140,
                justify='center'
            )
            name_label.place(relx=0.5, rely=0.15, anchor='center')
            
            # HP display
            hp_label = tk.Label(
                enemy_frame,
                text=f"HP: {enemy.current_hp}/{enemy.max_hp}",
                font=(self.font_family, self.font_size_normal),
                bg=self.COLORS['enemy_bg'],
                fg=hp_color,
                justify='center'
            )
            hp_label.place(relx=0.5, rely=0.4, anchor='center')
            
            # HP bar (simple visual)
            hp_bar = tk.Canvas(enemy_frame, width=140, height=12, bg=self.COLORS['bg_dark'], highlightthickness=0)
            hp_bar.place(relx=0.5, rely=0.55, anchor='center')
            bar_fill_width = int(140 * hp_percent)
            hp_bar.create_rectangle(0, 0, 140, 12, fill=self.COLORS['bg_dark'], outline='')
            if bar_fill_width > 0:
                hp_bar.create_rectangle(0, 0, bar_fill_width, 12, fill=hp_color, outline='')
            
            # Block
            if enemy.block > 0:
                block_label = tk.Label(
                    enemy_frame,
                    text=f"Block: {enemy.block}",
                    font=(self.font_family, self.font_size_normal),
                    bg=self.COLORS['enemy_bg'],
                    fg=self.COLORS['block'],
                    justify='center'
                )
                block_label.place(relx=0.5, rely=0.7, anchor='center')
            
            # Intent
            if enemy.intent_description:
                intent_label = tk.Label(
                    enemy_frame,
                    text=enemy.intent_description[:20],
                    font=(self.font_family, 8),
                    bg=self.COLORS['enemy_bg'],
                    fg=self.COLORS['text_light'],
                    wraplength=140,
                    justify='center'
                )
                intent_label.place(relx=0.5, rely=0.85, anchor='center')
            
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

