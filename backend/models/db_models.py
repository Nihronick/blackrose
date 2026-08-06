from datetime import datetime
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Identity,
    Index,
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


class Guild(Base):
    __tablename__ = "guilds"
    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    icon_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    max_members: Mapped[int] = mapped_column(Integer, server_default="20", default=20)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=sa_text("NOW()")
    )
    members: Mapped[list["GuildMember"]] = relationship(
        "GuildMember", back_populates="guild", cascade="all, delete-orphan"
    )
    custom_statuses: Mapped[list["GuildStatus"]] = relationship(
        "GuildStatus", back_populates="guild", cascade="all, delete-orphan"
    )


class GuildMember(Base):
    __tablename__ = "guild_members"
    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    guild_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("guilds.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True, index=True)
    nickname: Mapped[str] = mapped_column(Text, nullable=False)
    rank: Mapped[int] = mapped_column(Integer, server_default="1", default=1)
    rank_confirmed: Mapped[bool] = mapped_column(Boolean, server_default="false", default=False)
    stage: Mapped[int] = mapped_column(Integer, server_default="0", default=0)
    guild_role: Mapped[str] = mapped_column(
        Text, server_default="'guild_member'", default="guild_member"
    )
    status: Mapped[str] = mapped_column(
        Text, server_default="'active'", default="active"
    )
    status_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved: Mapped[bool] = mapped_column(Boolean, server_default="false", default=False)
    approved_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=sa_text("NOW()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=sa_text("NOW()"), onupdate=sa_text("NOW()")
    )
    guild: Mapped["Guild"] = relationship("Guild", back_populates="members")

    __table_args__ = (
        Index("ix_guild_members_guild_rank", "guild_id", "rank"),
    )


class GuildJoinRequest(Base):
    __tablename__ = "guild_join_requests"
    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    guild_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("guilds.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    nickname: Mapped[str] = mapped_column(Text, nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        Text, server_default="'pending'", default="pending"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=sa_text("NOW()")
    )
    resolved_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class GuildStatus(Base):
    __tablename__ = "guild_statuses"
    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    guild_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("guilds.id", ondelete="CASCADE"), nullable=False
    )
    key: Mapped[str] = mapped_column(Text, nullable=False)
    label: Mapped[str] = mapped_column(Text, nullable=False)
    color: Mapped[str] = mapped_column(Text, server_default="'gray'", default="gray")
    sort_order: Mapped[int] = mapped_column(Integer, server_default="0", default=0)
    guild: Mapped["Guild"] = relationship("Guild", back_populates="custom_statuses")

    __table_args__ = (
        Index("ix_guild_statuses_guild_key", "guild_id", "key", unique=True),
    )


class DiscordSyncChannel(Base):
    __tablename__ = "discord_sync_channels"
    channel_id: Mapped[str] = mapped_column(Text, primary_key=True)
    channel_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_key: Mapped[str] = mapped_column(Text, nullable=False)
    auto_translate: Mapped[bool] = mapped_column(Boolean, server_default="true", default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=sa_text("NOW()")
    )


class DiscordSyncedGuide(Base):
    __tablename__ = "discord_synced_guides"
    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    discord_message_id: Mapped[str] = mapped_column(Text, unique=True, nullable=False, index=True)
    discord_channel_id: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    guide_key: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(Text, nullable=False)
    author_tag: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=sa_text("NOW()"), onupdate=sa_text("NOW()")
    )

