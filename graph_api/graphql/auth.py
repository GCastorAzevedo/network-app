import strawberry
from strawberry.permission import BasePermission
from typing import Any


class IsAuthenticated(BasePermission):
    def has_permission(self, source: Any, info: strawberry.Info, **kwargs) -> bool:
        return True

    def get_nodes(self, source: Any, info: strawberry.Info, **kwargs) -> list[int]:
        nodes: list[int] = (
            info.context["nodes"] if info.context["nodes"] is not None else []
        )
        return nodes

    def get_user_id(self, source: Any, info: strawberry.Info):
        return info.context["user_id"]
