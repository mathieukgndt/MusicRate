# -*- coding: utf-8 -*-

"""
Gestion de la base de données SQLite
"""
import sqlite3
from datetime import datetime
from models import User, Artist, Album, Rating, Reply, Follow, Tag  # CHANGÉ: Comment → Reply


class Database:
    """Classe pour gérer la base de données SQLite"""
    
    def __init__(self, db_path='music_rating.db'):
        assert isinstance(db_path, str) and len(db_path) > 0, "DB path doit être une chaîne non vide"
        self.db_path = db_path
        self.init_database()


    def get_connection(self):
        """Crée une connexion à la base de données"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def delete_rating(self, rating_id, user_id):
        """Supprimer une note (seulement si c'est l'auteur)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Vérifier que la note appartient à l'utilisateur
        cursor.execute('SELECT * FROM ratings WHERE id = ? AND user_id = ?', (rating_id, user_id))
        rating = cursor.fetchone()
        
        if rating:
            cursor.execute('DELETE FROM ratings WHERE id = ?', (rating_id,))
            conn.commit()
            conn.close()
            return True
        
        conn.close()
        return False

    def delete_tag(self, tag_id, user_id):
        """Supprimer un tag (seulement si c'est l'auteur)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Vérifier que le tag appartient à l'utilisateur
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
        """Initialise les tables de la base de données"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Table des utilisateurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                profile_image TEXT,
                bio TEXT
            )
        ''')
        
        # Table des artistes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS artists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                spotify_id TEXT UNIQUE,
                image_url TEXT,
                genres TEXT
            )
        ''')
        
        # Table des albums
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS albums (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist_id INTEGER NOT NULL,
                release_date TEXT,
                spotify_id TEXT UNIQUE,
                image_url TEXT,
                genres TEXT,
                FOREIGN KEY (artist_id) REFERENCES artists (id)
            )
        ''')
        
        # Table des notes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                album_id INTEGER NOT NULL,
                score REAL NOT NULL,
                review TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (album_id) REFERENCES albums (id),
                UNIQUE(user_id, album_id)
            )
        ''')
        
        # Table des réponses aux critiques (NOUVEAU - remplace comments)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS replies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rating_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (rating_id) REFERENCES ratings (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Table des suivis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS follows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                follower_id INTEGER NOT NULL,
                following_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (follower_id) REFERENCES users (id),
                FOREIGN KEY (following_id) REFERENCES users (id),
                UNIQUE(follower_id, following_id)
            )
        ''')
        
        # Table des tags
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                artist_id INTEGER NOT NULL,
                tag_name TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (artist_id) REFERENCES artists (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        # Table des albums favoris (NOUVEAU - à ajouter après la table tags)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorite_albums (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                album_id INTEGER NOT NULL,
                position INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (album_id) REFERENCES albums (id),
                UNIQUE(user_id, album_id)
            )
        ''')
        
        # Index pour améliorer les performances des réponses
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_replies_rating_id 
            ON replies(rating_id)
        ''')
        
        conn.commit()
        conn.close()
    
    # ========== USERS ==========
    
    def create_user(self, username, email, password):
        """Crée un nouvel utilisateur"""
        assert isinstance(username, str) and len(username) > 0, "Username invalide"
        assert isinstance(email, str) and '@' in email, "Email invalide"
        
        password_hash = User.hash_password(password)
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, password_hash)
            )
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            conn.close()
            return None
    
    def get_user_by_username(self, username):
        """Récupère un utilisateur par son nom"""
        assert isinstance(username, str), "Username doit être une chaîne"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            # Vérifier si les colonnes existent
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

    def get_user_by_id(self, user_id):
        """Récupère un utilisateur par son ID"""
        assert isinstance(user_id, int) and user_id > 0, "User ID invalide"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            # Vérifier si les colonnes existent
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
    
    # ========== ARTISTS ==========
    
    def create_artist(self, name, spotify_id=None, image_url=None, genres=None):
        """Crée un nouvel artiste"""
        assert isinstance(name, str) and len(name) > 0, "Name invalide"
        
        conn = self.get_connection()
        cursor = conn.cursor()
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
            genres = row['genres'].split(',') if row['genres'] else []
            return Artist(row['id'], row['name'], row['spotify_id'], 
                         row['image_url'], genres)
        return None
    
    def get_artist_by_spotify_id(self, spotify_id):
        """Récupère un artiste par son Spotify ID"""
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
        """Recherche des artistes"""
        assert isinstance(query, str), "Query doit être une chaîne"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM artists WHERE name LIKE ? LIMIT 20', 
                      (f'%{query}%',))
        rows = cursor.fetchall()
        conn.close()
        
        artists = []
        for row in rows:
            genres = row['genres'].split(',') if row['genres'] else []
            artists.append(Artist(row['id'], row['name'], row['spotify_id'], 
                                 row['image_url'], genres))
        return artists
    
    # ========== ALBUMS ==========
    
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
        """Récupère un album par son Spotify ID"""
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
        """Récupère tous les albums d'un artiste"""
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
        """Recherche des albums"""
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
    
    # ========== NOTES ==========
    
    def create_rating(self, user_id, album_id, score, review=None):
        """Crée une nouvelle note"""
        assert isinstance(user_id, int) and user_id > 0, "User ID invalide"
        assert isinstance(album_id, int) and album_id > 0, "Album ID invalide"
        assert 0 <= score <= 10, "Score doit être entre 0 et 10"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
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
            # Mise à jour si existe déjà
            cursor.execute(
                '''UPDATE ratings SET score = ?, review = ? 
                   WHERE user_id = ? AND album_id = ?''',
                (score, review, user_id, album_id)
            )
            conn.commit()
            conn.close()
            return True
    
    def get_album_ratings(self, album_id):
        """Récupère toutes les notes d'un album"""
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
        """Récupère la note d'un utilisateur pour un album"""
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
        """Calcule la note moyenne d'un album"""
        assert isinstance(album_id, int) and album_id > 0, "Album ID invalide"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT AVG(score) as avg FROM ratings WHERE album_id = ?', 
                      (album_id,))
        row = cursor.fetchone()
        conn.close()
        
        return round(row['avg'], 2) if row['avg'] else 0
    
    def get_top_rated_albums(self, limit=10):
        """Récupère les albums les mieux notés"""
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
    
    # ========== RÉPONSES AUX CRITIQUES ==========
    
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
        """Récupère toutes les réponses d'une critique"""
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
        """Supprimer une réponse (seulement si c'est l'auteur)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Vérifier que la réponse appartient à l'utilisateur
        cursor.execute('SELECT * FROM replies WHERE id = ? AND user_id = ?', (reply_id, user_id))
        reply = cursor.fetchone()
        
        if reply:
            cursor.execute('DELETE FROM replies WHERE id = ?', (reply_id,))
            conn.commit()
            conn.close()
            return True
        
        conn.close()
        return False
    
    # ========== FOLLOWS ==========
    
    def follow_user(self, follower_id, following_id):
        """Permet à un utilisateur d'en suivre un autre"""
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
        """Vérifie si un utilisateur en suit un autre"""
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
        return result is not None
    
    # ========== TAGS ==========
    
    def create_tag(self, artist_id, tag_name, user_id):
        """Ajoute un tag à un artiste"""
        assert isinstance(artist_id, int) and artist_id > 0, "Artist ID invalide"
        assert isinstance(tag_name, str) and len(tag_name) > 0, "Tag name invalide"
        assert isinstance(user_id, int) and user_id > 0, "User ID invalide"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO tags (artist_id, tag_name, user_id) VALUES (?, ?, ?)',
            (artist_id, tag_name.lower(), user_id)
        )
        conn.commit()
        tag_id = cursor.lastrowid
        conn.close()
        return tag_id
    
    def get_artist_tags(self, artist_id):
        """Récupérer les tags d'un artiste avec comptage et ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, tag_name, user_id, COUNT(*) as count 
            FROM tags 
            WHERE artist_id = ? 
            GROUP BY tag_name
            ORDER BY count DESC
        ''', (artist_id,))
        tags = cursor.fetchall()
        conn.close()
        return tags
    
        

    def get_worst_rated_albums(self, limit=10):
        """Récupère les albums les moins bien notés"""
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
        """Récupère les genres préférés d'un utilisateur basé sur ses notes > 6.5"""
        assert isinstance(user_id, int) and user_id > 0, "User ID invalide"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Récupérer les albums notés > 6.5 par l'utilisateur
        cursor.execute('''
            SELECT albums.genres
            FROM ratings
            JOIN albums ON ratings.album_id = albums.id
            WHERE ratings.user_id = ? AND ratings.score > 6.5
        ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Compter les occurrences de chaque genre
        genre_counts = {}
        for row in rows:
            if row['genres']:
                genres = row['genres'].split(',')
                for genre in genres:
                    genre = genre.strip()
                    if genre:
                        genre_counts[genre] = genre_counts.get(genre, 0) + 1
        
        # Trier par occurrence
        sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
        return [genre for genre, count in sorted_genres[:5]]  # Top 5 genres


    def get_user_favorite_artists(self, user_id):
        """Récupère les artistes préférés d'un utilisateur basé sur ses notes > 6.5"""
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
        
        rows = cursor.fetchall()
        conn.close()
        
        return [row['artist_id'] for row in rows]


    def get_recommended_albums(self, user_id, limit=12):
        """Recommande des albums basés sur les préférences de l'utilisateur"""
        assert isinstance(user_id, int) and user_id > 0, "User ID invalide"
        
        # Debug : vérifier les notes de l'utilisateur
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM ratings WHERE user_id = ? AND score > 6.5', (user_id,))
        high_ratings_count = cursor.fetchone()['count']
        
        print(f"[DEBUG] User {user_id} a {high_ratings_count} notes > 6.5")
        
        favorite_genres = self.get_user_favorite_genres(user_id)
        favorite_artists = self.get_user_favorite_artists(user_id)
        
        print(f"[DEBUG] Genres favoris: {favorite_genres}")
        print(f"[DEBUG] Artistes favoris: {favorite_artists}")
        
        if not favorite_genres and not favorite_artists:
            print("[DEBUG] Pas de préférences, retour albums populaires")
            conn.close()
            return self.get_popular_unrated_albums(user_id, limit)
        
        # Récupérer les albums déjà notés par l'utilisateur
        cursor.execute('SELECT album_id FROM ratings WHERE user_id = ?', (user_id,))
        rated_album_ids = [row['album_id'] for row in cursor.fetchall()]
        
        print(f"[DEBUG] Albums déjà notés: {rated_album_ids}")
        
        recommendations = []
        
        # 1. Albums des artistes préférés non encore notés
        if favorite_artists:
            placeholders = ','.join('?' * len(favorite_artists))
            
            # Requête avec exclusion des albums déjà notés
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
            
            for row in rows:
                genres = row['genres'].split(',') if row['genres'] else []
                album = Album(row['id'], row['title'], row['artist_id'],
                            row['release_date'], row['spotify_id'],
                            row['image_url'], genres)
                recommendations.append({
                    'album': album,
                    'avg_score': round(row['avg_score'], 2) if row['avg_score'] else 0,
                    'num_ratings': row['num_ratings'],
                    'reason': 'Artiste similaire'
                })
        
        # 2. Albums avec des genres similaires non encore notés
        if favorite_genres and len(recommendations) < limit:
            # Requête avec exclusion des albums déjà notés et déjà recommandés
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
            
            for row in rows:
                if len(recommendations) >= limit:
                    break
                
                album_genres = row['genres'].split(',') if row['genres'] else []
                # Vérifier si au moins un genre correspond
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
        return recommendations[:limit]


    def get_popular_unrated_albums(self, user_id, limit=12):
        """Récupère des albums populaires non notés par l'utilisateur"""
        assert isinstance(user_id, int) and user_id > 0, "User ID invalide"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Récupérer les albums déjà notés
        cursor.execute('SELECT album_id FROM ratings WHERE user_id = ?', (user_id,))
        rated_album_ids = [row['album_id'] for row in cursor.fetchall()]
        
        # Récupérer les albums populaires non notés
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
    # Ajoutez ces fonctions à votre classe Database dans database.py

    def get_user_friends(self, user_id):
        """Récupère la liste des utilisateurs suivis par un utilisateur"""
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
        
        rows = cursor.fetchall()
        conn.close()
        
        friends = []
        for row in rows:
            friends.append(User(row['id'], row['username'], row['email'], 
                            row['password_hash'], row['created_at']))
        return friends


    def get_friends_recent_ratings(self, user_id, limit=20):
        """Récupère les notes récentes des amis d'un utilisateur"""
        assert isinstance(user_id, int) and user_id > 0, "User ID invalide"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Récupérer les notes des personnes suivies
        cursor.execute('''
            SELECT ratings.*, users.username, users.email
            FROM ratings
            JOIN follows ON ratings.user_id = follows.following_id
            JOIN users ON ratings.user_id = users.id
            WHERE follows.follower_id = ?
            ORDER BY ratings.created_at DESC
            LIMIT ?
        ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            # Récupérer l'album et l'artiste
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
                
                results.append({
                    'rating': rating,
                    'album': album,
                    'artist': artist,
                    'user': user
                })
        
        return results