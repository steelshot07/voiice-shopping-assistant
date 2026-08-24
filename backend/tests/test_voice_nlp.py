"""
Tests for the rule-based NLP voice command parser.

These tests exercise the parser only — no database, no HTTP.
"""

from decimal import Decimal

import pytest

from app.services.voice import ParsedVoiceCommand, parse_voice_command


# ──────────────────────────────────────────────
# ADD_ITEM intent
# ──────────────────────────────────────────────

class TestAddItem:
    @pytest.mark.parametrize("command,expected_product,expected_qty", [
        ("add apples", "apples", Decimal("1")),
        ("add 2 apples", "apples", Decimal("2")),
        ("add two apples", "apples", Decimal("2")),
        ("I want to add 2 apples", "apples", Decimal("2")),
        ("include 2 apples", "apples", Decimal("2")),
        ("I need 2 apples", "apples", Decimal("2")),
        ("get me 2 apples", "apples", Decimal("2")),
        ("buy 2 apples", "apples", Decimal("2")),
        ("grab 2 apples", "apples", Decimal("2")),
        ("pick up 2 apples", "apples", Decimal("2")),
        ("put 2 apples on my list", "apples", Decimal("2")),
        ("I need milk", "milk", Decimal("1")),
    ])
    def test_add_variations(self, command, expected_product, expected_qty):
        result = parse_voice_command(command)
        assert result.intent == "ADD_ITEM", f"Expected ADD_ITEM for '{command}', got {result.intent}"
        assert len(result.items) >= 1
        assert result.items[0].product_name.lower() == expected_product
        assert result.items[0].quantity == expected_qty
        assert result.confidence >= 0.5

    def test_add_with_unit(self):
        result = parse_voice_command("add 2 kg rice")
        assert result.intent == "ADD_ITEM"
        assert result.items[0].unit == "kg"
        assert result.items[0].quantity == Decimal("2")

    def test_add_ml_unit(self):
        result = parse_voice_command("add 500 ml milk")
        assert result.intent == "ADD_ITEM"
        assert result.items[0].unit == "ml"
        assert result.items[0].quantity == Decimal("500")

    def test_add_decimal_quantity(self):
        result = parse_voice_command("add 2.5 kg rice")
        assert result.intent == "ADD_ITEM"
        assert result.items[0].quantity == Decimal("2.5")
        assert result.items[0].unit == "kg"


# ──────────────────────────────────────────────
# REMOVE_ITEM intent
# ──────────────────────────────────────────────

class TestRemoveItem:
    @pytest.mark.parametrize("command,expected_product", [
        ("remove apples", "apples"),
        ("delete apples", "apples"),
        ("take apples off my list", "apples"),
        ("I don't need apples anymore", "apples"),
        ("forget apples", "apples"),
        ("drop apples", "apples"),
    ])
    def test_remove_variations(self, command, expected_product):
        result = parse_voice_command(command)
        assert result.intent == "REMOVE_ITEM", f"Expected REMOVE_ITEM for '{command}', got {result.intent}"
        assert len(result.items) >= 1
        assert result.items[0].product_name.lower() == expected_product
        assert result.confidence >= 0.5


# ──────────────────────────────────────────────
# UPDATE_QUANTITY intent
# ──────────────────────────────────────────────

class TestUpdateQuantity:
    @pytest.mark.parametrize("command,expected_product,expected_qty", [
        ("change apples to 3", "apples", Decimal("3")),
        ("set apples to 3", "apples", Decimal("3")),
        ("update apples to 5", "apples", Decimal("5")),
    ])
    def test_update_variations(self, command, expected_product, expected_qty):
        result = parse_voice_command(command)
        assert result.intent == "UPDATE_QUANTITY", f"Expected UPDATE_QUANTITY for '{command}', got {result.intent}"
        assert len(result.items) >= 1
        assert result.items[0].product_name.lower() == expected_product
        assert result.items[0].quantity == expected_qty

    def test_contextual_update(self):
        """'make that 3' should be UPDATE_QUANTITY with empty product (resolved from context)."""
        result = parse_voice_command("make that 3")
        assert result.intent == "UPDATE_QUANTITY"
        assert len(result.items) >= 1
        assert result.items[0].quantity == Decimal("3")

    def test_make_product_quantity(self):
        result = parse_voice_command("make apples 3")
        assert result.intent == "UPDATE_QUANTITY"
        assert result.items[0].product_name.lower() == "apples"
        assert result.items[0].quantity == Decimal("3")


# ──────────────────────────────────────────────
# CLEAR_LIST intent
# ──────────────────────────────────────────────

class TestClearList:
    @pytest.mark.parametrize("command", [
        "clear my list",
        "clear the list",
        "empty my list",
        "delete everything",
        "remove everything",
        "delete all",
        "remove all",
    ])
    def test_clear_variations(self, command):
        result = parse_voice_command(command)
        assert result.intent == "CLEAR_LIST", f"Expected CLEAR_LIST for '{command}', got {result.intent}"
        assert result.confidence >= 0.5


# ──────────────────────────────────────────────
# SHOW_LIST intent
# ──────────────────────────────────────────────

class TestShowList:
    @pytest.mark.parametrize("command", [
        "show my list",
        "show the list",
        "what's on my list",
        "what is on my shopping list",
        "list my items",
        "display my list",
    ])
    def test_show_variations(self, command):
        result = parse_voice_command(command)
        assert result.intent == "SHOW_LIST", f"Expected SHOW_LIST for '{command}', got {result.intent}"
        assert result.confidence >= 0.5


# ──────────────────────────────────────────────
# COMPLETE_ITEM intent
# ──────────────────────────────────────────────

class TestCompleteItem:
    @pytest.mark.parametrize("command,expected_product", [
        ("complete apples", "apples"),
        ("finish apples", "apples"),
        ("mark apples complete", "apples"),
        ("check off apples", "apples"),
        ("I am done with apples", "apples"),
        ("mark apples as done", "apples"),
    ])
    def test_complete_variations(self, command, expected_product):
        result = parse_voice_command(command)
        assert result.intent == "COMPLETE_ITEM", f"Expected COMPLETE_ITEM for '{command}', got {result.intent}"
        assert len(result.items) >= 1
        assert result.items[0].product_name.lower() == expected_product


# ──────────────────────────────────────────────
# HELP intent
# ──────────────────────────────────────────────

class TestHelp:
    @pytest.mark.parametrize("command", [
        "help",
        "what can you do",
        "what commands can I use",
        "how do I use this",
    ])
    def test_help_variations(self, command):
        result = parse_voice_command(command)
        assert result.intent == "HELP", f"Expected HELP for '{command}', got {result.intent}"
        assert result.confidence >= 0.5


# ──────────────────────────────────────────────
# Quantity expressions
# ──────────────────────────────────────────────

class TestQuantities:
    def test_couple(self):
        result = parse_voice_command("add a couple apples")
        assert result.intent == "ADD_ITEM"
        assert result.items[0].quantity == Decimal("2")

    def test_half_dozen(self):
        result = parse_voice_command("add half a dozen eggs")
        assert result.intent == "ADD_ITEM"
        assert result.items[0].quantity == Decimal("6")

    def test_dozen(self):
        result = parse_voice_command("add a dozen eggs")
        assert result.intent == "ADD_ITEM"
        assert result.items[0].quantity == Decimal("12")

    def test_decimal_kg(self):
        result = parse_voice_command("add 2.5 kg rice")
        assert result.intent == "ADD_ITEM"
        assert result.items[0].quantity == Decimal("2.5")
        assert result.items[0].unit == "kg"

    def test_500_ml(self):
        result = parse_voice_command("add 500 ml milk")
        assert result.intent == "ADD_ITEM"
        assert result.items[0].quantity == Decimal("500")
        assert result.items[0].unit == "ml"


# ──────────────────────────────────────────────
# Multi-item commands
# ──────────────────────────────────────────────

class TestMultiItem:
    def test_two_items_and(self):
        result = parse_voice_command("add apples and bananas")
        assert result.intent == "ADD_ITEM"
        assert len(result.items) == 2
        names = {i.product_name.lower() for i in result.items}
        assert "apples" in names
        assert "bananas" in names

    def test_three_items_comma_and(self):
        result = parse_voice_command("add 2 apples, 3 bananas and 1 litre milk")
        assert result.intent == "ADD_ITEM"
        assert len(result.items) == 3

    def test_items_need_conjunction(self):
        result = parse_voice_command("I need milk and eggs")
        assert result.intent == "ADD_ITEM"
        assert len(result.items) == 2


# ──────────────────────────────────────────────
# UNKNOWN / edge cases
# ──────────────────────────────────────────────

class TestUnknown:
    @pytest.mark.parametrize("command", [
        "what is the meaning of life",
        "tell me a joke",
        "sort out those things I need",
        "blah blah blah",
    ])
    def test_unknown(self, command):
        result = parse_voice_command(command)
        assert result.intent == "UNKNOWN" or result.confidence < 0.5, \
            f"'{command}' should be UNKNOWN or low confidence, got {result.intent} ({result.confidence})"

    def test_empty_command(self):
        result = parse_voice_command("")
        assert result.intent == "UNKNOWN"
        assert result.confidence == 0.0

    def test_negation_blocks_add(self):
        """'I don't want to add milk' should NOT be ADD_ITEM."""
        result = parse_voice_command("I don't want to add milk")
        assert result.intent != "ADD_ITEM"


# ──────────────────────────────────────────────
# Product name preservation
# ──────────────────────────────────────────────

class TestProductNamePreservation:
    def test_multi_word_product(self):
        result = parse_voice_command("add amul milk")
        assert result.intent == "ADD_ITEM"
        assert "amul" in result.items[0].product_name.lower()
        assert "milk" in result.items[0].product_name.lower()

    def test_product_with_brand(self):
        result = parse_voice_command("add colgate toothpaste")
        assert result.intent == "ADD_ITEM"
        product = result.items[0].product_name.lower()
        assert "colgate" in product
        assert "toothpaste" in product

    def test_unit_not_in_product_name(self):
        """Unit tokens like 'kg' should not leak into the product name."""
        result = parse_voice_command("add 2 kg rice")
        assert result.intent == "ADD_ITEM"
        assert "kg" not in result.items[0].product_name.lower()
        assert "rice" in result.items[0].product_name.lower()
