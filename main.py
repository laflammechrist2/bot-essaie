import telebot
import time
import threading
import os
from datetime import datetime, timedelta

# --- CONFIGURATION ---
TOKEN = "8736653618:AAHUovC-cs44RWTOrbFaNKYVu-yvytax8zE"
CANAL_ID = -1003713698152
LIEN_PAYE = "https://kheskieb.mychariow.shop/prd_7cpcfx"
DUREE_ESSAI_HEURES = 1
DB_FILE = "expulsions.txt"

bot = telebot.TeleBot(TOKEN)

# --- FONCTIONS TECHNIQUES ---
def enregistrer_expulsion(user_id):
    date_fin = datetime.now() + timedelta(hours=DUREE_ESSAI_HEURES)
    timestamp_fin = date_fin.timestamp()
    with open(DB_FILE, "a") as f:
        f.write(f"{user_id},{timestamp_fin}\n")

def est_deja_venu(user_id):
    if not os.path.exists(DB_FILE): return False
    with open(DB_FILE, "r") as f:
        return str(user_id) in f.read()

def obtenir_photo_canal(chat_id):
    try:
        chat = bot.get_chat(chat_id)
        if chat.photo:
            return bot.get_file(chat.photo.big_file_id).file_path
    except: return None

def boucle_verification_expulsions():
    while True:
        try:
            if os.path.exists(DB_FILE):
                nouvelles_lignes = []
                maintenant = datetime.now().timestamp()
                with open(DB_FILE, "r") as f:
                    lignes = f.readlines()
                for ligne in lignes:
                    parts = ligne.strip().split(",")
                    if len(parts) == 2:
                        u_id, t_fin = parts
                        if maintenant >= float(t_fin):
                            bot.ban_chat_member(CANAL_ID, int(u_id))
                            bot.unban_chat_member(CANAL_ID, int(u_id))
                            msg = (f"**❌ TON ESSAI GRATUIT DE {DUREE_ESSAI_HEURES} HEURE EST TERMINÉ.**\n\n"
                                   "<blockquote>Si tu veux continuer à suivre nos différents bande dessiné, webtoonx et manhwax et ne rien rater sur les prochains publication :</blockquote>\n\n"
                                   f"**👉 REJOINT NOUS ICI :**\n{LIEN_PAYE}\n\n"
                                   "**ON T'ATTEND DE L'AUTRE CÔTÉ ! 🚀🔥**")
                            bot.send_message(int(u_id), msg, parse_mode="HTML")
                        else: nouvelles_lignes.append(ligne)
                with open(DB_FILE, "w") as f:
                    f.writelines(nouvelles_lignes)
        except Exception as e: print(f"Erreur boucle: {e}")
        time.sleep(30)

@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        user_id = message.from_user.id
        prenom = (message.from_user.first_name).upper()
        if est_deja_venu(user_id):
            bot.send_message(user_id, f"**⚠️ {prenom} , TU AS DÉJÀ UTILISÉ TON ESSAI GRATUIT.**\n\n**ACCÈS VIP ICI :** {LIEN_PAYE}", parse_mode="HTML")
            return
        
        expire_ts = int(time.time() + (DUREE_ESSAI_HEURES * 3600))
        invite = bot.create_chat_invite_link(CANAL_ID, member_limit=1, expire_date=expire_ts)
        
        texte = (f"🤝 **BIENVENUE {prenom} PARMI NOUS .**\n\n"
                 "<blockquote>Si tu veux profiter de plus et meilleures bande dessiné excitante et veut diversifié ta culture</blockquote>\n\n"
                 f"👉 **{prenom} ,**\n"
                 "<blockquote>..Rejoignez directement le canal VIP ... tout juste là ⬇️\n👇</blockquote>\n\n"
                 f"{invite.invite_link}\n\n"
                 "**👇👇👇👇👇👇👇👇👇👇👇**\n\n"
                 "**👇 CLIC SUR LE MENU 🎛️ POUR COMMENCER 👇**")

        photo = obtenir_photo_canal(CANAL_ID)
        if photo:
            url = f"https://api.telegram.org/file/bot{TOKEN}/{photo}"
            bot.send_photo(user_id, url, caption=texte, parse_mode="HTML")
        else:
            bot.send_message(user_id, texte, parse_mode="HTML")
        enregistrer_expulsion(user_id)
    except Exception as e: print(f"Erreur Start: {e}")

if __name__ == "__main__":
    threading.Thread(target=boucle_verification_expulsions, daemon=True).start()
    print("Bot relancé...")
    bot.polling(none_stop=True)
