import re

import nh3
from fastapi import HTTPException
from pydantic import BaseModel, field_validator

_KEY_RE = re.compile(r"^[a-z0-9_-]{1,64}$")


def _validate_key(v: str) -> str:
    if not _KEY_RE.match(v):
        raise HTTPException(
            status_code=422,
            detail="Ключ должен содержать только строчные буквы, цифры, _ и - (до 64 символов)",
        )
    return v


class PreviewIn(BaseModel):
    text: str = ""


class CategoryIn(BaseModel):
    title: str
    icon_url: str | None = None
    sort_order: int = 0

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError("Название не может быть пустым")
        return v.strip()


class GuideIn(BaseModel):
    category_key: str
    title: str
    icon_url: str | None = None
    text: str = ""
    photo: list[str] = []
    video: list[str] = []
    document: list[str] = []
    sort_order: int = 0

    @field_validator("category_key")
    @classmethod
    def validate_category_key(cls, v):
        return _validate_key(v)

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError("Название не может быть пустым")
        return v.strip()

    @field_validator("photo", "video", "document", mode="before")
    @classmethod
    def validate_urls(cls, v):
        if not isinstance(v, list):
            return v
        for url in v:
            if url and not url.startswith(("https://", "http://")):
                raise ValueError(f"Только http/https URL: {url!r}")
        return v

    @field_validator("icon_url", mode="before")
    @classmethod
    def validate_icon_url(cls, v):
        if v and not v.startswith(("https://", "http://")):
            raise ValueError("icon_url должен быть http/https URL")
        return v


class ReorderItem(BaseModel):
    key: str
    sort_order: int


class ReorderIn(BaseModel):
    order: list[ReorderItem]


class CommentIn(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def validate_text(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Комментарий не может быть пустым")
        if len(v) > 1000:
            raise ValueError("Комментарий слишком длинный (макс. 1000 символов)")
        return nh3.clean(v, tags=set())


class TagsIn(BaseModel):
    tags: list[str]


class NotifyIn(BaseModel):
    guide_key: str
    guide_title: str
    category_key: str
    bot_token: str


class ImportMediaIn(BaseModel):
    url: str
    folder: str = "imported"
