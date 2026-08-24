"""
Rule-based NLP-style voice command pipeline.

Pipeline stages:
  1. Text normalization
  2. Number normalization (word → digit)
  3. Unit normalization
  4. Intent classification
  5. Entity extraction (quantity, unit, product)
  6. Multi-item splitting
  7. Confidence scoring

The parser NEVER touches the database.  It only produces a structured
``ParsedVoiceCommand`` that the router can execute.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Optional


# ──────────────────────────────────────────────
# Data classes
# ──────────────────────────────────────────────

@dataclass
class ParsedItem:
    product_name: str
    quantity: Decimal = Decimal("1")
    unit: Optional[str] = None


@dataclass
class ParsedVoiceCommand:
    intent: str
    items: list[ParsedItem] = field(default_factory=list)
    confidence: float = 0.0
    raw_transcript: str = ""


# ──────────────────────────────────────────────
# 1. Text normalization
# ──────────────────────────────────────────────

_CONTRACTIONS: dict[str, str] = {
    "don't": "do not",
    "doesn't": "does not",
    "didn't": "did not",
    "can't": "cannot",
    "won't": "will not",
    "wouldn't": "would not",
    "shouldn't": "should not",
    "couldn't": "could not",
    "i'm": "i am",
    "i've": "i have",
    "i'll": "i will",
    "i'd": "i would",
    "it's": "it is",
    "that's": "that is",
    "what's": "what is",
    "let's": "let us",
    "there's": "there is",
    "they're": "they are",
    "we're": "we are",
    "you're": "you are",
}


def _normalize_text(raw: str) -> str:
    """Lowercase, expand contractions, collapse whitespace, strip punctuation."""
    text = raw.strip().lower()

    # Expand contractions (longest-first so "wouldn't" beats "won't" etc.)
    for contraction, expansion in sorted(
        _CONTRACTIONS.items(), key=lambda kv: -len(kv[0])
    ):
        text = text.replace(contraction, expansion)

    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)

    # Strip trailing punctuation that speech-to-text may add
    text = text.rstrip(".,!?;:")

    return text.strip()


# ──────────────────────────────────────────────
# 2. Number normalization
# ──────────────────────────────────────────────

_WORD_NUMBERS: dict[str, str] = {
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "eleven": "11",
    "twelve": "12",
    "thirteen": "13",
    "fourteen": "14",
    "fifteen": "15",
    "sixteen": "16",
    "seventeen": "17",
    "eighteen": "18",
    "nineteen": "19",
    "twenty": "20",
    "thirty": "30",
    "forty": "40",
    "fifty": "50",
    "sixty": "60",
    "seventy": "70",
    "eighty": "80",
    "ninety": "90",
    "hundred": "100",
}

# Compound phrases that should be replaced *before* single-word numbers.
_COMPOUND_NUMBERS: list[tuple[str, str]] = [
    ("half a dozen", "6"),
    ("a half dozen", "6"),
    ("a couple of", "2"),
    ("couple of", "2"),
    ("a couple", "2"),
    ("a pair of", "2"),
    ("a pair", "2"),
    ("a dozen", "12"),
]


def _normalize_numbers(text: str) -> str:
    """Replace written numbers with digits."""
    # Compound phrases first (order matters)
    for phrase, digit in _COMPOUND_NUMBERS:
        text = re.sub(rf"\b{re.escape(phrase)}\b", digit, text)

    # Replace "a" / "an" only when used as a quantity before a unit or product
    # e.g. "add a milk" -> "add 1 milk", but not "i am a person"
    text = re.sub(r"\b(an?)\s+(?=\w)", "1 ", text)

    # Single-word numbers (longest first to handle "eighteen" before "eight")
    for word, digit in sorted(_WORD_NUMBERS.items(), key=lambda kv: -len(kv[0])):
        text = re.sub(rf"\b{word}\b", digit, text)

    return text


# ──────────────────────────────────────────────
# 3. Unit normalization
# ──────────────────────────────────────────────

_UNIT_MAP: dict[str, str] = {
    "kg": "kg",
    "kgs": "kg",
    "kilo": "kg",
    "kilos": "kg",
    "kilogram": "kg",
    "kilograms": "kg",
    "g": "gram",
    "gram": "gram",
    "grams": "gram",
    "l": "litre",
    "litre": "litre",
    "litres": "litre",
    "liter": "litre",
    "liters": "litre",
    "ml": "ml",
    "millilitre": "ml",
    "millilitres": "ml",
    "milliliter": "ml",
    "milliliters": "ml",
    "pack": "pack",
    "packs": "pack",
    "packet": "pack",
    "packets": "pack",
    "bottle": "bottle",
    "bottles": "bottle",
    "box": "box",
    "boxes": "box",
    "dozen": "dozen",
    "dozens": "dozen",
    "piece": "piece",
    "pieces": "piece",
    "item": "piece",
    "items": "piece",
    "count": "piece",
    "bunch": "bunch",
    "bunches": "bunch",
    "roll": "roll",
    "rolls": "roll",
    "pulls": "pulls",
}

_UNIT_PATTERN = "|".join(
    sorted(_UNIT_MAP.keys(), key=len, reverse=True)
)


def _normalize_unit(raw: str) -> Optional[str]:
    """Return canonical unit name or None."""
    return _UNIT_MAP.get(raw.lower().strip())


# ──────────────────────────────────────────────
# 4. Intent classification
# ──────────────────────────────────────────────

# Patterns are tried in order; first match wins.
# Each entry: (compiled regex, intent name, confidence boost)

_NEGATION_PREFIX = r"(?:i\s+do\s+not\s+(?:need|want)\s+)"

_INTENT_PATTERNS: list[tuple[re.Pattern, str, float]] = [
    # ── HELP (check early, short phrases) ──
    (re.compile(r"^(?:help|what (?:can you do|commands? can i use)|how do i(?: use this)?)$"), "HELP", 0.95),

    # ── CLEAR LIST ──
    (re.compile(r"\b(?:clear|empty)\s+(?:my\s+|the\s+)?(?:shopping\s+)?list\b"), "CLEAR_LIST", 0.95),
    (re.compile(r"\b(?:remove|delete)\s+(?:everything|all(?:\s+items)?)\b"), "CLEAR_LIST", 0.90),

    # ── SHOW LIST ──
    (re.compile(r"\b(?:show|display|view)\s+(?:my\s+|the\s+)?(?:shopping\s+)?(?:list|items)\b"), "SHOW_LIST", 0.95),
    (re.compile(r"\bwhat\s+is\s+on\s+(?:my\s+)?(?:shopping\s+)?list\b"), "SHOW_LIST", 0.95),
    (re.compile(r"\blist\s+(?:my\s+)?(?:shopping\s+)?items\b"), "SHOW_LIST", 0.90),

    # ── COMPLETE ITEM ──
    (re.compile(r"\b(?:complete|finish|done\s+with|check\s+off)\s+(?:the\s+)?(.+?)(?:\s+(?:as\s+)?(?:completed|done))?$"), "COMPLETE_ITEM", 0.90),
    (re.compile(r"\bmark\s+(?:the\s+)?(.+?)(?:\s+(?:as\s+)?(?:completed|complete|done))$"), "COMPLETE_ITEM", 0.90),
    (re.compile(r"\bi\s+am\s+done\s+with\s+(?:the\s+)?(.+)$"), "COMPLETE_ITEM", 0.85),

    # ── REMOVE ITEM (negation-based) ──
    (re.compile(r"\bi\s+do\s+not\s+(?:need|want)\s+(?:the\s+)?(.+?)(?:\s+anymore|\s+any\s+more)?$"), "REMOVE_ITEM", 0.90),

    # ── REMOVE ITEM (verb-based) ──
    (re.compile(r"\b(?:remove|delete)\s+(?:the\s+)?(.+?)(?:\s+from\s+(?:my\s+)?(?:shopping\s+)?list)?$"), "REMOVE_ITEM", 0.90),
    (re.compile(r"\btake\s+(?:the\s+)?(.+?)\s+off(?:\s+(?:my\s+)?(?:shopping\s+)?list)?$"), "REMOVE_ITEM", 0.90),
    (re.compile(r"\bforget\s+(?:the\s+|about\s+(?:the\s+)?)?(.+)$"), "REMOVE_ITEM", 0.85),
    (re.compile(r"\bdrop\s+(?:the\s+)?(.+?)(?:\s+from\s+(?:my\s+)?(?:shopping\s+)?list)?$"), "REMOVE_ITEM", 0.85),

    # ── UPDATE QUANTITY ──
    (re.compile(r"\b(?:change|update|set)\s+(?:the\s+)?(.+?)\s+to\s+(\d+(?:\.\d+)?)\b"), "UPDATE_QUANTITY", 0.90),
    (re.compile(r"\bmake\s+(?:the\s+)?(.+?)\s+(\d+(?:\.\d+)?)\b"), "UPDATE_QUANTITY", 0.85),

    # ── UPDATE QUANTITY (contextual follow-up) ──
    (re.compile(r"\b(?:actually\s+)?make\s+(?:that|it)\s+(\d+(?:\.\d+)?)\b"), "UPDATE_QUANTITY_CONTEXT", 0.80),

    # ── ADD ITEM (explicit verbs) ──
    (re.compile(r"\b(?:add|include|put)\s+(.+?)(?:\s+(?:to|on|in)\s+(?:my\s+)?(?:shopping\s+)?list)?$"), "ADD_ITEM", 0.90),
    (re.compile(r"\b(?:get|buy|grab|pick\s*up)\s+(?:me\s+)?(?:some\s+)?(.+)$"), "ADD_ITEM", 0.85),

    # ── ADD ITEM (need/want — but NOT negated) ──
    (re.compile(r"\bi\s+(?:need|want)\s+(?:to\s+(?:add|buy|get)\s+)?(.+)$"), "ADD_ITEM", 0.80),
]


def _check_negation(text: str) -> bool:
    """Return True if the text contains negation suggesting the user does NOT want to add."""
    negation_patterns = [
        r"\bi\s+do\s+not\s+(?:want\s+to\s+)?add\b",
        r"\bdo\s+not\s+add\b",
        r"\bno\b.*\badd\b",
    ]
    for pat in negation_patterns:
        if re.search(pat, text):
            return True
    return False


def _classify_intent(text: str) -> tuple[str, float, re.Match | None]:
    """Return (intent, confidence, match) for the first matching pattern."""
    for pattern, intent, confidence in _INTENT_PATTERNS:
        m = pattern.search(text)
        if m:
            # Guard: if classified as ADD but text has negation, demote to UNKNOWN
            if intent == "ADD_ITEM" and _check_negation(text):
                return "UNKNOWN", 0.3, None
            return intent, confidence, m
    return "UNKNOWN", 0.2, None


# ──────────────────────────────────────────────
# 5. Entity extraction
# ──────────────────────────────────────────────

def _extract_items_from_text(raw_items_text: str) -> list[ParsedItem]:
    """
    Parse text like ``2 kg rice, 3 bananas and 1 litre milk``
    into a list of ParsedItem.
    """
    # Split on commas, " and ", " plus ", " & "
    segments = re.split(r"\s*,\s*|\s+and\s+|\s+plus\s+|\s*&\s*", raw_items_text)
    items: list[ParsedItem] = []

    for segment in segments:
        segment = segment.strip()
        if not segment:
            continue
        item = _parse_single_item(segment)
        if item and item.product_name:
            items.append(item)

    return items


# Pattern: optional quantity, optional unit, then product name
_ITEM_PATTERN = re.compile(
    r"^"
    r"(?:(\d+(?:\.\d+)?)\s+)?"               # optional quantity
    r"(?:(" + _UNIT_PATTERN + r")\s+)?"       # optional unit
    r"(?:of\s+)?"                              # optional "of"
    r"(.+)"                                    # product name
    r"$",
    re.IGNORECASE,
)


def _parse_single_item(segment: str) -> Optional[ParsedItem]:
    """Parse a single item segment like '2 kg rice' or 'bananas'."""
    segment = segment.strip()

    # Remove filler words from start
    segment = re.sub(r"^(?:some|the|a\s+few)\s+", "", segment, flags=re.IGNORECASE)

    m = _ITEM_PATTERN.match(segment)
    if not m:
        # Fallback: treat entire segment as product name
        product = _clean_product_name(segment)
        if product:
            return ParsedItem(product_name=product)
        return None

    qty_raw, unit_raw, product_raw = m.groups()

    quantity = Decimal("1")
    if qty_raw:
        try:
            quantity = Decimal(qty_raw)
        except InvalidOperation:
            quantity = Decimal("1")

    unit = _normalize_unit(unit_raw) if unit_raw else None

    product = _clean_product_name(product_raw)
    if not product:
        return None

    return ParsedItem(product_name=product, quantity=quantity, unit=unit)


def _clean_product_name(name: str) -> str:
    """Clean filler words, articles, trailing punctuation from a product name."""
    name = name.strip()

    # Remove leading articles/filler
    name = re.sub(r"^(?:of|the|some|my)\s+", "", name, flags=re.IGNORECASE)

    # Remove trailing list references
    name = re.sub(
        r"\s+(?:to|on|in|from)\s+(?:my\s+)?(?:shopping\s+)?list$",
        "",
        name,
        flags=re.IGNORECASE,
    )

    # Remove trailing punctuation
    name = name.rstrip(".,!?;:")

    # Remove "please" / "also"
    name = re.sub(r"\b(?:please|also)\b", "", name, flags=re.IGNORECASE)

    # Collapse whitespace
    name = re.sub(r"\s+", " ", name).strip()

    return name


# ──────────────────────────────────────────────
# 6. Confidence scoring
# ──────────────────────────────────────────────

def _score_confidence(
    base_confidence: float,
    intent: str,
    items: list[ParsedItem],
) -> float:
    """Adjust confidence based on extracted entities."""
    score = base_confidence

    if intent in ("ADD_ITEM", "REMOVE_ITEM", "COMPLETE_ITEM"):
        if not items:
            score -= 0.3
        elif items[0].product_name and len(items[0].product_name) >= 2:
            score += 0.05
        if items and items[0].quantity and items[0].quantity > 0:
            score += 0.02

    if intent in ("CLEAR_LIST", "SHOW_LIST", "HELP"):
        # These don't need entities
        score += 0.05

    return max(0.0, min(1.0, round(score, 2)))


# ──────────────────────────────────────────────
# 7. Public API
# ──────────────────────────────────────────────

def parse_voice_command(command: str) -> ParsedVoiceCommand:
    """
    Parse a raw voice transcript into a structured command.

    This function NEVER modifies the database.
    """
    raw_transcript = command.strip()
    if not raw_transcript:
        return ParsedVoiceCommand(
            intent="UNKNOWN",
            confidence=0.0,
            raw_transcript="",
        )

    # Stage 1: Text normalization
    text = _normalize_text(raw_transcript)

    # Stage 2: Number normalization
    text = _normalize_numbers(text)

    # Stage 3: Intent classification
    intent, base_confidence, match = _classify_intent(text)

    items: list[ParsedItem] = []

    # Stage 4: Entity extraction based on intent
    if intent == "ADD_ITEM" and match:
        items_text = match.group(1)
        items = _extract_items_from_text(items_text)

    elif intent == "REMOVE_ITEM" and match:
        product_text = match.group(1)
        product = _clean_product_name(product_text)
        if product:
            items = [ParsedItem(product_name=product)]

    elif intent == "COMPLETE_ITEM" and match:
        product_text = match.group(1)
        product = _clean_product_name(product_text)
        if product:
            items = [ParsedItem(product_name=product)]

    elif intent == "UPDATE_QUANTITY" and match:
        product_text = match.group(1)
        qty_text = match.group(2)
        product = _clean_product_name(product_text)
        try:
            qty = Decimal(qty_text)
        except InvalidOperation:
            qty = Decimal("1")
        if product:
            items = [ParsedItem(product_name=product, quantity=qty)]

    elif intent == "UPDATE_QUANTITY_CONTEXT" and match:
        # Contextual follow-up: "make that 3"
        qty_text = match.group(1)
        try:
            qty = Decimal(qty_text)
        except InvalidOperation:
            qty = Decimal("1")
        # Product will be resolved from context by the router
        items = [ParsedItem(product_name="", quantity=qty)]
        intent = "UPDATE_QUANTITY"

    # Stage 5: Confidence scoring
    confidence = _score_confidence(base_confidence, intent, items)

    return ParsedVoiceCommand(
        intent=intent,
        items=items,
        confidence=confidence,
        raw_transcript=raw_transcript,
    )
