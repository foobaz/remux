#!/usr/bin/env python3

import argparse
import json
import random
import os
import signal
import string
import sys
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('src', type=str, nargs='+', help='path to video')
args = parser.parse_args()

temp_dst = ''

def exit_handler(signum, frame):
    try:
        os.remove(temp_dst)
    except FileNotFoundError:
        pass
    sys.exit()

def remux_to_extension(src, ext):
    before_ext, old_ext = os.path.splitext(src)
    random_string = ''.join(random.choice(string.digits + string.ascii_letters) for i in range(16))

    global temp_dst
    temp_dst = before_ext + '-temporary' + random_string + ext

    sameExtension = (ext == old_ext)
    if sameExtension:
        final_dst = src
    else:
        final_dst = before_ext + ext

    subprocess_args = ['ffmpeg', '-hide_banner', '-loglevel', 'fatal', '-i', src, '-c:v', 'copy', '-c:a', 'copy', '-c:s', 'copy', '-c:d', 'copy', '-map', '0', '-movflags', '+faststart', temp_dst]
    #print(' '.join(subprocess_args), file=sys.stderr)
    out = subprocess.call(subprocess_args)
    if not out == 0:
        os.remove(temp_dst)
        return

    os.rename(temp_dst, final_dst)
    if not sameExtension:
        os.remove(src)

    return 0

def is_video(src):
    subprocess_args = ['ffprobe', '-hide_banner', '-loglevel', 'fatal', '-show_streams', '-show_format', '-print_format', 'json', src]
    try:
        out = subprocess.check_output(subprocess_args)
    except subprocess.CalledProcessError as e:
        #print('\tnot video because ffprobe returned {}'.format(e.returncode), file=sys.stderr)
        return False

    j = json.loads(out.decode('utf-8'))

    if not 'format' in j:
        print('\tnot video because no format', file=sys.stderr)
        return False
    f = j['format']

    if not 'probe_score' in f:
        print('\tnot video because no format name', file=sys.stderr)
        return False

    score = f['probe_score']
    if not score >= 100:
        #print('\tnot video because probe score == {}'.format(score), file=sys.stderr)
        return False

    if not 'format_name' in f:
        print('\tnot video because no format name', file=sys.stderr)
        return False

    name = f['format_name']
    if name == 'gif' or name == 'image2' or name == 'mjpeg' or name == 'pipe' or name == 'pngpipe' or name == 'tty':
        #print('\tnot video because text file or image', file=sys.stderr)
        return False

    if not 'streams' in j:
        print('\tnot video because no streams', file=sys.stderr)
        return False

    s = j['streams']
    for stream in s:
        if not 'codec_type' in stream:
            continue
        codec_type = stream['codec_type']
        if codec_type == 'video':
            return True

    #print('\tnot video because no video streams', file=sys.stderr)
    return False

def remux_video(src):
    if not is_video(src):
        return

    print('remuxing {} ...'.format(src), file=sys.stderr)

    #print('\ttrying raw MPEG-4...', file=sys.stderr)
    out = remux_to_extension(src, '.m4v')
    if out == 0:
        print('\tconverted {} to raw MPEG-4'.format(src), file=sys.stderr)
        return

    #print('\ttrying WebM...', file=sys.stderr)
    out = remux_to_extension(src, '.webm')
    if out == 0:
        print('\tconverted {} to WebM'.format(src), file=sys.stderr)
        return

    #print('\ttrying Ogg...', file=sys.stderr)
    out = remux_to_extension(src, '.ogv')
    if out == 0:
        print('\tconverted {} to Ogg'.format(src), file=sys.stderr)
        return

    #print('\ttrying MPEG-4...', file=sys.stderr)
    out = remux_to_extension(src, '.mp4')
    if out == 0:
        print('\tconverted {} to MPEG-4'.format(src), file=sys.stderr)
        return

    #print('\ttrying QuickTime...', file=sys.stderr)
    out = remux_to_extension(src, '.avi')
    if out == 0:
        print('\tconverted {} to AVI'.format(src), file=sys.stderr)
        return

    #print('\ttrying QuickTime...', file=sys.stderr)
    out = remux_to_extension(src, '.mov')
    if out == 0:
        print('\tconverted {} to QuickTime'.format(src), file=sys.stderr)
        return

    #print('\ttrying Matroska...', file=sys.stderr)
    out = remux_to_extension(src, '.mkv')
    if out == 0:
        print('\tconverted {} to Matroska'.format(src), file=sys.stderr)
        return

    print('\tcould not convert {} to any container format'.format(src), file=sys.stderr)

signal.signal(signal.SIGINT, exit_handler)
signal.signal(signal.SIGTERM, exit_handler)
signal.signal(signal.SIGQUIT, exit_handler)

for s in args.src:
    remux_video(s)
