# Black Pixel Percentage Reddit Bot

A Python3 based Reddit bot calculating the true black pixel percentage of submissions, with comment support and an offline feature.

The script processes offline or online images, checks each pixel for their color value and calculate the percentage of true black pixels of the image.

The repository's name and the scritp's filename `bpb` stands for black percentage bot, <sub>because I suck at making up my mind and use variations of the name everywhere.</sub>

## Current public service

Right now the bot runs in two instances on a public server, which I paid for and exclusively use for this purpose. If the performance isn't cut out for the task I'll see what I can do. 

The bot will process the latest four submissions every four minutes, all comments of up to five stickied submissions and all comments of the latest 20 submissions. As the comment feature has been just recently introduced, I'm limiting the number of submissions, the bot scans for comment requests quite harsly. If it turns out to work well and people use it, I'll extend the scope to more (possibly all posts of /r/AmoledBackgrounds) to cover everything. This would probably require slower intervals or a "better" server. Time will tell.

## Disclaimer

The script currently runs on a pretty cheap server (a.k.a. the ominous *CLOUD*), which I've rented for a year now. If the server's not performant not enough or if it's used more than expected I'll have to see what I can do.

**For those who are using the [/r/AmoledBackgrounds (or better /u/OLEDBuddy) OLEDBuddy](https://play.google.com/store/apps/details?id=me.mikecroall.oledbuddy):** If you're experiencing a discrepancy between the calculated black pixel percentage it's most likely the compression of the used image hoster (e.g. imgur.com). We've briefly discussed our methods and have conclueded that it must be, that some hosters (again, e.g. imgur.com) compress images on upload and mess with the true black pixel percentage. 

The associated Reddit account is [/u/black-percentage-bot](https://www.reddit.com/user/black-percentage-bot/)

## Personal usage

Requires `pillow` for image processing and `praw` to access the reddit API.

	sudo pip3 install pillow praw

The script will process the newest 16 posts in [/r/AmoledBackgrounds](https://www.reddit.com/r/Amoledbackgrounds/) if not specified otherwise.

With the comment mode enabled (-c/--comments), the script with process up to _max_ new posts and up to five stickied submissions, reading each comment, checking for the trigger phrase and a direct image link, for which it will do its thing and answer the comment.

Alternatively the script can be used to process a local file or a number of local files in a specified directory (-o/--offline).

	usage: bpb.py [-h] [-s SUBREDDIT] [-c] [-m MAX] [-i INTERVALL] [-o OFFLINE]
	              [-l LOG] [-t TRIGGER] [-v] [-d]

	(True)BlackPercentageBot v0.2
	does things. Lacks an in-script description.
	Source: https://github.com/black-percentage-bot/bpb
	Reddit: https://www.reddit.com/user/black-percentage-bot/
	License: WTFPL

	optional arguments:
	  -h, --help            show this help message and exit
	  -s SUBREDDIT, --subreddit SUBREDDIT
	                        Defines the Subreddit to process. Default: AmoledBackgrounds
	  -c, --comments        Parses the comments, rather than the posts, used to answer comment requests. Default False
	  -m MAX, --max MAX     Defines the maximum number of processed posts (with -c/--comments, all comments in each post are processed). Default: 16
	  -i INTERVALL, --intervall INTERVALL
	                        If defined, the bot will repeatedly run in intervalls of the defined number (3600s for seconds, 60m for minutes or 1h for hours) until manually stopped. Default: False
	  -o OFFLINE, --offline OFFLINE
	                        Parse a local directory or single image, instead of a defined Subreddit. Default: False
	  -l LOG, --log LOG     Defines the log file with processed Reddit posts, using an absolute or relative path. Default: ./bpb.log
	  -t TRIGGER, --trigger TRIGGER
	                        Defines the phrase in comments to trigger the bot. Requries -c/--comments. Default: black percentage please
	  -v, --verbose         Verbose mode
	  -d, --debug           Debug mode. Doesn't post comment but prints it on the console.


## Feedback, reports, requests or rants

Open an issue or send me an e-mail (blackpercentagebot <sub>_0x40_</sub> tuta <sub>_0x2e_</sub> io).

Please include a link to the comment you're refering to for reports.

## Issues

	- Comment feature: Only the very first URL in a comment with the trigger request is considered
	- Comment feature: Works only if the direct image URL is the very last thing in the *line* which features the trigger prhase.

## In progress / ToDo's

 - Implement a process to interpret the ratelimit wait time, wait that long and then continue instead of exiting
 - Probably quite some bugfixes and performance (e.g. disk i/o) issues
 - `¯\_(ツ)_/¯`


## License

[WTFPL](LICENSE-WTFPL)