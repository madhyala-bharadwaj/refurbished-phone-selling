"""
Core business logic for the PhoneDash application.

This module contains all the functions that interact with the database and
implement the main features, such as creating phones, calculating prices,
managing inventory, and generating analytics. It acts as a service layer,
separating the API routing from the data manipulation.
"""

import json
from typing import List, Dict, Any, Optional
from database import db, save_phone_database, action_log_db, save_log_database
from models import Phone, ActionLog, PhonePage
from utils import map_condition_to_platform, calculate_platform_price

# --- Helper Functions ---


def _ensure_specifications_is_dict(phone_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensures the 'specifications' field is a dictionary.

    If 'specifications' is a JSON string (e.g., from a CSV upload),
    this function parses it into a dictionary. This prevents data type errors.

    Args:
        phone_data: A dictionary representing a phone.

    Returns:
        The phone dictionary with 'specifications' guaranteed to be a dict.
    """
    if "specifications" in phone_data and isinstance(phone_data["specifications"], str):
        try:
            phone_data["specifications"] = json.loads(phone_data["specifications"])
        except json.JSONDecodeError:
            # If parsing fails, default to an empty dict to prevent crashes.
            phone_data["specifications"] = {}
    return phone_data


# --- Action Logging Service ---


def log_action(action: str, details: str):
    """
    Records an action to the action log database.

    Args:
        action: The type of action performed (e.g., "Phone Created").
        details: A human-readable description of the action.
    """
    log_id = max([log["id"] for log in action_log_db]) + 1 if action_log_db else 1
    new_log = ActionLog(id=log_id, action=action, details=details)
    action_log_db.insert(
        0, new_log.dict()
    )  # Insert at the beginning for chronological order
    save_log_database(action_log_db)


# --- Phone CRUD and Management Services ---


def get_phone_by_id(phone_id: int) -> Optional[Phone]:
    """
    Retrieves a single phone from the database by its unique ID.

    Args:
        phone_id: The ID of the phone to retrieve.

    Returns:
        A Pydantic Phone model instance if found, otherwise None.
    """
    for phone in db:
        if phone["id"] == phone_id:
            return Phone(**_ensure_specifications_is_dict(phone))
    return None


def create_phone(phone_data: Dict[str, Any]) -> Phone:
    """
    Creates a new phone, adds it to the database, and logs the action.

    Args:
        phone_data: A dictionary of the new phone's attributes.

    Returns:
        A Pydantic Phone model instance of the newly created phone.
    """
    phone_id = max([p["id"] for p in db]) + 1 if db else 1
    phone_data = _ensure_specifications_is_dict(phone_data)

    new_phone = {
        "id": phone_id,
        **phone_data,
        "platform_prices": {},
        "manual_overrides": {},
        "listed_on": [],
        "tags": [],
    }
    new_phone["platform_prices"] = {
        p: calculate_platform_price(
            new_phone["base_price"], p, new_phone["manual_overrides"]
        )
        for p in ["X", "Y", "Z"]
    }

    db.append(new_phone)
    save_phone_database(db)
    log_action("Phone Created", f"New phone '{phone_data['model_name']}' was added.")
    return Phone(**new_phone)


def update_phone(phone_id: int, phone_update: Dict[str, Any]) -> Optional[Phone]:
    """
    Updates an existing phone's details in the database.

    Args:
        phone_id: The ID of the phone to update.
        phone_update: A dictionary of attributes to update.

    Returns:
        The updated Pydantic Phone model instance, or None if not found.
    """
    for phone in db:
        if phone["id"] == phone_id:
            # Handle nested dictionary updates separately to avoid overwriting.
            if "manual_overrides" in phone_update:
                phone["manual_overrides"] = phone_update["manual_overrides"]
                del phone_update["manual_overrides"]

            phone.update(phone_update)

            # Recalculate prices if the base price or overrides have changed.
            phone["platform_prices"] = {
                p: calculate_platform_price(
                    phone["base_price"], p, phone["manual_overrides"]
                )
                for p in ["X", "Y", "Z"]
            }

            save_phone_database(db)
            log_action(
                "Phone Updated",
                f"Phone ID {phone_id} ('{phone['model_name']}') was updated.",
            )
            return Phone(**_ensure_specifications_is_dict(phone))
    return None


def delete_phone(phone_id: int) -> bool:
    """
    Deletes a phone from the database by its ID.

    Args:
        phone_id: The ID of the phone to delete.

    Returns:
        True if the deletion was successful, False otherwise.
    """
    phone_to_delete = next((p for p in db if p["id"] == phone_id), None)
    if phone_to_delete:
        model_name = phone_to_delete["model_name"]
        db.remove(phone_to_delete)
        save_phone_database(db)
        log_action(
            "Phone Deleted", f"Phone '{model_name}' (ID: {phone_id}) was deleted."
        )
        return True
    return False


def list_phone_on_platform(phone_id: int, platform: str) -> Dict[str, Any]:
    """
    Simulates listing a phone on a specific platform after running business rule checks.

    Args:
        phone_id: The ID of the phone to list.
        platform: The target platform ('X', 'Y', or 'Z').

    Returns:
        A dictionary with a success message or an error message.
    """
    phone = get_phone_by_id(phone_id)
    if not phone:
        return {"error": "Phone not found"}
    if phone.stock_quantity == 0:
        return {"error": "Cannot list out-of-stock phone"}

    platform_condition = map_condition_to_platform(phone.condition, platform)
    if not platform_condition:
        return {"error": f"Condition '{phone.condition}' not supported on {platform}"}

    # Profitability check example
    if platform == "X" and phone.base_price < 50:
        return {"error": "Listing fee too high for this phone on platform X"}

    if platform not in phone.listed_on:
        phone.listed_on.append(platform)
        # Update the raw dictionary in the database
        for phone_dict in db:
            if phone_dict["id"] == phone_id:
                phone_dict["listed_on"] = phone.listed_on
                save_phone_database(db)
                break
        log_action(
            "Platform Listing", f"'{phone.model_name}' listed on platform {platform}."
        )

    return {
        "message": f"Successfully listed '{phone.model_name}' on platform {platform}"
    }


def search_and_filter_phones(
    brand: Optional[str],
    condition: Optional[str],
    platform: Optional[str],
    skip: int = 0,
    limit: int = 15,
) -> PhonePage:
    """
    Searches, filters, and paginates the phone inventory.

    Args:
        brand: The brand to filter by.
        condition: The condition to filter by.
        platform: The platform to filter by.
        skip: The number of items to skip for pagination.
        limit: The maximum number of items to return.

    Returns:
        A PhonePage object containing the list of phones and the total count.
    """
    results = db
    if brand:
        results = [p for p in results if p["brand"].lower() == brand.lower()]
    if condition:
        results = [p for p in results if p["condition"].lower() == condition.lower()]
    if platform:
        results = [p for p in results if platform in p["listed_on"]]

    total_items = len(results)
    paginated_results = results[skip : skip + limit]

    items = [Phone(**_ensure_specifications_is_dict(p)) for p in paginated_results]

    return PhonePage(total_items=total_items, items=items)


def bulk_list_on_platform(
    platform: str, brand: Optional[str], condition: Optional[str]
) -> Dict[str, int]:
    """
    Bulk lists all filtered phones onto a specific platform.

    Args:
        platform: The target platform.
        brand: The brand to filter by.
        condition: The condition to filter by.

    Returns:
        A dictionary with the count of successful and failed listings.
    """
    phone_page = search_and_filter_phones(brand, condition, None, skip=0, limit=len(db))
    phones_to_list = phone_page.items

    success_count = 0
    fail_count = 0
    for phone in phones_to_list:
        if platform not in phone.listed_on:
            result = list_phone_on_platform(phone.id, platform)
            if "error" in result:
                fail_count += 1
            else:
                success_count += 1

    log_action(
        "Bulk Listing",
        f"Attempted to bulk list {success_count + fail_count} phones on Platform {platform}. Success: {success_count}, Failed: {fail_count}.",
    )
    return {"success": success_count, "failed": fail_count}


def update_platform_prices():
    """Triggers a recalculation of all platform prices for all phones."""
    for phone in db:
        phone["platform_prices"] = {
            p: calculate_platform_price(
                phone["base_price"], p, phone.get("manual_overrides", {})
            )
            for p in ["X", "Y", "Z"]
        }
    save_phone_database(db)
    log_action("Price Update", "Automatic price update triggered for all phones.")


def bulk_upload_phones(phones_data: List[Dict[str, Any]]):
    """
    Adds multiple phones to the inventory from a list of dictionaries (from CSV).

    Args:
        phones_data: A list of phone data dictionaries.
    """
    count = 0
    for phone_data in phones_data:
        phone_data = _ensure_specifications_is_dict(phone_data)
        create_phone(phone_data)
        count += 1
    log_action("Bulk Upload", f"{count} phones were added via bulk upload.")


# --- Analytics and Log Services ---


def get_dashboard_analytics(
    brand: Optional[str], condition: Optional[str], platform: Optional[str]
) -> Dict[str, Any]:
    """
    Generates analytics data for the dashboard, applying filters.

    Args:
        brand: The brand to filter by.
        condition: The condition to filter by.
        platform: The platform to filter by.

    Returns:
        A dictionary containing various analytics metrics.
    """
    results = db
    if brand:
        results = [p for p in results if p["brand"].lower() == brand.lower()]
    if condition:
        results = [p for p in results if p["condition"].lower() == condition.lower()]
    if platform:
        results = [p for p in results if platform in p["listed_on"]]

    if not results:
        return {
            "total_phones": 0,
            "total_stock_units": 0,
            "total_inventory_value": 0,
            "stock_by_brand": {},
            "stock_by_condition": {},
        }

    brands = [p["brand"] for p in results]
    stock_by_brand = {b: brands.count(b) for b in set(brands)}

    conditions = [p["condition"] for p in results]
    stock_by_condition = {c: conditions.count(c) for c in set(conditions)}

    total_inventory_value = sum(p["base_price"] * p["stock_quantity"] for p in results)

    return {
        "total_phones": len(results),
        "total_stock_units": sum(p["stock_quantity"] for p in results),
        "total_inventory_value": total_inventory_value,
        "stock_by_brand": stock_by_brand,
        "stock_by_condition": stock_by_condition,
    }


def get_action_logs() -> List[ActionLog]:
    """Retrieves all action logs from the database."""
    return [ActionLog(**log) for log in action_log_db]
