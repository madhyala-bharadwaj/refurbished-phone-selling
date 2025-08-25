# models.py

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class PhoneBase(BaseModel):
    """
    Base model for a phone, containing common attributes.
    """

    model_name: str = Field(..., example="iPhone 12")
    brand: str = Field(..., example="Apple")
    condition: str = Field(..., example="Good")
    specifications: Dict[str, str] = Field(
        ..., example={"storage": "128GB", "color": "Black"}
    )
    stock_quantity: int = Field(..., ge=0, example=10)
    base_price: float = Field(..., gt=0, example=500.0)


class PhoneCreate(PhoneBase):
    """
    Model for creating a new phone. Inherits from PhoneBase.
    """

    pass


class PhoneUpdate(BaseModel):
    """
    Model for updating an existing phone. All fields are optional.
    """

    model_name: Optional[str] = None
    brand: Optional[str] = None
    condition: Optional[str] = None
    specifications: Optional[Dict[str, str]] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    base_price: Optional[float] = Field(None, gt=0)
    tags: Optional[List[str]] = None
    manual_overrides: Optional[Dict[str, float]] = None


class Phone(PhoneBase):
    """
    Model for representing a phone in the database and API responses.
    Includes all attributes of PhoneBase plus database-specific fields.
    """

    id: int
    platform_prices: Dict[str, float] = Field(
        ..., example={"X": 550.0, "Y": 548.0, "Z": 560.0}
    )
    manual_overrides: Dict[str, Optional[float]] = Field({}, example={"Y": 545.0})
    listed_on: List[str] = Field([], example=["X", "Y"])
    tags: List[str] = Field([], example=["out of stock", "discontinued"])

    class Config:
        """
        Pydantic configuration to allow creating models from ORM objects.
        """

        orm_mode = True


class PhonePage(BaseModel):
    """
    Model for a paginated response of phones.
    """

    total_items: int
    items: List[Phone]


class ActionLog(BaseModel):
    """
    Model for representing an action log entry.
    """

    id: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    action: str = Field(..., example="Phone Created")
    details: str = Field(..., example="Admin created 'iPhone 12'")
