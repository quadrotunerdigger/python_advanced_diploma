"""Экспорт всех Pydantic схем."""

from app.schemas.base import (
    BaseSchema,
    SuccessResponse,
    ErrorResponse,
    TweetIdResponse,
    MediaIdResponse,
)
from app.schemas.user import (
    UserBase,
    UserShort,
    UserProfile,
    UserProfileResponse,
)
from app.schemas.tweet import (
    TweetCreate,
    TweetAuthor,
    TweetResponse,
    TweetFeedResponse,
)
from app.schemas.media import (
    MediaResponse,
    MediaUploadResponse,
)

__all__ = [
    # Base
    "BaseSchema",
    "SuccessResponse",
    "ErrorResponse",
    "TweetIdResponse",
    "MediaIdResponse",
    # User
    "UserBase",
    "UserShort",
    "UserProfile",
    "UserProfileResponse",
    # Tweet
    "TweetCreate",
    "TweetAuthor",
    "TweetResponse",
    "TweetFeedResponse",
    # Media
    "MediaResponse",
    "MediaUploadResponse",
]