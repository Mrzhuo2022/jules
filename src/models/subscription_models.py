import uuid
from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

# Shared properties for a subscription
class SubscriptionBase(BaseModel):
    service_name: str = Field(..., example="Netflix")
    price: Decimal = Field(..., gt=0, example=15.99)
    currency: str = Field("USD", min_length=3, max_length=3, example="USD")
    billing_cycle: Literal['monthly', 'yearly'] = Field(..., example="monthly")
    next_renewal_date: date = Field(..., example="2025-09-09")

# Properties to receive on subscription creation
class SubscriptionCreate(SubscriptionBase):
    pass

# Properties to receive on subscription update
class SubscriptionUpdate(BaseModel):
    service_name: str | None = Field(None, example="Netflix Premium")
    price: Decimal | None = Field(None, gt=0, example=19.99)
    currency: str | None = Field(None, min_length=3, max_length=3, example="USD")
    billing_cycle: Literal['monthly', 'yearly'] | None = Field(None, example="monthly")
    next_renewal_date: date | None = Field(None, example="2025-10-09")

# Properties returned to the client
class Subscription(SubscriptionBase):
    id: uuid.UUID

    class Config:
        # This allows the model to be created from ORM objects
        from_attributes = True
