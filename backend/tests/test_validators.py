"""Tests for Pydantic validators in schemas."""

import pytest
from pydantic import ValidationError

from app.models.schemas import (
    CardBase,
    CardCreate,
    DeckBase,
    DeckCreate,
    CardRole,
)


class TestCardBaseValidators:
    """Test validators for CardBase model."""

    def test_valid_card(self):
        """Test creating a valid card."""
        card = CardBase(
            id="test-1",
            name="Lightning Bolt",
            mana_cost="{R}",
            cmc=1.0,
            color_identity=["R"],
            quantity=4,
            type_line="Instant",
            rarity="common",
            set_code="LEA",
        )
        assert card.name == "Lightning Bolt"
        assert card.quantity == 4

    def test_invalid_quantity_zero(self):
        """Test that quantity cannot be zero."""
        with pytest.raises(ValidationError) as exc_info:
            CardBase(
                id="test-1",
                name="Lightning Bolt",
                mana_cost="{R}",
                cmc=1.0,
                color_identity=["R"],
                quantity=0,
                type_line="Instant",
                rarity="common",
                set_code="LEA",
            )
        assert "Card quantity must be positive" in str(exc_info.value)

    def test_invalid_quantity_negative(self):
        """Test that quantity cannot be negative."""
        with pytest.raises(ValidationError) as exc_info:
            CardBase(
                id="test-1",
                name="Lightning Bolt",
                mana_cost="{R}",
                cmc=1.0,
                color_identity=["R"],
                quantity=-1,
                type_line="Instant",
                rarity="common",
                set_code="LEA",
            )
        assert "Card quantity must be positive" in str(exc_info.value)

    def test_invalid_color_identity(self):
        """Test that color identity must contain valid colors."""
        with pytest.raises(ValidationError) as exc_info:
            CardBase(
                id="test-1",
                name="Lightning Bolt",
                mana_cost="{R}",
                cmc=1.0,
                color_identity=["X"],
                quantity=4,
                type_line="Instant",
                rarity="common",
                set_code="LEA",
            )
        assert "Invalid color in color_identity" in str(exc_info.value)


class TestCardCreateValidators:
    """Test validators for CardCreate model."""

    def test_valid_card_create(self):
        """Test creating a valid card with CardCreate."""
        card = CardCreate(
            id="test-1",
            name="Lightning Bolt",
            type_line="Instant",
            rarity="common",
            set_code="LEA",
            color_identity=["R"],
            cmc=1.0,
        )
        assert card.name == "Lightning Bolt"

    def test_empty_name(self):
        """Test that card name cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            CardCreate(
                id="test-1",
                name="",
                type_line="Instant",
                rarity="common",
                set_code="LEA",
            )
        assert "Card name cannot be empty" in str(exc_info.value)

    def test_invalid_cmc_negative(self):
        """Test that CMC cannot be negative."""
        with pytest.raises(ValidationError) as exc_info:
            CardCreate(
                id="test-1",
                name="Test Card",
                type_line="Instant",
                rarity="common",
                set_code="LEA",
                cmc=-1.0,
            )
        assert "Converted mana cost (CMC) cannot be negative" in str(exc_info.value)


class TestDeckBaseValidators:
    """Test validators for DeckBase model."""

    def create_test_card(self, name, quantity, type_line="Creature", colors=None):
        """Helper to create a test card."""
        if colors is None:
            colors = ["R"]
        return CardBase(
            id=f"card-{name}",
            name=name,
            mana_cost="{R}",
            cmc=1.0,
            color_identity=colors,
            quantity=quantity,
            type_line=type_line,
            rarity="common",
            set_code="LEA",
        )

    def test_valid_deck(self):
        """Test creating a valid 60-card deck."""
        cards = [self.create_test_card(f"Card {i}", 4) for i in range(14)]
        lands = [self.create_test_card("Mountain", 20, "Basic Land — Mountain")]

        deck = DeckBase(
            name="Test Deck",
            format="Standard",
            colors=["R"],
            main_deck=cards,
            lands=lands,
        )
        assert deck.total_cards == 76

    def test_deck_too_small(self):
        """Test that deck must have at least 60 cards."""
        cards = [self.create_test_card("Card 1", 20)]

        with pytest.raises(ValidationError) as exc_info:
            DeckBase(
                name="Test Deck",
                format="Standard",
                colors=["R"],
                main_deck=cards,
            )
        assert "at least 60 cards" in str(exc_info.value)

    def test_too_many_non_basic_cards(self):
        """Test that non-basic cards cannot exceed 4 copies."""
        cards = [self.create_test_card("Lightning Bolt", 5)]

        with pytest.raises(ValidationError) as exc_info:
            # Need 60 cards total
            more_cards = [self.create_test_card(f"Card {i}", 4) for i in range(13)]
            lands = [self.create_test_card("Mountain", 11, "Basic Land — Mountain")]

            DeckBase(
                name="Test Deck",
                format="Standard",
                colors=["R"],
                main_deck=cards + more_cards,
                lands=lands,
            )
        assert "Too many copies of 'Lightning Bolt'" in str(exc_info.value)
        assert "Maximum 4 copies allowed" in str(exc_info.value)

    def test_basic_lands_unlimited(self):
        """Test that basic lands can have more than 4 copies."""
        cards = [self.create_test_card(f"Card {i}", 4) for i in range(10)]
        lands = [self.create_test_card("Mountain", 20, "Basic Land — Mountain")]

        deck = DeckBase(
            name="Test Deck",
            format="Standard",
            colors=["R"],
            main_deck=cards,
            lands=lands,
        )
        assert deck.total_cards == 60

    def test_sideboard_too_large(self):
        """Test that sideboard cannot exceed 15 cards."""
        cards = [self.create_test_card(f"Card {i}", 4) for i in range(14)]
        lands = [self.create_test_card("Mountain", 20, "Basic Land — Mountain")]
        sideboard = [self.create_test_card(f"SB Card {i}", 4) for i in range(4)]

        with pytest.raises(ValidationError) as exc_info:
            DeckBase(
                name="Test Deck",
                format="Standard",
                colors=["R"],
                main_deck=cards,
                lands=lands,
                sideboard=sideboard,
            )
        assert "at most 15 cards" in str(exc_info.value)

    def test_color_identity_mismatch(self):
        """Test that cards must match deck colors."""
        red_cards = [self.create_test_card(f"Card {i}", 4, colors=["R"]) for i in range(10)]
        blue_card = [self.create_test_card("Blue Card", 4, colors=["U"])]
        lands = [self.create_test_card("Mountain", 20, "Basic Land — Mountain", colors=["R"])]

        with pytest.raises(ValidationError) as exc_info:
            DeckBase(
                name="Test Deck",
                format="Standard",
                colors=["R"],  # Deck is red only
                main_deck=red_cards + blue_card,
                lands=lands,
            )
        assert "not in deck colors" in str(exc_info.value)

    def test_invalid_color_code(self):
        """Test that color codes must be valid."""
        cards = [self.create_test_card(f"Card {i}", 4) for i in range(14)]
        lands = [self.create_test_card("Mountain", 20, "Basic Land — Mountain")]

        with pytest.raises(ValidationError) as exc_info:
            DeckBase(
                name="Test Deck",
                format="Standard",
                colors=["X"],  # Invalid color
                main_deck=cards,
                lands=lands,
            )
        assert "Invalid color code" in str(exc_info.value)


class TestDeckCreateValidators:
    """Test validators for DeckCreate model."""

    def test_valid_deck_create(self):
        """Test creating a valid deck."""
        deck = DeckCreate(
            name="Test Deck",
            format="Standard",
            colors=["R"],
            mainboard={"card-1": 4, "card-2": 4, "card-3": 52},
            sideboard={"card-4": 15},
        )
        assert deck.name == "Test Deck"

    def test_empty_deck_name(self):
        """Test that deck name cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            DeckCreate(
                name="",
                format="Standard",
                colors=["R"],
                mainboard={"card-1": 60},
            )
        assert "Deck name cannot be empty" in str(exc_info.value)

    def test_mainboard_too_small(self):
        """Test that mainboard must have at least 60 cards."""
        with pytest.raises(ValidationError) as exc_info:
            DeckCreate(
                name="Test Deck",
                format="Standard",
                colors=["R"],
                mainboard={"card-1": 30},
            )
        assert "at least 60 cards" in str(exc_info.value)

    def test_sideboard_too_large(self):
        """Test that sideboard cannot exceed 15 cards."""
        with pytest.raises(ValidationError) as exc_info:
            DeckCreate(
                name="Test Deck",
                format="Standard",
                colors=["R"],
                mainboard={"card-1": 60},
                sideboard={"card-2": 20},
            )
        assert "at most 15 cards" in str(exc_info.value)

    def test_invalid_mainboard_quantity(self):
        """Test that mainboard quantities must be positive."""
        with pytest.raises(ValidationError) as exc_info:
            DeckCreate(
                name="Test Deck",
                format="Standard",
                colors=["R"],
                mainboard={"card-1": 0},
            )
        assert "Card quantity must be positive" in str(exc_info.value)

    def test_invalid_sideboard_quantity(self):
        """Test that sideboard quantities must be positive."""
        with pytest.raises(ValidationError) as exc_info:
            DeckCreate(
                name="Test Deck",
                format="Standard",
                colors=["R"],
                mainboard={"card-1": 60},
                sideboard={"card-2": -1},
            )
        assert "Card quantity must be positive" in str(exc_info.value)

    def test_invalid_color_code(self):
        """Test that color codes must be valid."""
        with pytest.raises(ValidationError) as exc_info:
            DeckCreate(
                name="Test Deck",
                format="Standard",
                colors=["X"],
                mainboard={"card-1": 60},
            )
        assert "Invalid color code" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
