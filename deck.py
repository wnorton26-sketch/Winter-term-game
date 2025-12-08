"""
Deck management system for the card battler game.
Handles deck, draw pile, discard pile, and hand management.

This module manages the card deck system, which is central to deck-building games.
Cards flow through different zones: draw pile -> hand -> discard pile.
Some cards can be "exhausted" (removed from combat entirely).
"""

import random
from typing import List, Optional
from card import Card


class Deck:
    """
    Manages a deck of cards including draw pile, discard pile, and hand.
    
    The deck system works like this:
    1. Draw pile: Cards waiting to be drawn (shuffled)
    2. Hand: Cards currently available to play
    3. Discard pile: Cards that have been played or discarded
    4. Exhaust pile: Cards permanently removed from combat
    
    When the draw pile is empty, the discard pile is shuffled and becomes
    the new draw pile (unless it's also empty).
    """
    
    def __init__(self, cards: List[Card] = None):
        """
        Initialize deck with cards.
        
        Creates a new deck with the provided cards. Cards start in the draw pile
        and are immediately shuffled. The discard pile, hand, and exhaust pile
        start empty.
        
        Args:
            cards: List of Card objects to initialize the deck with.
                  If None, creates an empty deck.
        """
        # Start with all cards in the draw pile
        self.draw_pile: List[Card] = cards.copy() if cards else []
        self.discard_pile: List[Card] = []  # Cards that have been played/discarded
        self.hand: List[Card] = []  # Cards currently available to play
        self.exhaust_pile: List[Card] = []  # Cards permanently removed from combat
        
        # Shuffle the draw pile so cards are in random order
        self.shuffle()
    
    def shuffle(self):
        """
        Shuffle the draw pile using Python's random.shuffle().
        
        This randomizes the order of cards in the draw pile, ensuring
        that card draws are unpredictable. Called automatically when
        the deck is created and when the discard pile is reshuffled.
        """
        random.shuffle(self.draw_pile)
    
    def draw(self, count: int = 1) -> List[Card]:
        """
        Draw cards from the draw pile into the hand.
        
        This is the primary way to get cards into your hand. If the draw
        pile is empty, it automatically reshuffles the discard pile and
        continues drawing. If both piles are empty, stops drawing.
        
        Args:
            count: Number of cards to draw (default: 1)
            
        Returns:
            List of Card objects that were drawn (may be less than count
            if deck runs out of cards)
        """
        drawn = []
        # Try to draw the requested number of cards
        for _ in range(count):
            # Check if draw pile is empty
            if not self.draw_pile:
                # Reshuffle discard pile into draw pile if available
                if self.discard_pile:
                    self.draw_pile = self.discard_pile.copy()
                    self.discard_pile.clear()
                    self.shuffle()
                else:
                    # Both piles empty, can't draw more
                    break
            
            # Draw one card from the top of the draw pile
            if self.draw_pile:
                card = self.draw_pile.pop(0)  # Remove from draw pile
                self.hand.append(card)  # Add to hand
                drawn.append(card)  # Track what was drawn
        
        return drawn
    
    def discard_hand(self):
        """
        Discard all cards currently in hand.
        
        This is typically called at the end of a turn. All cards in hand
        are moved to the discard pile, clearing the hand for the next turn.
        """
        # Move all hand cards to discard pile
        self.discard_pile.extend(self.hand)
        # Clear the hand
        self.hand.clear()
    
    def discard_card(self, card: Card):
        """
        Discard a specific card from hand.
        
        Used when a card is played - it moves from hand to discard pile.
        The card can be reshuffled later when the draw pile runs out.
        
        Args:
            card: The Card object to discard
        """
        if card in self.hand:
            self.hand.remove(card)  # Remove from hand
            self.discard_pile.append(card)  # Add to discard pile
    
    def exhaust_card(self, card: Card):
        """
        Exhaust (permanently remove) a card from hand.
        
        Exhausted cards are removed from combat entirely and cannot be
        reshuffled. This is used for cards with "Exhaust" keyword or
        special effects that remove cards permanently.
        
        Args:
            card: The Card object to exhaust
        """
        if card in self.hand:
            self.hand.remove(card)  # Remove from hand
            self.exhaust_pile.append(card)  # Add to exhaust pile (permanent)
    
    def add_card(self, card: Card, to_draw_pile: bool = True):
        """
        Add a card to the deck.
        
        Used when acquiring new cards (from rewards, shops, etc.).
        Can add to draw pile (immediate availability) or discard pile
        (will be available after reshuffle).
        
        Args:
            card: The Card object to add
            to_draw_pile: If True, add to draw pile; if False, add to discard pile
        """
        if to_draw_pile:
            self.draw_pile.append(card)  # Add to draw pile (can draw immediately)
        else:
            self.discard_pile.append(card)  # Add to discard (available after reshuffle)
    
    def remove_card(self, card: Card):
        """
        Remove a card from the deck entirely.
        
        Removes the card from all piles (draw, discard, hand) but NOT
        from exhaust pile (exhausted cards stay exhausted). Used when
        removing cards from your deck permanently.
        
        Args:
            card: The Card object to remove
        """
        # Remove from all active piles
        if card in self.draw_pile:
            self.draw_pile.remove(card)
        if card in self.discard_pile:
            self.discard_pile.remove(card)
        if card in self.hand:
            self.hand.remove(card)
        # Note: exhaust_pile is intentionally not cleared (exhausted cards stay exhausted)
    
    def get_hand_size(self) -> int:
        """
        Get the number of cards currently in hand.
        
        Returns:
            Number of cards in the hand
        """
        return len(self.hand)
    
    def get_draw_pile_size(self) -> int:
        """
        Get the number of cards in the draw pile.
        
        Returns:
            Number of cards remaining to be drawn
        """
        return len(self.draw_pile)
    
    def get_discard_pile_size(self) -> int:
        """
        Get the number of cards in the discard pile.
        
        Returns:
            Number of cards in the discard pile (will be reshuffled when draw pile empties)
        """
        return len(self.discard_pile)
    
    def get_total_cards(self) -> int:
        """
        Get total number of cards in deck (excluding exhaust pile).
        
        This counts all cards that can still be drawn/played. Exhausted
        cards are not counted as they're permanently removed.
        
        Returns:
            Total cards in draw_pile + discard_pile + hand
        """
        return len(self.draw_pile) + len(self.discard_pile) + len(self.hand)
    
    def reset_for_combat(self):
        """
        Reset deck for a new combat encounter.
        
        This combines all cards from hand and discard pile back into the
        draw pile, then shuffles. Used at the start of each combat to
        ensure a fresh deck. Exhausted cards remain exhausted (not reset).
        """
        # Combine all cards back into draw pile
        self.draw_pile.extend(self.discard_pile)  # Add discarded cards
        self.draw_pile.extend(self.hand)  # Add hand cards
        self.discard_pile.clear()  # Clear discard pile
        self.hand.clear()  # Clear hand
        # Note: exhaust_pile stays separate - exhausted cards remain exhausted
        
        # Shuffle the combined deck
        self.shuffle()
    
    def get_hand(self) -> List[Card]:
        """
        Get a copy of the current hand.
        
        Returns a copy (not the original list) so modifications don't
        affect the deck's internal state.
        
        Returns:
            List of Card objects currently in hand (copy)
        """
        return self.hand.copy()
    
    def to_dict(self) -> dict:
        """
        Convert deck to dictionary for serialization.
        
        Used for saving game state or sending deck data to frontends.
        Each card is converted to dict using its to_dict() method.
        
        Returns:
            Dictionary containing all deck state (all piles as lists of card dicts)
        """
        return {
            'draw_pile': [card.to_dict() for card in self.draw_pile],
            'discard_pile': [card.to_dict() for card in self.discard_pile],
            'hand': [card.to_dict() for card in self.hand],
            'exhaust_pile': [card.to_dict() for card in self.exhaust_pile]
        }

