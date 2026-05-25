from enum import StrEnum


class UserRole(StrEnum):
    AUTHOR = "author"
    MODERATOR = "moderator"
    ADMIN = "admin"


class ModerationStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"
