import click
from bs4 import BeautifulSoup
from termcolor import colored
from os import path, makedirs

from constants import SKIPPED_BASED_ON_TEXT, SKIPPED_TITLES, WHITELISTED_TITLES
from single_page_cleanup import cleanup_page


def parse_page(page_xml):
    xml_soup = BeautifulSoup(page_xml, features="lxml")
    title = xml_soup.title.get_text()
    text = xml_soup.find("text").text

    page = cleanup_page(title, text)
    return page


def get_next_tag_value(text, start_idx, tag):
    tag_s = f"<{tag}>"
    tag_e = f"</{tag}>"
    idx_s = text.find(tag_s, start_idx)
    idx_e = text.find(tag_e, start_idx)
    return text[idx_s + len(tag_s) : idx_e]


def is_important_article(page):
    is_important = False
    title = page.title.lower()
    for w_title in WHITELISTED_TITLES:
        if w_title.lower() in title:
            # print(f"{title}: is_important cause {w_title}")
            is_important = True
    text = page.text.lower()
    is_redirect = "#redirect" in text
    return is_important and not is_redirect


def is_skippable_article(page):
    is_invalid = page.is_event
    title = page.title.lower()
    for s_title in SKIPPED_TITLES:
        has_bad_title = s_title.lower() in title
        is_invalid = is_invalid or has_bad_title

    text = page.text.lower()
    for s_text_frag in SKIPPED_BASED_ON_TEXT:
        has_bad_text = s_text_frag.lower() in text
        # print(f"'{s_text_frag}': {has_bad_text}")
        is_invalid = is_invalid or has_bad_text

    is_important = is_important_article(page)
    # print(f"{title}: is_invalid={is_invalid}, is_important={is_important}")
    return is_invalid and not is_important


def read_pages(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        raw_text = f.read()

    page_tag = "<page>"
    page_idx = raw_text.find(page_tag)
    while page_idx != -1:
        next_page_idx = raw_text.find(page_tag, page_idx + 1)
        ns = get_next_tag_value(raw_text, page_idx, "ns")
        if ns == "0":
            page_xml = raw_text[page_idx:next_page_idx]
            yield page_xml
        page_idx = next_page_idx


@click.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.option("-o", "--out_filepath", help="Output file path")
def extract_articles(filepath, out_filepath):
    """Parse Genshin wiki dump and extract all valuable articles

    FILEPATH: Path to extracted genshin-impact.fandom's .xml file
    """

    print(colored("Parsing file for articles:", "blue"), filepath)

    pages = []
    total_page_cnt = 0
    for page_xml in read_pages(filepath):
        page = parse_page(page_xml)
        if page != None and not is_skippable_article(page):
            pages.append(page)
        else:
            # print(colored("Skip:", "red"), f"'{page.title}'")
            pass
        total_page_cnt += 1

    print(colored("Found articles:", "blue"), len(pages))

    if out_filepath == None:
        base, ext = path.splitext(filepath)
        out_filepath = f"{base}.output{ext}"

    # sort - longest first
    LIMIT = 500
    pages = sorted(pages, key=lambda x: -len(x))
    result_pages = set(pages[0:LIMIT])
    result_pages.update([x for x in pages if is_important_article(x)])
    print(
        colored(
            f"Writing {min(LIMIT, len(result_pages))} longest articles to:", "blue"
        ),
        f"'{out_filepath}'",
    )

    with open(out_filepath, "w", encoding="utf-8") as f:
        f.write(
            '<main xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xml:lang="en">\n'
        )
        for p in result_pages:
            f.write(str(p))
            # url = (
            # f"https://genshin-impact.fandom.com/wiki/{p.title.replace(' ', '%20')}"
            # )
            # f.write(f"[{len(p)}] '{url}'\n{p.text[:200]}\n\n")
        f.write("\n</main>")

    """
    # quick stats
    with open(out_filepath, "rb") as f:
        num_lines = sum(1 for _ in f)
    print(colored("Total lines:", "blue"), num_lines)
    print(colored("Longest articles:", "blue"))
    articles_by_len = sorted(PAGES_LEN.items(), key=lambda x: -x[1])
    for a, cnt in articles_by_len[0:10]:
        print(f"\t- '{a}': {cnt}ch")
    """


@click.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.option("-o", "--out_dirpath", help="Output directory")
@click.argument("title")
def dump_article(filepath, out_dirpath, title):
    """Dump Genshin wiki article to separate '.xml' file

    FILEPATH: Path to extracted genshin-impact.fandom's .xml file
    """
    print(colored("Looking for article:", "blue"), title)
    print(colored("Source xml:", "blue"), filepath)

    pages = []
    for page_xml in read_pages(filepath):
        xml_soup = BeautifulSoup(page_xml, features="lxml")
        page_title = xml_soup.title.get_text()
        if title in page_title:
            pages.append((page_title, page_xml))

    print(colored(f"Found {len(pages)} matching articles:", "blue"))
    makedirs(out_dirpath, exist_ok=True)
    for i, page in enumerate(pages):
        title, page_xml = page
        filename = f"{title.replace('/','_')}.dump_{i}.xml"
        filepath = path.join(out_dirpath, filename)
        print(f"\t* '{title}' -> '{filepath}'")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("<main>")
            f.write(page_xml)
            f.write("</main>")


@click.group()
def main():
    """Tool for parsing '.xml' dump from genshin-impact.fandom.com. Get it from 'https://genshin-impact.fandom.com/wiki/Special:Statistics'"""


if __name__ == "__main__":
    main.add_command(extract_articles)
    main.add_command(dump_article)
    main()
