# -*- coding: utf-8 -*-

"""
Ce fichier gère toute la base de données SQLite pour notre appli de notation de musique.
C'est comme un bibliothécaire qui range et retrouve toutes nos infos (utilisateurs, albums, notes, etc.)
"""

# On importe les modules nécessaires
import sqlite3  # Pour créer et gérer notre base de données
from datetime import datetime  # Pour gérer les dates et heures
from models import User, Artist, Album, Rating, Reply, Follow, Tag  # Nos "moules" pour créer des objets



class Database:
    """
    Cette classe est notre gestionnaire de base de données.
    Elle contient toutes les fonctions pour créer, lire, modifier et supprimer des données.
    """
    
    def __init__(self, db_path='music_rating.db'):
        """
        Cette fonction s'exécute automatiquement quand on crée un objet Database.
        db_path : le chemin vers notre fichier de base de données (par défaut: music_rating.db)
        """
        # On vérifie que le chemin est bien une chaîne de caractères non vide
        assert isinstance(db_path, str) and len(db_path) > 0, "DB path doit être une chaîne non vide"
        self.db_path = db_path  # On sauvegarde le chemin
        self.init_database()  # On crée les tables si elles n'existent pas encore
    
    def get_connection(self):
        """
        Crée une connexion à la base de données.
        C'est comme ouvrir le livre avant de le lire ou d'écrire dedans.
        """
        conn = sqlite3.connect(self.db_path)  # On se connecte au fichier SQLite
        conn.row_factory = sqlite3.Row  # Permet d'accéder aux colonnes par leur nom (plus pratique!)
        return conn
    
    def delete_rating(self, rating_id, user_id):
        """
        Supprime une note, mais seulement si c'est l'utilisateur qui l'a créée qui demande.
        rating_id : l'ID de la note à supprimer
        user_id : l'ID de l'utilisateur qui veut supprimer
        Retourne True si la suppression a réussi, False sinon
        """
        conn = self.get_connection()  # On ouvre la connexion
        cursor = conn.cursor()  # Le curseur permet d'exécuter des commandes SQL
        
        # On cherche la note avec cet ID ET cet utilisateur
        cursor.execute('SELECT * FROM ratings WHERE id = ? AND user_id = ?', (rating_id, user_id))
        rating = cursor.fetchone()  # On récupère le résultat
        
        if rating:  # Si on a trouvé la note (= l'utilisateur est bien l'auteur)
            cursor.execute('DELETE FROM ratings WHERE id = ?', (rating_id,))
            conn.commit()  # On valide les changements
            conn.close()  # On ferme la connexion
            return True
        
        conn.close()
        return False  # La note n'existe pas ou l'utilisateur n'est pas l'auteur

    def delete_tag(self, tag_id, user_id):
        """
        Supprime un tag, mais seulement si c'est l'utilisateur qui l'a créé.
        Fonctionne exactement comme delete_rating mais pour les tags.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # On vérifie que le tag appartient bien à l'utilisateur
        cursor.execute('SELECT * FROM tags WHERE id = ? AND user_id = ?', (tag_id, user_id))
        tag = cursor.fetchone()
        
        if tag:
            cursor.execute('DELETE FROM tags WHERE id = ?', (tag_id,))
            conn.commit()
            conn.close()
            return True
        
        conn.close()
        return False
    
    
    
    def init_database(self):
        """
        Cette fonction crée toutes les tables de notre base de données si elles n'existent pas.
        C'est comme créer les différentes sections d'un classeur.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # ===== TABLE DES UTILISATEURS =====
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,  -- ID unique qui s'incrémente automatiquement
                username TEXT UNIQUE NOT NULL,  -- Nom d'utilisateur (doit être unique)
                email TEXT UNIQUE NOT NULL,  -- Email (doit être unique)
                password_hash TEXT NOT NULL,  -- Mot de passe crypté (jamais en clair!)
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Date de création du compte
                profile_image TEXT,  -- URL de l'image de profil (peut être vide)
                bio TEXT,  -- Biographie de l'utilisateur
                casino_tokens INTEGER DEFAULT 1000  -- Jetons de casino (système de points)
            )
        ''')
        
        # On vérifie si la colonne casino_tokens existe déjà, sinon on l'ajoute
        # (utile pour les anciennes bases de données)
        cursor.execute("PRAGMA table_info(users)")  # PRAGMA = commande spéciale SQLite
        columns = [column[1] for column in cursor.fetchall()]  # On récupère les noms de colonnes
        if 'casino_tokens' not in columns:  # Si la colonne n'existe pas
            cursor.execute('ALTER TABLE users ADD COLUMN casino_tokens INTEGER DEFAULT 1000')
        
        # ===== TABLE DES ARTISTES =====
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS artists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,  -- Nom de l'artiste
                spotify_id TEXT UNIQUE,  -- ID Spotify (pour synchroniser avec Spotify)
                image_url TEXT,  -- Photo de l'artiste
                genres TEXT  -- Les genres musicaux (stockés comme texte séparé par des virgules)
            )
        ''')
        
        # ===== TABLE DES ALBUMS =====
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS albums (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,  -- Titre de l'album
                artist_id INTEGER NOT NULL,  -- Lien vers l'artiste (clé étrangère)
                release_date TEXT,  -- Date de sortie
                spotify_id TEXT UNIQUE,
                image_url TEXT,  -- Pochette de l'album
                genres TEXT,
                FOREIGN KEY (artist_id) REFERENCES artists (id)  -- Lie cet album à un artiste
            )
        ''')
        
        # ===== TABLE DES NOTES =====
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,  -- Qui a mis cette note?
                album_id INTEGER NOT NULL,  -- Sur quel album?
                score REAL NOT NULL,  -- La note (nombre décimal entre 0 et 10)
                review TEXT,  -- La critique écrite (optionnelle)
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (album_id) REFERENCES albums (id),
                UNIQUE(user_id, album_id)  -- Un utilisateur ne peut noter qu'une fois le même album
            )
        ''')
        
        # ===== TABLE DES RÉPONSES AUX CRITIQUES =====
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS replies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rating_id INTEGER NOT NULL,  -- À quelle critique cette réponse répond?
                user_id INTEGER NOT NULL,  -- Qui a écrit cette réponse?
                content TEXT NOT NULL,  -- Le contenu de la réponse
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (rating_id) REFERENCES ratings (id) ON DELETE CASCADE,  -- Si on supprime la critique, on supprime aussi les réponses
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # ===== TABLE DES SUIVIS (qui suit qui?) =====
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS follows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                follower_id INTEGER NOT NULL,  -- Qui suit?
                following_id INTEGER NOT NULL,  -- Qui est suivi?
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (follower_id) REFERENCES users (id),
                FOREIGN KEY (following_id) REFERENCES users (id),
                UNIQUE(follower_id, following_id)  -- On ne peut pas suivre 2 fois la même personne
            )
        ''')
        
        # ===== TABLE DES TAGS =====
        # Les tags sont des mots-clés qu'on peut ajouter aux artistes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                artist_id INTEGER NOT NULL,  -- Sur quel artiste?
                tag_name TEXT NOT NULL,  -- Le nom du tag (ex: "rock", "années 80")
                user_id INTEGER NOT NULL,  -- Qui a ajouté ce tag?
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (artist_id) REFERENCES artists (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # ===== TABLE DES ALBUMS FAVORIS =====
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorite_albums (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                album_id INTEGER NOT NULL,
                position INTEGER NOT NULL,  -- Position dans le top (1er, 2ème, etc.)
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (album_id) REFERENCES albums (id),
                UNIQUE(user_id, album_id)
            )
        ''')
        
        # ===== INDEX POUR AMÉLIORER LES PERFORMANCES =====
        # Un index, c'est comme un sommaire : ça permet de trouver plus vite les infos
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_replies_rating_id 
            ON replies(rating_id)
        ''')
        
        conn.commit()  # On valide toutes les créations de tables
        conn.close()
    
    # ========== FONCTIONS POUR LES UTILISATEURS ==========
    
    def create_user(self, username, email, password):
        """
        Crée un nouvel utilisateur dans la base de données.
        Le mot de passe est automatiquement crypté pour la sécurité.
        Retourne l'ID du nouvel utilisateur, ou None si ça a échoué (nom/email déjà pris)
        """
        # On vérifie que les données sont valides
        assert isinstance(username, str) and len(username) > 0, "Username invalide"
        assert isinstance(email, str) and '@' in email, "Email invalide"
        
        password_hash = User.hash_password(password)  # On crypte le mot de passe
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # On essaie d'insérer le nouvel utilisateur
            cursor.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, password_hash)
            )
            conn.commit()
            user_id = cursor.lastrowid  # lastrowid = dernier ID créé
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            # Erreur = le nom ou l'email existe déjà (UNIQUE constraint)
            conn.close()
            return None
    
    def get_user_by_username(self, username):
        """
        Cherche un utilisateur par son nom d'utilisateur.
        Retourne un objet User s'il existe, None sinon.
        """
        assert isinstance(username, str), "Username doit être une chaîne"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()  # fetchone() = récupère UNE ligne
        conn.close()
        
        if row:  # Si on a trouvé quelque chose
            # On essaie de récupérer les nouvelles colonnes (peuvent ne pas exister dans vieilles BDD)
            try:
                profile_image = row['profile_image']
                bio = row['bio']
            except (KeyError, IndexError):
                profile_image = None
                bio = None
            
            # On crée et retourne un objet User
            return User(row['id'], row['username'], row['email'], 
                    row['password_hash'], row['created_at'], 
                    profile_image, bio)
        return None

    def get_user_by_id(self, user_id):
        """
        Cherche un utilisateur par son ID.
        Fonctionne comme get_user_by_username mais avec l'ID.
        """
        assert isinstance(user_id, int) and user_id > 0, "User ID invalide"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            try:
                profile_image = row['profile_image']
                bio = row['bio']
            except (KeyError, IndexError):
                profile_image = None
                bio = None
            
            return User(row['id'], row['username'], row['email'], 
                    row['password_hash'], row['created_at'],
                    profile_image, bio)
        return None
    
    # ========== FONCTIONS POUR LES ARTISTES ==========
    
    def create_artist(self, name, spotify_id=None, image_url=None, genres=None):
        """
        Crée un nouvel artiste.
        genres est une liste de chaînes, qu'on va joindre avec des virgules pour stocker.
        """
        assert isinstance(name, str) and len(name) > 0, "Name invalide"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        # On transforme la liste de genres en texte: ["rock", "pop"] → "rock,pop"
        genres_str = ','.join(genres) if genres else None
        
        try:
            cursor.execute(
                'INSERT INTO artists (name, spotify_id, image_url, genres) VALUES (?, ?, ?, ?)',
                (name, spotify_id, image_url, genres_str)
            )
            conn.commit()
            artist_id = cursor.lastrowid
            conn.close()
            return artist_id
        except sqlite3.IntegrityError:
            conn.close()
            return None
    
    def get_artist_by_id(self, artist_id):
        """Récupère un artiste par son ID"""
        assert isinstance(artist_id, int) and artist_id > 0, "Artist ID invalide"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM artists WHERE id = ?', (artist_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            # On retransforme le texte en liste: "rock,pop" → ["rock", "pop"]
            genres = row['genres'].split(',') if row['genres'] else []
            return Artist(row['id'], row['name'], row['spotify_id'], 
                         row['image_url'], genres)
        return None
    
    def get_artist_by_spotify_id(self, spotify_id):
        """Récupère un artiste par son ID Spotify (utile pour synchroniser avec l'API Spotify)"""
        assert isinstance(spotify_id, str), "Spotify ID doit être une chaîne"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM artists WHERE spotify_id = ?', (spotify_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            genres = row['genres'].split(',') if row['genres'] else []
            return Artist(row['id'], row['name'], row['spotify_id'], 
                         row['image_url'], genres)
        return None
    
    def search_artists(self, query):
        """
        Cherche des artistes dont le nom contient 'query'.
        Exemple: query="Beat" va trouver "The Beatles"
        LIKE '%query%' = contient 'query' n'importe où dans le nom
        """
        assert isinstance(query, str), "Query doit être une chaîne"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM artists WHERE name LIKE ? LIMIT 20', 
                      (f'%{query}%',))  # % = joker (n'importe quels caractères)
        rows = cursor.fetchall()  # fetchall() = récupère TOUTES les lignes
        conn.close()
        
        # On transforme chaque ligne en objet Artist
        artists = []
        for row in rows:
            genres = row['genres'].split(',') if row['genres'] else []
            artists.append(Artist(row['id'], row['name'], row['spotify_id'], 
                                 row['image_url'], genres))
        return artists
    
    # ========== FONCTIONS POUR LES ALBUMS ==========
    
    def create_album(self, title, artist_id, release_date=None, 
                    spotify_id=None, image_url=None, genres=None):
        """Crée un nouvel album"""
        assert isinstance(title, str) and len(title) > 0, "Title invalide"
        assert isinstance(artist_id, int) and artist_id > 0, "Artist ID invalide"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        genres_str = ','.join(genres) if genres else None
        
        try:
            cursor.execute(
                '''INSERT INTO albums (title, artist_id, release_date, spotify_id, image_url, genres) 
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (title, artist_id, release_date, spotify_id, image_url, genres_str)
            )
            conn.commit()
            album_id = cursor.lastrowid
            conn.close()
            return album_id
        except sqlite3.IntegrityError:
            conn.close()
            return None
    
    def get_album_by_id(self, album_id):
        """Récupère un album par son ID"""
        assert isinstance(album_id, int) and album_id > 0, "Album ID invalide"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM albums WHERE id = ?', (album_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            genres = row['genres'].split(',') if row['genres'] else []
            return Album(row['id'], row['title'], row['artist_id'], 
                        row['release_date'], row['spotify_id'], 
                        row['image_url'], genres)
        return None
    
    def get_album_by_spotify_id(self, spotify_id):
        """Récupère un album par son ID Spotify"""
        assert isinstance(spotify_id, str), "Spotify ID doit être une chaîne"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM albums WHERE spotify_id = ?', (spotify_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            genres = row['genres'].split(',') if row['genres'] else []
            return Album(row['id'], row['title'], row['artist_id'], 
                        row['release_date'], row['spotify_id'], 
                        row['image_url'], genres)
        return None
    
    def get_albums_by_artist(self, artist_id):
        """Récupère tous les albums d'un artiste donné"""
        assert isinstance(artist_id, int) and artist_id > 0, "Artist ID invalide"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM albums WHERE artist_id = ?', (artist_id,))
        rows = cursor.fetchall()
        conn.close()
        
        albums = []
        for row in rows:
            genres = row['genres'].split(',') if row['genres'] else []
            albums.append(Album(row['id'], row['title'], row['artist_id'], 
                               row['release_date'], row['spotify_id'], 
                               row['image_url'], genres))
        return albums
    
    def search_albums(self, query):
        """Cherche des albums dont le titre contient 'query'"""
        assert isinstance(query, str), "Query doit être une chaîne"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM albums WHERE title LIKE ? LIMIT 20', 
                      (f'%{query}%',))
        rows = cursor.fetchall()
        conn.close()
        
        albums = []
        for row in rows:
            genres = row['genres'].split(',') if row['genres'] else []
            albums.append(Album(row['id'], row['title'], row['artist_id'], 
                               row['release_date'], row['spotify_id'], 
                               row['image_url'], genres))
        return albums
    
    # ========== FONCTIONS POUR LES NOTES ==========
    
    def create_rating(self, user_id, album_id, score, review=None):
        """
        Crée une nouvelle note pour un album.
        Si l'utilisateur a déjà noté cet album, la note sera mise à jour.
        """
        assert isinstance(user_id, int) and user_id > 0, "User ID invalide"
        assert isinstance(album_id, int) and album_id > 0, "Album ID invalide"
        assert 0 <= score <= 10, "Score doit être entre 0 et 10"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # On essaie d'insérer une nouvelle note
            cursor.execute(
                '''INSERT INTO ratings (user_id, album_id, score, review) 
                   VALUES (?, ?, ?, ?)''',
                (user_id, album_id, score, review)
            )
            conn.commit()
            rating_id = cursor.lastrowid
            conn.close()
            return rating_id
        except sqlite3.IntegrityError:
            # Si la note existe déjà (UNIQUE constraint), on la met à jour
            cursor.execute(
                '''UPDATE ratings SET score = ?, review = ? 
                   WHERE user_id = ? AND album_id = ?''',
                (score, review, user_id, album_id)
            )
            conn.commit()
            conn.close()
            return True
    
    def get_album_ratings(self, album_id):
        """Récupère toutes les notes d'un album donné"""
        assert isinstance(album_id, int) and album_id > 0, "Album ID invalide"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM ratings WHERE album_id = ?', (album_id,))
        rows = cursor.fetchall()
        conn.close()
        
        ratings = []
        for row in rows:
            ratings.append(Rating(row['id'], row['user_id'], row['album_id'], 
                                 row['score'], row['review'], row['created_at']))
        return ratings
    
    def get_user_rating(self, user_id, album_id):
        """Récupère la note d'un utilisateur spécifique pour un album spécifique"""
        assert isinstance(user_id, int) and user_id > 0, "User ID invalide"
        assert isinstance(album_id, int) and album_id > 0, "Album ID invalide"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM ratings WHERE user_id = ? AND album_id = ?', 
                      (user_id, album_id))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Rating(row['id'], row['user_id'], row['album_id'], 
                         row['score'], row['review'], row['created_at'])
        return None
    
    def get_album_average_rating(self, album_id):
        """
        Calcule la note moyenne d'un album.
        AVG() = fonction SQL qui calcule la moyenne
        """
        assert isinstance(album_id, int) and album_id > 0, "Album ID invalide"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT AVG(score) as avg FROM ratings WHERE album_id = ?', 
                      (album_id,))
        row = cursor.fetchone()
        conn.close()
        
        # round() arrondit à 2 décimales (ex: 7.666667 → 7.67)
        return round(row['avg'], 2) if row['avg'] else 0
    
    def get_top_rated_albums(self, limit=10):
        """
        Récupère les albums les mieux notés.
        On ne garde que les albums avec au moins 3 notes (pour éviter qu'un album avec une seule note de 10 soit premier)
        """
        assert isinstance(limit, int) and limit > 0, "Limit doit être positif"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT album_id, AVG(score) as avg_score, COUNT(*) as num_ratings
            FROM ratings
            GROUP BY album_id
            HAVING num_ratings >= 3
            ORDER BY avg_score DESC
            LIMIT ?
        ''', (limit,))
        # GROUP BY = regroupe par album
        # HAVING = filtre après le regroupement (comme WHERE mais pour les groupes)
        # ORDER BY DESC = trie du plus grand au plus petit
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            album = self.get_album_by_id(row['album_id'])
            if album:
                results.append({
                    'album': album,
                    'avg_score': round(row['avg_score'], 2),
                    'num_ratings': row['num_ratings']
                })
        return results
    
    # ========== FONCTIONS POUR LES RÉPONSES AUX CRITIQUES ==========
    
    def create_reply(self, rating_id, user_id, content):
        """Crée une nouvelle réponse à une critique"""
        assert isinstance(rating_id, int) and rating_id > 0, "Rating ID invalide"
        assert isinstance(user_id, int) and user_id > 0, "User ID invalide"
        assert isinstance(content, str) and len(content) > 0, "Content invalide"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO replies (rating_id, user_id, content) VALUES (?, ?, ?)',
            (rating_id, user_id, content)
        )
        conn.commit()
        reply_id = cursor.lastrowid
        conn.close()
        return reply_id
    
    def get_rating_replies(self, rating_id):
        """
        Récupère toutes les réponses d'une critique donnée.
        ORDER BY created_at ASC = trie par date croissante (les plus anciennes d'abord)
        """
        assert isinstance(rating_id, int) and rating_id > 0, "Rating ID invalide"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM replies WHERE rating_id = ? ORDER BY created_at ASC', 
            (rating_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        replies = []
        for row in rows:
            replies.append(Reply(row['id'], row['rating_id'], row['user_id'], 
                               row['content'], row['created_at']))
        return replies
    
    def get_replies_count(self, rating_id):
        """Compte le nombre de réponses pour une critique"""
        assert isinstance(rating_id, int) and rating_id > 0, "Rating ID invalide"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM replies WHERE rating_id = ?', (rating_id,))
        row = cursor.fetchone()
        conn.close()
        return row['count'] if row else 0
    
    def delete_reply(self, reply_id, user_id):
        """Supprime une réponse (seulement si c'est l'auteur)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # On vérifie que la réponse appartient bien à l'utilisateur
        cursor.execute('SELECT * FROM replies WHERE id = ? AND user_id = ?', (reply_id, user_id))
        reply = cursor.fetchone()
        
        if reply:
            cursor.execute('DELETE FROM replies WHERE id = ?', (reply_id,))
            conn.commit()
            conn.close()
            return True
        
        conn.close()
        return False
    
    # ========== FONCTIONS POUR LES SUIVIS (système d'amis) ==========
    
    def follow_user(self, follower_id, following_id):
        """
        Permet à un utilisateur d'en suivre un autre.
        follower_id = celui qui suit
        following_id = celui qui est suivi
        """
        assert isinstance(follower_id, int) and follower_id > 0, "Follower ID invalide"
        assert isinstance(following_id, int) and following_id > 0, "Following ID invalide"
        assert follower_id != following_id, "Impossible de se suivre soi-même"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO follows (follower_id, following_id) VALUES (?, ?)',
                (follower_id, following_id)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # Erreur = on suit déjà cette personne
            conn.close()
            return False
    
    def unfollow_user(self, follower_id, following_id):
        """Permet à un utilisateur d'arrêter de suivre un autre"""
        assert isinstance(follower_id, int) and follower_id > 0, "Follower ID invalide"
        assert isinstance(following_id, int) and following_id > 0, "Following ID invalide"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'DELETE FROM follows WHERE follower_id = ? AND following_id = ?',
            (follower_id, following_id)
        )
        conn.commit()
        conn.close()
        return True
    
    def is_following(self, follower_id, following_id):
        """
        Vérifie si un utilisateur en suit un autre.
        Retourne True si oui, False sinon.
        """
        assert isinstance(follower_id, int) and follower_id > 0, "Follower ID invalide"
        assert isinstance(following_id, int) and following_id > 0, "Following ID invalide"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM follows WHERE follower_id = ? AND following_id = ?',
            (follower_id, following_id)
        )
        result = cursor.fetchone()
        conn.close()
        return result is not None  # Si result existe = True, sinon = False
    
    # ========== FONCTIONS POUR LES TAGS ==========
    
    def create_tag(self, artist_id, tag_name, user_id):
        """
        Ajoute un tag à un artiste (comme des hashtags).
        Exemple: ajouter "indie" à l'artiste Arctic Monkeys
        """
        assert isinstance(artist_id, int) and artist_id > 0, "Artist ID invalide"
        assert isinstance(tag_name, str) and len(tag_name) > 0, "Tag name invalide"
        assert isinstance(user_id, int) and user_id > 0, "User ID invalide"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO tags (artist_id, tag_name, user_id) VALUES (?, ?, ?)',
            (artist_id, tag_name.lower(), user_id)  # .lower() = tout en minuscules pour cohérence
        )
        conn.commit()
        tag_id = cursor.lastrowid
        conn.close()
        return tag_id
    
    def get_artist_tags(self, artist_id):
        """
        Récupère tous les tags d'un artiste avec le nombre de fois qu'ils ont été utilisés.
        Exemple: "indie" x5, "rock" x3
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, tag_name, user_id, COUNT(*) as count 
            FROM tags 
            WHERE artist_id = ? 
            GROUP BY tag_name
            ORDER BY count DESC
        ''', (artist_id,))
        # COUNT(*) compte combien de fois chaque tag apparaît
        tags = cursor.fetchall()
        conn.close()
        return tags
    
    def get_worst_rated_albums(self, limit=10):
        """
        Récupère les albums les MOINS bien notés.
        C'est l'inverse de get_top_rated_albums (ORDER BY ASC au lieu de DESC)
        """
        assert isinstance(limit, int) and limit > 0, "Limit doit être positif"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT album_id, AVG(score) as avg_score, COUNT(*) as num_ratings
            FROM ratings
            GROUP BY album_id
            HAVING num_ratings >= 3
            ORDER BY avg_score ASC
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            album = self.get_album_by_id(row['album_id'])
            if album:
                results.append({
                    'album': album,
                    'avg_score': round(row['avg_score'], 2),
                    'num_ratings': row['num_ratings']
                })
        return results

    def get_user_favorite_genres(self, user_id):
        """
        Trouve les genres préférés d'un utilisateur en analysant ses bonnes notes.
        On regarde les albums qu'il a notés > 6.5/10
        """
        assert isinstance(user_id, int) and user_id > 0, "User ID invalide"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # On récupère les genres des albums bien notés par l'utilisateur
        cursor.execute('''
            SELECT albums.genres
            FROM ratings
            JOIN albums ON ratings.album_id = albums.id
            WHERE ratings.user_id = ? AND ratings.score > 6.5
        ''', (user_id,))
        # JOIN = on relie la table ratings avec la table albums pour avoir les infos des deux
        
        rows = cursor.fetchall()
        conn.close()
        
        # On compte combien de fois chaque genre apparaît
        genre_counts = {}  # Dictionnaire pour compter: {"rock": 5, "pop": 3, ...}
        for row in rows:
            if row['genres']:  # Si l'album a des genres
                genres = row['genres'].split(',')  # On sépare: "rock,pop" → ["rock", "pop"]
                for genre in genres:
                    genre = genre.strip()  # .strip() enlève les espaces inutiles
                    if genre:
                        # On incrémente le compteur pour ce genre
                        genre_counts[genre] = genre_counts.get(genre, 0) + 1
        
        # On trie les genres par nombre d'occurrences (du plus au moins fréquent)
        sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
        # lambda x: x[1] = on trie par la valeur (le nombre), pas par la clé (le nom du genre)
        
        return [genre for genre, count in sorted_genres[:5]]  # On retourne les 5 premiers

    def get_user_favorite_artists(self, user_id):
        """
        Trouve les artistes préférés d'un utilisateur.
        On regarde les artistes dont il a bien noté les albums (> 6.5)
        """
        assert isinstance(user_id, int) and user_id > 0, "User ID invalide"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT albums.artist_id, COUNT(*) as count, AVG(ratings.score) as avg_score
            FROM ratings
            JOIN albums ON ratings.album_id = albums.id
            WHERE ratings.user_id = ? AND ratings.score > 6.5
            GROUP BY albums.artist_id
            ORDER BY avg_score DESC, count DESC
            LIMIT 5
        ''', (user_id,))
        # On regroupe par artiste, on compte combien d'albums bien notés, et on calcule la moyenne
        
        rows = cursor.fetchall()
        conn.close()
        
        return [row['artist_id'] for row in rows]

    def get_recommended_albums(self, user_id, limit=12):
        """
        ALGORITHME DE RECOMMANDATION !
        Cette fonction recommande des albums à un utilisateur basé sur ses goûts.
        C'est comme Netflix qui te propose des films basés sur ce que tu as aimé.
        """
        assert isinstance(user_id, int) and user_id > 0, "User ID invalide"
        
        # === ÉTAPE 1: On analyse les goûts de l'utilisateur ===
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # On compte combien d'albums l'utilisateur a bien notés
        cursor.execute('SELECT COUNT(*) as count FROM ratings WHERE user_id = ? AND score > 6.5', (user_id,))
        high_ratings_count = cursor.fetchone()['count']
        
        print(f"[DEBUG] User {user_id} a {high_ratings_count} notes > 6.5")
        
        # On récupère ses genres et artistes préférés
        favorite_genres = self.get_user_favorite_genres(user_id)
        favorite_artists = self.get_user_favorite_artists(user_id)
        
        print(f"[DEBUG] Genres favoris: {favorite_genres}")
        print(f"[DEBUG] Artistes favoris: {favorite_artists}")
        
        # Si l'utilisateur n'a pas assez noté d'albums, on lui propose juste des albums populaires
        if not favorite_genres and not favorite_artists:
            print("[DEBUG] Pas de préférences, retour albums populaires")
            conn.close()
            return self.get_popular_unrated_albums(user_id, limit)
        
        # === ÉTAPE 2: On récupère les albums déjà notés pour ne pas les recommander ===
        cursor.execute('SELECT album_id FROM ratings WHERE user_id = ?', (user_id,))
        rated_album_ids = [row['album_id'] for row in cursor.fetchall()]
        
        print(f"[DEBUG] Albums déjà notés: {rated_album_ids}")
        
        recommendations = []
        
        # === ÉTAPE 3: On cherche des albums d'artistes similaires ===
        if favorite_artists:
            # On crée une requête SQL dynamique avec le bon nombre de "?"
            placeholders = ','.join('?' * len(favorite_artists))
            
            # Si l'utilisateur a déjà noté des albums, on les exclut
            if rated_album_ids:
                rated_placeholders = ','.join('?' * len(rated_album_ids))
                query = f'''
                    SELECT albums.*, AVG(ratings.score) as avg_score, COUNT(ratings.id) as num_ratings
                    FROM albums
                    LEFT JOIN ratings ON albums.id = ratings.album_id
                    WHERE albums.artist_id IN ({placeholders})
                    AND albums.id NOT IN ({rated_placeholders})
                    GROUP BY albums.id
                    HAVING num_ratings >= 1
                    ORDER BY avg_score DESC
                    LIMIT ?
                '''
                cursor.execute(query, (*favorite_artists, *rated_album_ids, limit // 2))
                # *favorite_artists décompresse la liste: [1,2,3] → 1,2,3
                # limit // 2 = on prend la moitié du nombre demandé
            else:
                query = f'''
                    SELECT albums.*, AVG(ratings.score) as avg_score, COUNT(ratings.id) as num_ratings
                    FROM albums
                    LEFT JOIN ratings ON albums.id = ratings.album_id
                    WHERE albums.artist_id IN ({placeholders})
                    GROUP BY albums.id
                    HAVING num_ratings >= 1
                    ORDER BY avg_score DESC
                    LIMIT ?
                '''
                cursor.execute(query, (*favorite_artists, limit // 2))
            
            rows = cursor.fetchall()
            print(f"[DEBUG] Trouvé {len(rows)} albums d'artistes similaires")
            
            # On transforme chaque résultat en objet Album et on l'ajoute aux recommandations
            for row in rows:
                genres = row['genres'].split(',') if row['genres'] else []
                album = Album(row['id'], row['title'], row['artist_id'],
                            row['release_date'], row['spotify_id'],
                            row['image_url'], genres)
                recommendations.append({
                    'album': album,
                    'avg_score': round(row['avg_score'], 2) if row['avg_score'] else 0,
                    'num_ratings': row['num_ratings'],
                    'reason': 'Artiste similaire'  # Pourquoi on recommande cet album
                })
        
        # === ÉTAPE 4: On complète avec des albums de genres similaires ===
        if favorite_genres and len(recommendations) < limit:
            # On exclut les albums déjà recommandés et déjà notés
            already_recommended_ids = [item['album'].id for item in recommendations]
            all_excluded = rated_album_ids + already_recommended_ids
            
            if all_excluded:
                excluded_placeholders = ','.join('?' * len(all_excluded))
                query = f'''
                    SELECT albums.*, AVG(ratings.score) as avg_score, COUNT(ratings.id) as num_ratings
                    FROM albums
                    LEFT JOIN ratings ON albums.id = ratings.album_id
                    WHERE albums.genres IS NOT NULL 
                    AND albums.id NOT IN ({excluded_placeholders})
                    GROUP BY albums.id
                    HAVING num_ratings >= 1
                    ORDER BY avg_score DESC
                    LIMIT ?
                '''
                cursor.execute(query, (*all_excluded, limit * 2))
            else:
                cursor.execute('''
                    SELECT albums.*, AVG(ratings.score) as avg_score, COUNT(ratings.id) as num_ratings
                    FROM albums
                    LEFT JOIN ratings ON albums.id = ratings.album_id
                    WHERE albums.genres IS NOT NULL
                    GROUP BY albums.id
                    HAVING num_ratings >= 1
                    ORDER BY avg_score DESC
                    LIMIT ?
                ''', (limit * 2,))
            
            rows = cursor.fetchall()
            print(f"[DEBUG] Trouvé {len(rows)} albums potentiels pour genres similaires")
            
            # On vérifie que l'album a au moins un genre en commun avec les préférences
            for row in rows:
                if len(recommendations) >= limit:  # On s'arrête quand on a assez de recommandations
                    break
                
                album_genres = row['genres'].split(',') if row['genres'] else []
                # On vérifie si au moins un genre correspond
                # any() retourne True si AU MOINS un élément de la liste est True
                if any(genre.strip() in favorite_genres for genre in album_genres):
                    genres = row['genres'].split(',') if row['genres'] else []
                    album = Album(row['id'], row['title'], row['artist_id'],
                                row['release_date'], row['spotify_id'],
                                row['image_url'], genres)
                    recommendations.append({
                        'album': album,
                        'avg_score': round(row['avg_score'], 2) if row['avg_score'] else 0,
                        'num_ratings': row['num_ratings'],
                        'reason': 'Genre similaire'
                    })
        
        conn.close()
        
        print(f"[DEBUG] Total recommandations: {len(recommendations)}")
        return recommendations[:limit]  # On retourne au maximum 'limit' recommandations

    def get_popular_unrated_albums(self, user_id, limit=12):
        """
        Récupère des albums populaires que l'utilisateur n'a pas encore notés.
        Utilisé comme solution de secours pour les nouveaux utilisateurs.
        """
        assert isinstance(user_id, int) and user_id > 0, "User ID invalide"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # On récupère les albums déjà notés par l'utilisateur
        cursor.execute('SELECT album_id FROM ratings WHERE user_id = ?', (user_id,))
        rated_album_ids = [row['album_id'] for row in cursor.fetchall()]
        
        # On récupère les albums populaires qui n'ont pas été notés par l'utilisateur
        if rated_album_ids:
            placeholders = ','.join('?' * len(rated_album_ids))
            query = f'''
                SELECT albums.*, AVG(ratings.score) as avg_score, COUNT(ratings.id) as num_ratings
                FROM albums
                LEFT JOIN ratings ON albums.id = ratings.album_id
                WHERE albums.id NOT IN ({placeholders})
                GROUP BY albums.id
                HAVING num_ratings >= 3
                ORDER BY avg_score DESC, num_ratings DESC
                LIMIT ?
            '''
            cursor.execute(query, (*rated_album_ids, limit))
        else:
            # Si l'utilisateur n'a encore rien noté, on prend juste les plus populaires
            cursor.execute('''
                SELECT albums.*, AVG(ratings.score) as avg_score, COUNT(ratings.id) as num_ratings
                FROM albums
                LEFT JOIN ratings ON albums.id = ratings.album_id
                GROUP BY albums.id
                HAVING num_ratings >= 3
                ORDER BY avg_score DESC, num_ratings DESC
                LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            genres = row['genres'].split(',') if row['genres'] else []
            album = Album(row['id'], row['title'], row['artist_id'],
                        row['release_date'], row['spotify_id'],
                        row['image_url'], genres)
            results.append({
                'album': album,
                'avg_score': round(row['avg_score'], 2) if row['avg_score'] else 0,
                'num_ratings': row['num_ratings'],
                'reason': 'Populaire'
            })
        
        return results
    
    # ========== FONCTIONS POUR LE SYSTÈME D'AMIS ==========

    def get_user_friends(self, user_id):
        """
        Récupère la liste des utilisateurs suivis par un utilisateur.
        C'est comme la liste de tes amis sur un réseau social.
        """
        assert isinstance(user_id, int) and user_id > 0, "User ID invalide"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT users.* 
            FROM users
            JOIN follows ON users.id = follows.following_id
            WHERE follows.follower_id = ?
            ORDER BY users.username
        ''', (user_id,))
        # On joint la table users avec follows pour récupérer les infos des personnes suivies
        
        rows = cursor.fetchall()
        conn.close()
        
        friends = []
        for row in rows:
            friends.append(User(row['id'], row['username'], row['email'], 
                            row['password_hash'], row['created_at']))
        return friends

    def get_friends_recent_ratings(self, user_id, limit=20):
        """
        Récupère les notes récentes des amis d'un utilisateur.
        C'est comme le fil d'actualité d'Instagram/TikTok mais pour les critiques musicales !
        """
        assert isinstance(user_id, int) and user_id > 0, "User ID invalide"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # On récupère les notes des personnes que l'utilisateur suit
        cursor.execute('''
            SELECT ratings.*, users.username, users.email
            FROM ratings
            JOIN follows ON ratings.user_id = follows.following_id
            JOIN users ON ratings.user_id = users.id
            WHERE follows.follower_id = ?
            ORDER BY ratings.created_at DESC
            LIMIT ?
        ''', (user_id, limit))
        # ORDER BY created_at DESC = les plus récentes en premier
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            # Pour chaque note, on récupère aussi l'album et l'artiste correspondants
            album = self.get_album_by_id(row['album_id'])
            if album:
                artist = self.get_artist_by_id(album.artist_id)
                user = User(row['user_id'], row['username'], row['email'], '', '')
                
                rating = Rating(
                    row['id'],
                    row['user_id'],
                    row['album_id'],
                    row['score'],
                    row['review'],
                    row['created_at']
                )
                
                # On crée un dictionnaire avec toutes les infos nécessaires
                results.append({
                    'rating': rating,
                    'album': album,
                    'artist': artist,
                    'user': user
                })
        
        return results