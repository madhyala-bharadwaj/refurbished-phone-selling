"""
Utility functions for the PhoneDash application.

This module contains helper functions that perform specific, isolated tasks,
such as calculating platform-specific prices and mapping internal conditions
to platform-specific categories. This keeps the main services logic cleaner.
"""

from typing import Optional, Dict


def calculate_platform_price(
    base_price: float, platform: str, manual_overrides: Dict[str, Optional[float]]
) -> float:
    """
    Calculates the selling price on a specific platform based on its fee structure.

    It first checks for a manual price override for the given platform. If one
    exists, it is used. Otherwise, it calculates the price based on the
    platform's unique fee rules.

    Args:
        base_price: The base price of the phone.
        platform: The platform to calculate the price for ('X', 'Y', 'Z').
        manual_overrides: A dictionary of manually set prices.

    Returns:
        The calculated platform-specific price, rounded to 2 decimal places.
    """
    # Check for a manual override first
    if platform in manual_overrides and manual_overrides[platform] is not None:
        return manual_overrides[platform]

    # If no override, calculate based on the platform's fee structure
    if platform == "X":
        # 10% fee
        price = base_price * 1.10
    elif platform == "Y":
        # 8% fee + $2 fixed fee
        price = (base_price * 1.08) + 2.0
    elif platform == "Z":
        # 12% fee
        price = base_price * 1.12
    else:
        # Default to base price if the platform is unknown
        price = base_price

    return round(price, 2)


def map_condition_to_platform(internal_condition: str, platform: str) -> Optional[str]:
    """
    Maps an internal inventory condition to a platform-specific category.

    Args:
        internal_condition: The internal condition standard (e.g., "Excellent").
        platform: The target platform ('X', 'Y', 'Z').

    Returns:
        The platform-specific condition string, or None if the condition is not
        supported on the target platform.
    """
    # This dictionary defines the translation rules from internal to external conditions.
    CONDITION_MAPPERS = {
        "X": {
            "Excellent": "New",
            "Good": "Good",
            "Scrap": "Scrap",
        },
        "Y": {
            "Excellent": "3 stars (Excellent)",
            "Good": "2 stars (Good)",
            "Usable": "1 star (Usable)",
        },
        "Z": {
            "Excellent": "New",
            "Good": "As New",
            "Usable": "Good",
        },
    }

    platform_map = CONDITION_MAPPERS.get(platform)
    if platform_map:
        # Return the mapped condition if it exists for the given platform.
        return platform_map.get(internal_condition)

    # Return None if the platform itself is not in our mapper.
    return None
