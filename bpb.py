#!/usr/bin/python3
import praw, os, requests, sys, argparse
from io import StringIO
from PIL import Image
import time

from os import access, R_OK
from os.path import isfile

def check_offline(p):
	if (os.path.isfile(p) or os.path.isdir(p)) and os.access(p, os.R_OK):
		return p
	else:
		raise argparse.ArgumentTypeError("\""+str(p)+"\" is not a directory, a file or it's not readable.")

def check_log(p):
	if os.path.isfile(p) and os.access(p, os.R_OK) and os.access(p, os.W_OK):
		return p
	else:
		raise argparse.ArgumentTypeError("The defined log file \""+str(p)+"\" is not a file or read-/writeable.")

# calculate percentage
# returns list of percentage, trueblack pixel count and total number of 
# m defines the mode: "online" or "offline".
def calc_perc(u,m):
	tbpc = 0
	if m == "online":
		img = Image.open(requests.get(u, stream=True).raw)
	else:
		img = Image.open(u)
	pic = img.load()
	total = img.height*img.width

	for h in range(0, img.height):
		for w in range(0, img.width):

			# I am definitely no image format wizard.
			# For some reason pixels are sometimes defined as a list (e.g. true black is [0,0,0])
			# and sometimes as a single int (e.g. true black is 0).
			# If you read this and know why, shoot me a message.
			if isinstance(pic[w,h],int):
				if pic[w,h] == 0:
					tbpc += 1
			else: 
				if pic[w,h][0] == 0 and pic[w,h][1] == 0 and pic[w,h][2] == 0:
					tbpc += 1

	return([tbpc/(total/100),tbpc,total])

def main():

	title = "(True)BlackPercentageBot v0.1\n"
	desc = "does things. Lacks an in-script description.\nSource: https://gitlab.com/black-percentage-bot/bpb\nReddit: https://www.reddit.com/user/black-percentage-bot/\nLicense: WTFPL"
	def_sub = "AmoledBackgrounds"
	def_off = False
	def_log = "./bpb.log"
	def_com = False
	def_max = 16
	def_tri = "calculate black percentage please"

	# Supported image files
	image_file_exts = ['png','jpg','jpeg','gif']

	# Reddit API / praw settings (see praw.ini)
	reddit = praw.Reddit('bpb')

	# source code
	source = "https://gitlab.com/black-percentage-bot/bpb"
	
	# bot message for comments
	bot_msg = "\n\n---\n\n^*beep-boop*. ^I'm ^a ^bot. ^Post ^feedback, ^reports, ^requests ^or ^rants ^[here.]("+str(source)+")"

	parser = argparse.ArgumentParser(description=title+desc,formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument("-s", "--subreddit", help="Defines the Subreddit to process. Default: "+str(def_sub), default=def_sub)
	parser.add_argument("-c", "--comments", help="Parses the comments, rather than the posts, used to answer comment requests. Default "+str(def_com), default=def_com, action='store_true')
	parser.add_argument("-m", "--max", help="Defines the maximum number of processed posts (with -c/--comments, all comments in each post are processed). Default: "+str(def_max), type=int)
	parser.add_argument("-o", "--offline", help="Parse a local directory or single image, instead of a defined Subreddit. Default: "+str(def_off), default=def_off, type=check_offline)
	parser.add_argument("-l", "--log", help="Defines the log file with processed Reddit posts, using an absolute or relative path. Default: "+str(def_log), default=def_log, type=check_log)
	parser.add_argument("-t", "--trigger", help="Defines the phrase in comments to trigger the bot. Requries -c/--comments. Default: "+str(def_tri), default=def_tri, type=str)
	parser.add_argument("-v", "--verbose", help="Verbose mode", action='store_true')
	parser.add_argument("-d", "--debug", help="Debug mode. Doesn't post comment but prints it on the console.", action='store_true')

	args = parser.parse_args()
	sub = args.subreddit
	com = args.comments
	max = args.max
	off = args.offline
	log = args.log
	ver = args.verbose
	dbg = args.debug

	if off:
		if os.path.isfile(off):
			perc = calc_perc(off,"offline")
			if ver:
				print("\""+str(off)+"\" has a (true) black pixel percentage of "+str(round(perc[0],4))+"% with "+str(perc[1])+" black pixels of "+str(perc[2])+".")
			else:
				print(str(round(perc[0],4))+"% "+str(off))
		else:
			for f in os.listdir(off):
				file=os.path.join(off, f)
				if f.split('.')[-1] in image_file_exts:
					perc = calc_perc(file,"offline")
					if ver:
						print("\""+str(file)+"\" has a (true) black pixel percentage of "+str(round(perc[0],4))+"% with "+str(perc[1])+" black pixels of "+str(perc[2])+".")
					else:
						print(str(round(perc[0],4))+"% "+str(file))
				elif ver:
					print("Skipped \""+str(file)+"\", due to the unsupported file extension.")
		exit(0)

	subreddit = reddit.subreddit(sub)
	processed_list = []

	if not com:
		# read log to list
		# not required in comment mode
		if os.path.isfile(log):
			with open(log, "r") as f:
				processed_list = f.read()
				processed_list = processed_list.split("\n")
				processed_list = list(filter(None, processed_list))
		else:
			processed_list = []

	num = 0
	for submission in subreddit.new(limit=max):
		num+=1
		if ver:
			print("["+str(time.strftime("%H:%M:%S"))+"] ",end='')
			print("Processing #"+str(num)+"... ",end='')
		
		if com:
			print("Comment mode not implemented yet.")
			exit(0)
		else:
			# Process post only if not already processed (see log) or bot is in comment mode
			if (submission.id in processed_list) or com:
				if ver:
					print("Previosuly processed.")
			else:
				url = submission.url
				if url.split('.')[-1] in image_file_exts:
					if ver:
						print("Found supported image ("+str(url)+"): ")

					perc = calc_perc(url,"online")
					
					comment = "^^\(true\) Black pixel percentage: **"+str(round(perc[0],4))+"%** ^^^\("+str(perc[1])+"/"+str(perc[2])+"\)"+bot_msg
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

				if not com:
					# add submission id to the log file
					# not required in comment mode
					with open(log, "a") as f:
							f.write(submission.id + "\n")


if __name__ == "__main__":
	main()