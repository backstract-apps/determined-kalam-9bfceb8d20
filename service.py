from sqlalchemy.orm import Session, aliased
from database import SessionLocal
from sqlalchemy import and_, or_
from typing import *
from loguru import logger
from fastapi import Request, UploadFile, HTTPException, status
from fastapi.responses import RedirectResponse, StreamingResponse
import models, schemas
import boto3
import jwt
from datetime import datetime, timezone, date, time
import requests
import math
import os
import json
import random
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from agents import (
    Agent,
    Runner,
    RunConfig,
    ModelSettings,
    InputGuardrail,
    OutputGuardrail,
)
import agent_session_store as store


load_dotenv()


def convert_to_datetime(date_string):
    if isinstance(date_string, datetime):
        return date_string
    if date_string is None:
        return datetime.now()
    if not date_string.strip():
        return datetime.now()
    if "T" in date_string:
        try:
            return datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        except ValueError:
            date_part = date_string.split("T")[0]
            try:
                return datetime.strptime(date_part, "%Y-%m-%d")
            except ValueError:
                return datetime.now()
    else:
        # Try to determine format based on first segment
        parts = date_string.split("-")
        if len(parts[0]) == 4:
            # Likely YYYY-MM-DD format
            try:
                return datetime.strptime(date_string, "%Y-%m-%d")
            except ValueError:
                return datetime.now()

        # Try DD-MM-YYYY format
        try:
            return datetime.strptime(date_string, "%d-%m-%Y")
        except ValueError:
            return datetime.now()

        # Fallback: try YYYY-MM-DD if not already tried
        if len(parts[0]) != 4:
            try:
                return datetime.strptime(date_string, "%Y-%m-%d")
            except ValueError:
                return datetime.now()

        return datetime.now()


class SessionStoreAdapter:

    def load_session(self, session_id: str) -> dict:
        return store.load_session_memory(session_id)

    def save_session(self, session_id: str, data: dict) -> None:
        store.save_session_memory(session_id, data)


_memory_adapter = SessionStoreAdapter()


async def agent_create_session(body: str):
    """Start a new chat session."""
    meta = store.create_session(title=body, session_id=body)
    return meta


async def agent_get_history(session_id: str):
    """Return the human-readable message history for a session."""
    if not store.get_session(session_id):
        raise HTTPException(404, "Session not found")
    messages = store.get_chat_history(session_id)
    return {"session_id": session_id, "messages": messages}


async def _agent_generate_title(
    first_message: str, run_config: RunConfig, agent: Agent
) -> str:
    """Ask the LLM for a short 4-word session title from the first user message."""
    try:
        result = await asyncio.wait_for(
            Runner.run(
                agent,
                f"Give a 4-word title (no quotes, no punctuation) that summarises this message: {first_message[:300]}",
                run_config=run_config,
            ),
            timeout=15,
        )
        title = str(result.final_output).strip()[:60]
        return title if title else first_message[:40]
    except Exception:
        return first_message[:40]


async def get_watchlist(
    request: Request,
    db: Session,
):

    query = db.query(models.Watchlist)

    watchlist_all = query.all()
    watchlist_all = (
        [new_data.to_dict() for new_data in watchlist_all]
        if watchlist_all
        else watchlist_all
    )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"watchlist_all": watchlist_all},
    }
    return res


async def get_listings(
    request: Request,
    db: Session,
):

    query = db.query(models.Listings)

    listings_all = query.all()
    listings_all = (
        [new_data.to_dict() for new_data in listings_all]
        if listings_all
        else listings_all
    )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"listings_all": listings_all},
    }
    return res


async def get_profiles(
    request: Request,
    db: Session,
):

    query = db.query(models.Profiles)

    profiles_all = query.all()
    profiles_all = (
        [new_data.to_dict() for new_data in profiles_all]
        if profiles_all
        else profiles_all
    )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"profiles_all": profiles_all},
    }
    return res


async def get_users(
    request: Request,
    db: Session,
):

    query = db.query(models.Users)

    users_all = query.all()
    users_all = (
        [new_data.to_dict() for new_data in users_all] if users_all else users_all
    )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"users_all": users_all},
    }
    return res


async def get_platform_auth_package_mayson_sso_auth_callback(
    request: Request,
    db: Session,
):

    user_identity: str = "i"

    user_password: str = "top_secret_area_51"

    from passlib.hash import md5_crypt

    encrypt_pass = md5_crypt.hash(user_password)

    # get user email from request

    try:
        param_obj = dict(request.query_params)

        not_found_page = "https://mayson.dev/not-found"
        user_identity = param_obj.get(
            "user_email", "no-user-identity-received-from-backend"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

    query = db.query(models.Users)
    query = query.filter(and_(models.Users.email == user_identity))
    has_a_record = query.count() > 0

    if has_a_record:
        pass

    else:

        record_to_be_added = {"email": user_identity, "password": encrypt_pass}
        new_users = models.Users(**record_to_be_added)
        db.add(new_users)
        db.commit()
        db.refresh(new_users)
        post_user_record = new_users.to_dict()

    query = db.query(models.Users)
    query = query.filter(and_(models.Users.email == user_identity))

    user_record = query.first()

    user_record = (
        (
            user_record.to_dict()
            if hasattr(user_record, "to_dict")
            else vars(user_record)
        )
        if user_record
        else user_record
    )

    import jwt
    from datetime import timezone

    secret_key = """vI0ddZJ-mrUJi9TYiV1rXQNMzX2EtmjCV_LJU1SEwl4="""
    bs_jwt_payload = {
        "exp": int(datetime.now(timezone.utc).timestamp() + 86400),
        "data": user_record,
    }

    generated_jwt = jwt.encode(bs_jwt_payload, secret_key, algorithm="HS256")

    # define client

    try:
        request_token = generated_jwt or "no-generated-jwt"
        request_provider = param_obj.get("provider", "no-provider-from-backend")
        final_url = f'{param_obj.get("frontend-redirect", not_found_page)}?token={request_token}&provider={request_provider}'

        return RedirectResponse(url=final_url)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

    res = {
        "status": 200,
        "message": "The request has been successfully processed",
        "data": {"message": "success_response"},
    }
    return res


async def get_reviews(
    request: Request,
    db: Session,
):

    query = db.query(models.Reviews)

    reviews_all = query.all()
    reviews_all = (
        [new_data.to_dict() for new_data in reviews_all] if reviews_all else reviews_all
    )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"reviews_all": reviews_all},
    }
    return res


async def post_platform_auth_package_mayson_auth_user_login(
    request: Request,
    db: Session,
    raw_data: schemas.PostPlatformAuthPackageMaysonAuthUserLogin,
):
    email: str = raw_data.email
    password: str = raw_data.password

    query = db.query(models.Users)
    query = query.filter(and_(models.Users.email == email))

    oneRecord = query.first()

    oneRecord = (
        (oneRecord.to_dict() if hasattr(oneRecord, "to_dict") else vars(oneRecord))
        if oneRecord
        else oneRecord
    )

    if oneRecord:
        from passlib.hash import md5_crypt

        password_hash_mayson = oneRecord["password"]
        password_valid = md5_crypt.verify(password, password_hash_mayson)
        if password_valid:
            validated_password = True
        else:
            validated_password = False
    else:
        validated_password = False

    login_status: str = "Login initiated"

    if validated_password:

        login_status = "Login success"

    else:

        raise HTTPException(status_code=401, detail="Bad credentials.")

    query = db.query(models.Users)
    query = query.filter(and_(models.Users.email == email))

    user_record = query.first()

    user_record = (
        (
            user_record.to_dict()
            if hasattr(user_record, "to_dict")
            else vars(user_record)
        )
        if user_record
        else user_record
    )

    import jwt
    from datetime import timezone

    secret_key = """vI0ddZJ-mrUJi9TYiV1rXQNMzX2EtmjCV_LJU1SEwl4="""
    bs_jwt_payload = {
        "exp": int(datetime.now(timezone.utc).timestamp() + 86400),
        "data": user_record,
    }

    generated_jwt = jwt.encode(bs_jwt_payload, secret_key, algorithm="HS256")

    login_status = "Login successful"

    res = {
        "status": 200,
        "message": "Login successful",
        "data": {"jwt": generated_jwt, "login_status": login_status},
    }
    return res


async def get_orders(
    request: Request,
    db: Session,
):

    query = db.query(models.Orders)

    orders_all = query.all()
    orders_all = (
        [new_data.to_dict() for new_data in orders_all] if orders_all else orders_all
    )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"orders_all": orders_all},
    }
    return res


async def get_messages(
    request: Request,
    db: Session,
):

    query = db.query(models.Messages)

    messages_all = query.all()
    messages_all = (
        [new_data.to_dict() for new_data in messages_all]
        if messages_all
        else messages_all
    )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"messages_all": messages_all},
    }
    return res


async def get_orders_id(
    request: Request,
    db: Session,
    id: Union[int, float],
):

    query = db.query(models.Orders)
    query = query.filter(and_(models.Orders.id == id))

    orders_one = query.first()

    orders_one = (
        (orders_one.to_dict() if hasattr(orders_one, "to_dict") else vars(orders_one))
        if orders_one
        else orders_one
    )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"orders_one": orders_one},
    }
    return res


async def post_orders(
    request: Request,
    db: Session,
    raw_data: schemas.PostOrders,
):
    listing_id: Union[int, float] = raw_data.listing_id
    buyer_id: Union[int, float] = raw_data.buyer_id
    seller_id: Union[int, float] = raw_data.seller_id
    final_price: float = raw_data.final_price
    status: str = raw_data.status
    created_at_dt: str = convert_to_datetime(raw_data.created_at_dt)
    updated_at_dt: str = convert_to_datetime(raw_data.updated_at_dt)

    record_to_be_added = {
        "status": status,
        "buyer_id": buyer_id,
        "seller_id": seller_id,
        "listing_id": listing_id,
        "final_price": final_price,
        "created_at_dt": created_at_dt,
        "updated_at_dt": updated_at_dt,
    }
    new_orders = models.Orders(**record_to_be_added)
    db.add(new_orders)
    db.commit()
    db.refresh(new_orders)
    orders_inserted_record = new_orders.to_dict()

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"orders_inserted_record": orders_inserted_record},
    }
    return res


async def put_orders_id(
    request: Request,
    db: Session,
    raw_data: schemas.PutOrdersId,
):
    id: str = raw_data.id
    listing_id: Union[int, float] = raw_data.listing_id
    buyer_id: Union[int, float] = raw_data.buyer_id
    seller_id: Union[int, float] = raw_data.seller_id
    final_price: float = raw_data.final_price
    status: str = raw_data.status
    created_at_dt: str = convert_to_datetime(raw_data.created_at_dt)
    updated_at_dt: str = convert_to_datetime(raw_data.updated_at_dt)

    query = db.query(models.Orders)
    query = query.filter(and_(models.Orders.id == id))
    orders_edited_record = query.first()

    if orders_edited_record:
        for key, value in {
            "id": id,
            "status": status,
            "buyer_id": buyer_id,
            "seller_id": seller_id,
            "listing_id": listing_id,
            "final_price": final_price,
            "created_at_dt": created_at_dt,
            "updated_at_dt": updated_at_dt,
        }.items():
            setattr(orders_edited_record, key, value)

        db.commit()

        db.refresh(orders_edited_record)

        orders_edited_record = (
            orders_edited_record.to_dict()
            if hasattr(orders_edited_record, "to_dict")
            else vars(orders_edited_record)
        )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"orders_edited_record": orders_edited_record},
    }
    return res


async def delete_orders_id(
    request: Request,
    db: Session,
    id: Union[int, float],
):

    query = db.query(models.Orders)
    query = query.filter(and_(models.Orders.id == id))

    record_to_delete = query.first()
    if record_to_delete:
        db.delete(record_to_delete)
        db.commit()
        orders_deleted = record_to_delete.to_dict()
    else:
        orders_deleted = record_to_delete

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"orders_deleted": orders_deleted},
    }
    return res


async def get_profiles_id(
    request: Request,
    db: Session,
    id: Union[int, float],
):

    query = db.query(models.Profiles)
    query = query.filter(and_(models.Profiles.id == id))

    profiles_one = query.first()

    profiles_one = (
        (
            profiles_one.to_dict()
            if hasattr(profiles_one, "to_dict")
            else vars(profiles_one)
        )
        if profiles_one
        else profiles_one
    )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"profiles_one": profiles_one},
    }
    return res


async def post_profiles(
    request: Request,
    db: Session,
    raw_data: schemas.PostProfiles,
):
    users_id: Union[int, float] = raw_data.users_id
    full_name: str = raw_data.full_name
    avatar_url: str = raw_data.avatar_url
    location: str = raw_data.location
    bio: str = raw_data.bio
    rating_avg: float = raw_data.rating_avg
    created_at_dt: str = convert_to_datetime(raw_data.created_at_dt)
    updated_at_dt: str = convert_to_datetime(raw_data.updated_at_dt)

    record_to_be_added = {
        "bio": bio,
        "location": location,
        "users_id": users_id,
        "full_name": full_name,
        "avatar_url": avatar_url,
        "rating_avg": rating_avg,
        "created_at_dt": created_at_dt,
        "updated_at_dt": updated_at_dt,
    }
    new_profiles = models.Profiles(**record_to_be_added)
    db.add(new_profiles)
    db.commit()
    db.refresh(new_profiles)
    profiles_inserted_record = new_profiles.to_dict()

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"profiles_inserted_record": profiles_inserted_record},
    }
    return res


async def put_profiles_id(
    request: Request,
    db: Session,
    raw_data: schemas.PutProfilesId,
):
    id: str = raw_data.id
    users_id: Union[int, float] = raw_data.users_id
    full_name: str = raw_data.full_name
    avatar_url: str = raw_data.avatar_url
    location: str = raw_data.location
    bio: str = raw_data.bio
    rating_avg: float = raw_data.rating_avg
    created_at_dt: str = convert_to_datetime(raw_data.created_at_dt)
    updated_at_dt: str = convert_to_datetime(raw_data.updated_at_dt)

    query = db.query(models.Profiles)
    query = query.filter(and_(models.Profiles.id == id))
    profiles_edited_record = query.first()

    if profiles_edited_record:
        for key, value in {
            "id": id,
            "bio": bio,
            "location": location,
            "users_id": users_id,
            "full_name": full_name,
            "avatar_url": avatar_url,
            "rating_avg": rating_avg,
            "created_at_dt": created_at_dt,
            "updated_at_dt": updated_at_dt,
        }.items():
            setattr(profiles_edited_record, key, value)

        db.commit()

        db.refresh(profiles_edited_record)

        profiles_edited_record = (
            profiles_edited_record.to_dict()
            if hasattr(profiles_edited_record, "to_dict")
            else vars(profiles_edited_record)
        )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"profiles_edited_record": profiles_edited_record},
    }
    return res


async def delete_profiles_id(
    request: Request,
    db: Session,
    id: Union[int, float],
):

    query = db.query(models.Profiles)
    query = query.filter(and_(models.Profiles.id == id))

    record_to_delete = query.first()
    if record_to_delete:
        db.delete(record_to_delete)
        db.commit()
        profiles_deleted = record_to_delete.to_dict()
    else:
        profiles_deleted = record_to_delete

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"profiles_deleted": profiles_deleted},
    }
    return res


async def get_watchlist_id(
    request: Request,
    db: Session,
    id: Union[int, float],
):

    query = db.query(models.Watchlist)
    query = query.filter(and_(models.Watchlist.id == id))

    watchlist_one = query.first()

    watchlist_one = (
        (
            watchlist_one.to_dict()
            if hasattr(watchlist_one, "to_dict")
            else vars(watchlist_one)
        )
        if watchlist_one
        else watchlist_one
    )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"watchlist_one": watchlist_one},
    }
    return res


async def post_watchlist(
    request: Request,
    db: Session,
    raw_data: schemas.PostWatchlist,
):
    users_id: Union[int, float] = raw_data.users_id
    listing_id: Union[int, float] = raw_data.listing_id
    created_at_dt: str = convert_to_datetime(raw_data.created_at_dt)

    record_to_be_added = {
        "users_id": users_id,
        "listing_id": listing_id,
        "created_at_dt": created_at_dt,
    }
    new_watchlist = models.Watchlist(**record_to_be_added)
    db.add(new_watchlist)
    db.commit()
    db.refresh(new_watchlist)
    watchlist_inserted_record = new_watchlist.to_dict()

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"watchlist_inserted_record": watchlist_inserted_record},
    }
    return res


async def put_watchlist_id(
    request: Request,
    db: Session,
    raw_data: schemas.PutWatchlistId,
):
    id: str = raw_data.id
    users_id: Union[int, float] = raw_data.users_id
    listing_id: Union[int, float] = raw_data.listing_id
    created_at_dt: str = convert_to_datetime(raw_data.created_at_dt)

    query = db.query(models.Watchlist)
    query = query.filter(and_(models.Watchlist.id == id))
    watchlist_edited_record = query.first()

    if watchlist_edited_record:
        for key, value in {
            "id": id,
            "users_id": users_id,
            "listing_id": listing_id,
            "created_at_dt": created_at_dt,
        }.items():
            setattr(watchlist_edited_record, key, value)

        db.commit()

        db.refresh(watchlist_edited_record)

        watchlist_edited_record = (
            watchlist_edited_record.to_dict()
            if hasattr(watchlist_edited_record, "to_dict")
            else vars(watchlist_edited_record)
        )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"watchlist_edited_record": watchlist_edited_record},
    }
    return res


async def delete_watchlist_id(
    request: Request,
    db: Session,
    id: Union[int, float],
):

    query = db.query(models.Watchlist)
    query = query.filter(and_(models.Watchlist.id == id))

    record_to_delete = query.first()
    if record_to_delete:
        db.delete(record_to_delete)
        db.commit()
        watchlist_deleted = record_to_delete.to_dict()
    else:
        watchlist_deleted = record_to_delete

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"watchlist_deleted": watchlist_deleted},
    }
    return res


async def get_platform_auth_package_mayson_sso_auth_login_google(
    request: Request,
    db: Session,
):

    # define client

    try:
        import httpx

        async def google_login():
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": "Bearer v4.public.eyJlbWFpbF9pZCI6ICJnZnN2aXNoYWxzQGdtYWlsLmNvbSIsICJ1c2VyX2lkIjogImIxZjE5MWJhYTVkOTQwOWZiNDQ4YzlhYTBjOGJlY2MwIiwgIm9yZ19pZCI6ICJOQSIsICJzdGF0ZSI6ICJzaWdudXAiLCAicm9sZV9uYW1lIjogIk5BIiwgInJvbGVfaWQiOiAiTkEiLCAicGxhbl9pZCI6ICIxMDEiLCAiYWNjb3VudF92ZXJpZmllZCI6ICIxIiwgImFjY291bnRfc3RhdHVzIjogIjAiLCAidXNlcl9uYW1lIjogIkdGU1Zpc2hhbCIsICJzaWdudXBfcXVlc3Rpb24iOiAzLCAidG9rZW5fbGltaXQiOiBudWxsLCAidG9rZW5fdHlwZSI6ICJhY2Nlc3MiLCAiZXhwIjogMTc4NDY5OTc3NywgImV4cGlyeV90aW1lIjogMTc4NDY5OTc3N326PvOdUXgQim4DiqZdwfu2MZYrisLZ0oRSqpicOlueg6Yl3zOhsjdKxps1FIfxAepSHfYMFWtS8hPn_cM2qksM",
                    "Content-Type": "application/json",
                }

                res = await client.get(
                    "https://cc1fbde45ead-in-south-01.mayson.dev/sigma/api/v1/sso/auth/google/login?collection_id=coll_a2ea7f17d37e4f23a3ae2df1a29c0d3f",
                    headers=headers,
                )

            res.raise_for_status()

            try:
                response_obj = dict(res.json())
                final_url = response_obj.get("value")
                return final_url
            except Exception as e:
                return f"https://mayson.dev/not-found?reason={str(e)}"

        return RedirectResponse(url=await google_login())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

    res = {
        "status": 200,
        "message": "The request has been successfully processed",
        "data": {"message": "success_response"},
    }
    return res


async def get_reviews_id(
    request: Request,
    db: Session,
    id: Union[int, float],
):

    query = db.query(models.Reviews)
    query = query.filter(and_(models.Reviews.id == id))

    reviews_one = query.first()

    reviews_one = (
        (
            reviews_one.to_dict()
            if hasattr(reviews_one, "to_dict")
            else vars(reviews_one)
        )
        if reviews_one
        else reviews_one
    )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"reviews_one": reviews_one},
    }
    return res


async def post_reviews(
    request: Request,
    db: Session,
    raw_data: schemas.PostReviews,
):
    order_id: Union[int, float] = raw_data.order_id
    reviewer_id: Union[int, float] = raw_data.reviewer_id
    reviewee_id: Union[int, float] = raw_data.reviewee_id
    rating: Union[int, float] = raw_data.rating
    comment: str = raw_data.comment
    created_at_dt: str = convert_to_datetime(raw_data.created_at_dt)

    record_to_be_added = {
        "rating": rating,
        "comment": comment,
        "order_id": order_id,
        "reviewee_id": reviewee_id,
        "reviewer_id": reviewer_id,
        "created_at_dt": created_at_dt,
    }
    new_reviews = models.Reviews(**record_to_be_added)
    db.add(new_reviews)
    db.commit()
    db.refresh(new_reviews)
    reviews_inserted_record = new_reviews.to_dict()

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"reviews_inserted_record": reviews_inserted_record},
    }
    return res


async def put_reviews_id(
    request: Request,
    db: Session,
    raw_data: schemas.PutReviewsId,
):
    id: str = raw_data.id
    order_id: Union[int, float] = raw_data.order_id
    reviewer_id: Union[int, float] = raw_data.reviewer_id
    reviewee_id: Union[int, float] = raw_data.reviewee_id
    rating: Union[int, float] = raw_data.rating
    comment: str = raw_data.comment
    created_at_dt: str = convert_to_datetime(raw_data.created_at_dt)

    query = db.query(models.Reviews)
    query = query.filter(and_(models.Reviews.id == id))
    reviews_edited_record = query.first()

    if reviews_edited_record:
        for key, value in {
            "id": id,
            "rating": rating,
            "comment": comment,
            "order_id": order_id,
            "reviewee_id": reviewee_id,
            "reviewer_id": reviewer_id,
            "created_at_dt": created_at_dt,
        }.items():
            setattr(reviews_edited_record, key, value)

        db.commit()

        db.refresh(reviews_edited_record)

        reviews_edited_record = (
            reviews_edited_record.to_dict()
            if hasattr(reviews_edited_record, "to_dict")
            else vars(reviews_edited_record)
        )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"reviews_edited_record": reviews_edited_record},
    }
    return res


async def delete_reviews_id(
    request: Request,
    db: Session,
    id: Union[int, float],
):

    query = db.query(models.Reviews)
    query = query.filter(and_(models.Reviews.id == id))

    record_to_delete = query.first()
    if record_to_delete:
        db.delete(record_to_delete)
        db.commit()
        reviews_deleted = record_to_delete.to_dict()
    else:
        reviews_deleted = record_to_delete

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"reviews_deleted": reviews_deleted},
    }
    return res


async def get_listings_id(
    request: Request,
    db: Session,
    id: Union[int, float],
):

    query = db.query(models.Listings)
    query = query.filter(and_(models.Listings.id == id))

    listings_one = query.first()

    listings_one = (
        (
            listings_one.to_dict()
            if hasattr(listings_one, "to_dict")
            else vars(listings_one)
        )
        if listings_one
        else listings_one
    )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"listings_one": listings_one},
    }
    return res


async def post_listings(
    request: Request,
    db: Session,
    raw_data: schemas.PostListings,
):
    seller_id: Union[int, float] = raw_data.seller_id
    title: str = raw_data.title
    description: str = raw_data.description
    price: float = raw_data.price
    category: str = raw_data.category
    item_condition: str = raw_data.item_condition
    images_json: str = raw_data.images_json
    status: str = raw_data.status
    views_count: Union[int, float] = raw_data.views_count
    created_at_dt: str = convert_to_datetime(raw_data.created_at_dt)
    updated_at_dt: str = convert_to_datetime(raw_data.updated_at_dt)

    record_to_be_added = {
        "price": price,
        "title": title,
        "status": status,
        "category": category,
        "seller_id": seller_id,
        "description": description,
        "images_json": images_json,
        "views_count": views_count,
        "created_at_dt": created_at_dt,
        "updated_at_dt": updated_at_dt,
        "item_condition": item_condition,
    }
    new_listings = models.Listings(**record_to_be_added)
    db.add(new_listings)
    db.commit()
    db.refresh(new_listings)
    listings_inserted_record = new_listings.to_dict()

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"listings_inserted_record": listings_inserted_record},
    }
    return res


async def put_listings_id(
    request: Request,
    db: Session,
    raw_data: schemas.PutListingsId,
):
    id: str = raw_data.id
    seller_id: Union[int, float] = raw_data.seller_id
    title: str = raw_data.title
    description: str = raw_data.description
    price: float = raw_data.price
    category: str = raw_data.category
    item_condition: str = raw_data.item_condition
    images_json: str = raw_data.images_json
    status: str = raw_data.status
    views_count: Union[int, float] = raw_data.views_count
    created_at_dt: str = convert_to_datetime(raw_data.created_at_dt)
    updated_at_dt: str = convert_to_datetime(raw_data.updated_at_dt)

    query = db.query(models.Listings)
    query = query.filter(and_(models.Listings.id == id))
    listings_edited_record = query.first()

    if listings_edited_record:
        for key, value in {
            "id": id,
            "price": price,
            "title": title,
            "status": status,
            "category": category,
            "seller_id": seller_id,
            "description": description,
            "images_json": images_json,
            "views_count": views_count,
            "created_at_dt": created_at_dt,
            "updated_at_dt": updated_at_dt,
            "item_condition": item_condition,
        }.items():
            setattr(listings_edited_record, key, value)

        db.commit()

        db.refresh(listings_edited_record)

        listings_edited_record = (
            listings_edited_record.to_dict()
            if hasattr(listings_edited_record, "to_dict")
            else vars(listings_edited_record)
        )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"listings_edited_record": listings_edited_record},
    }
    return res


async def delete_listings_id(
    request: Request,
    db: Session,
    id: Union[int, float],
):

    query = db.query(models.Listings)
    query = query.filter(and_(models.Listings.id == id))

    record_to_delete = query.first()
    if record_to_delete:
        db.delete(record_to_delete)
        db.commit()
        listings_deleted = record_to_delete.to_dict()
    else:
        listings_deleted = record_to_delete

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"listings_deleted": listings_deleted},
    }
    return res


async def get_users_id(
    request: Request,
    db: Session,
    id: Union[int, float],
):

    query = db.query(models.Users)
    query = query.filter(and_(models.Users.id == id))

    users_one = query.first()

    users_one = (
        (users_one.to_dict() if hasattr(users_one, "to_dict") else vars(users_one))
        if users_one
        else users_one
    )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"users_one": users_one},
    }
    return res


async def post_users(
    request: Request,
    db: Session,
    raw_data: schemas.PostUsers,
):
    email: str = raw_data.email
    password: str = raw_data.password
    created_at_dt: str = convert_to_datetime(raw_data.created_at_dt)

    record_to_be_added = {
        "email": email,
        "password": password,
        "created_at_dt": created_at_dt,
    }
    new_users = models.Users(**record_to_be_added)
    db.add(new_users)
    db.commit()
    db.refresh(new_users)
    users_inserted_record = new_users.to_dict()

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"users_inserted_record": users_inserted_record},
    }
    return res


async def put_users_id(
    request: Request,
    db: Session,
    raw_data: schemas.PutUsersId,
):
    id: str = raw_data.id
    email: str = raw_data.email
    password: str = raw_data.password
    created_at_dt: str = convert_to_datetime(raw_data.created_at_dt)

    query = db.query(models.Users)
    query = query.filter(and_(models.Users.id == id))
    users_edited_record = query.first()

    if users_edited_record:
        for key, value in {
            "id": id,
            "email": email,
            "password": password,
            "created_at_dt": created_at_dt,
        }.items():
            setattr(users_edited_record, key, value)

        db.commit()

        db.refresh(users_edited_record)

        users_edited_record = (
            users_edited_record.to_dict()
            if hasattr(users_edited_record, "to_dict")
            else vars(users_edited_record)
        )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"users_edited_record": users_edited_record},
    }
    return res


async def delete_users_id(
    request: Request,
    db: Session,
    id: Union[int, float],
):

    query = db.query(models.Users)
    query = query.filter(and_(models.Users.id == id))

    record_to_delete = query.first()
    if record_to_delete:
        db.delete(record_to_delete)
        db.commit()
        users_deleted = record_to_delete.to_dict()
    else:
        users_deleted = record_to_delete

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"users_deleted": users_deleted},
    }
    return res


async def get_messages_id(
    request: Request,
    db: Session,
    id: Union[int, float],
):

    query = db.query(models.Messages)
    query = query.filter(and_(models.Messages.id == id))

    messages_one = query.first()

    messages_one = (
        (
            messages_one.to_dict()
            if hasattr(messages_one, "to_dict")
            else vars(messages_one)
        )
        if messages_one
        else messages_one
    )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"messages_one": messages_one},
    }
    return res


async def post_messages(
    request: Request,
    db: Session,
    raw_data: schemas.PostMessages,
):
    listing_id: Union[int, float] = raw_data.listing_id
    sender_id: Union[int, float] = raw_data.sender_id
    receiver_id: Union[int, float] = raw_data.receiver_id
    body: str = raw_data.body
    offer_amount: float = raw_data.offer_amount
    offer_status: str = raw_data.offer_status
    created_at_dt: str = convert_to_datetime(raw_data.created_at_dt)

    record_to_be_added = {
        "body": body,
        "sender_id": sender_id,
        "listing_id": listing_id,
        "receiver_id": receiver_id,
        "offer_amount": offer_amount,
        "offer_status": offer_status,
        "created_at_dt": created_at_dt,
    }
    new_messages = models.Messages(**record_to_be_added)
    db.add(new_messages)
    db.commit()
    db.refresh(new_messages)
    messages_inserted_record = new_messages.to_dict()

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"messages_inserted_record": messages_inserted_record},
    }
    return res


async def put_messages_id(
    request: Request,
    db: Session,
    raw_data: schemas.PutMessagesId,
):
    id: str = raw_data.id
    listing_id: Union[int, float] = raw_data.listing_id
    sender_id: Union[int, float] = raw_data.sender_id
    receiver_id: Union[int, float] = raw_data.receiver_id
    body: str = raw_data.body
    offer_amount: float = raw_data.offer_amount
    offer_status: str = raw_data.offer_status
    created_at_dt: str = convert_to_datetime(raw_data.created_at_dt)

    query = db.query(models.Messages)
    query = query.filter(and_(models.Messages.id == id))
    messages_edited_record = query.first()

    if messages_edited_record:
        for key, value in {
            "id": id,
            "body": body,
            "sender_id": sender_id,
            "listing_id": listing_id,
            "receiver_id": receiver_id,
            "offer_amount": offer_amount,
            "offer_status": offer_status,
            "created_at_dt": created_at_dt,
        }.items():
            setattr(messages_edited_record, key, value)

        db.commit()

        db.refresh(messages_edited_record)

        messages_edited_record = (
            messages_edited_record.to_dict()
            if hasattr(messages_edited_record, "to_dict")
            else vars(messages_edited_record)
        )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"messages_edited_record": messages_edited_record},
    }
    return res


async def delete_messages_id(
    request: Request,
    db: Session,
    id: Union[int, float],
):

    query = db.query(models.Messages)
    query = query.filter(and_(models.Messages.id == id))

    record_to_delete = query.first()
    if record_to_delete:
        db.delete(record_to_delete)
        db.commit()
        messages_deleted = record_to_delete.to_dict()
    else:
        messages_deleted = record_to_delete

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"messages_deleted": messages_deleted},
    }
    return res


async def get_platform_auth_package_mayson_sso_auth_me(
    request: Request,
    db: Session,
):

    # get auth header

    try:
        auth_header = request.headers.get("authorization")
        auth_header = (
            auth_header[7:]
            if auth_header and auth_header.lower().startswith("bearer ")
            else auth_header
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

    import jwt

    try:
        user_profile = jwt.decode(
            auth_header,
            """vI0ddZJ-mrUJi9TYiV1rXQNMzX2EtmjCV_LJU1SEwl4=""",
            algorithms=["HS256"],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token.")

    # profile_data = user_profile["data"]

    try:
        profile_data = user_profile["data"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

    res = {
        "status": 200,
        "message": "The request has been successfully processed",
        "data": {"user_profile": profile_data},
    }
    return res


async def post_platform_auth_package_mayson_auth_user_register(
    request: Request,
    db: Session,
    raw_data: schemas.PostPlatformAuthPackageMaysonAuthUserRegister,
):
    email: str = raw_data.email
    password: str = raw_data.password

    query = db.query(models.Users)
    query = query.filter(and_(models.Users.email == email))

    existing_record = query.first()

    existing_record = (
        (
            existing_record.to_dict()
            if hasattr(existing_record, "to_dict")
            else vars(existing_record)
        )
        if existing_record
        else existing_record
    )

    if existing_record:

        raise HTTPException(status_code=400, detail="User already exists.")
    else:
        pass

    from passlib.hash import md5_crypt

    encrypt_pass = md5_crypt.hash(password)

    record_to_be_added = {"email": email, "password": encrypt_pass}
    new_users = models.Users(**record_to_be_added)
    db.add(new_users)
    db.commit()
    db.refresh(new_users)
    post_user_record = new_users.to_dict()

    res = {"status": 200, "message": "User registered successfully", "data": {}}
    return res
