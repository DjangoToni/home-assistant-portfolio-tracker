"""Pure helpers for Portfolio Tracker registry lifecycle management."""

from __future__ import annotations

from typing import Any


def active_device_identifiers(
    entry_id: str,
    holdings: list[dict[str, Any]],
    indexes: list[str],
) -> set[str]:
    """Return every device identifier that belongs to the current options."""
    identifiers = {entry_id}
    identifiers.update(
        f"{entry_id}_{holding['holding_id']}"
        for holding in holdings
        if holding.get("holding_id")
    )
    identifiers.update(
        f"{entry_id}_index_{symbol.replace('^', '').lower()}"
        for symbol in indexes
    )
    return identifiers
