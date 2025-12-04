"""
Card system for the card battler game.
Data-driven card objects with effects and metadata.
"""

from enum import Enum
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field


class CardType(Enum):
    """Types of cards in the game."""
    ATTACK = "attack"
    SKILL = "skill"
    POWER = "power"


class CardRarity(Enum):
    """Card rarity levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"


@dataclass
class Card:
    """Represents a single card in the game."""
    name: str
    card_type: CardType
    cost: int
    description: str
    rarity: CardRarity = CardRarity.COMMON
    
    # Card effects (stored as data)
    damage: int = 0
    block: int = 0
    energy_gain: int = 0
    card_draw: int = 0
    
    # Status effects to apply
    status_effects: Dict[str, int] = field(default_factory=dict)  # {status_name: amount}
    
    # Upgrade values (for upgraded cards)
    upgraded: bool = False
    upgrade_damage: int = 0
    upgrade_block: int = 0
    upgrade_cost_reduction: int = 0
    
    def get_cost(self) -> int:
        """Get the current cost of the card (accounting for upgrades)."""
        return max(0, self.cost - (self.upgrade_cost_reduction if self.upgraded else 0))
    
    def get_damage(self) -> int:
        """Get the current damage of the card (accounting for upgrades)."""
        return self.damage + (self.upgrade_damage if self.upgraded else 0)
    
    def get_block(self) -> int:
        """Get the current block of the card (accounting for upgrades)."""
        return self.block + (self.upgrade_block if self.upgraded else 0)
    
    def upgrade(self):
        """Upgrade this card."""
        self.upgraded = True
    
    def to_dict(self) -> Dict:
        """Convert card to dictionary for serialization."""
        return {
            'name': self.name,
            'card_type': self.card_type.value,
            'cost': self.get_cost(),
            'description': self.description,
            'rarity': self.rarity.value,
            'damage': self.get_damage(),
            'block': self.get_block(),
            'energy_gain': self.energy_gain,
            'card_draw': self.card_draw,
            'status_effects': self.status_effects,
            'upgraded': self.upgraded
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Card':
        """Create card from dictionary."""
        card = cls(
            name=data['name'],
            card_type=CardType(data['card_type']),
            cost=data.get('cost', 0),
            description=data.get('description', ''),
            rarity=CardRarity(data.get('rarity', 'common')),
            damage=data.get('damage', 0),
            block=data.get('block', 0),
            energy_gain=data.get('energy_gain', 0),
            card_draw=data.get('card_draw', 0),
            status_effects=data.get('status_effects', {}),
            upgraded=data.get('upgraded', False)
        )
        return card


class CardLibrary:
    """Library of all available cards in the game."""
    
    @staticmethod
    def get_all_cards() -> List[Card]:
        """Get all cards in the library."""
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
        """Get a card by its name."""
        for card in CardLibrary.get_all_cards():
            if card.name.lower() == name.lower():
                # Return a copy so modifications don't affect the library
                import copy
                return copy.deepcopy(card)
        return None
    
    @staticmethod
    def get_cards_by_type(card_type: CardType) -> List[Card]:
        """Get all cards of a specific type."""
        return [card for card in CardLibrary.get_all_cards() if card.card_type == card_type]
    
    @staticmethod
    def get_starter_deck() -> List[Card]:
        """Get a starter deck for new players."""
        import copy
        starter = []
        # 5 Strikes
        for _ in range(5):
            starter.append(CardLibrary.get_card_by_name("Strike"))
        # 4 Defends
        for _ in range(4):
            starter.append(CardLibrary.get_card_by_name("Defend"))
        return starter

