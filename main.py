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
            file_info = bot.get_file(chat.photo.big_file_id)
            return file_info.file_path
    except:
        return None

# --- LA TOUR DE CONTRÔLE ---

def boucle_verification_expulsions():
    while True:
        if os.path.exists(DB_FILE):
            nouvelles_lignes = []
            maintenant = datetime.now().timestamp()
            with open(DB_FILE, "r") as f:
                lignes = f.readlines()
            for ligne in lignes:
                try:
                    user_id, timestamp_fin = ligne.strip().split(",")
                    if maintenant >= float(timestamp_fin):
                        # --- MESSAGE DE FIN (MAJUSCULES ET GRAS) ---
                        msg_fin = (
                            f"**❌ TON ESSAI GRATUIT DE {DUREE_ESSAI_HEURES} HEURE EST TERMINÉ.**\n\n"
                            "<blockquote>Si tu veux continuer à suivre nos différents bande dessiné, webtoonx et manhwax et ne rien rater sur les prochains publication :</blockquote>\n\n"
                            f"**👉 REJOINT NOUS ICI :**\n{LIEN_PAYE}\n\n"
                            "**ON T'ATTEND DE L'AUTRE CÔTÉ ! 🚀🔥**"
                        )
                        bot.ban_chat_member(CANAL_ID, int(user_id))
                        bot.unban_chat_member(CANAL_ID, int(user_id))
                        bot.send_message(user_id, msg_fin, parse_mode="MarkdownV2" if "V2" in str(bot) else "Markdown")
                    else:
                        nouvelles_lignes.append(ligne)
                except: continue
            with open(DB_FILE, "w") as f:
                f.writelines(nouvelles_lignes)
        time.sleep(30)

# --- COMMANDE START ---

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    prenom = (message.from_user.first_name).upper()

    if est_deja_venu(user_id):
        bot.send_message(user_id, f"**⚠️ {prenom} , TU AS DÉJÀ UTILISÉ TON ESSAI GRATUIT.**\n\n**ACCÈS VIP ICI :** {LIEN_PAYE}", parse_mode="Markdown")
        return

    try:
        expire_ts = int(time.time() + (DUREE_ESSAI_HEURES * 3600))
        invite = bot.create_chat_invite_link(CANAL_ID, member_limit=1, expire_date=expire_ts)

        # Construction du message selon tes instructions
        texte_bienvenue = (
            f"🤝 **BIENVENUE {prenom} PARMI NOUS .**\n\n"
            "<blockquote>Si tu veux profiter de plus et meilleures bande dessiné excitante et veut diversifié ta culture</blockquote>\n\n"
            f"👉 **{prenom} ,**\n"
            "<blockquote>..Rejoignez directement le canal VIP ... tout juste là ⬇️\n👇</blockquote>\n\n"
            f"{invite.invite_link}\n"
            f"{invite.invite_link}\n"
            "**👇👇👇👇👇👇👇👇👇👇👇**\n\n"
            "**👇 CLIC SUR LE MENU 🎛️ POUR COMMENCER 👇**"
        )

        photo_path = obtenir_photo_canal(CANAL_ID)
        if photo_path:
            photo_url = f"https://api.telegram.org/file/bot{TOKEN}/{photo_path}"
            bot.send_photo(user_id, photo_url, caption=texte_bienvenue, parse_mode="HTML")
        else:
            bot.send_message(user_id, texte_bienvenue, parse_mode="HTML")

        enregistrer_expulsion(user_id)

    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    t = threading.Thread(target=boucle_verification_expulsions)
    t.daemon = True
    t.start()
    print("BOT LANCÉ AVEC LES NOUVEAUX TEXTES...")
    bot.polling(none_stop=True)
