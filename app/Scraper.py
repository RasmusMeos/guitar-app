import os
import requests
from bs4 import BeautifulSoup
import urllib3
from app.errors import ErrorCode
import logging
logger = logging.getLogger(__name__)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Scraper:
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.SERPER_API_KEY = os.getenv("SERPER_API_KEY")  # demo eesmärgil on API võti kaasas

    # --- ABIMEETODID ---

    def _fetch_html(self, url: str, error_code: ErrorCode) -> str | ErrorCode:
        """
        Tagastab HTML-i sisu, mida kraapida või spetsiifilise veakoodi
        """
        try:
            res = requests.get(url, headers=self.headers, verify=False)
            res.raise_for_status()
            return res.text
        except requests.RequestException:
            logger.error(f"[ERROR] {error_code.name}")
            return error_code

    @staticmethod
    def _find_artist_info_and_pages(base_html: str) -> tuple[str, list[str]]:
        """
        Tagastab artisti nime and teiste artisti lehtede URL-id (kui eksisteerib pagination ehk lehekülje numeratsioon).
        """
        soup = BeautifulSoup(base_html, "html.parser")

        artist_name = ""
        meta_title = soup.find("meta", property="og:title")
        if meta_title:
            artist_name = meta_title.get("content", "").split(" (")[0].strip()

        pagination = soup.find("div", class_="pager")
        page_links = []
        if pagination:
            for a in pagination.find_all("a", href=True):
                href = a["href"]
                if "_page_" in href:
                    full_url = "https://www.azchords.com" + href
                    if full_url not in page_links:  # väldime duplikaate (Next ja Last leheküljed võivad viidata samale URL-ile)
                        page_links.append(full_url)

        return artist_name, sorted(set(page_links))


    @staticmethod
    def _find_all_links(html: str) -> list[str]:
        '''
        Meetod, mis otsib ja tagastab ette antud HTML-ist kõikide lugude lingid.
        '''
        base = "https://www.azchords.com"
        bs = BeautifulSoup(html, "html.parser")
        tbody = bs.find("tbody", attrs={"data-link": "row"})
        if not tbody:
            return []

        all_links = []

        for tr in tbody.find_all("tr", class_="rowlink"):
            # I variant - lood, millele eksiteerib mitu varianti (valime parima versiooni)
            if tr.get("data-type") == "go_dpd":
                best_link = ""
                best_rating = -1.0
                for li in tr.select("ul.dropdown-menu li"):
                    a = li.find("a", href=True)
                    if not a or not a["href"] or a["href"] == "#":
                        continue
                    href = a["href"]
                    rating_tag = a.find("div", class_="vtext pull-right")
                    rating = 0.0
                    if rating_tag:
                        try:
                            rating = float(rating_tag.text.strip("★"))  # &#9733; kodeerituna
                        except ValueError:
                            pass
                    if rating > best_rating:
                        best_rating = rating
                        best_link = href
                all_links.append(base + best_link)
            else:
                # II variant - ühe versiooniga lood
                a = tr.find("a", href=True)
                if a:
                    href = a["href"]
                    if href and href != "#":
                        all_links.append(base + href)

        return all_links

    # -- MEETODID, MIS ON VÄLJASPOOLT KUTSUTAVAD ---

    def find_azchords_page(self, artist_name: str) -> str | ErrorCode:
        '''
        Esitab päringu https://serper.dev/ API-le ning tagastab artisti AZChords lehekülje lingi
        '''
        if artist_name.lower().startswith("the "): # AZChords ei kasuta "The" prefiksi
            artist_name = artist_name[4:]

        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": self.SERPER_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "q": f"site:azchords.com \"{artist_name} chords\""
        }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            logger.warning(f"Päring ebaõnnestus: {response.text}")
            return ErrorCode.SERPER_FAILURE

        data = response.json()

        for result in data.get("organic", []):
            link = result.get("link", "")
            if "-chords-" in link and "_page_" not in link:
                return link

        return ErrorCode.AZCHORDS_ARTIST_BASE_LINK_NOT_FOUND


    def find_youtube_url(self, artist: str, song_title: str) -> str | ErrorCode:
        """
        Otsib YouTube'i linki artisti ja loo nime põhjal, kasutades Serper.dev API-t.
        Tagastab esimese leitud video lingi või veakoodi.
        """
        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": self.SERPER_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "q": f"site:youtube.com {artist} {song_title}"
        }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            logger.warning(f"Päring ebaõnnestus: {response.text}")
            return ErrorCode.SERPER_FAILURE

        data = response.json()
        top_result = data.get("organic", [])[0] if data.get("organic") else None
        if top_result and "link" in top_result:
            return top_result["link"]

        return ErrorCode.YOUTUBE_LINK_NOT_FOUND


    def find_artist_name_and_links(self, base_url: str) -> tuple[str, list[str]] | ErrorCode:
        '''
        Meetod, mis analüüsib Serperi pakutud linki, tagastades artisti nime ja kõikide lugude lingid
        '''
        all_songs = []
        base_html = self._fetch_html(base_url, ErrorCode.AZCHORDS_ARTIST_BASE_LINK_NOT_FOUND)
        if isinstance(base_html, ErrorCode):
            return base_html

        artist_name, page_links = self._find_artist_info_and_pages(base_html)
        base_page_song_links: list[str] = self._find_all_links(base_html)
        all_songs.extend(base_page_song_links)

        if len(page_links) > 0:
            for link in page_links:
                html = self._fetch_html(link, ErrorCode.AZCHORDS_ARTIST_PAGINATION_LINK_NOT_FOUND)
                if isinstance(html, ErrorCode):
                    logger.warning(html)
                    continue
                current_page_links = self._find_all_links(html)
                all_songs.extend(current_page_links)

        return artist_name, all_songs


    def find_chords_text(self, song_url: str) -> tuple[str,str] | ErrorCode:
        """
        Leiame ning tagastame akordi tabulatuuri ja loo pealkirja
        """

        tab_html = self._fetch_html(song_url, ErrorCode.AZCHORDS_ARTIST_SONG_LINK_NOT_FOUND)
        if isinstance(tab_html, ErrorCode):
            return tab_html

        bs = BeautifulSoup(tab_html, "html.parser")

        # leiame loo pealkirja
        song_title = ""
        meta_desc = bs.find("meta", property="og:description")
        if meta_desc:
            song_title = meta_desc.get("content", "").split(" Chords")[0].strip()
        if not song_title:
            return ErrorCode.INVALID_TITLE

        # leiame loo sõnad ja akordid
        pre = bs.find("pre", id="content")
        if not pre:
            return ErrorCode.CHORDS_NOT_FOUND

        return pre.text.strip(), song_title
