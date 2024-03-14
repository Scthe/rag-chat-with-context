from termcolor import colored
import re

from constants import (
    IGNORED_TEMPLATE_PREFFIX,
    # LINES_THAT_FORCES_SKIP_ARTICLE,
    LINES_THAT_ONLY_TAKE_FIRST_SENTENCE,
    SKIPPED_PARAGRAPHS,
    TEMPLATE_TYPE_USE_TEXT,
)


def cleanup_links(matchobj):
    text = matchobj.group(1)

    # lanugage/file links e.g. [[fr:Beidou/Histoire]]
    if text.startswith("File:"):
        return ""

    # Remove ':Category:' from:
    # [[:Category:Tall Female Characters|tall female]]
    text = re.sub(r":.+:", "", text)

    text = text.replace("|", " ")
    text = text.replace("#", " ")
    # There are 7 matches e.g. '/Mondstadt Mondstadt' or '/Story Conch Retrospection'
    text = text.replace("/", " ")

    # check for malformed link after processing
    if not re.match(r"[\w\"' \?\.\(\)]+", text):
        print(colored("Suspicious link:", "red"), f"'{text}'")
    # print(matchobj.group(1), "->", text)
    return text


def parse_template_kv(text):
    """
    RAW:
    {{Domain Levels/Blessing
    |level=4
    |sets=Brave Heart,Martial Artist,Tenacity of the Millelith,Pale Flame
    }}
    BUT WE ALREADY PARSED IT TO:
    level=4|sets=Brave Heart,Martial Artist,Tenacity of the Millelith,Pale Flame
    """
    parts = text.split("|")
    result = {}
    for p in parts:
        m = re.match(f"(.+)=(.+)", p)
        if not m:
            result[""] = p
        else:
            k = m.group(1).strip()
            result[k] = m.group(2)
    # print(result)
    return result


def concat_kv(kv, filter_fn):
    keys_ok = [x for x in kv.keys() if filter_fn(x)]
    # print(keys_ok)
    vals = [kv[x] for x in keys_ok]
    # print(len(vals))
    return "\n".join(vals)


def cleanup_templates(page_title, matchobj):
    text = matchobj.group(1)
    textLC = text.lower()
    # print(colored(text[:10], "yellow"), f"'{text}'")

    is_ok = True
    for fp in IGNORED_TEMPLATE_PREFFIX:
        fp = fp.lower()
        is_ok = is_ok and not textLC.startswith(fp)
    if not is_ok:
        # print(f'ignore: "{text}"')
        return ""

    if textLC in ["!", "'|b", "cx", "f"]:
        return ""
    if textLC.startswith("code row"):
        return ""

    if textLC == "lmdash":
        return "-"

    # Inside dialogue e.g.
    # '#ifeq:PAGENAME|The Rhythm that Leads to the Gloomy Path|It is because of the Tree of Dreams.'
    if textLC.startswith("#ifeq"):
        return text.split("|")[1]

    # some list
    if textLC.startswith("#lsth"):
        return ", ".join(text[6:].split("|"))

    # tabs
    if textLC.startswith("#tag:tabber|"):
        return text[len("#tag:tabber|") + 1 :]

    # additional note ref
    if textLC.startswith("#tag:ref|"):
        # print("|||", text)
        result = text[len("#tag:ref|") : -len("|group=Note")]
        # print("|||", result)
        return result

    parts = text.split("|")
    if len(parts) == 1:
        type = text.strip().lower()
    else:
        # type - special expression e.g. Quote:
        # '{{Quote|Captain of her crew, The Crux. She's quite an unbound and forthright woman.|In-game character attributes and profile page text}}
        type = parts[0].lower().strip()
        text = "|".join(parts[1:])

    if (
        "navbox" in type
        or "infobox" in type
        or "list" in type
        or "table" in type
        or "tabs" in type
    ):
        return ""

    # take middle part:
    if type in ["quote"]:
        text = "|".join(parts[1:-1])
        # print(colored(type, "green"), f"'{text}'")
        return text

    if type.startswith("subst:"):
        return page_title

    if type == "icon/stars":
        return f"{text} stars"
    if type == "a":
        return ""  # audio

    if type == "domain levels/blessing":
        return parse_template_kv(text).get("sets", "")
    if type == "projection of elemental symbol info":
        return parse_template_kv(text).get("outfit", "")
    if type == "mail":
        return parse_template_kv(text).get("text", "")
    if type == "teyvatquest":
        return parse_template_kv(text).get("title", "")
    if type == "me":
        return parse_template_kv(text).get("id", "")
    if type == "vo" or type.startswith("vo/"):
        return ""
    if type == "assets":
        return ""
    if type == "characters by boss":
        kv = parse_template_kv(text)
        return f"bosses={kv.get('bosses', '-')}\nmaterials={kv.get('materials', '-')}"
    if type == "glowing ornament info":
        kv = parse_template_kv(text)
        return kv.get("outfit", "") + ":" + kv.get("outfit", "")
    if type == "furnishing mentions":
        kv = parse_template_kv(text)
        return kv.get("name", "") + "," + kv.get("", "")
    if type == "artifact set":
        text = text.replace("show_caption=1", "")
        return text.replace("|", " ")
    if type == "wish item pool data":
        kv = parse_template_kv(text)
        return kv.get("character", kv.get("weapon", ""))
    if type == "elemental shield data":
        text = text.replace("|noec=1", "")
        return text.replace("|", " ")
    if type == "official introduction":
        kv = parse_template_kv(text)
        return kv.get("character", "") + ":" + kv.get("title", "")
    if type == "companion":
        kv = parse_template_kv(text)
        return kv.get("character", "") + "\n" + kv.get("rewards", "")
    if type == "colon":
        return "."
    if type == "readable":
        kv = parse_template_kv(text)
        return kv.get("text", "")
    if type == "version":
        kv = parse_template_kv(text)
        return (
            kv.get("title", "")
            + " "
            + kv.get("version", "")
            + "\n"
            + kv.get("description", "")
        )
    if type == "vo/outfit":
        kv = parse_template_kv(text)
        return concat_kv(kv, lambda x: x.endswith("en"))
    if type == "soundtrack usage":
        kv = parse_template_kv(text)
        return ", ".join(kv.values())
    if type == "event":
        kv = parse_template_kv(text)
        n = kv.get("name", "")
        ts = kv.get("time_start", "")
        te = kv.get("time_end", "")
        return f"{n} :\nStart time: {ts}\nEnd time: {te}"
    if type == "tabber":
        result = []
        for line in text.split("\n"):
            if line.startswith(":"):
                result.append(line)
        return "\n".join(result)
    if type == "character story":
        kv = parse_template_kv(text)
        return concat_kv(kv, lambda x: x.startswith("text"))
    if type == "viewpoint":
        kv = parse_template_kv(text)
        return concat_kv(kv, lambda x: x.startswith("title") or x.startswith("text"))
    if type == "a4":  # voice sound file
        return ""

    # take first part
    if type in [
        "item",
        "outfit",
        "all schemes to know explanation",
        "round",
        "element",
        "lexicon",
        "icon/stars",
        "icon/primogem",
        "icon/ar exp",
        "icon/mora",
        "icon/companionship",
        "ref/companion",
        "ref/location",
        "tcg icon",
        "ref/book",
        "sic",
        "furnishing",
        "lex",
        "tcg card",
        "check",
        "ingredient",
        "assets/outfit",
        "ref/npc",
        "if self",
        "icon/ui",
        "chapter",
        "character",
        "ja",
        "constellation",
        "wt",
        "icon/element",
        # important ones (big text):
        "shop",
        "talent",
        "card",
    ]:
        return text.split("|")[0]
    # take 2nd part
    if type in [
        "mc",
    ]:
        return text.split("|")[1]

    # take 2nd part
    if type in ["community"]:
        if "|" in text:
            return text.split("|")[1]
        return ""

    if type not in TEMPLATE_TYPE_USE_TEXT:
        print(colored(f"Uknown template: '{type}':", "yellow"), f"'{text}'")
        # l = UNKNOWN_TEMPLATES.get(type, [])
        # l.append(text)
        # UNKNOWN_TEMPLATES[type] = l

    text = text.replace("|", " ")
    text = text.replace("#", " ")
    return text


def dump_table(text):
    text = text.group(1)
    text = "\n".join([x.lstrip("|!- ") for x in text.split("\n")])
    # print(text)
    return text


def remove_uneeded_paragraphs(text):
    result = []
    is_inside_skipped_p = False
    skipped_p_level = 999  # 2 for h2, 3 for h3 etc.

    for line in text.split("\n"):
        m = re.match(r"^===?([^=]*?)===?$", line)
        if m:
            title = m.group(1).lower()
            level = line.count("=") // 2
            # print(
            # f'Paragraph h{level} "{title}", skipped_p_level={skipped_p_level}"'
            # )

            # we skipped on h2, we should only change this decision on another h2
            if level <= skipped_p_level:
                is_inside_skipped_p = title in SKIPPED_PARAGRAPHS
                if is_inside_skipped_p:
                    skipped_p_level = level
                else:
                    skipped_p_level = 999
            # print(
            # "  " * (level - 2),
            # f'Paragraph h{level} "{title}", skipped={is_inside_skipped_p}',
            # )

        if not is_inside_skipped_p:
            line = line.lstrip(";:")
            line = line.replace("'''", "")
            line = line.replace("''", "'")
            line = line.replace("====", "")  # h4
            line = line.replace("===", "")  # h3
            line = line.replace("==", "")  # h2
            lines = line.split("br /")
            result.extend(lines)
    return "\n".join(result)


def line_contains_any_of(line, strs):
    line = line.lower()
    for s in strs:
        if s.lower() in line:
            # print(colored(s, "red"))
            # print(colored(line, "blue"))
            return True
    return False


def regex_remove(text, ptrn):
    return re.sub(ptrn, "", text)


def cleanup_text(text):
    result = []
    for line in text.split("\n"):
        line = line.lstrip(";:")
        line = line.replace("'''", "")
        line = line.replace("====", "")  # h4
        line = line.replace("===", "")  # h3
        line = line.replace("==", "")  # h2
        lines = line.split("br /")
        result.extend(lines)
    text = "\n".join(result)

    # {| class="wikitable" .... |}
    WIKI_TABLE_REGEX = r'\{\| ?class=["\']?.*wikitable.*?\n(.*?)\|\}'
    text = re.sub(WIKI_TABLE_REGEX, dump_table, text, flags=re.S)
    # {| class="article-table" .... |}
    # impl. same as above
    ARTICLE_TABLE_REGEX = r'\{\| ?class=["\']?.*article-table.*?\n(.*?)\|\}'
    text = re.sub(ARTICLE_TABLE_REGEX, dump_table, text, flags=re.S)
    # {| class="fandom-table" .... |}
    # impl. same as above
    FANDOM_TABLE_REGEX = r'\{\| ?class=["\']?.*fandom-table.*?\n(.*?)\|\}'
    text = re.sub(FANDOM_TABLE_REGEX, dump_table, text, flags=re.S)
    # {|\n ... \n|}
    # impl. same as above
    INSERT_TEXT_REGEX = r"\{\|\n(.*?)\|\}"
    text = re.sub(INSERT_TEXT_REGEX, dump_table, text, flags=re.S)
    # {|\n ... \n|}
    # impl. same as above
    TDT_REGEX = r"\{\|[^\n]*?tdt2.+?\n(.*?)\|\}"
    text = re.sub(TDT_REGEX, dump_table, text, flags=re.S)

    # remove '&lt;gallery&gt; .... &lt;/gallery&gt;'
    SUB_REGEX = r"&lt;gallery&gt;(.*?)&lt;\/gallery&gt;"
    text = re.sub(SUB_REGEX, "", text, flags=re.S)

    # remove unresolveed templates '\{\{ .... }}'
    SUB_REGEX = r"\{\{(.*?)\}\}"
    text = re.sub(SUB_REGEX, "", text, flags=re.S)

    # remove '&lt; ... &gt;'
    # SUB_REGEX = r"&lt;.*?&gt;"
    SUB_REGEX = r"<.*?>"
    text = re.sub(SUB_REGEX, "", text, flags=re.S)
    text = text.replace("&mdash;", "-")
    text = text.replace("&ndash;", "-")
    text = text.replace("&nbsp;", " ")
    text = text.replace("&minus;", "-")
    text = text.replace("&shy;", "")

    text = text.replace("description=", "")
    text = text.replace("quote=", "")
    # aaaa="\d+"
    text = regex_remove(text, r'colspan="\d+"')
    text = regex_remove(text, r'rowspan="\d+"')
    # aaaa="...."
    text = regex_remove(text, r'style=".*?"')
    text = regex_remove(text, r'align=".*?"')
    text = regex_remove(text, r'id=".*?"')
    text = regex_remove(text, r'note=".*?"')
    text = regex_remove(text, r'width=".*?"')
    text = regex_remove(text, r'data-sort-value=".*?"')
    text = regex_remove(text, r'title=".*?"')
    # [https:// ... ]
    text = regex_remove(text, r"\[https?://.+?\]")
    #
    SUB_REGEX = r"^\s*?\|\s*"  # leftover '   |   ' at the start of the line
    text = re.sub(SUB_REGEX, "", text, flags=re.M)

    return text


class ArticlePage:
    def __init__(self, title):
        self.title = title
        self.text = ""
        self.is_event = False

    def __len__(self):
        return len(self.text)

    def __str__(self):
        return (
            f"<page>\n<title>{self.title}</title>\n<text>{self.text}</text>\n</page>\n"
        )


def cleanup_page(title, text):
    page = ArticlePage(title)

    # remove comments
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)

    text = remove_uneeded_paragraphs(text)

    # clean links e.g. '[[Liyue Qixing]]'
    text = re.sub(r"\[\[(.*?)\]\]", cleanup_links, text)

    # clean templates e.g.
    # '{{About|the playable character|the Genius Invokation TCG Character Card|Kaeya (Character Card)}}'
    TEMPLATE_REGEX = r"\{\{([^\{\{]*?)\}\}"
    cleanup_templates__ = lambda x: cleanup_templates(title, x)
    text = re.sub(TEMPLATE_REGEX, cleanup_templates__, text, flags=re.S)
    text = re.sub(TEMPLATE_REGEX, cleanup_templates__, text, flags=re.S)
    text = re.sub(TEMPLATE_REGEX, cleanup_templates__, text, flags=re.S)

    text = cleanup_text(text)

    result = []
    for line in text.splitlines():
        line = line.strip()

        if line.startswith("Start time:"):
            page.is_event = True

        # if line_contains_any_of(line, LINES_THAT_FORCES_SKIP_ARTICLE):
        # return None

        if ".png" in line:
            continue

        if len(line) > 0:
            result.append(line)

        # skip after first line
        if line_contains_any_of(line, LINES_THAT_ONLY_TAKE_FIRST_SENTENCE):
            break
        if line.lower() == "energy":  # enemy stats
            break

    page.text = "\n".join(result)
    return page
