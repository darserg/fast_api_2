from fastapi import HTTPException, status

from src.core.enums import UserRole
from src.repositories.users import UserRepository
from src.schemas.users import UserRoleUpdate, UserUpdate
from src.services.audit import AuditService


class UserService:
    def __init__(self, user_repo: UserRepository, audit_service: AuditService) -> None:
        self.user_repo = user_repo
        self.audit_service = audit_service

    async def list_users(self):
        return await self.user_repo.get_all()

    async def get_user(self, user_id: str):
        user = await self.user_repo.get(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def get_by_username(self, username: str):
        user = await self.user_repo.get_by_username(username)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def update_user(self, user_id: str, payload: UserUpdate, current_user) -> object:
        user = await self.get_user(user_id)
        self._require_owner_or_admin(user.id, current_user)
        updated = await self.user_repo.update(user, payload.model_dump(exclude_unset=True))
        await self.audit_service.log(
            actor_id=current_user.id,
            action="user.update",
            entity_type="user",
            entity_id=user.id,
            after_state=payload.model_dump(exclude_unset=True),
        )
        return updated

    async def update_role(self, user_id: str, payload: UserRoleUpdate, current_user):
        self._require_admin(current_user)
        user = await self.get_user(user_id)
        update_data = {"role": payload.role.value}
        if payload.is_active is not None:
            update_data["is_active"] = payload.is_active
        updated = await self.user_repo.update(user, update_data)
        await self.audit_service.log(
            actor_id=current_user.id,
            action="user.role_update",
            entity_type="user",
            entity_id=user.id,
            after_state=update_data,
        )
        return updated

    async def delete_user(self, user_id: str, current_user) -> None:
        user = await self.get_user(user_id)
        self._require_owner_or_admin(user.id, current_user)
        await self.user_repo.delete(user)
        await self.audit_service.log(
            actor_id=current_user.id,
            action="user.delete",
            entity_type="user",
            entity_id=user.id,
        )

    @staticmethod
    def _require_owner_or_admin(owner_id: str, current_user) -> None:
        if owner_id == current_user.id:
            return
        if current_user.role == UserRole.ADMIN:
            return
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    @staticmethod
    def _require_admin(current_user) -> None:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permissions required",
            )

    @staticmethod
    def require_staff(current_user) -> None:
        if current_user.role not in {UserRole.MODERATOR, UserRole.ADMIN}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Staff permissions required",
            )
