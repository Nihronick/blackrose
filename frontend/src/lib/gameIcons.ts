/**
 * BlackRose - Game Icons Registry
 * Synced with backend/icons.py — uses HuggingFace datasets CDN
 */

const BASE_URL = "https://huggingface.co/datasets/Nihronick/blackrose-media/resolve/main/icons";
const WSRV = "https://wsrv.nl/?url=";
const WSRV_OPT = "&output=webp&n=-1";

const _url = (path: string) => {
  // Encode each path segment separately (same as backend _url())
  const encoded = path.split("/").map(p => encodeURIComponent(p)).join("/");
  const raw = `${BASE_URL}/${encoded}`;
  if (path.endsWith(".gif")) return raw;
  return `${WSRV}${raw}${WSRV_OPT}`;
};

// Сокращенный список из backend/icons.py (основные категории)
export const GAME_ICONS: Record<string, string> = {
  // Классы
  "class_c17": _url("class_etc/c17.png"),
  "class_c18": _url("class_etc/c18.png"),
  "class_c19": _url("class_etc/c19.png"),
  "class19": _url("discord_migrated/1055586742952018001.webp"),
  "class_c20": _url("discord_migrated/1055586744231272498.webp"),
  "class_terra": _url("class_etc/Tera.png"),
  "class_nova": _url("class_etc/Nova.png"),
  "class_sid": _url("class_etc/Seed.png"),
  
  // Мечи
  "mythic1": _url("discord_migrated/1055585728140148747.webp"),
  "orr6": _url("discord_migrated/1055585923364048966.webp"),
  "orr12": _url("discord_migrated/1211887493360648263.webp"),
  "orr18": _url("discord_migrated/1237969505477722112.webp"),
  "orr24": _url("discord_migrated/1349197221496885309.webp"),
  "orb6": _url("discord_migrated/1378271019399385209.webp"),
  "orb12": _url("discord_migrated/1211868352184844328.webp"),
  "orb18": _url("discord_migrated/1378271093495697428.webp"),
  "orb24": _url("discord_migrated/1378271179365814425.webp"),
  
  // Спириты (Духи)
  "noah": _url("spirits/Noah.png"),
  "loar": _url("spirits/Loar.png"),
  "sala": _url("spirits/Sala.png"),
  "mum": _url("spirits/Mum.png"),
  "bo": _url("spirits/Bo.png"),
  "radon": _url("discord_migrated/1129588019763089488.webp"),
  "zappy": _url("spirits/Zappy.png"),
  "kart": _url("spirits/Kart.png"),
  "herh": _url("spirits/Herh.png"),
  "todd": _url("spirits/Todd.png"),
  "luga": _url("spirits/Luga.png"),
  "ark": _url("spirits/Ark.png"),
  
  // Скиллы
  "wb": _url("skills/WarriorBurn.png"),
  "warrior_burn": _url("skills/WarriorBurn.png"),
  "rage": _url("skills/Rage.png"),
  "rave": _url("discord_migrated/1055598059628789772.webp"),
  "blizzard": _url("skills/Blizzard.png"),
  "dh": _url("skills/DemonHunt.png"),
  "demonhunt": _url("skills/DemonHunt.png"),
  "lb": _url("skills/LightningBody.png"),
  "lightning_body": _url("skills/LightningBody.png"),
  
  // Ресурсы
  "diamond": _url("class_etc/diamond.png"),
  "gold": _url("class_etc/gold.png"),
  "gem": _url("class_etc/gem.png"),
  "fire": _url("class_etc/FIRE_GEM.png"),
  "water": _url("class_etc/luna_gem.png"),
  "earth": _url("class_etc/zeke_gem.png"),
  "wind": _url("class_etc/ellie_gem.png"),

  // Прочее
  "br": _url("class_etc/BR.png"),
  "relic": _url("class_etc/relic.png"),
  "cube": _url("class_etc/cube.png"),
};

// Регистронезависимый поиск
const LOWER_ICONS = Object.fromEntries(
  Object.entries(GAME_ICONS).map(([k, v]) => [k.toLowerCase(), v])
);

export const getGameIconUrl = (name: string): string | null => {
  // Пытаемся найти по имени или по icon_ID
  const cleanName = name.replace(/^icon_/, "");
  return GAME_ICONS[name] || LOWER_ICONS[name.toLowerCase()] || 
         GAME_ICONS[cleanName] || LOWER_ICONS[cleanName.toLowerCase()] || null;
};
