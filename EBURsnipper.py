'''
The EBUR128 version of the silence snipper script aims to get a more exact
reading of silences using the EBU R128 function in ffmpeg. We grab the
Momentary silences from the output which measure every 100ms, and hopefully
can make more exact snips using this, and find silences where the normal
script could not.
'''

import subprocess, os, sys, re

# Sort out the keyword arguments
path = sys.argv[1]
threshold = sys.argv[2]

print('Path is ' + str(path))
print('Threshold is ' + str(threshold))

# Make a List of all video files in the folder
raw_clips = []
for name in os.listdir(path):
    if name.endswith('.mp4'):
        raw_clips.append(name)

# This function is designed to work whether or not a start/end edit point was found
def getTrim(clip, start, end, output):
    print('Trimming {}...'.format(clip))
    print('Start: {}'.format(start))
    print('End: {}'.format(end))
    if start != '':
        print('Edit point at start found.')
        start = '-ss ' + start
    if end != '':
        print('Edit point at end found.')
        end = '-to ' + end
    subprocess.run('ffmpeg -hide_banner -loglevel warning {} {} -i {} {}'
                    .format(start, end, clip, output),
                    shell=True)
    print('Trim finished.')

# Grab the total duration of a clip and clean the output
def getClipDuration(clip):
    print('Grabbing duration for {}...'.format(clip))
    clip_duration = subprocess.run(
        'ffprobe -hide_banner -v error -select_streams v:0 -show_entries stream=duration -of default=nw=1:nk=1 {}'
        .format(clip),
        shell=True, capture_output=True, text=True
    )
    clip_duration = float(re.findall('\d*\.\d*', clip_duration.stdout)[0])
    print('Duration is ' + str(clip_duration))
    return clip_duration

# This will return a list of silences under the threshold dB using EBU R128's output
def getSilences(clip, thresh):
    print('Getting silences for {} at {}dB...'.format(clip, thresh))
    ffmpeg_output = subprocess.run('ffmpeg -hide_banner -nostats -i {} -filter_complex ebur128 -f null - 2>&1 | findstr "Parsed"'
        .format(clip),
        shell=True, capture_output=True, text=True
    )

    # This is all just cleaning the output
    timestamps = re.findall('t:\s?\d*\.?\d*', ffmpeg_output.stdout)[4:-2]
    loudness = re.findall('M:\s?-\d*\.?\d', ffmpeg_output.stdout)[4:-2]
    for i in range(len(timestamps)):
        timestamps[i] = float(timestamps[i][3:])
    for i in range(len(loudness)):
        loudness[i] = float(loudness[i][loudness[i].find('-'):])

    # Here we're going through the lists to detect periods below the dB threshold
    counter = 0
    silences = []
    for i in range(len(loudness)):
        if loudness[i] < float(thresh):
            counter = counter + 1
        elif counter > 0:
            silences.append((timestamps[i-counter], timestamps[i-1]))
            counter = 0
        else:
            counter = 0

    print('Silences for {} found:'.format(clip))
    for i in silences:
        print(i)
    return silences

# This picks the ideal silence out of the list provided
def silencePicker(clip, silences):
    clip_duration = getClipDuration(clip)
    # Discount the items not towards the beginning or end
    viable_starts, viable_ends = [], []
    for silence in silences:
        if silence[0] < clip_duration * 0.3:
            viable_starts.append(silence)
        if silence[0] > clip_duration * 0.7:
            viable_ends.append(silence)
    print(str(len(viable_starts)) + ' viable starts found:')
    for i in viable_starts:
        print(i)
    print(str(len(viable_ends)) + ' viable ends found:')
    for i in viable_ends:
        print(i)

    # Aim for the longest silence duration possible before returning
    start_diffs, end_diffs = [], []
    if len(viable_starts) > 0:
        for i in viable_starts:
            start_diffs.append(i[1] - i[0])
        max_diff = viable_starts[start_diffs.index(max(start_diffs))]

        # If the silence was long enough to register two time blocks or more,
        # we'll take the middle point of the silence as our edit point
        if max_diff[0] == max_diff[1]:
            startpoint = str(max_diff[0])
        else:
            startpoint = max_diff[0] + (max_diff[1] - max_diff[0]) / 2
    else:
        startpoint = ''

    # Doing the same thing for the endpoints
    if len(viable_ends) > 0:
        for i in viable_ends:
            end_diffs.append(i[1] - i[0])
        max_diff = viable_ends[end_diffs.index(max(end_diffs))]
        if max_diff[0] == max_diff[1]:
            endpoint = str(max_diff[0])
        else:
            endpoint = max_diff[0] + (max_diff[1] - max_diff[0]) / 2
    else:
        endpoint = ''

    return startpoint, endpoint

# Loop through all the raw clips, get silences, pick silences, then trim
def main():
    for clip in raw_clips:
        silences = getSilences(clip, threshold)
        startpoint, endpoint = silencePicker(clip, silences)

        # Trim the files along their edit points and output a new file
        output = 'a' + str(clip)[:2] + str(clip)[2:]
        print('Outputting file ' + output + '...')
        getTrim(clip, str(startpoint), str(endpoint), output)
        print('Done.')

if __name__ == '__main__':
    main()
