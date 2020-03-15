import telebot
import ast
import logging
import copy
import os
import time
import sqlite3
from sqlite3 import Error
from flask import Flask, request
from telegram.ext import Updater
from telebot import types,util
from random import seed,randint
from openpyxl import Workbook
workbook = Workbook()
sheet = workbook.active #for working on xlsx file
#telebot.logger.setLevel(logging.DEBUG) #for debugging telegram api
API_TOKEN = os.getenv("API_TOKEN")#this value will set localy on your host and will obtain from botfather
WEBHOOK_LISTEN = '0.0.0.0' #default
server = Flask(__name__)
def sql_connection():
	try:
		con=sqlite3.connect('mydatabase.db')
		print("connection is established ,database created")
		return con
	except Error:
		print(Error)
def sql_table():
	global db
	courobj=db.cursor()
	courobj.execute("CREATE TABLE merrymaker(username text,firstname text,lastname text,phonenumber real,point real,state text)")
	db.commit()
def sql_insert(data):
	global db
	courobj=db.cursor()
	courobj.execute("""INSERT INTO merrymaker(username,firstname,lastname,phonenumber,point,state) VALUES(?,?,?,?,?,?)""",data)
	db.commit()
def sql_update(key,data,username):
	global db
	courobj=db.cursor()
	courobj.execute("UPDATE merrymaker SET {}={} where username={}".format(key,data,username))
	db.commit()
global db
db=sql_connection()
sql_table()

global answerlist,questionsdoc,questionlist
lines=open('questions.txt','r').readlines()
count,countans,answerlist,questionsdoc,questionlist=0,5,[],{},[]
while countans<len(lines):
	answerlist.append(int(lines[countans].rstrip("\n")))
	countans+=6
while count<len(lines):
	questionlist.append(lines[count].rstrip("\n"))
	questionsdoc[lines[count].rstrip("\n")]=[lines[count+1].rstrip("\n"),lines[count+2].rstrip("\n"),lines[count+3].rstrip("\n"),lines[count+4].rstrip("\n")]
	count+=6
seed(1)
crossIcon = u"\u274C"
flag= u"\u2690"
bot = telebot.TeleBot(API_TOKEN)
#bot=telebot.AsyncTeleBot(API_TOKEN) #if you want your bot respond asynchronus
markup = types.ReplyKeyboardMarkup()
itembtn1 = types.KeyboardButton('My point')
itembtn2 = types.KeyboardButton('Fight on')
itembtn3 = types.KeyboardButton('billboard')
itembtn4 = types.KeyboardButton('home')
markup.row(itembtn1)
markup.row(itembtn2)
markup.row(itembtn3)
markup.add(itembtn4)
mksighup = types.ForceReply(selective=False)
global first,second,third,champions
sighuplist,champions,first,second,third={},['','',''],0,0,0
def makestringlist(a,b,c,d):
	stringdata = {u"\u2160":a , u"\u2161": b, u"\u2162": c,u"\u2163":d}
	return stringdata

def makeKeyboard(stringList):
    markup2 = types.InlineKeyboardMarkup()
    for key, value in stringList.items():
        if len(value)>20:
          value=value[0:20]
        markup2.add(types.InlineKeyboardButton(text=key,
                                              callback_data="['value', '" + value + "', '" + key + "']"))
    return markup2

@bot.message_handler(commands=['end'])
def surrend(message):
	try:
		sql_update('state','finish',message.from_user.username)
		bot.reply_to(message, 'oh my friend {} it was so hard for you,i khow'.format(message.from_user.first_name))
	except:
		print("there is problem in database",message.from_user.username)
		pass
@bot.message_handler(commands=['begin'])
def beginner(message):
	if message.from_user.username in sighuplist.keys():
		if sighuplist[message.from_user.username]['state']=='finish' :
			bot.reply_to(message, 'sorry you lose your chance !!!')
		elif sighuplist[message.from_user.username]['state']=='on match':
			bot.reply_to(message,'you are in match right now!')
			handle_command_adminwindow(message)
		elif sighuplist[message.from_user.username]['state']=='alive':
			sighuplist[message.from_user.username]['state']='on match'
			sighuplist[message.from_user.username]['timer']=time.time()
			handle_command_adminwindow(message)
	else:
		bot.reply_to(message, 'signup please \n /start \n /begin')

@bot.message_handler(commands=['next'])
def handle_command_adminwindow(message):
	if message.from_user.username in sighuplist.keys():
		sighuplist[message.from_user.username]['questionnum']+=1
		if sighuplist[message.from_user.username]['questionnum'] ==20 or sighuplist[message.from_user.username]['questionnum']>20 :
			bot.send_message(message.chat.id,u'\u2302'+'congratulation you have answered to all questions\nand your point is :{}'.format(sighuplist[message.from_user.username]['point']))
			bot.send_message(message.chat.id, u"\u26Fe"+" just take rest and relax", reply_markup=markup)
			sighuplist[message.from_user.username]['state']='finish'
		else:
			getquestion(message)
			sighuplist[message.from_user.username]['timer']=time.time()
	else:
		bot.reply_to(message, 'signup and begin match please \n /start')

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    global answerlist,questionsdoc,questionlist
    if (call.data.startswith("['value'")):
        valueFromCallBack = ast.literal_eval(call.data)[1]
        keyFromCallBack = ast.literal_eval(call.data)[2]
    if (time.time()-sighuplist[call.message.chat.username]['timer'])==45 or (time.time()-sighuplist[call.message.chat.username]['timer'])>45:
        bot.send_message(call.message.chat.id,'your time is finished!!!')
    elif len(valueFromCallBack)==20 :
        if valueFromCallBack==questionsdoc[questionlist[sighuplist[call.message.chat.username]['questionnumbers'][-1]]][answerlist[sighuplist[call.message.chat.username]['questionnumbers'][-1]]-1][0:20]:
           sighuplist[call.message.chat.username]['point']+=20
    elif valueFromCallBack==questionsdoc[questionlist[sighuplist[call.message.chat.username]['questionnumbers'][-1]]][answerlist[sighuplist[call.message.chat.username]['questionnumbers'][-1]]-1]:
        sighuplist[call.message.chat.username]['point']+=20
    bot.answer_callback_query(callback_query_id=call.id,
                          show_alert=True,
                          text="You Clicked " + valueFromCallBack + " and your choice is " + keyFromCallBack)
    bot.edit_message_text(chat_id=call.message.chat.id,
                          text="ok now for next question send next command \n /next",
                          message_id=call.message.message_id,
                          reply_markup=None,
                          parse_mode='HTML')
    nextquestion(call)

def sighup(message):
	if message.reply_to_message != None:
		try:
			if message.text=='flow':
				doc = open('output.xlsx', 'rb')
				bot.send_document(message.chat.id, doc)
			elif  len(message.text) != 11:
				msg = bot.reply_to(message, 'wrong input please input your phone number correctly: \n ex:09xxxxxxxxx',reply_markup=mksighup)
			else:
				bot.send_message(message.chat.id, " Ok now enter your first name :")
				sighuplist[message.from_user.username]={'match':'on','firstname':'','lastname':'','phonenumber':message.text,'questionnumbers':[],'stringList':'stringList','state':'alive','point':0,'questionnum':0,'timer':time.time(),'chat_id':message.chat.id}
				sighuplist[message.from_user.username]['stringList']=makequestion(message)
				z=(sighuplist[message.from_user.username],sighuplist[message.from_user.username]['firstname'],sighuplist[message.from_user.username]['lastname'],sighuplist[message.from_user.username]['phonenumber'],sighuplist[message.from_user.username]['point'],sighuplist[message.from_user.username]['state'])
				sql_insert(z)
		except:
			pass
	elif  message.content_type=='text':
		try:
			if message.text=='My point':
			 	bot.reply_to(message, "your point is :{}".format(sighuplist[message.from_user.username]['point']))
			elif message.text=='billboard':
				bot.send_message(message.chat.id, billboard(message))
			elif message.text=='home':
				send_welcome(message)
			elif message.text=='Fight on':
				bot.send_message(message.chat.id, "Alright you have only 15 sec for each question , 10 question and only one chance \n this are your commands\nfor surrendering /end \nfor next question /next \nfor begining /begin ")
			else:
				try:
					if sighuplist[message.from_user.username]['firstname'] =='':
						sighuplist[message.from_user.username]['firstname']=message.text
						bot.reply_to(message, "Good {} enter your lastname:".format(message.text))
					elif sighuplist[message.from_user.username]['lastname']=='':
						sighuplist[message.from_user.username]['lastname']=message.text
						bot.reply_to(message, "Well done {} {} your signup is complete".format(sighuplist[message.from_user.username]['firstname'],sighuplist[message.from_user.username]['lastname']))
						bot.send_message(message.chat.id, "Please choose from  this options", reply_markup=markup)
					else:
						bot.send_message(message.chat.id, "Please choose from  this options", reply_markup=markup)
				except:
						bot.reply_to(message, 'signup please \n /start')
		except:
			pass
	else:
		bot.reply_to(message, "wrong input!!!")

def getquestion(message):
	global answerlist,questionsdoc,questionlist
	s=questionlist[sighuplist[message.from_user.username]['questionnumbers'][-1]]
	g=questionsdoc[s]
	for text in util.split_string('{}\n{}\n{}\n{}\n{}'.format(str(sighuplist[message.from_user.username]['questionnum'])+':'+s,u"\u2160"+":"+g[0],u"\u2161"+":"+g[1],u"\u2162"+":"+g[2],u"\u2163"+":"+g[3]), 3000):
		bot.reply_to(message,text=text,reply_markup=makeKeyboard(sighuplist[message.from_user.username]['stringList']),parse_mode='HTML')

def makequestion(message):
	global answerlist,questionsdoc,questionlist
	n=randint(0,len(questionlist))
	sighuplist[message.from_user.username]['questionnumbers'].append(n)
	q=questionsdoc[questionlist[n]]
	return makestringlist(q[0],q[1],q[2],q[3])

def nextquestion(call):
	global answerlist,questionsdoc,questionlist
	number=randint(0,len(questionlist)-1)
	while number in sighuplist[call.message.chat.username]['questionnumbers']:
		number=randint(0,len(questionlist)-1)
		pass
	sighuplist[call.message.chat.username]['questionnumbers'].append(number)
	x=questionsdoc[questionlist[number]]
	sighuplist[call.message.chat.username]['stringList']=makestringlist(x[0],x[1],x[2],x[3])

def billboard(message):
	global first,second,third,champions
	for i in sighuplist.keys():
		if sighuplist[i]['point']==first or sighuplist[i]['point']>first:
			first=sighuplist[i]['point']
			champions[0]='{} : {}'.format(i,sighuplist[i]['point'])
	bill=copy.deepcopy(sighuplist)
	try:
		del bill[i]
		for i in bill.keys():
			if bill[i]['point']==second or bill[i]['point']>second:
				second=bill[i]['point']
				champions[1]='{} : {}'.format(i,bill[i]['point'])
	except:
		return '{}'.format(champions[0])
	try:
		bill2=copy.deepcopy(bill)
		del bill2[i]
		for i in bill2.keys():
			if bill2[i]['point']==third or bill2[i]['point']>third:
				third=bill2[i]['point']
				champions[2]='{} : {}'.format(i,bill2[i]['point'])
	except:
		return '{}\n{}'.format(champions[0],champions[1])
	return '{}\n{}\n{}'.format(champions[0],champions[1],champions[2])

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
	try:
		bot.reply_to(message,'hi {} Welcome to home we have examination hear'.format(message.from_user.first_name))
		if sighuplist.get(message.from_user.username)!=None:
			bot.send_message(message.chat.id, "Please choose from  this options", reply_markup=markup)
			pass
		else:
			bot.reply_to(message, "Enter your phone number:", reply_markup=mksighup)
	except:
		pass
@bot.message_handler(func=sighup)
def startmatch(message):
	if sighuplist[message.from_user.username]['firstname'] !='':
		bot.reply_to(message, "Please choose from options", reply_markup=markup)

@bot.message_handler(content_types=['document', 'audio'])
def handle_docs_audio(message):
	pass

@bot.message_handler(commands=['alpha'])
def output(message):
	try:
		bot.reply_to(message, "Hi mr/mis {} you are in alpha office enter password to receive results".format(message.from_user.first_name),reply_markup=mksighup)
	except:
		pass
	row=1
	for i in sighuplist:
		sheet["A{}".format(row)]=i
		sheet["b{}".format(row)]=sighuplist[i]['firstname']
		sheet["c{}".format(row)]=sighuplist[i]['lastname']
		sheet["d{}".format(row)]=sighuplist[i]['phonenumber']
		sheet["e{}".format(row)]=sighuplist[i]['point']
		sheet["f{}".format(row)]=sighuplist[i]['state']
		row+=1
	workbook.save(filename="output.xlsx")

@server.route('/' + API_TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url="https://civilmatch.herokuapp.com/{}".format(API_TOKEN)) #this will create by heroku create command
    return "!", 200

if __name__ == "__main__":
    server.run(host=WEBHOOK_LISTEN, port=int(os.environ.get("PORT", "8443")))
