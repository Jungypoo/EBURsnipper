# EBURsnipper
This script uses the EBUR128 system in FFMPEG to detect silences towards the beginning and end of several videos files in a folder, and then trims the video files at points halfway through those silences. The resulting output files can then be automated to a timeline in Premiere with transitions, making for easy editing. The original use was for editing CSGO highlights videos at gaps in the commentary, but if it helps anyone else, then great!

The EBUR128 version of the silence snipper script aims to get a more exact reading of silences using the EBU R128 function in ffmpeg. We grab the Momentary silences from the output which measure every 100ms, and hopefully can make more exact snips using this, and find silences where the normal script could not.

This script requires both Python and FFMPEG to be installed. For the instructions below, make sure the folder housing this script is added to PATH.

Open a terminal and run EBURsnipper.py from within the folder that houses the video files. You'll need to send two arguments along with the command -- the first is the path (just "." if you're already inside the right folder), and the second is the dB threshold you'd like to use to determine what a "silence" is. I usually go for -30dB.

That means a common command in the terminal would look like this:

EBURsnipper.py . -30

The script will then output files that are snipped at their silence points, with an "a" at the beginning of the filename for easy sorting in the folder. You can now add these files to your editing program of choice. In Premiere you can use the "automate to sequence" tool with transitions to easily add everything to the timeline. Other apps like Resolve regognise Python, so it's possible to automate adding clips to the timeline there as well. Plus there's MoviePy, FFMPEG concat, or whatever your preferred method might be.

GLHF and feel free to contact me at @TheJunglist 
