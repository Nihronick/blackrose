"""
BlackRose Mini App - Управление иконками
"""

from urllib.parse import quote

# ═══════════════════════════════════════════════════════
# БАЗОВЫЙ URL ДЛЯ ИЗОБРАЖЕНИЙ
# ═══════════════════════════════════════════════════════
BASE_URL = "https://raw.githubusercontent.com/Nihronick/blackrose/main/assets/images/icons"


def _url(path: str) -> str:
    """Безопасное формирование URL — кодирует пробелы и спецсимволы"""
    # Разбиваем путь на части и кодируем каждую
    parts = path.split("/")
    encoded_parts = [quote(part, safe="") for part in parts]
    return f"{BASE_URL}/{'/'.join(encoded_parts)}"


# ═══════════════════════════════════════════════════════
# CLASS_ETC (Классы, мечи, реликвии и прочее)
# ═══════════════════════════════════════════════════════
CLASS_ETC = {
    # Классы
    "class_c17": _url("class_etc/c17.png"),
    "class_c18": _url("class_etc/c18.png"),
    "class_c19": _url("class_etc/c19.png"),
    "class_c20": _url("class_etc/c20.png"),
    "class_terra": _url("class_etc/Tera.png"),
    "class_nova": _url("class_etc/Nova.png"),
    "class_sid": _url("class_etc/Seed.png"),
    # Мечи 
    "sword_m1": _url("class_etc/m1_sword.png"),
    "sword_opp": _url("class_etc/orr.png"),
    "sword_orb": _url("class_etc/orb.png"),
    "sword_awaken": _url("class_etc/awaken.png"),
    "sword_absolutev1": _url("class_etc/AbsoluteV1.png"),
    "sword_absolutev2": _url("class_etc/AbsoluteV2.gif"),
    "sword_immortal": _url("class_etc/immortl_sword.png"),
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
    "crit%": _url("class_etc/CRIT%.png"),
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
}

# ═══════════════════════════════════════════════════════
# PROMOTION (Промоуты)
# ═══════════════════════════════════════════════════════
PROMOTION = {
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
    "PillarOfFire": _url("skills/PillarOfFire.png"),
    "PowerImpact": _url("skills/PowerImpact.png"),
    "PowerStrike": _url("skills/PowerStrike.png"),
    "Rage": _url("skills/Rage.png"),
    "Rave": _url("skills/Rave.png"),
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
    "spirit_radon": _url("spirits/Radon.png"),
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
    "awaken_e": _url("spirit/awaken_e.png"),
    "awaken_a": _url("spirit/awaken_a.png"),
}

# ═══════════════════════════════════════════════════════
# КАТЕГОРИИ ИНФОРМАЦИИ
# ═══════════════════════════════════════════════════════
INFO_CATEGORIES = {
    "info_general": _url("class_etc/sl_icon.png"),
    "info_event": _url("info_event.png"),
    "info_rage": _url("skills/Rage.png"),
    "info_ads": _url("class_etc/rek_scroll.png"),
    "info_pets": _url("info_pets.png"),
    "info_sword": _url("info_sword.png"),
    "info_farm": _url("info_farm.png"),
    "info_spirit": _url("info_spirit.png"),
    "info_build": _url("info_build.png"),
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
    "guild_guild": _url("118.png"),
    "guild_wyvern": _url("guild_wyvern.png"),
    "guild_cooking": _url("guild_cooking.png"),
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
