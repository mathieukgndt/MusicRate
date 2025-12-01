# -*- coding: utf-8 -*-

"""
Intégration avec l'API Spotify
"""
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


class SpotifyAPI:
    """Classe pour interagir avec l'API Spotify"""
    
    def __init__(self, client_id, client_secret):

        assert isinstance(client_id, str) and len(client_id) > 0, "Client ID invalide"
        assert isinstance(client_secret, str) and len(client_secret) > 0, "Client Secret invalide"
        
        auth_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        self.sp = spotipy.Spotify(auth_manager=auth_manager)
    
    def search_albums(self, query, limit=10):
        """Recherche des albums sur Spotify"""
        assert isinstance(query, str) and len(query) > 0, "Query invalide"
        assert isinstance(limit, int) and 1 <= limit <= 50, "Limit doit être entre 1 et 50"
        
        try:
            results = self.sp.search(q=query, type='album', limit=limit)
            albums = []
            
            for item in results['albums']['items']:
                album_data = {
                    'id': item['id'],
                    'name': item['name'],
                    'artist': item['artists'][0]['name'],
                    'artist_id': item['artists'][0]['id'],
                    'release_date': item['release_date'],
                    'image_url': item['images'][0]['url'] if item['images'] else None,
                    'spotify_url': item['external_urls']['spotify']
                }
                albums.append(album_data)
            
            return albums
        except Exception as e:
            print(f"Erreur lors de la recherche d'albums: {e}")
            return []
    
    def search_artists(self, query, limit=10):
        """Recherche des artistes sur Spotify"""
        assert isinstance(query, str) and len(query) > 0, "Query invalide"
        assert isinstance(limit, int) and 1 <= limit <= 50, "Limit doit être entre 1 et 50"
        
        try:
            results = self.sp.search(q=query, type='artist', limit=limit)
            artists = []
            
            for item in results['artists']['items']:
                artist_data = {
                    'id': item['id'],
                    'name': item['name'],
                    'genres': item['genres'],
                    'image_url': item['images'][0]['url'] if item['images'] else None,
                    'spotify_url': item['external_urls']['spotify'],
                    'popularity': item['popularity']
                }
                artists.append(artist_data)
            
            return artists
        except Exception as e:
            print(f"Erreur lors de la recherche d'artistes: {e}")
            return []
    
    def get_album_details(self, album_id):
        """Récupère les détails complets d'un album"""
        assert isinstance(album_id, str) and len(album_id) > 0, "Album ID invalide"
        
        try:
            album = self.sp.album(album_id)
            
            album_data = {
                'id': album['id'],
                'name': album['name'],
                'artist': album['artists'][0]['name'],
                'artist_id': album['artists'][0]['id'],
                'release_date': album['release_date'],
                'total_tracks': album['total_tracks'],
                'image_url': album['images'][0]['url'] if album['images'] else None,
                'genres': album.get('genres', []),
                'label': album.get('label', ''),
                'popularity': album.get('popularity', 0),
                'spotify_url': album['external_urls']['spotify'],
                'tracks': []
            }
            
            # Ajouter les pistes
            for track in album['tracks']['items']:
                track_data = {
                    'name': track['name'],
                    'duration_ms': track['duration_ms'],
                    'track_number': track['track_number']
                }
                album_data['tracks'].append(track_data)
            
            return album_data
        except Exception as e:
            print(f"Erreur lors de la récupération de l'album: {e}")
            return None
    
    def get_artist_details(self, artist_id):
        """Récupère les détails complets d'un artiste"""
        assert isinstance(artist_id, str) and len(artist_id) > 0, "Artist ID invalide"
        
        try:
            artist = self.sp.artist(artist_id)
            
            artist_data = {
                'id': artist['id'],
                'name': artist['name'],
                'genres': artist['genres'],
                'image_url': artist['images'][0]['url'] if artist['images'] else None,
                'popularity': artist['popularity'],
                'followers': artist['followers']['total'],
                'spotify_url': artist['external_urls']['spotify']
            }
            
            return artist_data
        except Exception as e:
            print(f"Erreur lors de la récupération de l'artiste: {e}")
            return None
    
    def get_artist_albums(self, artist_id, limit=20):
        """Récupère les albums d'un artiste"""
        assert isinstance(artist_id, str) and len(artist_id) > 0, "Artist ID invalide"
        assert isinstance(limit, int) and 1 <= limit <= 50, "Limit doit être entre 1 et 50"
        
        try:
            results = self.sp.artist_albums(artist_id, limit=limit, album_type='album')
            albums = []
            
            for item in results['items']:
                album_data = {
                    'id': item['id'],
                    'name': item['name'],
                    'release_date': item['release_date'],
                    'total_tracks': item['total_tracks'],
                    'image_url': item['images'][0]['url'] if item['images'] else None,
                    'spotify_url': item['external_urls']['spotify']
                }
                albums.append(album_data)
            
            return albums
        except Exception as e:
            print(f"Erreur lors de la récupération des albums de l'artiste: {e}")
            return []
    
    def get_new_releases(self, limit=20):
        """Récupère les nouvelles sorties"""
        assert isinstance(limit, int) and 1 <= limit <= 50, "Limit doit être entre 1 et 50"
        
        try:
            results = self.sp.new_releases(limit=limit)
            albums = []
            
            for item in results['albums']['items']:
                album_data = {
                    'id': item['id'],
                    'name': item['name'],
                    'artist': item['artists'][0]['name'],
                    'artist_id': item['artists'][0]['id'],
                    'release_date': item['release_date'],
                    'image_url': item['images'][0]['url'] if item['images'] else None,
                    'spotify_url': item['external_urls']['spotify']
                }
                albums.append(album_data)
            
            return albums
        except Exception as e:
            print(f"Erreur lors de la récupération des nouvelles sorties: {e}")
            return []
    
    def get_album_tracks(self, spotify_album_id):
        """Récupère les pistes d'un album avec durée formatée"""
        assert isinstance(spotify_album_id, str) and len(spotify_album_id) > 0, "Album ID invalide"
        
        try:
            album = self.sp.album(spotify_album_id)
            tracks = []
            
            for track in album['tracks']['items']:
                track_data = {
                    'name': track['name'],
                    'duration_ms': track['duration_ms'],
                    'track_number': track['track_number'],
                    'duration_formatted': self._format_duration(track['duration_ms'])
                }
                tracks.append(track_data)
            
            return tracks
        except Exception as e:
            print(f"Erreur lors de la récupération des pistes: {e}")
            return []
    
    def _format_duration(self, duration_ms):
        """Formate la durée en minutes:secondes"""
        seconds = duration_ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"