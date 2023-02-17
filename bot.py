from telegram.ext import Updater
import telegram.ext
import jdatetime as dt
import random

updater = Updater(token='', use_context=True)
updater_log = Updater(token='',use_context=True)
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

reply_keyboard = [['🔹ورود','🔹ثبت نام'],['/Start']]
start_kb = telegram.ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
menu_keyboard = [['⏱افزودن زمان'],['📊گزارشات','🔰مسابقات','⚜️گروه ها'],['🚑راهنما','🥳حمایت مالی🥳']]
menu_kb = telegram.ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True, one_time_keyboard=True)
races_keyboard = [['⌛️پایان یافته','⏳در حال اجرا'],['🔹پیوستن','🔹ایجاد کردن','🔙بازگشت']]
races_kb = telegram.ReplyKeyboardMarkup(races_keyboard, resize_keyboard=True, one_time_keyboard=True)
back_keyboard = [['🔙بازگشت']]
back_kb = telegram.ReplyKeyboardMarkup(back_keyboard, resize_keyboard=True, one_time_keyboard=True)
r_ongoing_keyboard = [['🔙بازگشت','❌ترک مسابقه']]
r_ongoing_kb = telegram.ReplyKeyboardMarkup(r_ongoing_keyboard, resize_keyboard=True, one_time_keyboard=True)
g_keyboard = [['📗هفته','📚ماه'],['🔙بازگشت','❌ترک گروه']]
g_kb = telegram.ReplyKeyboardMarkup(g_keyboard, resize_keyboard=True, one_time_keyboard=True)
add_time_keyboard = [['🌝امروز','🌚دیروز'],['🔙بازگشت']]
add_time_kb = telegram.ReplyKeyboardMarkup(add_time_keyboard, resize_keyboard=True, one_time_keyboard=True)
admin_keyboard = [['پیام','استعلام کاربر'],['مسدود کردن','رفع مسدودیت'],['🔙بازگشت']]
admin_kb = telegram.ReplyKeyboardMarkup(admin_keyboard, resize_keyboard=True, one_time_keyboard=True)

datetime_format = '%Y/%m/%d'
timezone = 3.5 # h
users = {}
races = {'ongoing' : {}, 'finished' : {}}
groups = {}
block_users = []
admins = ['Harispy']
channel = '@kharakhenee'
dp = updater.dispatcher

import os.path
import json
from tinydb import TinyDB, Query

users_db_path = '/home/Harispy/users.json'
races_db_path = '/home/Harispy/races.json'
groups_db_path = '/home/Harispy/groups.json'
block_users_db_path = '/home/Harispy/block_users.json'

if not os.path.isfile(users_db_path):
  open(users_db_path, 'a').close()
if not os.path.isfile(races_db_path):
  open(races_db_path, 'a').close()
if not os.path.isfile(groups_db_path):
  open(groups_db_path, 'a').close()
if not os.path.isfile(block_users_db_path):
  open(block_users_db_path, 'a').close()

try :
  with open(users_db_path, 'r') as users_db:
    users = json.load(users_db)
    print('users db load successfully :)')
except:
  print('cant read users db')

try :
  with open(races_db_path, 'r') as races_db:
    races = json.load(races_db)
    print('races db load successfully :)')
except:
  print('cant read races db')

try :
  with open(groups_db_path, 'r') as groups_db:
    groups = json.load(groups_db)
    print('groups db load successfully :)')
except:
  print('cant read groups db')

try :
  with open(block_users_db_path, 'r') as block_users_db:
    block_users = json.load(block_users_db)
    print('block_users db load successfully :)')
except:
  print('cant read block_users db')
###########################################################################
def update_users_db():
  try:
    with open(users_db_path, 'w') as users_db:
      json.dump(users,users_db)
      print('users db update successfully :)')
  except:
    print('cant update users db')

def update_races_db():
  try:
    with open(races_db_path, 'w') as races_db:
      json.dump(races,races_db)
      print('races db update successfully :)')
  except:
    print('cant update races db')

def update_groups_db():
  try:
    with open(groups_db_path, 'w') as groups_db:
      json.dump(groups,groups_db)
      print('groups db update successfully :)')
  except:
    print('cant update groups db')

def update_block_users_db():
  try:
    with open(block_users_db_path, 'w') as block_users_db:
      json.dump(block_users,block_users_db)
      print('block_users db update successfully :)')
  except:
    print('cant update block_users db')
###########################################################################

time_db = TinyDB('/home/Harispy/time_db.json')
time_db_archive = TinyDB('/home/Harispy/time_db_archive.json')

def update_time_db():
  all = time_db.all()
  c = []
  now = (dt.datetime.now() + dt.timedelta(hours = timezone)).strftime(datetime_format)
  now = dt.datetime.strptime(now,datetime_format)
  for it in all:
    x = dt.datetime.strptime(it['datetime'],datetime_format)
    if (now - x) > dt.timedelta(days = 31):
      time_db_archive.insert({'username':it['username'],'datetime':it['datetime'],'time':it['time']})
      c.append(it.doc_id)
  time_db.remove(doc_ids=c)

update_time_db()

def send_msg(users_msg,msg):
  chat_id = set()
  for user in users_msg:
    chat_id.add(users[user]['chat_id'])
  chat_id.discard(0)
  for c in chat_id:
    updater.bot.send_message(chat_id = c, text = msg)
  return len(chat_id)

def send_msg_channel(id, msg):
  updater.bot.send_message(chat_id = id, text = msg)

def time_report(user, day):
  time = 0
  days = 0
  res = time_db.search(Query().username == user)
  for it in res:
    x = dt.datetime.strptime(it['datetime'],datetime_format)
    now = (dt.datetime.now() + dt.timedelta(hours = timezone)).strftime(datetime_format)
    now = dt.datetime.strptime(now,datetime_format)
    if (now - x) <= dt.timedelta(days = day) and (not now == x):
      time += it['time']
      days += 1
  if days == 0:
    days = 1
  return {'time' : time, 'days' :days}

def today(user):
  now = (dt.datetime.now() + dt.timedelta(hours = timezone)).strftime(datetime_format)
  res = time_db.search((Query().username == user) & (Query().datetime == now))
  if len(res) == 1 :
    return res[0]['time']
  else:
    return 0

def week(user):
  now = int((dt.datetime.now() + dt.timedelta(hours = timezone)).strftime('%w'))
  res = time_report(user,now)
  t = today(user)
  if t :
    res['time'] += t
    res['days'] += 1
  return res

def month(user):
  now = int((dt.datetime.now() + dt.timedelta(hours = timezone)).strftime('%d'))
  now -= 1
  res = time_report(user,now)
  t = today(user)
  if t :
    res['time'] += t
    res['days'] += 1
  return res

def ranking(players,msg):

  ranking = sorted(players.items(), key=lambda x: x[1], reverse=True)
  rank = 1
  for user in ranking:
    if rank == 1 :
      emoji = '🥇'
    elif rank == 2 :
      emoji = '🥈'
    elif rank == 3 :
      emoji = '🥉'
    else :
      emoji = '🔸'
    msg += "{}{}) {} : {:.2f}⌛️\n".format(emoji,rank,user[0],user[1])
    rank += 1
  return msg

def race_info(race_code, state):
  now = (dt.datetime.now() + dt.timedelta(hours = timezone))
  if state == 'finished':
    time = 'مسابقه پایان یافته است'
  elif dt.datetime.strptime(races[state][race_code]['start_time'],datetime_format) > now :
    time_remaining = dt.datetime.strptime(races[state][race_code]['start_time'],datetime_format) - now
    time = str(time_remaining) + ' تا شروع مسابقه'
  else:
    time_remaining = dt.datetime.strptime(races[state][race_code]['end_time'],datetime_format) - now
    time = str(time_remaining).split('.')[0] + '\n⏱باقی مانده تا پایان مسابقه'

  result = "🔹🔶{}🔶🔹\n\nکد : {}\n{}\n\nرتبه بندی :\n\n".format(races[state][race_code]['name'],race_code,time)
  return ranking(races[state][race_code]['members'],result)

def group_day(code):
  res = {}
  for user in groups[code]['members']:
    res[user] = today(user)
  return ranking(res,"🔹🔶{}🔶🔹\n\nCode : {}\n\nرتبه بندی روزانه :\n\n".format(groups[code]['name'],code))

def group_week(code):
  res = {}
  for user in groups[code]['members']:
    res[user] = week(user)['time']
  return ranking(res,"🔹🔶{}🔶🔹\n\nCode : {}\n\nرتبه بندی هفتگی :\n\n".format(groups[code]['name'],code))

def group_month(code):
  res = {}
  for user in groups[code]['members']:
    res[user] = month(user)['time']
  return ranking(res,"🔹🔶{}🔶🔹\n\nCode : {}\n\nرتبه بندی ماهانه :\n\n".format(groups[code]['name'],code))

def update_finished_race() :
  temp = []
  for race in races['ongoing']:
    if dt.datetime.strptime(races['ongoing'][race]['end_time'],datetime_format) < (dt.datetime.now() + dt.timedelta(hours = timezone)) :
      races['finished'][race] = races['ongoing'][race]
      temp.append(race)

  for t in temp :
    for m in races['ongoing'][t]['members']:
      users[m]['races']['finished'][races['finished'][t]['name']] = t
      del users[m]['races']['ongoing'][races['finished'][t]['name']]
    del races['ongoing'][t]
    update_users_db()
    update_races_db()
    try:
      if len(races['finished'][t]['members']) > 0 :
        send_msg(races['finished'][t]['members'],race_info(t,'finished'))
      log(race_info(t,'finished'))
    except:
      log("Error : update finished races send msg")
    log('Race {} just finished! name : {}'.format(t,races['finished'][t]['name']))

update_finished_race()

def races_kb_gen(user,state):
  keyboard = [[]]
  for race in users[user]['races'][state] :
    c = 1
    temp = 0
    if c > 3 :
      c -= 3
      keyboard.append([])
      temp +=1
    keyboard[temp].append(race)
    c +=1
  keyboard.append(['🔙بازگشت'])
  return telegram.ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

def groups_kb_gen(user):
  keyboard = [[]]
  for group in users[user]['groups'] :
    c = 1
    temp = 0
    if c > 3 :
      c -= 3
      keyboard.append([])
      temp +=1
    keyboard[temp].append(group)
    c +=1
  keyboard.append(['🔹پیوستن','🔹ایجاد کردن','🔙بازگشت'])
  return telegram.ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

def add_time(user, time, date):
  date = dt.datetime.fromgregorian(datetime=date)
  h, m = map(int,time.split(':'))
  time = h + (m/60)
  if time > 24 :
    return False
  date += dt.timedelta(hours = timezone)
  date = date.strftime(datetime_format)
  l = time_db.search((Query().username == user) & (Query().datetime == date))
  if len(l) == 0:
    id = time_db.insert({'username':user,'datetime':date,'time':time})
  else :
    if (time + l[0]['time']) > 24 :
      return False
    time_db.update({'time' : time + l[0]['time']},(Query().username == user) & (Query().datetime == date))

  users[user]['total'] += time

  for race in users[user]['races']['finished']:
    if dt.datetime.strptime(races['finished'][users[user]['races']['finished'][race]]['start_time'],datetime_format) <= dt.datetime.strptime(date,datetime_format) and dt.datetime.strptime(races['finished'][users[user]['races']['finished'][race]]['end_time'],datetime_format) > dt.datetime.strptime(date,datetime_format) :
      races['finished'][users[user]['races']['finished'][race]]['members'][user] += time

  for race in users[user]['races']['ongoing']:
    if dt.datetime.strptime(races['ongoing'][users[user]['races']['ongoing'][race]]['start_time'],datetime_format) <= dt.datetime.strptime(date,datetime_format) :
      races['ongoing'][users[user]['races']['ongoing'][race]]['members'][user] += time
  print(user,' Added ',time,'h')
  return True

def report(user):
  w = time_report(user,7)
  m = time_report(user,30)
  state = '👨🏼‍🎓{}👩🏼‍🎓\n\n\n'.format(user)
  state += '⏱کل زمان مطالعه شما : {:.2f} ساعت\n\n'.format(users[user]['total'])
  state += '📝مطالعه امروز : {:.2f} ساعت\n'.format(today(user))
  state += '📓مطالعه 7 روز گذشته : {:.2f} ساعت\n'.format(w['time'])
  state += '📚مطالعه 30 روز گذشته : {:.2f} ساعت\n\n'.format(m['time'])
  state += '⌛️میانگین 7 روز گذشته(روز های وارد شده) : {:.2f} ساعت\n'.format(w['time'] / w['days'])
  state += '⌛️میانگین 30 روز گذشته(روز های وارد شده) : {:.2f} ساعت\n\n'.format(m['time'] / m['days'])
  state += '⌛️میانگین 7 روز گذشته : {:.2f} ساعت\n'.format(w['time'] / 7)
  state += '⌛️میانگین 30 روز گذشته : {:.2f} ساعت\n'.format(m['time'] / 30)
  if (w['time'] / 7) > (m['time'] / 30) :
    state += '\n📈رشد میانگین هفته نسبت به ماه : 🔷{:.1f}'.format((w['time'] / 7)-(m['time'] / 30))
  if (w['time'] / 7) < (m['time'] / 30) :
    state += '\n📉افت میانگین هفته نسبت به ماه : 🔶{:.1f}'.format((m['time'] / 30)-(w['time'] / 7))
  return state

def remove_time(user,id):
  id = int(id)
  if time_db.get(doc_id=id)['username'] == user:
    users[user]['total'] -= time_db.get(doc_id=id)['time']
    time_db.remove(doc_ids=[id])

def log(msg):
  print(msg)
  updater_log.bot.send_message(chat_id="149014424", text=msg)
#sorted(d.items(), key=lambda x: x[1])

# /start

def start(update, context):
  if 'state' in context.user_data :
    if context.user_data['login'] == True:
      context.user_data['state'] = 'menu'
      context.user_data['back_state'] = '0'
      context.user_data['back_msg'] = ''
      context.bot.send_message(chat_id = update.effective_chat.id,text = "منو:",reply_markup=menu_kb)
      return

  for user in users:
    if users[user]['chat_id'] == update.effective_chat.id :
      context.user_data['login'] = True
      context.user_data['state'] = 'menu'
      context.user_data['back_state'] = '0'
      context.user_data['back_msg'] = ''
      context.bot.send_message(chat_id = update.effective_chat.id,text = "به سامانه مطالعاتی خوش امدید ^^)\nبرای مطالعه راهنما از دستور /help استفاده کنید",reply_markup=menu_kb)
      context.user_data['username'] = user
      context.user_data['pass'] = users[user]['pass']
      if not users[user]['tel_id'] == str(update.message.from_user.username):
        users[user]['tel_id'] = str(update.message.from_user.username)
        update_users_db()
      return

  context.user_data['login'] = False
  context.user_data['state'] = '0' # start
  context.user_data['back_state'] = '0'
  context.user_data['back_msg'] = ''

  context.bot.send_message(chat_id = update.effective_chat.id,text = "به سامانه مطالعاتی خوش امدید ^^)\nبرای مطالعه راهنما از دستور /help استفاده کنید",reply_markup=start_kb)

# /help

def help(update, context):
  msg ="راهنما:\n\nیوزرنیم و پسورد خود را به خاطر بسپارید تا وقتی از اکانت دیگری میخواهید با ربات کار کنید از انها استفاده کنید\nتذکر : تاریخی ک زمان رو اضافه میکنید مهمه پس برای اضافه کردن زمان مطالعه دیروز گزینه دیروز رو انتخاب کنید\nتذکر : اگر پیامی را برای ربات ارسال کردید پاک کردن و یا ویرایش پیام باعث تغییرش نمیشود چون ربات پیام رو دریافت کرده\nدر صورت داشتن مشکل به مدیریت پیام دهید\n\nسرور دیسکورد :\ndiscord.gg/wzQjSS".format(channel)
  #برای استفاده از ربات در هنگام خاموشی میتوانید از قابلیت افلاین استفاده کنید که به شرح زیر است : \nفقط کافیست پیام هایی که در هنگام روشن بودن برای ربات ارسال میکنید در زمان خاموشی به ترتیب ارسال کنید\nبرای مثال برای اضافه کردن 2 ساعت زمان پیام های زیر را در زمان خاموشی برای ربات ارسال میکنیم\n\n⏱افزودن زمان\n🌝امروز\n2:00\n\nیا برای دیدن مسابقه ی در حال اجرا ای با نام abc پیام های زیر را ارسال میکنیم\n\n🔰مسابقات\n⏳در حال اجرا\nabc\n\nنکته : فوروارد کردن پیام ها مشکلی ایجاد نمیکند\nدر اضافه کردن زمان به صورت افلاین تاریخ ارسال پیام در نظر گرفته میشود نه تارخ روشن شدن روبات\n
  context.bot.send_message(chat_id = update.effective_chat.id,text = msg)

def admin(update, context):
  if 'state' not in context.user_data :
    start(update, context)
  if not context.user_data['login'] :
    context.bot.send_message(chat_id = update.effective_chat.id, text="لطفا ابتدا وارد اکانت خود شوید :/")
    return

  if context.user_data['username'] in admins:
    context.user_data['state'] = 'admin'
    context.user_data['back_state'] = 'menu'
    context.user_data['back_msg'] = 'menu'
    context.bot.send_message(chat_id = update.effective_chat.id,text = "پنل مدیریت فعال شد ^^)",reply_markup=None)
    context.bot.send_message(chat_id = update.effective_chat.id,text = "تعداد کاربران ربات : {}\nتعداد گروه ها : {}\nتعداد مسابقات در حال اجرا : {}\n".format(len(users),len(groups),len(races['ongoing'])),reply_markup=admin_kb)
  else:
    context.bot.send_message(chat_id = update.effective_chat.id,text = "شما به این بخش دسترسی ندارید")

# msg

def msg(update, context):

  if update.effective_chat.id in block_users:
    return

  if type(update.message) == type(None):
    return

  msg = update.message.text

  if msg == '🚑راهنما':
    help(update, context)
    return

  if 'state' not in context.user_data :
    start(update, context)

  if not context.user_data['login'] :

    log('@{} ({}) {}'.format(str(update.message.from_user.username),dt.datetime.fromgregorian(datetime=(update.message.date + dt.timedelta(hours = timezone))).strftime('%H : %M'),msg))

    if msg == "🔹ثبت نام": #signup
      context.bot.send_message(chat_id = update.effective_chat.id, text="نام کاربری را وارد کنید :")
      context.user_data['state'] = 'su1'
      return

    if msg == "🔹ورود": #sign in
      context.bot.send_message(chat_id = update.effective_chat.id, text="نام کاربری خود را وارد کنید :")
      context.user_data['state'] = 'si1'
      return

    if context.user_data['state'] == 'su1' : #username
      if update.message.text in users :
        context.bot.send_message(chat_id = update.effective_chat.id, text="این نام کاربری قبلا انتخواب شده است 😕 \nنام کاربری دیگری انتخواب کنید :")
        return

      context.user_data['username'] = update.message.text
      context.bot.send_message(chat_id = update.effective_chat.id, text="رمز عبور را وارد کنید :")
      context.user_data['state'] = 'su2'
      return

    elif context.user_data['state'] == 'su2' : #pass
      username = context.user_data['username']
      password = update.message.text

      try : #add new user
        users[username] = {'pass' : password,'total' : 0, 'races' : {'ongoing' : {}, 'finished' : {}}, 'groups': {}, 'chat_id':update.effective_chat.id, 'tel_id' : str(update.message.from_user.username)}
        context.user_data['state'] = 'menu'
        context.user_data['login'] = True
        context.bot.send_message(chat_id = update.effective_chat.id, text="تمام... اکانت ساخته شد ;)",reply_markup=menu_kb)
        update_users_db()
        for admin in admins:
          updater.bot.send_message(chat_id = users[admin]['chat_id'], text = 'کاربر جدید : '.format(username))
        ######### log
        log("New User : {}".format(context.user_data['username']))
        ######### log
        return

      except:
        context.bot.send_message(chat_id = update.effective_chat.id, text="دوباره امتحان کنید :/")
        context.user_data['state'] == '0'
        context.user_data.clear()
        return

    if context.user_data['state'] == 'si1' : #username
      context.user_data['username'] = update.message.text
      context.bot.send_message(chat_id = update.effective_chat.id, text="رمز عبور خود را وارد کنید:")
      context.user_data['state'] = 'si2'
      return

    elif context.user_data['state'] == 'si2' : #login
      context.user_data['pass'] = update.message.text
      username = context.user_data['username']
      password = context.user_data['pass']

      try : #logining
        if username in users :
          if users[username]['pass'] == password :
            context.user_data['state'] = 'menu'
            context.user_data['login'] = True
            context.bot.send_message(chat_id = update.effective_chat.id, text="سلام {} ;)".format(context.user_data['username']),reply_markup=menu_kb)

            if not users[username]['chat_id'] == update.effective_chat.id:
              users[username]['chat_id'] = update.effective_chat.id

            if not users[username]['tel_id'] == str(update.message.from_user.username):
              users[username]['tel_id'] = str(update.message.from_user.username)

            update_users_db()
            return

          else:
            context.bot.send_message(chat_id = update.effective_chat.id, text="رمز عبور اشتباه است.")
            context.user_data['state'] = 'si1'
            return

        else:
          context.bot.send_message(chat_id = update.effective_chat.id, text="نام کاربری یافت نشد. دوباره امتحان کنید :/")
          context.user_data['state'] = 'si1'
          return
        ######### log
        log("login : {}".format(context.user_data['username']))
        ######### log
        return

      except:
        context.bot.send_message(chat_id = update.effective_chat.id, text="دوباره امتحان کنید :/")
        context.user_data['state'] == '0'
        context.user_data.clear()
        return

  else:
    log('{}({}) : {}'.format(context.user_data['username'],dt.datetime.fromgregorian(datetime=(update.message.date + dt.timedelta(hours = timezone))).strftime('%H : %M'),msg))

    if msg == "🔙بازگشت" :
      if context.user_data['back_state'] == '0':
        context.bot.send_message(chat_id = update.effective_chat.id, text="شما نمیتوانید عقب بروید😐")
        return
      context.user_data['state'] = context.user_data['back_state']
      msg = context.user_data['back_msg']

    if context.user_data['state'] == 'admin' and msg == 'مسدود کردن':
      context.bot.send_message(chat_id = update.effective_chat.id, text='نام کاربری را برای مسدود کردن ارسال کنید',reply_markup=back_kb)
      context.user_data['state'] = 'admin_block'
      context.user_data['back_state'] = 'admin'
      context.user_data['back_msg'] = 'admin'
      return

    if context.user_data['state'] == 'admin_block':
      user = update.message.text
      if user in users :
        if user not in admins:
          if users[user]['chat_id'] not in block_users:
            block_users.append(users[user]['chat_id'])
            update_block_users_db()
            context.bot.send_message(chat_id = update.effective_chat.id, text='کاربر مسدود شد',reply_markup=admin_kb)
            send_msg([user],'دسترسی شما به ربات مسدود شده است')
          else:
            context.bot.send_message(chat_id = update.effective_chat.id, text="کاربر قبلا مسدود شده است",reply_markup=admin_kb)
        else:
          context.bot.send_message(chat_id = update.effective_chat.id, text='شما نمی توانید ادمین را مسدود کنید',reply_markup=admin_kb)
      else:
        context.bot.send_message(chat_id = update.effective_chat.id, text="کاربر پیدا نشد!",reply_markup=admin_kb)
      context.user_data['state'] = 'admin'
      context.user_data['back_state'] = 'menu'
      context.user_data['back_msg'] = 'menu'
      return

    if context.user_data['state'] == 'admin' and msg == 'رفع مسدودیت':
      context.bot.send_message(chat_id = update.effective_chat.id, text='نام کاربری را برای رفع مسدودیت ارسال کنید',reply_markup=back_kb)
      context.user_data['state'] = 'admin_unblock'
      context.user_data['back_state'] = 'admin'
      context.user_data['back_msg'] = 'admin'
      return

    if context.user_data['state'] == 'admin_unblock':
      user = update.message.text
      if user in users :
        if users[user]['chat_id'] in block_users:
          block_users.remove(users[user]['chat_id'])
          update_block_users_db()
          context.bot.send_message(chat_id = update.effective_chat.id, text='مسدودیت کاربر رفع شد',reply_markup=admin_kb)
          send_msg([user],'مسدودیت حساب شما رفع شده است')
        else:
          context.bot.send_message(chat_id = update.effective_chat.id, text="کاربر مسدود نیست",reply_markup=admin_kb)
      else:
        context.bot.send_message(chat_id = update.effective_chat.id, text="کاربر پیدا نشد!",reply_markup=admin_kb)
      context.user_data['state'] = 'admin'
      context.user_data['back_state'] = 'menu'
      context.user_data['back_msg'] = 'menu'
      return

    if context.user_data['state'] == 'admin' and msg == 'پیام':
      context.bot.send_message(chat_id = update.effective_chat.id, text='نام کاربری گیرنده را وارد کنید : (برای پیام عمومی "all" را ارسال کنید)',reply_markup=back_kb)
      context.user_data['state'] = 'admin_msg'
      context.user_data['back_state'] = 'admin'
      context.user_data['back_msg'] = 'admin'
      return

    if context.user_data['state'] == 'admin_msg':
      context.user_data['admin_msg_to'] = update.message.text
      context.bot.send_message(chat_id = update.effective_chat.id, text='متن پیام را ارسال کنید:',reply_markup=back_kb)
      context.user_data['state'] = 'admin_msg2'
      context.user_data['back_state'] = 'admin'
      context.user_data['back_msg'] = 'پیام'
      return

    if context.user_data['state'] == 'admin_msg2':
      msg = update.message.text
      try:
        if context.user_data['admin_msg_to'] == 'all':
          res = send_msg(users, msg)
          context.bot.send_message(chat_id = update.effective_chat.id,text = "🎉پیام به {} کاربر ارسال شد".format(res))
        else:
          if context.user_data['admin_msg_to'] in users :
            send_msg([context.user_data['admin_msg_to']], msg)
            context.bot.send_message(chat_id = update.effective_chat.id,text = "پیام ارسال شد😁")
          else:
            context.bot.send_message(chat_id = update.effective_chat.id,text = "کاربر پیدا نشد !")

      except:
        context.bot.send_message(chat_id = update.effective_chat.id,text = "خطا!")
      context.user_data['state'] = 'admin'
      context.user_data['back_state'] = 'menu'
      context.user_data['back_msg'] = 'menu'

    if context.user_data['state'] == 'admin' and msg == 'استعلام کاربر':
      context.bot.send_message(chat_id = update.effective_chat.id, text='نام کاربری را برای استعلام ارسال کنید ( برای دریافت لیست کاربران "all" را ارسال کنید) :',reply_markup=back_kb)
      context.user_data['state'] = 'admin_user'
      context.user_data['back_state'] = 'admin'
      context.user_data['back_msg'] = 'admin'
      return

    if context.user_data['state'] == 'admin_user':
      user = update.message.text
      if user == "all":
        res = "({})".format(len(users))
        for it in users:
          res += it
          res += ','
        context.bot.send_message(chat_id = update.effective_chat.id, text=res,reply_markup=admin_kb)
      elif user in users :
        g = ''
        r = ''
        for it in users[user]['groups']:
          g += '{} : {}'.format(it, users[user]['groups'][it])
          g += '\n'
        for it in users[user]['races']['ongoing']:
          r += '{} : {}'.format(it, users[user]['races']['ongoing'][it])
          r += '\n'
        res = "نام کاربری : {}\nرمز عبور : {}\nآیدی تلگرام : {}\n\nگروه های عضو شده : {}\nمسابقات در حال اجرای عضو شده : {}".format(user,users[user]['pass'],users[user]['tel_id'],g,r)
        context.bot.send_message(chat_id = update.effective_chat.id, text=res,reply_markup=None)
        context.bot.send_message(chat_id = update.effective_chat.id, text=report(user),reply_markup=admin_kb)
      else:
        context.bot.send_message(chat_id = update.effective_chat.id, text="کاربر پیدا نشد!",reply_markup=admin_kb)

      context.user_data['state'] = 'admin'
      context.user_data['back_state'] = 'menu'
      context.user_data['back_msg'] = 'menu'
      return

    if msg == "🔹ثبت نام" or msg == "🔹ورود" : #check
      context.bot.send_message(chat_id = update.effective_chat.id, text="شما با نام {} وارد شده اید".format(context.user_data['username']),reply_markup=menu_kb)
      return

    if context.user_data['state'] == 'menu' and msg == "🔰مسابقات" :
      context.bot.send_message(chat_id = update.effective_chat.id, text="Finished races or Ongoing races ?",reply_markup=races_kb)
      context.user_data['state'] = 'r'
      context.user_data['back_state'] = 'menu'
      context.user_data['back_msg'] = 'menu'
      return

    if context.user_data['state'] == 'r' and msg == "🔹پیوستن" :
      if len(users[context.user_data['username']]['races']['ongoing']) >= 3 :
        context.bot.send_message(chat_id = update.effective_chat.id, text="شما نمیتوانید در بیش از ۳ مسابقه عضو شوید",reply_markup=races_kb)
        return
      context.bot.send_message(chat_id = update.effective_chat.id, text="کد مسابقه را وارد کنید :",reply_markup=back_kb)
      context.user_data['state'] = 'r_join1'
      context.user_data['back_state'] = 'menu'
      context.user_data['back_msg'] = '🔰مسابقات'
      return

    if context.user_data['state'] == 'r_join1':
      race_code = update.message.text
      update_finished_race()
      if race_code in races['ongoing'] :
        if context.user_data['username'] in races['ongoing'][race_code]['members'] :
          context.bot.send_message(chat_id = update.effective_chat.id, text="شما از قبل در این مسابقه عضو هستید",reply_markup=races_kb)
          context.user_data['state'] = 'r'
          context.user_data['back_state'] = 'menu'
          context.user_data['back_msg'] = 'menu'
          return
        elif len(races['ongoing'][race_code]['members']) >= 40 :
          context.bot.send_message(chat_id = update.effective_chat.id, text="ظرفیت مسابقه تکمیل است.",reply_markup=races_kb)
          context.user_data['state'] = 'r'
          context.user_data['back_state'] = 'menu'
          context.user_data['back_msg'] = 'menu'
          return
        else :
          races['ongoing'][race_code]['members'][context.user_data['username']] = 0
          users[context.user_data['username']]['races']['ongoing'][races['ongoing'][race_code]['name']] = race_code
          update_users_db()
          update_races_db()
          context.bot.send_message(chat_id = update.effective_chat.id, text="شما با موفقیت در مسابقه عضو شدید🥳",reply_markup=races_kb)
          context.user_data['state'] = 'r'
          context.user_data['back_state'] = 'menu'
          context.user_data['back_msg'] = 'menu'
          return
      else :
        context.bot.send_message(chat_id = update.effective_chat.id, text="مسابقه پیدا نشد!",reply_markup=back_kb)
        return


    if context.user_data['state'] == 'r' and msg == "🔹ایجاد کردن" :
      if len(users[context.user_data['username']]['races']['ongoing']) >= 3 :
        context.bot.send_message(chat_id = update.effective_chat.id, text="شما نمیتوانید در بیش از ۳ مسابقه عضو شوید",reply_markup=races_kb)
        return
      context.bot.send_message(chat_id = update.effective_chat.id, text="نام مسابقه را وارد کنید :",reply_markup=back_kb)
      context.user_data['state'] = 'r_create1'
      context.user_data['back_state'] = 'menu'
      context.user_data['back_msg'] = '🔰مسابقات'
      return

    if context.user_data['state'] == 'r_create1' :
      context.chat_data['race_name'] = update.message.text
      context.bot.send_message(chat_id = update.effective_chat.id, text="تاریخ شروع مسابقه را وارد کنید : \nبرای مثال: 1399/05/28",reply_markup=back_kb)
      context.user_data['state'] = 'r_create2'
      context.user_data['back_state'] = 'r'
      context.user_data['back_msg'] = '🔹ایجاد کردن'
      return

    if context.user_data['state'] == 'r_create2' :
      try: #check time
        time = dt.datetime.strptime(update.message.text,datetime_format)
        if time > (dt.datetime.now() + dt.timedelta(hours = timezone)):
          context.chat_data['race_start_time'] = time.strftime(datetime_format)
        else:
          context.bot.send_message(chat_id = update.effective_chat.id, text="زمان قابل قبول نیست\nدوباره امتحان کنید:",reply_markup=back_kb)
          return
      except:
        context.bot.send_message(chat_id = update.effective_chat.id, text="دوباره در فرمت درست ارسال کنید :",reply_markup=back_kb)
        return

      context.bot.send_message(chat_id = update.effective_chat.id, text="تاریخ پایان مسابقه را وارد کنید : \nبرای مثال : 1399/06/30",reply_markup=back_kb)
      context.user_data['state'] = 'r_create3'
      context.user_data['back_state'] = 'r_create1'
      context.user_data['back_msg'] = context.chat_data['race_name']
      return

    if context.user_data['state'] == 'r_create3' :
      try: # check time
        time = dt.datetime.strptime(update.message.text,datetime_format) + dt.timedelta(days = +1)
        if time > dt.datetime.strptime(context.chat_data['race_start_time'],datetime_format):
          context.chat_data['race_end_time'] = time.strftime(datetime_format)
        else:
          context.bot.send_message(chat_id = update.effective_chat.id, text="تاریخ قابل قبول نیست\nدوباره امتحان کنید :",reply_markup=back_kb)
          return
      except:
        context.bot.send_message(chat_id = update.effective_chat.id, text="دوباره در فرمت درست ارسال کنید :",reply_markup=back_kb)
        return

      race_code = str(random.randint(100000, 1000000))
      while race_code in races:
        race_code = str(random.randint(100000, 1000000))
      races['ongoing'][race_code] = {'name' : context.chat_data['race_name'], 'members' : {context.user_data['username'] : 0}, 'start_time' : context.chat_data['race_start_time'], 'end_time' : context.chat_data['race_end_time']}
      update_races_db()
      users[context.user_data['username']]['races']['ongoing'][races['ongoing'][race_code]['name']] = race_code
      update_users_db()
      context.bot.send_message(chat_id = update.effective_chat.id, text="تبریک🥳 مسابقه ساخته شد \nکد مسابقه شما : {} \nکد رو به دوستتنتون بدهید ^^".format(race_code),reply_markup=races_kb)
      context.user_data['state'] = 'r'
      context.user_data['back_state'] = 'menu'
      context.user_data['back_msg'] = 'menu'
      context.chat_data.clear()
      return

    if context.user_data['state'] == 'r' and msg == "⏳در حال اجرا" :
      update_finished_race()
      if len(users[context.user_data['username']]['races']['ongoing']) == 0 :
        context.bot.send_message(chat_id = update.effective_chat.id, text="شما مسابقه در حال اجرا ندارید!",reply_markup=races_kb)
        return
      context.bot.send_message(chat_id = update.effective_chat.id, text="کدام ؟",reply_markup=races_kb_gen(context.user_data['username'],'ongoing'))
      context.user_data['state'] = 'r_ongoing1'
      context.user_data['back_state'] = 'menu'
      context.user_data['back_msg'] = '🔰مسابقات'
      return

    if context.user_data['state'] == 'r_ongoing1':
      if update.message.text in users[context.user_data['username']]['races']['ongoing']:
        race_code = users[context.user_data['username']]['races']['ongoing'][update.message.text]
        context.bot.send_message(chat_id = update.effective_chat.id, text=race_info(race_code, 'ongoing'),reply_markup=r_ongoing_kb)
        context.user_data['r_ongoing_left'] = race_code
        context.user_data['state'] = 'r_ongoing2'
        context.user_data['back_state'] = 'r'
        context.user_data['back_msg'] = '⏳در حال اجرا'
        return
      else:
        context.bot.send_message(chat_id = update.effective_chat.id, text="Wrong!",reply_markup=races_kb_gen(context.user_data['username'],'ongoing'))
        return

    if context.user_data['state'] == 'r_ongoing2' and msg == "❌ترک مسابقه":
      race_name = races['ongoing'][context.user_data['r_ongoing_left']]['name']
      del users[context.user_data['username']]['races']['ongoing'][race_name]
      update_users_db()
      del races['ongoing'][context.user_data['r_ongoing_left']]['members'][context.user_data['username']]
      update_races_db()
      context.bot.send_message(chat_id = update.effective_chat.id, text='شما از {} خارج شدید'.format(race_name),reply_markup=races_kb_gen(context.user_data['username'],'ongoing'))
      context.user_data['state'] = 'r_ongoing1'
      context.user_data['back_state'] = 'menu'
      context.user_data['back_msg'] = '🔰مسابقات'
      return
##################################################################################
    if context.user_data['state'] == 'menu' and msg == "⚜️گروه ها" :
      context.bot.send_message(chat_id = update.effective_chat.id, text="کدام ؟",reply_markup=groups_kb_gen(context.user_data['username']))
      context.user_data['state'] = 'g'
      context.user_data['back_state'] = 'menu'
      context.user_data['back_msg'] = 'menu'
      return

    if context.user_data['state'] == 'g' and msg == "🔹پیوستن" :
      if len(users[context.user_data['username']]['groups']) >= 6 :
        context.bot.send_message(chat_id = update.effective_chat.id, text="شما نمیتوانید در بیش از ۶ گروه عضو شوید😕",reply_markup=groups_kb_gen(context.user_data['username']))
        return
      context.bot.send_message(chat_id = update.effective_chat.id, text="کد گروه را وارد کنید :",reply_markup=back_kb)
      context.user_data['state'] = 'g_join1'
      context.user_data['back_state'] = 'menu'
      context.user_data['back_msg'] = '⚜️گروه ها'
      return

    if context.user_data['state'] == 'g_join1':
      group_code = update.message.text
      if group_code in groups :
        if context.user_data['username'] in groups[group_code]['members'] :
          context.bot.send_message(chat_id = update.effective_chat.id, text="شما قبلا در این گروه عضو شده اید 🙃",reply_markup=groups_kb_gen(context.user_data['username']))
          context.user_data['state'] = 'g'
          context.user_data['back_state'] = 'menu'
          context.user_data['back_msg'] = 'menu'
          return
        else :
          groups[group_code]['members'].append(context.user_data['username'])
          users[context.user_data['username']]['groups'][groups[group_code]['name']] = group_code
          update_users_db()
          update_groups_db()
          context.bot.send_message(chat_id = update.effective_chat.id, text="با موفقیت به گروه پیوستید",reply_markup=groups_kb_gen(context.user_data['username']))
          context.user_data['state'] = 'g'
          context.user_data['back_state'] = 'menu'
          context.user_data['back_msg'] = 'menu'
          return
      else :
        context.bot.send_message(chat_id = update.effective_chat.id, text="گروه پیدا نشد😕",reply_markup=back_kb)
        return


    if context.user_data['state'] == 'g' and msg == "🔹ایجاد کردن" :
      if len(users[context.user_data['username']]['groups']) >= 6 :
        context.bot.send_message(chat_id = update.effective_chat.id, text="شما نمیتوانید در بیشتر از ۶ گروه عضو شوید ",reply_markup=groups_kb_gen(context.user_data['username']))
        return
      context.bot.send_message(chat_id = update.effective_chat.id, text="نامی برای گروه انتخواب کنید :",reply_markup=back_kb)
      context.user_data['state'] = 'g_create1'
      context.user_data['back_state'] = 'menu'
      context.user_data['back_msg'] = '⚜️گروه ها'
      return

    if context.user_data['state'] == 'g_create1' :

      group_code = str(random.randint(10000, 100000))
      while group_code in groups:
        group_code = str(random.randint(10000, 100000))
      groups[group_code] = {'name' : update.message.text, 'members' : [context.user_data['username']]}
      update_groups_db()
      users[context.user_data['username']]['groups'][groups[group_code]['name']] = group_code
      update_users_db()
      context.bot.send_message(chat_id = update.effective_chat.id, text="تبریک🥳 گروه ساخته شد \nکد گروه شما : {} \nکد گروه را برای دوستانتان ارسال کنید ^^".format(group_code),reply_markup=groups_kb_gen(context.user_data['username']))
      context.user_data['state'] = 'g'
      context.user_data['back_state'] = 'menu'
      context.user_data['back_msg'] = 'menu'
      context.chat_data.clear()
      return

    if context.user_data['state'] == 'g':
      if update.message.text in users[context.user_data['username']]['groups']:
        group_code = users[context.user_data['username']]['groups'][update.message.text]
        context.bot.send_message(chat_id = update.effective_chat.id, text=group_day(group_code),reply_markup=g_kb)
        context.user_data['g_left'] = group_code
        context.user_data['state'] = 'g1'
        context.user_data['back_state'] = 'menu'
        context.user_data['back_msg'] = '⚜️گروه ها'
        return
      else:
        context.bot.send_message(chat_id = update.effective_chat.id, text="گروه مورد نظر پیدا نشد 😕",reply_markup=groups_kb_gen(context.user_data['username']))
        return

    if context.user_data['state'] == 'g1' and msg == "📗هفته":
      context.bot.send_message(chat_id = update.effective_chat.id, text=group_week(context.user_data['g_left']),reply_markup=g_kb)
      context.user_data['state'] = 'g1'
      context.user_data['back_state'] = 'menu'
      context.user_data['back_msg'] = '⚜️گروه ها'
      return

    if context.user_data['state'] == 'g1' and msg == "📚ماه":
      context.bot.send_message(chat_id = update.effective_chat.id, text=group_month(context.user_data['g_left']),reply_markup=g_kb)
      context.user_data['state'] = 'g1'
      context.user_data['back_state'] = 'menu'
      context.user_data['back_msg'] = '⚜️گروه ها'
      return

    if context.user_data['state'] == 'g1' and msg == "❌ترک گروه":
      group_name = groups[context.user_data['g_left']]['name']
      del users[context.user_data['username']]['groups'][group_name]
      update_users_db()
      groups[context.user_data['g_left']]['members'].remove(context.user_data['username'])
      if len(groups[context.user_data['g_left']]['members']) == 0:
        del groups[context.user_data['g_left']]
      update_groups_db()
      context.bot.send_message(chat_id = update.effective_chat.id, text='شما از {} خارج شدید'.format(group_name),reply_markup=groups_kb_gen(context.user_data['username']))
      context.user_data['state'] = 'g'
      context.user_data['back_state'] = 'menu'
      context.user_data['back_msg'] = 'menu'
      return

      ##############################################
    if context.user_data['state'] == 'r' and msg == "⌛️پایان یافته" :
      update_finished_race()
      if len(users[context.user_data['username']]['races']['finished']) == 0 :
        context.bot.send_message(chat_id = update.effective_chat.id, text="مسابقه پایان یافته ای وجود ندارد !",reply_markup=races_kb)
        return
      context.bot.send_message(chat_id = update.effective_chat.id, text="مسابقه مورد نظر را انتخواب کنید",reply_markup=races_kb_gen(context.user_data['username'],'finished'))
      context.user_data['state'] = 'r_finished1'
      context.user_data['back_state'] = 'menu'
      context.user_data['back_msg'] = '🔰مسابقات'
      return

    if context.user_data['state'] == 'r_finished1':
      if update.message.text in users[context.user_data['username']]['races']['finished']:
        race_code = users[context.user_data['username']]['races']['finished'][update.message.text]
        context.bot.send_message(chat_id = update.effective_chat.id, text=race_info(race_code, 'finished'))
        context.user_data['state'] = 'r_finished1'
        context.user_data['back_state'] = 'menu'
        context.user_data['back_msg'] = '🔰مسابقات'
        return
      else:
        context.bot.send_message(chat_id = update.effective_chat.id, text="مسابقه پیدا نشد 😕",reply_markup=races_kb_gen(context.user_data['username'],'finished'))
        return

    if context.user_data['state'] == 'menu' and msg == "⏱افزودن زمان" :
      context.bot.send_message(chat_id = update.effective_chat.id, text="مطالعه امروز را وارد می کنید یا دیروز ؟",reply_markup=add_time_kb)
      context.user_data['state'] = 'add_time'
      context.user_data['back_state'] = 'menu'
      context.user_data['back_msg'] = 'menu'
      return

    if context.user_data['state'] == 'add_time' and msg == "🌝امروز" :
      context.bot.send_message(chat_id = update.effective_chat.id, text="زمان مطالعه امروز خود را وارد کنید (ساعت:دقیقه):",reply_markup=back_kb)
      context.user_data['add_time_delta'] = 0
      context.user_data['state'] = 'add_time2'
      context.user_data['back_state'] = 'menu'
      context.user_data['back_msg'] = '⏱افزودن زمان'
      return

    if context.user_data['state'] == 'add_time' and msg == "🌚دیروز" :
      context.bot.send_message(chat_id = update.effective_chat.id, text="زمان مطالعه دیروز خود را وارد کنید (ساعت:دقیقه) :",reply_markup=back_kb)
      context.user_data['add_time_delta'] = -1
      context.user_data['state'] = 'add_time2'
      context.user_data['back_state'] = 'menu'
      context.user_data['back_msg'] = '⏱افزودن زمان'
      return

    if context.user_data['state'] == 'add_time2':
      update_finished_race()
      try:
        if not add_time(context.user_data['username'],update.message.text,update.message.date + dt.timedelta(days=context.user_data['add_time_delta'])):
          context.bot.send_message(chat_id = update.effective_chat.id, text="شما نمیتوانید بیشتر از 24 ساعت در روز اضافه کنید 😕",reply_markup=back_kb)
          return
      except:
        context.bot.send_message(chat_id = update.effective_chat.id, text="زمان را به فرمت روبرو وارد کنید 6:28",reply_markup=back_kb)
        return
      context.bot.send_message(chat_id = update.effective_chat.id, text="⏱زمان اضافه شد ^^",reply_markup=menu_kb)
      update_users_db()
      update_races_db()
      context.user_data['state'] = 'menu'
      context.user_data['back_state'] = '0'
      context.user_data['back_msg'] = 'menu'
      return

    # if context.user_data['state'] == 'menu' and msg == "✂️Remove time" :
    #   context.bot.send_message(chat_id = update.effective_chat.id, text="شماره پیگیری زمان را وارد کنید :",reply_markup=back_kb)
    #   context.user_data['state'] = 'remove_time'
    #   context.user_data['back_state'] = 'menu'
    #   context.user_data['back_msg'] = 'menu'
    #   return

    # if context.user_data['state'] == 'remove_time':
    #   update_finished_race()
    #   try:
    #     remove_time(context.user_data['username'],update.message.text)
    #   except:
    #     context.bot.send_message(chat_id = update.effective_chat.id, text="شماره پیگیری اشتباه است",reply_markup=back_kb)
    #     return
    #   context.bot.send_message(chat_id = update.effective_chat.id, text="✂️زمان حذف شد ^^",reply_markup=menu_kb)
    #   update_users_db()
    #   update_races_db()
    #   context.user_data['state'] = 'menu'
    #   context.user_data['back_state'] = '0'
    #   context.user_data['back_msg'] = 'menu'
    #   return

    if context.user_data['state'] == 'menu' and msg == '📊گزارشات':
      context.bot.send_message(chat_id = update.effective_chat.id, text=report(context.user_data['username']),reply_markup=menu_kb)
      context.user_data['state'] = 'menu'
      context.user_data['back_state'] = '0'
      context.user_data['back_msg'] = 'menu'
      return

    if context.user_data['state'] == 'menu' and msg == "menu":
      context.bot.send_message(chat_id = update.effective_chat.id, text="منو :",reply_markup=menu_kb)
      return

    if context.user_data['state'] == 'admin' and msg == "admin":
      context.bot.send_message(chat_id = update.effective_chat.id, text="پنل ادمین :",reply_markup=admin_kb)
      context.user_data['back_state'] = '0'
      context.user_data['back_msg'] = 'menu'
      return

    if context.user_data['state'] == 'menu' and msg == "🥳حمایت مالی🥳" :
      context.bot.send_message(chat_id = update.effective_chat.id, text="برای حمایت از ربات از لینک زیر استفاده کنید :\n\nzarinp.al/harispy",reply_markup=menu_kb)
      context.user_data['state'] = 'menu'
      context.user_data['back_state'] = '0'
      context.user_data['back_msg'] = 'menu'
      return



  #context.bot.send_message(chat_id = update.effective_chat.id, text="i dont know About '{}'🤷🏼‍♂️".format(update.message.text))

from telegram.ext import CommandHandler, MessageHandler, Filters

# /start
start_handler = CommandHandler('start', start)
dp.add_handler(start_handler)
# /help
help_handler = CommandHandler('help', help)
dp.add_handler(help_handler)
# message
msg_handler = MessageHandler(Filters.text & (~Filters.command),msg)
dp.add_handler(msg_handler)
# admin send message
admin_handler = CommandHandler('admin', admin)
dp.add_handler(admin_handler)

log("Turned On😅")
updater.start_polling()
updater.idle()
updater.stop()
