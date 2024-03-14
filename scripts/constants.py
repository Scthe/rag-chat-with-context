WHITELISTED_TITLES__ = [
    "/lore",
    "The Shogun",
    # "Dvalin",
]
WHITELISTED_TITLES = [x.lower() for x in WHITELISTED_TITLES__]

SKIPPED_TITLES = [
    "Timeline",  # a lot of info, but very messy to actually get smething of value from it
    "Bounty/List",
    "Version",  # This is ALOT of text {separate router?}
    "Card)<",  # A LOT of TCG removed {separate router?}
    "Ley Line Disorder",
    "Ley Line Outcrop",
    "Soundtrack",  # :( {separate router?}
    "Special Program",  # {separate router?}
    "Glossary",
    "MiHoYo",
    "Fishing Point/",
    "/Voice-Overs",
    "/Gallery",
    "/Change History",
    "/Fishing Point/",
    "MiHoYo",
    "Blessing of the Welkin Moon",
    "Viewpoint/",
    "Tutorial/",
    "/Texts",
    "/Design",  # one for each region
    "Loading Screen/",
    "Genius Invokation TCG/",  # {separate router?}
    "Genius Invokation TCG",
    "The Shimmering Voyage Vol.3",
    "/Story",  # event stories
    "Wish/",
    "Labyrinth Warriors/",
    "Serenitea Pot/",
    "Developers Discussion",
    "Weapon EXP/",
    "Weapon/Level Scaling",
    "Weapon/Sub Stat Scaling",
    "ATK",
    "Shield/",
    "RES/",  # resistances
    "Elemental Reaction/",
    "Paimon Menu",
    "Photo Mode",
    "Genshin Impact × HEYTEA",
    "Furnishing Blueprint",
    "Restaurant",
    "Elemental Absorption",
    "Talent Level Increase",
    "Arena of Champions",
    "Elemental Node",
    "Teyvat",  # not parseable
    "Hilichurlian",
    "Interruption Resistance/",
    "Parametric Transformer",
    "Adventurer Handbook/",
    "Adventure Encounters",
    "Holiday Artwork",
    "Character Archive",
    "Spiral Abyss/Floors",
    "Map",
    "Aggravation/",
    "Ley Line Monolith",
    "Transport Balloon",
    "Wish",
    "Chat",
    "Monetization",
    "Request",
    "Expedition",
    "Sohreh",
    "Where Shadows Writhe",
    # "Web Event",
    # "Event",
    ### Years
    "2019",
    "2020",
    "2021",
    "2022",
    "2023",
    "2024",
    # "/Story",
    # "(Quest)",
    # "/Characters",  # characters that take part in quests
    "/Background",  # dev interview
    "Elemental Gauge Theory",
    "Character Introduction",
    "Out of Bounds",
    "Targeting",
    "Obstacle",
    "Controls",
    ### special:
    "Guizhong (Quest)",
    "While It's Warm",  # quest
    "Lil' Fungi's Fun-Tastic Fiesta",
    "Downtown",
    "Tower of Ipsissimus",
    "Internal Cooldown",
    "Notice Board",
    "Noticeboard",
    "Bulletin Board",
    "Collected Miscellany",  # article about youtube videos
    "Attribute Optimization",
    # "Ancient Log",
    "Wangshan Hall, Main Hall",
    "Shield/Enemy",
    "Yoriki Samurai",
    "Loot System",
    "Abyss Corridor",
    "Developer Insight",
    "Inventory",
    "Battle Pass",
    "Screen",
    "Account",
    "/Menu",
    "Rhythm Game",
    "Genshin Symphony",
    "HoYoLAB",
    "HOYO-MiX",
    "Wanderlust Invocation",
    "Error",
    "Archive Mechanicus",
    "Orthant of Wishes",
    "Internal Cooldown",
    "Shadows Amidst Snowstorms",
    "An Unforgettable Journey",
    "Replication",
    "Klee Mail",
    "The Rusty Rudder",
    "A Study in Potions",
    "Comics",
    "Legend of the Vagabond Sword",
    "A Journey of Art and Heritage",
    "Forest of Jnana and Vidya",  # 4th OST
    "Genshin Impact × Pizza Hut",
    "Genshin Impact × Razer Collaboration",
    "Notices",
    "UID",
    "Frozen",
    "Random Event",
    "Quick Start",
    "Normal Attack",
    "Genshin Impact × OnePlus",
    "At Tunnel's End, Light",
    "CRIT Hit",
    "Damage",
    "Damage Sequence",
    "Elemental Resonance",
    "Hitlag",
    "Materials Office",
    "5-Star Weapons",
    "To the Church's Free Spirit",
    "Streamer Partner Program",
    "La vaguelette",
    "Duelist Rising",
    "Like Rhyme and Song",
    "HP Loss",
    "Vacuum Field",
    "TCG Player's Manual",
    "Teyvat Food Notes",
    "Video",
    "Artifact/Occurrence",
    "NPC/Dialogue Reward",
    "Interruption ResistanceInterruption Resistance",
    "Character Detail",  # miHoYo blog posts
    "Weekly Boss",
    "Character Ascension Material",
    "Local Legend",
    # "Someone's Ledger",
    # "Wangshan Swordsman's Inscriptions",
    # "Wakamatsu",
    # "Delaroche's Bait",
    # "Mek",
    # "HoYoLAB/Paimon's Paintings",
    # "Jakob",  # some random dude has one of the longest articles?
    # "Energy/Data",
    # "Realm of Tranquil Eternity/Background",  # ost dev comments
]


SKIPPED_BASED_ON_TEXT = [
    ### Quests
    "Event Quest",
    "event World Quest",  # special for 'Drama Phantasmagoria: Tale of the Sword-Wielding Princess!'
    "events of the quest",
    "of the Archon Quests",  # they are sooo long
    "is the Archon Quest chapter",
    "unlocks the quests",
    "List of Quests",
    "quest of the",
    "is a Quest in",
    "is a Quest Item",  # not important anyway?
    "quest-exclusive NPC",  # removes a lot of minor NPCs
    "event-exclusive NPC",
    "are Quest Item",
    "hidden Quest Item",
    "quest-exclusive enemy",
    "is a World Quest in",
    "is a follow-up quest",
    "is a World Quest",
    "is a Quest Domain",
    "is a Random World Quest",
    "hidden World Quest",
    "is the only quest in",
    "is an Event Quest",
    "is the first part",
    "is the first act",
    "is the second part",
    "the second act of",
    "is a festival",
    "is the third part in the ",
    "is the third act of",
    "is the third part",
    "is the third part",
    "is the fourth part of",
    "is the fourth act",
    "is the fifth act",
    "fourth and final part of No Mere Stone",
    "is the last part of Of",
    "is a World Quest in",
    "is a follow-up quest",
    "a One-Time Domain",
    # constellations etc.
    "Level 1 Constellation",
    "Level 2 Constellation",
    "Level 3 Constellation",
    "Level 4 Constellation",
    "Level 5 Constellation",
    "Level 6 Constellation",
    # TCG
    "Character Card Elemental Burst",
    "Character Card Elemental Skill",
    "Character Card Normal Attack",
    "Card in Genius Invokation TCG",
    "Support Card in Genius Invokation TCG",
    #
    "is an Artifact in the set",
    "is an Artifact Piece",
    "is an Artifact Set",
    "is a Domain of Blessing",
    "is a Realm Layout",
    "is a limited time Gadget",
    "used to Weapon Ascension Materials",
    "set of interactables",
    "Rather Aged Notes",
    "is a soundtrack",
    "the event-exclusive",
    "is an advertisement board",
]

LINES_THAT_ONLY_TAKE_FIRST_SENTENCE = [
    ### Events
    "Quests and Events",
    "Hangout Event:",
    "in a Spring Breeze",
    "is the second act of Windblume",
    "Spring Breeze event",
    "is a festival",
    "is a Recurring Event",
    ### World
    "Hidden Exploration Objective",
    "set of interactables",
    "Mining Outcrop Search",  # Mining Outcrop
    "Points of Interest",  # starts location details
    "Exploration",  # starts location details
    ### Weapons
    "-Star claymore",
    "-Star Catalyst",
    "-Star bow",
    "-Star sword",
    "-Star polearm",
    "is a Liyue polearm",
    "is a Liyue claymore",
    "is a Liyue catalyst",
    "is a Liyue bow",
    "-star Weapon Series",
    "type = Forging",
    "type = Crafting",
    "type = Converting",
    "How to Obtain",
    "Ascensions and Stats",
    ### Crafting materials
    "is a Character Ascension Material",  # {separate router? - materials/crafting}
    "is a weapon Ascension Material",
    "Character and Weapon Enhancement Material",
    "Weapon Enhancement Materials",
    ### Commisions
    "is a Daily Commission",
    "temporary daily commission",
    "is a repeatable Daily Commission",
    "is a basic daily commission",
    "is an NPC Daily Commission",
    "repeatable commission",
    "NPC Commission",
    "Daily Commission that ",
    ### not important items
    "soundtrack album",
    "-Star Character Outfit",
    "is a Character Outfit",
    "is a Furnishing",  # {separate router? - furnishing}
    "is a type of Ornamental Fish",
    "and an NPC located",
    "is an open-world NPC",
    "is a type of fish",
    "Alternate Character Outfit",
    "is a message board",
    "is a billboard",
    "is a food",
    "is an event item",
    "is an item in the",
    "is a Gadget",
    "is a Special Dish",
    "is a Gadget obtained",
    "are unlockable fast-travel points",
    "is a creatable Furnishing item",
    "is a Book Collection",
    "is a weekly Reputation Request",
    "interactable notes",
    "are a set of interactable notes",
    "is a set of interactable notes",
    "is a series of interactables",
    "are interactable items",
    "is an outdoor gift set",
    "is an indoor gift set",
    "is a special enemy",
    "is a Wind Glider",
    "is a Furnishing item",
    "is a Cooking Ingredient",
    "are a Cooking Ingredient",
    "is a Local Specialty",
    "are a Local Specialty",
    "is an Achievement",
    "is an item used",
    "is a quest reward",
    ### Rest
    "Archive Categories",  # archive
    "Shop Availability",  # https://genshin-impact.fandom.com/wiki/Mora
    "Damage Bonus",  # https://genshin-impact.fandom.com/wiki/Catalyze
    "Locations",
    "Ending Rewards",
    "an open-world NPC",
    "character_name",  # domain special chars.
    "Favorite Furnishing Sets",
    "Idle Quotes",
    "Phase 1",  # weekly bosses etc.
    "Ultimate Overlord's Mega Magic Sword",
    "Confessions of an Outlander",
    "Spring Breeze event",
    "How to Unlock",
    "Base Attribute",
    "Attribute Scaling",
    "Cumulative Stamina Bonus",
    "To Treat the Well-Meaning Well",
    "Stamina cost",
    "Challenge Features",
    "Electrograna can be leveled up and gain new abilities via",  # https://genshin-impact.fandom.com/wiki/Electrogranum
    # long texts
    "The Narzissenkreuz Adventure",
    "The Proscribed, Hidden in Plain Sight",
    "Dodo-King of the Sea: Lying in Wait",
    "Searching for Zhongli",  # Quest: The Fond Farewell
    "End of the Oneiric Euthymia Rules",  # Ei weekly boss
    "Entering the Golden House",  # skip dialogue in 'Heart of Glaze'
    "(Engage the Fatui)",  # Solitary Fragrance
    "(Approach the southern spot)",  # Equilibrium
    "Players will often find Common Enemies in the open world while exploring",
    "A Swordmaster's Path Is Paved With Broken Blades",
    "New Chronicles of the Six Kitsune",
    "Bounties can be done in Co-Op Mode",
]

SKIPPED_PARAGRAPHS__ = [
    "Other Languages",
    "Voice-Overs",
    "References",
    "Navigation",
    "Mail",
    "Change History",
    "Video Guides",
    "Gallery",
    "Soundtracks",  # location/boss soundtracks
    "Attribute Scaling",  # unparseable numbers
    "Advanced Properties",  # unparseable numbers
    "Abilities and Attacks",  # unparseable numbers
    "World Level and Ascension",  # unparseable numbers
    "Dialogue",  # useless text
    "=Dialgoue Set #1=",  # useless text
    "=Dialgoue Set #2=",  # useless text
    "Dialogue Set #1",
    "Dialogue Set #2",
    "Talk Dialogue",
    "Special Dialogue",  # useless text
    "Stats",  # unparseable numbers
    "Creation",  # furniture recipe
    "Trial Character",  # unparseable numbers
    "Location",
    "Gameplay Notes",
    "Steps",
    "Recipe",
    "Interactables",
    "Clementine Line",  # Fontaine public transport
    "Navia Line",  # Fontaine public transport
    "Personnel",  # Tenryou_Commission
    "Leaders",  # Tenryou_Commission
    "Military",  # Tenryou_Commission
    "Members",  # Sumeru_Akademiya
    "Quests and Events",
    "Character Appearances",
    "Shop",
    "First Time Completion Rewards",
    "Soundtracks",
    "Trust Rank",  # https://genshin-impact.fandom.com/wiki/Serenitea_Pot
    "Jar of Riches",
    "Teapot Traveling Salesman",
    "Co-Op Mode",
    "Guides",
    "Available Hangouts",
    "Rewards",
    "Trivia",  # a lot of non-in-game references
]
SKIPPED_PARAGRAPHS = [x.lower() for x in SKIPPED_PARAGRAPHS__]

IGNORED_TEMPLATE_PREFFIX = [
    "dicon",
    "dialogue start",
    "dialogue end",
    # Dialog voiceover .ogg file
    "a|vo",
    "other languages",
    "change history",
    "reflist",
    "enemy table",
    "drops",
    "collapsible",
    "wish list",
    "wishes by category table",
    "statuses by category table",
    "icon/ar exp",
    "icon/primogem",
    "ref/manga",
    "icon/mora",
    "world boss rewards",
    "assumed",
    "removed",
    "genius invokation tcg talent cards table",
    "1s",
    "2s",
    "3s",
    "4s",
    "5s",
    "code container",
    "keys",
    "subst:!",
    "toc limit",
    "cbt info",
    "event list",
    "currentversion",
    "versions",
    "trim",
    "gift shop history",
    "furnishings by category gallery",
    "Talent Upgrade/List",
    "Talent Upgrade/Cross Table",
    "shop/footer",
    "IsDesktop",
    "reset",
    "mc ",
    "Preview",
    "Character Ascensions/List",
    "SoundtrackTabs",
    "Soundtrack/Total",
    "artifact sub stats",
    "Soundtracks by Category",
    "Elemental Reaction Intro",
    "Transformative Reaction Damage",
    "Genius Invokation TCG",
    "characters by talent category list",
    "event rewards by version tables",
    "Artifact Main Stats",
    "Furnishing Sets by Category Table",
    "Icon/TCG",
    "regiontabs",
    "Event Rewards Table",
    "videos by category table",
    "wish featured history",
    "stubdialogue",
    "wish series by category table",
    "events by version tables",
    "Mails by Category Table List",
    "column/start",
    "DISPLAYTITLE:Sisi",
    "clr",
    "ko-rm",
    "subst:void",
    "Name Order",
    "Genesis Crystal Regional Comparison",
    "World Quest Series by Region List",
    "Lock",
    "Companion/Footer",
    "companion/header",
    "cite",
    "items by category table",
    "character talent materials",
    "character talent materials/ascension",
    "weapon ascension materials",
    "constellations scale by category table",
    "Heated Battle Mode History Table",
    "normal attack scaling",
    "charged attack scaling",
    "plunging attack scaling",
    "normal attack scaling/tartaglia",
    "normal attack scaling/raiden shogun",
    "charged attack scaling/tartaglia",
    "charged attack scaling/raiden shogun",
    "plunging attack scaling/raiden shogun",
    "reputation quests by region list",
    "Map",
    "story key",
    "talent table",
    "gadgets by category table",
    "Stub Dialogue",
    "Welcome",
    "Character List",
    "DiscordWidget",
    "Reset/Main",
    "Upcoming",
    "LastEdits",
    "Latest Videos",
    "Traveler Talents and Constellations",
    "Domains by Category Gallery",
    "Domain Levels/Mastery",
    "Domain Levels/Forgery",
    "ref/cs",
    "Category Total",
    "talent vo/traveler",
    "Current Event",
    "Paimon's Bargains Items",
    "characters by talent book",
    "Character Appearances",
    "books by publisher table",
    "quests by category table",
    "Spiral Abyss Blessings",
    "Achievement/Total",
    "EVT",
    "EventOver",
    "NameOrder",
    "Color Hydro DMG Bonus",
    "Lowercase Title",
    "Achievement/Primogems/Total",
    "Past Memories",
    "china only",
    "PAGENAME",
    "SpiralAbyssTabs",
    "Gnostic Hymn Reward List",
    "Sojourner's Battle Pass Reward List",
    "Trial Character/Event/Header",
    "Tocright",
    "Trial Character/Event/Footer",
    "Starglitter Exchange History",
    "ResistanceTabs",
    "formatnum",
    "DISPLAYTITLE:",
    "shop usage",
    "HistoryTabs",
    "characters by local specialty",
    "paimon's bargains history",
    "Under Construction",
    "Vendor",
    "loopogv",
    "SereniteaPotTabs",
    "DamageBonusTabs",
    "Talent VOs",
    "Related Items",
    "Introductory Note",
    "domain materials by weekday",
    "Recipes",
    "Wish History Table",
    "Furnishing/Total",
    "rubi hazura haneasobi",
    "alchemy recipes",
    "Dropped By",
    "Commission Rewards",
    "housingcompanion",
    "Files by Category Gallery",
    "ScalingTabs",
    "Domain by Weekday",
    "icon/quest",
    "tx",
    "Icons by Category",
    "Talent Upgrade",
    "Unofficial Translation",
    "Column/Start",
    "Column/End",
    "cards by category",
    "Hangout Event Endings",
    "shop/header",
    "LoadingScreenTabs",
    "shop availability",
    "Character Ascensions and Stats",
    "birthday intro",
    "verify",
    "craft usage",
    "tprgt story",
    "paimon's bargains",
    "test run",
    "blessing of the abyssal moon",
    "blessing of the abyssal moon schedule",
    "abyssal moon spire",
    "wish item",
    "gift shop",
    "assets/namecard",
    "paimon's paintings images",
    "thousandquestions",
    "tcg cost",
    "tcg health",
    "#dplvar:set",
    "sino",
    "character expression",
    "components by category gallery",
    "namecards by category gallery",
    "birthday artwork by year",
    "vo search by title",
    "combat",
    "Sold By",
    "Enemies by Category List",
    "Artwork",
    "Character Mentions",
    "Ascension Usage",
    "CharacterSystemTabs",
    "Locations Gallery",
    "subst:#tag:gallery",
    "talents scale by category table",
    "characters by ascension stat table",
    "Artifact List",
    "Files by Character Gallery",
    "locations by category gallery",
    "Cleanup",
    "Enemy Intro",
    "NPCs by Region List",
    "Talent Leveling Usage",
    "trials by character",
    "Quests and Events",
    "Quest Domains",
    # C'mon..
    "mails by category list",
    # Reference to particular voice file, no need for that
    "Ref/VO",
    # For russian names, e.g.
    # '{{Lang|Melnikov|ru=Мельников|ru_rm={{#invoke:ru-rm|main|Мельников}}}}'
    "#invoke",
    # datatables
    # Would require dumping HTML. Against TOS
    "#DPL:",
    "#dpl:",
    # some dynamic parsing, we could parse if's but...
    # Would require dumping HTML. Against TOS
    "#ifexpr:",
    # only used with '#if:IsDesktop|...'
    "#if:",
    # not important usually
    "#lst:",
    # variables
    "#vardefine:",
    "#var:",
    # ???
    "#evt:",
    "#time:",
    "#subst:",
    "#expr:",
    # ???
    ":manet",
    "#evl:uiam8zl4af8",
    # misc
    "genius invokation tcg stages/detailed",
    "meta",
    "ogvgallery",
    "ordermethod",
    "size",
]

TEMPLATE_TYPE_USE_TEXT__ = [
    "ref/quest",
    "ref/food",
    "ref/artiset",
    "ref/wildlife",
    "ref/outfit",
    "ref/mail",
    "ref/talent",
    "ref/vp",
    "ref/domain",
    "ref/enemy",
    "ref/heo",
    "ref/arti",
    "ref/weapon",
    "ref/item",
    "ref/furnishing",
    "enemy stats",
    "Rubi",
    "key",
    "icon",
    "achievement",
    "fishing point",
    "Domain Enemies",
    "for",
    "Hangout Event Rewards",
    "Hangout Event Endings",
    "hangout ending",
    "ref/bb",
    "constellation lore",
    "Constellation Lore",
    "tcg summon",
    "ll",
    "cutscene description",
    "Battle Pass Missions",
    "Energy Drops",
    "main",
    "achievement/primogems",
    "Highlight",
    "floral jelly",
    "wish pool",
    "Hangout Branch",
    "Statue of The Seven",
    "environmental damage",
    "location",
    "Item Description",
    "hilidream",
    "pyro",
    "Material Quality",
    "cryo",
    "Hatnote",
    "Ref/Loading",
    "Not a typo",
    "bp talent books text",
    "namecard",
    "see also",
    "Enemy Attacks/Header",
    "Disambiguation",
    "Wood",
    "artifact list",
    "elements",
    "not a typo",
    "cancelled",
    "Star",
    "obf",
    "special dish",
    "zh",
    "fr",
    "it",
    "Wet",
    "w",
    "ko",
    "de",
    "es",
    "Shield Gauge Data Row",
    "pt",
    "tr",
    "nowrap",
    "'",
    "s",
    "t",
    "f",
    "obfuscate",
    "cx",
    "tt",
    "ru",
    "id",
    "vi",
    "lang",
    "enemies",
    "Effect",
    "constellations table",
    "dpl furnishing categories",
    "Weekly Boss Rewards",
    "turnarounds",
    "stub",
    "anemo",
    "Further",
    "pneuma",
    "dendro",
    "aura",
    "geo",
    "anchor",
    "transformative reaction damage",
    "ach",
    "electro",
    "Frozen",
    "hydro",
    "Physical",
    "Ousia",
    "artifact lore",
    "artifactlore",
    "talent vo",
    "featured",
    "local specialty",
    "No Selflink",
    # important ones (big text):
    "about",
    "quest",
    "color",
    "tutorial",
    "description",
    "transclude",
    "enemy",
    "recipe",
    "weapon ascensions and stats",
    "enemy attacks",
    "quest description",
    "talent note",
    "advanced properties",
    "talent scaling",
    "attribute",
    "ar",
    "black screen",
    "trial character",
    "event rewards",
    # "character story",
    "battle pass rewards",
    "trial character/event",
    "bounty",
    "location intro",
    "wish",
    "column",
]

TEMPLATE_TYPE_USE_TEXT = [x.lower().strip() for x in TEMPLATE_TYPE_USE_TEXT__]
