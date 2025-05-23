<p align="center">
    <img src="data/wichtigesbild.png" alt="Schmetterlings" width="400"/>
</p>

# Marschzeitberechnung

_Den Schmetterling packt die Wanderslust!!_

Dies ist ein Tool fürs Plannen von Wanderungen. Gestützt and die Marschzeitplanungstabelle von PBS wird hiermit eine Autonome Version bereitgestellt. Das Tool benötigt eine GPX Datei mit der Route von [Geo Admin](https://map.geo.admin.ch/) (Erklährung weiter unten).

Mit Diesem Repo kann vom einrichten des Enviroments bis hin zur Nutzung zu verfühgung gestell.

## Requirements

- [Git](https://git-scm.com/)
- IDE wie [Visual Studio Code](https://code.visualstudio.com/)
- [Anaconda Distribution](https://www.anaconda.com/products/distribution) oder [Miniconda](https://docs.conda.io/en/latest/miniconda.html)

## Repository lokal klonen

Mit Git in einem Terminal das GitHub Repository _GrSchmetterling_Hackathon_ in ein lokales Verzeichnis klonen.

```shell
cd /path/to/workspace
# Clone Repository
git clone https://github.com/rbo-xyz/GrSchmetterling_Hackathon.git
```

### Git Projekt mit Visual Studio Code lokal klonen

Öffne ein neues Visual Studio Code Fenster und wähle unter Start _Clone Git Repository_. Alternativ öffne die Command Palette in VS Code `CTRL+Shift+P` (_View / Command Palette_) und wähle `Git: clone`.
Füge die Git web URL `https://github.com/rbo-xyz/GrSchmetterling_Hackathon.git` ein und bestätige die Eingabe mit Enter. Wähle einen Ordner in welchen das Repository _geklont_ werden soll.

## installieren

Öffne ein Terminal und wechsle in den _preprocessing_ Ordner.

1. Virtuelle Umgebung für Python mit allen Requirements mit der `requirements.yml` automatisch oder mit `requirements.txt` manuell aufsetzen.

```shell
# go to YML-File
cd preprocessing
# Füge conda-forge den als Channel in conda hinzu, da sonst nicht alle Pakete installiert werden können.
conda env create -f requirements.yml
# Env aktivieren.
conda activate <myname>

```

## API Dokumentation

Bei diesem Programm wird auf folgende API zugegriffen:

- Point HEIGHT_URL = "https://api3.geo.admin.ch/rest/services/height"
- Line HEIGHT_URL = "https://api3.geo.admin.ch/rest/services/profile.json"

um aus 2D Geometrien 3D zu erstellen.

Auf https://api3.geo.admin.ch/rest/services sind maximal Abfragen mit 5000 Zeichen möglich.

## Route erstellen

Auf [Geo Admin](https://map.geo.admin.ch/) im Register "Zeichnen & Messen auf Karte" kann mit dem Tool Linie die Wanderroute eingezeichnet werden.<br/>
_Tipp:_ Mehrere Linien pro Route sind erlaubt.<br/>

Mit dem Tool Symbol können die Einzelnen Wegpunkte platziert werden. Anschliessend im Fenster, dass sich geöffnet hat kann im Feld Text kann ein Name angegeben werden. <br/>
_Tipp:_ durch anklicken des Symbols kann das Fenster wieder geöffnet werden. Die Wegpunkte werden bei der Berechnung, automatisch auf den nächsten Punkt auf der Linie verschoben.<br/>

Über das Dropdown bei Export kann ein **GPX** exportiert werden.<br/>

**pro GPX darf nur eine Route erfasst sein!**

## Verwendung des Marschzeitberechungs Tool

Der Pfad zum GPX, Angaben zur Laufgeschwindigkeit , usw. müssen eingegeben werden <br/>

<p align="center">
    <img src="data/Fenster_ausgefuellt.jpg" alt="Schmetterlings" width="800"/>
</p>

Anschliessend kann auf den **berechnen** Knopf gedrückt werden. Sobald dies durch ist kann im Fenster die Daten betrachtet werden. <br/>
Über den Export Konpf kann ein PDf generiert werden.
<br/>

<p align="center">
    <img src="data/Fenster_berechnet.jpg" alt="Schmetterlings" width="800"/>
</p><br/>
<br/>
<br/>

Beste Grüsse Gruppe Schmetterling<br/>
Manuel Aebi, Raffaele Boppart, Michael Kamm, Ignaz Kuczynski, Alexander Rühli
