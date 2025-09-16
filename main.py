import os
from flask import Flask, request
from telegram import Bot
from eth_utils import keccak

app = Flask(__name__)

# Récupération des variables d'environnement
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
MORALIS_SECRET = os.environ.get("MORALIS_SECRET")  # tu définiras ça dans Render

bot = Bot(token=TELEGRAM_TOKEN)

# Liste des wallets à suivre (débutant : en dur)
WATCHED_ADDRESSES = [
    "0x38998FD784f4D29cDfdd2454442d2Fed1d6dE4f5"
    "0x798B62eAD9ff3336f32AbbA90336cAbE6C678aAf"  # <-- mets ton wallet ici
]

# Fonction d'envoi sur Telegram
def send_message(chat_id, text):
    bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")

@app.route("/moralis_webhook", methods=["POST"])
def moralis_webhook():
    raw_body = request.get_data(as_text=True)
    provided_sig = request.headers.get("x-signature")
    
    # Vérification de la signature (sécurité)
    if provided_sig and MORALIS_SECRET:
        gen = "0x" + keccak(text=raw_body + MORALIS_SECRET).hex()
        if gen != provided_sig:
            return "invalid signature", 403

    body = request.json or {}

    # Exemple : récupération des transactions
    if "txs" in body:
        for tx in body["txs"]:
            frm = tx.get("fromAddress", "").lower()
            to = tx.get("toAddress", "").lower()
            value = int(tx.get("value", "0"))
            eth_value = value / 10**18
            tx_hash = tx.get("hash")

            # Vérifie si l'adresse suivie est impliquée
            if frm in WATCHED_ADDRESSES or to in WATCHED_ADDRESSES:
                msg = (
                    f"🔔 <b>Nouvelle transaction</b>\n"
                    f"{eth_value:.6f} ETH\n"
                    f"From: {frm}\nTo: {to}\n"
                    f"<a href='https://etherscan.io/tx/{tx_hash}'>Voir sur Etherscan</a>"
                )
                # Mets ton chat_id ici (tu peux le récupérer via getUpdates)
                send_message(chat_id="TestCryptoBsxBot", text=msg)

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
