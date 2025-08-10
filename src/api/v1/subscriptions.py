import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from src.models.subscription_models import (
    Subscription,
    SubscriptionCreate,
    SubscriptionUpdate,
)
from src.api.v1.dependencies import get_current_user

router = APIRouter()

# --- FAKE DATABASE ---
# A simple list to store subscription records in memory.
# In a real application, this would be replaced with database operations.
fake_subscriptions_db = []


@router.post("/", response_model=Subscription, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription: SubscriptionCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new subscription for the currently authenticated user.
    """
    user_id = current_user["id"]
    new_sub_id = uuid.uuid4()

    # In a real app, this would be an INSERT query into the `subscriptions` table.
    db_subscription = {
        "id": new_sub_id,
        "user_id": user_id,
        "last_reminder_sent_at": None,
        **subscription.dict()
    }
    fake_subscriptions_db.append(db_subscription)

    return db_subscription


@router.get("/", response_model=List[Subscription])
async def read_subscriptions(
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve all subscriptions for the currently authenticated user.
    """
    user_id = current_user["id"]

    # In a real app, this would be a SELECT query with a WHERE clause on `user_id`.
    user_subscriptions = [
        sub for sub in fake_subscriptions_db if sub["user_id"] == user_id
    ]

    return user_subscriptions


@router.get("/{subscription_id}", response_model=Subscription)
async def read_subscription(
    subscription_id: uuid.UUID,
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve a specific subscription by its ID.
    Ensures the subscription belongs to the current user.
    """
    user_id = current_user["id"]

    # In a real app, this would be a SELECT query with a WHERE clause on `id` and `user_id`.
    for sub in fake_subscriptions_db:
        if sub["id"] == subscription_id:
            if sub["user_id"] != user_id:
                # If the sub exists but belongs to another user, raise 404
                # to avoid leaking information about its existence.
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")
            return sub

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")


@router.put("/{subscription_id}", response_model=Subscription)
async def update_subscription(
    subscription_id: uuid.UUID,
    subscription_in: SubscriptionUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update a subscription's details.
    """
    user_id = current_user["id"]

    # Find the subscription and verify ownership
    sub_index = -1
    for i, sub in enumerate(fake_subscriptions_db):
        if sub["id"] == subscription_id:
            if sub["user_id"] != user_id:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")
            sub_index = i
            break

    if sub_index == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")

    # Update the data
    # `exclude_unset=True` ensures we only update fields that were actually provided.
    update_data = subscription_in.dict(exclude_unset=True)
    fake_subscriptions_db[sub_index].update(update_data)

    return fake_subscriptions_db[sub_index]


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscription(
    subscription_id: uuid.UUID,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a subscription.
    """
    user_id = current_user["id"]

    sub_to_delete = None
    for sub in fake_subscriptions_db:
        if sub["id"] == subscription_id:
            if sub["user_id"] != user_id:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")
            sub_to_delete = sub
            break

    if sub_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")

    fake_subscriptions_db.remove(sub_to_delete)

    # No content is returned for a 204 response
    return
