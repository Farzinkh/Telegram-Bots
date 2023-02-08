import os
import html
import json
import traceback
import requests
import time
import mysql.connector
import logging
import jdatetime
from unidecode import unidecode
import openpyxl as op
from telegram import Update, ForceReply,ParseMode, ReplyKeyboardRemove,InlineKeyboardButton, InlineKeyboardMarkup,ReplyKeyboardMarkup, message
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext,ConversationHandler,CallbackQueryHandler, commandhandler, conversationhandler

TOKEN='1985786479:AAF17e8UzIWdiPuDCzezK2uHX10vmFN-suI'
DEVELOPER_CHAT_ID = 675347977
ADMIN_CHAT_ID = 181912509
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
config={
  #host:"localhost",
  #user:"root",
  'host':"rfabaszadeh.mysql.pythonanywhere-services.com",
  'user':"rfabaszadeh",
  'password':"09033969200Rf",
  #database:"medadrangi"
  'database':'rfabaszadeh$medadrangi'}

### LOAD DATABASE
global mycursor,mydb,isonline,starttime
starttime=time.time()
mydb = mysql.connector.connect(**config)
mycursor = mydb.cursor()
mycursor.execute("SHOW TABLES")
isonline=False
for x in mycursor:
  if x[0]=='customers':
    print('loading database...')
    #sql="ALTER TABLE customers ADD username VARCHAR(150)"
    #sql = "DROP TABLE customers" #delete table
    #mycursor.execute(sql)
    break
else:
    print('creating table...')
    mycursor.execute("CREATE TABLE customers (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255),phonenumber VARCHAR(255), chatid VARCHAR(255),payment VARCHAR(255),username VARCHAR(150))")
    val = ('Empty',)
    mycursor.execute(sql, val)
    mydb.commit()

#mydb.close()

### CREATE FACTORS DIR
if os.path.exists('factors'):
    pass
else:
    os.mkdir('factors')
if os.path.exists('history'):
    pass
else:
    os.mkdir('history')

NAME, PHONENUMBER, LOCATION = range(3)
TOPIC,TEXT,IMAGE=range(3)
FACTOR,SUBSIDY=range(2)
ANNOUNCMENT=range(1)
reply_keyboard = [
    ['Replace', 'Delete'],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
### DATABASE

def save(name,chatid,phonenumber=0):
    global mycursor,mydb
    sql = "INSERT INTO customers (name,phonenumber,chatid,payment) VALUES (%s,%s,%s,%s)"
    adr = (name,phonenumber,chatid,str(0))
    try:
        mycursor.execute(sql, adr)
    except Exception as e:
        mydb = mysql.connector.connect(**config)
        mycursor = mydb.cursor()
        mycursor.execute(sql, adr)
        logger.error(e.args)
    mydb.commit()
    print(mycursor.rowcount, "record inserted.")

def newannouncment(update: Update, context: CallbackContext) -> int:
    global mycursor,mydb
    try:
        os.remove('announcment.txt')
    except:
        pass
    with open('announcment.txt', mode="w", encoding="utf-8") as f:
        f.write(update.message.text)
    update.message.reply_text('announcment updated check out /announcement.')
    return ConversationHandler.END

def sendprivatemessage(update: Update, context: CallbackContext) -> int:
    try:
        test=update.message.text.split(';')
        context.bot.send_message(chat_id=test[0], text=test[1])
        update.message.reply_text('message sent successfully.')
        return ConversationHandler.END
    except:
        update.message.reply_text('message is in wrong format please correct it and send again.')
        return ANNOUNCMENT

def fetchannouncment():
    with open('announcment.txt', mode="r", encoding="utf-8") as f:
        txt=f.read()
    return txt

def load():
    global mycursor,mydb
    try:
        mycursor.execute("SELECT * FROM customers")
    except Exception as e:
        mydb = mysql.connector.connect(**config)
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM customers")
        logger.error(e.args)
    myresult = mycursor.fetchall()
    return myresult

def getinfo(chatid):
    global mycursor,mydb
    sql = "SELECT * FROM customers WHERE chatid = %s"
    adr = (chatid, )
    try:
        mycursor.execute(sql, adr)
    except Exception as e:
        mydb = mysql.connector.connect(**config)
        mycursor = mydb.cursor()
        mycursor.execute(sql, adr)
        logger.error(e.args)
    myresult = mycursor.fetchall()[0]
    result='نام : {}\nشماره تماس : {}\nمبلغ پرداختی : {}'.format(myresult[1],myresult[2],myresult[4])
    return result

def fetchphonenumber(chatid):
    global mycursor,mydb
    sql = "SELECT phonenumber FROM customers WHERE chatid = %s"
    adr = (chatid, )
    try:
        mycursor.execute(sql, adr)
    except Exception as e:
        mydb = mysql.connector.connect(**config)
        mycursor = mydb.cursor()
        mycursor.execute(sql, adr)
        logger.error(e.args)
    myresult = mycursor.fetchall()
    return myresult[0][0]

def getricher():
    #mydb = mysql.connector.connect(**config)
    #mycursor = mydb.cursor()
    sql = "SELECT * FROM customers ORDER BY payment"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for x in myresult:
        print(x)
    #mydb.close()

def delete(chatid):
    #mydb = mysql.connector.connect(**config)
    #mycursor = mydb.cursor()
    sql = "DELETE FROM customers WHERE chatid = %s"
    adr=(chatid,)
    mycursor.execute(sql,adr)
    mydb.commit()
    print(mycursor.rowcount, "record deleted")
    #mydb.close()

def updatepayment(payment,chatid):
    global mycursor,mydb
    sql = "SELECT payment FROM customers WHERE chatid = %s"
    adr = (chatid, )
    try:
        mycursor.execute(sql, adr)
    except Exception as e:
        mydb = mysql.connector.connect(**config)
        mycursor = mydb.cursor()
        mycursor.execute(sql, adr)
        logger.error(e.args)
    myresult = mycursor.fetchall()[0][0]
    payment=str(int(payment)+int(myresult))
    sql = "UPDATE customers SET payment = %s WHERE chatid = %s"
    val = (payment,chatid)
    mycursor.execute(sql, val)
    mydb.commit()
    return payment

def updatephonenumber(phonenumber,chatid):
    global mycursor,mydb
    sql = "UPDATE customers SET phonenumber = %s WHERE chatid = %s"
    val = (phonenumber,chatid)
    try:
        mycursor.execute(sql, val)
    except Exception as e:
        mydb = mysql.connector.connect(**config)
        mycursor = mydb.cursor()
        mycursor.execute(sql, val)
        logger.error(e.args)
    mydb.commit()

def updatename(name,chatid):
    global mycursor,mydb
    sql = "UPDATE customers SET name = %s WHERE chatid = %s"
    val = (name,chatid)
    try:
        mycursor.execute(sql, val)
    except Exception as e:
        mydb = mysql.connector.connect(**config)
        mycursor = mydb.cursor()
        mycursor.execute(sql, val)
        logger.error(e.args)
    mydb.commit()

#### BOT
def getallfactors():
    address='factors'
    for i in os.listdir(address):
        if os.listdir(address+'/'+i)==[]:
            os.rmdir(address+'/'+i)
    adr={}
    for key in os.listdir(address):
        adr[key]=os.listdir(address+'/'+key)
    return adr

def send_announcments(context,bot_message):
    global mycursor,mydb
    try:
        mycursor.execute("SELECT chatid FROM customers")
    except Exception as e:
        mydb = mysql.connector.connect(**config)
        mycursor = mydb.cursor()
        mycursor.execute("SELECT chatid FROM customers")
        logger.error(e.args)
    myresult = mycursor.fetchall()
    for key in myresult:
        context.bot.send_message(chat_id=key[0], text=bot_message)
        time.sleep(1)

def start(update: Update, context: CallbackContext) -> int:
    user = update.effective_user.name
    try:
        getinfo(update.message.chat_id)
        update.message.reply_text('سلام {} خوش آمدید برای مطالعه اطلاعیه /announcement و برای دریافت اطلاعات بیشتر /help را بزنید.'.format(user))
        return ConversationHandler.END
    except:
        update.message.reply_text(
            ' سلام {} به بخش ثبت نام خوش آمدید'
            'برای لغو ثبت نام خود /cancel  را وارد کنید'
            'شما را به چه نام بشناسیم؟' .format(user),
            reply_markup=ForceReply(selective=True),
        )
    return NAME

def getaccunts():
    wb=op.Workbook()
    wb.create_sheet('Report')
    std=wb.get_sheet_by_name('Sheet')
    wb.remove_sheet(std)
    sh=wb['Report']
    sh.append(('row','name','phonenumber','chat_id','subsidy','username'))
    for item in load():
        sh.append(item)
    wb.save("accunts.xlsx")

def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    #query.edit_message_text(text=f"User name: {query.from_user.id}")
    query.edit_message_text(text=f"Selected option: {query.data}")
    if query.from_user.id==DEVELOPER_CHAT_ID or query.from_user.id==ADMIN_CHAT_ID:
        if query.data=='accunts':
            getaccunts()
            context.bot.send_document(chat_id=query.from_user.id, document=open("accunts.xlsx", 'rb'))
        elif query.data=='addannonsment':
            query.edit_message_text(text='Enter /newannouncment to write an announcment and then publish it in office.')
        elif query.data=="private":
            query.edit_message_text(text='Enter /private to start procedure.')
        elif query.data=='annonsment':
            send_announcments(context,fetchannouncment())
        elif query.data=='delete':
            for ID in os.listdir('factors'):
                for factor in os.listdir('factors/'+ID):
                    os.remove('factors/'+ID+'/'+factor)
            query.edit_message_text(text="all factors deleted.")
        elif query.data=='history':
            query.edit_message_text(text='Enter /addtohistory to start procedure.')
        elif query.data=='factors':
            adress=getallfactors()
            for data in adress.items():
                info=getinfo(data[0])
                for factor in data[1]:
                    context.bot.send_document(chat_id=query.from_user.id,caption=info, document=open('factors/'+data[0]+'/'+factor, 'rb'))
        else:
            for item in os.listdir('history/'+query.data):
                if item[-3:]=='jpg':
                    context.bot.send_photo(chat_id=query.from_user.id,photo=open('history/'+query.data+'/'+item, 'rb'))
                else:
                    with open('history/'+query.data+'/readme.txt', mode="r", encoding="utf-8") as f:
                        txt=f.read()
                    query.edit_message_text(text=txt)
    else:
        for item in os.listdir('history/'+query.data):
            if item[-3:]=='jpg':
                context.bot.send_photo(chat_id=query.from_user.id,photo=open('history/'+query.data+'/'+item, 'rb'))
            else:
                with open('history/'+query.data+'/readme.txt', mode="r", encoding="utf-8") as f:
                    txt=f.read()
                query.edit_message_text(text=txt)


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    if update.message.chat_id==DEVELOPER_CHAT_ID or update.message.chat_id==ADMIN_CHAT_ID:
        """Sends a message with three inline buttons attached."""
        keyboard = [
            [
                InlineKeyboardButton("Accunts", callback_data='accunts'),
                InlineKeyboardButton("Factors", callback_data='factors'),
            ],
            [InlineKeyboardButton("Delete factors", callback_data='delete')],
            [InlineKeyboardButton("History management", callback_data='history')],
            [InlineKeyboardButton("Update annonsment", callback_data='addannonsment')],
            [InlineKeyboardButton("Publish an annonsment", callback_data='annonsment')],
            [InlineKeyboardButton("Send private message to a user", callback_data='private')],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text('Welcome to office Please choose what to do:', reply_markup=reply_markup)
    else:
        update.message.reply_text('در این بات شما اطلاعیه های به روز را با دستور /announcement می توانیید دنبال کنید یا برای کمک از بخش /donate  اقدام کنید.')
def show_info(update: Update, context: CallbackContext) -> None:
    try:
        update.message.reply_text(getinfo(update.message.chat_id))
    except:
        #update.message.reply_text('{} you have to signup first simply by \n/start your id is {}.'.format(update.message.from_user.first_name,update.effective_chat.id))
        update.message.reply_text('لطفا ابتدا با دستور زیر  /n/startبت نام کنید')

def readannouncment(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(fetchannouncment())

def settings(update: Update, context: CallbackContext) -> int:
    user = update.effective_user.name
    update.message.reply_text(
            'سلام {} به بخش تنظیمات خوش آمدید در اینجا شما می توانید اسم و شماره تماس خود را عوض کنید '
            'برای پایان دادن به پروسه /cancel را وارد کنید .\n\n'
            'شما را به چه نام بشناسیم؟'.format(user),
            reply_markup=ForceReply(selective=True),
        )
    return NAME


def donate(update: Update, context: CallbackContext) -> int:
    try:
        getinfo(update.message.chat_id)
    except:
        update.message.reply_text('عزیز لطفا ابتدا ثبت/start نام کرده و سپس وارد این بخش شوید{}'.format(update.message.from_user.first_name))
        return ConversationHandler.END
    update.message.reply_text('متاسفانه در حال حاضر امکان پرداخت مستقیم در بات وجود ندارد لزا پرداخت خود را به روش کارت به کارت به\nشماره کارت :3053 7272 3374 6104\nبه نام : آقای عارف عباسزاده \nواریز نمایید و فاکتور و مبلغ پرداختی به ریال را به ترتیب برای ما ارسال کنید')
    update.message.reply_text('لطفا از فاکتور پرداخت خود عکس گرفته و آن را ارسال کنید و یا برای لغو عملیات /cancel را وارد کنید',reply_markup=ForceReply(selective=True))
    return FACTOR

def factor(update: Update, context: CallbackContext) -> int:
    photo_file = update.message.photo[-1].get_file()
    try:
        photo_file.download('factors/'+str(update.message.chat_id)+'/'+photo_file.file_id+'.jpg')
    except:
        os.mkdir('factors/'+str(update.message.chat_id))
        photo_file.download('factors/'+str(update.message.chat_id)+'/'+photo_file.file_id+'.jpg')
    update.message.reply_text('لطفا مبلغ را به ریال وارد کنید ',reply_markup=ForceReply(selective=True))
    return SUBSIDY

def subsidy(update: Update, context: CallbackContext) -> int:
    subs=update.message.text
    try:
        if int(unidecode(subs))==0:
            update.message.reply_text('مبلغ پرداختی نمی تواند صفر باشد لطفا اصلاح کنید !',reply_markup=ForceReply(selective=True))
            return SUBSIDY
        total=updatepayment(unidecode(subs),update.message.chat_id)
    except:
        update.message.reply_text('لطفا مبلغ را به ریال و به صورت عددی وارد کنید !',reply_markup=ForceReply(selective=True))
        return SUBSIDY
    update.message.reply_text('شما مبلغ {} ریال به خیریه واریز کردید جمع واریز های شما تا این لحظه {} ریال می باشد'.format(unidecode(subs),total))
    try:
        context.bot.send_message(chat_id=ADMIN_CHAT_ID,text=update.effective_user.name+' donated '+unidecode(subs)+" Rial")
        #context.bot.send_message(chat_id=DEVELOPER_CHAT_ID,text=update.effective_user.name+' donated '+unidecode(subs)+" Rial")
    except:
        global mycursor,mydb
        sql = "SELECT * FROM customers WHERE chatid = %s"
        adr = (update.message.chat_id, )
        try:
            mycursor.execute(sql, adr)
        except Exception as e:
            mydb = mysql.connector.connect(**config)
            mycursor = mydb.cursor()
            mycursor.execute(sql, adr)
            logger.error(e.args)
        name= mycursor.fetchall()[0][0]
        context.bot.send_message(chat_id=ADMIN_CHAT_ID,text=name+' donated '+unidecode(subs)+" Rial")
    finally:
        return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.debug("User %s canceled the signup.", user.first_name)
    update.message.reply_text(
        'عملیات پایان یافت', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def setannouncment(update: Update, context: CallbackContext) -> int:
    if update.message.chat_id==DEVELOPER_CHAT_ID or update.message.chat_id == ADMIN_CHAT_ID:
        update.message.reply_text('Enter announcment text now or send /cancel to stop upgradeing.',reply_markup=ForceReply(selective=True))
        return ANNOUNCMENT
    else:
        update.message.reply_text('Sorry you dont have permission for this.')
        return ConversationHandler.END

def privatemessagehandler(update: Update, context: CallbackContext) ->int:
    if update.message.chat_id==DEVELOPER_CHAT_ID or update.message.chat_id == ADMIN_CHAT_ID:
        update.message.reply_text('Enter chat_id and message seprated by ; or send /cancel to stop messageing.',reply_markup=ForceReply(selective=True))
        return ANNOUNCMENT
    else:
        update.message.reply_text('Sorry you dont have permission for this.')
        return ConversationHandler.END

def editname(update: Update, context: CallbackContext) -> int:
    updatename(update.message.text,update.message.chat_id)
    update.message.reply_text('لطفا شماره تماس خود را وارد کنید',reply_markup=ForceReply(selective=True))
    return PHONENUMBER

def getname(update: Update, context: CallbackContext) -> int:
    save(update.message.text,update.message.chat_id)
    update.message.reply_text('شماره تماس خود را وارد کنید ',reply_markup=ForceReply(selective=True))
    return PHONENUMBER

def getphonenumber(update: Update, context: CallbackContext) -> int:
    phonenumber=update.message.text
    updatephonenumber(unidecode(phonenumber),update.message.chat_id)
    update.message.reply_text('ثبت نام شما تکمیل شد\nاطلاعات حساب شما :\n{}'.format(getinfo(update.message.chat_id)))
    try:
        os.mkdir('factors/'+str(update.message.chat_id))
    except:
        pass
    return ConversationHandler.END

def is_time_between(check_time=None):
    from datetime import datetime, time
    begin_time,end_time=time(16,30),time(20,30)
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.now().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time


def send_message_job(context):
    global starttime
    t=time.time()-starttime
    now=jdatetime.datetime.now()
    f=time.time()+(3600*3.5)
    if is_time_between():
        print('{}{}'.format(now.strftime("%Y %b %a %d "),time.strftime('%H:%M:%S', time.gmtime(f))))
        context.bot.send_message(chat_id=DEVELOPER_CHAT_ID,text='Bot is alive for {} hours until {}{}.'.format(round(t/3600),now.strftime("%Y %b %a %d "),time.strftime('%H:%M:%S', time.gmtime(f))))
        context.bot.send_message(chat_id=ADMIN_CHAT_ID,text='Bot is alive for {} hours until {}{}.'.format(round(t/3600),now.strftime("%Y %b %a %d "),time.strftime('%H:%M:%S', time.gmtime(f))))

def error_handler(update: object, context: CallbackContext) -> None:
    global isonline
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    try:
        if context.error.message=='Conflict: terminated by other getUpdates request; make sure that only one bot instance is running' :
            if isonline:
                pass
            else:
                context.bot.send_message(chat_id=DEVELOPER_CHAT_ID, text='Bot is online')
                isonline=True
        else:
            logger.error(msg="Exception while handling an update:", exc_info=context.error)
            # traceback.format_exception returns the usual python message about an exception, but as a
            # list of strings rather than a single string, so we have to join them together.
            tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
            tb_string = ''.join(tb_list)

            # Build the message with some markup and additional information about what happened.
            # You might need to add some logic to deal with messages longer than the 4096 character limit.
            update_str = update.to_dict() if isinstance(update, Update) else str(update)
            message = (
                f'An exception was raised while handling an update\n'
                f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
                '</pre>\n\n'
                f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
                f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
                f'<pre>{html.escape(tb_string)}</pre>'
            )

            # Finally, send the message
            context.bot.send_message(chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML)
    except:
            logger.error(msg="Exception while handling an update:", exc_info=context.error)
            # traceback.format_exception returns the usual python message about an exception, but as a
            # list of strings rather than a single string, so we have to join them together.
            tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
            tb_string = ''.join(tb_list)

            # Build the message with some markup and additional information about what happened.
            # You might need to add some logic to deal with messages longer than the 4096 character limit.
            update_str = update.to_dict() if isinstance(update, Update) else str(update)
            try:
                message = (
                    f'An exception was raised while handling an update\n'
                    f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
                    '</pre>\n\n'
                    f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
                    f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
                    f'<pre>{html.escape(tb_string)}</pre>'
                    f'<pre>error happend for user= {html.escape(update.effective_user.name)}</pre>\n\n'
                )

                # Finally, send the message
                context.bot.send_message(chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML)
            except:
                message = (
                    f'An exception was raised while handling an update\n'
                    f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
                    '</pre>\n\n'
                    f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
                    f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
                    f'<pre>{html.escape(tb_string)}</pre>'
                )

                # Finally, send the message
                context.bot.send_message(chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML)
### HISTORY
def addtohistory(update: Update, context: CallbackContext) -> int:
    if update.message.chat_id==DEVELOPER_CHAT_ID or update.message.chat_id==ADMIN_CHAT_ID:
        update.message.reply_text('Enter a topic for this event and you can cancel this procedure anytime by /cancel.',reply_markup=ForceReply(selective=True))
        return TOPIC
    else:
        update.message.reply_text('Sorry you dont have permission for this.')
        return ConversationHandler.END


def Topic(update: Update, context: CallbackContext) -> int:
    global historytopic,temp
    if os.path.exists('history/'+update.message.text) or update.message.text=="Delete" or update.message.text=="Replace":
        if update.message.text=='Delete':
            for item in os.listdir('history/'+temp):
                os.remove('history/'+temp+'/'+item)
            os.rmdir('history/'+temp)
            update.message.reply_text('"{}" deleted.'.format(temp))
            return ConversationHandler.END
        elif update.message.text=='Replace':
            for item in os.listdir('history/'+temp):
                os.remove('history/'+temp+'/'+item)
            historytopic=temp
            update.message.reply_text('Enter text for this event.',reply_markup=ForceReply(selective=True))
            return TEXT
        else:
            temp=update.message.text
            update.message.reply_text('"{}" have been used before what do you what to do with it? or just enter another topic.'.format(update.message.text),reply_markup=markup)
        return TOPIC
    else:
        os.mkdir('history/'+update.message.text)
        historytopic=update.message.text
        update.message.reply_text('Enter text for this event.',reply_markup=ForceReply(selective=True))
        return TEXT

def Text(update: Update, context: CallbackContext) -> int:
    global historytopic
    text=update.message.text
    with open('history/'+historytopic+'/'+'readme.txt', 'w',encoding='utf-8') as f:
        f.write(text)
    update.message.reply_text('Send an image for this event or you can skip this by /skip.',reply_markup=ForceReply(selective=True))
    return IMAGE

def Image(update: Update, context: CallbackContext) -> int:
    global historytopic
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('history/'+historytopic+'/'+photo_file.file_id+'.jpg')
    update.message.reply_text('Done now check out /history.')
    return ConversationHandler.END

def skip_Image(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Done now check out /history.')
    return ConversationHandler.END

def show_history(update: Update, context: CallbackContext) -> None:
    keyboard = []
    for event in os.listdir('history'):
        keyboard.append([InlineKeyboardButton(event, callback_data=event)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('به آرشیو ما خوش آمدید لطفا رخداد مورد نظر خود را انتخاب کنید.', reply_markup=reply_markup)

def redirect(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('درخواست نامعتبر است لطفا از menu عمل مورد نظر را انتخاب کنید.')

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)
    job_queue = updater.job_queue
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("myinfo", show_info))
    dispatcher.add_handler(CommandHandler("history",show_history))
    dispatcher.add_handler(CommandHandler("announcement", readannouncment))
    dispatcher.add_handler(CommandHandler("help", help_command,))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    # on non command i.e message - echo the message on Telegram
    #dispatcher.add_handler(InlineQueryHandler(inlinequery))
    #dispatcher.add_handler(MessageHandler(Filters.text, echo))
    Announcment=ConversationHandler(
        entry_points=[CommandHandler("newannouncment",setannouncment)],
        states={
           ANNOUNCMENT : [MessageHandler(Filters.text & ~Filters.command, newannouncment)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(Announcment)
    privatemessage=ConversationHandler(
        entry_points=[CommandHandler("private",privatemessagehandler)],
        states={
           ANNOUNCMENT : [MessageHandler(Filters.text & ~Filters.command, sendprivatemessage)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(privatemessage)
    History=ConversationHandler(
        entry_points=[CommandHandler('addtohistory', addtohistory)],
        states={
            TOPIC: [MessageHandler(Filters.text & ~Filters.command, Topic)],
            TEXT: [MessageHandler(Filters.text & ~Filters.command, Text)],
            IMAGE: [
                MessageHandler(Filters.photo , Image),
                CommandHandler('skip', skip_Image),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(History)
    Settings=ConversationHandler(
        entry_points=[CommandHandler('settings', settings)],
        states={
            NAME: [MessageHandler(Filters.text & ~Filters.command, editname)],
            PHONENUMBER: [
                MessageHandler(Filters.text & ~Filters.command, getphonenumber),
                #CommandHandler('skip', skip_phonenumber),
            ],
            #LOCATION: [
            #    MessageHandler(Filters.location, location),
            #    CommandHandler('skip', skip_location),
            #],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(Settings)
    signup_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(Filters.text & ~Filters.command, getname)],
            PHONENUMBER: [
                MessageHandler(Filters.text & ~Filters.command, getphonenumber),
                #CommandHandler('skip', skip_phonenumber),
            ],
            #LOCATION: [
            #    MessageHandler(Filters.location, location),
            #    CommandHandler('skip', skip_location),
            #],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(signup_handler)
    donate_handler = ConversationHandler(
        entry_points=[CommandHandler('donate', donate)],
        states={
            FACTOR: [MessageHandler(Filters.photo, factor)],
            SUBSIDY: [MessageHandler(Filters.text & ~Filters.command, subsidy)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(donate_handler)
    dispatcher.add_error_handler(error_handler)
    dispatcher.add_handler(MessageHandler(Filters.text or Filters.document.category("image") & ~Filters.command, redirect))

    # Start the Bot
    updater.start_polling()
    updater.dispatcher.bot.sendMessage(chat_id=DEVELOPER_CHAT_ID, text='Bot turns on!')
    job_queue.run_repeating(send_message_job,interval=3600.0,first=0.0)
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
    updater.dispatcher.bot.sendMessage(chat_id=DEVELOPER_CHAT_ID, text='Bot turns off!')


if __name__ == '__main__':
    main()