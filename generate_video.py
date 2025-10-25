"""
Générateur automatique de vidéos YouTube Shorts et TikTok
Version simplifiée avec Edge TTS (gratuit, sans configuration complexe)
"""

import os
import json
import requests
from datetime import datetime
import random
import asyncio

# ============================================
# CONFIGURATION
# ============================================

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY', '')

# Thèmes de faits
THEMES = [
    "science",
    "histoire",
    "animaux",
    "espace",
    "nature",
    "technologie"
]

print("=" * 50)
print("🚀 DÉMARRAGE DU GÉNÉRATEUR AUTOMATIQUE")
print("=" * 50)

# ============================================
# ÉTAPE 1 : Récupérer un fait vérifié
# ============================================

def get_verified_fact():
    """Récupère un fait vérifié depuis Wikipedia"""
    print("\n🔍 Recherche d'un fait intéressant...")
    
    url = "https://fr.wikipedia.org/api/rest_v1/page/random/summary"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        fact = {
            'title': data.get('title', ''),
            'extract': data.get('extract', ''),
            'source': data.get('content_urls', {}).get('desktop', {}).get('page', '')
        }
        
        print(f"✅ Fait trouvé : {fact['title']}")
        return fact
        
    except Exception as e:
        print(f"⚠️ Utilisation d'un fait de secours : {e}")
        return {
            'title': 'Le miel ne périme jamais',
            'extract': 'Le miel est le seul aliment qui ne se périme jamais. Des pots de miel vieux de 3000 ans retrouvés dans des tombes égyptiennes étaient encore parfaitement comestibles.',
            'source': 'https://fr.wikipedia.org/wiki/Miel'
        }

# ============================================
# ÉTAPE 2 : Générer le script vidéo
# ============================================

def generate_script(fact):
    """Utilise l'IA pour créer un script captivant"""
    print("\n📝 Génération du script vidéo...")
    
    if not OPENAI_API_KEY:
        print("⚠️ Pas de clé OpenAI - utilisation d'un script par défaut")
        return f"Saviez-vous que {fact['extract'][:200]}... Incroyable non ? Abonne-toi pour découvrir d'autres faits surprenants !"
    
    prompt = f"""Crée un script de vidéo TikTok/YouTube Shorts (30-40 secondes) sur ce fait :

Titre : {fact['title']}
Contenu : {fact['extract']}

Instructions :
- Commence par un HOOK captivant (question choc)
- Style oral, naturel, énergique
- 30-40 secondes maximum
- Termine par "Abonne-toi pour plus !"
- UNIQUEMENT le texte à dire, rien d'autre"""

    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {'role': 'system', 'content': 'Tu crées des scripts viraux pour TikTok.'},
            {'role': 'user', 'content': prompt}
        ],
        'temperature': 0.9,
        'max_tokens': 300
    }
    
    try:
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            script = response.json()['choices'][0]['message']['content'].strip()
            print("✅ Script généré avec succès")
            return script
        else:
            print(f"⚠️ Erreur API OpenAI ({response.status_code}), script par défaut")
            return f"Saviez-vous que {fact['extract'][:150]}... Abonne-toi pour découvrir d'autres faits surprenants !"
        
    except Exception as e:
        print(f"⚠️ Erreur génération script : {e}")
        return f"Découvrez ce fait incroyable : {fact['extract'][:150]}... Pour plus de contenu, abonne-toi !"

# ============================================
# ÉTAPE 3 : Générer la voix-off (Edge TTS)
# ============================================

async def generate_voiceover_async(script, output_path="voiceover.mp3"):
    """Génère la voix-off avec Edge TTS (Microsoft, gratuit)"""
    print("\n🎤 Génération de la voix-off...")
    
    try:
        import edge_tts
        
        # Voix française naturelle
        voice = "fr-FR-DeniseNeural"  # Voix féminine
        
        communicate = edge_tts.Communicate(script, voice)
        await communicate.save(output_path)
        
        print(f"✅ Voix-off créée : {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Erreur génération voix : {e}")
        return None

def generate_voiceover(script, output_path="voiceover.mp3"):
    """Wrapper synchrone pour Edge TTS"""
    return asyncio.run(generate_voiceover_async(script, output_path))

# ============================================
# ÉTAPE 4 : Télécharger des visuels
# ============================================

def download_stock_videos(theme, count=2):
    """Télécharge des vidéos depuis Pexels"""
    print(f"\n🎬 Téléchargement de vidéos : {theme}")
    
    if not PEXELS_API_KEY:
        print("⚠️ Pas de clé Pexels - vidéo sans visuels")
        return []
    
    headers = {'Authorization': PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={theme}&per_page={count}&orientation=portrait"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        videos = response.json().get('videos', [])
        
        video_files = []
        for i, video in enumerate(videos[:count]):
            # Trouver la vidéo en qualité SD (plus rapide)
            video_file = None
            for vf in video.get('video_files', []):
                if vf.get('quality') == 'sd':
                    video_file = vf
                    break
            
            if not video_file and video.get('video_files'):
                video_file = video['video_files'][0]
            
            if video_file:
                video_url = video_file['link']
                filename = f"video_{i}.mp4"
                
                vid_response = requests.get(video_url, timeout=30)
                with open(filename, 'wb') as f:
                    f.write(vid_response.content)
                
                video_files.append(filename)
                print(f"  ✅ Téléchargé : {filename}")
        
        return video_files
        
    except Exception as e:
        print(f"⚠️ Erreur téléchargement : {e}")
        return []

# ============================================
# ÉTAPE 5 : Créer la vidéo finale
# ============================================

def create_video(video_files, voiceover_path, script, output="final_video.mp4"):
    """Assemble la vidéo avec MoviePy"""
    print("\n🎥 Création de la vidéo finale...")
    
    try:
        from moviepy.editor import (VideoFileClip, AudioFileClip, TextClip, 
                                    CompositeVideoClip, concatenate_videoclips, 
                                    ColorClip)
        
        # Charger l'audio
        audio = AudioFileClip(voiceover_path)
        duration = audio.duration
        
        # Si pas de vidéos, créer un fond coloré
        if not video_files:
            print("⚠️ Création d'un fond de couleur")
            video = ColorClip(size=(1080, 1920), color=(20, 20, 40), duration=duration)
        else:
            # Charger et traiter les vidéos
            clips = []
            for video_file in video_files:
                clip = VideoFileClip(video_file)
                # Redimensionner en format portrait 9:16
                clip = clip.resize(height=1920)
                if clip.w > 1080:
                    clip = clip.crop(x_center=clip.w/2, width=1080, height=1920)
                clips.append(clip)
            
            # Concaténer
            video = concatenate_videoclips(clips, method="compose")
            
            # Ajuster à la durée audio
            if video.duration < duration:
                # Boucler si trop court
                video = video.loop(duration=duration)
            else:
                video = video.subclip(0, duration)
        
        # Ajouter l'audio
        video = video.set_audio(audio)
        
        # Créer sous-titres simplifiés (3 mots par écran)
        words = script.split()
        subtitle_clips = []
        words_per_screen = 3
        word_duration = duration / (len(words) / words_per_screen)
        
        for i in range(0, len(words), words_per_screen):
            text = ' '.join(words[i:i+words_per_screen])
            
            txt_clip = TextClip(
                text,
                fontsize=60,
                color='white',
                font='Arial-Bold',
                stroke_color='black',
                stroke_width=2,
                size=(1000, None),
                method='caption'
            )
            txt_clip = txt_clip.set_position('center')
            txt_clip = txt_clip.set_duration(word_duration)
            txt_clip = txt_clip.set_start((i/words_per_screen) * word_duration)
            subtitle_clips.append(txt_clip)
        
        # Composer
        final = CompositeVideoClip([video] + subtitle_clips)
        
        # Exporter
        final.write_videofile(
            output,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            preset='ultrafast',
            threads=2
        )
        
        print(f"✅ Vidéo créée : {output}")
        return output
        
    except Exception as e:
        print(f"❌ Erreur création vidéo : {e}")
        import traceback
        traceback.print_exc()
        return None

# ============================================
# FONCTION PRINCIPALE
# ============================================

def main():
    """Fonction principale"""
    
    try:
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
        
        # 5. Créer la vidéo
        final_video = create_video(videos, voiceover, script)
        
        if not final_video:
            print("❌ Échec création vidéo")
            return
        
        # 6. Sauvegarder les infos
        title = f"Fait incroyable : {fact['title'][:50]}"
        description = f"{script}\n\nSource : {fact['source']}\n\n#Shorts #FaitsSurprenants #Education"
        
        info = {
            'title': title,
            'description': description,
            'video_path': final_video,
            'date': datetime.now().isoformat()
        }
        
        with open('video_info.json', 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        
        print("\n" + "="*50)
        print("✅ VIDÉO CRÉÉE AVEC SUCCÈS !")
        print(f"📁 Fichier : {final_video}")
        print(f"📝 Titre : {title}")
        print("="*50)
        
        # Note : Upload YouTube/TikTok à ajouter plus tard
        print("\n💡 Pour publier automatiquement, configurez les APIs YouTube/TikTok")
        
    except Exception as e:
        print(f"\n❌ ERREUR GÉNÉRALE : {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
