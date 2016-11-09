# Serveur de vérification des e-billets

Cette application permet de centraliser les données relevées par les différents clients Android vérifiant les billets à l'entrée du gala.

## Schémas de fonctionnement

```
┌─────────────────────────────────────────────┐            ┌─────────────────────────────────────────────┐
│                   Serveur                   │            │                 Application                 │
│                                            Demande des clefs                                           │
│    ┌───────────────────────────────────┐    │            │    ┌───────────────────────────────────┐    │
│    │              GetKeys            ◀─┼────┼────────────┼────┼────                               │    │
│    │                                   │    │            │    │            Paramètres             │    │
│    │          data/keys.json         ──┼────┼────────────┼────┼───▶                               │    │
│    └───────────────────────────────────┘    │            │    └───────────────────────────────────┘    │
│                                            Réception des clefs                                         │
│                                             │            │                                             │
│    ┌───────────────────────────────────┐    │            │                                             │
│    │             ValidateApi           │    │            │    ┌───────────────────────────────────┐    │
│    │  ┌──────────────────────────────┐ │    │            │    │                                   │    │
│    │  │                              │ │    │            │    │     Vérification du code bar      │    │
│    │  │   Teste d'existence en BDD   │◀┼────┼────┐       │    │                                   │    │
│    │  │                              │ │    │    │       │    └────────────────┬──────────────────┘    │
│    │  └───────────────┬──────────────┘ │    │    │       │                     │                       │
│    │     N'existe pas │     Existe     │    │    │       Envoi :       ┌───────┴──────────┐            │
│    │         ┌────────┴────────┐       │    │    │Code de vérification │                  │            │
│    │  ┌──────▼─────┐    ┌──────▼─────┐ │    │    │  Nombre de places   │                  │            │
│    │  │            │    │            │ │    │    │   Quanitée validé   │                  │            │
│    │  │            │    │            │ │    │    │       │             ▼                  │            │
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

## Interface d'administration

Il est possible d'accéder à /admin pour obtenir une liste de toutes les validations effectuées et d'annuler le passage d'un billet.

# Installation du serveur sur une machine

Le serveur a été testé sur un raspberry pi 2 modèle B.

Le principe est de fabriquer un hotspot wifi avec le raspberry et de faire tourner le serveur de ebillet en arrière plan.

Pour daemoniser le serveur, il faut itiliser le script ebillet.service qui est à placer dans /etc/init.d, le modifier par rapport à la configuration réelle des fichiers et du nom d'utilisateur et d'activer le service au démarage de la machine

Il faut également créer la base de donnée en se positionnant dans Server et lancer createDB.sh

Il est possible d'avoir une configuration spécifique pour le serveur quisera ignorée par git en créant settings\_custom.py à côté de settings.py.

Enfin, il ne faut pas oublier d'installer les dépedances du logiciel qui sont python3.4 et le contenu de requirements.txt

Pour faire tourner le serveur sur le port 80 sans executer le serveur avec les droits de route, il est possible d'utiliser firewall.sh qui redirige le trafic du port 80 port 8080
