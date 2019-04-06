#!/usr/bin/python3
import praw, os, requests, sys, argparse, datetime, re
from io import StringIO
from PIL import Image
import time

from os import access, R_OK
from os.path import isfile

#Image.MAX_IMAGE_PIXELS = 1000000000
#Image.MAX_IMAGE_PIXELS = 207370000                                                                                             

def check_offline(p):
	if (os.path.isfile(p) or os.path.isdir(p)) and os.access(p, os.R_OK):
		return p
	else:
		raise argparse.ArgumentTypeError("\""+str(p)+"\" is not a directory, a file or it's not readable.")

# parse valid url from string
# only the first link in the string will be returned
def get_url(s):
    #previously used url matcher
    url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', s)
    return url

	#u=""
    #if isinstance(s, String):

     #   print("ADFASDFASDF:" +str(s))
      #  u=re.search("(?P<url>https?://[^\s]+)", s).group("url")
    	# if markdown links are used, links are pollutted
       # if u.endswith(')') or u.endswith(']'):
       #     return u[:-1]
    #return u

# Ok so the same log file can be used for submissions and comments,
# but if two instances on the same system use the same log file I may have a race condition/concurrency issue here.
def check_log(p):
	if os.path.isfile(p) and os.access(p, os.R_OK) and os.access(p, os.W_OK):
		return p
	else:
		try:
			open(p, 'a').close()
		except Exception as e:
			raise argparse.ArgumentTypeError("The defined log file \""+str(p)+"\" is not a file or read-/writeable.")
			
		if os.path.isfile(p) and os.access(p, os.R_OK) and os.access(p, os.W_OK):
			return p
		else:
			raise argparse.ArgumentTypeError("The defined log file \""+str(p)+"\" is not a file or read-/writeable.")

# Process all comments, takes loads of arguments
# sub = Submission
# tri = Trigger string
# ver = Verbouse flag
# prc = Processed list
# log = Logfile
# iex = Image extensions
# msg = Bot message
# dbg = Debug flag
def process_all_comments(sub, tri, ver, prc, log, iex, msg, dbg):

	sub.comments.replace_more(limit=None)
	cn=0
	for comment in sub.comments.list():
		#print(comment.body)
		cn+=1
		if comment.id in prc:
			continue
		if tri in comment.body.lower():
			url=get_url(comment.body)
			if url:
				if url[0].split('.')[-1] in iex:
					print("\nValid request comment: ", str(url[0]))
					
					perc = calc_perc(url[0],"online")						
					com = "^^\(true\) Black pixel percentage: **"+str(round(perc[0],2))+"%** ^^^\("+str(perc[1])+"/"+str(perc[2])+"\)"+msg
					if not dbg:
						comment.reply(com)
					else:
						print('[DEBUG] '+str(com))
					
					prc.append(comment.id)
					with open(log, "a") as f:
							f.write(comment.id + "\n")
				elif ver:
					print('Request comment with unsupported URL. '+str(url[0]))
			elif ver:
				print('Request comment without URL.')
		if ver:
			print('.',end='', flush=True)

	return(cn)

def check_intervall(i):

	try:
		if isinstance(int(i[:-1]),int):
			if i.lower().endswith('s'):
				return int(i[:-1])
			elif i.lower().endswith('m'):
				return int(i[:-1])*60
			elif i.lower().endswith('h'):
				return int(i[:-1])*60*60
			else:
				raise argparse.ArgumentTypeError("The defined intervall unit \""+str(i[-1])+"\" is not supported. Use 's' for seconds, 'm' for minutes or 'h' for hours (e.g -i 427s)")
		else:
			raise argparse.ArgumentTypeError("The defined intervall time \""+str(i[:-1])+"\" is not an integer.")
	except ValueError as e:
		raise argparse.ArgumentTypeError("The defined intervall time \""+str(i[:-1])+"\" is not an integer.")

# calculate percentage
# returns list of percentage, trueblack pixel count and total number of 
# m defines the mode: "online" or "offline".
def calc_perc(u,m):
	tbpc = 0
	if m == "online":
		try:
			img = Image.open(requests.get(u, stream=True).raw)
		except exception as e:
			print("\n["+str(time.strftime("%H:%M:%S"))+"] [ERROR] ", end='', flush=True)
			print(str(e))
			print()
			return "err"
	else:
		img = Image.open(u)
	pic = img.load()
	total = img.height*img.width

	for h in range(0, img.height):
		for w in range(0, img.width):

			# I am definitely no image format wizard.
			# For some reason pixels are sometimes defined as a list (e.g. true black is [0,0,0])
			# and sometimes as a single int (e.g. true black is 0).
			# Grayscale image true black seems to be [0,255].
			# If you read this and know why, shoot me a message.
			if isinstance(pic[w,h],int):
				if pic[w,h] == 0:
					tbpc += 1
			else: 
				try:
					if isinstance(pic[w,h][2],int):
						if pic[w,h][0] == 0 and pic[w,h][1] == 0 and pic[w,h][2] == 0:
							tbpc += 1
				except IndexError:
					# prolly grayscale: 0, 255
					if pic[w,h][0] == 0 and pic[w,h][1] == 255:
						tbpc += 1

	return([tbpc/(total/100),tbpc,total])

def main():

	# source code
	source_url = "https://github.com/black-percentage-bot/bpb"
	reddit_url = "https://www.reddit.com/user/black-percentage-bot"

	title = "(True)BlackPercentageBot v0.2\n"
	desc = "does things. Lacks an in-script description.\nSource: "+str(source_url)+"\nReddit: "+str(reddit_url)+"/\nLicense: WTFPL"
	def_sub = "AmoledBackgrounds"
	def_off = False
	def_log = "./bpb.log"
	def_com = False
	def_max = 16
	def_itv = False
	def_tri = "black percentage please"

	# Supported image files
	image_file_exts = ['png','jpg','jpeg','gif']

	# Reddit API / praw settings (see praw.ini)
	reddit = praw.Reddit('bpb')
	
	# bot message for comments
	bot_msg = "\n\n---\n\n^*beep-boop*. ^I'm ^a ^bot. ^Post ^feedback, ^reports, ^requests ^or ^rants ^[here.]("+str(source_url)+") ^^Details ^^on ^^the ^^discrepancy ^^between ^^this ^^and ^^[OLEDBuddy](https://play.google.com/store/apps/details?id=me.mikecroall.oledbuddy) ^^included."

	parser = argparse.ArgumentParser(description=title+desc,formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument("-s", "--subreddit", help="Defines the Subreddit to process. Default: "+str(def_sub), default=def_sub)
	parser.add_argument("-c", "--comments", help="Parses the comments, rather than the posts, used to answer comment requests. Default "+str(def_com), default=def_com, action='store_true')
	parser.add_argument("-m", "--max", help="Defines the maximum number of processed posts (with -c/--comments, all comments in each post are processed). Default: "+str(def_max), type=int)
	parser.add_argument("-i", "--intervall", help="If defined, the bot will repeatedly run in intervalls of the defined number (3600s for seconds, 60m for minutes or 1h for hours) until manually stopped. Default: "+str(def_itv), type=check_intervall)
	parser.add_argument("-o", "--offline", help="Parse a local directory or single image, instead of a defined Subreddit. Default: "+str(def_off), default=def_off, type=check_offline)
	parser.add_argument("-l", "--log", help="Defines the log file with processed Reddit posts, using an absolute or relative path. Default: "+str(def_log), default=def_log, type=check_log)
	parser.add_argument("-t", "--trigger", help="Defines the phrase in comments to trigger the bot. Requries -c/--comments. Default: "+str(def_tri), default=def_tri, type=str)
	parser.add_argument("-v", "--verbose", help="Verbose mode", action='store_true')
	parser.add_argument("-d", "--debug", help="Debug mode. Doesn't post comment but prints it on the console.", action='store_true')

	args = parser.parse_args()
	sub = args.subreddit
	com = args.comments
	max = args.max
	itv = args.intervall
	off = args.offline
	log = args.log
	ver = args.verbose
	dbg = args.debug
	tri = args.trigger

	start_time=datetime.datetime.utcnow()

	if off:
		if os.path.isfile(off):
			perc = calc_perc(off,"offline")
			if ver:
				print("\""+str(off)+"\" has a (true) black pixel percentage of "+str(round(perc[0],2))+"% with "+str(perc[1])+" black pixels of "+str(perc[2])+".")
			else:
				print(str(round(perc[0],4))+"% "+str(off))
		else:
			for f in os.listdir(off):
				file=os.path.join(off, f)
				if f.split('.')[-1] in image_file_exts:
					perc = calc_perc(file,"offline")
					if ver:
						print("\""+str(file)+"\" has a (true) black pixel percentage of "+str(round(perc[0],2))+"% with "+str(perc[1])+" black pixels of "+str(perc[2])+".")
					else:
						print(str(round(perc[0],4))+"% "+str(file))
				elif ver:
					print("Skipped \""+str(file)+"\", due to the unsupported file extension.")
		exit(0)

	subreddit = reddit.subreddit(sub)
	processed_list = []

	# read log to list
	with open(log, "r") as f:
		processed_list = f.read()
		processed_list = processed_list.split("\n")
		processed_list = list(filter(None, processed_list))

	rep_num = 0

	while True:
		num = 0
		rep_num += 1
		err = False

		if ver and itv:
			print("["+str(time.strftime("%H:%M:%S"))+"] ", end='', flush=True)
			print("Repetition #"+str(rep_num)+" - Uptime: "+str(datetime.timedelta(seconds=((datetime.datetime.utcnow()-start_time).total_seconds()))))

		# process submissions
		if not com:

			for submission in subreddit.new(limit=max):
				num+=1
				if ver:
					print("["+str(time.strftime("%H:%M:%S"))+"] ", end='', flush=True)
					print("Processing submission #"+str(num)+"... ", end='', flush=True)
				# Process post only if not already processed (see log)
				if submission.id in processed_list:
					if ver:
						print("Previosuly processed.")
				else:
					url = submission.url
					if url.split('.')[-1] in image_file_exts:
						if ver:
							print("Found supported image ("+str(url)+"): ")
						perc = calc_perc(url,"online")						
						if perc == err:
							time.sleep(itv)
							continue
						comment = "^^\(true\) Black pixel percentage: **"+str(round(perc[0],2))+"%** ^^^\("+str(perc[1])+"/"+str(perc[2])+"\)"+bot_msg
						if not dbg:
							try:
								submission.reply(comment)
							except praw.exceptions.APIException as e:
								if "RATELIMIT" in str(e):
									print("\n[ERROR] Reddit API ratelimit reached.")
								if ver:
									print("\n\n"+str(e))
									exit(1)
							if ver:
								print("\t"+str(comment))
						else:
							print("[DEBUG] ["+str(time.strftime("%H:%M:%S"))+"]\n\t"+str(repr(comment))+"\n\tfor "+str(url))

					else:
						if ver:
							print("No image or unsupported format. ("+str(url)+")")

					processed_list.append(submission.id)
					with open(log, "a") as f:
						f.write(submission.id + "\n")
		# process comments
		else: 
			if ver:
				print("["+str(time.strftime("%H:%M:%S"))+"] ", end='', flush=True)
				print("Processing all comments of up to five stickied submissions.")

			num = 0
			# process all comments in the stickies (max 5).
			for submission in subreddit.hot(limit=5):
				num+=1
				if not submission.stickied:
					break
				if ver:
					print("["+str(time.strftime("%H:%M:%S"))+"] ", end='', flush=True)
					print("Processing stickied submission #"+str(num)+"... ", end='', flush=True)
				#def process_all_comments(sub, tri, ver, prc, log, iex, msg, dbg):
				cn = process_all_comments(submission, tri, ver, processed_list, log, image_file_exts, bot_msg, dbg)
				if ver:					
					print(" ("+str(cn) +" comments)")

			if ver:
				print("["+str(time.strftime("%H:%M:%S"))+"] ", end='', flush=True)
				print("Processing all comments of the newest "+str(max)+" submissions.")

			num = 0
			# process all comments of the newest max posts
			for submission in subreddit.new(limit=max):
				num+=1
				if ver:
					print("["+str(time.strftime("%H:%M:%S"))+"] ", end='', flush=True)
					print("Processing submission #"+str(num)+"... ", end='', flush=True)
				cn = process_all_comments(submission, tri, ver, processed_list, log, image_file_exts, bot_msg, dbg)
				
				if ver:					
					print(" ("+str(cn) +" comments)")
		if not itv:
			break
		else:
			print("["+str(time.strftime("%H:%M:%S"))+"] ", end='', flush=True)
			print("Sleeping until "+str(time.strftime("%H:%M:%S", time.localtime(int(time.time()+itv))))+" for next repetition... ", end='', flush=True)
			time.sleep(itv)
			print("done.")

if __name__ == "__main__":
	main()
