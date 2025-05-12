document.addEventListener("DOMContentLoaded", () => {

  // Vajalikud konstandid
  const tabElement = document.getElementById("chords-tab");
  const simplifyElement = document.getElementById("simplify-toggle");
  const transposeElement = document.getElementById("transpose");

  const currentKey = window.songData.keyIdentified;
  const MAJOR_KEYS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
  const MINOR_KEYS = MAJOR_KEYS.map(k => k + "m");
  const allKeys = currentKey.endsWith("m") ? MINOR_KEYS : MAJOR_KEYS;

  // Oleku muutumise "jälgimine"
  let baseTab = window.songData.baseTabText; // lihtsustamata tabulatuur
  let chordPositions = window.songData.chordPositions; // lähtub alati lihtsustamata akordide struktuurist
  let currentKeyState = currentKey;
  let simplifiedTab = null; // hoiab lihtsustatud akordide tabulatuuri

  // Transponeerimise funktsionaalsuse loomine
  for (const key of allKeys) {
    const option = document.createElement("option");
    option.value = key;
    option.text = key;
    if (key === currentKey) option.selected = true;
    transposeElement.appendChild(option);
  }

  // Akordide lihtsustamine -> esitame päringu vaid juhul, kui lihtsustatud
  // tabulatuur selle helistiku jaoks pole juba brauserile saadaval
  simplifyElement.addEventListener("change", async () => {
    if (simplifyElement.checked) {
      if (!simplifiedTab) {
        const res = await fetch("/simplify", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            tab_text: baseTab,
            chord_positions: chordPositions
          })
        });
        const data = await res.json();
        simplifiedTab = data.modified_tab;
      }
      tabElement.textContent = simplifiedTab;
    } else {
      tabElement.textContent = window.songData.currentTabText;
    }
  });

  // Transponeerimine
  transposeElement.addEventListener("change", async (e) => {
    const targetKey = e.target.value;
    if (targetKey === currentKeyState) return;

    // transponeerime alati viimati saadud (mitte lihtsustatud) baas-tabulatuuri põhjal
    const res = await fetch("/transpose", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        src_key: currentKeyState,
        target_key: targetKey,
        tab_text: baseTab,
        chord_positions: chordPositions
      })
    });

    const data = await res.json();
    const transposedTab = data.transposed_tab;
    const updatedChordPos = data.chord_positions;

    // uuendame seisu
    window.songData.currentTabText = transposedTab;
    baseTab = transposedTab;
    chordPositions = updatedChordPos;
    currentKeyState = targetKey;
    simplifiedTab = null; // invalideerime brauseri vahemälu
    simplifyElement.checked = false;
    tabElement.textContent = transposedTab;
  });


  // Lemmikuks märkimine
  const favBtnElement = document.querySelector(".favourite-toggle");
  favBtnElement.addEventListener("click", async () => {
    const img = favBtnElement.querySelector("img");
    const response = await fetch("/toggle-favourite", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ song_id: window.songData.songId })
    });

    const data = await response.json();
      img.src = data.is_favourite
        ? "/static/img/fav_on.png"
        : "/static/img/fav_off.png";
  });

  if (simplifyElement.checked) {
  simplifyElement.dispatchEvent(new Event("change"));
  }

});
