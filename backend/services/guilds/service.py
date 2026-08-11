from sqlalchemy import select, func
from core.db import get_sessionmaker
from models.db_models import Guild, GuildMember, GuildJoinRequest, GuildStatus
from core.logging import get_logger
from datetime import datetime, timezone

logger = get_logger("blackrose.services.guilds")

class GuildService:
    async def get_all_guilds(self):
        try:
            async with get_sessionmaker()() as session:
                result = await session.execute(select(Guild).order_by(Guild.name))
                guilds = result.scalars().all()
                
                counts_res = await session.execute(
                    select(GuildMember.guild_id, func.count(GuildMember.id))
                    .group_by(GuildMember.guild_id)
                )
                counts = {row[0]: row[1] for row in counts_res.all()}
                
                res = []
                for g in guilds:
                    res.append({
                        "id": g.id,
                        "name": g.name,
                        "icon_url": g.icon_url,
                        "description": g.description,
                        "max_members": g.max_members,
                        "is_active": g.is_active,
                        "member_count": counts.get(g.id, 0)
                    })
                return res
        except Exception as e:
            logger.error(f"Error in get_all_guilds: {e}")
            return []
            
    async def get_guild_roster(self, guild_id: int):
        async with get_sessionmaker()() as session:
            g = await session.get(Guild, guild_id)
            if not g:
                return None
                
            res = await session.execute(
                select(GuildMember)
                .where(GuildMember.guild_id == guild_id)
                .order_by(GuildMember.rank.desc())
                .limit(100)
            )
            members = res.scalars().all()
            
            # Auto-seed sample roster if guild has 0 members
            if not members and g.id == 1:
                sample_members = [
                    GuildMember(guild_id=1, user_id=1001, nickname="Bannibal", rank=21, stage=1750, guild_role="guild_master", status="active", approved=True),
                    GuildMember(guild_id=1, user_id=1002, nickname="Ellie", rank=20, stage=1620, guild_role="guild_vice_master", status="active", approved=True),
                    GuildMember(guild_id=1, user_id=1003, nickname="Zeke", rank=19, stage=1580, guild_role="guild_member", status="active", approved=True),
                    GuildMember(guild_id=1, user_id=1004, nickname="Kael", rank=18, stage=1500, guild_role="guild_member", status="active", approved=True),
                    GuildMember(guild_id=1, user_id=1005, nickname="Aria", rank=17, stage=1420, guild_role="guild_member", status="active", approved=True),
                    GuildMember(guild_id=1, user_id=1006, nickname="Dante", rank=16, stage=1350, guild_role="guild_member", status="active", approved=True),
                    GuildMember(guild_id=1, user_id=1007, nickname="Vesper", rank=15, stage=1290, guild_role="guild_member", status="trial", approved=True),
                ]
                session.add_all(sample_members)
                await session.commit()
                
                res = await session.execute(
                    select(GuildMember)
                    .where(GuildMember.guild_id == guild_id)
                    .order_by(GuildMember.rank.desc())
                )
                members = res.scalars().all()

            total_ranks = sum(m.rank for m in members)
            member_count = len(members)
            average_rank = total_ranks / member_count if member_count > 0 else 0
            
            return {
                "guild": {
                    "id": g.id,
                    "name": g.name,
                    "icon_url": g.icon_url,
                    "description": g.description
                },
                "stats": {
                    "total_ranks": total_ranks,
                    "average_rank": round(average_rank, 2),
                    "member_count": member_count
                },
                "members": [
                    {
                        "id": m.id,
                        "user_id": m.user_id,
                        "nickname": m.nickname,
                        "rank": m.rank,
                        "rank_confirmed": m.rank_confirmed,
                        "stage": m.stage,
                        "guild_role": m.guild_role,
                        "status": m.status,
                        "status_note": m.status_note,
                        "approved": m.approved
                    }
                    for m in members
                ]
            }

    async def get_my_profile(self, user_id: int):
        async with get_sessionmaker()() as session:
            res = await session.execute(
                select(GuildMember).where(GuildMember.user_id == user_id)
            )
            m = res.scalar_one_or_none()
            if not m:
                return None
            return {
                "id": m.id,
                "guild_id": m.guild_id,
                "nickname": m.nickname,
                "rank": m.rank,
                "stage": m.stage,
                "guild_role": m.guild_role,
                "status": m.status,
                "status_note": m.status_note,
                "approved": m.approved
            }

    async def update_my_profile(self, user_id: int, nickname: str, stage: int):
        async with get_sessionmaker()() as session:
            res = await session.execute(
                select(GuildMember).where(GuildMember.user_id == user_id)
            )
            m = res.scalar_one_or_none()
            if not m:
                return False
            m.nickname = nickname
            m.stage = stage
            await session.commit()
            return True

    async def create_join_request(self, user_id: int, guild_id: int, nickname: str, message: str | None):
        async with get_sessionmaker()() as session:
            in_guild = await session.execute(select(GuildMember).where(GuildMember.user_id == user_id))
            if in_guild.scalar_one_or_none():
                return {"error": "Уже состоите в гильдии"}
                
            pending = await session.execute(
                select(GuildJoinRequest).where(
                    GuildJoinRequest.user_id == user_id, 
                    GuildJoinRequest.status == 'pending'
                )
            )
            if pending.scalar_one_or_none():
                return {"error": "Уже есть активная заявка"}
                
            guild = await session.get(Guild, guild_id)
            if not guild:
                return {"error": "Гильдия не найдена"}
                
            count_res = await session.execute(
                select(func.count(GuildMember.id)).where(GuildMember.guild_id == guild_id)
            )
            if count_res.scalar() >= guild.max_members:
                return {"error": "Гильдия переполнена"}
                
            req = GuildJoinRequest(
                guild_id=guild_id,
                user_id=user_id,
                nickname=nickname,
                message=message
            )
            session.add(req)
            await session.commit()
            return {"id": req.id}

    async def approve_request(self, request_id: int, approver_id: int):
        async with get_sessionmaker()() as session:
            req = await session.get(GuildJoinRequest, request_id)
            if not req or req.status != 'pending':
                return {"error": "Заявка не найдена или уже обработана"}
                
            guild = await session.get(Guild, req.guild_id)
            count_res = await session.execute(
                select(func.count(GuildMember.id)).where(GuildMember.guild_id == req.guild_id)
            )
            if count_res.scalar() >= guild.max_members:
                return {"error": "Гильдия переполнена"}
                
            req.status = 'approved'
            req.resolved_by = approver_id
            req.resolved_at = datetime.now(timezone.utc)
            
            member = GuildMember(
                guild_id=req.guild_id,
                user_id=req.user_id,
                nickname=req.nickname,
                approved=True,
                approved_by=approver_id
            )
            session.add(member)
            await session.commit()
            
            # Send Telegram Notification
            from services.notifications.service import notification_service
            await notification_service.notify_request_approved(req.user_id, guild.name)
            return {"ok": True}

    async def reject_request(self, request_id: int, approver_id: int):
        async with get_sessionmaker()() as session:
            req = await session.get(GuildJoinRequest, request_id)
            if not req or req.status != 'pending':
                return {"error": "Заявка не найдена или уже обработана"}
                
            guild = await session.get(Guild, req.guild_id)
            guild_name = guild.name if guild else "гильдию"

            req.status = 'rejected'
            req.resolved_by = approver_id
            req.resolved_at = datetime.now(timezone.utc)
            await session.commit()

            # Send Telegram Notification
            from services.notifications.service import notification_service
            await notification_service.notify_request_rejected(req.user_id, guild_name)
            return {"ok": True}

    async def update_member(self, member_id: int, data, updater_id: int):
        async with get_sessionmaker()() as session:
            member = await session.get(GuildMember, member_id)
            if not member:
                return {"error": "Участник не найден"}
                
            can_manage = await self.can_manage_guild(updater_id, member.guild_id)
            if not can_manage:
                return {"error": "Нет прав"}

            dumped = data.model_dump(exclude_unset=True)
            old_rank = member.rank

            for k, v in dumped.items():
                setattr(member, k, v)
                
            await session.commit()

            # Notify if rank changed
            if "rank" in dumped and dumped["rank"] != old_rank:
                guild = await session.get(Guild, member.guild_id)
                guild_name = guild.name if guild else "гильдии"
                rank_num = dumped["rank"]
                
                # Rank name helper
                rank_names = {
                    1: 'Stone', 2: 'Bronze', 3: 'Iron', 4: 'Silver', 5: 'Eisenhart',
                    6: 'Eldenwood', 7: 'Adamant', 8: 'Orichalcum', 9: 'Blue Abyss',
                    10: 'Warfrost', 11: 'Diadust', 12: 'Black Mythril', 13: 'Dark Nox',
                    14: 'Demon Metal', 15: 'Ancient Canine', 16: 'Gigarock', 17: 'Cyclos',
                    18: 'Dragonos', 19: 'Ragnablood', 20: 'Ether', 21: 'Infinaut'
                }
                rank_name = rank_names.get(rank_num, f"Rank {rank_num}")

                from services.notifications.service import notification_service
                await notification_service.notify_rank_updated(
                    user_id=member.user_id,
                    guild_name=guild_name,
                    new_rank=rank_num,
                    rank_name=rank_name
                )

            return {"ok": True}

    async def remove_member(self, member_id: int, remover_id: int):
        async with get_sessionmaker()() as session:
            member = await session.get(GuildMember, member_id)
            if not member:
                return {"error": "Участник не найден"}
                
            can_manage = await self.can_manage_guild(remover_id, member.guild_id)
            if not can_manage and remover_id != member.user_id:
                return {"error": "Нет прав"}
                
            await session.delete(member)
            await session.commit()
            return {"ok": True}

    async def create_guild(self, name: str, icon_url: str | None, description: str | None, max_members: int):
        async with get_sessionmaker()() as session:
            g = Guild(
                name=name,
                icon_url=icon_url,
                description=description,
                max_members=max_members
            )
            session.add(g)
            await session.commit()
            return {"id": g.id}

    async def update_guild(self, guild_id: int, data):
        async with get_sessionmaker()() as session:
            g = await session.get(Guild, guild_id)
            if not g:
                return False
            for k, v in data.model_dump(exclude_unset=True).items():
                setattr(g, k, v)
            await session.commit()
            return True

    async def delete_guild(self, guild_id: int):
        async with get_sessionmaker()() as session:
            g = await session.get(Guild, guild_id)
            if not g:
                return False
            await session.delete(g)
            await session.commit()
            return True

    async def get_pending_requests(self, guild_id: int = None):
        async with get_sessionmaker()() as session:
            q = select(GuildJoinRequest).where(GuildJoinRequest.status == 'pending')
            if guild_id:
                q = q.where(GuildJoinRequest.guild_id == guild_id)
            res = await session.execute(q)
            reqs = res.scalars().all()
            return [
                {
                    "id": r.id,
                    "user_id": r.user_id,
                    "nickname": r.nickname,
                    "message": r.message,
                    "created_at": r.created_at
                }
                for r in reqs
            ]

    async def add_custom_status(self, guild_id: int, key: str, label: str, color: str):
        async with get_sessionmaker()() as session:
            st = GuildStatus(guild_id=guild_id, key=key, label=label, color=color)
            session.add(st)
            await session.commit()
            return {"id": st.id}

    async def remove_custom_status(self, status_id: int):
        async with get_sessionmaker()() as session:
            st = await session.get(GuildStatus, status_id)
            if st:
                await session.delete(st)
                await session.commit()
            return True

    async def get_guild_statuses(self, guild_id: int):
        async with get_sessionmaker()() as session:
            res = await session.execute(
                select(GuildStatus).where(GuildStatus.guild_id == guild_id)
            )
            sts = res.scalars().all()
            base = [
                {"key": "active", "label": "Активен", "color": "green"},
                {"key": "inactive", "label": "Неактивен", "color": "gray"},
            ]
            custom = [{"id": s.id, "key": s.key, "label": s.label, "color": s.color} for s in sts]
            return base + custom

    async def can_manage_guild(self, user_id: int, guild_id: int) -> bool:
        from services.common.members import member_service
        if await member_service.is_admin(user_id):
            return True
            
        async with get_sessionmaker()() as session:
            res = await session.execute(
                select(GuildMember).where(
                    GuildMember.user_id == user_id,
                    GuildMember.guild_id == guild_id,
                    GuildMember.guild_role.in_(("guild_master", "guild_vice_master"))
                )
            )
            m = res.scalar_one_or_none()
            return m is not None

guild_service = GuildService()
