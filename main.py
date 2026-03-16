import telebot
import time
import threading
import os
import datetime

# --- CONFIGURATION ---
TOKEN = "8736653618:AAHUovC-cs44RWTOrbFaNKYVu-yvytax8zE"
CANAL_ID = -1003713698152
LIEN_PAYE = "https://kheskieb.mychariow.shop/prd_7cpcfx"
DUREE_ESSAI = 3600  # Modifié à 1 heure (3600 secondes)
DB_FILE = "utilisateurs.txt"

bot = telebot.TeleBot(TOKEN)

def deja_teste(user_id):
    if not os.path.exists(DB_FILE):
        return False
    with open(DB_FILE, "r") as f:
        return str(user_id) in f.read()

def marquer_teste(user_id):
    with open(DB_FILE, "a") as f:
        f.write(str(user_id) + "\n")

def processus_expulsion(user_id):
    # Attente de 1 heure
    time.sleep(DUREE_ESSAI)
    try:
        # Expulsion du canal
        bot.ban_chat_member(CANAL_ID, user_id)
        # Débannissement pour permettre un futur achat
        bot.unban_chat_member(CANAL_ID, user_id)
        
        # Notification de fin
        bot.send_message(user_id, f"❌ Ton essai gratuit de 1 heure est terminé.\n\nPour revenir définitivement, c'est ici : {LIEN_PAYE}")
        print(f"Utilisateur {user_id} expulsé après 1h.")
    except Exception as e:
        print(f"Erreur lors de l'expulsion de {user_id} : {e}")

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    
    if deja_teste(user_id):
        bot.send_message(user_id, f"⚠️ Tu as déjà profité de l'essai gratuit.\n\nPrends ton accès ici : {LIEN_PAYE}")
        return

    try:
        # Calcul de l'expiration du LIEN (1 heure à partir de maintenant)
        # On ajoute une petite marge de 5 min au lien pour être sûr qu'il puisse entrer
        expire_timestamp = int(time.time() + 3600 + 300) 
        
        # Création du lien d'invitation unique avec expiration technique
        invite = bot.create_chat_invite_link(
            CANAL_ID, 
            member_limit=1, 
            expire_date=expire_timestamp
        )
        
        bot.send_message(user_id, f"🎁 Bienvenue ! Voici ton accès gratuit pour 1 HEURE :\n\n{invite.invite_link}\n\n⚠️ Attention : Ce lien expire vite et tu seras retiré du canal dans 60 minutes.")
        
        marquer_teste(user_id)
        
        # Lancement du chrono d'expulsion (1h)
        t = threading.Thread(target=processus_expulsion, args=(user_id,))
        t.daemon = True # Pour que le thread ne bloque pas l'arrêt du bot
        t.start()
        
    except Exception as e:
        bot.send_message(user_id, "Erreur : Vérifie que le bot est Administrateur avec droit d'inviter et de bannir.")
        print(f"Erreur : {e}")

print("Le bot est lancé (Mode 1 Heure)...")
bot.polling(none_stop=True)
