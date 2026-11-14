from fastapi import APIRouter

# Register all ORM classes before the first query so cross-module relationships
# (for example User.orders) can be resolved by SQLAlchemy.
import wapang.app.auth.models
import wapang.app.items.models
import wapang.app.orders.models
import wapang.app.stores.models
import wapang.app.users.models

from wapang.app.auth.router import auth_router
from wapang.app.items.router import item_router
from wapang.app.users.router import user_router


api_router = APIRouter()

api_router.include_router(user_router, prefix="/users", tags=["users"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(item_router, prefix="/items", tags=["items"])
