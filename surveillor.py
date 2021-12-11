import json
import os
import subprocess
import ffmpy
from datetime import datetime
import requests
import concurrent.futures
from time import sleep
import threading


def m3u8_link_recorder(m3u8_link: str, model_username: str):
    """records video through m3u8 link. Is called by concurrent_stream_recording 
    method to be executed once per m3u8 link in parallel."""

    vids_preprocessed_dir = "vids_preprocessed"
    model_path = os.path.join(vids_preprocessed_dir, model_username)
    datetime_tag = datetime.now().strftime("%y%m%d_%H%M%S")
    vid_name = f"{datetime_tag}.mkv"
    vid_path = os.path.join(vids_preprocessed_dir, model_username, vid_name)
    ff = ffmpy.FFmpeg(
        inputs={m3u8_link: None},
        outputs={vid_path: "-c copy"}
    )

    if os.path.isdir(vids_preprocessed_dir) == False:
        os.mkdir(vids_preprocessed_dir)
    if os.path.isdir(model_path) == False:
        os.mkdir(model_path)

    thread_1 = threading.Thread(target=ff.run)
    thread_1.start()
    while not ff.process:
        sleep(600)
    ff.process.terminate()
    thread_1.join()


def model_list_grabber():
    """ask xhamsterlive.com which models are online (with all sorts of other data). 
    Is pre-configured to look for girls. tuple index: id, uname, 480p option"""

    url = "https://xhamsterlive.com/api/front/v2/models?topLimit=10000&primaryTag=girls"
    r = requests.get(url, stream=True)
    req = json.loads(r.content)
    models = req.get("blocks")[5].get("models")
    model_list_saver(models)
    models_online_resolution_option_480p = []

    for model in models:
        id = str(model.get("id"))
        if model.get("broadcastSettings").get("presets").get("testing") == None:
            resolution_option_480p = False
        else:
            resolution_option_480p = True
        uname = str(model.get("username"))
        models_online_resolution_option_480p.append(tuple([id, uname, resolution_option_480p]))
    
    return models_online_resolution_option_480p, models


def model_list_saver(model_list):
    """called to save API-data to create a cool dataset."""

    data_dump_dir = "data_dump"
    datetime_tag = datetime.now().strftime("%y%m%d_%H%M%S")
    json_file_name = f"{datetime_tag}.json"
    json_file_path = os.path.join(data_dump_dir, json_file_name)

    if os.path.isdir(data_dump_dir) == False:
        os.mkdir(data_dump_dir)
    with open(json_file_path, "w") as fp:
        json.dump(model_list, fp)


def stream_download_decider(all_model_names_480_option: tuple):
    """takes tuple of all models online with odel id, model uname and 480p option. Will 
decide according to models_followed.txt list rank which four models to record."""

    models_followed_online = []
    with open("models_followed.txt", "r") as f:
        for line in f.readlines():
            model_followed = line.replace("\n", "")
            for id_online, uname_online, option_480p_online in all_model_names_480_option:
                if model_followed == uname_online.lower():
                    models_followed_online.append(
                        tuple([id_online, uname_online, option_480p_online]))
    print(models_followed_online)

    return models_followed_online


def concurrent_stream_recording(models_online_followed: tuple):

    models_to_record = 8
    m3u8_links = []
    usernames = [x[1] for x in models_online_followed]

    for id, uname, option_480p in models_online_followed:
        if option_480p == True:
            m3u8_link = f"https://b-hls-01.strpst.com/hls/{id}/{id}_480p.m3u8"
            m3u8_links.append(m3u8_link)
        elif option_480p == False:
            m3u8_link = f"https://b-hls-01.strpst.com/hls/{id}/{id}.m3u8"
            m3u8_links.append(m3u8_link)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(m3u8_link_recorder,m3u8_links[:models_to_record], usernames[:models_to_record])


def video_stitcher():
    """invoke method for stitching together videos in each subdirectory of "vids_preprocessed"
-directory which is instatiated by m3u8_link_recorder"""

    veedos = "vids_preprocessed"
    subdirs = os.listdir(veedos)
    for subdir in subdirs:
        dir_and_subdir = "{}/{}".format(veedos, subdir)
        vids = os.listdir(dir_and_subdir)
        list_txt_dir = "{}/mylist.txt".format(dir_and_subdir)
        for vid in vids:
            vid_str = "\"file {}\"".format(vid)
            output_dir = "{}/output.mkv".format(dir_and_subdir)
            command_list = ["echo", vid_str, ">>", list_txt_dir]
            subprocess.run("echo {} >> {}".format(
                vid_str, list_txt_dir), shell=True)
        subprocess.run(
            "ffmpeg -f concat -safe 0 -i {} -c copy {}".format(list_txt_dir, output_dir), shell=True)
        for vid in vids:
            vid_dir = "{}/{}".format(dir_and_subdir, vid)
            subprocess.run("rm {}".format(vid_dir), shell=True)
        subprocess.run("rm {}".format(list_txt_dir), shell=True)


def model_surveillance_list_changer():
    """change list of models to surveil"""

    pass


"""DBs needed: model surveillance list/m3u8 links/surveillance on-off switch table, json 
response model lists, recorded videos, processed videos"""


def main():
    while True:
        for i in range(6):
            models_online, models = model_list_grabber()
            models_online_followed = stream_download_decider(models_online)
            concurrent_stream_recording(models_online_followed)
        video_stitcher()


if __name__ == "__main__":
    main()
