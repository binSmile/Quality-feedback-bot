# @feedbackbot

"""
Attention! You must put api-key into config.py
"""
from config import token
adminslist = [8888888]  # list of telegrams admins id


import os
import shutil
from datetime import datetime
import telebot
from telebot import types
import sqlite3
import zipfile

print('bot starts')

with open('statexport.log', 'a') as logger:
    logger.write('%s bot run \n' % (datetime.now().isoformat()))

conn = sqlite3.connect('database.db', check_same_thread=False,
                       isolation_level=None,
                       detect_types=sqlite3.PARSE_COLNAMES
                       )
cursor = conn.cursor()


def db_table_val(user_id: int, user_name: str, user_surname: str, username: str, Goodway: str, CleanShowroom: str,
                 WaitingQueueTerminal: str, WaitingQueueDispatcher: str, CleanWaitingQueue: str, datetime: str,
                 ShowRoomPhoto: str, WaitingQueuePhoto: str):
    cursor.execute(
        'INSERT INTO answers (user_id,user_name, user_surname, username, Goodway, CleanShowroom,  WaitingQueueTerminal, \
         WaitingQueueDispatcher,  CleanWaitingQueue, datetime, ShowRoomPhoto, WaitingQueuePhoto) VALUES \
          (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (user_id, user_name, user_surname, username, Goodway, CleanShowroom, WaitingQueueTerminal,
         WaitingQueueDispatcher, CleanWaitingQueue, datetime, ShowRoomPhoto, WaitingQueuePhoto))
    conn.commit()




def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


def getFolderSize(p):
    from functools import partial
    prepend = partial(os.path.join, p)
    return sum([(os.path.getsize(f) if os.path.isfile(f) else getFolderSize(f)) for f in
                map(prepend, os.listdir(p))])


def check_permission(cursor, uid):
    c = cursor
    query = c.execute("select admin_id FROM admins WHERE admin_id = %s;" % uid)
    a = cursor.fetchall()
    return bool(a)


def export(cursor):
    from xlsxwriter.workbook import Workbook
    workbook = Workbook('answers.xlsx')
    worksheet = workbook.add_worksheet()
    c = cursor
    mysel = c.execute("SELECT * FROM answers")
    head = ['N', 'user_name', 'user_surname', 'username', 'user_id', 'Goodway', 'CleanShowroom', 'WaitingQueueTerminal',
            'WaitingQueueDispatcher', 'CleanWaitingQueue', '??????????', 'ShowRoomPhoto', 'WaitingQueuePhoto']
    worksheet.write_row(0, 0, head)
    head = ['N', 'user_name', 'user_surname', 'username', 'user_id', '???????????????? ????????', '?????????????? ?? ?????????????????????? ????????',
            '?????????????? ?? ????????????????', '?????????????? ?? ????????????????????', '?????????????? ?? ???????? ???????????????? ????????????????', '??????????', '???????? ????????????',
            '???????? ??????????????']
    worksheet.write_row(1, 0, head)

    for i, row in enumerate(mysel):
        for j, value in enumerate(row):
            worksheet.write(i + 2, j, value)
    workbook.close()

    zipf = zipfile.ZipFile('photos.zip', 'w', zipfile.ZIP_DEFLATED)
    zipdir('photos/', zipf)
    zipf.close()


states = {}
inventories = {}
notes = {}
wait = {}
bot = telebot.TeleBot(token)
Flag = {}


@bot.message_handler(commands=["start", "export", "clean", "stat", "addadmin", "deladmin","statext"])
def start_game(message):
    user = message.chat.id
    states[user] = 0
    if 'start' in message.text:
        inventories[user] = []
        bot.send_message(user, "???????????? ????????! ?? ??? feedbackbot ?? ?? ??????, ?????? ???? ???????????? ???????????? ?????? ?????????? ????")

        if not notes.get(user):
            notes[user] = {}
        notes[user]['us_name'] = message.from_user.first_name
        notes[user]['us_sname'] = message.from_user.last_name
        notes[user]['us_uname'] = message.from_user.username

        process_state(user, states[user], inventories[user])
    else:
        if not check_permission(cursor, user):
            with open('statexport.log', 'a') as logger:
                logger.write(
                    '%s %s %s %s BLOCK \n' % (datetime.now().isoformat(), user, message.from_user.username, message.text))
        else:
            with open('statexport.log', 'a') as logger:
                logger.write(
                    '%s %s %s %s \n' % (datetime.now().isoformat(), user, message.from_user.username, message.text))
            if 'export' in message.text:
                # print(user,message.from_user.username)
                export(cursor)
                bot.send_message(user, "?????? ?????? ???????? ??????????????!")
                with  open('answers.xlsx', 'rb') as statdata:
                    bot.send_document(message.chat.id, statdata)
                with  open('photos.zip', 'rb') as statdata:
                    bot.send_document(message.chat.id, statdata)
                os.remove('photos.zip')
                os.remove('answers.xlsx')

            elif 'stat' in message.text:
                cursor.execute('SELECT Count(*) FROM answers')
                conn.commit()
                DBlineCounts = cursor.fetchall()[0][0]

                DBsize = os.stat('database.db').st_size / 1e6
                Photosize = getFolderSize('photos') / 1e6

                bot.send_message(user,
                                 """???????????????????? \n 
                ?? ???????? ????????????????????  %s ????????????(????)\n
                ???????? ??????????: %s ???? \n
                ?????????????????? ??????????: %s ????""" % (DBlineCounts, DBsize, Photosize))

                if 'statext' in message.text:

                    cursor.execute('SELECT * FROM admins')
                    admins = cursor.fetchall()
                    bot.send_message(user,'???????????? ??????????????: %s' % str(admins))

                    with  open('statexport.log', 'rb') as statdata:
                        bot.send_document(message.chat.id, statdata)



            elif 'clean' in message.text:
                try:

                    zipf = zipfile.ZipFile('photos_bak.zip', 'w', zipfile.ZIP_DEFLATED)
                    zipdir('Photos/', zipf)
                    zipf.close()

                    zipf = zipfile.ZipFile('database_bak.db.zip', 'w', zipfile.ZIP_DEFLATED)
                    zipdir('database.db', zipf)
                    zipf.close()

                    shutil.rmtree('Photos')
                    os.mkdir('photos')
                except Exception as e:
                    bot.send_message(user, "????-???? ?????????? ???? ??????.")
                    bot.reply_to(message, e)

                cursor.execute('delete from answers')
                conn.commit()
                bot.send_message(user, "?????? ??????????")

            elif 'addadmin' in message.text:
                nuid = message.text.split(' ')[-1]
                cursor.execute(
                    'INSERT INTO admins (admin_id) VALUES (%s)' % nuid)
                conn.commit()
                bot.send_message(user, "???????????????????????? %s ???????????????? ?? ???????????? ??????????????" % nuid)
            elif 'deladmin' in message.text:
                nuid = message.text.split(' ')[-1]
                cursor.execute('DELETE FROM admins WHERE admin_id = %s;' % nuid)
                conn.commit()
                bot.send_message(user, "???????????????????????? %s ???????????? ???? ???????????? ??????????????"  % nuid)



@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    user = message.chat.id
    st = states.get(user, 0)
    if st >= 4:  # ???????????????? ?????????????????? ?????? ???????????????? ?? ==10 ???? 11
        # if True:
        try:
            phList = []
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            src = '' + file_info.file_path;
            phList += [src]
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)


        except Exception as e:
            bot.send_message(user, "?????????????? ???? ????????. ???? ??????-???? ?????????? ???? ??????. ?? ???? ???????? ?????????????????? ????????")
            bot.reply_to(message, e)
            phList = e
        wait[user] = False
        if st in [4, 5]:
            print(st)
            states[user] = 5
            if not notes[user].get('ShowRoomPhoto'):
                notes[user]['ShowRoomPhoto'] = []
            notes[user]['ShowRoomPhoto'] += phList
        elif st in [10, 11]:
            states[user] = 11
            if not notes[user].get('WaitingQueuePhoto'):
                notes[user]['WaitingQueuePhoto'] = []
            notes[user]['WaitingQueuePhoto'] += phList

        if not Flag.get(user):
            Flag[user] = True
            bot.reply_to(message, "?????????????? ???? ????????")
            process_state(user, states[user], inventories[user])


@bot.message_handler(content_types=['text'])
def thanking(message):
    user = message.chat.id
    st = states.get(user, 0)
    if not notes.get(user):
        notes[user] = {}

    if st == 2:  # Goodway
        notes[user]['Goodway'] = message.text
        bot.send_message(user, "??????????????")
        wait[user] = False
        states[user] = 3
        process_state(user, states[user], inventories[user])
    elif st == 4:
        #     notes[user]['CleanShowroom'] = message.text  ## ???????????????? ???????? ?????? ???????????????????? ?????? ?????????????
        #     bot.send_message(user, "?????????????? ???? ????????")
        wait[user] = False
        states[user] = 5
        process_state(user, states[user], inventories[user])

    elif st == 6:
        notes[user]['WaitingQueueTerminal'] = message.text
        bot.send_message(user, "??????????????!")
        wait[user] = False
        states[user] = 7
        process_state(user, states[user], inventories[user])

    elif st == 8:
        notes[user]['WaitingQueueDispatcher'] = message.text
        bot.send_message(user, "??????????????!")
        wait[user] = False
        states[user] = 9
        process_state(user, states[user], inventories[user])

    elif st == 10:
        notes[user]['CleanWaitingQueue'] = message.text  ## ???????????????? ???????? ?????? ???????????????????? ?????? ?????????????
        bot.send_message(user, "??????????????")
        wait[user] = False
        states[user] = 11
        process_state(user, states[user], inventories[user])

    # else:
    #     bot.send_message(user, "?????????????? ????????????, ????????????????????")


@bot.callback_query_handler(func=lambda call: True)
def user_answer(call):
    user = call.message.chat.id
    if not notes.get(user):
        notes[user] = {}
    process_answer(user, call.data)


def process_state(user, state, inventory):
    kb = types.InlineKeyboardMarkup()

    # bot.send_photo(user, pictures[state])

    if state == 0:
        msg = "?????? ???????? ??????????????, ???????? ?????????? ?????????? ?? ?????? ???????????? ?????? ?????????????????? ?????????????"
        kb.add(types.InlineKeyboardButton(text="????", callback_data="GoodWayY"))
        kb.add(types.InlineKeyboardButton(text="??????", callback_data="GoodWayN"))
        bot.send_message(user, msg, reply_markup=kb)

    elif state == 3:
        msg = "???????? ????????????. \n ?? ?????????????????????? ???????? ??????????, ?????? ???????????? ?? ?????????"
        kb.add(types.InlineKeyboardButton(text="??????????!", callback_data="CleanShowroom0"))
        kb.add(types.InlineKeyboardButton(text="???????? ????????", callback_data="CleanShowroom1"))
        kb.add(types.InlineKeyboardButton(text="???????? ??????????", callback_data="CleanShowroom2"))
        bot.send_message(user, msg, reply_markup=kb)

    elif state == 5:

        msg = "?????????? ?? ?????????????? ?? ???????????????? ???????????????? ?????????? 1 ?????????????"
        kb.add(types.InlineKeyboardButton(text="????, ?????????? ????????????", callback_data="WaitingQueueTerminal0"))
        kb.add(types.InlineKeyboardButton(text="??????, ?????????? ????????????", callback_data="WaitingQueueTerminal1"))
        bot.send_photo(user, caption=msg, photo=open('terminal.jpg', 'rb'), reply_markup=kb)
        # bot.send_message(user, msg, reply_markup=kb)

    elif state == 7:
        msg = "?????????? ?? ?????????????? ?? ???????????????????? ???????????????? ?????????? 5 ??????????? "
        kb.add(types.InlineKeyboardButton(text="????, ????????????", callback_data="WaitingQueueDispatcherY"))
        kb.add(types.InlineKeyboardButton(text="??????, ??????????", callback_data="WaitingQueueDispatcherN"))
        bot.send_photo(user, caption=msg, photo=open('operator.jpg', 'rb'), reply_markup=kb)
        # bot.send_message(user, msg, reply_markup=kb)

    elif state == 9:
        msg = "?? ???????? ???????????????? ???????????????? ???????? ???????????"
        kb.add(types.InlineKeyboardButton(text="????", callback_data="CleanWaitingQueueY"))
        kb.add(types.InlineKeyboardButton(text="??????", callback_data="CleanWaitingQueueN"))
        bot.send_message(user, msg, reply_markup=kb)

    elif state == 11:

        bot.send_message(user,
                         "???? ???? ???????????? ?????????? ???? ??????????! ???? \n ?????? ????????????! ?????????????????????? ?????? ?? ???????????????? ?????????????????????? ??????????!")
        # bot.send_message(user, str(notes))
        finish(user, notes[user])
        states[user] = 0


def finish(user, result):
    r = result
    db_table_val(user,
                 r.get('us_name'),
                 r.get('us_sname'),
                 r.get('us_uname'),
                 r.get('Goodway'),
                 r.get('CleanShowroom'),
                 r.get('WaitingQueueTerminal'),
                 r.get('WaitingQueueDispatcher'),
                 r.get('CleanWaitingQueue'),
                 datetime.now().isoformat(),
                 str(r.get('ShowRoomPhoto')),
                 str(r.get('WaitingQueuePhoto')))


def process_answer(user, answer):
    if states.get(user, 0) == 0:
        if "GoodWay" in answer:
            if answer == 'GoodWayY':
                bot.send_message(user, "??????????????!")
                states[user] = 3
                notes[user]['Goodway'] = '????'

            elif answer == 'GoodWayN':
                bot.send_message(user, "???????????????? ?????????????????? ?? ?????????? ??????????, ????????????????????.")
                states[user] = 2
                wait[user] = True

    elif states[user] == 3:
        if answer == 'CleanShowroom0':
            bot.send_message(user, "????????????????????????!")
            states[user] = 5
            notes[user]['CleanShowroom'] = '??????????'
        else:
            if answer == 'CleanShowroom1':
                notes[user]['CleanShowroom'] = '????????'
            elif answer == 'CleanShowroom2':
                notes[user]['CleanShowroom'] = '??????????'

            bot.send_message(user, "??????????????????????????????, ????????????????????, ??????????/???????? ?? ???????????????? ??????, ?? ?? ?????? ????????????????!")
            states[user] = 4
            wait[user] = True
            Flag[user] = False

    elif states[user] == 5:
        if answer == 'WaitingQueueTerminal0':
            bot.send_message(user, "????????")
            states[user] = 7
            notes[user]['WaitingQueueTerminal'] = '1'


        else:
            bot.send_message(user, "?????????????? ?????????????????")
            states[user] = 6
            wait[user] = True

    elif states[user] == 7:
        if answer == 'WaitingQueueDispatcherY':
            bot.send_message(user, "????????")
            states[user] = 9
            notes[user]['WaitingQueueDispatcher'] = '?????????? 5'

        else:
            bot.send_message(user, "?????????????? ?????????????????")
            states[user] = 8
            wait[user] = True

    elif states[user] == 9:
        if answer == 'CleanWaitingQueueY':
            # bot.send_message(user, "????????")
            states[user] = 11
            notes[user]['CleanWaitingQueue'] = '??????????'
        else:
            bot.send_message(user, "??????????????????????????????, ????????????????????, ??????????/???????? ?? ???????????????? ??????, ?? ?? ?????? ????????????????!")
            states[user] = 10
            wait[user] = True
            Flag[user] = False

    if not wait.get(user, False):
        process_state(user, states[user], inventories[user])


if __name__ == '__main__':
    # bot.infinity_polling()
    bot.polling(none_stop=True)
