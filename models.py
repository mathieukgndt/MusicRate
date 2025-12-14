# -*- coding: utf-8 -*-

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User:
    """Classe représentant un utilisateur"""
    
    def __init__(self, user_id, username, email, password_hash, created_at=None, profile_image=None, bio=None):
        assert isinstance(username, str) and len(username) > 0, "Username doit être une chaîne non vide"
        assert isinstance(email, str) and '@' in email, "Email doit être valide"
        assert isinstance(password_hash, str), "Password hash doit être une chaîne"
        
        self.id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at or datetime.now()
        self.profile_image = profile_image
        self.bio = bio
    
    @staticmethod
    def hash_password(password):
        """Hash un mot de passe avec werkzeug"""
        return generate_password_hash(password)
    
    def check_password(self, password):
        """Vérifie si le mot de passe correspond au hash"""
        return check_password_hash(self.password_hash, password)


class Artist:
    """Classe représentant un artiste"""
    
    def __init__(self, artist_id, name, spotify_id=None, image_url=None, genres=None):
        assert isinstance(name, str) and len(name) > 0, "Name doit être une chaîne non vide"
        
        self.id = artist_id
        self.name = name
        self.spotify_id = spotify_id
        self.image_url = image_url
        self.genres = genres or []
    
    def to_dict(self):
        """Convertit l'artiste en dictionnaire"""
        return {
            'id': self.id,
            'name': self.name,
            'spotify_id': self.spotify_id,
            'image_url': self.image_url,
            'genres': self.genres
        }


class Album:
    """Classe représentant un album"""
    
    def __init__(self, album_id, title, artist_id, release_date=None, 
                 spotify_id=None, image_url=None, genres=None):
        assert isinstance(title, str) and len(title) > 0, "Title doit être une chaîne non vide"
        assert isinstance(artist_id, int) and artist_id > 0, "Artist ID doit être un entier positif"
        
        self.id = album_id
        self.title = title
        self.artist_id = artist_id
        self.release_date = release_date
        self.spotify_id = spotify_id
        self.image_url = image_url
        self.genres = genres or []
    
    def to_dict(self):
        """Convertit l'album en dictionnaire"""
        return {
            'id': self.id,
            'title': self.title,
            'artist_id': self.artist_id,
            'release_date': self.release_date,
            'spotify_id': self.spotify_id,
            'image_url': self.image_url,
            'genres': self.genres
        }


class Rating:
    """Classe représentant une note donnée par un utilisateur"""
    
    def __init__(self, rating_id, user_id, album_id, score, review=None, created_at=None):
        assert isinstance(user_id, int) and user_id > 0, "User ID doit être un entier positif"
        assert isinstance(album_id, int) and album_id > 0, "Album ID doit être un entier positif"
        assert isinstance(score, (int, float)) and 0 <= score <= 10, "Score doit être entre 0 et 10"
        
        self.id = rating_id
        self.user_id = user_id
        self.album_id = album_id
        self.score = score
        self.review = review
        self.created_at = created_at or datetime.now()
    
    def to_dict(self):
        """Convertit la note en dictionnaire"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'album_id': self.album_id,
            'score': self.score,
            'review': self.review,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }


class Reply:
    """Classe représentant une réponse à une critique"""
    
    def __init__(self, reply_id, rating_id, user_id, content, created_at=None):
        assert isinstance(rating_id, int) and rating_id > 0, "Rating ID doit être un entier positif"
        assert isinstance(user_id, int) and user_id > 0, "User ID doit être un entier positif"
        assert isinstance(content, str) and len(content) > 0, "Content doit être une chaîne non vide"
        
        self.id = reply_id
        self.rating_id = rating_id
        self.user_id = user_id
        self.content = content
        self.created_at = created_at or datetime.now()
    
    def to_dict(self):
        """Convertit la réponse en dictionnaire"""
        return {
            'id': self.id,
            'rating_id': self.rating_id,
            'user_id': self.user_id,
            'content': self.content,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }


class Follow:
    """Classe représentant une relation de suivi entre utilisateurs"""
    
    def __init__(self, follow_id, follower_id, following_id, created_at=None):
        assert isinstance(follower_id, int) and follower_id > 0, "Follower ID doit être un entier positif"
        assert isinstance(following_id, int) and following_id > 0, "Following ID doit être un entier positif"
        assert follower_id != following_id, "Un utilisateur ne peut pas se suivre lui-même"
        
        self.id = follow_id
        self.follower_id = follower_id
        self.following_id = following_id
        self.created_at = created_at or datetime.now()
    
    def to_dict(self):
        """Convertit le suivi en dictionnaire"""
        return {
            'id': self.id,
            'follower_id': self.follower_id,
            'following_id': self.following_id,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }


class Tag:
    """Classe représentant un tag pour un artiste"""
    
    def __init__(self, tag_id, artist_id, tag_name, user_id, created_at=None):
        assert isinstance(artist_id, int) and artist_id > 0, "Artist ID doit être un entier positif"
        assert isinstance(tag_name, str) and len(tag_name) > 0, "Tag name doit être une chaîne non vide"
        assert isinstance(user_id, int) and user_id > 0, "User ID doit être un entier positif"
        
        self.id = tag_id
        self.artist_id = artist_id
        self.tag_name = tag_name.lower()
        self.user_id = user_id
        self.created_at = created_at or datetime.now()
    
    def to_dict(self):
        """Convertit le tag en dictionnaire"""
        return {
            'id': self.id,
            'artist_id': self.artist_id,
            'tag_name': self.tag_name,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }