from typing import Dict, Tuple, List, Any
import re
from pychord import Chord
from pychord.utils import note_to_val
from app.errors import ErrorCode

class Processor:

    # --- KONSTANDID ---
    MAJOR_KEYS: Dict[str, Dict[str, float]] = {
        "C": {"C": 1.5, "Dm": 1.0, "Em": 1.0, "F": 1.2, "G": 1.3, "Am": 1.0, "Bdim": 1.0},
        "C#": {"C#": 1.5, "D#m": 1.0, "Fm": 1.0, "F#": 1.2, "G#": 1.3, "A#m": 1.0, "Cdim": 1.0},
        "D": {"D": 1.5, "Em": 1.0, "F#m": 1.0, "G": 1.2, "A": 1.3, "Bm": 1.0, "C#dim": 1.0},
        "D#": {"D#": 1.5, "Fm": 1.0, "Gm": 1.0, "G#": 1.2, "A#": 1.3, "Cm": 1.0, "Ddim": 1.0},
        "E": {"E": 1.5, "F#m": 1.0, "G#m": 1.0, "A": 1.2, "B": 1.3, "C#m": 1.0, "D#dim": 1.0},
        "F": {"F": 1.5, "Gm": 1.0, "Am": 1.0, "A#": 1.2, "C": 1.3, "Dm": 1.0, "Edim": 1.0},
        "F#": {"F#": 1.5, "G#m": 1.0, "A#m": 1.0, "B": 1.2, "C#": 1.3, "D#m": 1.0, "Fdim": 1.0},
        "G": {"G": 1.5, "Am": 1.0, "Bm": 1.0, "C": 1.2, "D": 1.3, "Em": 1.0, "F#dim": 1.0},
        "G#": {"G#": 1.5, "A#m": 1.0, "Cm": 1.0, "C#": 1.2, "D#": 1.3, "Fm": 1.0, "Gdim": 1.0},
        "A": {"A": 1.5, "Bm": 1.0, "C#m": 1.0, "D": 1.2, "E": 1.3, "F#m": 1.0, "G#dim": 1.0},
        "A#": {"A#": 1.5, "Cm": 1.0, "Dm": 1.0, "D#": 1.2, "F": 1.3, "Gm": 1.0, "Adim": 1.0},
        "B": {"B": 1.5, "C#m": 1.0, "D#m": 1.0, "E": 1.2, "F#": 1.3, "G#m": 1.0, "A#dim": 1.0},
    }

    MINOR_KEYS: Dict[str, Dict[str, float]] = {
        "Cm": {"Cm": 1.5, "Ddim": 1.0, "D#": 1.2, "Fm": 1.0, "Gm": 1.3, "G#": 1.0, "A#": 1.0},
        "C#m": {"C#m": 1.5, "D#dim": 1.0, "E": 1.2, "F#m": 1.0, "G#m": 1.3, "A": 1.0, "B": 1.0},
        "Dm": {"Dm": 1.5, "Edim": 1.0, "F": 1.2, "Gm": 1.0, "Am": 1.3, "A#": 1.0, "C": 1.0},
        "D#m": {"D#m": 1.5, "Fdim": 1.0, "F#": 1.2, "G#m": 1.0, "A#m": 1.3, "B": 1.0, "C#": 1.0},
        "Em": {"Em": 1.5, "F#dim": 1.0, "G": 1.2, "Am": 1.0, "Bm": 1.3, "C": 1.0, "D": 1.0},
        "Fm": {"Fm": 1.5, "Gdim": 1.0, "G#": 1.2, "A#m": 1.0, "Cm": 1.3, "C#": 1.0, "D#": 1.0},
        "F#m": {"F#m": 1.5, "G#dim": 1.0, "A": 1.2, "Bm": 1.0, "C#m": 1.3, "D": 1.0, "E": 1.0},
        "Gm": {"Gm": 1.5, "Adim": 1.0, "A#": 1.2, "Cm": 1.0, "Dm": 1.3, "D#": 1.0, "F": 1.0},
        "G#m": {"G#m": 1.5, "A#dim": 1.0, "B": 1.2, "C#m": 1.0, "D#m": 1.3, "E": 1.0, "F#": 1.0},
        "Am": {"Am": 1.5, "Bdim": 1.0, "C": 1.2, "Dm": 1.0, "Em": 1.3, "F": 1.0, "G": 1.0},
        "A#m": {"A#m": 1.5, "Cdim": 1.0, "C#": 1.2, "D#m": 1.0, "Fm": 1.3, "F#": 1.0, "G#": 1.0},
        "Bm": {"Bm": 1.5, "C#dim": 1.0, "D": 1.2, "Em": 1.0, "F#m": 1.3, "G": 1.0, "A": 1.0},
    }

    FLATS_TO_SHARPS: Dict[str, str] = {
        "Ab": "G#",
        "Bb": "A#",
        "Db": "C#",
        "Eb": "D#",
        "Gb": "F#",
    }

    # --- AKORDIDE TUVASTAMINE ---

    def _extract_chords_line_by_line(self, text: str) -> Tuple[Dict[str, int], Dict[str, List[Tuple[int, int]]]]:
        """
        Otsib kitarriakorde tekstist kasutades regex mustrit.
        Sobitab ridu, mis koosnevad ainult akordidest
        :return
        chord_counts: iga akordi tekstis esinemise sagedus
        chord_positions: list iga akordi asukohad tekstis
        """
        chord_pattern = r'(?<!\w)[A-G](?:[#b])?(?:m|maj|min|dim|aug|sus|add|[0-9])*(?:/[A-G](?:[#b])?)?(?!\w)'
        line_pattern = re.compile(rf'^\s*(?:{chord_pattern}\s*)+$')

        chord_counts: Dict[str, int] = {}
        chord_positions: Dict[str, List[Tuple[int, int]]] = {}

        offset = 0
        for i, line in enumerate(text.splitlines(keepends=True)):
            line_content = line.strip("\r\n")

            # erandina vaatame, kas esimene rida algab fraasiga "(I/i)ntro: "
            if i == 0 and line_content.lower().startswith("intro: "):
                line_content = line_content[7:].lstrip() # seitse tähemärki
                intro_offset = line.lower().find("intro: ") + 7
            else:
                intro_offset = 0

            if not line.strip():
                offset += len(line)
                continue
            if not line_pattern.fullmatch(line_content.strip()):
                offset += len(line)
                continue
            for match in re.finditer(chord_pattern, line_content):
                chord = match.group()
                start = offset + intro_offset + match.start()
                end = offset + intro_offset + match.end()

                chord_counts[chord] = chord_counts.get(chord, 0) + 1
                chord_positions.setdefault(chord, []).append((start, end))
            offset += len(line)

        return chord_counts, chord_positions


    # --- TEISENDAMINE JA STANDARDISEERIMINE ---

    @staticmethod
    def _get_chord_features(chord_str: str) -> Dict[str, Any] | None:
        """
        Ekstraheerib ja tagastab akordi põhiheli (root), kuju (quality) ('', 'm', 'dim') ning
        lipud is_minor (mi-kolmkõla) ja is_dominant_seventh (nt B7, G7).
        """
        chord_str = chord_str.strip()
        try:
            chord = Chord(chord_str)
            root = chord.root
            q = str(chord.quality)

            is_minor = False
            is_dom_7th = False

            if q.startswith("m") and not q.startswith("maj"):
                quality = "m"
                is_minor = True
            elif "dim" in q:
                quality = "dim"
            else:
                quality = ""

            if re.fullmatch(r"7.*", q) and "maj" not in q and "dim" not in q:
                is_dom_7th = True

            return {
                "root": root,
                "quality": quality,
                "is_minor": is_minor,
                "is_dom_7th": is_dom_7th,
            }
        except ValueError:
            # varuvariant
            match = re.match(r"^([A-G][#b]?)(m(?!aj)|dim|7)?", chord_str)
            if match:
                root = match.group(1)
                quality = match.group(2) or ""
                is_minor = quality == "m"
                is_dom7 = quality.startswith("7") if quality and not quality.startswith(
                    ("maj", "dim")) else False  # igaks juhuks maj/dim kontroll
                return {
                    "root": root,
                    "quality": quality,
                    "is_minor": is_minor,
                    "is_dom_7th": is_dom7,
                }

            return None

    def _convert_flats_to_sharps(self, chord_counts: Dict[str, int],
                                chord_positions: Dict[str, List[Tuple[int, int]]]) -> Tuple[
        Dict[str, int], Dict[str, List[Tuple[int, int]]]]:
        """
        Asendab kõik bemollid nende ekvivalentsete dieesidega
        Funktsioon eeldab, et sisendakordid on sobivad
        chord_counts ja chord_positions akordide järjestused ühtivad
        """
        to_sharp_chord_counts: Dict[str, int] = {}
        to_sharp_chord_positions: Dict[str, List[Tuple[int, int]]] = {}

        for chord in chord_counts.keys():
            new_chord = self._convert_chord_to_sharp(chord)

            to_sharp_chord_counts[new_chord] = to_sharp_chord_counts.get(new_chord, 0) + chord_counts[chord]
            to_sharp_chord_positions.setdefault(new_chord, []).extend(chord_positions[chord])

        return to_sharp_chord_counts, to_sharp_chord_positions

    @staticmethod
    def _convert_chord_to_sharp(chord_str: str) -> str:
        for flat, sharp in Processor.FLATS_TO_SHARPS.items():
            if flat in chord_str:
                chord_str = chord_str.replace(flat, sharp)
        return chord_str

    def _convert_flats_in_tab_to_sharps(self, tab_text: str, chord_positions: Dict[str, List[Tuple[int, int]]]) -> str:
        text_chars = list(tab_text)
        for chord, positions in chord_positions.items():
            converted = self._convert_chord_to_sharp(chord)
            if converted != chord:
                for start, end in positions:
                    text_chars[start:end] = list(converted.ljust(end - start))

        return "".join(text_chars)



    def _standardize_chord_counts(self, chord_counts: Dict[str, int]) -> Dict[str, int]:
        std_chord_counts: Dict[str, int] = {}
        for chord, count in chord_counts.items():
            parsed = self._get_chord_features(chord)
            if not parsed:
                continue
            if parsed["is_minor"] or parsed["quality"] == "dim":
                std_chord = parsed["root"] + parsed["quality"]
            else:
                std_chord = parsed["root"]
            std_chord_counts[std_chord] = std_chord_counts.get(std_chord, 0) + chord_counts[chord]
        return std_chord_counts


    def _standardize_chord_positions(self, chord_positions: Dict[str, List[Tuple[int, int]]]) -> Dict[
        str, List[Tuple[int, int]]]:
        std_chord_positions: Dict[str, List[Tuple[int, int]]] = {}
        for chord, positions in chord_positions.items():
            parsed = self._get_chord_features(chord)
            if not parsed:
                continue
            if parsed["is_minor"] or parsed["quality"] == "dim":
                std_chord = parsed["root"] + parsed["quality"]
            else:
                std_chord = parsed["root"]
            std_chord_positions.setdefault(std_chord, []).extend(positions)
        return std_chord_positions



    # --- HELISTIKU TUVASTAMINE ---

    def _score_key(self, chord_counts: Dict[str, int], scale_weights: Dict[str, float]) -> float:
        '''
        Kaalutud skoori arvutamine ühe konktreetse skaala joaks loos esineva akordide arvu põhjal
        Tagastatud skoori kasutatakse helistiku tuvastamiseks

        :param chord_counts: loos leiduvad akordid ja nende sagedused (mitu korda loos esinevad)
        :param scale_weights: MAJOR_KEYS või MINOR_KEYS "sõnaraamat"
        :return:
        '''
        score = 0.0
        for chord_str, count in chord_counts.items():
            if chord_str in scale_weights:
                weight = scale_weights[chord_str]
                score += count * weight
        return score

    @staticmethod
    def _key_tiebreaker(candidates: List[str], std_chord_positions: Dict[str, List[Tuple[int, int]]]) -> str | None:
        """
        Katse otsustada lõplik helistik, vaadates:
        - esimest ja viimast akordi
        - tihti esinevaid "chord progressions" mustreid
        - dominant 7ths olemasolu (tuleviku arendusena)
        :param candidates: sobivad kandidaadid, mis võiksid olla helistikuks
        :param std_chord_positions: akordid ja nende asukohad algtekstis
        :return: kõige paremini sobistuva helistiku võti või None, kui mõni sisend puudub või otsust ei suudetud langetada
        """
        if not std_chord_positions or not candidates:
            return None

        # loome sorteeritud ennikute listi, mille esimene positsioon viitab akordile ja teine tema positsioonile (algusele)
        all_chord_occ_ordered: list = sorted(
            [(chord, pos[0]) for chord, positions in std_chord_positions.items() for pos in positions],
            key=lambda x: x[1],
        )
        # loome listi, milles on ainult akordid nende esinemise järjekorras, ja loome sellest sõne
        chord_sequence: str = " ".join([chord for chord, _ in all_chord_occ_ordered])

        first_chord = chord_sequence.split(" ")[0]
        last_chord = chord_sequence.split(" ")[-1]

        def progression_score(prog_key: str) -> float:
            score_prog = 0.0

            if prog_key in Processor.MAJOR_KEYS:
                scale = list(Processor.MAJOR_KEYS[prog_key].keys())
                dim_chord = scale[6]
                if dim_chord in chord_sequence:
                    score_prog += 0.5
                progressions = [
                    (2.0, f"{scale[0]} {scale[3]} {scale[4]}"),  # I–IV–V
                    (1.5, f"{scale[0]} {scale[4]} {scale[5]} {scale[3]}"),  # I–V–vi–IV
                    (1.3, f"{scale[0]} {scale[5]} {scale[3]} {scale[4]}"),  # I–vi–IV–V
                    (1.2, f"{scale[0]} {scale[1]}"),  # I-ii
                ]
            elif prog_key in Processor.MINOR_KEYS:
                scale = list(Processor.MINOR_KEYS[prog_key].keys())
                progressions = [
                    (2.0, f"{scale[0]} {scale[3]} {scale[4]}"),  # i–iv–v
                    (1.5, f"{scale[0]} {scale[5]} {scale[2]} {scale[6]}"),  # i–VI–III–VII
                    (1.3, f"{scale[0]} {scale[6]} {scale[5]} {scale[4]}"),  # i–VII–VI–V
                    (1.2, f"{scale[0]} {scale[3]}"),  # i-iv
                ]
            else:
                return 0.0

            for weight, progression in progressions:
                if progression in chord_sequence:
                    score_prog += weight
            return score_prog

        scored_candidates: Dict[str, float] = {}
        for key in candidates:
            score = 0.0
            unique_chords = len(std_chord_positions)
            bonus = 0.5
            if unique_chords == 3:
                bonus = 0.75
            if unique_chords > 3:
                bonus = 1.0
            if first_chord == key:  # algab toonikaga
                score += bonus
            if last_chord == key:  # lõppeb toonikaga
                score += bonus
            score += progression_score(key)
            scored_candidates[key] = score

        best = max(scored_candidates, key=scored_candidates.get)
        max_score = max(scored_candidates.values())
        tied = [k for k, v in scored_candidates.items() if v == max_score]
        if scored_candidates[best] == 0 or len(tied) > 1:
            return None  # ei õnnestunud lõpliku otsust teha
        return best

    def _find_key(self, chord_counts: Dict[str, int], std_chord_positions: Dict[str, List[Tuple[int, int]]]) -> Tuple[
        str, float]:
        '''
        Helistiku tuvastamine
        Vaadatakse nii mažoorseid kui ka minoorseid skaalasid
        Tagastab kõige tõenäolisema helistiku
        '''

        key_scores: Dict[str, float] = {}

        for key, weights in Processor.MAJOR_KEYS.items():
            key_scores[key] = self._score_key(chord_counts, weights)

        for key, weights in Processor.MINOR_KEYS.items():
            key_scores[key] = self._score_key(chord_counts, weights)

        best_key = max(key_scores, key=key_scores.get)
        best_score = key_scores[best_key]

        candidates = [candidate for candidate, score in key_scores.items() if (best_score - score) <= 10.0]

        if len(candidates) > 1:
            tiebreak = self._key_tiebreaker(candidates, std_chord_positions)
            if tiebreak:
                return tiebreak, key_scores[tiebreak]

        return best_key, best_score

    # -- MEETODID, MIDA VÄLJASPOOLT KUTSUDA --

    def transpose_tab_text(self, tab_text: str, src_key: str, target_key: str,
                           chord_positions: Dict[str, List[Tuple[int, int]]]) -> Tuple[str, Dict[str, List[Tuple[int, int]]]]:
        """
        Transponeerib kõik tekstis leiduvad akordid uude helistikku.
        :param tab_text: lähtetekst akordidega
        :param src_key: praegune helistik
        :param target_key: helistik, millesse soovitakse transponeerida
        :param chord_positions: tekstis esinevad akordid ja nende asukohad
        :return: transponeeritud akordidega tekst ning uued akordide positsioonid tekstis
        """
        if not chord_positions or src_key == target_key:
            return tab_text, {k: v.copy() for k, v in chord_positions.items()}

        tab_chars = list(tab_text) # modifitseerime tähemärgi haaval

        # Koostame akordide positsioonidest listi ning sorteerime algindeksi alusel
        occurrences: List[Tuple[int, int, str]] = sorted(
            # akord: s - algusindeks, e - lõppindeks, ch - nimetus/notatsioon
            ((s, e, ch) for ch, positions in chord_positions.items() for s, e in positions),
            key=lambda x: x[0],
            reverse=True, # töötleme (hiljem) teksti paremalt vasemale, et indeksid ei nihkuks enne asendamist
        )

        # Arvutame helistike vahe pooltoonides
        shift: int = note_to_val(target_key.replace("m", "")) - note_to_val(src_key.replace("m", ""))

        for start, end, orign_chord in occurrences:
            try:
                chord_obj = Chord(orign_chord)
                chord_obj.transpose(shift)
                new_chord = self._convert_chord_to_sharp(str(chord_obj))
            except ValueError:
                # kui transponeerimine ei õnnestu (vigane/tundmatu akord), jätame vahele
                continue

            original_len = end - start # algse akordi "laius" tekstis
            new_len = len(new_chord)

            # Uue akordi koostamine, mida transponeeritud tabulatuuri (teksti) paigutada
            if new_len < original_len:
                # akord lühenes -> tagame, et pikkused ühtiksid, täites selleks vahe tühikutega
                display_chord = new_chord.ljust(original_len)
            else:
                display_chord = new_chord

                surplus = new_len - original_len # mitme tähemärgi võrra uus akord pikem

                # Kui uus akord pikem, proovime tekstis olevad tühikud consume'ida, et mitte nihutada järgnevaid ridu
                while surplus > 0 and end < len(tab_chars) and tab_chars[end] == " " and tab_chars[end+1] == " ":
                    del tab_chars[end]
                    surplus -= 1

                # Kui ruumi ikkagi ei jagu, lisame lõppu tühiku, et säilitada loetavus
                if surplus > 0 and (end >= len(tab_chars) or not tab_chars[end].isspace()):
                    display_chord += " "

            tab_chars[start:end] = list(display_chord)

        transposed_tab = "".join(tab_chars)
        _, new_positions = self._extract_chords_line_by_line(transposed_tab)

        return transposed_tab, new_positions


    def simplify_chords(self, tab_text: str, chord_positions: Dict[str, List[Tuple[int, int]]]) -> str:
        simplified: dict = {}
        for chord in chord_positions:
            parsed = self._get_chord_features(chord)
            if not parsed:
                simplified[chord] = chord
            elif parsed["is_dom_7th"]:
                simplified[chord] = parsed["root"] + "7"
            elif parsed["is_minor"]:
                simplified[chord] = parsed["root"] + parsed["quality"]
            else:
                simplified[chord] = parsed["root"]

        text_chars = list(tab_text)
        occurrences = sorted(
            ((s, e, ch) for ch, positions in chord_positions.items() for s, e in positions),
            key=lambda x: x[0],
            reverse=True,
        )
        for start, end, origin_chord in occurrences:
            new_chord = simplified[origin_chord]

            original_len = end - start
            new_len = len(new_chord)

            assert new_len <= original_len, (
                f"Lihtsustatud akord {new_chord!r} pikem kui originaalne {origin_chord!r}"
            )

            display_chord = new_chord.ljust(original_len) # lihtsustatud akord on alati ülimalt sama pikk kui originaalne
            text_chars[start:end] = list(display_chord)

        return "".join(text_chars)



    def process_chord_tab(self, raw_tab: str) -> Tuple[str, str, Dict[str, List[Tuple[int, int]]]] | ErrorCode:
        chord_counts_raw, chord_pos_raw = self._extract_chords_line_by_line(raw_tab)
        if not chord_counts_raw or not chord_pos_raw:
            return ErrorCode.NO_CHORDS_SCRAPED
        converted_tab = self._convert_flats_in_tab_to_sharps(raw_tab, chord_pos_raw)
        chord_counts_converted, chord_pos_converted = self._convert_flats_to_sharps(chord_counts_raw, chord_pos_raw)
        chord_counts_standard = self._standardize_chord_counts(chord_counts_converted)
        chord_pos_standard = self._standardize_chord_positions(chord_pos_converted)
        best_key, best_score = self._find_key(chord_counts_standard, chord_pos_standard)
        return best_key, converted_tab, chord_pos_converted
