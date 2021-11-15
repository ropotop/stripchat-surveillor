This script records models from stripchat.com/xhamsterlive.com continuously by exploiting a publically accessible API of the site and agnostic hls-routing. As of now this script has still many problems including:

- no cli-options functionality
- only refreshes models-to-record-list, once last models stream of the current models-to-record-list hasn't been accessible by ffmpeg for quite some time. should do that regularly, concurrently with ffmpeg-streaming of previous models-to-record-list.
- generally not finished (but does the minimal things it should do, so works)
- don't know if running video_stitcher in parallel with main() will break the script

selenium chromedriver chromium automation is not used anymore because m3u8-link can be deducted by model-id (which is accessible by simple API-request). any selenium-related code is deprecated.

before running this script, create "models_followed.txt" file. Inside this file, list the model usernames that you want to be surveilled/recorded separated by newline (capitalisation doesn't matter, rank-ordered list).

then (on linux) cd into the directory of this script and execute "python3 main.py". If all requirements are met, the script will start outputting which of the models in models_followed.txt file are on-line (top 8 on-line) and then a bunch of ffmpeg log. This script is tested on linux and Python 3.8.10
