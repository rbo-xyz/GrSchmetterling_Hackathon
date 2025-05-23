<p align="center">
    <img src="data/wichtigesbild.png" alt="Schmetterlings" width="400"/>
</p>

# Marschzeitberechnung
Dies ist ein Tool fürs Plannen von Wanderungen. Gestützt and die Marschzeitplanungstabelle von PBS wird hiermit eine Autonome Version bereitgestellt. Das Tool benötigt eine GPX Datei mit der Route von [Geo Admin](https://map.geo.admin.ch/) (Erklährung weiter unten).

Mit Diesem Repo kann vom einrichten des Enviroments bis hin zur Nutzung zu verfühgung gestell. 


## Requirements

- [Git](https://git-scm.com/)
- IDE wie [Visual Studio Code](https://code.visualstudio.com/) 
- [Anaconda Distribution](https://www.anaconda.com/products/distribution) oder [Miniconda](https://docs.conda.io/en/latest/miniconda.html)

## Repository lokal klonen
Mit Git in einem Terminal das GitHub Repository *GrSchmeterling_Hackathon* in ein lokales Verzeichnis klonen.

``` shell
cd /path/to/workspace
# Clone Repository 
git clone https://github.com/rbo-xyz/GrSchmetterling_Hackathon.git
```

### Git Projekt mit Visual Studio Code lokal klonen
Öffne ein neues Visual Studio Code Fenster und wähle unter Start *Clone Git Repository*. Alternativ öffne die Command Palette in VS Code `CTRL+Shift+P` (*View / Command Palette*) und wähle `Git: clone`. 
Füge die Git web URL `https://github.com/TickettoEscape/4230_TickettoEscape.git` ein und bestätige die Eingabe mit Enter. Wähle einen Ordner in welchen das Repository *geklont* werden soll.

## installieren
Öffne ein Terminal und wechsle in den *preprocessing* Ordner.
1. Virtuelle Umgebung für Python mit allen Requirements mit der `myname.yml` automatisch oder mit  `requirements.txt` manuell aufsetzen.

```shell
# go to YML-File
cd preprocessing
# Füge conda-forge den als Channel in conda hinzu, da sonst nicht alle Pakete installiert werden können.
conda env create -f myname.yml
# Env aktivieren.
conda activate Ticket_to_Escape


## API Dokumentation
Bei diesem Programm wird auf folgende API zugegriffen:
- Point HEIGHT_URL = "https://api3.geo.admin.ch/rest/services/height"
- Line HEIGHT_URL = "https://api3.geo.admin.ch/rest/services/profile.json"
um aus 2D Geometrien 3D zu erstellen.

Auf https://api3.geo.admin.ch/rest/services sind maximal Abfragen mit 5000 Zeichen möglich.


## Route erstellen

```
