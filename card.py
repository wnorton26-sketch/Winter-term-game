"""
Card system for the card battler game.
Data-driven card objects with effects and metadata.

This module defines the core card system including:
- Card types (Attack, Skill, Power)
- Card rarities (Common, Uncommon, Rare)
- Card data structure with all effects
- Card library containing all available cards
- Card upgrade system
"""

from enum import Enum
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field


class CardType(Enum):
    """
    Enumeration of card types in the game.
    
    Card types determine the category of a card:
    - ATTACK: Cards that deal damage to enemies
    - SKILL: Cards that provide utility (block, card draw, etc.)
    - POWER: Cards that provide persistent effects throughout combat
    """
    ATTACK = "attack"  # Offensive cards that deal damage
    SKILL = "skill"    # Utility cards (defense, card draw, etc.)
    POWER = "power"    # Persistent effect cards that stay active


class CardRarity(Enum):
    """
    Enumeration of card rarity levels.
    
    Rarity affects how often cards appear in card rewards and shops:
    - COMMON: Most frequently found cards, basic effects
    - UNCOMMON: Moderately rare, stronger effects
    - RARE: Very rare, powerful effects
    """
    COMMON = "common"      # Most common cards, basic effects
    UNCOMMON = "uncommon"  # Moderately rare, stronger effects
    RARE = "rare"          # Very rare, powerful effects


@dataclass
class Card:
    """
    Represents a single card in the game.
    
    Cards are data-driven objects that contain all information needed to play them.
    This includes costs, effects, and upgrade values. Cards are immutable in the
    library but can be copied and modified when added to decks.
    
    Attributes:
        name: The display name of the card (e.g., "Strike", "Defend")
        card_type: The type of card (ATTACK, SKILL, or POWER)
        cost: Base energy cost to play the card
        description: Text description shown to the player
        rarity: How rare the card is (affects availability)
        damage: Base damage dealt by the card (0 if not an attack)
        block: Base block gained from the card (0 if not defensive)
        energy_gain: Additional energy gained when playing (rare effect)
        card_draw: Number of cards drawn when playing (utility effect)
        status_effects: Dictionary mapping status names to amounts applied
        upgraded: Whether this card has been upgraded
        upgrade_damage: Additional damage when upgraded
        upgrade_block: Additional block when upgraded
        upgrade_cost_reduction: Energy cost reduction when upgraded
    """
    name: str  # Display name of the card
    card_type: CardType  # Type: ATTACK, SKILL, or POWER
    cost: int  # Energy cost to play this card
    description: str  # Flavor text and effect description
    rarity: CardRarity = CardRarity.COMMON  # How rare the card is
    
    # Card effects (stored as data)
    # These values represent what the card does when played
    damage: int = 0  # Damage dealt to enemies (for attack cards)
    block: int = 0  # Block gained (for defensive cards)
    energy_gain: int = 0  # Extra energy gained (rare utility effect)
    card_draw: int = 0  # Cards drawn when played (utility effect)
    
    # Status effects to apply when card is played
    # Format: {status_name: amount} - e.g., {"vulnerable": 2} applies 2 vulnerable
    status_effects: Dict[str, int] = field(default_factory=dict)
    
    # Upgrade values (for upgraded cards)
    # When a card is upgraded, these values modify the base stats
    upgraded: bool = False  # Whether this card instance has been upgraded
    upgrade_damage: int = 0  # Additional damage when upgraded
    upgrade_block: int = 0  # Additional block when upgraded
    upgrade_cost_reduction: int = 0  # Energy cost reduction when upgraded
    
    def get_cost(self) -> int:
        """
        Get the current energy cost of the card, accounting for upgrades.
        
        Returns:
            The effective cost after upgrades. Never returns negative (minimum 0).
        """
        # If upgraded, reduce cost by upgrade_cost_reduction
        # Use max(0, ...) to ensure cost never goes below 0
        return max(0, self.cost - (self.upgrade_cost_reduction if self.upgraded else 0))
    
    def get_damage(self) -> int:
        """
        Get the current damage value of the card, accounting for upgrades.
        
        Returns:
            Base damage plus any upgrade damage bonus if the card is upgraded.
        """
        # Add upgrade damage bonus if the card has been upgraded
        return self.damage + (self.upgrade_damage if self.upgraded else 0)
    
    def get_block(self) -> int:
        """
        Get the current block value of the card, accounting for upgrades.
        
        Returns:
            Base block plus any upgrade block bonus if the card is upgraded.
        """
        # Add upgrade block bonus if the card has been upgraded
        return self.block + (self.upgrade_block if self.upgraded else 0)
    
    def upgrade(self):
        """
        Mark this card as upgraded.
        
        This sets the upgraded flag to True, which enables upgrade bonuses
        when get_cost(), get_damage(), or get_block() are called.
        """
        self.upgraded = True
    
    def to_dict(self) -> Dict:
        """
        Convert card to dictionary for serialization.
        
        This is used for saving game state, sending data to frontends (GUI/web),
        and network communication. Uses get_cost(), get_damage(), get_block() to
        include upgrade bonuses in the serialized data.
        
        Returns:
            Dictionary containing all card data in a serializable format.
        """
        return {
            'name': self.name,
            'card_type': self.card_type.value,  # Convert enum to string
            'cost': self.get_cost(),  # Use get_cost() to include upgrades
            'description': self.description,
            'rarity': self.rarity.value,  # Convert enum to string
            'damage': self.get_damage(),  # Use get_damage() to include upgrades
            'block': self.get_block(),  # Use get_block() to include upgrades
            'energy_gain': self.energy_gain,
            'card_draw': self.card_draw,
            'status_effects': self.status_effects,
            'upgraded': self.upgraded
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Card':
        """
        Create a Card instance from a dictionary (deserialization).
        
        This is the reverse of to_dict(), used for loading saved games or
        receiving card data from external sources. Uses .get() with defaults
        to handle missing fields gracefully.
        
        Args:
            data: Dictionary containing card data (from to_dict() or similar)
            
        Returns:
            New Card instance with data from the dictionary
        """
        card = cls(
            name=data['name'],
            card_type=CardType(data['card_type']),  # Convert string back to enum
            cost=data.get('cost', 0),  # Default to 0 if missing
            description=data.get('description', ''),
            rarity=CardRarity(data.get('rarity', 'common')),  # Default to common
            damage=data.get('damage', 0),
            block=data.get('block', 0),
            energy_gain=data.get('energy_gain', 0),
            card_draw=data.get('card_draw', 0),
            status_effects=data.get('status_effects', {}),
            upgraded=data.get('upgraded', False)
        )
        return card


class CardLibrary:
    """
    Library of all available cards in the game.
    
    This class serves as a central repository for all card definitions.
    Cards are defined here as static data, and methods provide access
    to cards by name, type, or as a starter deck. This allows for
    easy expansion - just add new Card() instances to get_all_cards().
    """
    
    @staticmethod
    def get_all_cards() -> List[Card]:
        """
        Get all cards available in the game library.
        
        This method returns a list of all card definitions. Each card
        is a Card instance with its properties defined. To add new cards,
        simply add new Card() instances to this list.
        
        Returns:
            List of all Card objects in the game
        """
        return [
            # Attack Cards
            Card(
                name="Strike",
                card_type=CardType.ATTACK,
                cost=1,
                damage=6,
                description="Deal 6 damage.",
                rarity=CardRarity.COMMON,
                upgrade_damage=3
            ),
            Card(
                name="Bash",
                card_type=CardType.ATTACK,
                cost=2,
                damage=8,
                description="Deal 8 damage. Apply 2 Vulnerable.",
                rarity=CardRarity.COMMON,
                status_effects={"vulnerable": 2},
                upgrade_damage=2
            ),
            Card(
                name="Cleave",
                card_type=CardType.ATTACK,
                cost=1,
                damage=8,
                description="Deal 8 damage to ALL enemies.",
                rarity=CardRarity.COMMON,
                upgrade_damage=3
            ),
            Card(
                name="Heavy Blade",
                card_type=CardType.ATTACK,
                cost=2,
                damage=14,
                description="Deal 14 damage.",
                rarity=CardRarity.UNCOMMON,
                upgrade_damage=4
            ),
            Card(
                name="Whirlwind",
                card_type=CardType.ATTACK,
                cost=3,
                damage=5,
                description="Deal 5 damage to ALL enemies X times.",
                rarity=CardRarity.UNCOMMON,
                upgrade_damage=2
            ),
            
            # Skill Cards
            Card(
                name="Defend",
                card_type=CardType.SKILL,
                cost=1,
                block=5,
                description="Gain 5 Block.",
                rarity=CardRarity.COMMON,
                upgrade_block=3
            ),
            Card(
                name="Shrug It Off",
                card_type=CardType.SKILL,
                cost=1,
                block=8,
                card_draw=1,
                description="Gain 8 Block. Draw 1 card.",
                rarity=CardRarity.COMMON,
                upgrade_block=3
            ),
            Card(
                name="Armaments",
                card_type=CardType.SKILL,
                cost=1,
                block=5,
                description="Gain 5 Block. Upgrade a card in your hand.",
                rarity=CardRarity.UNCOMMON,
                upgrade_block=2
            ),
            Card(
                name="Flame Barrier",
                card_type=CardType.SKILL,
                cost=2,
                block=12,
                description="Gain 12 Block. When attacked, deal 4 damage back.",
                rarity=CardRarity.UNCOMMON,
                upgrade_block=4
            ),
            Card(
                name="Impervious",
                card_type=CardType.SKILL,
                cost=2,
                block=30,
                description="Gain 30 Block.",
                rarity=CardRarity.RARE,
                upgrade_block=10
            ),
            
            # Power Cards
            Card(
                name="Metallicize",
                card_type=CardType.POWER,
                cost=1,
                description="At the end of your turn, gain 3 Block.",
                rarity=CardRarity.UNCOMMON,
                status_effects={"metallicize": 3}
            ),
            Card(
                name="Barricade",
                card_type=CardType.POWER,
                cost=3,
                description="Block is not removed at the start of your turn.",
                rarity=CardRarity.RARE,
                status_effects={"barricade": 1}
            ),
            Card(
                name="Demon Form",
                card_type=CardType.POWER,
                cost=3,
                description="At the start of your turn, gain 2 Strength.",
                rarity=CardRarity.RARE,
                status_effects={"demon_form": 1}
            ),
        ]
    
    @staticmethod
    def get_card_by_name(name: str) -> Optional[Card]:
        """
        Get a card from the library by its name (case-insensitive).
        
        This method searches through all cards and returns a copy of the
        matching card. A copy is returned (not the original) so that
        modifications (like upgrades) don't affect the library template.
        
        Args:
            name: The name of the card to find (case-insensitive)
            
        Returns:
            A copy of the Card if found, None otherwise
        """
        # Search through all cards
        for card in CardLibrary.get_all_cards():
            # Case-insensitive comparison
            if card.name.lower() == name.lower():
                # Return a deep copy so modifications don't affect the library
                # This is important because cards can be upgraded/modified
                import copy
                return copy.deepcopy(card)
        return None  # Card not found
    
    @staticmethod
    def get_cards_by_type(card_type: CardType) -> List[Card]:
        """
        Get all cards of a specific type from the library.
        
        Useful for filtering cards by type (e.g., all attack cards,
        all skill cards, etc.). Used for card rewards, shops, etc.
        
        Args:
            card_type: The CardType enum value to filter by
            
        Returns:
            List of all cards matching the specified type
        """
        # List comprehension filters cards by type
        return [card for card in CardLibrary.get_all_cards() if card.card_type == card_type]
    
    @staticmethod
    def get_starter_deck() -> List[Card]:
        """
        Get a starter deck for new players.
        
        The starter deck is a balanced set of basic cards that new players
        begin with. Currently consists of 5 Strikes and 4 Defends, which
        provides a good mix of offense and defense.
        
        Returns:
            List of Card objects representing the starter deck
        """
        import copy
        starter = []
        # Add 5 Strike cards (basic attack cards)
        for _ in range(5):
            starter.append(CardLibrary.get_card_by_name("Strike"))
        # Add 4 Defend cards (basic defense cards)
        for _ in range(4):
            starter.append(CardLibrary.get_card_by_name("Defend"))
        return starter

