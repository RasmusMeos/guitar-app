import json
import html
from flask import Blueprint, request, render_template, flash, jsonify, session, redirect, url_for
from app.Scraper import Scraper
from app.Processor import Processor
from app.errors import ErrorCode
from app.utils import *
from app.models import artists, chords, favourite, songs
import logging
logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def index():
    if "user_id" not in session:
        return redirect(url_for('auth.login'))
    return redirect(url_for('main.search'))


@main_bp.route('/search', methods=['GET', 'POST'])
def search():
    if "user_id" not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'GET':
        return render_template('index.html')

    artist_query = request.form.get('artist')
    if not artist_query:
        flash("Palun sisesta artisti nimi.", "error")
        return render_template('index.html')

    scraper = Scraper()
    base_artist_url = scraper.find_azchords_page(artist_query)
    if isinstance(base_artist_url, ErrorCode):
        flash("Artistile ei leitud sobivaid tulemusi. Palun kontrolli nime ja proovi uuesti.", "error")
        return render_template('index.html')

    # Uurime, kas artistiga seotud URL juba eksisteerib andmebaasis
    artist = artists.get_artist_by_url(base_artist_url)
    if not artist:
        result = scraper.find_artist_name_and_links(base_artist_url)
        if isinstance(result, ErrorCode):
            flash("Artistile ei leitud sobivaid tulemusi. Palun kontrolli nime ja proovi uuesti.", "error")
            return render_template('index.html')

        artist_name, song_links = result
        artist_id = artists.insert_artist(base_artist_url, artist_name)
        songs.insert_all_songs(song_links, artist_id)
    else:
        artist_id = artist["id"]
        artist_name = artist["a_name"]

    # Esitame päringu 7 suvalise loo jaoks
    songs_to_display_or_process: List[dict] = songs.get_random_songs_for_display(artist_id, limit=7)

    results: list[dict] = []
    processor = Processor()
    for entry in songs_to_display_or_process:
        # Kui lugu pole veel töödeldud
        if not entry["tab"]:
            scraping_result = scraper.find_chords_text(entry["url"])
            if isinstance(scraping_result, ErrorCode):
                logger.warning(f"Kraapija ei leidnud sisu või pealkiri vigane, loo ID: {entry['id']}. Kustutame andmebaasist.")
                songs.delete_song(entry["id"])
                continue
            tab, raw_title = scraping_result
            title = html.unescape(raw_title) # et pealkirjad oleksid loetavamad - nt &#039; -> '
            processing_result = processor.process_chord_tab(tab)
            if isinstance(processing_result, ErrorCode):
                logger.warning(f"Regex ei leidnud akorde, loo ID: {entry['id']}. Kustutame andmebaasist.")
                songs.delete_song(entry["id"])
                continue
            best_key, converted_tab, chord_pos = processing_result
            result = songs.update_song(entry["id"], title, converted_tab, json.dumps(pythonic_to_json(chord_pos)), best_key)
            results.append(result) if result else logger.warning(f"Andmebaasi uuendamine ebaõnnestus loo ID-ga {entry['id']} jaoks.")
        else:
            results.append({
                "id": entry["id"],
                "title": entry["title"],
                "tab": entry["tab"],
                "chord_positions": json.loads(entry["chord_positions"]),
                "in_key": entry["in_key"]
            })

    if not results:
        flash("Artistile ei leitud sobivaid tulemusi. Palun kontrolli nime ja proovi uuesti.", "error")
        return render_template("index.html")

    # teeme päringu kasutaja teatud akordide kohta, et teha sobivuse hinnang
    known_chords: list[str] = chords.get_user_known_chords(session["user_id"])

    # teeme päringu kasutaja lemmikuks märgitud lugude kohta
    favourites_set = set(favourite.get_user_favourite_song_ids(session["user_id"]))
    for displayed_song in results:
        displayed_song["is_favourite"]: bool = displayed_song["id"] in favourites_set

    # koostame dicti, millisele artistile lood kuuluvad (struktuuri on vaja kuvamiseks)
    artists_dict: dict[int, str] = {result["id"]: artist_name for result in results}

    for s in results:
        all_chords = list(s["chord_positions"].keys())
        known_matches = [c for c in all_chords if c in known_chords]
        unknown_matches = [c for c in all_chords if c not in known_chords]
        match_ratio = len(known_matches) / len(all_chords) if all_chords else 0
        s["match_ratio"] = match_ratio
        s["unknown_matches"] = unknown_matches

    results.sort(key=lambda mr: mr["match_ratio"], reverse=True)



    return render_template('results.html', page_title=f"Otsingutulemused - {artist_name}", artists=artists_dict, songs=results, known_chords=known_chords)


@main_bp.route('/song', methods=['GET'])
def song():
    if "user_id" not in session:
        return redirect(url_for('auth.login'))

    song_id = request.args.get('id', type=int)
    artist = request.args.get('artist', type=str)
    if not song_id or not artist:
        flash("Lugu ei leitud.", "error")
        return redirect(url_for("main.index"))

    one_song = songs.get_song_by_id(song_id)
    if not one_song:
        flash("Lugu ei leitud.", "error")
        return redirect(url_for("main.index"))

    # Kontrollime, kas kõik vajalikud väljad eksisteerivad ja pole tühjad
    required_fields = ["title", "in_key", "tab", "chord_positions"]
    if not all(one_song.get(field) for field in required_fields):
        flash("Lugu ei leitud.", "error")
        return redirect(url_for("main.index"))

    # kas konkreetne lugu on kasutaja poolt lemmikuks märgitud
    is_fav = favourite.is_favourite(session["user_id"], one_song["id"])

    if one_song["yt_url"]:
        yt_url = one_song["yt_url"]
    else:
        scraper = Scraper()
        yt_url = scraper.find_youtube_url(artist, one_song["title"])
        if isinstance(yt_url, ErrorCode):
            logger.warning(yt_url.value)
            yt_url = None
            pass
        else:
            songs.update_song_yt_url(song_id, yt_url)


    return render_template('song.html',
                           song_id=one_song["id"],
                           title=one_song["title"],
                           in_key=one_song["in_key"],
                           tab=one_song["tab"],
                           chord_positions=json.loads(one_song["chord_positions"]),
                           is_favourite=is_fav,
                           yt_url=yt_url)


@main_bp.route('/my-chords', methods=['GET', 'POST'])
def my_chords():
    if "user_id" not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        chords_ids = [int(chord_id) for chord_id in request.form.getlist('chords')]
        chords.update_user_chords(session["user_id"], chords_ids)
        flash("Akordid uuendatud.", "success")
        return redirect(url_for('main.my_chords'))

    chords_by_category = chords.get_all_chords_with_user_selection(session["user_id"])
    return render_template('my_chords.html', chords_by_category=chords_by_category)


@main_bp.route('/transpose', methods=['POST'])
def transpose():
    data = request.get_json()
    src_key = data['src_key']
    target_key = data['target_key']
    tab_text = data['tab_text']
    chord_pos = data['chord_positions']

    p = Processor()
    transposed_tab, updated_positions = p.transpose_tab_text(tab_text,src_key,target_key,json_to_pythonic(chord_pos))
    return jsonify({'transposed_tab': transposed_tab, 'chord_positions': pythonic_to_json(updated_positions)})


@main_bp.route('/simplify', methods=['POST'])
def simplify():
    data = request.get_json()
    tab_text = data['tab_text']
    chord_pos = data['chord_positions']

    p = Processor()
    simplified_tab = p.simplify_chords(tab_text, json_to_pythonic(chord_pos))
    return jsonify({'modified_tab': simplified_tab})


@main_bp.route('/toggle-favourite', methods=['POST'])
def toggle_favourite():
    if "user_id" not in session:
        return jsonify({"error": "Sisselogimata!"}), 401

    data = request.get_json()
    song_id = data['song_id']
    if not song_id:
        return jsonify({"error": "song_id puudu!"}), 400

    is_favourite = favourite.toggle_favourite_song(session["user_id"], song_id)
    return jsonify({'is_favourite': is_favourite})


@main_bp.route('/favourites')
def favourites():
    if "user_id" not in session:
        return redirect(url_for('auth.login'))

    fav_songs = favourite.get_user_favourite_songs(session["user_id"])

    if not fav_songs:
        flash("Ühtegi lemmikut lugu pole veel märgitud.", "error")
        return redirect(url_for("main.index"))

    fav_song_ids = set(favourite.get_user_favourite_song_ids(session["user_id"]))
    for fav_song in fav_songs:
        fav_song["is_favourite"]: bool = fav_song["id"] in fav_song_ids
        fav_song["chord_positions"] = json.loads(fav_song["chord_positions"])

    known_chords: list[str] = chords.get_user_known_chords(session["user_id"])

    artists_dict: dict[int, str] = {fav_song["id"]: fav_song["artist_name"] for fav_song in fav_songs}

    for s in fav_songs:
        all_chords = list(s["chord_positions"].keys())
        known_matches = [c for c in all_chords if c in known_chords]
        unknown_matches = [c for c in all_chords if c not in known_chords]
        match_ratio = len(known_matches) / len(all_chords) if all_chords else 0
        s["match_ratio"] = match_ratio
        s["unknown_matches"] = unknown_matches

    fav_songs.sort(key=lambda mr: mr["match_ratio"], reverse=True)

    return render_template("results.html", page_title="Lemmikuks märgitud lood", artists=artists_dict, songs=fav_songs, known_chords=known_chords)


