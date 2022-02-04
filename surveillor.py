#! /usr/bin/env python

import concurrent.futures
import json
import os
import sys
import threading
from datetime import datetime
from time import sleep
import logging

import ffmpy
import requests


def logit(message: str):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler("surveil.log")
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.info(f"{datetime_tag()}: {message}")


def datetime_tag():
    return datetime.now().strftime("%y%m%d_%H%M%S")


def m3u8_link_recorder(m3u8_link: str, model_username: str, sleep_time: int):
    """records video through m3u8 link. Is called by concurrent_stream_recording 
    method to be executed once per m3u8 link in parallel.
    """

    vids_preprocessed_dir = "vids_preprocessed"
    model_path = os.path.join(vids_preprocessed_dir, model_username)
    vid_name = f"{datetime_tag()}.mkv"
    vid_path = os.path.join(vids_preprocessed_dir, model_username, vid_name)
    ff = ffmpy.FFmpeg(
        inputs={m3u8_link: None},
        outputs={vid_path: "-c copy"}
    )

    if not os.path.isdir(vids_preprocessed_dir):
        os.mkdir(vids_preprocessed_dir)
    if not os.path.isdir(model_path):
        os.mkdir(model_path)

    logit(f"{model_username} is being recorded")

    thread_1 = threading.Thread(target=ff.run)
    thread_1.start()
    while not ff.process:
        sleep(sleep_time)
    ff.process.terminate()
    thread_1.join()

    logit(f"{model_username} recording stopped")


def model_list_grabber():
    """ask xhamsterlive.com which models are online (with all sorts of other data). 
    tuple index: id, uname, 480p option
    """

    url = "https://xhamsterlive.com/api/front/v2/models?topLimit=10000"
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
        models_online_resolution_option_480p.append(
            tuple([id, uname, resolution_option_480p]))


    return models_online_resolution_option_480p, models


def model_list_saver(model_list):
    """called to save API-data to create a cool dataset.
    """

    data_dump_dir = "data_dump"
    json_file_name = f"{datetime_tag()}.json"
    json_file_path = os.path.join(data_dump_dir, json_file_name)

    if not os.path.isdir(data_dump_dir):
        os.mkdir(data_dump_dir)
    with open(json_file_path, "w") as fp:
        json.dump(model_list, fp)


def stream_download_decider(all_model_names_480_option: tuple):
    """takes tuple of all models online with odel id, model uname and 480p option. Will 
    decide according to models_followed.txt list rank which four models to record.
    """

    models_followed_online = []
    if len(sys.argv) == 1:
        with open("models_followed.txt", "r") as f:
            for line in f.readlines():
                model_followed = line.replace("\n", "")
                for id_online, uname_online, option_480p_online in all_model_names_480_option:
                    if model_followed == uname_online.lower():
                        models_followed_online.append(
                            tuple([id_online, uname_online, option_480p_online]))
    else:
        models_followed = sys.argv[1:]
        for model_followed in models_followed:
            for id_online, uname_online, option_480p_online in all_model_names_480_option:
                if model_followed == uname_online.lower():
                    models_followed_online.append(
                        tuple([id_online, uname_online, option_480p_online]))
    if len(models_followed_online) > 0:
        print(models_followed_online)
        
    elif len(models_followed_online) == 0:
        print("none of your models are online")

    return models_followed_online


def concurrent_stream_recording(models_online_followed: tuple, sleep_time: int, models_to_record: int):
    """Invokes concurrent library.
    """

    m3u8_links = []
    usernames = [x[1] for x in models_online_followed]

    for id, uname, option_480p in models_online_followed:
        if option_480p:
            m3u8_link = f"https://b-hls-01.strpst.com/hls/{id}/{id}_480p.m3u8"
            m3u8_links.append(m3u8_link)
        elif not option_480p:
            m3u8_link = f"https://b-hls-01.strpst.com/hls/{id}/{id}.m3u8"
            m3u8_links.append(m3u8_link)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(m3u8_link_recorder,
                     m3u8_links[:models_to_record], usernames[:models_to_record], [sleep_time] * models_to_record)


def video_stitcher():
    """invoke method for stitching together videos in each subdirectory of "vids_preprocessed"
    -directory which is instatiated by m3u8_link_recorder
    """

    vids_preprocessed_dir = "vids_preprocessed"
    subdirs = os.listdir(vids_preprocessed_dir)

    logit(f"video_stitcher started")

    for subdir in subdirs:
        dir_and_subdir = os.path.join(vids_preprocessed_dir, subdir)
        if len(os.listdir(dir_and_subdir)) > 1:
            vids = os.listdir(dir_and_subdir)
            list_txt_dir = os.path.join(dir_and_subdir, "my_list.txt")
            output_dir = os.path.join(
                dir_and_subdir, f"concat_{datetime_tag()}.mkv")

            dict_ = dict(zip([int(''.join((x.split('_')[-2], x.split('_')[-1].replace('.mkv', '')))) for x in vids], [x for x in vids]))
            vids_sorted = list(dict(sorted(dict_.items())).values())
            with open(list_txt_dir, "w") as fp:
                for vid in vids_sorted:
                    vid_str = f"file {vid}\n"
                    fp.writelines(vid_str)

            ff = ffmpy.FFmpeg(
                global_options={"-f concat -safe 0"},
                inputs={list_txt_dir: None},
                outputs={output_dir: "-c copy"}
            )
            ff.run()

            for vid in vids:
                vid_dir = os.path.join(dir_and_subdir, vid)
                os.remove(vid_dir)
            os.remove(list_txt_dir)
            logit(f"video_stitcher concatenated {subdir}")


def main():
    while True:
        for i in range(3):
            models_online, models = model_list_grabber()
            logit(f"{len(models_online)} followed models are online")
            models_online_followed = stream_download_decider(models_online)
            logit(f"{len(models_online_followed)} followed models are online")
            concurrent_stream_recording(models_online_followed, 150, 8)
        video_stitcher()


if __name__ == "__main__":
    main()
