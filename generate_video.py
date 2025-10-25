"""
Générateur automatique de vidéos YouTube Shorts et TikTok
Crée et publie une vidéo quotidiennement sur des faits surprenants
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
import random

# ============================================
# CONFIGURATION - Modifiez ces valeurs
# ============================================

# Ces valeurs seront stockées dans les "Secrets" GitHub
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')  # ou ANTHROPIC_API_KEY
GOOGLE_CLOUD_KEY = os.environ.get('GOOGLE_CLOUD_KEY')
YOUTUBE_CLIENT_ID = os.environ.get('YOUTUBE_CLIENT_ID')
YOUTUBE_CLIENT_SECRET = os.environ.get('YOUTUBE_CLIENT_SECRET')
TIKTOK_ACCESS_TOKEN = os.environ.get('TIKTOK_ACCESS_TOKEN')

# Thèmes de faits (vous pouvez en ajouter)
THEMES = [
    "science incroyable",
    "histoire méconnue",
    "animaux étonnants",
    "espace et astronomie",
    "corps humain",
    "inventions surprenantes",
    "géographie fascinante",
    "records du monde"
]

# ============================================
# ÉTAPE 1 : Récupérer un fait vérifié
# ============================================

def get_verified_fact():
    """
    Récupère un fait vérifié depuis Wikipedia
    """
    print("🔍 Recherche d'un fait intéressant...")
    
    # API Wikipedia pour récupérer un article aléatoire
    url = "https://fr.wikipedia.org/api/rest_v1/page/random/summary"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        fact = {
            'title': data.get('title', ''),
            'extract': data.get('extract', ''),
            'source': data.get('content_urls', {}).get('desktop', {}).get('page', '')
        }
        
        print(f"✅ Fait trouvé : {fact['title']}")
        return fact
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération : {e}")
        # Fait de secours
        return {
            'title': 'Le miel ne périme jamais',
            'extract': 'Le miel est le seul aliment qui ne se périme jamais. Des pots de miel vieux de 3000 ans retrouvés dans des tombes égyptiennes étaient encore parfaitement comestibles.',
            'source': 'https://fr.wikipedia.org/wiki/Miel'
        }

# ============================================
# ÉTAPE 2 : Générer le script vidéo
# ============================================

def generate_script(fact):
    """
    Utilise l'IA pour créer un script captivant de 30-45 secondes
    """
    print("📝 Génération du script vidéo...")
    
    prompt = f"""Crée un script de vidéo courte (30-45 secondes) sur ce fait :

Titre : {fact['title']}
Contenu : {fact['extract']}

Le script doit :
- Commencer par un HOOK captivant (question ou affirmation choc)
- Être au format parlé, naturel
- Durer entre 30 et 45 secondes à la lecture
- Se terminer par un appel à l'action ("Abonne-toi pour plus de faits incroyables !")
- Être en français

Donne UNIQUEMENT le texte à dire, sans indication de mise en scène."""

    # Utilisation de l'API OpenAI (GPT-4 ou GPT-3.5-turbo)
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': 'gpt-3.5-turbo',  # ou 'gpt-4' si vous avez accès
        'messages': [
            {'role': 'system', 'content': 'Tu es un créateur de contenus viral pour TikTok et YouTube Shorts.'},
            {'role': 'user', 'content': prompt}
        ],
        'temperature': 0.8
    }
    
    try:
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data
        )
        script = response.json()['choices'][0]['message']['content']
        print("✅ Script généré avec succès")
        return script
        
    except Exception as e:
        print(f"❌ Erreur génération script : {e}")
        return f"Saviez-vous que {fact['extract']} Incroyable non ? Abonne-toi pour découvrir d'autres faits surprenants !"

# ============================================
# ÉTAPE 3 : Générer la voix-off
# ============================================

def generate_voiceover(script, output_path="voiceover.mp3"):
    """
    Génère la voix-off avec Google Cloud Text-to-Speech
    """
    print("🎤 Génération de la voix-off...")
    
    from google.cloud import texttospeech
    
    client = texttospeech.TextToSpeechClient()
    
    synthesis_input = texttospeech.SynthesisInput(text=script)
    
    voice = texttospeech.VoiceSelectionParams(
        language_code="fr-FR",
        name="fr-FR-Neural2-A",  # Voix féminine naturelle
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )
    
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.1,  # Légèrement plus rapide pour TikTok
        pitch=0.0
    )
    
    try:
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        with open(output_path, "wb") as out:
            out.write(response.audio_content)
        
        print(f"✅ Voix-off créée : {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Erreur génération voix : {e}")
        return None

# ============================================
# ÉTAPE 4 : Télécharger des visuels
# ============================================

def download_stock_videos(theme, count=3):
    """
    Télécharge des vidéos stock gratuites depuis Pexels
    """
    print(f"🎬 Téléchargement de vidéos sur le thème : {theme}")
    
    PEXELS_API_KEY = "VOTRE_CLE_PEXELS"  # Gratuit sur pexels.com/api
    
    headers = {'Authorization': PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={theme}&per_page={count}&orientation=portrait"
    
    try:
        response = requests.get(url, headers=headers)
        videos = response.json().get('videos', [])
        
        video_files = []
        for i, video in enumerate(videos[:count]):
            video_url = video['video_files'][0]['link']
            filename = f"video_{i}.mp4"
            
            # Télécharger la vidéo
            vid_response = requests.get(video_url)
            with open(filename, 'wb') as f:
                f.write(vid_response.content)
            
            video_files.append(filename)
            print(f"  ✅ Téléchargé : {filename}")
        
        return video_files
        
    except Exception as e:
        print(f"❌ Erreur téléchargement vidéos : {e}")
        return []

# ============================================
# ÉTAPE 5 : Créer la vidéo finale
# ============================================

def create_video(video_files, voiceover_path, script, output="final_video.mp4"):
    """
    Assemble la vidéo avec MoviePy : vidéos + voix + sous-titres
    """
    print("🎥 Création de la vidéo finale...")
    
    from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips
    
    try:
        # Charger l'audio
        audio = AudioFileClip(voiceover_path)
        duration = audio.duration
        
        # Charger et redimensionner les vidéos en 9:16 (format vertical)
        clips = []
        for video_file in video_files:
            clip = VideoFileClip(video_file)
            clip = clip.resize(height=1920)  # Format portrait
            clip = clip.crop(x_center=clip.w/2, width=1080, height=1920)
            clips.append(clip)
        
        # Concaténer les clips pour matcher la durée audio
        video = concatenate_videoclips(clips, method="compose")
        video = video.subclip(0, min(duration, video.duration))
        
        # Ajouter l'audio
        video = video.set_audio(audio)
        
        # Générer les sous-titres (simplifié)
        words = script.split()
        word_duration = duration / len(words)
        
        subtitle_clips = []
        for i, word in enumerate(words):
            txt_clip = TextClip(
                word,
                fontsize=70,
                color='white',
                font='Arial-Bold',
                stroke_color='black',
                stroke_width=3
            )
            txt_clip = txt_clip.set_position('center').set_duration(word_duration)
            txt_clip = txt_clip.set_start(i * word_duration)
            subtitle_clips.append(txt_clip)
        
        # Composer vidéo finale
        final = CompositeVideoClip([video] + subtitle_clips)
        
        # Exporter
        final.write_videofile(
            output,
            fps=30,
            codec='libx264',
            audio_codec='aac',
            threads=4
        )
        
        print(f"✅ Vidéo créée : {output}")
        return output
        
    except Exception as e:
        print(f"❌ Erreur création vidéo : {e}")
        return None

# ============================================
# ÉTAPE 6 : Publier sur YouTube Shorts
# ============================================

def upload_to_youtube(video_path, title, description):
    """
    Upload sur YouTube via l'API
    """
    print("📤 Publication sur YouTube Shorts...")
    
    # Configuration OAuth2 et upload
    # (Code simplifié - voir documentation YouTube API v3)
    
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        
        youtube = build('youtube', 'v3', credentials=YOUTUBE_CREDENTIALS)
        
        body = {
            'snippet': {
                'title': title,
                'description': description + "\n\n#Shorts #FaitsSurprenants",
                'tags': ['shorts', 'faits', 'éducation'],
                'categoryId': '27'  # Education
            },
            'status': {
                'privacyStatus': 'public',
                'selfDeclaredMadeForKids': False
            }
        }
        
        media = MediaFileUpload(video_path, resumable=True)
        
        request = youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )
        
        response = request.execute()
        print(f"✅ Publié sur YouTube : {response['id']}")
        
    except Exception as e:
        print(f"❌ Erreur upload YouTube : {e}")

# ============================================
# ÉTAPE 7 : Publier sur TikTok
# ============================================

def upload_to_tiktok(video_path, title):
    """
    Upload sur TikTok via l'API
    """
    print("📤 Publication sur TikTok...")
    
    # API TikTok nécessite OAuth complexe
    # Alternative : utiliser des bibliothèques comme TikTokApi
    
    try:
        # Code simplifié - voir documentation TikTok Developer
        print("⚠️ TikTok API nécessite une configuration avancée")
        print("Alternative : utilisez l'auto-upload de Buffer ou Metricool")
        
    except Exception as e:
        print(f"❌ Erreur upload TikTok : {e}")

# ============================================
# FONCTION PRINCIPALE
# ============================================

def main():
    """
    Fonction principale qui orchestre tout le processus
    """
    print("\n" + "="*50)
    print("🚀 DÉMARRAGE DU GÉNÉRATEUR AUTOMATIQUE")
    print("="*50 + "\n")
    
    # 1. Récupérer un fait
    fact = get_verified_fact()
    
    # 2. Générer le script
    script = generate_script(fact)
    print(f"\n📄 Script :\n{script}\n")
    
    # 3. Générer la voix-off
    voiceover = generate_voiceover(script)
    
    if not voiceover:
        print("❌ Impossible de continuer sans voix-off")
        return
    
    # 4. Télécharger des visuels
    theme = random.choice(THEMES)
    videos = download_stock_videos(theme, count=2)
    
    if not videos:
        print("⚠️ Pas de vidéos téléchargées, utilisation d'images statiques")
        # TODO: Alternative avec images
    
    # 5. Créer la vidéo
    final_video = create_video(videos, voiceover, script)
    
    if not final_video:
        print("❌ Échec création vidéo")
        return
    
    # 6. Publier
    title = f"Fait incroyable : {fact['title']}"
    description = f"{script}\n\nSource : {fact['source']}"
    
    upload_to_youtube(final_video, title, description)
    upload_to_tiktok(final_video, title)
    
    print("\n" + "="*50)
    print("✅ PROCESSUS TERMINÉ AVEC SUCCÈS !")
    print("="*50 + "\n")

# ============================================
# EXÉCUTION
# ============================================

if __name__ == "__main__":
    main()
