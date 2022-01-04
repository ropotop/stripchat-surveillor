This script records models from stripchat.com/xhamsterlive.com continuously by exploiting a publically accessible API of the site and agnostic hls-routing.

This script is tested in Ubuntu and with ffmpeg version 4.2.4-1ubuntu0.1. If it functions for other operating systems or ffmpeg binaries is not known.

The easiest way to run this script (in Ubuntu):

'''
python3 surveillor.py <model usernames in lower-case, separated by space>
'''

To ease repeated recording of a long list of followed models, create models_followed.txt and write each model username in lower-case separated by newline into this text file. Then execute script without arguments.
