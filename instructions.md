# Veebirakenduse seadistamise juhend

Selle rakenduse seadistamiseks on vaja installida Docker:

- Dockeri link macOS-i jaoks: https://docs.docker.com/desktop/setup/install/mac-install/
- Dockeri link Windowsi jaoks: https://docs.docker.com/desktop/setup/install/windows-install/

---

## 1. Dockeri paigaldus

### 1.1 Paigaldus Windowsile

1. Ava Windowsi aken ja otsi **Command Prompt** või lihtsalt **cmd**. Seejärel ava Command Prompt.
2. Sisesta avanenud aknasse käsk:
   ```bash
   cd Downloads
    ```
3. Installeeri Docker, kasutades käsku:
      ```bash
    start /w "" "Docker Desktop Installer.exe" install
    ```
4. Vajuta **"Yes"** ning avanenud Dockeri aknas **"OK"** (vaikeväärtused jäävad). Installeerimine võtab mõni minut aega.
5. Installatsiooni lõppedes tee arvutile vajadusel restart.
6. Ava Docker Desktop. Seejärel vali **Accept → Skip → Skip**. Oota kuni Docker Engine on käivitunud.

### 1.2 Paigaldus macOS-ile

1. Ava terminal ja sisesta ükshaaval järgnevad käsud:
      ```bash
   cd ~/Downloads
   ```

   ```bash
   sudo hdiutil attach Docker.dmg
   ```

   ```bash
   sudo /Volumes/Docker/Docker.app/Contents/MacOS/install
   ```

   ```bash
   sudo hdiutil detach /Volumes/Docker
   ```
   
2. Ava Docker Desktop. Seejärel vali **Accept** ja **Skip** (akende olemasolul). Oota kuni Docker Engine on käivitunud.

## 2.Veebirakenduse paigaldus

### 2.1 Keskkonnamuutujate seadistamine
1. Ava projekti juurkaustas fail nimega `.env`.

2. Täida järgnevad väljad:
   ```bash
   FLASK_SECRET_KEY=<suvaline sõne väärtus>
   SERPER_API_KEY=<Serper API võti>
   ```
- **FLASK_SECRET_KEY:** `<suvaline sõne väärtus>` — asenda suvalise tekstiga (kasutatakse sessioonihalduseks)
- **SERPER_API_KEY:** `<Serper API võti>` — asenda API-võtmega, mille saad tasuta luua lehel: https://serper.dev/.

Alternatiivselt, võib API-võtit küsida autorilt.

Järgnevad tegevused saab sooritada otse Docker Desktopi terminalis. Selleks vali alt ribalt **Terminal → Enable**.
macOS-i puhul võib sobivam olla kasutada süsteemi terminali.

### 2.2 Dockeri tõmmisfaili loomine (Docker image)

1. Liigu kausta, kuhu zip-fail sai lahti pakitud. Näiteks:
   ```bash
   cd Downloads/<kausta nimi>
   ```
Asenda `<kausta nimi>` lahti pakitud kausta nimega.

2. Sisesta käsk:
   ```bash
   docker build -t guitar-app-image .
   ```

### 2.3 Docker konteineri loomine ja käivitamine

1. Sisesta käsk:
   ```bash
   docker run -d -p 5001:5000 --env-file .env --name guitar-app guitar-app-image
      ```
Kui port 5001 on hõivatud, asenda see näiteks väärtusega 5002.

2. Veebirakendus nüüd töötab. Ava brauseris:
-  http://localhost:5001/
  
   või

- http://127.0.0.1:5001/

3. Loo omale konto. Ainuke piirang on, et parool peab olema vähemalt **8 tähemärki**.

   **NB!** Veebirakendus kasutab lokaalset andmebaasi ning seega kontoandmeid kuhugi välja ei saadeta.

4. Et peatada rakendus:
   ```bash
   docker stop guitar-app
      ```
5. Uuesti käivitamiseks:
   ```bash
   docker start guitar-app
      ```
   
## 3. Veebirakenduse ja Dockeri eemaldamine
1. Peata ja eemalda konteiner:
   ```bash
   docker stop guitar-app
      ```
      ```bash
   docker rm guitar-app
      ```

2. Eemalda tõmmisfail:
   ```bash
   docker image rm guitar-app-image
      ```
3. Sulge Docker Desktop ja deinstalli rakendus.






