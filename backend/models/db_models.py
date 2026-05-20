from datetime import datetime
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    String,
    Text,
    text as sa_text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TSVECTOR
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(AsyncAttrs, DeclarativeBase):
    pass

class Category(Base):
    __tablename__ = "categories"
    key: Mapped[str] = mapped_column(Text, primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    icon_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, server_default="0", default=0, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=sa_text("NOW()")
    )
    guides: Mapped[list["Guide"]] = relationship(
        "Guide", back_populates="category", cascade="all, delete-orphan"
    )

class Guide(Base):
    __tablename__ = "guides"
    key: Mapped[str] = mapped_column(Text, primary_key=True)
    category_key: Mapped[str] = mapped_column(
        Text, ForeignKey("categories.key", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    icon_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    text: Mapped[str] = mapped_column(Text, server_default="''", default="")
    photo: Mapped[list[str]] = mapped_column(ARRAY(Text), server_default="{}", default=list)
    video: Mapped[list[str]] = mapped_column(ARRAY(Text), server_default="{}", default=list)
    document: Mapped[list[str]] = mapped_column(ARRAY(Text), server_default="{}", default=list)
    sort_order: Mapped[int] = mapped_column(Integer, server_default="0", default=0, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=sa_text("NOW()"), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=sa_text("NOW()"), onupdate=sa_text("NOW()"), index=True
    )
    views: Mapped[int] = mapped_column(BigInteger, server_default="0", default=0, index=True)
    search_vec = mapped_column(TSVECTOR, nullable=True)
    category: Mapped["Category"] = relationship("Category", back_populates="guides")
    tags: Mapped[list["GuideTag"]] = relationship(
        "GuideTag", back_populates="guide", cascade="all, delete-orphan"
    )
    comments: Mapped[list["GuideComment"]] = relationship(
        "GuideComment", back_populates="guide", cascade="all, delete-orphan"
    )

class GuideTag(Base):
    __tablename__ = "guide_tags"
    guide_key: Mapped[str] = mapped_column(
        Text, ForeignKey("guides.key", ondelete="CASCADE"), primary_key=True
    )
    tag: Mapped[str] = mapped_column(Text, primary_key=True)
    guide: Mapped["Guide"] = relationship("Guide", back_populates="tags")

class GuideHistory(Base):
    __tablename__ = "guide_history"
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    guide_key: Mapped[str] = mapped_column(Text, nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    changed_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=sa_text("NOW()")
    )
    snapshot = mapped_column(JSONB, nullable=True)

class GuideComment(Base):
    __tablename__ = "guide_comments"
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    guide_key: Mapped[str] = mapped_column(
        Text, ForeignKey("guides.key", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    username: Mapped[str | None] = mapped_column(Text, nullable=True)
    first_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=sa_text("NOW()")
    )
    guide: Mapped["Guide"] = relationship("Guide", back_populates="comments")

class UserSubscription(Base):
    __tablename__ = "user_subscriptions"
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    category_key: Mapped[str] = mapped_column(
        Text, ForeignKey("categories.key", ondelete="CASCADE"), primary_key=True
    )

class Member(Base):
    __tablename__ = "members"
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(Text, nullable=True)
    first_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    role: Mapped[str] = mapped_column(Text, server_default="'member'", default="member")
    added_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=sa_text("NOW()")
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default="true", default=True
    )

class LocalAdmin(Base):
    __tablename__ = "local_admins"
    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=sa_text("NOW()")
    )

class ViewLog(Base):
    __tablename__ = "view_logs"
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    guide_key: Mapped[str] = mapped_column(
        Text, ForeignKey("guides.key", ondelete="CASCADE"), nullable=False
    )
    viewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=sa_text("NOW()")
    )
