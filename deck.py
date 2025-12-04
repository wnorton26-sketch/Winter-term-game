"""
Deck management system for the card battler game.
Handles deck, draw pile, discard pile, and hand management.
"""

import random
from typing import List, Optional
from card import Card


class Deck:
    """Manages a deck of cards including draw pile, discard pile, and hand."""
    
    def __init__(self, cards: List[Card] = None):
        """Initialize deck with cards."""
        self.draw_pile: List[Card] = cards.copy() if cards else []
        self.discard_pile: List[Card] = []
        self.hand: List[Card] = []
        self.exhaust_pile: List[Card] = []  # Cards removed from combat
        
        # Shuffle the draw pile
        self.shuffle()
    
    def shuffle(self):
        """Shuffle the draw pile."""
        random.shuffle(self.draw_pile)
    
    def draw(self, count: int = 1) -> List[Card]:
        """Draw cards from the draw pile."""
        drawn = []
        for _ in range(count):
            if not self.draw_pile:
                # Reshuffle discard pile into draw pile
                if self.discard_pile:
                    self.draw_pile = self.discard_pile.copy()
                    self.discard_pile.clear()
                    self.shuffle()
                else:
                    break  # No more cards to draw
            
            if self.draw_pile:
                card = self.draw_pile.pop(0)
                self.hand.append(card)
                drawn.append(card)
        
        return drawn
    
    def discard_hand(self):
        """Discard all cards in hand."""
        self.discard_pile.extend(self.hand)
        self.hand.clear()
    
    def discard_card(self, card: Card):
        """Discard a specific card from hand."""
        if card in self.hand:
            self.hand.remove(card)
            self.discard_pile.append(card)
    
    def exhaust_card(self, card: Card):
        """Exhaust (remove) a card from hand."""
        if card in self.hand:
            self.hand.remove(card)
            self.exhaust_pile.append(card)
    
    def add_card(self, card: Card, to_draw_pile: bool = True):
        """Add a card to the deck."""
        if to_draw_pile:
            self.draw_pile.append(card)
        else:
            self.discard_pile.append(card)
    
    def remove_card(self, card: Card):
        """Remove a card from the deck entirely."""
        if card in self.draw_pile:
            self.draw_pile.remove(card)
        if card in self.discard_pile:
            self.discard_pile.remove(card)
        if card in self.hand:
            self.hand.remove(card)
    
    def get_hand_size(self) -> int:
        """Get the number of cards in hand."""
        return len(self.hand)
    
    def get_draw_pile_size(self) -> int:
        """Get the number of cards in draw pile."""
        return len(self.draw_pile)
    
    def get_discard_pile_size(self) -> int:
        """Get the number of cards in discard pile."""
        return len(self.discard_pile)
    
    def get_total_cards(self) -> int:
        """Get total number of cards in deck (excluding exhaust pile)."""
        return len(self.draw_pile) + len(self.discard_pile) + len(self.hand)
    
    def reset_for_combat(self):
        """Reset deck for a new combat (combine all piles, shuffle, draw starting hand)."""
        # Combine all cards back into draw pile
        self.draw_pile.extend(self.discard_pile)
        self.draw_pile.extend(self.hand)
        self.discard_pile.clear()
        self.hand.clear()
        # Note: exhaust_pile stays separate
        
        self.shuffle()
    
    def get_hand(self) -> List[Card]:
        """Get current hand."""
        return self.hand.copy()
    
    def to_dict(self) -> dict:
        """Convert deck to dictionary for serialization."""
        return {
            'draw_pile': [card.to_dict() for card in self.draw_pile],
            'discard_pile': [card.to_dict() for card in self.discard_pile],
            'hand': [card.to_dict() for card in self.hand],
            'exhaust_pile': [card.to_dict() for card in self.exhaust_pile]
        }

