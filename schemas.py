from pydantic import BaseModel,Field,field_validator

import datetime

import uuid

from typing import Any, Dict, List,Optional,Tuple,Union

import re

class Listings(BaseModel):
    seller_id: Optional[Union[int, float]]=None
    title: str
    description: Optional[str]=None
    price: float
    category: Optional[str]=None
    item_condition: Optional[str]=None
    images_json: Optional[str]=None
    status: Optional[str]=None
    views_count: Optional[Union[int, float]]=None
    created_at_dt: Optional[Any]=None
    updated_at_dt: Optional[Any]=None


class ReadListings(BaseModel):
    seller_id: Optional[Union[int, float]]=None
    title: str
    description: Optional[str]=None
    price: float
    category: Optional[str]=None
    item_condition: Optional[str]=None
    images_json: Optional[str]=None
    status: Optional[str]=None
    views_count: Optional[Union[int, float]]=None
    created_at_dt: Optional[Any]=None
    updated_at_dt: Optional[Any]=None
    class Config:
        from_attributes = True


class Messages(BaseModel):
    listing_id: Optional[Union[int, float]]=None
    sender_id: Optional[Union[int, float]]=None
    receiver_id: Optional[Union[int, float]]=None
    body: str
    offer_amount: Optional[float]=None
    offer_status: Optional[str]=None
    created_at_dt: Optional[Any]=None


class ReadMessages(BaseModel):
    listing_id: Optional[Union[int, float]]=None
    sender_id: Optional[Union[int, float]]=None
    receiver_id: Optional[Union[int, float]]=None
    body: str
    offer_amount: Optional[float]=None
    offer_status: Optional[str]=None
    created_at_dt: Optional[Any]=None
    class Config:
        from_attributes = True


class Orders(BaseModel):
    listing_id: Optional[Union[int, float]]=None
    buyer_id: Optional[Union[int, float]]=None
    seller_id: Optional[Union[int, float]]=None
    final_price: float
    status: Optional[str]=None
    created_at_dt: Optional[Any]=None
    updated_at_dt: Optional[Any]=None


class ReadOrders(BaseModel):
    listing_id: Optional[Union[int, float]]=None
    buyer_id: Optional[Union[int, float]]=None
    seller_id: Optional[Union[int, float]]=None
    final_price: float
    status: Optional[str]=None
    created_at_dt: Optional[Any]=None
    updated_at_dt: Optional[Any]=None
    class Config:
        from_attributes = True


class Profiles(BaseModel):
    users_id: Optional[Union[int, float]]=None
    full_name: Optional[str]=None
    avatar_url: Optional[str]=None
    location: Optional[str]=None
    bio: Optional[str]=None
    rating_avg: Optional[float]=None
    created_at_dt: Optional[Any]=None
    updated_at_dt: Optional[Any]=None


class ReadProfiles(BaseModel):
    users_id: Optional[Union[int, float]]=None
    full_name: Optional[str]=None
    avatar_url: Optional[str]=None
    location: Optional[str]=None
    bio: Optional[str]=None
    rating_avg: Optional[float]=None
    created_at_dt: Optional[Any]=None
    updated_at_dt: Optional[Any]=None
    class Config:
        from_attributes = True


class Reviews(BaseModel):
    order_id: Optional[Union[int, float]]=None
    reviewer_id: Optional[Union[int, float]]=None
    reviewee_id: Optional[Union[int, float]]=None
    rating: int
    comment: Optional[str]=None
    created_at_dt: Optional[Any]=None


class ReadReviews(BaseModel):
    order_id: Optional[Union[int, float]]=None
    reviewer_id: Optional[Union[int, float]]=None
    reviewee_id: Optional[Union[int, float]]=None
    rating: int
    comment: Optional[str]=None
    created_at_dt: Optional[Any]=None
    class Config:
        from_attributes = True


class Users(BaseModel):
    email: str
    password: str
    created_at_dt: Optional[Any]=None


class ReadUsers(BaseModel):
    email: str
    password: str
    created_at_dt: Optional[Any]=None
    class Config:
        from_attributes = True


class Watchlist(BaseModel):
    users_id: Optional[Union[int, float]]=None
    listing_id: Optional[Union[int, float]]=None
    created_at_dt: Optional[Any]=None


class ReadWatchlist(BaseModel):
    users_id: Optional[Union[int, float]]=None
    listing_id: Optional[Union[int, float]]=None
    created_at_dt: Optional[Any]=None
    class Config:
        from_attributes = True




class PostPlatformAuthPackageMaysonAuthUserLogin(BaseModel):
    email: str = Field(..., max_length=100)
    password: str = Field(..., max_length=100)

    class Config:
        from_attributes = True



class PostOrders(BaseModel):
    listing_id: Optional[int]=None
    buyer_id: Optional[int]=None
    seller_id: Optional[int]=None
    final_price: Any = Field(...)
    status: Optional[str]=None
    created_at_dt: Optional[str]=None
    updated_at_dt: Optional[str]=None

    class Config:
        from_attributes = True



class PutOrdersId(BaseModel):
    id: str = Field(..., max_length=100)
    listing_id: Optional[int]=None
    buyer_id: Optional[int]=None
    seller_id: Optional[int]=None
    final_price: Any = Field(...)
    status: Optional[str]=None
    created_at_dt: Optional[str]=None
    updated_at_dt: Optional[str]=None

    class Config:
        from_attributes = True



class PostProfiles(BaseModel):
    users_id: Optional[int]=None
    full_name: Optional[str]=None
    avatar_url: Optional[str]=None
    location: Optional[str]=None
    bio: Optional[str]=None
    rating_avg: Optional[Any]=None
    created_at_dt: Optional[str]=None
    updated_at_dt: Optional[str]=None

    class Config:
        from_attributes = True



class PutProfilesId(BaseModel):
    id: str = Field(..., max_length=100)
    users_id: Optional[int]=None
    full_name: Optional[str]=None
    avatar_url: Optional[str]=None
    location: Optional[str]=None
    bio: Optional[str]=None
    rating_avg: Optional[Any]=None
    created_at_dt: Optional[str]=None
    updated_at_dt: Optional[str]=None

    class Config:
        from_attributes = True



class PostWatchlist(BaseModel):
    users_id: Optional[int]=None
    listing_id: Optional[int]=None
    created_at_dt: Optional[str]=None

    class Config:
        from_attributes = True



class PutWatchlistId(BaseModel):
    id: str = Field(..., max_length=100)
    users_id: Optional[int]=None
    listing_id: Optional[int]=None
    created_at_dt: Optional[str]=None

    class Config:
        from_attributes = True



class PostReviews(BaseModel):
    order_id: Optional[int]=None
    reviewer_id: Optional[int]=None
    reviewee_id: Optional[int]=None
    rating: int = Field(...)
    comment: Optional[str]=None
    created_at_dt: Optional[str]=None

    class Config:
        from_attributes = True



class PutReviewsId(BaseModel):
    id: str = Field(..., max_length=100)
    order_id: Optional[int]=None
    reviewer_id: Optional[int]=None
    reviewee_id: Optional[int]=None
    rating: int = Field(...)
    comment: Optional[str]=None
    created_at_dt: Optional[str]=None

    class Config:
        from_attributes = True



class PostListings(BaseModel):
    seller_id: Optional[int]=None
    title: str = Field(..., max_length=255)
    description: Optional[str]=None
    price: Any = Field(...)
    category: Optional[str]=None
    item_condition: Optional[str]=None
    images_json: Optional[str]=None
    status: Optional[str]=None
    views_count: Optional[int]=None
    created_at_dt: Optional[str]=None
    updated_at_dt: Optional[str]=None

    class Config:
        from_attributes = True



class PutListingsId(BaseModel):
    id: str = Field(..., max_length=100)
    seller_id: Optional[int]=None
    title: str = Field(..., max_length=255)
    description: Optional[str]=None
    price: Any = Field(...)
    category: Optional[str]=None
    item_condition: Optional[str]=None
    images_json: Optional[str]=None
    status: Optional[str]=None
    views_count: Optional[int]=None
    created_at_dt: Optional[str]=None
    updated_at_dt: Optional[str]=None

    class Config:
        from_attributes = True



class PostUsers(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., max_length=255)
    created_at_dt: Optional[str]=None

    class Config:
        from_attributes = True



class PutUsersId(BaseModel):
    id: str = Field(..., max_length=100)
    email: str = Field(..., max_length=255)
    password: str = Field(..., max_length=255)
    created_at_dt: Optional[str]=None

    class Config:
        from_attributes = True



class PostMessages(BaseModel):
    listing_id: Optional[Union[int, float]]=None
    sender_id: Optional[Union[int, float]]=None
    receiver_id: Optional[Union[int, float]]=None
    body: str = Field(..., max_length=100)
    offer_amount: Optional[Any]=None
    offer_status: Optional[str]=None
    created_at_dt: Optional[str]=None

    class Config:
        from_attributes = True



class PutMessagesId(BaseModel):
    id: str = Field(..., max_length=100)
    listing_id: Optional[Union[int, float]]=None
    sender_id: Optional[Union[int, float]]=None
    receiver_id: Optional[Union[int, float]]=None
    body: str = Field(..., max_length=100)
    offer_amount: Optional[Any]=None
    offer_status: Optional[str]=None
    created_at_dt: Optional[str]=None

    class Config:
        from_attributes = True



class PostPlatformAuthPackageMaysonAuthUserRegister(BaseModel):
    email: str = Field(..., max_length=100)
    password: str = Field(..., max_length=100)

    class Config:
        from_attributes = True



# Query Parameter Validation Schemas

class GetOrdersIdQueryParams(BaseModel):
    """Query parameter validation for get_orders_id"""
    id: int = Field(..., ge=1, description="Id")

    class Config:
        populate_by_name = True


class DeleteOrdersIdQueryParams(BaseModel):
    """Query parameter validation for delete_orders_id"""
    id: int = Field(..., ge=1, description="Id")

    class Config:
        populate_by_name = True


class GetProfilesIdQueryParams(BaseModel):
    """Query parameter validation for get_profiles_id"""
    id: int = Field(..., ge=1, description="Id")

    class Config:
        populate_by_name = True


class DeleteProfilesIdQueryParams(BaseModel):
    """Query parameter validation for delete_profiles_id"""
    id: int = Field(..., ge=1, description="Id")

    class Config:
        populate_by_name = True


class GetWatchlistIdQueryParams(BaseModel):
    """Query parameter validation for get_watchlist_id"""
    id: int = Field(..., ge=1, description="Id")

    class Config:
        populate_by_name = True


class DeleteWatchlistIdQueryParams(BaseModel):
    """Query parameter validation for delete_watchlist_id"""
    id: int = Field(..., ge=1, description="Id")

    class Config:
        populate_by_name = True


class GetReviewsIdQueryParams(BaseModel):
    """Query parameter validation for get_reviews_id"""
    id: int = Field(..., ge=1, description="Id")

    class Config:
        populate_by_name = True


class DeleteReviewsIdQueryParams(BaseModel):
    """Query parameter validation for delete_reviews_id"""
    id: int = Field(..., ge=1, description="Id")

    class Config:
        populate_by_name = True


class GetListingsIdQueryParams(BaseModel):
    """Query parameter validation for get_listings_id"""
    id: int = Field(..., ge=1, description="Id")

    class Config:
        populate_by_name = True


class DeleteListingsIdQueryParams(BaseModel):
    """Query parameter validation for delete_listings_id"""
    id: int = Field(..., ge=1, description="Id")

    class Config:
        populate_by_name = True


class GetUsersIdQueryParams(BaseModel):
    """Query parameter validation for get_users_id"""
    id: int = Field(..., ge=1, description="Id")

    class Config:
        populate_by_name = True


class DeleteUsersIdQueryParams(BaseModel):
    """Query parameter validation for delete_users_id"""
    id: int = Field(..., ge=1, description="Id")

    class Config:
        populate_by_name = True


class GetMessagesIdQueryParams(BaseModel):
    """Query parameter validation for get_messages_id"""
    id: int = Field(..., ge=1, description="Id")

    class Config:
        populate_by_name = True


class DeleteMessagesIdQueryParams(BaseModel):
    """Query parameter validation for delete_messages_id"""
    id: int = Field(..., ge=1, description="Id")

    class Config:
        populate_by_name = True
