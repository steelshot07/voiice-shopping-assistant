from decimal import Decimal

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.dependencies import get_current_user, rate_limit_authenticated_user
from app.database import get_db
from app.models.product import Product
from app.models.shopping_item import ShoppingItem
from app.models.user import User
from app.schemas.voice import (
    ProductOption,
    VoiceCommandRequest,
    VoiceCommandResponse,
    VoiceItemResult,
)
from app.services.voice import ParsedItem, parse_voice_command

router = APIRouter(
    prefix="/voice",
    tags=["Voice"],
)


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _find_catalog_products(db: Session, query: str) -> list[Product]:
    """Search catalog for available products matching query."""
    normalized = query.strip().lower()
    if not normalized:
        return []

    # 1. Try exact match (case-insensitive)
    exact = db.scalars(
        select(Product)
        .options(joinedload(Product.category))
        .where(Product.available.is_(True), Product.name.ilike(normalized))
        .order_by(Product.name.asc())
        .limit(10)
    ).all()
    if exact:
        return list(exact)

    # 2. Partial match
    partial = db.scalars(
        select(Product)
        .options(joinedload(Product.category))
        .where(Product.available.is_(True), Product.name.ilike(f"%{normalized}%"))
        .order_by(Product.name.asc())
        .limit(10)
    ).all()
    if partial:
        return list(partial)

    # 3. Try matching individual words in the query
    words = normalized.split()
    if len(words) > 1:
        for word in words:
            if len(word) < 3:
                continue
            word_matches = db.scalars(
                select(Product)
                .options(joinedload(Product.category))
                .where(Product.available.is_(True), Product.name.ilike(f"%{word}%"))
                .order_by(Product.name.asc())
                .limit(10)
            ).all()
            if word_matches:
                return list(word_matches)

    return []


def _product_to_option(p: Product) -> ProductOption:
    return ProductOption(
        id=p.id,
        name=p.name,
        category=p.category_name,
        price=f"{p.price:.2f}" if p.price is not None else None,
        unit=p.size_unit,
    )


def _find_shopping_item(
    db: Session, user_id: int, product_query: str
) -> list[ShoppingItem]:
    """Find shopping list items matching a product name."""
    normalized = product_query.strip().lower()
    return list(
        db.scalars(
            select(ShoppingItem)
            .join(Product)
            .options(joinedload(ShoppingItem.product).joinedload(Product.category))
            .where(
                ShoppingItem.user_id == user_id,
                ShoppingItem.completed.is_(False),
                Product.name.ilike(f"%{normalized}%"),
            )
            .order_by(ShoppingItem.id.asc())
        ).all()
    )


# ──────────────────────────────────────────────
# Intent handlers
# ──────────────────────────────────────────────

def _handle_add_item(
    parsed_items: list[ParsedItem],
    current_user: User,
    db: Session,
) -> tuple[str, str, list[VoiceItemResult], dict | None]:
    """Execute ADD_ITEM for one or more items. Returns (status, message, items, context)."""
    results: list[VoiceItemResult] = []
    overall_status = "success"
    last_context: dict | None = None

    for pi in parsed_items:
        products = _find_catalog_products(db, pi.product_name)

        if len(products) == 0:
            results.append(VoiceItemResult(
                product_name=pi.product_name,
                status="not_found",
                message=f"Couldn't find '{pi.product_name}' in the catalog.",
            ))
            overall_status = "error" if overall_status != "ambiguous" else "ambiguous"
            continue

        if len(products) > 1:
            # Check for exact name match among the results
            exact = [p for p in products if p.name.lower() == pi.product_name.lower()]
            if len(exact) == 1:
                products = exact
            else:
                results.append(VoiceItemResult(
                    product_name=pi.product_name,
                    status="ambiguous",
                    message=f"Found {len(products)} products matching '{pi.product_name}'. Which one?",
                    options=[_product_to_option(p) for p in products[:5]],
                ))
                overall_status = "ambiguous"
                continue

        product = products[0]
        quantity = pi.quantity or Decimal("1")
        unit = pi.unit

        # Check for existing item
        existing = db.scalar(
            select(ShoppingItem).where(
                ShoppingItem.user_id == current_user.id,
                ShoppingItem.product_id == product.id,
                ShoppingItem.completed.is_(False),
            )
        )

        if existing:
            existing.quantity += quantity
            if unit is not None:
                existing.unit = unit
            db.commit()
            db.refresh(existing)

            results.append(VoiceItemResult(
                product_name=product.name,
                product_id=product.id,
                quantity=float(existing.quantity),
                unit=existing.unit,
                status="success",
                message=f"Added {quantity} more {product.name} (total: {existing.quantity}).",
            ))
        else:
            item = ShoppingItem(
                user_id=current_user.id,
                product_id=product.id,
                quantity=quantity,
                unit=unit,
                completed=False,
            )
            db.add(item)
            db.commit()
            db.refresh(item)

            unit_display = f" {unit}" if unit else ""
            results.append(VoiceItemResult(
                product_name=product.name,
                product_id=product.id,
                quantity=float(quantity),
                unit=unit,
                status="success",
                message=f"Added {quantity}{unit_display} {product.name}.",
            ))

        last_context = {
            "last_action": "ADD_ITEM",
            "last_product": product.name,
            "last_product_id": product.id,
            "last_quantity": float(quantity),
        }

    success_count = sum(1 for r in results if r.status == "success")
    total = len(results)

    if success_count == total:
        msg = results[0].message if total == 1 else f"Added {success_count} items."
        status_str = "success"
    elif success_count > 0:
        msg = f"Added {success_count} of {total} items. Some need attention."
        status_str = "ambiguous"
    else:
        msg = results[0].message if total == 1 else "Couldn't add any items."
        status_str = overall_status

    return status_str, msg, results, last_context


def _handle_remove_item(
    parsed_items: list[ParsedItem],
    current_user: User,
    db: Session,
) -> tuple[str, str, list[VoiceItemResult]]:
    """Execute REMOVE_ITEM."""
    results: list[VoiceItemResult] = []

    for pi in parsed_items:
        matches = _find_shopping_item(db, current_user.id, pi.product_name)

        if not matches:
            results.append(VoiceItemResult(
                product_name=pi.product_name,
                status="not_found",
                message=f"'{pi.product_name}' is not on your list.",
            ))
            continue

        if len(matches) > 1:
            results.append(VoiceItemResult(
                product_name=pi.product_name,
                status="ambiguous",
                message=f"Found {len(matches)} items matching '{pi.product_name}'. Which one?",
                options=[_product_to_option(m.product) for m in matches if m.product],
            ))
            continue

        item = matches[0]
        product_name = item.product.name if item.product else pi.product_name
        product_id = item.product_id

        db.delete(item)
        db.commit()

        results.append(VoiceItemResult(
            product_name=product_name,
            product_id=product_id,
            status="success",
            message=f"Removed {product_name} from your list.",
        ))

    success_count = sum(1 for r in results if r.status == "success")
    total = len(results)
    msg = results[0].message if total == 1 else f"Removed {success_count} of {total} items."
    status_str = "success" if success_count == total else "error"

    return status_str, msg, results


def _handle_update_quantity(
    parsed_items: list[ParsedItem],
    current_user: User,
    db: Session,
    context: dict | None,
) -> tuple[str, str, list[VoiceItemResult], dict | None]:
    """Execute UPDATE_QUANTITY."""
    results: list[VoiceItemResult] = []
    new_context: dict | None = None

    for pi in parsed_items:
        product_query = pi.product_name

        # If product name is empty, try context
        if not product_query and context:
            product_query = context.get("last_product", "")

        if not product_query:
            results.append(VoiceItemResult(
                product_name="",
                status="error",
                message="Which product should I update?",
            ))
            continue

        matches = _find_shopping_item(db, current_user.id, product_query)

        if not matches:
            results.append(VoiceItemResult(
                product_name=product_query,
                status="not_found",
                message=f"'{product_query}' is not on your list.",
            ))
            continue

        if len(matches) > 1:
            results.append(VoiceItemResult(
                product_name=product_query,
                status="ambiguous",
                message=f"Found {len(matches)} items matching '{product_query}'. Which one?",
                options=[_product_to_option(m.product) for m in matches if m.product],
            ))
            continue

        item = matches[0]
        item.quantity = pi.quantity
        db.commit()
        db.refresh(item)

        product_name = item.product.name if item.product else product_query
        results.append(VoiceItemResult(
            product_name=product_name,
            product_id=item.product_id,
            quantity=float(item.quantity),
            unit=item.unit,
            status="success",
            message=f"Updated {product_name} to {item.quantity}.",
        ))

        new_context = {
            "last_action": "UPDATE_QUANTITY",
            "last_product": product_name,
            "last_product_id": item.product_id,
            "last_quantity": float(item.quantity),
        }

    msg = results[0].message if len(results) == 1 else "Updated quantities."
    status_str = "success" if all(r.status == "success" for r in results) else "error"

    return status_str, msg, results, new_context


def _handle_complete_item(
    parsed_items: list[ParsedItem],
    current_user: User,
    db: Session,
) -> tuple[str, str, list[VoiceItemResult]]:
    """Execute COMPLETE_ITEM."""
    results: list[VoiceItemResult] = []

    for pi in parsed_items:
        matches = _find_shopping_item(db, current_user.id, pi.product_name)

        if not matches:
            results.append(VoiceItemResult(
                product_name=pi.product_name,
                status="not_found",
                message=f"'{pi.product_name}' is not on your list.",
            ))
            continue

        if len(matches) > 1:
            results.append(VoiceItemResult(
                product_name=pi.product_name,
                status="ambiguous",
                message=f"Found {len(matches)} items matching '{pi.product_name}'. Which one?",
                options=[_product_to_option(m.product) for m in matches if m.product],
            ))
            continue

        item = matches[0]
        if not item.completed:
            item.completed = True
            db.commit()
            db.refresh(item)

        product_name = item.product.name if item.product else pi.product_name
        results.append(VoiceItemResult(
            product_name=product_name,
            product_id=item.product_id,
            quantity=float(item.quantity),
            unit=item.unit,
            status="success",
            message=f"Marked {product_name} as complete.",
        ))

    msg = results[0].message if len(results) == 1 else "Marked items complete."
    status_str = "success" if all(r.status == "success" for r in results) else "error"

    return status_str, msg, results


# ──────────────────────────────────────────────
# Main endpoint
# ──────────────────────────────────────────────

@router.post(
    "/command",
    response_model=VoiceCommandResponse,
    dependencies=[Depends(rate_limit_authenticated_user)],
)
def voice_command(
    data: VoiceCommandRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    parsed = parse_voice_command(data.command)

    # ── LOW CONFIDENCE / UNKNOWN ──
    if parsed.confidence < 0.5 or parsed.intent == "UNKNOWN":
        return VoiceCommandResponse(
            intent=parsed.intent,
            status="unknown",
            message="I couldn't understand that command.",
            confidence=parsed.confidence,
            transcript=parsed.raw_transcript,
            suggestion="Try something like 'Add 2 apples' or 'Remove milk'.",
        )

    # ── HELP ──
    if parsed.intent == "HELP":
        return VoiceCommandResponse(
            intent="HELP",
            status="success",
            message="Here's what I can do:",
            confidence=parsed.confidence,
            transcript=parsed.raw_transcript,
            suggestion=(
                "• 'Add 2 apples' — add items\n"
                "• 'Remove milk' — remove items\n"
                "• 'Change apples to 3' — update quantity\n"
                "• 'Show my list' — view your list\n"
                "• 'Mark apples complete' — check off items\n"
                "• 'Clear my list' — remove everything"
            ),
        )

    # ── SHOW LIST ──
    if parsed.intent == "SHOW_LIST":
        active_items = db.scalars(
            select(ShoppingItem)
            .options(joinedload(ShoppingItem.product))
            .where(
                ShoppingItem.user_id == current_user.id,
                ShoppingItem.completed.is_(False),
            )
            .order_by(ShoppingItem.id.asc())
        ).all()

        count = len(active_items)
        if count == 0:
            msg = "Your shopping list is empty."
        else:
            names = [i.product.name if i.product else "Unknown" for i in active_items[:5]]
            more = f" and {count - 5} more" if count > 5 else ""
            msg = f"You have {count} item(s): {', '.join(names)}{more}."

        return VoiceCommandResponse(
            intent="SHOW_LIST",
            status="success",
            message=msg,
            confidence=parsed.confidence,
            transcript=parsed.raw_transcript,
        )

    # ── CLEAR LIST ──
    if parsed.intent == "CLEAR_LIST":
        active_items = db.scalars(
            select(ShoppingItem).where(
                ShoppingItem.user_id == current_user.id,
                ShoppingItem.completed.is_(False),
            )
        ).all()

        count = len(active_items)

        if count == 0:
            return VoiceCommandResponse(
                intent="CLEAR_LIST",
                status="success",
                message="Your shopping list is already empty.",
                confidence=parsed.confidence,
                transcript=parsed.raw_transcript,
            )

        if not data.confirmed:
            return VoiceCommandResponse(
                intent="CLEAR_LIST",
                status="confirmation_needed",
                message=f"Clear your entire shopping list? This will remove {count} item(s).",
                confidence=parsed.confidence,
                transcript=parsed.raw_transcript,
                confirmation_required=True,
            )

        for item in active_items:
            db.delete(item)
        db.commit()

        return VoiceCommandResponse(
            intent="CLEAR_LIST",
            status="success",
            message=f"Cleared {count} item(s) from your shopping list.",
            confidence=parsed.confidence,
            transcript=parsed.raw_transcript,
        )

    # ── ADD ITEM ──
    if parsed.intent == "ADD_ITEM":
        if not parsed.items:
            return VoiceCommandResponse(
                intent="ADD_ITEM",
                status="error",
                message="What would you like to add?",
                confidence=parsed.confidence,
                transcript=parsed.raw_transcript,
                suggestion="Try 'Add 2 apples' or 'Add milk and eggs'.",
            )

        resp_status, msg, items, ctx = _handle_add_item(
            parsed.items, current_user, db
        )
        return VoiceCommandResponse(
            intent="ADD_ITEM",
            status=resp_status,
            message=msg,
            items=items,
            confidence=parsed.confidence,
            transcript=parsed.raw_transcript,
            context=ctx,
        )

    # ── REMOVE ITEM ──
    if parsed.intent == "REMOVE_ITEM":
        if not parsed.items:
            return VoiceCommandResponse(
                intent="REMOVE_ITEM",
                status="error",
                message="What would you like to remove?",
                confidence=parsed.confidence,
                transcript=parsed.raw_transcript,
                suggestion="Try 'Remove apples' or 'Delete milk'.",
            )

        resp_status, msg, items = _handle_remove_item(
            parsed.items, current_user, db
        )
        return VoiceCommandResponse(
            intent="REMOVE_ITEM",
            status=resp_status,
            message=msg,
            items=items,
            confidence=parsed.confidence,
            transcript=parsed.raw_transcript,
        )

    # ── UPDATE QUANTITY ──
    if parsed.intent == "UPDATE_QUANTITY":
        if not parsed.items:
            return VoiceCommandResponse(
                intent="UPDATE_QUANTITY",
                status="error",
                message="What would you like to update?",
                confidence=parsed.confidence,
                transcript=parsed.raw_transcript,
                suggestion="Try 'Change apples to 3'.",
            )

        resp_status, msg, items, ctx = _handle_update_quantity(
            parsed.items, current_user, db, data.context
        )
        return VoiceCommandResponse(
            intent="UPDATE_QUANTITY",
            status=resp_status,
            message=msg,
            items=items,
            confidence=parsed.confidence,
            transcript=parsed.raw_transcript,
            context=ctx,
        )

    # ── COMPLETE ITEM ──
    if parsed.intent == "COMPLETE_ITEM":
        if not parsed.items:
            return VoiceCommandResponse(
                intent="COMPLETE_ITEM",
                status="error",
                message="What would you like to mark as complete?",
                confidence=parsed.confidence,
                transcript=parsed.raw_transcript,
                suggestion="Try 'Mark apples complete'.",
            )

        resp_status, msg, items = _handle_complete_item(
            parsed.items, current_user, db
        )
        return VoiceCommandResponse(
            intent="COMPLETE_ITEM",
            status=resp_status,
            message=msg,
            items=items,
            confidence=parsed.confidence,
            transcript=parsed.raw_transcript,
        )

    # Fallback
    return VoiceCommandResponse(
        intent=parsed.intent,
        status="unknown",
        message="I couldn't understand that command.",
        confidence=parsed.confidence,
        transcript=parsed.raw_transcript,
        suggestion="Try 'Add 2 apples' or 'Remove milk'.",
    )
