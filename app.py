# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from database import Database
from spotify_api import SpotifyAPI
from functools import wraps
import secrets
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'clef_hyper_secrete'  

UPLOAD_FOLDER = 'static/uploads/profiles'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

SPOTIFY_CLIENT_ID = '1d12cda46ed94410b210fa95ff0c1d6d'
SPOTIFY_CLIENT_SECRET = '0bdf1645b4704190b29c9403b5573064'


db = Database()



try:
    if SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET:
        spotify = SpotifyAPI(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
        print("✅ Spotify API configurée !")
    else:
        spotify = None
        print("⚠️  Spotify API non configurée.")
except Exception as e:
    spotify = None
    print(f"⚠️  Erreur dans la base Spotify: {e}")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vous devez être connecté pour accéder à cette page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def import_artist_albums(artist_id, spotify_artist_id):
    """
    Importe tous les albums d'un artiste depuis Spotify
    
    Args:
        artist_id: L'ID de l'artiste dans votre base de données
        spotify_artist_id: L'ID Spotify de l'artiste
    
    Returns:
        Le nombre d'albums importés
    """
    if not spotify:
        return 0

    artist_albums = spotify.get_artist_albums(spotify_artist_id)
    
    if not artist_albums:
        return 0
    
    albums_added = 0
    
    for album_data in artist_albums:
   
        existing_album = db.get_album_by_spotify_id(album_data['id'])
        
        if not existing_album:

            album_id = db.create_album(
                album_data['name'],
                artist_id,
                album_data['release_date'],
                album_data['id'],
                album_data['image_url'],
                album_data.get('genres', [])
            )
            
            if album_id:
                albums_added += 1
    
    return albums_added

# ========== ROUTES PRINCIPALES ==========

@app.route('/')
def index():
    """Page d'accueil avec les albums les mieux notés, les pires, et recommandations"""
    top_albums = db.get_top_rated_albums(limit=12)
    worst_albums = db.get_worst_rated_albums(limit=8)
    

    for item in top_albums:
        artist = db.get_artist_by_id(item['album'].artist_id)
        item['artist'] = artist
    
    for item in worst_albums:
        artist = db.get_artist_by_id(item['album'].artist_id)
        item['artist'] = artist
    

    
    return render_template('index.html', 
                          top_albums=top_albums,
                          worst_albums=worst_albums,)


# ========== AUTHENTIFICATION ==========

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Inscription d'un nouvel utilisateur"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
       
        if not username or not email or not password:
            flash('Tous les champs sont requis', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Le mot de passe doit contenir au moins 6 caractères', 'danger')
            return render_template('register.html')
        
   
        user_id = db.create_user(username, email, password)
        
        if user_id:
            flash('Compte créé avec succès! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Ce nom d\'utilisateur ou email est déjà utilisé', 'danger')
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Connexion d'un utilisateur"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = db.get_user_by_username(username)
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f'Bienvenue {user.username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Déconnexion"""
    session.clear()
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('index'))


# ========== RECHERCHE ==========

@app.route('/search')
def search():
    """Page de recherche"""
    query = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'all')
    
    if not query:
        return render_template('search.html', query='', results={})
    
    results = {
        'albums': [],
        'artists': [],
        'spotify_albums': [],
        'spotify_artists': []
    }
    

    if search_type in ['all', 'albums']:
        results['albums'] = db.search_albums(query)
    
    if search_type in ['all', 'artists']:
        results['artists'] = db.search_artists(query)

    if spotify:
        if search_type in ['all', 'albums']:
            results['spotify_albums'] = spotify.search_albums(query, limit=10)
        
        if search_type in ['all', 'artists']:
            results['spotify_artists'] = spotify.search_artists(query, limit=10)
    
    return render_template('search.html', query=query, results=results, search_type=search_type)


# ========== ALBUMS ==========

@app.route('/album/<int:album_id>')
def album_detail(album_id):
    """Page de détail d'un album"""
    album = db.get_album_by_id(album_id)
    
    if not album:
        flash('Album introuvable', 'danger')
        return redirect(url_for('index'))
    
    artist = db.get_artist_by_id(album.artist_id)
    ratings = db.get_album_ratings(album_id)
    avg_rating = db.get_album_average_rating(album_id)
    
 
    for rating in ratings:
        rating.user = db.get_user_by_id(rating.user_id)
        rating.replies_count = db.get_replies_count(rating.id)

    user_rating = None
    if 'user_id' in session:
        user_rating = db.get_user_rating(session['user_id'], album_id)
    

    tracks = []
    if spotify and album.spotify_id:
        tracks = spotify.get_album_tracks(album.spotify_id)
    
    return render_template('album.html', 
                          album=album, 
                          artist=artist,
                          ratings=ratings,
                          avg_rating=avg_rating,
                          user_rating=user_rating,
                          tracks=tracks)


@app.route('/album/<int:album_id>/tracklist')
def album_tracklist(album_id):
    """Page dédiée à la liste des titres d'un album"""
    album = db.get_album_by_id(album_id)
    
    if not album:
        flash('Album introuvable', 'danger')
        return redirect(url_for('index'))
    
    artist = db.get_artist_by_id(album.artist_id)
    
    tracks = []
    total_duration_ms = 0
    
    if spotify and album.spotify_id:
        tracks = spotify.get_album_tracks(album.spotify_id)
        total_duration_ms = sum(track['duration_ms'] for track in tracks)
    
    total_minutes = total_duration_ms // 60000
    total_seconds = (total_duration_ms % 60000) // 1000
    
    return render_template('tracklist.html', 
                          album=album, 
                          artist=artist,
                          tracks=tracks,
                          total_minutes=total_minutes,
                          total_seconds=total_seconds)

@app.route('/album/<int:album_id>/rate', methods=['POST'])
@login_required
def rate_album(album_id):
    """Ajouter/modifier une note pour un album"""
    score = request.form.get('score', type=float)
    review = request.form.get('review', '').strip()
    
    if score is None or not (0 <= score <= 10):
        flash('Note invalide (doit être entre 0 et 10)', 'danger')
        return redirect(url_for('album_detail', album_id=album_id))
    
    db.create_rating(session['user_id'], album_id, score, review if review else None)
    flash('Note enregistrée avec succès!', 'success')
    
    return redirect(url_for('album_detail', album_id=album_id))

@app.route('/album/<int:album_id>/rating/<int:rating_id>/delete', methods=['POST'])
@login_required
def delete_rating(album_id, rating_id):
    """Supprimer une note"""
    if db.delete_rating(rating_id, session['user_id']):
        flash('Note supprimée avec succès!', 'success')
    else:
        flash('Impossible de supprimer cette note', 'danger')
    
    return redirect(url_for('album_detail', album_id=album_id))


# ========== RÉPONSES AUX CRITIQUES ==========

@app.route('/rating/<int:rating_id>/replies')
def rating_replies(rating_id):
    """Page de conversation pour une critique"""
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ratings WHERE id = ?', (rating_id,))
    rating = cursor.fetchone()
    conn.close()
    
    if not rating:
        flash('Critique introuvable', 'danger')
        return redirect(url_for('index'))
    
    album = db.get_album_by_id(rating['album_id'])
    artist = db.get_artist_by_id(album.artist_id)
    rating_user = db.get_user_by_id(rating['user_id'])
    
    replies = db.get_rating_replies(rating_id)
    
    for reply in replies:
        reply.user = db.get_user_by_id(reply.user_id)
    
    from models import Rating
    rating_obj = Rating(
        rating['id'],
        rating['user_id'],
        rating['album_id'],
        rating['score'],
        rating['review'],
        rating['created_at']
    )
    rating_obj.user = rating_user
    
    return render_template('rating_replies.html',
                          rating=rating_obj,
                          album=album,
                          artist=artist,
                          replies=replies)


@app.route('/rating/<int:rating_id>/reply', methods=['POST'])
@login_required
def add_reply(rating_id):
    """Ajouter une réponse à une critique"""
    content = request.form.get('content', '').strip()
    
    if not content:
        flash('La réponse ne peut pas être vide', 'danger')
        return redirect(url_for('rating_replies', rating_id=rating_id))
    
    db.create_reply(rating_id, session['user_id'], content)
    flash('Réponse ajoutée avec succès!', 'success')
    
    return redirect(url_for('rating_replies', rating_id=rating_id))


@app.route('/rating/<int:rating_id>/reply/<int:reply_id>/delete', methods=['POST'])
@login_required
def delete_reply(rating_id, reply_id):
    """Supprimer une réponse"""
    if db.delete_reply(reply_id, session['user_id']):
        flash('Réponse supprimée avec succès!', 'success')
    else:
        flash('Impossible de supprimer cette réponse', 'danger')
    
    return redirect(url_for('rating_replies', rating_id=rating_id))




# ========== ARTISTES ==========

@app.route('/artist/<int:artist_id>')
def artist_detail(artist_id):
    """Page de détail d'un artiste"""
    artist = db.get_artist_by_id(artist_id)
    
    if not artist:
        flash('Artiste introuvable', 'danger')
        return redirect(url_for('index'))
    
    albums = db.get_albums_by_artist(artist_id)
    tags = db.get_artist_tags(artist_id)
    
    for album in albums:
        album.avg_rating = db.get_album_average_rating(album.id)
    
    return render_template('artist.html', artist=artist, albums=albums, tags=tags)


@app.route('/artist/<int:artist_id>/tag', methods=['POST'])
@login_required
def add_artist_tag(artist_id):
    """Ajouter un tag à un artiste"""
    tag_name = request.form.get('tag', '').strip().lower()
    
    if not tag_name:
        flash('Le tag ne peut pas être vide', 'danger')
        return redirect(url_for('artist_detail', artist_id=artist_id))
    
    db.create_tag(artist_id, tag_name, session['user_id'])
    flash('Tag ajouté avec succès!', 'success')
    
    return redirect(url_for('artist_detail', artist_id=artist_id))

@app.route('/artist/<int:artist_id>/tag/<int:tag_id>/delete', methods=['POST'])
@login_required
def delete_tag(artist_id, tag_id):
    """Supprimer un tag"""
    if db.delete_tag(tag_id, session['user_id']):
        flash('Tag supprimé avec succès!', 'success')
    else:
        flash('Impossible de supprimer ce tag', 'danger')
    
    return redirect(url_for('artist_detail', artist_id=artist_id))



@app.route('/album/add_from_spotify/<spotify_id>')
@login_required
def add_album_from_spotify(spotify_id):
    """Ajouter un album depuis Spotify et importer les autres albums de l'artiste"""
    if not spotify:
        flash('L\'API Spotify n\'est pas configurée', 'danger')
        return redirect(url_for('search'))
    
    existing_album = db.get_album_by_spotify_id(spotify_id)
    if existing_album:
        flash('Cet album existe déjà dans la base de données', 'info')
        return redirect(url_for('album_detail', album_id=existing_album.id))
    
    album_data = spotify.get_album_details(spotify_id)
    
    if not album_data:
        flash('Impossible de récupérer les informations de l\'album', 'danger')
        return redirect(url_for('search'))
    
    artist = db.get_artist_by_spotify_id(album_data['artist_id'])
    if not artist:
        artist_data = spotify.get_artist_details(album_data['artist_id'])
        artist_id = db.create_artist(
            artist_data['name'],
            artist_data['id'],
            artist_data['image_url'],
            artist_data['genres']
        )
    else:
        artist_id = artist.id
    
    album_id = db.create_album(
        album_data['name'],
        artist_id,
        album_data['release_date'],
        album_data['id'],
        album_data['image_url'],
        album_data['genres']
    )
    
    albums_added = import_artist_albums(artist_id, album_data['artist_id'])
    

    
    return redirect(url_for('album_detail', album_id=album_id))



@app.route('/profile/<int:user_id>')
def user_profile(user_id):
    """Page de profil d'un utilisateur"""
    user = db.get_user_by_id(user_id)
    
    if not user:
        flash('Utilisateur introuvable', 'danger')
        return redirect(url_for('index'))
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as count FROM ratings WHERE user_id = ?', (user_id,))
    ratings_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM follows WHERE following_id = ?', (user_id,))
    followers_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM follows WHERE follower_id = ?', (user_id,))
    following_count = cursor.fetchone()['count']
    
    stats = {
        'ratings_count': ratings_count,
        'followers_count': followers_count,
        'following_count': following_count
    }
    
    cursor.execute('''
        SELECT * FROM ratings 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT 20
    ''', (user_id,))
    rating_rows = cursor.fetchall()
    
    user_ratings = []
    for row in rating_rows:
        album = db.get_album_by_id(row['album_id'])
        artist = db.get_artist_by_id(album.artist_id)
        user_ratings.append({
            'rating': row,
            'album': album,
            'artist': artist
        })
    
    cursor.execute('''
        SELECT * FROM ratings 
        WHERE user_id = ? AND score >= 7
        ORDER BY score DESC, created_at DESC
        LIMIT 5
    ''', (user_id,))
    favorite_rows = cursor.fetchall()
    
    favorite_albums = []
    for row in favorite_rows:
        album = db.get_album_by_id(row['album_id'])
        artist = db.get_artist_by_id(album.artist_id)
        favorite_albums.append({
            'album': album,
            'artist': artist,
            'score': row['score']
        })
    
    conn.close()
    
    is_following = False
    if 'user_id' in session and session['user_id'] != user_id:
        is_following = db.is_following(session['user_id'], user_id)
    
    return render_template('profile.html', 
                          profile_user=user, 
                          user_ratings=user_ratings,
                          favorite_albums=favorite_albums,
                          stats=stats,
                          is_following=is_following)

@app.route('/artist/add_from_spotify/<spotify_id>')
@login_required
def add_artist_from_spotify(spotify_id):
    """Ajouter un artiste depuis Spotify avec ses albums"""
    if not spotify:
        flash('L\'API Spotify n\'est pas configurée', 'danger')
        return redirect(url_for('search'))
    
    existing_artist = db.get_artist_by_spotify_id(spotify_id)
    if existing_artist:
        return redirect(url_for('artist_detail', artist_id=existing_artist.id))
    
    artist_data = spotify.get_artist_details(spotify_id)
    
    if not artist_data:
        flash('Impossible de récupérer les informations de l\'artiste', 'danger')
        return redirect(url_for('search'))
    
    artist_id = db.create_artist(
        artist_data['name'],
        artist_data['id'],
        artist_data['image_url'],
        artist_data['genres']
    )
    
    if not artist_id:
        flash('Erreur lors de la création de l\'artiste', 'danger')
        return redirect(url_for('search'))
    
    albums_added = import_artist_albums(artist_id, spotify_id)
    
    
    return redirect(url_for('artist_detail', artist_id=artist_id))
    

@app.route('/profile/update-bio', methods=['POST'])
@login_required
def update_bio():
    """Mettre à jour la bio de l'utilisateur"""
    bio = request.form.get('bio', '').strip()
    
    if len(bio) > 200:
        flash('La bio ne peut pas dépasser 200 caractères', 'danger')
        return redirect(url_for('user_profile', user_id=session['user_id']))
    
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET bio = ? WHERE id = ?', (bio, session['user_id']))
    conn.commit()
    conn.close()
    
    flash('Bio mise à jour avec succès !', 'success')
    return redirect(url_for('user_profile', user_id=session['user_id']))


@app.route('/profile/update-image', methods=['POST'])
@login_required
def update_profile_image():
    """Mettre à jour l'image de profil"""
    
    if 'profile_image_file' in request.files:
        file = request.files['profile_image_file']
        
        if file and file.filename != '':
            if not allowed_file(file.filename):
                flash('Format de fichier non autorisé. Utilisez PNG, JPG, JPEG, GIF ou WEBP.', 'danger')
                return redirect(url_for('user_profile', user_id=session['user_id']))
            
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT profile_image FROM users WHERE id = ?', (session['user_id'],))
            old_image = cursor.fetchone()
            
            if old_image and old_image['profile_image']:
                old_image_path = old_image['profile_image']
                if old_image_path.startswith('/static/'):
                    old_image_path = old_image_path[8:]  
                    full_path = os.path.join('static', old_image_path)
                    if os.path.exists(full_path):
                        try:
                            os.remove(full_path)
                        except:
                            pass
            
            filename = secure_filename(file.filename)
            name, ext = os.path.splitext(filename)
            unique_filename = f"user_{session['user_id']}_{int(datetime.now().timestamp())}{ext}"
            
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            
            db_path = f"/static/uploads/profiles/{unique_filename}"
            
            cursor.execute('UPDATE users SET profile_image = ? WHERE id = ?', 
                         (db_path, session['user_id']))
            conn.commit()
            conn.close()
            
            flash('Photo de profil mise à jour avec succès !', 'success')
            return redirect(url_for('user_profile', user_id=session['user_id']))
    
    profile_image_url = request.form.get('profile_image_url', '').strip()
    
    if profile_image_url:
        if not (profile_image_url.startswith('http://') or profile_image_url.startswith('https://')):
            flash('URL d\'image invalide', 'danger')
            return redirect(url_for('user_profile', user_id=session['user_id']))
        
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET profile_image = ? WHERE id = ?', 
                     (profile_image_url, session['user_id']))
        conn.commit()
        conn.close()
        
        flash('Photo de profil mise à jour avec succès !', 'success')
        return redirect(url_for('user_profile', user_id=session['user_id']))
    
    flash('Aucune image sélectionnée', 'warning')
    return redirect(url_for('user_profile', user_id=session['user_id']))


@app.route('/profile/delete-image', methods=['POST'])
@login_required
def delete_profile_image():
    """Supprimer la photo de profil"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT profile_image FROM users WHERE id = ?', (session['user_id'],))
    result = cursor.fetchone()
    
    if result and result['profile_image']:
        image_path = result['profile_image']
        
        if image_path.startswith('/static/'):
            image_path = image_path[8:]  
            full_path = os.path.join('static', image_path)
            if os.path.exists(full_path):
                try:
                    os.remove(full_path)
                except:
                    pass
        
        cursor.execute('UPDATE users SET profile_image = NULL WHERE id = ?', (session['user_id'],))
        conn.commit()
        flash('Photo de profil supprimée', 'info')
    
    conn.close()
    return redirect(url_for('user_profile', user_id=session['user_id']))


@app.route('/friends')
@login_required
def friends():
    """Page des amis de l'utilisateur"""
    friends_list = db.get_user_friends(session['user_id'])
    
    friends_recent_ratings = db.get_friends_recent_ratings(session['user_id'], limit=20)
    
    return render_template('friends.html', 
                          friends=friends_list,
                          friends_recent_ratings=friends_recent_ratings)

@app.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def follow_user(user_id):
    """Suivre un utilisateur"""
    if user_id == session['user_id']:
        flash('Vous ne pouvez pas vous suivre vous-même nan mais sérieux vous vous prenez pour qui', 'warning')
        return redirect(url_for('user_profile', user_id=user_id))
    
    db.follow_user(session['user_id'], user_id)
    flash('Vous suivez maintenant cet utilisateur', 'success')
    
    return redirect(url_for('user_profile', user_id=user_id))


@app.route('/unfollow/<int:user_id>', methods=['POST'])
@login_required
def unfollow_user(user_id):
    """Ne plus suivre un utilisateur"""
    db.unfollow_user(session['user_id'], user_id)
    flash('Vous ne suivez plus cet utilisateur', 'info')
    
    return redirect(url_for('user_profile', user_id=user_id))

reset_tokens = {}

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Page de demande de réinitialisation de mot de passe"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not email:
            flash('Veuillez entrer votre adresse email', 'danger')
            return render_template('forgot_password.html')
        
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            token = secrets.token_urlsafe(32)
            expiry = datetime.now() + timedelta(hours=1)  
            reset_tokens[token] = {
                'user_id': user['id'],
                'email': email,
                'expiry': expiry
            }
            

            reset_link = url_for('reset_password', token=token, _external=True)
            
            flash(f'Un lien de réinitialisation a été généré', 'info')
            flash(f'Lien de test (copier ce lien) : {reset_link}', 'warning')
            
            flash('Si un compte existe avec cet email, un lien de réinitialisation sera envoyé.', 'success')
        else:
            flash('Si un compte existe avec cet email, un lien de réinitialisation sera envoyé.', 'success')
        
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html')


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Page de réinitialisation du mot de passe avec token"""
    
    if token not in reset_tokens:
        flash('Lien de réinitialisation invalide ou expiré', 'danger')
        return redirect(url_for('login'))
    
    token_data = reset_tokens[token]
    
    if datetime.now() > token_data['expiry']:
        del reset_tokens[token]
        flash('Le lien de réinitialisation a expiré. Veuillez faire une nouvelle demande.', 'danger')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not password or not confirm_password:
            flash('Tous les champs sont requis', 'danger')
            return render_template('reset_password.html', token=token)
        
        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas', 'danger')
            return render_template('reset_password.html', token=token)
        
        if len(password) < 6:
            flash('Le mot de passe doit contenir au moins 6 caractères', 'danger')
            return render_template('reset_password.html', token=token)
        
        from models import User
        new_password_hash = User.hash_password(password)
        
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET password_hash = ? WHERE id = ?',
            (new_password_hash, token_data['user_id'])
        )
        conn.commit()
        conn.close()
        
        del reset_tokens[token]
        
        flash('Mot de passe réinitialisé avec succès ! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', token=token)
 

# ========== PARAMÈTRES UTILISATEUR ==========

@app.route('/settings')
@login_required
def settings():
    """Page des paramètres utilisateur"""
    current_user = db.get_user_by_id(session['user_id'])
    return render_template('settings.html', current_user=current_user)


@app.route('/settings/update-username', methods=['POST'])
@login_required
def update_username():
    """Modifier le nom d'utilisateur"""
    new_username = request.form.get('new_username', '').strip()
    password = request.form.get('password', '')
    
    if not new_username or not password:
        flash('Tous les champs sont requis', 'danger')
        return redirect(url_for('settings'))
    
    if len(new_username) < 3 or len(new_username) > 30:
        flash('Le nom d\'utilisateur doit contenir entre 3 et 30 caractères', 'danger')
        return redirect(url_for('settings'))
    
    user = db.get_user_by_id(session['user_id'])
    if not user.check_password(password):
        flash('Mot de passe incorrect', 'danger')
        return redirect(url_for('settings'))
    
    existing_user = db.get_user_by_username(new_username)
    if existing_user and existing_user.id != session['user_id']:
        flash('Ce nom d\'utilisateur est déjà pris', 'danger')
        return redirect(url_for('settings'))
    
    # Mettre à jour le nom d'utilisateur
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET username = ? WHERE id = ?', (new_username, session['user_id']))
    conn.commit()
    conn.close()
    
    # Mettre à jour la session
    session['username'] = new_username
    
    flash('Nom d\'utilisateur mis à jour avec succès !', 'success')
    return redirect(url_for('settings'))


@app.route('/settings/update-email', methods=['POST'])
@login_required
def update_email():
    """Modifier l'adresse email"""
    new_email = request.form.get('new_email', '').strip()
    password = request.form.get('password', '')
    
    # Validation
    if not new_email or not password:
        flash('Tous les champs sont requis', 'danger')
        return redirect(url_for('settings'))
    
    if '@' not in new_email:
        flash('Adresse email invalide', 'danger')
        return redirect(url_for('settings'))
    
    # Vérifier le mot de passe
    user = db.get_user_by_id(session['user_id'])
    if not user.check_password(password):
        flash('Mot de passe incorrect', 'danger')
        return redirect(url_for('settings'))
    
    # Vérifier si l'email existe déjà
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ? AND id != ?', (new_email, session['user_id']))
    existing_email = cursor.fetchone()
    
    if existing_email:
        conn.close()
        flash('Cette adresse email est déjà utilisée', 'danger')
        return redirect(url_for('settings'))
    
    # Mettre à jour l'email
    cursor.execute('UPDATE users SET email = ? WHERE id = ?', (new_email, session['user_id']))
    conn.commit()
    conn.close()
    
    flash('Adresse email mise à jour avec succès !', 'success')
    return redirect(url_for('settings'))


@app.route('/settings/update-password', methods=['POST'])
@login_required
def update_password():
    """Modifier le mot de passe"""
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_new_password = request.form.get('confirm_new_password', '')
    
    # Validation
    if not current_password or not new_password or not confirm_new_password:
        flash('Tous les champs sont requis', 'danger')
        return redirect(url_for('settings'))
    
    if len(new_password) < 6:
        flash('Le nouveau mot de passe doit contenir au moins 6 caractères', 'danger')
        return redirect(url_for('settings'))
    
    if new_password != confirm_new_password:
        flash('Les nouveaux mots de passe ne correspondent pas', 'danger')
        return redirect(url_for('settings'))
    
    # Vérifier le mot de passe actuel
    user = db.get_user_by_id(session['user_id'])
    if not user.check_password(current_password):
        flash('Mot de passe actuel incorrect', 'danger')
        return redirect(url_for('settings'))
    
    # Mettre à jour le mot de passe
    from models import User
    new_password_hash = User.hash_password(new_password)
    
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (new_password_hash, session['user_id']))
    conn.commit()
    conn.close()
    
    flash('Mot de passe mis à jour avec succès !', 'success')
    return redirect(url_for('settings'))


@app.route('/settings/delete-account', methods=['POST'])
@login_required
def delete_account():
    """Supprimer le compte utilisateur"""
    confirmation = request.form.get('confirmation', '').strip()
    password = request.form.get('password', '')
    
    # Validation
    if confirmation != 'SUPPRIMER':
        flash('Confirmation incorrecte. Vous devez taper "SUPPRIMER" exactement.', 'danger')
        return redirect(url_for('settings'))
    
    # Vérifier le mot de passe
    user = db.get_user_by_id(session['user_id'])
    if not user.check_password(password):
        flash('Mot de passe incorrect', 'danger')
        return redirect(url_for('settings'))
    
    # Supprimer toutes les données de l'utilisateur
    conn = db.get_connection()
    cursor = conn.cursor()
    
    user_id = session['user_id']
    
    # Supprimer les réponses
    cursor.execute('DELETE FROM replies WHERE user_id = ?', (user_id,))
    
    # Supprimer les notes
    cursor.execute('DELETE FROM ratings WHERE user_id = ?', (user_id,))
    
    # Supprimer les follows (en tant que follower et following)
    cursor.execute('DELETE FROM follows WHERE follower_id = ? OR following_id = ?', (user_id, user_id))
    
    # Supprimer les tags
    cursor.execute('DELETE FROM tags WHERE user_id = ?', (user_id,))
    
    # Supprimer l'utilisateur
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    
    conn.commit()
    conn.close()
    
    # Déconnecter l'utilisateur
    session.clear()
    
    flash('Votre compte a été supprimé avec succès. Allez bye looser !.', 'info')
    return redirect(url_for('index'))


# ========== ERREURS ==========

@app.errorhandler(404)
def page_not_found(e):
    """Page 404"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    """Erreur 500"""
    return render_template('500.html'), 500


if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════╗
    ║   🎵 Site de notation musicale - Flask 🎵    ║
    ╠═══════════════════════════════════════════════╣
    ║  Serveur démarré sur http://127.0.0.1:5000    ║
    ║                                               ║
    ║                                               ║
    ║                                               ║
    ║                                               ║ 
    ║                                               ║
    ╚═══════════════════════════════════════════════╝
    """)
    app.run(debug=True, use_reloader=False)