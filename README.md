# BlackPixelPercentage Reddit Bot

A Python3 based Reddit bot calculating the true black pixel percentage of submissions, with comment support and an offline feature.

The script will load an offline or online image, check each pixel for its color value and calculate the percentage of true black pixels in the image.

## Disclaimer

The script is still in beta and I run it manually every now and then.
If this turns out to be appreciated, I'll move it to a server and have it run periodically.

The associated Reddit account is [/u/black-percentage-bot](https://www.reddit.com/user/black-percentage-bot/)

## Usage

Requires `pillow` for image processing and `praw` to access the reddit API.

	sudo pip3 install pillow praw

The script will process the newest 16 posts in [/r/AmoledBackgrounds](https://www.reddit.com/r/Amoledbackgrounds/) if not specified otherwise.

With the comment mode enabled (-c/--comments), the script with process up to _max_ posts, reading each comment, checking for the trigger phrase and a direct image link, for which it will do its thing and answer the comment.

Alternatively the script can be used to process a local file or a number of local files in a specified directory (-o/--offline).

	usage: bpb.py [-h] [-s SUBREDDIT] [-c COMMENTS] [-m MAX] [-o OFFLINE] [-l LOG]
	              [-t TRIGGER] [-v] [-d]

	(True)BlackPercentageBot v0.1
	does things. Lacks an in-script description.
	Source: https://gitlab.com/black-percentage-bot/bpb
	Reddit: https://www.reddit.com/user/black-percentage-bot/
	License: WTFPL

	optional arguments:
	  -h, --help            show this help message and exit
	  -s SUBREDDIT, --subreddit SUBREDDIT
	                        Defines the Subreddit to process. Default: AmoledBackgrounds
	  -c COMMENTS, --comments COMMENTS
	                        Parses the comments, rather than the posts, used to answer comment requests. Default False
	  -m MAX, --max MAX     Defines the maximum number of processed posts (with -c/--comments, all comments in each post are processed). Default: 16
	  -o OFFLINE, --offline OFFLINE
	                        Parse a local directory or single image, instead of a defined Subreddit. Default: False
	  -l LOG, --log LOG     Defines the log file with processed Reddit posts, using an absolute or relative path. Default: ./bpb.log
	  -t TRIGGER, --trigger TRIGGER
	                        Defines the phrase in comments to trigger the bot. Requries -c/--comments. Default: calculate black percentage please
	  -v, --verbose         Verbose mode
	  -d, --debug           Debug mode. Doesn't post comment but prints it on the console.



## Feedback, reports, requests or rants

Open an issue or send me an e-mail (blackpercentagebot <sub>_0x40_</sub> tuta <sub>_0x2e_</sub> io).

Please include a link to the comment you're refering to for reports.

## In progress / ToDo's

 - Actually implement the comment function
 - Implement a process to interpret the ratelimit wait time, wait that long and then continue instead of exiting
 - Probably quite some bugfixes and performance issues
 - `¯\_(ツ)_/¯`

## License

[WTFPL](LICENSE-WTFPL)