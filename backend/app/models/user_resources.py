"""SQLAlchemy models for user resources including wildcards and currency."""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, func

from app.core.database import Base


class UserResources(Base):
    """
    Model for tracking user's MTGA resources including wildcards and currency.

    Attributes:
        id (int): The unique identifier for the user resources record.
        user_id (int): The user identifier (foreign key to users.id).
        common_wildcards (int): Number of common wildcards owned.
        uncommon_wildcards (int): Number of uncommon wildcards owned.
        rare_wildcards (int): Number of rare wildcards owned.
        mythic_wildcards (int): Number of mythic rare wildcards owned.
        gold (int): Amount of gold currency.
        gems (int): Amount of gems (premium currency).
        updated_at (datetime): Last update timestamp.
        created_at (datetime): Creation timestamp.
    """
    __tablename__ = "user_resources"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey('users.id', ondelete='CASCADE'),
        unique=True, nullable=False, index=True
    )

    # Wildcards by rarity
    common_wildcards = Column(Integer, default=0, nullable=False)
    uncommon_wildcards = Column(Integer, default=0, nullable=False)
    rare_wildcards = Column(Integer, default=0, nullable=False)
    mythic_wildcards = Column(Integer, default=0, nullable=False)

    # Currency
    gold = Column(Integer, default=0, nullable=False)
    gems = Column(Integer, default=0, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    def update_wildcards(self, rarity: str, amount: int):
        """
        Update wildcard count for a specific rarity.

        Args:
            rarity (str): The rarity type ('common', 'uncommon', 'rare', 'mythic')
            amount (int): The new amount (not delta, absolute value)

        Raises:
            ValueError: If rarity is invalid or amount is negative
        """
        if amount < 0:
            raise ValueError("Wildcard amount cannot be negative")

        rarity_lower = rarity.lower()
        if rarity_lower == 'common':
            self.common_wildcards = amount
        elif rarity_lower == 'uncommon':
            self.uncommon_wildcards = amount
        elif rarity_lower == 'rare':
            self.rare_wildcards = amount
        elif rarity_lower == 'mythic':
            self.mythic_wildcards = amount
        else:
            raise ValueError(f"Invalid rarity type: {rarity}")

    def add_wildcards(self, rarity: str, count: int):
        """
        Add wildcards to the user's collection.

        Args:
            rarity (str): The rarity type ('common', 'uncommon', 'rare', 'mythic')
            count (int): Number of wildcards to add

        Raises:
            ValueError: If rarity is invalid
        """
        rarity_lower = rarity.lower()
        if rarity_lower == 'common':
            self.common_wildcards += count
        elif rarity_lower == 'uncommon':
            self.uncommon_wildcards += count
        elif rarity_lower == 'rare':
            self.rare_wildcards += count
        elif rarity_lower == 'mythic':
            self.mythic_wildcards += count
        else:
            raise ValueError(f"Invalid rarity type: {rarity}")

    def spend_wildcard(self, rarity: str) -> bool:
        """
        Spend a wildcard of the specified rarity.

        Args:
            rarity (str): The rarity type ('common', 'uncommon', 'rare', 'mythic')

        Returns:
            bool: True if wildcard was spent successfully, False if insufficient wildcards

        Raises:
            ValueError: If rarity is invalid
        """
        rarity_lower = rarity.lower()
        if rarity_lower == 'common':
            if self.common_wildcards > 0:
                self.common_wildcards -= 1
                return True
        elif rarity_lower == 'uncommon':
            if self.uncommon_wildcards > 0:
                self.uncommon_wildcards -= 1
                return True
        elif rarity_lower == 'rare':
            if self.rare_wildcards > 0:
                self.rare_wildcards -= 1
                return True
        elif rarity_lower == 'mythic':
            if self.mythic_wildcards > 0:
                self.mythic_wildcards -= 1
                return True
        else:
            raise ValueError(f"Invalid rarity type: {rarity}")
        return False

    def update_currency(self, gold: int = None, gems: int = None):
        """
        Update currency amounts.

        Args:
            gold (int, optional): New gold amount
            gems (int, optional): New gems amount

        Raises:
            ValueError: If amounts are negative
        """
        if gold is not None:
            if gold < 0:
                raise ValueError("Gold amount cannot be negative")
            self.gold = gold
        if gems is not None:
            if gems < 0:
                raise ValueError("Gems amount cannot be negative")
            self.gems = gems
