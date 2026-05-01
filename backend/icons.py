"""
BlackRose Mini App - Управление иконками
"""

from urllib.parse import quote

# ═══════════════════════════════════════════════════════
# БАЗОВЫЙ URL ДЛЯ ИЗОБРАЖЕНИЙ
# ═══════════════════════════════════════════════════════
# Иконки в исходном репозитории хранятся в frontend/public/assets/images/icons
BASE_URL = "https://cdn.jsdelivr.net/gh/Nihronick/blackrose@gh-pages/assets/images/icons"
WSRV = "https://wsrv.nl/?url="
WSRV_OPT = "&output=webp&n=-1"


def _url(path: str) -> str:
    """Формирует URL иконки через wsrv.nl — отдаёт WebP на лету, кешируется навсегда."""
    parts = path.split("/")
    encoded_parts = [quote(part, safe="") for part in parts]
    raw = f"{BASE_URL}/{'/'.join(encoded_parts)}"
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
    "class19": _url("discord_migrated/1055586742952018001.webp"),
    "class_c20": _url("discord_migrated/1055586744231272498.webp"),
    "class_terra": _url("class_etc/Tera.png"),
    "class_nova": _url("class_etc/Nova.png"),
    "class_sid": _url("class_etc/Seed.png"),
    # Мечи
    "mythic1": _url("discord_migrated/1055585728140148747.webp"),
    "Orr6": _url("discord_migrated/1055585923364048966.webp"),
    "Orr12": _url("discord_migrated/1211887493360648263.webp"),
    "Orr18": _url("discord_migrated/1237969505477722112.webp"),
    "Orr24": _url("discord_migrated/1349197221496885309.webp"),

    "orb6": _url("discord_migrated/1378271019399385209.webp"),
    "orb12": _url("discord_migrated/1211868352184844328.webp"),
    "orb18": _url("discord_migrated/1378271093495697428.webp"),
    "orb24": _url("discord_migrated/1378271179365814425.webp"),
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
    "light_shard": _url("discord_migrated/1400147911526056067.webp"),
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
    "skillbook": _url("discord_migrated/1290965217345540188.webp"),
    "BlackOrb": _url("discord_migrated/1209708648952107028.webp"),
    "cube": _url("class_etc/cube.png"),
    "diary": _url("class_etc/diary.png"),
    "drevo": _url("class_etc/drevo.png"),
    "fam_altar": _url("class_etc/fam_altar.png"),
    "fam_gem": _url("class_etc/fam_gem.png"),
    "guild_cooking": _url("class_etc/guild_cooking.png"),
    "hp_reg_stone": _url("class_etc/hp_reg_stone.png"),

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
    "Melon2": _url("discord_migrated/1134338854657208412.webp"),
    "star": "https://discord.com/assets/6dcab1360be157d5.svg",
}

# ═══════════════════════════════════════════════════════
# PROMOTION (Промоуты)
# ═══════════════════════════════════════════════════════
PROMOTION = {
    "adamant": _url("discord_migrated/1054852905020170390.webp"),
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
    "PillarOfFire": _url("discord_migrated/1054837539896295484.webp"),
    "PowerImpact": _url("skills/PowerImpact.png"),
    "PowerStrike": _url("skills/PowerStrike.png"),
    "Rage": _url("skills/Rage.png"),
    "Rave": _url("discord_migrated/1055598059628789772.webp"),
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
    "FireSlash": _url("discord_migrated/1054837281246163054.webp"),
    "IceStone": _url("discord_migrated/1054837289466986589.webp"),
    "LightningSlash": _url("discord_migrated/1054837295062188053.webp"),
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
    "spirit_radon": _url("discord_migrated/1129588019763089488.webp"),
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
    "adv_forest": _url("class_etc/circulation_gem.png"),
}

# ═══════════════════════════════════════════════════════
# ГИЛЬДИЯ
# ═══════════════════════════════════════════════════════
GUILD = {}

# ═══════════════════════════════════════════════════════
# ВСЕ ИКОНКИ + АЛИАСЫ
# ═══════════════════════════════════════════════════════

# Краткие имена для удобства (алиасы)
ALIASES = {
    # Спириты
    "noah": SPIRIT["spirit_noah"],
    "loar": SPIRIT["spirit_loar"],
    "sala": SPIRIT["spirit_sala"],
    "mum": SPIRIT["spirit_mum"],
    "bo": SPIRIT["spirit_bo"],
    "radon": SPIRIT["spirit_radon"],
    "zappy": SPIRIT["spirit_zappy"],
    "kart": SPIRIT["spirit_kart"],
    "herh": SPIRIT["spirit_herh"],
    "todd": SPIRIT["spirit_todd"],
    "luga": SPIRIT["spirit_luga"],
    "ark": SPIRIT["spirit_ark"],
    # Синонимы и сокращения для гайдов
    "wb": SKILLS["WarriorBurn"],
    "warrior_burn": SKILLS["WarriorBurn"],
    "dancingwave": SKILLS["DancingWaves"],
    "dancing_wave": SKILLS["DancingWaves"],
    "flamewave": SKILLS["FlameWave"],
    "flame_wave": SKILLS["FlameWave"],
    "gigarock": SKILLS["GigaStrike"],
    "giga_rock": SKILLS["GigaStrike"],
    "eisenhardt": PROMOTION["promo_eisenhart"],
    "brozen": PROMOTION["promo_bronze"],
    "arcanite": PROMOTION["promo_arcanite"],
    "black_mythril": PROMOTION["promo_black_mithril"],
    "blackmythril": PROMOTION["promo_black_mithril"],
    "demonmetal": PROMOTION["promo_demonite"],
    "dragonos": PROMOTION["promo_dragonos"],
    "warfrost": PROMOTION["promo_frost"],
    "frost": PROMOTION["promo_frost"],
    "cyclos": PROMOTION["promo_cyclone"],
    "cyclone": PROMOTION["promo_cyclone"],
    "blitzgold": PROMOTION["promo_gold"],
    "demonhunt": SKILLS["DemonHunt"],
    "dh": SKILLS["DemonHunt"],
    "strong": SKILLS["StrongCurrent"],
    "strong_current": SKILLS["StrongCurrent"],
    "lightning_body": SKILLS["LightningBody"],
    "lb": SKILLS["LightningBody"],
    "blizzard": SKILLS["Blizzard"],
    "rage": SKILLS["Rage"],
    "rave": SKILLS["Rave"],
    # Удаленные дубликаты - теперь алиасы
    "hp_stone": CLASS_ETC["hp_reg_stone"],  # Дубликат, используем основное имя
    "M1": CLASS_ETC["sword_m1"],  # Discord ID заменен на локальный файл
    "Tera": CLASS_ETC["class_terra"],  # Discord ID заменен на локальный файл
    "Nova": CLASS_ETC["class_nova"],  # Discord ID заменен на локальный файл
    "Seed": CLASS_ETC["class_sid"],  # Discord ID заменен на локальный файл
    "OrrBase": CLASS_ETC["sword_opp"],  # Дубликат sword_opp (используется в гайдах)
    "orb": CLASS_ETC["sword_orb"],  # Дубликат sword_orb (используется в гайдах)
    "adv_mind": CLASS_ETC["gold"],  # migrated from duplicate
    "cat_promoutes": PROMOTION["promo_frost"],  # migrated from duplicate
    "icon_1054837281246163054": SKILLS["FireSlash"],  # migrated from duplicate
    "icon_1054837289466986589": SKILLS["IceStone"],  # migrated from duplicate
    "icon_1054837295062188053": SKILLS["LightningSlash"],  # migrated from duplicate
    "icon_1054837539896295484": SKILLS["PillarOfFire"],  # migrated from duplicate
    "icon_1054852905020170390": PROMOTION["adamant"],  # migrated from duplicate
    "icon_1055585728140148747": CLASS_ETC["mythic1"],  # migrated from duplicate
    "icon_1055585923364048966": CLASS_ETC["Orr6"],  # migrated from duplicate
    "icon_1055586742952018001": CLASS_ETC["class19"],  # migrated from duplicate
    "icon_1055586744231272498": CLASS_ETC["class_c20"],  # migrated from duplicate
    "icon_1055598059628789772": SKILLS["Rave"],  # migrated from duplicate
    "icon_1129588019763089488": SPIRIT["spirit_radon"],  # migrated from duplicate
    "icon_1134338854657208412": CLASS_ETC["Melon2"],  # migrated from duplicate
    "icon_1209708648952107028": CLASS_ETC["BlackOrb"],  # migrated from duplicate
    "icon_1211868352184844328": CLASS_ETC["orb12"],  # migrated from duplicate
    "icon_1211887493360648263": CLASS_ETC["Orr12"],  # migrated from duplicate
    "icon_1237969505477722112": CLASS_ETC["Orr18"],  # migrated from duplicate
    "icon_1290965217345540188": CLASS_ETC["skillbook"],  # migrated from duplicate
    "icon_1349197221496885309": CLASS_ETC["Orr24"],  # migrated from duplicate
    "icon_1378271019399385209": CLASS_ETC["orb6"],  # migrated from duplicate
    "icon_1378271093495697428": CLASS_ETC["orb18"],  # migrated from duplicate
    "icon_1378271179365814425": CLASS_ETC["orb24"],  # migrated from duplicate
    "icon_1400147911526056067": CLASS_ETC["light_shard"],  # migrated from duplicate
    "info_rage": SKILLS["Rage"],  # migrated from duplicate

}



# ═══════════════════════════════════════════════════════
# MIGRATED FROM DISCORD GUIDES
# ═══════════════════════════════════════════════════════
MIGRATED = {
    "icon_1054837307947098162": _url("discord_migrated/1054837307947098162.webp"),
    "icon_1054837329367420998": _url("discord_migrated/1054837329367420998.webp"),
    "icon_1054837335084236881": _url("discord_migrated/1054837335084236881.webp"),
    "icon_1054837351270060173": _url("discord_migrated/1054837351270060173.webp"),
    "icon_1054837355497922641": _url("discord_migrated/1054837355497922641.webp"),
    "icon_1054837360354938950": _url("discord_migrated/1054837360354938950.webp"),
    "icon_1054837443347615796": _url("discord_migrated/1054837443347615796.webp"),
    "icon_1054837450415022140": _url("discord_migrated/1054837450415022140.webp"),
    "icon_1054837455246868560": _url("discord_migrated/1054837455246868560.webp"),
    "icon_1054837459994812426": _url("discord_migrated/1054837459994812426.webp"),
    "icon_1054837499027013642": _url("discord_migrated/1054837499027013642.webp"),
    "icon_1054837500012671046": _url("discord_migrated/1054837500012671046.webp"),
    "icon_1054837501195468851": _url("discord_migrated/1054837501195468851.webp"),
    "icon_1054837502499889262": _url("discord_migrated/1054837502499889262.webp"),
    "icon_1054837514675966034": _url("discord_migrated/1054837514675966034.webp"),
    "icon_1054837516102021211": _url("discord_migrated/1054837516102021211.webp"),
    "icon_1054837517523882115": _url("discord_migrated/1054837517523882115.webp"),
    "icon_1054837518668923000": _url("discord_migrated/1054837518668923000.webp"),
    "icon_1054837524343824444": _url("discord_migrated/1054837524343824444.webp"),
    "icon_1054837525799248034": _url("discord_migrated/1054837525799248034.webp"),
    "icon_1054837527204352010": _url("discord_migrated/1054837527204352010.webp"),
    "icon_1054837528714293288": _url("discord_migrated/1054837528714293288.webp"),
    "icon_1054837537312608287": _url("discord_migrated/1054837537312608287.webp"),
    "icon_1054837538793197628": _url("discord_migrated/1054837538793197628.webp"),
    "icon_1054837540970057778": _url("discord_migrated/1054837540970057778.webp"),
    "icon_1054837553951416431": _url("discord_migrated/1054837553951416431.webp"),
    "icon_1054837555482341487": _url("discord_migrated/1054837555482341487.webp"),
    "icon_1054837556778373120": _url("discord_migrated/1054837556778373120.webp"),
    "icon_1054837558133129236": _url("discord_migrated/1054837558133129236.webp"),
    "icon_1054837580388126721": _url("discord_migrated/1054837580388126721.webp"),
    "icon_1054837582124560485": _url("discord_migrated/1054837582124560485.webp"),
    "icon_1054837583382847648": _url("discord_migrated/1054837583382847648.webp"),
    "icon_1054837613074321561": _url("discord_migrated/1054837613074321561.webp"),
    "icon_1054837628563890197": _url("discord_migrated/1054837628563890197.webp"),
    "icon_1054837629679575160": _url("discord_migrated/1054837629679575160.webp"),
    "icon_1054837631726395506": _url("discord_migrated/1054837631726395506.webp"),
    "icon_1054837638730879106": _url("discord_migrated/1054837638730879106.webp"),
    "icon_1054837659052285972": _url("discord_migrated/1054837659052285972.webp"),
    "icon_1054837660025360464": _url("discord_migrated/1054837660025360464.webp"),
    "icon_1054837661195583558": _url("discord_migrated/1054837661195583558.webp"),
    "icon_1054837662445469706": _url("discord_migrated/1054837662445469706.webp"),
    "icon_1054852900565819473": _url("discord_migrated/1054852900565819473.webp"),
    "icon_1054852902277099560": _url("discord_migrated/1054852902277099560.webp"),
    "icon_1054852906903425035": _url("discord_migrated/1054852906903425035.webp"),
    "icon_1054852908442718279": _url("discord_migrated/1054852908442718279.webp"),
    "icon_1054852911399714816": _url("discord_migrated/1054852911399714816.webp"),
    "icon_1054853047894941747": _url("discord_migrated/1054853047894941747.webp"),
    "icon_1054853274613862490": _url("discord_migrated/1054853274613862490.webp"),
    "icon_1054853414686834699": _url("discord_migrated/1054853414686834699.webp"),
    "icon_1055585922177040454": _url("discord_migrated/1055585922177040454.webp"),
    "icon_1055586248552628274": _url("discord_migrated/1055586248552628274.webp"),
    "icon_1055586814481678407": _url("discord_migrated/1055586814481678407.webp"),
    "icon_1055587557976580106": _url("discord_migrated/1055587557976580106.webp"),
    "icon_1055588078254825585": _url("discord_migrated/1055588078254825585.webp"),
    "icon_1057163620703813684": _url("discord_migrated/1057163620703813684.webp"),
    "icon_1058492848279912569": _url("discord_migrated/1058492848279912569.webp"),
    "icon_1060039749336830002": _url("discord_migrated/1060039749336830002.webp"),
    "icon_1060039750913888296": _url("discord_migrated/1060039750913888296.webp"),
    "icon_1060039752704864336": _url("discord_migrated/1060039752704864336.webp"),
    "icon_1060039754382585856": _url("discord_migrated/1060039754382585856.webp"),
    "icon_1060039755561193562": _url("discord_migrated/1060039755561193562.webp"),
    "icon_1060039928794333184": _url("discord_migrated/1060039928794333184.webp"),
    "icon_1078109040225292338": _url("discord_migrated/1078109040225292338.webp"),
    "icon_1060758770373886002": _url("discord_migrated/1060758770373886002.webp"),
    "icon_1060758772752056380": _url("discord_migrated/1060758772752056380.webp"),
    "icon_1060758774421409792": _url("discord_migrated/1060758774421409792.webp"),
    "icon_1060758775839080598": _url("discord_migrated/1060758775839080598.webp"),
    "icon_1060758778221436989": _url("discord_migrated/1060758778221436989.webp"),
    "icon_1060758779488112701": _url("discord_migrated/1060758779488112701.webp"),
    "icon_1060758780775764058": _url("discord_migrated/1060758780775764058.webp"),
    "icon_1060758784106057880": _url("discord_migrated/1060758784106057880.webp"),
    "icon_1060758787092402237": _url("discord_migrated/1060758787092402237.webp"),
    "icon_1060758788237443132": _url("discord_migrated/1060758788237443132.webp"),
    "icon_1060758791207002131": _url("discord_migrated/1060758791207002131.webp"),
    "icon_1060759190672515092": _url("discord_migrated/1060759190672515092.webp"),
    "icon_1063957405207121991": _url("discord_migrated/1063957405207121991.webp"),
    "icon_1071202177479098408": _url("discord_migrated/1071202177479098408.webp"),
    "icon_1083099023415713895": _url("discord_migrated/1083099023415713895.webp"),
    "icon_1090019626307555329": _url("discord_migrated/1090019626307555329.webp"),
    "icon_1124431948736106618": _url("discord_migrated/1124431948736106618.webp"),
    "icon_1127994010422739075": _url("discord_migrated/1127994010422739075.webp"),
    "icon_1129565901952389160": _url("discord_migrated/1129565901952389160.webp"),
    "icon_1129565908759752806": _url("discord_migrated/1129565908759752806.webp"),
    "icon_1129565909716058244": _url("discord_migrated/1129565909716058244.webp"),
    "icon_1129565910768812072": _url("discord_migrated/1129565910768812072.webp"),
    "icon_1123568469821100032": _url("discord_migrated/1123568469821100032.webp"),
    "icon_1129588010032308294": _url("discord_migrated/1129588010032308294.webp"),
    "icon_1129588011269636208": _url("discord_migrated/1129588011269636208.webp"),
    "icon_1129588012427251722": _url("discord_migrated/1129588012427251722.webp"),
    "icon_1129588013383561327": _url("discord_migrated/1129588013383561327.webp"),
    "icon_1129588014088200223": _url("discord_migrated/1129588014088200223.webp"),
    "icon_1129588015925297203": _url("discord_migrated/1129588015925297203.webp"),
    "icon_1129588017493979258": _url("discord_migrated/1129588017493979258.webp"),
    "icon_1129588021486964836": _url("discord_migrated/1129588021486964836.webp"),
    "icon_1129588496638681181": _url("discord_migrated/1129588496638681181.webp"),
    "icon_1129588498375123034": _url("discord_migrated/1129588498375123034.webp"),
    "icon_1129588499528552508": _url("discord_migrated/1129588499528552508.webp"),
    "icon_1133899080611926159": _url("discord_migrated/1133899080611926159.webp"),
    "icon_1133899362750173305": _url("discord_migrated/1133899362750173305.webp"),
    "icon_1133899445482836008": _url("discord_migrated/1133899445482836008.webp"),
    "icon_1133899568073945118": _url("discord_migrated/1133899568073945118.webp"),
    "icon_1134338853679923230": _url("discord_migrated/1134338853679923230.webp"),
    "icon_1131610389348618271": _url("discord_migrated/1131610389348618271.webp"),
    "icon_1131610390598529098": _url("discord_migrated/1131610390598529098.webp"),
    "icon_1131610391840047164": _url("discord_migrated/1131610391840047164.webp"),
    "icon_1139514468557140089": _url("discord_migrated/1139514468557140089.webp"),
    "icon_1141496057423999026": _url("discord_migrated/1141496057423999026.webp"),
    "icon_1174921381201330276": _url("discord_migrated/1174921381201330276.webp"),
    "icon_1178911252785942601": _url("discord_migrated/1178911252785942601.webp"),
    "icon_1180968900905668648": _url("discord_migrated/1180968900905668648.webp"),
    "icon_1195949656354586744": _url("discord_migrated/1195949656354586744.webp"),
    "icon_1195951217524867154": _url("discord_migrated/1195951217524867154.webp"),
    "icon_1195951234327257138": _url("discord_migrated/1195951234327257138.webp"),
    "icon_1195951394973302814": _url("discord_migrated/1195951394973302814.webp"),
    "icon_1209706860727242823": _url("discord_migrated/1209706860727242823.webp"),
    "icon_1211212441988366367": _url("discord_migrated/1211212441988366367.webp"),
    "icon_1211868018590879864": _url("discord_migrated/1211868018590879864.webp"),
    "icon_1257278191832399872": _url("discord_migrated/1257278191832399872.webp"),
    "icon_1260970526642405437": _url("discord_migrated/1260970526642405437.webp"),
    "icon_1276144888508977162": _url("discord_migrated/1276144888508977162.webp"),
    "icon_1283966815814291456": _url("discord_migrated/1283966815814291456.webp"),
    "icon_1290963101914628137": _url("discord_migrated/1290963101914628137.webp"),
    "icon_1315113407631851520": _url("discord_migrated/1315113407631851520.webp"),
    "icon_1319143179454517358": _url("discord_migrated/1319143179454517358.webp"),
    "icon_1319158997508423793": _url("discord_migrated/1319158997508423793.webp"),
    "icon_1319158999249064007": _url("discord_migrated/1319158999249064007.webp"),
    "icon_1319159000863866890": _url("discord_migrated/1319159000863866890.webp"),
    "icon_1319159002948440084": _url("discord_migrated/1319159002948440084.webp"),
    "icon_1319159005620342795": _url("discord_migrated/1319159005620342795.webp"),
    "icon_1319159006841012306": _url("discord_migrated/1319159006841012306.webp"),
    "icon_1319159008204165131": _url("discord_migrated/1319159008204165131.webp"),
    "icon_1319159228266578000": _url("discord_migrated/1319159228266578000.webp"),
    "icon_1332873898366205963": _url("discord_migrated/1332873898366205963.webp"),
    "icon_1365046130702024825": _url("discord_migrated/1365046130702024825.webp"),
    "icon_1388512556519526483": _url("discord_migrated/1388512556519526483.webp"),
    "icon_1401743654770446336": _url("discord_migrated/1401743654770446336.webp"),
    "icon_1415539577690656901": _url("discord_migrated/1415539577690656901.webp"),
    "icon_1458671724831707146": _url("discord_migrated/1458671724831707146.webp"),
    "icon_1458963780380917965": _url("discord_migrated/1458963780380917965.webp"),
    "icon_1464858568976109582": _url("discord_migrated/1464858568976109582.webp"),
    "icon_966086910231597096": _url("discord_migrated/966086910231597096.webp"),
    "icon_1464096337959063674": _url("discord_migrated/1464096337959063674.webp"),}

ALL_ICONS = {
    **CLASS_ETC,
    **PROMOTION,
    **SKILLS,
    **SPIRIT,
    **INFO_CATEGORIES,
    **ADVENTURES,
    **GUILD,
    **ALIASES,
    **MIGRATED,
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
