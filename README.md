This script records models from stripchat.com/xhamsterlive.com continuously by exploiting a publically accessible API of the site and agnostic hls-routing. As of now this script has still many problems including:

- no cli-options functionality
- buggy multi-threading of ffmpeg-recording
- only refreshes models-to-record-list, once last models stream of the current models-to-record-list hasn't been accessible by ffmpeg for quite some time. should do that regularly, concurrently with ffmpeg-streaming of previous models-to-record-list.
- generally not finished 

before running this script, create "models_followed.txt" file. Inside this file, list the model usernames that you want to be surveilled/recorded separated by newline (capitalisation doesn't matter, rank-ordered list). Example:

modelone
modeltwo
modelthree

then (on ubuntu) cd into the directory of this script and execute "python3 main.py". If all requirements are met, the script will start outputting which of the models in models_followed.txt file are on-line (top 8 on-line) and then a bunch of ffmpeg log.
