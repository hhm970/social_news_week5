from urllib.request import urlopen
from datetime import datetime
from bs4 import BeautifulSoup


def get_html(url):
    page = urlopen(url)
    html_bytes = page.read()
    html = html_bytes.decode("utf_8")
    return html_doc


def parse_stories_bs(domain_url, html):
    stories = []
    soup = BeautifulSoup(html, "html.parser")
    # TO DO

    return stories


if __name__ == "__main__":
    bbc_url = "http://bbc.co.uk"
    bbc_html_doc = get_html(bbc_url)
