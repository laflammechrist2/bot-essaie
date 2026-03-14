import telebot
import time
import threading
import os

# --- CONFIGURATION ---
TOKEN = "8736653618:AAHUovC-cs44RWTOrbFaNKYVu-yvytax8zE"
CANAL_ID = -1003713698152
LIEN_PAYE = "https://kheskieb.mychariow.shop/prd_7cpcfx"
DUREE_ESSAI = 7200  # 2 heures en secondes
DB_FILE = "utilisateurs.txt" # Pour bloquer les tricheurs

bot = telebot.TeleBot(TOKEN)

# Fonction pour enregistrer les tricheurs
def deja_teste(user_id):
    if not os.path.exists(DB_FILE):
        return False
    with open(DB_FILE, "r") as f:
        return str(user_id) in f.read()

def marquer_teste(user_id):
    with open(DB_FILE, "a") as f:
        f.write(str(user_id) + "\n")

def processus_expulsion(user_id):
    # Attente des 2 heures
    time.sleep(DUREE_ESSAI)
    try:
        # Expulsion
        bot.ban_chat_member(CANAL_ID, user_id)
        # On débannit immédiatement (pour qu'il puisse payer et revenir)
        bot.unban_chat_member(CANAL_ID, user_id)
        
        # Message de fin d'essai
        bot.send_message(user_id, f"❌ Ton essai gratuit est terminé.\n\nPour accéder à nouveau au canal sans limite, tu peux acheter ton accès ici : {LIEN_PAYE}")
        print(f"Utilisateur {user_id} expulsé après 2h.")
    except Exception as e:
        print(f"Erreur lors de l'expulsion de {user_id} : {e}")

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    
    if deja_teste(user_id):
        bot.send_message(user_id, "⚠️ Tu as déjà utilisé ton essai gratuit. Achète un accès ici : " + LIEN_PAYE)
        return

    try:
        # Création d'un lien d'invitation unique (valable 1 fois)
        invite = bot.create_chat_invite_link(CANAL_ID, member_limit=1)
        
        bot.send_message(user_id, f"🎁 Bienvenue ! Voici ton accès gratuit pour 2 heures :\n{invite.invite_link}\n\n⚠️ Tu seras automatiquement retiré après ce délai.")
        
        # Marquer l'utilisateur comme ayant déjà testé
        marquer_teste(user_id)
        
        # Lancer le chrono dans un fil séparé (thread)
        t = threading.Thread(target=processus_expulsion, args=(user_id,))
        t.start()
        
    except Exception as e:
        bot.send_message(user_id, "Désolé, une erreur est survenue. Vérifie que le bot est bien Administrateur du canal.")
        print(f"Erreur : {e}")

print("Le bot est lancé...")
bot.polling(none_stop=True)