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
│    │             Validate              │    │            │    ┌───────────────────────────────────┐    │
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
		"key": "VDLV7897IEetisuare"
	},
	{
		"id": 7988,
		"key": "TISEdodp7897tesiuaV8V"
	}
]
```

## Format de requête et de réception des informations

Requête vers /validate : (utilise la méthode POST)

```json
{
	"verif": "EXAMPLE", // Code de vérification du billet
	"nb": 9, // Nombre de places totales du billet
	"qt": 2 // Quantité à valider
}
```

Réception :

```json
{
	"valid": true, // true ou false selon si valide ou non
	"avaliable": 7 // Nombre de places restantes sur le billet
}
```
