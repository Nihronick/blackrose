import re
from icons import get_icon, get_stats

def format_guide_text(text: str) -> str:
    """
    Заменяет плейсхолдеры иконок на HTML img теги
    Пример: {{promo_ether}} → <img src="URL" width="20">
    """
    # Находим все плейсхолдеры {{icon_name}}
    
    from icons import get_icon

    def replace_icon(match):
        icon_name = match.group(1)
        icon_url = get_icon(icon_name)
        return f'<img src="{icon_url}" alt="{icon_name}" width="20" height="20" style="vertical-align: middle; margin: 0 4px;">'

    # Заменяем {{icon_name}} на img теги
    formatted_text = re.sub(r"\{\{(\w+)\}\}", replace_icon, text)

    # Дополнительно: заменяем переносы строк на <br>
    formatted_text = formatted_text.replace("\n", "<br>")

    # Заменяем **text** на <strong>text</strong>
    formatted_text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", formatted_text)

    # Заменяем *text* на <em>text</em>
    formatted_text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", formatted_text)

    return formatted_text


# ═══════════════════════════════════════════════════════
# 📋 КАТЕГОРИИ (с иконками)
# ═══════════════════════════════════════════════════════
MAIN_CATEGORIES = {
    "cat_promoutes": {"title": "Промоуты", "icon": get_icon("promo_nox")},
    "info_general": {
        "title": "Общая информация",
        "icon": "https://raw.githubusercontent.com/Nihronick/blackrose/main/assets/images/icons/class_etc/sl_icon.png",
    },
    "adv_adventures": {
        "title": "Приключения",
        "icon": "https://raw.githubusercontent.com/Nihronick/blackrose/main/assets/images/icons/class_etc/adventure.png",
    },
    "guild_guild": {
        "title": "Гильдия",
        "icon": "https://raw.githubusercontent.com/Nihronick/blackrose/main/assets/images/icons/class_etc/118.png",
    },
}

# ═══════════════════════════════════════════════════════
# 📂 ПОДКАТЕГОРИИ (с иконками)
# ═══════════════════════════════════════════════════════
SUBMENUS = {
    "cat_promoutes": [
        ("promo_ether", "Эфир", get_icon("promo_ether")),
        ("promo_black_mithril", "Чёрный Мифрил", get_icon("promo_black_mithril")),
        ("promo_demonite", "Демонит", get_icon("promo_demonite")),
        ("promo_dragonos", "Драгонос", get_icon("promo_dragonos")),
        ("promo_blood", "Кровь Великих", get_icon("promo_blood")),
        ("promo_frost", "Иней Войны", get_icon("promo_frost")),
        ("promo_nox", "Тёмный Нокс", get_icon("promo_nox")),
        ("promo_abyss", "Синяя Бездна", get_icon("promo_abyss")),
        ("promo_infinat", "Инфинат", get_icon("promo_infinat")),
        ("promo_cyclone", "Циклон", get_icon("promo_cyclone")),
        ("promo_ancient", "Эйшенткенаин", get_icon("promo_ancient")),
        ("promo_gigalor", "Гигалор", get_icon("promo_gigalor")),
    ],
    "info_general": [
        (
            "info_event",
            "Что покупать на ивенте?",
            (get_icon("pero_viol")),
        ),
        (
            "info_rage",
            "Как играть с Яростью?",
            (get_icon("info_rage")),
        ),
        (
            "info_ads",
            "Просмотр рекламы",
            (get_icon("info_ads")),
        ),
        (
            "info_pets",
            "Прокачка спутников",
            (get_icon("miho")),
        ),
        (
            "info_sword",
            "Меч душ и гравировка",
            (get_icon("soul_sword")),
        ),
        (
            "info_farm",
            "Фарм этапов",
            (get_icon("farm")),
        ),
        (
            "info_spirit",
            "Духи/Spirits",
            (get_icon("spirit_bo")),
        ),
    ],
    "adv_adventures": [
        (
            "adv_cave",
            "Учебная пещера",
            (get_icon("adv_cave")),
        ),
        (
            "adv_rift",
            "Межпространственный разлом",
            (get_icon("adv_rift")),
        ),
        (
            "adv_shelter",
            "Приют Спящего Пламени",
            (get_icon("adv_shelter")),
        ),
        (
            "adv_mind",
            "Золотой рудник",
            (get_icon("adv_mind")),
        ),
        (
            "adv_forest",
            "Лес циркуляции",
            (get_icon("adv_forest")),
        ),
    ],
    "guild_guild": [
        (
            "guild_wyvern",
            "Виверна",
            "https://raw.githubusercontent.com/Nihronick/blackrose/main/public/images/icons/guild_wyvern.png",
        ),
        (
            "guild_cooking",
            "Приготовление блюд",
            "https://raw.githubusercontent.com/Nihronick/blackrose/main/public/images/icons/guild_cooking.png",
        ),
    ],
}

# ═══════════════════════════════════════════════════════
# 📚 ГАЙДЫ (с иконками)
# 💡 ЗАМЕНЯЙТЕ "photo" НА URL (Imgur, Яндекс Диск, GitHub)
# ═══════════════════════════════════════════════════════
CONTENT = {
    # 🪨 ПРОМОУТЫ
    "promo_ether": {
        "title": "Эфир | Ether",
        "icon": get_icon("promo_ether"),
        "text": """**Характеристики:**
 Ориентировочный этап: **340 ± 5**
{{atk}}Атака: 100f (с 10 слотами скиллов и Яростью меньше)
{{crit}}Крит. урон: 20а
{{ds}}ДС: 3000
 Класс: {{class_c17}} - {{class_c19}}
 Меч: {{sword_m1}} или {{sword_opp}}
 Реликвии: 30-40
{{ellie}}**Спутники:**
Навык Элли на понижение ОЗ: 30-40
{{spirit_ark}}**Духи:**
{{spirit_noah}} Noah, {{spirit_loar}} Loar, {{spirit_sala}} Sala: 1-3{{starv2}}
💡 **Советы:**
 Фокус на атаке и критическом уроне""",
        "photo": [],  # 🔽 ЗАМЕНИТЕ НА URL: ["https://i.imgur.com/abc123.png"]
        "video": None,
        "document": None,
    },
    "promo_black_mithril": {
        "title": "Чёрный Мифрил | Black Mythril",
        "icon": get_icon("promo_black_mithril"),
        "text": """**Характеристики:**
 Ориентировочный этап: **460 ± 5**
{{atk}}Атака: 1.7-2g
{{crit}}Крит. урон: 25-28а
{{ds}}ДС: 4500-4800
 Класс: {{class_c18}} - {{class_c19}}
 Меч: {{sword_opp}}
 Реликвии: 40-50
 Навыки: ({{Blizzard}}/{{GigaImpact}}){{FlameSlash}}({{HellfireSlash}}/{{DemonHunt}}/{{Rave}}/{{FlowingBlade}}){{CurvedBlade}}
 ({{WrathOfGods}}/{{Rage}}){{Meditation}}{{SpeedSword}}{{EarthsWill}}{{BurningSword}}
{{ellie}}**Спутники:**
 Уровень понижения ХР мобов: 45+(Песня эльфов)
{{spirit_ark}} **Духи:**
 {{spirit_noah}}: 3{{starv2}}-5{{starv2}}, E3-5
 {{spirit_loar}}: 3{{starv2}}-5{{starv2}}, E3-5
 {{spirit_sala}}: миф, E1-2
💡 **Советы:**
 С Бредом у Sala можно больше E1
 Первый Бред = Менее 600х ХП
 Второй Гнев Богов = Около 300х ХП
 Второй Бред 175-150 ХП на убийство""",
        "photo": [],  # 🔽 Добавьте URL
        "video": None,
        "document": None,
    },
    "promo_demonite": {
        "title": "Демонит | Demon Metal",
        "icon": get_icon("promo_demonite"),
        "text": """**Характеристики:**
 Ориентировочный этап: **550 ± 5**
{{atk}}Атака: 60-65g
{{crit}}Крит. урон: 30-34а
{{ds}}ДС: 5000-5200
 Класс: {{class_c19}} - {{class_c20}}
 Меч: {{sword_opp}} 3-5{{starv2}}
 Реликвии: 40-50
 Навыки: {{SpeedSword}}{{EarthsWill}}{{CurvedBlade}}{{BurningSword}}{{Meditation}}
 {{WrathOfGods}}{{FlameSlash}}({{HellfireSlash}}/{{Blizzard}}/{{GigaImpact}}/{{FlowingBlade}}/{{Rage}}/{{Rave}}/{{DemonHunt}})
 💡 **Советы:**
 При открытие первого {{Rave}}, спамьте {{Rave}} чтобы получить открытие с {{spirit_sala}}, если не получается, перезапускайте игру, чем больше мобов убьете тем легче будет бой.
 Очень сложно получить 2 раза в конце {{DemonHunt}}, попробуйте рассчитать время так, чтобы активировать {{Meditation}} и {{Rave}}, за 23.5-21 {{WarthOfGods}} секунду. Жди {{spirit_noah}}, спамь {{DemonHunt}} и {{Rave}}
{{ellie}}**Спутники:**
 Навык Элли на понижение ХР мобов: 50+
{{spirit_ark}} **Духи:**
 {{spirit_noah}}: 3{{starv2}}-миф, E3-5
 {{spirit_loar}}: 3{{starv2}}-5{{starv2}}, E3-5
 {{spirit_sala}}: миф, E1-2
 **Камни навыков:**
 Вода, Камень, Огонь""",
        "photo": [],
        "video": None,
        "document": None,
    },
    "promo_dragonos": {
        "title": "Драгонос | Dragonos",
        "icon": get_icon("promo_dragonos"),
        "text": """**Характеристики:**
Ориентировочный этап: **610 ± 5**
{{atk}}Атака: 250-300g с орбом, без 700g
{{hp}}ХП: 4g
{{crit}}Крит. урон: 32-37а
{{ds}}ДС: 5800-6200
Класс: {{class_c19}}, {{class_c20}} без орба
Меч: {{sword_opp}} 3-5{{starv2}}, {{sword_awaken}}
Реликвии: 50-60
Навыки: 1.({{HellfireSlash}}{{FlowingBlade}}{{WrathOfGods}}{{Meditation}}{{Rage}}
{{FlameSlash}}{{SpeedSword}}{{EarthsWill}}{{CurvedBlade}}{{BurningSword}})

2.({{HellfireSlash}}{{FlowingBlade}}{{WrathOfGods}}{{Meditation}}{{Rave}}
{{FlameSlash}}{{SpeedSword}}{{EarthsWill}}{{CurvedBlade}}{{BurningSword}})

3.({{DemonHunt}}{{WrathOfGods}}{{Meditation}}{{Rave}}({{Blizzard}}/{{GigaImpact}})
{{FlameSlash}}{{SpeedSword}}{{EarthsWill}}{{CurvedBlade}}{{BurningSword}})
{{ellie}}**Спутники:**
Навык Элли на понижение ОЗ врагов: 50+
{{spirit_ark}} **Духи:**
{{spirit_noah}}: миф, E4-5
{{spirit_loar}}: миф, E4-5
{{spirit_sala}}: миф, E1-5
💎 **Камни навыков:**
Вода, Камень, Огонь
**Урон стихий:**
Огня и камня: 3-4к""",
        "photo": [],
        "video": None,
        "document": None,
    },
    "promo_blood": {
        "title": "Кровь Великих | RagnaBlood",
        "icon": get_icon("promo_blood"),
        "text": """**Характеристики:**
Ориентировочный этап: **700 ± 5**
{{atk}}Атака: 9h
{{crit}}Крит. урон: 35-40а
{{ds}}ДС: 8000-8400
Класс: {{class_c20}} 0-3{{starv2}}
Меч: {{sword_opp}} 5{{starv2}} / {{sword_awaken}} 0-4{{starv2}}
Реликвии: 50-60
Навыки:
1.({{Blizzard}}{{WrathOfGods}}{{DemonHunt}}{{CurvedBlade}}{{SpeedSword}}
{{BurningSword}}{{EarthsWill}}{{Meditation}}{{FlameSlash}}{{Rave}})

2.({{Blizzard}}{{WrathOfGods}}{{FlameSlash}}{{HellfireSlash}}{{Meditation}}
{{BurningSword}}{{EarthsWill}}{{CurvedBlade}}{{SpeedSword}}{{Rave}})

3.({{GigaImpact}}{{WrathOfGods}}{{FlameSlash}}{{HellfireSlash}}{{Meditation}}
{{BurningSword}}{{EarthsWill}}{{CurvedBlade}}{{SpeedSword}}{{Rave}})

4.({{GigaImpact}}{{WrathOfGods}}{{FlameSlash}}{{HellfireSlash}}{{Meditation}}
{{BurningSword}}{{EarthsWill}}{{CurvedBlade}}{{SpeedSword}}{{FlowingBlade}})
{{ellie}}**Спутники:**
Эльфийская песня: 70-80 лвл
Мудрость войны: 40-50
{{spirit_ark}} **Духи:**
{{spirit_noah}}: миф, E4-5
{{spirit_loar}}: миф, E4-5
{{spirit_sala}}: миф, E3-5
 💡 **Советы:**
 Фазовый сдвиг босса, повысит сопротивляемость и заблокирует 3 навыка игрока. Нажми {{Blizzard}}, чтобы остановить блокировку навыка.
**Урон стихий:**
Огня и Камня: 6-8к
**Камни навыков:**
Вода, Камень, Огонь""",
        "photo": [],
        "video": None,
        "document": None,
    },
    "promo_frost": {
        "title": "Иней Войны | WarFrost",
        "icon": get_icon("promo_frost"),
        "text": """**Характеристики:**
Ориентировочный этап: **770 ± 5**
{{atk}}Атака: 156h
{{hp}}{{hpr}}ХП/ХПР: минимум 630g/30g
{{crit}}Крит. урон: 63-67а
{{ds}}ДС: 12000-12500
Класс: {{class_c20}} 2-5{{starv2}}
Меч: {{sword_awaken}} 3-5{{starv2}} → {{sword_absolutev1}}
Реликвии: 60-70
Навыки:
1.({{BurningSword}}{{CurvedBlade}}{{EarthsWill}}{{SpeedSword}}{{HellfireSlash}}
{{WrathOfGods}}{{Meditation}}{{Rave}}{{FlameSlash}}{{Rave}})

2.({{BurningSword}}{{CurvedBlade}}{{EarthsWill}}{{SpeedSword}}{{LightningBody}}
{{WrathOfGods}}{{Meditation}}{{Rave}}{{FlameSlash}}{{Rave}}) если Адский удар слабый

3.({{BurningSword}}{{CurvedBlade}}{{EarthsWill}}{{SpeedSword}}{{RedLightning}}
{{WrathOfGods}}{{Meditation}}{{Rave}}{{FlameSlash}}{{Rave}}) если возвышены Молнии
{{ellie}}**Спутники:**
Эльфийская песня: 70+
Мудрость войны: 50+
{{spirit_ark}} **Духи:**
{{spirit_noah}}, {{spirit_loar}}, {{spirit_sala}}: все миф, E4-5
{{fam_na}}**Фамильяр:**
Необязательно, но делается дешево: 6{{starv2}}6{{starv2}}6{{starv2}} или 7{{starv2}}7{{starv2}}7{{starv2}}
{{fam_hi}}Хи/{{fam_ti}}Ти {{fam_ku}}Ку {{fam_na}}На
**Камни навыков:**
Вода, Земля, Огонь""",
        "photo": [],
        "video": None,
        "document": None,
    },
    "promo_nox": {
        "title": "Тёмный Нокс | Dark Nox",
        "icon": get_icon("promo_nox"),
        "text": """**Характеристики:**
Ориентировочный этап: **850 ± 5**
{{atk}}Атака: 4i
{{crit}}Крит. урон: 72а
{{ds}}ДС: 18500-19500
Класс: {{class_terra}} 0-5{{starv2}}
Меч: {{sword_awaken}} 3-5{{starv2}} → {{sword_absolutev1}} 0-3{{starv2}}
Реликвии: 60-70
Навыки:
Если были возвышены Молнии и используй {{FlowingBlade}} если {{FlameSlash}} очень хорошо прокачен
1.{{FlameSlash}}({{HellfireSlash}}/{{RedLightning}}/{{FlowingBlade}}){{DancingWaves}}
({{Blizzard}}/{{GigaImpact}}){{Meditation}}{{WrathOfGods}}{{CurvedBlade}}{{EarthsWill}}{{SpeedSword}}{{BurningSword}}

2.({{FlameSlash}}{{Rave}}{{DancingWaves}}({{Blizzard}}/{{GigaImpact}}){{Meditation}}
{{WrathOfGods}}{{CurvedBlade}}{{EarthsWill}}{{SpeedSword}}{{BurningSword}}) если сможешь затаймить {{WrathOfGods}} + Бред под {{spirit_noah}}

{{ellie}}**Спутники:**
Эльфийская песня: 80+
Мудрость войны: 60+
{{spirit_ark}} **Духи:**
{{spirit_noah}}, {{spirit_loar}}, {{spirit_sala}}: все миф, E5
{{fam_na}}**Фамильяр:**
{{fam_hi}}/{{fam_ti}}/{{fam_je}}|{{fam_ku}}|{{fam_na}}/{{fam_leon}}: 7{{starv2}}7{{starv2}}7{{starv2}}
Используй самую сильную доступную тебе комбинацию
**Камни навыков:**
Вода, Камень, Огонь
💡 **Важно:**
На этом промоуте игроки могут делать больший упор в меч или в класс. Если у вас условный сид, то меч будет хуже. Также с реликвиями: если меньше крита, то больше атаки. Не обязательно делать всё так же!""",
        "photo": [],
        "video": None,
        "document": None,
    },
    "promo_abyss": {
        "title": "Синяя Бездна | Blue Abyss",
        "icon": get_icon("promo_abyss"),
        "text": """**Характеристики:**
Ориентировочный этап: **955 ± 5**
{{atk}}{{crit}}Атака и крит.урон: ~150i с 200а ИЛИ 180-200i с 150а
{{hp}}ХП: минимум 310h и около 18h РХР
{{ds}}ДС: 29000-31000
Класс: {{class_terra}} 3-5{{starv2}}, {{class_sid}}
Меч: {{sword_absolutev1}} 3-5{{starv2}} → {{sword_absolutev2}}
Реликвии: 80-100
Навыки:
1.({{FlameSlash}}{{HellfireSlash}}{{DancingWaves}}{{Blizzard}}{{Meditation}}
{{WrathOfGods}}{{CurvedBlade}}{{EarthsWill}}{{SpeedSword}}{{BurningSword}})

2.({{FlameSlash}}{{RedLightning}}{{DancingWaves}}{{Blizzard}}{{Meditation}}
{{WrathOfGods}}{{CurvedBlade}}{{EarthsWill}}{{SpeedSword}}{{BurningSword}}) Если были возвышены Молнии

3.({{FlameSlash}}{{Rave}}{{DancingWaves}}{{Blizzard}}{{Meditation}}
{{WrathOfGods}}{{CurvedBlade}}{{EarthsWill}}{{SpeedSword}}{{BurningSword}}) если сможешь затаймить {{WrathOfGods}} + Бред под {{spirit_noah}}
{{ellie}}**Спутники:**
Эльфийская песня: 100 лвл
Мудрость войны: 80+
{{spirit_ark}} **Духи:**
{{spirit_noah}},{{spirit_loar}}, {{spirit_sala}}: все миф, E5
{{fam_na}}**Фамильяр:**
{{fam_hi}}/{{fam_ti}}/{{fam_je}}|{{fam_ku}}|{{fam_na}}/{{fam_leon}}: 7{{starv2}}
💡 **Советы:**
Торнадо уменьшает время действия навыков при каждом их использовании(отключи автоматический режим)
Мощная атака, которая скорее всего убъет вас с одного удара(танцующие волны или оглушение помогут отсрочить)
**Элементальный урон:**
Огня: 14-15а
**Камни навыков:**
Вода, Камень, Огонь""",
        "photo": [],
        "video": None,
        "document": None,
    },
    "promo_infinat": {
        "title": "Инфинат | Inflnat",
        "icon": get_icon("promo_infinat"),
        "text": """**Характеристики:**
Ориентировочный этап: **1020 ± 5**
{{atk}}Атака: 3.5j-3.7j
{{hp}}{{hpr}}ХП/ХПР: 4.5i/230h
{{crit}}Крит. урон: 210а-220а
{{ds}}ДС: 30000-35000
Класс: {{class_sid}} 0-5{{starv2}}
Меч: {{sword_absolutev2}} 3-5{{starv2}} → {{sword_immortal}}
Реликвии: крит, урон 100
Навыки:
1.({{FlameSlash}}({{HellfireSlash}}/{{RedLightning}})({{Blizzard}}/{{LifeMana}}){{FlowingBlade}}{{Meditation}}
{{Meditation}}{{WrathOfGods}}{{CurvedBlade}}{{EarthsWill}}{{SpeedSword}}{{BurningSword}}

2.({{FlameSlash}}({{HellfireSlash}}/{{RedLightning}}){{FlowingBlade}}{{Rave}}{{Meditation}}
{{WrathOfGods}}{{CurvedBlade}}{{EarthsWill}}{{SpeedSword}}{{BurningSword}}) Если сможешь убить фазу 2 во время Бреда, чтобы мгновенно убить фазу 3 с Бреда

{{ellie}}**Спутники:**
Эльфийская песня: 100 лвл
Мудрость войны: 100 лвл
{{spirit_ark}} **Духи:**
{{spirit_noah}}, {{spirit_loar}}, {{spirit_sala}}: все миф, E5
{{fam_na}}**Фамильяр:**
{{fam_hi}}/{{fam_ti}}/{{fam_je}}|{{fam_ku}}|{{fam_na}}/{{fam_leon}}: 7{{starv2}}
**Элементальный урон:**
Огня: 18а+
Земли: 15а+
**Камни навыков:**
Вода, Камень, Огонь
💡 **Советы:**
Во время {{WrathOfGods}} чтобы таймер не был потрачен в пустую из-за отбрасывания.
Используйте {{spirit_noah}} + {{Rave}}, активируй Бред раньше обычного, т.к отбрасывание босса на второй фазе не позволит добить его на третьей фазе с помощью полностью заряженного Бреда.
💡 **Примечание:**
У кого-то может быть наоборот: есть нова, но нет фулл меча""",
        "photo": [],
        "video": None,
        "document": None,
    },
    "promo_cyclone": {
        "title": "Циклон | Ciclos",
        "icon": get_icon("promo_cyclone"),
        "text": """**Характеристики:**
Ориентировочный этап: **1120 ± 5**
{{atk}}Атака: 290j-320j
{{crit}}Крит. урон: 235а-245а
{{ds}}ДС: 48000-53000
Класс: {{class_sid}} 3-5{{starv2}}, {{class_nova}}
Меч: {{sword_absolutev2}} 3-5{{starv2}} → {{sword_immortal}}
Реликвии: крит, урон 100
Навыки:
1.({{CurvedBlade}}{{BurningSword}}{{FlameSlash}}{{EarthsWill}}{{StrongCurrent}}
{{WrathOfGods}}{{HellfireSlash}}{{DemonHunt}}{{Meditation}}{{Rave}})

2.({{CurvedBlade}}{{BurningSword}}{{GigaStrike}}{{EarthsWill}}{{StrongCurrent}}
{{WrathOfGods}}{{Rage}}{{DemonHunt}}{{Meditation}}{{Rave}})
{{ellie}}**Спутники:**
Эльфийская песня: 100 лвл
Мудрость войны: 100 лвл
{{spirit_ark}} **Духи:**
{{spirit_noah}}, {{spirit_loar}}, {{spirit_sala}}: все миф, E5
{{fam_na}}**Фамильяр:**
{{fam_hi}}/{{fam_ti}}/{{fam_je}}|{{fam_ku}}|{{fam_na}}/{{fam_leon}}: 7{{starv2}}
**Элементальный урон:**
Огня и Камня: 30а-33а
**Камни навыков:**
Вода, Камень, Огонь""",
        "photo": [],
        "video": None,
        "document": None,
    },
    "promo_ancient": {
        "title": "Эйшенткенаин | Ancient Canine",
        "icon": get_icon("promo_ancient"),
        "text": """ ⚠️ **Дисклеймер:**
Урон, получаемый из статов ниже, непосредственно связан с самой проходкой. При других прожатиях может понадобиться больше урона.
**Характеристики:**
Ориентировочный этап: **1190-1200 ± 5**
Без фамика 8{{starv2}}8{{starv2}}8{{starv2}} проходится уже на 1200
{{atk}}Атака: 8.5k-9k
{{crit}}Крит. урон: 280а-300а
{{ds}}ДС: 70000-75000
Класс: {{class_sid}} 4-5{{starv2}}, {{class_nova}}
Меч: {{sword_absolutev2}} 4-5{{starv2}} → {{sword_immortal}}
Реликвии: 100 крит, урон
Навыки:
1.({{BurningSword}}{{EarthsWill}}{{CurvedBlade}}{{SpeedSword}}({{HellfireSlash}}/{{LightningStroke}}/{{RedLightning}}/{{DemonHunt}})
({{GigaImpact}}/{{Blizzard}}){{WrathOfGods}}{{Meditation}}{{Rave}}{{FlameSlash}})
{{ellie}}**Спутники:**
Эльфийская песня: 100
Мудрость войны: 100
{{spirit_ark}} **Духи:**
{{spirit_sala}} (в первом слоте!), {{spirit_noah}}, {{spirit_loar}}: все миф 2-5{{starv2}}, либо иммортал, E5
💡 **Советы:**
Вариант прохождения: Жмите {{Blizzard}} затем {{Meditation}}. Ждите когда {{WrathOfGods}} не достигнет значения 8.2-8.6 затем {{Rave}}.
Босс отбросит назад, как только вы вернетесь должны получить {{spirit_sala}} и жмите {{Rave}}, хп у босса дожно остаться примерно 769х.
После {{Rave}}, жмите {{Blizzard}}. {{Meditation}} - сохрани до пояление {{WrathOfGods}}.
{{Blizzard}} Во время зарядки босса(желтая полоска) у вас будет время восстановится {{Meditation}}.Жми {{Meditation}} + {{Rave}} как только будут готовы, должен прокнуть {{spirit_sala}}.
Хп босса должно достигнуть 400х. 
{{Blizzard}} Во время зарядки босса(желтая полоска) у вас будет время восстановится {{Meditation}}.
После отбрасывания необходимо активировать умение {{Meditation}} в нужный момент, иначе перезарядка вашего {{WarthOfGods}}{{Rave}} сбросится до 0. Рассчитай время активации так, чтобы пламя обтекало ваш навык, активируй его после того, как оно достигнет верхнего угла значка.
Если вы правильно рассчитаете время, вы почти у цели. Подождит, пока {{Meditation}} будет готов, и активируй его. {{Rave}} + Фамильяр + {{Blizzard}}.
Когда ты используешь {{Rave}} у босса должно быть 125х и тогда ГГ.
{{fam_na}}**Фамильяр:**
Так как босс имеет стихию Огня, желательно иметь А (фамильяр)
Или ХИКУНА: все 7{{starv2}} и выше
**Камни навыков:**
Вода, Камень, Ветер
**Элементальный урон:**
Огня: 35-40а
Ветра: 30а+
Воды: 25а+ (если используете А)
Земли: 35-40а (если используете Охоту на демонов)""",
        "photo": [],
        "video": None,
        "document": None,
    },
    "promo_gigalor": {
        "title": "Гигалор | Gigarock",
        "icon": get_icon("promo_gigalor"),
        "text": """**Характеристики:**
Ориентировочный этап: **1300 ± 5**
{{atk}}Атака: 350k с яростью / 380k без ярости
{{hp}}{{hpr}}ХП/ХПР: если без ярости - неважно / с яростью желательно более 500g
{{crit}}Крит. урон: 350а-370а
{{ds}}ДС: 100000+
Класс: {{class_nova}}
Меч: {{sword_immortal}}
Реликвии: 100
{{ellie}}**Спутники:**
Эльфийская песня: 100 лвл
Мудрость войны: 100 лвл
{{spirit_ark}} **Духи:**
{{spirit_noah}}, {{spirit_loar}}, {{spirit_sala}}: все миф-имм, E5
{{fam_na}} **Фамильяр:**
ХИКУНА: 8{{starv2}}, 8{{starv2}}, 8{{starv2}}
**Камни навыков:**
Вода, Земля, Огонь
💡 **Примечание:**
Статы максимально примерные! У кого-то может не быть 8 фамильяра или высокого уровня 🔥 или других баффающих навыков.""",
        "photo": [],
        "video": None,
        "document": None,
    },
    # 📜 ОБЩАЯ ИНФОРМАЦИЯ
    "info_event": {
        "title": "Что покупать на ивенте?",
        "icon": get_icon("pero_viol"),
        "text": """**Что покупать на ивенте?**
📌 Приоритет 1: {{legendary_spirit}}Легендарный дух
📌 Приоритет 2: {{random_epic_spirit}}3 эпических духа
📌 Приоритет 3: {{legendary_skill}}До черного мифрила можете покупать легендарный навык({{Meditation}}Медитация,{{HellfireSlash}}Адский удар,{{Rage}}Ярость)
📌 Приоритет 4: Бери навыки РЕДКИЕ приоритет будет на картинке
📌 Приоритет 5: Зеленые перья{{pero_berez}} и фиолетовые{{pero_viol}} - это только в том случае, когда редкие навыки уже заполнены.
❗️❗️❗️Не стоит менять на АЛМАЗЫ, только покупка по приоритету""",
        "photo": ["https://raw.githubusercontent.com/Nihronick/blackrose/main/assets/guides/event.jpg"],
        "video": None,
        "document": None,
    },
    "info_rage": {
        "title": "Как играть с Яростью?",
        "icon": get_icon("Rage"),
        "text": """Обучающее видео, смотрите на тайминги нажатия кнопок""",
        "photo": [],
        "video": ["https://raw.githubusercontent.com/Nihronick/blackrose/main/assets/guides/rage1.mp4","https://raw.githubusercontent.com/Nihronick/blackrose/main/assets/guides/rage2.mp4"],  # 🔽 Добавьте URL видео
        "document": None,
    },
    "info_ads": {
        "title": "Просмотр рекламы",
        "icon": get_icon("info_ads"),
        "text": """**Просмотр рекламы**
Мужик ну тут либо VPN, по-другому отдаешь свои кровные шекели в районе 500-700 рублей на покупку скипа""",
        "photo": [],
        "video": None,
        "document": None,
    },
    "info_pets": {
        "title": "Прокачка спутников",
        "icon": get_icon("miho"),
        "text": """**Прокачка спутников**
Просто, качай по приоритету указаному тут, с звездой прям нужно качать. Души на твое усмотрение, какой меч хочешь получать.
Инфо о спутниках...""",
        "photo": ["https://raw.githubusercontent.com/Nihronick/blackrose/main/assets/guides/companion.jpg"],
        "video": None,
        "document": [],  # 🔽 Добавьте URL документов
    },
    "info_sword": {
        "title": "Меч душ и гравировка",
        "icon": get_icon("soul_sword"),
        "text": """**Рекомендуется**
отдавать предпочтение высокоуровневым самоцветам Души, которые увеличивают коэффициент полезного действия оружия.,
Отдавайте предпочтение самоцветам души более высокой редкости (эпическим, легендарным, мифическим), чтобы получить более мощные дополнительные возможности.,
Постарайтесь собрать как можно больше драгоценных камней ATK (L-образной формы), не забывая при этом заполнять игровое поле.
Золотые блоки в начале и середине игры (I-образной формы) могут значительно увеличить ваш процент золота. Из-за этого может оказаться полезным сохранить 2 набора гравюр в начале игры: 1 для увеличения количества золотых монет (используется во время фермерства) и 1 для увеличения урона (используется во время толкания(стадии) или ежедневной работы по мере необходимости).,
Поздняя игра: Оружие Дущи уровня 1500+ может отдавать предпочтение критическим блокам из-за худшего вычисления блоков Atk,
как в начале игры: Если у вас уровень ниже Dragonos, крит может временно превышать ATK из-за вычисления.""",
        "photo": ["https://raw.githubusercontent.com/Nihronick/blackrose/main/assets/guides/soul_sword1.png",
            "https://raw.githubusercontent.com/Nihronick/blackrose/main/assets/guides/soul_sword2.png"],
        "video": None,
        "document": [],  # 🔽 Добавьте URL документов
    },
    "info_farm": {
        "title": "Фарм этапов",
        "icon": get_icon("farm"),
        "text": """**Фарм этапов**
Наиболее важными этапами являются этапы с 4mpw и 18mpw (после этапа 160):,
4mpw -> Эти этапы хороши для получения опыта и золота. Поскольку на нем меньше мобов, время прохождения будет меньше, так что вы сможете проходить более высокие уровни и получать больше опыта и золота.
18mpw -> Эти уровни хороши для сбора кубов, душ, снаряжения и алмазов. Хотя вам придется проходить более низкие уровни, чтобы у вас было приличное время прохождения (от 36 до 42 секунд), вы будете убивать гораздо больше монстров и, таким образом, получите больше ресурсов.
❗️Онлайн против оффлайна
Онлайн-фермерство лучше, чем оффлайн!
1 - У вас есть ограниченное количество часов, в течение которых вы можете находиться в автономном режиме (10 часов), поэтому, если вы забудете войти в систему и получить свои награды, вы перестанете получать их.
2 - Вы не получите бриллианты за ежедневные задания.
3 - Вы не получаете снаряжение с оффлайн-фермы.
4 - Стоимость кубов и душ на оффлайн-ферме намного ниже, чем на онлайн-ферме.
Но у оффлайн-фермы все же есть некоторые преимущества (особенно если вы только начали игру).:
После 160-го этапа вы получаете только 4 и 18 mpw соответственно, так что вы не можете выбирать, где фармить""",
        "photo": [],
        "video": None,
        "document": None,
    },
    "info_spirit": {
        "title": "Духи/Spirits",
        "icon": get_icon("spirit_noah"),
        "text": """{{spirit_ark}} **Духи - Оптимизация**
Оптимизация духа ранней игры,
Когда мы начинаем играть с духами, мы хотим, чтобы нашими статами были два духа, которых мы рано пробуждаем на А6 (игроки могут назвать это мифическим возвышением),и два духа с хорошими множителями навыков, так что в целом мы получаем максимальную выгоду при наименьшем количестве духов.
Поскольку характеристики всех 3-х экипированных духов усредняются, наличие 2-х высоко пробужденных духов компенсирует отсутствие характеристик у третьего улучшенного.

Мы берем по 1 духу из каждого элемента(огонь,земля,ветер,вода), чтобы оптимизировать наши ресурсы.

Оптимизация духов в середине игры,
Когда вы пополняете свой список духов и работаете над созданием Бессмертных духов, после достижения мифического уровня 12/12 вы можете начать работать над улучшениями.
Для бессмертных приоритет пробуждения меняется по мере расширения ваших возможностей.
A - возвышение духа, E - усиление духа(навыка)

{{fire}}Fire: Sala A6 -> Mum E5 -> Mum A6 ->  Bo A6 -> Mum A12 -> Sala E5 -> Sala A12 -> A12 Bo -> A18 Mum -> A18 Sala
{{earth}}Earth: Loar A6E5 -> Noah E5 -> Noah A6 > Radon A6 -> Noah A12 -> Loar A12 -> A12 Radon -> A18 Noah -> A18 Loar
{{wind}}Wind: Zappy A6E5 -> Kart A6 -> Herh A6 -> Zappy A12 -> Kart E5 -> A12 Kart -> A12 Herh -> A18 Zappy
{{water}}Water: Todd E5 -> Todd A6 -> Luga A6 -> Ark A6 -> Luga E5 -> Luga A12/Todd A12 -> A12 Ark -> A18 Luga -> A18 Todd

📌Немного про источник циркуляции
Основные духи, у которых сами поднимаем уровень.
Noah, Zappy, Loar, Todd, Radon, Mum
Присоединяем к фонтану
Nerh,Ark,Boo,Kart,Sala,Luga

❗️❗️❗️Пробуждение:
После 12/12 Мифических духов вы разблокируете его.
Выберите вариант с 4 равными полосами, пропустите при появлении запроса.
В нем есть несколько наград в виде бриллиантов, а статистика в целом повышается на 20%.""",
        "photo": [],
        "video": None,
        "document": None,
    },
    # 🌳 ПРИКЛЮЧЕНИЯ
    "adv_cave": {
        "title": "Учебная пещера",
        "icon": get_icon("adv_cave"),
        "text": """
**Навыки:**
Начало игры
{{FlameSlash}}{{HellfireSlash}}{{Meditation}}{{FireSword}}{{SpeedSword}}{{EarthsWill}}{{CurvedBlade}}{{BurningSword}} 

Середина игры +
{{FlameSlash}}{{HellfireSlash}}{{PillarofFire}} {{DemonHunt}} {{Meditation}} 
{{FlowingBlade}}{{SpeedSword}}{{EarthsWill}}{{BurningSword}}{{StrongCurrent}}/{{WrathOfGods}}

{{spirit_ark}}Духи:
{{spirit_luga}} {{spirit_mum}} {{spirit_zappy}} предпочтительнее использовать их, но {{spirit_radon}} {{spirit_kart}} также подойдет в этом подземелье, вы также можете использовать любого пробужденного духа, если заметите, что наносите больше урона. 

💡 **Советы:**
Эта сборка предназначена для земных этапов - 5/10 : от "Плавающего клинка" до "Огненного меча", так как без "Охоты на демонов" увеличение скорости атаки будет незначительным.
Зоны
(Зона 1 нейтральная -> Зона 2 Пожарная -> Зона 3 водная -> Зона 4 Ветровая -> Зона 5 Земная -> повторить.)""",
        "photo": [],
        "video": None,
        "document": None,
    },
    "adv_rift": {
        "title": "Межпространственный разлом",
        "icon": get_icon("adv_rift"),
        "text": """
{{spirit_ark}}Духи:
{{spirit_noah}}{{spirit_herh}} предпочтительно использовать их, но подойдут любые духи с более высоким пробуждением. 

Навыки:
Origin of Chaos Rave build
{{Rave}}{{Meditation}}({{FlameSlash}}/{{HellfireSlash}}/{{RedLightning}}/{{LightningStroke}}/{{PowerStrike}}/{{GigaStrike}})
{{WrathOfGods}}{{SpeedSword}}{{CurvedBlade}}{{BurningSword}}{{EarthsWill}}

Origin of Chaos Raveless build
Earlygame
{{FlowingBlade}}{{Meditation}}({{FlameSlash}}/{{HellfireSlash}}/{{RedLightning}}/{{GigaStrike}})
{{FireSword}}{{SpeedSword}}{{CurvedBlade}}{{BurningSword}}{{EarthsWill}}

Mid-lategame
{{FlowingBlade}}{{Meditation}}({{FlameSlash}}/{{HellfireSlash}}/{{RedLightning}}/{{LightningStroke}}/{{PowerStrike}}/{{GigaStrike}})
{{WrathOfGods}}{{SpeedSword}}{{CurvedBlade}}{{BurningSword}}{{EarthsWill}}

Если вы используете фамильяра, попробуйте использовать его против слабости стихий + {{spirit_noah}} + {{WrathOfGods}}
камни: земля/земля/огонь для ударов {{WrathOfGods}} и Огненных ударов

💡 **Советы:**
У босса Рифта есть несколько умений по очереди, оранжевая полоска под боссом указывает, когда умение будет активировано. 
Если босс использует атаку, активируйте "танцующие волны"({{DancingWaves}}), чтобы уклониться от нее, если это удобно, активируйте "танцующие волны", но навык все равно будет обновлен при следующей атаке. 
Если вы не хотите запускать Rift вручную, не используйте {{DancingWaves}}.""",
        "photo": [],
        "video": None,
        "document": None,
    },
    "adv_shelter": {
        "title": "Приют Спящего Пламени",
        "icon": get_icon("adv_shelter"),
        "text": """
Навыки: 
Раняя стадия - Средняя стадия игры {{HellfireSlash}}{{GigaStrike}}{{RedLightning}}{{Meditation}}{{SpeedSword}}{{EarthsWill}}{{CurvedBlade}}{{BurningSword}}

Поздняя стадия: {{FlameSlash}}{{RedLightning}}{{Blizzard}}{{WrathOfGods}}{{Meditation}}{{SpeedSword}}{{EarthsWill}}{{CurvedBlade}}{{BurningSword}}{{DancingWaves}}

Авто билд:{{HellfireSlash}}{{FlameSlash}}{{Meditation}}{{WrathOfGods}}{{FlowingBlade}}{{SpeedSword}}{{EarthsWill}}{{CurvedBlade}}{{BurningSword}}({{LifeMana}}/{{FireSword}})      

Ручной билд: {{FlameSlash}}{{GigaStrike}}{{DancingWaves}}{{WrathOfGods}}{{Rave}}{{Meditation}}{{SpeedSword}}{{EarthsWill}}{{CurvedBlade}}{{BurningSword}}

{{spirit_ark}}Духи: {{spirit_noah}}{{spirit_bo}} предпочтительнее использовать их, но подойдут любые духи с сильным пробуждением. 

💡 **Советы:**
Ранняя игра
Используйте: {{Blizzard}} чтобы оглушить дракона, когда он наносит ответный удар, и {{DancingWaves}} чтобы уклониться от него и других его атак.
Предлагаемые навыки являются минимальными и не учитывают ваш элементарный навык, урон от улучшенных навыков или что-либо еще, обязательно измените это в соответствии со своими потребностями.
Поздняя игра
При использовании поздней сборки {{Rave}} вы сможете: совершить {{Rave}} один раз в начале с помощью {{WrathOfGods}} и еще раз в конце с помощью {{WrathOfGods}} и {{spirit_noah}} не забудьте сохранить урон вашего фамильяра для финального рейва.
Босс нападет на вас ровно через 5 секунд и, скорее всего, убьет вас, если вы будете на низком уровне, поэтому используйте {{DancingWaves}}, чтобы избежать этой атаки""",
        "photo": [],
        "video": None,
        "document": None,
    },
    "adv_mind": {
        "title": "Золотой рудник",
        "icon": get_icon("gold"),
        "text": """**Золотой рудник**
Увеличьте свой максимальный этаж с 5 зоны, используя всего 1 перо.,
Производите фарм, используя 3 пера на повторе в зоне 1-4 зоны, чтобы вы могли уничтожить 90-95% врагов, когда пол имеет стихию земли (это, должно быть, труднее всего очистить, так как большинство навыков фермерства - это ветер).
Старайтесь фармить зону 2, но подойдет любая зона, кроме зоны 5. Зона 5 хуже подходит для фарма, потому что в ней меньше мобов, а значит, фарм принесет меньше ресурсов. Зона 1 даст немного меньше опыта, чем область 2.,
Старайтесь фармить нечетные этажи, где ресурсы увеличиваются. После закрытия 250-го этажа шахты выделите 4n+1 этаж, так как кубические усиления закончились.,
Проверьте свою ситуацию. Каждый раз, когда вы будете фармить закрытую шахту, ваш урон будет разным, поэтому больше ресурсов вы сможете получить на разных участках или этажах. Это простые рекомендации.,
лучшее время для запуска закрытой шахты - это когда вы можете накапливать ежедневные свитки + "горячее время выходных" + бонусы за события, получая 12-кратное золото и 6-кратный опыт.,
Использование усилителя событий для получения большего количества кубов в закрытой шахте бесполезно, потому что большинство кубов в Закрытой шахте добывается из сундука. Использование обычной ежедневной прокрутки кубов все еще может быть полезным, потому что мы обычно получаем больше кубов от мобов в закрытой шахте, чем от обычных 18mpw.
**Навыки:**
Early Game
{{Fulgurous}}{{Flamewave}}{{ThunderSlash}}{{LightningStroke}}{{Agile}}
{{BurningSword}}{{IronWill}}{{FireSword}}{{LifeMana}}/{{ManasBlessing}}

Mid Game
{{Fulgurous}}{{Supersonic}}{{Flamewave}}{{ThunderboltSlash}}{{RedLightning}}
{{Meditation}}{{Agile}}{{FireSword}}{{BurningSword}} 

End Game
{{Agile}}{{Supersonic}}{{RedLightning}}{{Blizzard}}{{Meditation}}
{{LightningBody}}{{Rage}}{{BurningSword}}{{FireSword}}{{Fulgurous}}

{{spirit_ark}}Духи:
Предпочтительнее использовать {{spirit_todd}}, {{spirit_mum}} и {{spirit_zappy}}. При необходимости, вы также можете использовать {{spirit_radnon}}, {{spirit_kart}}, или {{spirit_luga}} , или ваш высший пробужденный дух""",
        "photo": [],
        "video": None,
        "document": None,
    },
    "adv_forest": {
        "title": "Лес циркуляции",
        "icon": get_icon("adv_forest"),
        "text": """
Навыки:
Начало игры
{{LightningStroke}}{{RedLightning}}{{SpeedSword}}{{EarthsWill}}{{CurvedBlade}}{{BurningSword}} 

Середина игры
{{Supersonic}}{{LightningStroke}}{{RedLightning}}{{Meditation}}{{FireSword}}
{{SpeedSword}}{{EarthsWill}}{{CurvedBlade}}{{BurningSword}}{{StrongCurrent}}/{{LightningBody}}

Поздняя игра
{{Supersonic}}{{LightningStroke}}{{RedLightning}}{{Meditation}}{{Rage}}
{{SpeedSword}}{{EarthsWill}}{{CurvedBlade}}{{BurningSword}}{{FlowingBlade}}/{{LightningBody}}

Овладение навыком(Skill Mastery)
если {{FlameSlash}}{{HellfireSlash}} пробужден, используйте его вместо {{RedLightning}}{{LightningStroke}} 
если {{RedLightning}}{{LightningStroke}} пробудился, используйте его вместо {{FlameSlash}}{{HellfireSlash}}
Та же логика с Awaken 2
{{spirit_ark}}Духи:
Начало игры
{{spirit_zappy}}{{spirit_sala}}{{spirit_loar}}

Середина игры
{{spirit_zappy}}{{spirit_mum}}{{spirit_noah}} 

Конец игры
{{spirit_zappy}}{{spirit_mum}}{{spirit_kart}} 

{{spirit_zappy}}{{spirit_mum}}{{spirit_kart}} является предпочтительным на всех этапах игры, однако это требует больших вложений в духов. Вы можете использовать {{spirit_sala}} {{spirit_noah}} {{spirit_radon}} или любые другие высокоразвитые духи в качестве 2-го или 3-го слота. 
{{spirit_kart}} обгонит {{spirit_noah}} по производительности примерно на e3-4, если у вас улучшенный Карт, рекомендуется протестировать его на 3-м слоте.
{{spirit_radon}} может работать лучше при высоком пробуждении / усилении в качестве 3-го слота, если использовать {{FlameSlash}}{{HellfireSlash}}

💡 **Советы:**
В ручную {{Supersonic}} после победы над группой кристаллов, чтобы быстрее перейти к следующей группе, вы также можете использовать ручное заклинание{{Meditation}}, чтобы оптимизировать время действия баффов{{Supersonic}}{{Blizzard}}. 
Вы можете выйти из Леса без штрафных санкций, так что смело проверяйте свои возможности.""",
        "photo": [],
        "video": None,
        "document": None,
    },
    # 🛡 ГИЛЬДИЯ
    "guild_wyvern": {
        "title": "Виверна",
        "text": """ **Виверна - Гильдейское событие**
Событие для всех игроков Гильдии, в котором есть несколько этапов.
1. Распределение
2. Фарм ресурсов и готовка их
3. Битва с Виверной.
Почему это важно.
Чем выше находиться наша гильдия, тем больше ресурсов мы получаем индивидуально(от ранга гильдии), каждый кто внес наиболее больший вклад(индивидуальный: Готовка,Битва с виверной), получает ещё больше ресурсов согласно внутреннему рангу гильдии.""",
        "photo": [],
        "video": None,
        "document": None,
    },
    "guild_cooking": {
        "title": "Приготовление блюд",
        "icon": get_icon("guild_cooking"),
        "text": """🍲 **Приготовление блюд**
Приоритет еды, будет озвучен ГМ, т.к каждый сезон блюда меняются, но есть опредленные свойства блюд, которые не меняются.
9- еда дает больше ресурсов в дальнейшем фарме, готовится первоочередно.
Шашлык – увеличивает время действия баффа. (Примечание: В сезоне может название поменяться, и бафф)
Омурис – Увеличивает время боя в рейде. (римечание: В сезоне может название поменяться, и бафф)
Фруктовый салат / Жевательная паста – Уменьшает время восстановления навыка.
Бессмертный стейк - Увеличивает урон от виверн.
Бонусы стихий - Определите приоритетность элементов, которые вы будете использовать (огонь и земля для большинства игроков).
""",
        "photo": [],
        "video": None,
        "document": None,
    },
}


# ═══════════════════════════════════════════════════════
# 📊 СТАТИСТИКА
# ═══════════════════════════════════════════════════════
def get_stats():
    """Получить статистику гайдов"""
    total_guides = len(CONTENT)
    total_categories = len(MAIN_CATEGORIES)
    total_photos = sum(len(guide.get("photo", []) or []) for guide in CONTENT.values())
    total_videos = sum(len(guide.get("video", []) or []) for guide in CONTENT.values())
    total_documents = sum(len(guide.get("document", []) or []) for guide in CONTENT.values())

    return {
        "total_guides": total_guides,
        "total_categories": total_categories,
        "total_photos": total_photos,
        "total_videos": total_videos,
        "total_documents": total_documents,
        "guides_with_photos": sum(1 for guide in CONTENT.values() if guide.get("photo")),
        "guides_with_videos": sum(1 for guide in CONTENT.values() if guide.get("video")),
    }
