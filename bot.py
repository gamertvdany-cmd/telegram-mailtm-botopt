import os
import random
import string
import uuid
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ---------------- TOKEN ----------------
# Tomar token de variable de entorno
TOKEN = os.environ.get("TOKEN")
API_KEY = os.environ.get("API_KEY", "clave_temporal")  # para enviar OTPs a la API

# ---------------- Datos ----------------
usuarios = {}       # chat_id -> datos del usuario
numeros_temp = {}   # número temporal -> dict: {user_chat_id, mensajes}

# ---------------- Funciones ----------------
def generar_numero():
    """Genera un número temporal tipo +1555XXXXXXX"""
    suffix = ''.join(random.choices(string.digits, k=7))
    return f"+1555{suffix}"

def generar_id():
    """Genera ID único para cada número temporal"""
    return str(uuid.uuid4())

# ---------------- Comandos del bot ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    numero = generar_numero()
    numero_id = generar_id()
    usuarios[chat_id] = numero_id
    numeros_temp[numero_id] = {"user_chat_id": chat_id, "numero": numero, "mensajes": []}

    await update.message.reply_text(
        f"✅ Tu número temporal es: {numero}\n"
        "Úsalo donde necesites recibir OTPs.\n"
        "Para simular un OTP: /sendotp <mensaje>\n"
        "Para ver tus mensajes: /inbox"
    )

async def sendotp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id not in usuarios:
        await update.message.reply_text("Primero escribe /start para generar tu número temporal.")
        return

    if not context.args:
        await update.message.reply_text("Usa: /sendotp <mensaje>")
        return

    mensaje = " ".join(context.args)
    numero_id = usuarios[chat_id]
    numeros_temp[numero_id]["mensajes"].append(mensaje)

    await update.message.reply_text(f"📩 OTP simulado recibido: {mensaje}")

async def inbox(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id not in usuarios:
        await update.message.reply_text("Primero escribe /start para generar tu número temporal.")
        return

    numero_id = usuarios[chat_id]
    mensajes = numeros_temp[numero_id]["mensajes"]
    if not mensajes:
        await update.message.reply_text("Tu bandeja está vacía 📭")
        return

    texto = "\n\n".join(mensajes)
    await update.message.reply_text(f"📬 Mensajes para {numeros_temp[numero_id]['numero']}:\n\n{texto}")

# ---------------- Mensajes normales también se guardan ----------------
async def recibir_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    texto = update.message.text

    if chat_id not in usuarios:
        return
