"""
BlackRose Mini App - Управление иконками
"""

from urllib.parse import quote

# ═══════════════════════════════════════════════════════
# БАЗОВЫЙ URL ДЛЯ ИЗОБРАЖЕНИЙ
# ═══════════════════════════════════════════════════════
BASE_URL = "https://raw.githubusercontent.com/Nihronick/blackrose/main/assets/images/icons"
WSRV     = "https://wsrv.nl/?url="
WSRV_OPT = "&output=webp&n=-1"


def _url(path: str) -> str:
    """Формирует URL иконки через wsrv.nl — отдаёт WebP на лету, кешируется навсегда."""
    parts         = path.split("/")
    encoded_parts = [quote(part, safe="") for part in parts]
    raw           = f"{BASE_URL}/{'/'.join(encoded_parts)}"
    # GIF оставляем как есть — wsrv.nl конвертирует их в статичный WebP,
    # что ломает анимацию. Если анимация важна — убери проверку.
    if path.endswith(".gif"):
        return raw
    return f"{WSRV}{raw}{WSRV_OPT}"


# ═══════════════════════════════════════════════════════
# CLASS_ETC (Классы, мечи, реликвии и прочее)
# ═══════════════════════════════════════════════════════
CLASS_ETC = {
    # Классы
    "class_c17": _url("class_etc/c17.png"),
    "class_c18": _url("class_etc/c18.png"),
    "class_c19": _url("class_etc/c19.png"),
    "class19": "https://wsrv.nl/?url=cdn.discordapp.com/emojis/1055586742952018001.webp?size=44",
    "class_c20": "https://wsrv.nl/?url=cdn.discordapp.com/emojis/1055586744231272498.webp?size=44",
    "class_terra": _url("class_etc/Tera.png"),
    "class_nova": _url("class_etc/Nova.png"),
    "class_sid": _url("class_etc/Seed.png"),
    "Seed": "https://wsrv.nl/?url=cdn.discordapp.com/emojis/1174921381201330276.webp?size=44",
    "Nova": "https://wsrv.nl/?url=cdn.discordapp.com/emojis/1276144888508977162.webp?size=44",
    "Tera": "https://wsrv.nl/?url=cdn.discordapp.com/emojis/1055588078254825585.webp?size=44",
    # Мечи 
    "mythic1": "https://wsrv.nl/?url=cdn.discordapp.com/emojis/1055585728140148747.webp?size=44",
    "OrrBase": "https://wsrv.nl/?url=cdn.discordapp.com/emojis/1055585922177040454.webp?size=44",
    "Orr6": "https://wsrv.nl/?url=cdn.discordapp.com/emojis/1055585923364048966.webp?size=44",
    "Orr12": "https://wsrv.nl/?url=cdn.discordapp.com/emojis/1211887493360648263.webp?size=44",
    "Orr18": "https://wsrv.nl/?url=cdn.discordapp.com/emojis/1237969505477722112.webp?size=44&animated=true",
    "Orr24": "https://wsrv.nl/?url=cdn.discordapp.com/emojis/1349197221496885309.webp?size=44&animated=true",
    "M1": "https://wsrv.nl/?url=cdn.discordapp.com/emojis/1211868018590879864.webp?size=44",
    "orb": "https://wsrv.nl/?url=cdn.discordapp.com/emojis/1127994010422739075.webp?size=44",
    "orb6": "https://wsrv.nl/?url=cdn.discordapp.com/emojis/1378271019399385209.webp?size=44",
    "orb12": "https://wsrv.nl/?url=cdn.discordapp.com/emojis/1211868352184844328.webp?size=44",
    "orb18": "https://wsrv.nl/?url=cdn.discordapp.com/emojis/1378271093495697428.webp?size=44",
    "orb24": "https://wsrv.nl/?url=cdn.discordapp.com/emojis/1378271179365814425.webp?size=44",
    "sword_m1": _url("class_etc/m1_sword.png"),
    "sword_opp": _url("class_etc/orr.png"),
    "sword_orb": _url("class_etc/orb.png"),
    "sword_awaken": _url("class_etc/awaken.png"),
    "sword_absolutev1": _url("class_etc/AbsoluteV1.png"),
    "sword_absolutev2": _url("class_etc/AbsoluteV2.gif"),
    "sword_immortal": _url("class_etc/immortl_sword.png"),
    "memory_tree": _url("class_etc/memory_tree.png"),
    "eq": _url("class_etc/eq.png"),
    "all": _url("class_etc/all.png"),
    "msg": _url("class_etc/msg.png"),
    # Спутники
    "luna": _url("class_etc/luna.png"),
    "ellie": _url("class_etc/ellie.png"),
    "miho": _url("class_etc/miho.png"),
    "zeke": _url("class_etc/zeke.png"),
    # Другое
    "soul_sword": _url("class_etc/soul_sword.png"),
    "acc": _url("class_etc/ACC.png"),
    "ds": _url("class_etc/DEATH_STRIKE.png"),
    "atk": _url("class_etc/ATK.png"),
    "crit": _url("class_etc/CRIT_DMG.png"),
    "crit2": _url("class_etc/CRIT2.png"),
    "hp": _url("class_etc/HP.png"),
    "hpr": _url("class_etc/HP_RECOVERY.png"),
    "diamond": _url("class_etc/diamond.png"),
    "gold": _url("class_etc/gold.png"),
    "gem": _url("class_etc/gem.png"),
    "earth": _url("class_etc/zeke_gem.png"),
    "fire": _url("class_etc/FIRE_GEM.png"),
    "water": _url("class_etc/luna_gem.png"),
    "wind": _url("class_etc/ellie_gem.png"),
    "farm": _url("class_etc/afk.png"),
    "pero_viol": _url("class_etc/Pero_viol.png"),
    "pero_berez": _url("class_etc/Pero_berez.png"),
    "legendary_spirit": _url("class_etc/legendary_spirir.png"),
    "random_epic_spirit": _url("class_etc/random_epic_spirit.png"),
    "legendary_skill": _url("class_etc/legendary_skill.png"),
    "light_shard": "https://wsrv.nl/?url=cdn.discordapp.com/emojis/1400147911526056067.webp?size=44",
    "stage": _url("class_etc/stage.png"),
    "Constellation": _url("class_etc/Constellation.png"),
    "boss": _url("class_etc/boss.png"),
    "BR": _url("class_etc/BR.png"),
    "cock": _url("class_etc/cock.png"),
    "cum": _url("class_etc/cum.png"),
    "dig": _url("class_etc/dig.png"),
    "raid": _url("class_etc/raid.png"),
    "relic": _url("class_etc/relic.png"),
    "woman": _url("class_etc/woman.png"),
    "skillbook": "https://wsrv.nl/?url=cdn.discordapp.com/emojis/1290965217345540188.webp?size=44",
    "BlackOrb": "https://cdn.discordapp.com/emojis/1209708648952107028.webp?size=44",
    "cube": _url("class_etc/cube.png"),
    "diary": _url("class_etc/diary.png"),
    "drevo": _url("class_etc/drevo.png"),
    "fam_altar": _url("class_etc/fam_altar.png"),
    "fam_gem": _url("class_etc/fam_gem.png"),
    "guild_cooking": _url("class_etc/guild_cooking.png"),
    "hp_reg_stone": _url("class_etc/hp_reg_stone.png"),
    "hp_stone": _url("class_etc/hp_reg_stone.png"),
    "mithic_skill": _url("class_etc/mithic_skill.png"),
    "quest": _url("class_etc/quest.png"),
    "random_legendary_spirit": _url("class_etc/random_legendary_spirit.png"),
    "random_spirit": _url("class_etc/random_spirit.png"),
    "red_soul": _url("class_etc/red_soul.png"),
    "sin_soul": _url("class_etc/sin_soul.png"),
    "skill_master": _url("class_etc/skill_master.png"),
    "summon_class": _url("class_etc/summon_class.png"),
    "summon_sword": _url("class_etc/summon_sword.png"),
    "chest": _url("class_etc/chest.png"),
    "seruigem": _url("class_etc/seruigem.png"),
    "shard": _url("class_etc/shard.png"),
    "shop": _url("class_etc/shop.png"),
    "shrine": _url("class_etc/shrine.png"),
    "191": _url("class_etc/191.png"),
}

# ═══════════════════════════════════════════════════════
# PROMOTION (Промоуты)
# ═══════════════════════════════════════════════════════
PROMOTION = {
    "adamant": "https://cdn.discordapp.com/emojis/1054852905020170390.webp?size=44",
    "promo_ether": _url("promotion/Ether.png"),
    "promo_black_mithril": _url("promotion/Black_Mythril.png"),
    "promo_demonite": _url("promotion/Demon_Metal.png"),
    "promo_dragonos": _url("promotion/Dragonos.png"),
    "promo_blood": _url("promotion/Ragnablood.png"),
    "promo_frost": _url("promotion/Warfrost.png"),
    "promo_nox": _url("promotion/Dark_Nox.png"),
    "promo_abyss": _url("promotion/Blue_Abyss.png"),
    "promo_infinat": _url("promotion/Infinaut.png"),
    "promo_cyclone": _url("promotion/Cyclos.png"),
    "promo_ancient": _url("promotion/Ancient_Canine.png"),
    "promo_gigalor": _url("promotion/Gigarock.png"),
    "cat_promoutes": _url("promotion/Warfrost.png"),
    "promo_adamant": _url("promotion/Adamant.png"),
    "promo_arcanite": _url("promotion/Acranite.png"),
    "promo_stone": _url("promotion/Stone.png"),
    "promo_silver": _url("promotion/Silver.png"),
    "promo_orichalcum": _url("promotion/Orichalcum.png"),
    "promo_gold": _url("promotion/Gold.png"),
    "promo_iron": _url("promotion/Iron.png"),
    "promo_bronze": _url("promotion/Bronze.png"),
    "promo_diadust": _url("promotion/Diadust.png"),
    "promo_eisenhart": _url("promotion/Eisenhart.png"),
    "promo_Eldenwood": _url("promotion/Eldenwood.png"),
    "promo_mithrill": _url("promotion/Mithrill.png"),
}

# ═══════════════════════════════════════════════════════
# SKILLS (Навыки и камни)
# ═══════════════════════════════════════════════════════
SKILLS = {
    "Agile": _url("skills/Agile.png"),
    "Blizzard": _url("skills/Blizzard.png"),
    "BurningSword": _url("skills/BurningSword.png"),
    "CurvedBlade": _url("skills/CurvedBlade.png"),
    "DancingWaves": _url("skills/DancingWaves.png"),
    "DemonHunt": _url("skills/DemonHunt.png"),
    "EarthsWill": _url("skills/EarthsWill.png"),
    "FireBlast": _url("skills/FireBlast.png"),
    "FireSword": _url("skills/FireSword.png"),
    "FlameSlash": _url("skills/FlameSlash.png"),
    "FlameWave": _url("skills/FlameWave.png"),
    "FlowingBlade": _url("skills/FlowingBlade.png"),
    "Fulgurous": _url("skills/Fulgurous.png"),
    "GigaImpact": _url("skills/GigaImpact.png"),
    "GigaStrike": _url("skills/GigaStrike.png"),
    "GroundsBlessing": _url("skills/GroundsBlessing.png"),
    "HellfireSlash": _url("skills/HellfireSlash.png"),
    "HotBlast": _url("skills/HotBlast.png"),
    "IceShower": _url("skills/IceShower.png"),
    "IceTime": _url("skills/IceTime.png"),
    "IronWill": _url("skills/IronWill.png"),
    "LifeMana": _url("skills/LifeMana.png"),
    "LightningStroke": _url("skills/LightingStroke.png"),
    "LightningBody": _url("skills/LightningBody.png"),
    "ManasBlessing": _url("skills/ManasBlessing.png"),
    "Mantra": _url("skills/Mantra.png"),
    "Meditation": _url("skills/Meditation.png"),
    "PillarOfFire": "https://wsrv.nl/?url=cdn.discordapp.com/emojis/1054837539896295484.webp?size=44",
    "PowerImpact": _url("skills/PowerImpact.png"),
    "PowerStrike": _url("skills/PowerStrike.png"),
    "Rage": _url("skills/Rage.png"),
    "Rave": "https://wsrv.nl/?url=cdn.discordapp.com/emojis/1055598059628789772.webp?size=44",
    "RedLightning": _url("skills/RedLighting.png"),
    "SpeedSword": _url("skills/SpeedSword.png"),
    "StrongCurrent": _url("skills/StrongCurrent.png"),
    "Supersonic": _url("skills/Supersonic.png"),
    "ThunderboltSlash": _url("skills/ThunderboltSlash.png"),
    "ThunderSlash": _url("skills/ThunderSlash.png"),
    "WarriorBurn": _url("skills/WarriorBurn.png"),
    "WaterSlash": _url("skills/WaterSlash.png"),
    "WindSword": _url("skills/WindSword.png"),
    "WrathOfGods": _url("skills/WrathOfGods.png"),
}

# ═══════════════════════════════════════════════════════
# SPIRIT (Духи и фамильяры)
# ═══════════════════════════════════════════════════════
SPIRIT = {
    # Духи — папка "spirits"
    "spirit_noah": _url("spirits/Noah.png"),
    "spirit_loar": _url("spirits/Loar.png"),
    "spirit_sala": _url("spirits/Sala.png"),
    "spirit_mum": _url("spirits/Mum.png"),
    "spirit_bo": _url("spirits/Bo.png"),
    "spirit_radon": "https://cdn.discordapp.com/emojis/1129588019763089488.webp?size=44",
    "spirit_zappy": _url("spirits/Zappy.png"),
    "spirit_kart": _url("spirits/Kart.png"),
    "spirit_herh": _url("spirits/Herh.png"),
    "spirit_todd": _url("spirits/Todd.png"),
    "spirit_luga": _url("spirits/Luga.png"),
    "spirit_ark": _url("spirits/Ark.png"),
    # Навыки духов
    "skill_noah": _url("spirits/noah_skill.png"),
    "skill_loar": _url("spirits/loar_skill.png"),
    "skill_sala": _url("spirits/sala_skill.png"),
    "skill_mum": _url("spirits/mum_skill.png"),
    "skill_bo": _url("spirits/bo_skill.png"),
    "skill_radon": _url("spirits/raddon_skill.png"),
    "skill_zappy": _url("spirits/zappy_skill.png"),
    "skill_kart": _url("spirits/kart_skill.png"),
    "skill_herh": _url("spirits/herh_skill.png"),
    "skill_todd": _url("spirits/todd_skill.png"),
    "skill_luga": _url("spirits/luga_skill.png"),
    "skill_ark": _url("spirits/ark_skill.png"),
    # Фамильяры — папка "spirits"
    "fam_hi": _url("spirits/HI.png"),
    "fam_je": _url("spirits/JE.png"),
    "fam_ku": _url("spirits/KU.png"),
    "fam_a": _url("spirits/A.png"),
    "fam_leon": _url("spirits/LEON.png"),
    "fam_mus": _url("spirits/MUS.png"),
    "fam_na": _url("spirits/NA.png"),
    "fam_pe": _url("spirits/PE.png"),
    "fam_po": _url("spirits/PO.png"),
    "fam_ru": _url("spirits/RU.png"),
    "fam_sha": _url("spirits/SHA.png"),
    "fam_ti": _url("spirits/TI.png"),
    # Звёзды
    "star": _url("class_etc/star.png"),
    "starv2": _url("class_etc/star_v2.png"),
}

# ═══════════════════════════════════════════════════════
# КАТЕГОРИИ ИНФОРМАЦИИ
# ═══════════════════════════════════════════════════════
INFO_CATEGORIES = {
    "info_general": _url("class_etc/sl_icon.png"),
    "info_rage": _url("skills/Rage.png"),
    "info_ads": _url("class_etc/rek_scroll.png"),
}

# ═══════════════════════════════════════════════════════
# ПРИКЛЮЧЕНИЯ
# ═══════════════════════════════════════════════════════
ADVENTURES = {
    "adv_adventures": _url("class_etc/adventure.png"),
    "adv_cave": _url("class_etc/exp.png"),
    "adv_rift": _url("class_etc/violet_cube.png"),
    "adv_shelter": _url("class_etc/latent_power.png"),
    "adv_mind": _url("class_etc/gold.png"),
    "adv_forest": _url("class_etc/circulation_gem.png"),
}

# ═══════════════════════════════════════════════════════
# ГИЛЬДИЯ
# ═══════════════════════════════════════════════════════
GUILD = {

}

# ═══════════════════════════════════════════════════════
# ВСЕ ИКОНКИ
# ═══════════════════════════════════════════════════════
ALL_ICONS = {
    **CLASS_ETC,
    **PROMOTION,
    **SKILLS,
    **SPIRIT,
    **INFO_CATEGORIES,
    **ADVENTURES,
    **GUILD,
}


# ═══════════════════════════════════════════════════════
# HELPER ФУНКЦИИ
# ═══════════════════════════════════════════════════════


# Кеш для регистронезависимого поиска: lower(key) -> original_url
_ICONS_LOWER: dict = {}

def _build_lower_cache():
    global _ICONS_LOWER
    _ICONS_LOWER = {k.lower(): v for k, v in ALL_ICONS.items()}

_build_lower_cache()


def get_icon(name: str, default: str = None) -> str:
    """Получить URL иконки по имени. Поиск регистронезависимый."""
    return ALL_ICONS.get(name) or _ICONS_LOWER.get(name.lower(), default)


def get_category_icons(category: str) -> dict:
    """Получить все иконки категории"""
    categories = {
        "class_etc": CLASS_ETC,
        "promotion": PROMOTION,
        "skills": SKILLS,
        "spirit": SPIRIT,
        "info": INFO_CATEGORIES,
        "adventures": ADVENTURES,
        "guild": GUILD,
    }
    return categories.get(category, {})


def list_all_icons() -> list:
    """Список всех имён иконок"""
    return list(ALL_ICONS.keys())


def generate_icon_html(name: str, size: int = 32) -> str:
    """HTML тег для иконки"""
    url = get_icon(name)
    if not url:
        return ""
    return (
        f'<img src="{url}" alt="{name}" width="{size}" height="{size}" '
        f'class="inline-icon" onerror="this.style.display=\'none\'">'
    )


def get_stats() -> dict:
    """Статистика иконок"""
    return {
        "total_icons": len(ALL_ICONS),
        "class_etc": len(CLASS_ETC),
        "promotion": len(PROMOTION),
        "skills": len(SKILLS),
        "spirit": len(SPIRIT),
        "info": len(INFO_CATEGORIES),
        "adventures": len(ADVENTURES),
        "guild": len(GUILD),
    }