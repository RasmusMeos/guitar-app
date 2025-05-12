from enum import IntEnum

class ErrorCode(IntEnum):
    SERPER_FAILURE = 1
    AZCHORDS_ARTIST_BASE_LINK_NOT_FOUND = 2
    AZCHORDS_ARTIST_PAGINATION_LINK_NOT_FOUND = 3
    AZCHORDS_ARTIST_SONG_LINK_NOT_FOUND = 4
    CHORDS_NOT_FOUND = 5
    NO_CHORDS_SCRAPED = 6
    YOUTUBE_LINK_NOT_FOUND = 7
    INVALID_TITLE = 8
    UNKNOWN_ERROR = 99

error_messages = {
    ErrorCode.SERPER_FAILURE: "Otsing ebaõnnestus. Kontrolli internetiühendust või proovi hiljem uuesti.",
    ErrorCode.AZCHORDS_ARTIST_BASE_LINK_NOT_FOUND: "Artisti ei leitud. Palun kasuta täielikku artisti nime või proovi teist artisti!",
    ErrorCode.AZCHORDS_ARTIST_SONG_LINK_NOT_FOUND: "Artisti lehe laadimine ebaõnnestus.",
    ErrorCode.CHORDS_NOT_FOUND: "Lehelt ei leitud akorde.",
    ErrorCode.NO_CHORDS_SCRAPED: "Akorde ei õnnestunud kraapida. Andmestik on tühi!",
    ErrorCode.YOUTUBE_LINK_NOT_FOUND: "Serperi vastuses ei olnud sobivat linki!",
    ErrorCode.INVALID_TITLE: "Loo pealkiri puudub või on vigane.",
    ErrorCode.UNKNOWN_ERROR: "Tundmatu viga. Palun proovi uuesti.",
}
