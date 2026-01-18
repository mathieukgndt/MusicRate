\# 🎵 MusicRate - Site de Notation Musicale



!\[Python](https://img.shields.io/badge/Python-3.8+-blue.svg)

!\[Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)

!\[SQLite](https://img.shields.io/badge/SQLite-3-lightgrey.svg)

!\[Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)



\*\*MusicRate\*\* est une application web complète permettant aux utilisateurs de découvrir, noter et partager leurs avis sur des albums musicaux. Intégrant l'API Spotify.



---



\## 📋 Table des matières



\- \[Fonctionnalités](#-fonctionnalités)

\- \[Technologies utilisées](#-technologies-utilisées)

\- \[Architecture du projet](#-architecture-du-projet)

\- \[Installation](#-installation)

\- \[Configuration](#-configuration)

\- \[Utilisation](#-utilisation)

\- \[Structure de la base de données](#-structure-de-la-base-de-données)

\- \[Documentation des modules](#-documentation-des-modules)

\- \[API Spotify](#-api-spotify)

\- \[Fonctionnalités avancées](#-fonctionnalités-avancées)

\- \[Captures d'écran](#-captures-décran)

\- \[Crédits](#-crédits)



---



\## ✨ Fonctionnalités



\### 🔐 Authentification et Gestion de Compte

\- \*\*Inscription/Connexion\*\* sécurisée avec hachage de mots de passe

\- \*\*Récupération de mot de passe\*\* par token sécurisé

\- \*\*Profils utilisateurs\*\* personnalisables :

&nbsp; - Photo de profil (upload ou URL)

&nbsp; - Biographie (200 caractères max)

&nbsp; - Statistiques (notes, followers, suivis)

\- \*\*Paramètres de compte\*\* :

&nbsp; - Modification du nom d'utilisateur

&nbsp; - Changement d'email

&nbsp; - Mise à jour du mot de passe

&nbsp; - Suppression de compte avec confirmation



\### 🎼 Gestion Musicale

\- \*\*Recherche\*\* d'albums et d'artistes :

&nbsp; - Dans la base de données locale

&nbsp; - Via l'API Spotify avec intégration automatique

\- \*\*Détails des albums\*\* :

&nbsp; - Informations complètes (date de sortie, genres, artiste)

&nbsp; - Liste des titres avec durées

&nbsp; - Lien direct vers Spotify

&nbsp; - Note moyenne et nombre de notations

\- \*\*Pages artistes\*\* :

&nbsp; - Discographie complète

&nbsp; - Image et genres musicaux



\### ⭐ Système de Notation

\- \*\*Notes de 0 à 10\*\* (par incréments de 0.5)

\- \*\*Critiques textuelles\*\* optionnelles

\- \*\*Modification/suppression\*\* de ses propres notes

\- \*\*Système de réponses\*\* :

&nbsp; - Conversations sous chaque critique

&nbsp; - Fils de discussion dédiés

&nbsp; - Suppression de ses propres réponses



\### 👥 Fonctionnalités Sociales

\- \*\*Système de suivi\*\* (follow/unfollow)

\- \*\*Page Amis\*\* :

&nbsp; - Liste des personnes suivies

&nbsp; - Activité récente des amis

&nbsp; - Accès rapide aux profils

\- \*\*Profils publics\*\* :

&nbsp; - Top 5 albums préférés

&nbsp; - Notes récentes

&nbsp; - Statistiques complètes





\### 📊 Classements

\- \*\*Albums les mieux notés\*\* (note moyenne ≥ 3 avis)

\- \*\*Albums les moins bien notés\*\* (pour savoir quoi éviter 😅)

\- \*\*Filtrage par nombre minimum de notes\*\* pour éviter les biais



---



\## 🛠 Technologies utilisées



\### Backend

\- \*\*Python 3.8+\*\*

\- \*\*Flask 3.0+\*\* - Framework web

\- \*\*SQLite\*\* - Base de données

\- \*\*Werkzeug\*\* - Hachage de mots de passe

\- \*\*Spotipy\*\* - Intégration API Spotify



\### Frontend

\- \*\*Jinja2\*\* - Moteur de templates

\- \*\*Bootstrap 5.3\*\* - Framework CSS

\- \*\*Bootstrap Icons\*\* - Bibliothèque d'icônes

\- \*\*JavaScript (Vanilla)\*\* - Animations et interactivité

\- \*\*HTML5 Canvas\*\* - Animation de particules en arrière-plan



\### API Externe

\- \*\*Spotify Web API\*\* - Recherche et récupération de données musicales



---



\## 📁 Architecture du projet



```

MusicRate/

│

├── app.py                      # Application Flask principale

├── database.py                 # Gestion de la base de données SQLite

├── models.py                   # Modèles de données (User, Album, Rating, etc.)

├── spotify\_api.py              # Wrapper pour l'API Spotify

├── music\_rating.db             # Base de données SQLite (générée automatiquement)

│

├── templates/                  # Templates HTML Jinja2

│   ├── base.html              # Template de base avec navigation et styles

│   ├── index.html             # Page d'accueil

│   ├── login.html             # Page de connexion

│   ├── register.html          # Page d'inscription

│   ├── forgot\_password.html   # Demande de réinitialisation

│   ├── reset\_password.html    # Réinitialisation de mot de passe

│   ├── search.html            # Page de recherche

│   ├── album.html             # Détails d'un album

│   ├── tracklist.html         # Liste des titres d'un album

│   ├── artist.html            # Détails d'un artiste

│   ├── profile.html           # Profil utilisateur

│   ├── settings.html          # Paramètres du compte

│   ├── friends.html           # Page des amis

│   └── rating\_replies.html    # Réponses aux critiques

│

└── static/                     # Fichiers statiques

&nbsp;   ├── css/

&nbsp;   │   └── style.css          # Styles personnalisés

&nbsp;   └── uploads/

&nbsp;       └── profiles/          # Photos de profil uploadées

```



---



\## 🚀 Installation



\### Prérequis

\- \*\*Python 3.8 ou supérieur\*\*

\- \*\*pip\*\* (gestionnaire de paquets Python)

\- Un compte \*\*Spotify Developer\*\* (gratuit)



\### Étape 1 : Cloner le projet

```bash

git clone https://github.com/votre-username/musicrate.git

cd musicrate

```



\### Étape 2 : Créer un environnement virtuel (recommandé)

```bash

\# Windows

python -m venv venv

venv\\Scripts\\activate



\# Linux/Mac

python3 -m venv venv

source venv/bin/activate

```



\### Étape 3 : Installer les dépendances

```bash

pip install -r requirements.txt

```



\*\*Contenu du fichier `requirements.txt` :\*\*

```

Flask==3.0.0

spotipy==2.23.0

werkzeug==3.0.0

```



\### Étape 4 : Configurer Spotify API

1\. Allez sur \[Spotify Developer Dashboard](https://developer.spotify.com/dashboard)

2\. Créez une nouvelle application

3\. Copiez votre \*\*Client ID\*\* et \*\*Client Secret\*\*

4\. Ouvrez `app.py` et remplacez :

```python

SPOTIFY\_CLIENT\_ID = 'VOTRE\_CLIENT\_ID'

SPOTIFY\_CLIENT\_SECRET = 'VOTRE\_CLIENT\_SECRET'

```



\### Étape 5 : Lancer l'application

```bash

python app.py

```



L'application sera accessible à l'adresse : \*\*http://127.0.0.1:5000\*\*



---



\## ⚙️ Configuration



\### Variables de configuration dans `app.py`



```python

\# Clé secrète Flask (CHANGEZ-LA en production !)

app.secret\_key = 'clef\_hyper\_secrete'



\# Dossier d'upload des photos de profil

UPLOAD\_FOLDER = 'static/uploads/profiles'



\# Extensions de fichiers autorisées

ALLOWED\_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}



\# Taille maximale des fichiers (5 MB)

MAX\_FILE\_SIZE = 5 \* 1024 \* 1024



\# Identifiants Spotify API

SPOTIFY\_CLIENT\_ID = 'votre\_client\_id'

SPOTIFY\_CLIENT\_SECRET = 'votre\_client\_secret'

```



\### Base de données

La base de données SQLite (`music\_rating.db`) est créée automatiquement au premier lancement. Toutes les tables sont initialisées par le module `database.py`.



---



\## 📖 Utilisation



\### 1️⃣ Créer un compte

1\. Cliquez sur \*\*"S'inscrire"\*\* dans la navigation

2\. Remplissez le formulaire (nom d'utilisateur, email, mot de passe)

3\. Connectez-vous avec vos identifiants



\### 2️⃣ Rechercher des albums

1\. Utilisez la barre de recherche en haut

2\. Les résultats proviennent de :

&nbsp;  - \*\*Base de données locale\*\* (albums déjà ajoutés)

&nbsp;  - \*\*Spotify API\*\* (nouveaux albums)

3\. Cliquez sur \*\*"Ajouter"\*\* pour intégrer un album Spotify



\### 3️⃣ Noter un album

1\. Accédez à la page de l'album

2\. Donnez une note de 0 à 10

3\. Ajoutez une critique (optionnel)

4\. Cliquez sur \*\*"Enregistrer"\*\*



\### 4️⃣ Interagir avec la communauté

\- \*\*Suivre des utilisateurs\*\* : Visitez un profil et cliquez sur "Suivre"

\- \*\*Répondre aux critiques\*\* : Cliquez sur "Réponses" sous une critique

\- \*\*Voir l'activité de vos amis\*\* : Page "Amis"



\### 5️⃣ Personnaliser son profil

1\. Allez dans \*\*"Mon profil"\*\*

2\. Cliquez sur les boutons de modification pour :

&nbsp;  - Changer votre photo de profil

&nbsp;  - Modifier votre bio

3\. Accédez aux \*\*"Paramètres"\*\* pour :

&nbsp;  - Changer votre nom d'utilisateur

&nbsp;  - Modifier votre email

&nbsp;  - Mettre à jour votre mot de passe



---



\## 🗄 Structure de la base de données



\### Table `users`

Stocke les informations des utilisateurs.



| Colonne | Type | Description |

|---------|------|-------------|

| `id` | INTEGER (PK) | Identifiant unique |

| `username` | TEXT (UNIQUE) | Nom d'utilisateur |

| `email` | TEXT (UNIQUE) | Adresse email |

| `password\_hash` | TEXT | Mot de passe haché |

| `created\_at` | TIMESTAMP | Date d'inscription |

| `profile\_image` | TEXT | URL/chemin de la photo |

| `bio` | TEXT | Biographie (200 caractères) |



\### Table `artists`

Stocke les artistes musicaux.



| Colonne | Type | Description |

|---------|------|-------------|

| `id` | INTEGER (PK) | Identifiant unique |

| `name` | TEXT | Nom de l'artiste |

| `spotify\_id` | TEXT (UNIQUE) | ID Spotify |

| `image\_url` | TEXT | URL de l'image |

| `genres` | TEXT | Genres (séparés par virgules) |



\### Table `albums`

Stocke les albums musicaux.



| Colonne | Type | Description |

|---------|------|-------------|

| `id` | INTEGER (PK) | Identifiant unique |

| `title` | TEXT | Titre de l'album |

| `artist\_id` | INTEGER (FK) | Référence à l'artiste |

| `release\_date` | TEXT | Date de sortie |

| `spotify\_id` | TEXT (UNIQUE) | ID Spotify |

| `image\_url` | TEXT | URL de la couverture |

| `genres` | TEXT | Genres musicaux |



\### Table `ratings`

Stocke les notes données par les utilisateurs.



| Colonne | Type | Description |

|---------|------|-------------|

| `id` | INTEGER (PK) | Identifiant unique |

| `user\_id` | INTEGER (FK) | Référence à l'utilisateur |

| `album\_id` | INTEGER (FK) | Référence à l'album |

| `score` | REAL | Note (0-10) |

| `review` | TEXT | Critique textuelle |

| `created\_at` | TIMESTAMP | Date de création |



\*\*Contrainte :\*\* Un utilisateur ne peut noter qu'une seule fois un album (UNIQUE sur `user\_id`, `album\_id`).



\### Table `replies`

Stocke les réponses aux critiques.



| Colonne | Type | Description |

|---------|------|-------------|

| `id` | INTEGER (PK) | Identifiant unique |

| `rating\_id` | INTEGER (FK) | Référence à la critique |

| `user\_id` | INTEGER (FK) | Auteur de la réponse |

| `content` | TEXT | Contenu de la réponse |

| `created\_at` | TIMESTAMP | Date de création |



\### Table `follows`

Gère les relations de suivi entre utilisateurs.



| Colonne | Type | Description |

|---------|------|-------------|

| `id` | INTEGER (PK) | Identifiant unique |

| `follower\_id` | INTEGER (FK) | Utilisateur qui suit |

| `following\_id` | INTEGER (FK) | Utilisateur suivi |

| `created\_at` | TIMESTAMP | Date du suivi |



\*\*Contrainte :\*\* Un utilisateur ne peut suivre qu'une seule fois un autre utilisateur


| Colonne | Type | Description |

|---------|------|-------------|

| `id` | INTEGER (PK) | Identifiant unique |

| `artist\_id` | INTEGER (FK) | Référence à l'artiste |

| `tag\_name` | TEXT | Nom du tag (minuscules) |

| `user\_id` | INTEGER (FK) | Auteur du tag |

| `created\_at` | TIMESTAMP | Date de création |



---



\## 📚 Documentation des modules



\### `app.py` - Application Flask principale



\*\*Responsabilités :\*\*

\- Gestion des routes HTTP

\- Authentification et sessions utilisateur

\- Logique métier de l'application

\- Upload et gestion des fichiers

\- Intégration des modules externes



\*\*Routes principales :\*\*



| Route | Méthode | Description |

|-------|---------|-------------|

| `/` | GET | Page d'accueil avec classements |

| `/register` | GET, POST | Inscription |

| `/login` | GET, POST | Connexion |

| `/logout` | GET | Déconnexion |

| `/search` | GET | Recherche d'albums/artistes |

| `/album/<id>` | GET | Détails d'un album |

| `/album/<id>/rate` | POST | Noter un album |

| `/artist/<id>` | GET | Détails d'un artiste |

| `/profile/<id>` | GET | Profil utilisateur |

| `/settings` | GET | Paramètres du compte |

| `/friends` | GET | Page des amis |



\*\*Décorateur `@login\_required` :\*\*

Protège les routes nécessitant une authentification.



```python

@login\_required

def protected\_route():

&nbsp;   # Code accessible uniquement si connecté

&nbsp;   pass

```



---



\### `database.py` - Gestion de la base de données



\*\*Classe `Database` :\*\*



Gère toutes les interactions avec SQLite via des méthodes Python.



\*\*Méthodes principales :\*\*



\#### Utilisateurs

```python

create\_user(username, email, password)          # Crée un utilisateur

get\_user\_by\_username(username)                  # Récupère par nom

get\_user\_by\_id(user\_id)                         # Récupère par ID

```



\#### Artistes

```python

create\_artist(name, spotify\_id, image\_url, genres)  # Crée un artiste

get\_artist\_by\_id(artist\_id)                         # Récupère par ID

get\_artist\_by\_spotify\_id(spotify\_id)                # Récupère par Spotify ID

search\_artists(query)                               # Recherche d'artistes

```



\#### Albums

```python

create\_album(title, artist\_id, ...)             # Crée un album

get\_album\_by\_id(album\_id)                       # Récupère par ID

get\_album\_by\_spotify\_id(spotify\_id)             # Récupère par Spotify ID

get\_albums\_by\_artist(artist\_id)                 # Albums d'un artiste

search\_albums(query)                            # Recherche d'albums

```



\#### Notes et Critiques

```python

create\_rating(user\_id, album\_id, score, review) # Crée/met à jour une note

get\_album\_ratings(album\_id)                     # Toutes les notes d'un album

get\_user\_rating(user\_id, album\_id)              # Note d'un utilisateur

get\_album\_average\_rating(album\_id)              # Note moyenne

get\_top\_rated\_albums(limit)                     # Meilleurs albums

get\_worst\_rated\_albums(limit)                   # Pires albums

delete\_rating(rating\_id, user\_id)               # Supprime une note

```



\#### Réponses

```python

create\_reply(rating\_id, user\_id, content)       # Crée une réponse

get\_rating\_replies(rating\_id)                   # Récupère les réponses

get\_replies\_count(rating\_id)                    # Compte les réponses

delete\_reply(reply\_id, user\_id)                 # Supprime une réponse

```



\#### Système Social

```python

follow\_user(follower\_id, following\_id)          # Suivre un utilisateur

unfollow\_user(follower\_id, following\_id)        # Ne plus suivre

is\_following(follower\_id, following\_id)         # Vérifie si suit

get\_user\_friends(user\_id)                       # Liste des amis

get\_friends\_recent\_ratings(user\_id, limit)      # Activité des amis

```





\*\*Assertions de sécurité :\*\*

Toutes les méthodes incluent des assertions pour valider les entrées :

```python

assert isinstance(user\_id, int) and user\_id > 0, "User ID invalide"

assert isinstance(query, str) and len(query) > 0, "Query invalide"

```



---



\### `models.py` - Modèles de données



Définit les classes Python représentant les entités de la base de données.



\#### Classe `User`

```python

User(user\_id, username, email, password\_hash, created\_at, profile\_image, bio)



\# Méthodes

User.hash\_password(password)        # Hash un mot de passe

user.check\_password(password)       # Vérifie le mot de passe

```



\#### Classe `Artist`

```python

Artist(artist\_id, name, spotify\_id, image\_url, genres)



\# Méthode

artist.to\_dict()  # Convertit en dictionnaire

```



\#### Classe `Album`

```python

Album(album\_id, title, artist\_id, release\_date, spotify\_id, image\_url, genres)



\# Méthode

album.to\_dict()  # Convertit en dictionnaire

```



\#### Classe `Rating`

```python

Rating(rating\_id, user\_id, album\_id, score, review, created\_at)



\# Méthode

rating.to\_dict()  # Convertit en dictionnaire

```



\#### Classe `Reply`

```python

Reply(reply\_id, rating\_id, user\_id, content, created\_at)



\# Méthode

reply.to\_dict()  # Convertit en dictionnaire

```



\#### Classe `Follow`

```python

Follow(follow\_id, follower\_id, following\_id, created\_at)



\# Méthode

follow.to\_dict()  # Convertit en dictionnaire

```



\#### Classe `Tag`

```python

Tag(tag\_id, artist\_id, tag\_name, user\_id, created\_at)



\# Méthode

tag.to\_dict()  # Convertit en dictionnaire

```



\*\*Toutes les classes incluent des assertions de validation.\*\*



---



\### `spotify\_api.py` - Wrapper API Spotify



\*\*Classe `SpotifyAPI` :\*\*



Encapsule les appels à l'API Spotify via la bibliothèque `spotipy`.



\#### Initialisation

```python

spotify = SpotifyAPI(client\_id, client\_secret)

```



\#### Méthodes de recherche

```python

search\_albums(query, limit=10)          # Recherche d'albums

search\_artists(query, limit=10)         # Recherche d'artistes

get\_album\_details(album\_id)             # Détails complets d'un album

get\_artist\_details(artist\_id)           # Détails d'un artiste

get\_artist\_albums(artist\_id, limit=20)  # Albums d'un artiste

get\_album\_tracks(spotify\_album\_id)      # Liste des titres

get\_new\_releases(limit=20)              # Nouvelles sorties

```



\#### Formatage

```python

\_format\_duration(duration\_ms)           # Convertit ms en "min:sec"

```



\*\*Structure des données retournées :\*\*



Albums :

```python

{

&nbsp;   'id': 'spotify\_id',

&nbsp;   'name': 'Titre',

&nbsp;   'artist': 'Nom artiste',

&nbsp;   'artist\_id': 'spotify\_artist\_id',

&nbsp;   'release\_date': '2024-01-15',

&nbsp;   'image\_url': 'https://...',

&nbsp;   'spotify\_url': 'https://open.spotify.com/...',

&nbsp;   'tracks': \[...]  # Pour get\_album\_details

}

```



Artistes :

```python

{

&nbsp;   'id': 'spotify\_id',

&nbsp;   'name': 'Nom',

&nbsp;   'genres': \['rock', 'indie'],

&nbsp;   'image\_url': 'https://...',

&nbsp;   'popularity': 75,

&nbsp;   'followers': 1000000,

&nbsp;   'spotify\_url': 'https://open.spotify.com/...'

}

```



---



\## 🎧 API Spotify



\### Configuration requise



1\. \*\*Créer un compte développeur :\*\*

&nbsp;  - Allez sur \[Spotify Developer Dashboard](https://developer.spotify.com/dashboard)

&nbsp;  - Connectez-vous avec votre compte Spotify (ou créez-en un)



2\. \*\*Créer une application :\*\*

&nbsp;  - Cliquez sur "Create an App"

&nbsp;  - Nom : `MusicRate` (ou autre)

&nbsp;  - Description : Application de notation musicale

&nbsp;  - Acceptez les conditions d'utilisation



3\. \*\*Récupérer les identifiants :\*\*

&nbsp;  - Dans le dashboard de votre app, cliquez sur "Settings"

&nbsp;  - Copiez le \*\*Client ID\*\*

&nbsp;  - Cliquez sur "View client secret" et copiez le \*\*Client Secret\*\*



4\. \*\*Configurer dans l'application :\*\*

&nbsp;  ```python

&nbsp;  # app.py

&nbsp;  SPOTIFY\_CLIENT\_ID = 'votre\_client\_id\_ici'

&nbsp;  SPOTIFY\_CLIENT\_SECRET = 'votre\_client\_secret\_ici'

&nbsp;  ```



\### Limitations

\- \*\*Rate limit :\*\* 180 requêtes/minute (avec Client Credentials)

\- \*\*Pas d'authentification utilisateur\*\* nécessaire (mode lecture seule)

\- \*\*Accès aux données publiques\*\* uniquement



---



\## 🚀 Fonctionnalités avancées


\### 1. Import Automatique d'Albums



\*\*Fonctionnalité d'import en cascade :\*\*



Lorsqu'un utilisateur ajoute un album depuis Spotify, l'application :

1\. Crée l'album dans la base

2\. Crée/récupère l'artiste

3\. \*\*Importe automatiquement tous les autres albums de l'artiste\*\*



```python

def import\_artist\_albums(artist\_id, spotify\_artist\_id):

&nbsp;   """Importe tous les albums d'un artiste"""

&nbsp;   artist\_albums = spotify.get\_artist\_albums(spotify\_artist\_id)

&nbsp;   

&nbsp;   for album\_data in artist\_albums:

&nbsp;       if not db.get\_album\_by\_spotify\_id(album\_data\['id']):

&nbsp;           db.create\_album(...)  # Crée l'album

```



\*\*Avantage :\*\* Enrichit rapidement la base de données.



\### 2. Système de Réponses aux Critiques



\*\*Architecture de conversation :\*\*

\- Chaque critique peut avoir \*\*plusieurs réponses\*\*

\- Page dédiée avec fil de discussion

\- Badge indiquant le nombre de réponses

\- Suppression par l'auteur uniquement



\*\*Workflow :\*\*

```

Critique (Rating)

&nbsp;   ├── Réponse 1 (Reply)

&nbsp;   ├── Réponse 2 (Reply)

&nbsp;   └── Réponse 3 (Reply)

```



\### 3. Animation de Fond Canvas



\*\*Système de particules interactives :\*\*



Le fichier `base.html` inclut une animation JavaScript créant un effet visuel dynamique :



```javascript

// 50 particules violettes flottantes

// Lignes reliant les particules proches

// Gradients lumineux radials

// Performance optimisée avec requestAnimationFrame

```



\*\*Caractéristiques :\*\*

\- 50 particules animées

\- Lignes dynamiques entre particules proches

\- Gradients lumineux en arrière-plan

\- Adaptation automatique à la taille de l'écran



\### 5. Upload de Photos de Profil



\*\*Double méthode d'upload :\*\*



\*\*Méthode 1 - Upload de fichier :\*\*

```python

\# Validation du fichier

\- Extensions autorisées : png, jpg, jpeg, gif, webp

\- Taille max : 5 MB

\- Nom sécurisé avec secure\_filename()

\- Prévisualisation avant upload

```



\*\*Méthode 2 - URL externe :\*\*

```python

\# L'utilisateur peut coller une URL d'image hébergée

\- Validation basique (http/https)

\- Stockage direct de l'URL

```



\*\*Gestion automatique :\*\*

\- Suppression de l'ancienne image lors d'un remplacement

\- Noms de fichiers uniques avec timestamp



\### 6. Récupération de Mot de Passe



\*\*Système de tokens sécurisés :\*\*



```python

\# Génération d'un token aléatoire

token = secrets.token\_urlsafe(32)



\# Expiration après 1 heure

expiry = datetime.now() + timedelta(hours=1)



\# Stockage temporaire en mémoire

reset\_tokens\[token] = {

&nbsp;   'user\_id': user\_id,

&nbsp;   'email': email,

&nbsp;   'expiry': expiry

}

```



\*\*Flow de réinitialisation :\*\*

1\. L'utilisateur entre son email

2\. Un token est généré et associé au compte

3\. Le lien de réinitialisation contient le token

4\. Validation du token à l'ouverture

5\. Changement de mot de passe et suppression du token



---





