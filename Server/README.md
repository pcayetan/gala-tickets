# Serveur de vérification des e-billets

Cette application permet de centraliser les données relevées par les différents clients Android vérifiant les billets à l'entrée du gala.

## Installation

* Il est recommendé d'installer Poetry pour utiliser et développer ce logiciel. Merci de suivre les instructions ici précentes : [https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installation)
* La génération de la base de donnée nécessite sqlite3, c'est généralement pré-installé sur le système, si ça ne l'est pas, plus d'informations sur : [https://www.sqlite.org/download.html](https://www.sqlite.org/download.html)

```bash
poetry install
poetry shell

# Création de la base de donnée
./createDB.sh

# Configuration du server
## Liste de tickets bannis
cp data/banlist.json.example data/banlist.json
nano data/banlist.json # Voir configuration plus bas

## Clefs de vérification des tickets
cp data/keys.json.example data/keys.json
nano data/keys.json # Voir configuration plus bas

# Lancement du serveur
cd src
./server.py # Disponnible sur localhost:8080/webscan

# Avant la mise en prod
echo "DEBUG = False" > settings_custom.py
nano src/settings_custom.py # Voir configuration plus bas
```

## Configuration
### Tickets bannis banlist.json

C'est une simple liste de numéros de tickets bannis à remplire.
Exemple:

```json
[
    "23 19 33 1 04B5F7BB",
    "23 19 41 1 F11B7EA5"
]
```

### Clefs de vérification keys.json

Ce fichier contint les clefs privées utilisées pour valides les billets. Chaque billet contient un numéro de produit et sa clef privée associée. C'est une liste de dictionnaire suivant le format de l'exemple suivant:

```json
[
    {
        "id": 1120, // Identifiant du produit
        "key": "VDLV7897IEetisuare", // clef privée
        "is_child": true // Si c'est un ticket pour enfant ou non
    },
    {
        "id": 7988,
        "key": "TISEdodp7897tesiuaV8V",
        "is_child": false
    }
]
```

### Configuration du serveur settings\_custom.py

```python
HOST = '0.0.0.0' # Filtre d'écoute (ne généralement pas changer)
PORT = '8080' # Port d'écoute
DEBUG = True # Mode debug (METTRE À False EN PRODUCTION)

ADMIN_PAGE_URL = '/admin' # URL de la page d'administration
```

## Application web

### Scan des tickets /webscan

L'interface est disponnible en accédant à `/webscan` sur le serveur.
Due à des limitations de sécurité sur les navigateurs récents, la caméra ne fonctionne pas sans support du https. Pour contourner cela, il est recommandé d'utiliser **les douchettes à QR code du crunchlab**.

## Interface d'administration /admin

Il est possible et **recommandé** d'accéder à `/admin` pour obtenir une liste de toutes les validations effectuées et d'annuler le passage d'un billet. L'accès à cette page est configurable dans les paramètres du serveur (plus haut).

Cette page est **très réconfortante pour les bénévoles**, il est recommandé de la laisser toujours ouverte.


## Schémas de fonctionnement de l'API (déprécié)

```
           ┌─────────────────────────────────────────────┐            ┌─────────────────────────────────────────────┐
           │                   Serveur                   │            │                 Application                 │
           │    ┌───────────────────────────────────┐   Demande des clefs  ┌───────────────────────────────────┐    │
           │    │              GetKeys            ◀─┼────┼────────────┼────┼────                               │    │
           │    │          data/keys.json         ──┼────┼────────────┼────┼───▶                               │    │
           │    └───────────────────────────────────┘   Réception des clefs│            Paramètres             │    │
           │    ┌───────────────────────────────────┐ Demande de la liste noir                                 │    │
           │    │            GetBanlist         ◀───┼────┼────────────┼────┼──                                 │    │
           │    │         data/banlist.json     ────┼────┼────────────┼────┼─▶                                 │    │
           │    └───────────────────────────────────┘   Réception de la    └───────────────────────────────────┘    │
           │    ┌───────────────────────────────────┐    │liste noir  │                                             │
           │    │            ValidateApi            │    │            │    ┌───────────────────────────────────┐    │
           │    │  ┌──────────────────────────────┐ │    │            │    │                                   │    │
           │    │  │                              │ │    │            │    │     Vérification du code bar      │    │
           │    │  │   Teste d'existence en BDD   │◀┼────┼────┐       │    │                                   │    │
           │    │  │                              │ │    │    │       │    └────────────────┬──────────────────┘    │
           │    │  └───────────────┬──────────────┘ │    │    │       │                     │                       │
           │    │     N'existe pas │     Existe     │    │    │       Envoi :       ┌───────┴──────────┐            │
           │    │         ┌────────┴────────┐       │    │    │Code de vérification │                  │            │
           │    │  ┌──────▼─────┐    ┌──────▼─────┐ │    │    │  Nombre de places   │                  │            │
           │    │  │            │    │            │ │    │    │   Quanitée validé   │                  │            │
           │    │  │            │    │            │ │    │    │   Type de produit   ▼                  │            │
           │    │  │            │    │            │ │    │    │       │    ┌─────────────────┐         │            │
           │    │  │  NewEntry  │    │UpdateEntry │ │    │    │       │    │                 │         │            │
           │    │  │            │    │            │ │    │    └───────┼────│ Vérification de │         │            │
           │    │  │            │    │            │ │    │    ┌───────┼───▶│disponibilité au │         │            │
           │    │  │            │    │            │ │    │    │       │    │     serveur     │         │            │
           │    │  │            │    │            │ │    │    │       │    │                 │         │            │
           │    │  └──────┬─────┘    └──────┬─────┘ │    │    │       │    └────────┬────────┘         │            │
           │    │         │                 │       │    │    │    Réception :      │                  │            │
           │    │  ┌──────▼─────────────────▼────┐  │    │    │ Quantité restante   ├───────────────┐  │            │
           │    │  │                             │  │    │    │    Validation       │               │  │            │
           │    │  │                             │  │    │    │       │ ┌───────────┼───────────────┼──┼──────────┐ │
           │    │  │  Génération de la réponse   │──┼────┼────┘       │ │           ▼     Réponse   ▼  ▼          │ │
           │    │  │                             │  │    │            │ │  ┌────────────────┐  ┌────────────────┐ │ │
           │    │  │                             │  │    │            │ │  │                │  │                │ │ │
           │    │  └─────────────────────────────┘  │    │            │ │  │      Oui       │  │      Non       │ │ │
           │    │                                   │    │            │ │  │                │  │                │ │ │
           │    └───────────────────────────────────┘    │            │ │  └────────────────┘  └────────────────┘ │ │
           │                                             │            │ └─────────────────────────────────────────┘ │
           └─────────────────────────────────────────────┘            └─────────────────────────────────────────────┘
```

## Format de réception des clefs

Requête vers /keys
data/keys.json.example

```json
[
	{
		"id": 1120,
		"key": "VDLV7897IEetisuare",
		"is_child": true
	},
	{
		"id": 7988,
		"key": "TISEdodp7897tesiuaV8V",
		"is_child": false
	}
]
```

## Format de réception de la liste de tickets bannis

Requête vers /banlist
data/banlist.joson.example

```json
[
	"23 19 33 1 04B5F7BB",
	"23 19 41 1 F11B7EA5"
]
```

## Format de requête et de réception des informations

Requête vers /validate : (utilise la méthode POST)

```json
{
	"verif": "EXAMPLE", // Clef de vérification
	"type": "89", // Type de produit
	"nb": 9, // Nombre de places totales du billet
	"qt": 2 // Quantité à valider
}
```

Réception :

```json
{
	"valid": true, // true ou false selon si valide ou non
	"available": 7 // Nombre de places restantes sur le billet
}
```

# Installation du serveur sur une machine (originales de 2016)

Le serveur a été testé sur un raspberry pi 2 modèle B.

Le principe est de fabriquer un hotspot wifi avec le raspberry et de faire tourner le serveur de ebillet en arrière plan.

Pour daemoniser le serveur, il faut itiliser le script ebillet.service qui est à placer dans /etc/init.d, le modifier par rapport à la configuration réelle des fichiers et du nom d'utilisateur et d'activer le service au démarage de la machine

Il faut également créer la base de donnée en se positionnant dans Server et lancer createDB.sh

Il est possible d'avoir une configuration spécifique pour le serveur quisera ignorée par git en créant settings\_custom.py à côté de settings.py.

Enfin, il ne faut pas oublier d'installer les dépedances du logiciel qui sont python3.4 et le contenu de requirements.txt

Pour faire tourner le serveur sur le port 80 sans executer le serveur avec les droits de route, il est possible d'utiliser firewall.sh qui redirige le trafic du port 80 port 8080
