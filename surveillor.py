from time import sleep
import json
import subprocess
from datetime import datetime
import requests
import concurrent.futures



"""records video through m3u8 link. Is called by concurrent_stream_recording method to be executed once per m3u8 link in parallel."""


def m3u8_link_recorder(m3u8_link: str, model_username: str):
    tag = datetime.now().strftime("%y%m%d_%H%M%S")
    subprocess.run(["mkdir", "vids_preprocessed/{}".format(model_username)])
    subprocess.run(["ffmpeg", "-i", m3u8_link, "-c", "copy",
                   "vids_preprocessed/{}/{}.mkv".format(model_username, tag)])


"""this function is not needed anymore because the obligatory API-call that is needed to see which models are on-line
 gives enough information to deduct the m3u8-link"""


def m3u8_link_saver():
    pass


"""ask xhamsterlive.com which models are online (with all sorts of other data). Is pre-configured to look for girls."""


def model_list_grabber():
    url = "https://xhamsterlive.com/api/front/v2/models?topLimit=10000&primaryTag=girls"
    r = requests.get(url, stream=True)
    req = json.loads(r.content)
    models = req.get("blocks")[5].get("models")
    resolution_option_480p = []
    ids_online = []
    for model in models:
        ids_online.append(str(model.get("id")))
        if model.get("broadcastSettings").get("presets").get("testing") == None:
            resolution_option_480p.append(False)
        else:
            resolution_option_480p.append(True)

    models_online = dict(zip(ids_online, resolution_option_480p))

    return models_online, models


"""called to save API-data to create a cool dataset."""


def model_list_saver():
    pass


"""takes dict of all models online with model uname as key and model id as value. Will 
decide according to models_followed.txt list rank which four models to record"""


def stream_download_decider(all_model_names_480_option: dict, models: list):
    model_unames_online = []
    model_ids_online = []
    for model in models:
        model_unames_online.append(model.get("username"))
        model_ids_online.append(model.get("id"))

    models_unames_ids_dict = dict(zip(model_unames_online, model_ids_online))

    option_480p = []
    ids_followed_online = []
    with open("models_followed.txt", "r") as f:
        for line in f.readlines():
            model_followed = line.replace("\n", "")
            for i, model_online in enumerate(model_unames_online):
                if model_followed == model_online.lower():
                    option_480p.append(
                        all_model_names_480_option.get(str(model_ids_online[i])))
                    ids_followed_online.append(
                        models_unames_ids_dict.get(model_online))

    return models_unames_ids_dict, dict(zip(ids_followed_online, option_480p))


"""no need for m3u8_link_recorder here because takes dict straight away."""


def concurrent_stream_recording(usernames_ids_to_record, option_480p):
    models_to_record = 8
    usernames = list(usernames_ids_to_record.keys())
    ids = list(usernames_ids_to_record.values())
    m3u8_links = []
    for id in ids:
        for stream_option in list(option_480p.keys()):
            if stream_option == id:
                if option_480p.get(stream_option) == True:
                    m3u8_link = "https://b-hls-01.strpst.com/hls/{}/{}_480p.m3u8".format(
                        id, id)
                    m3u8_links.append(m3u8_link)
                elif option_480p.get(stream_option) == False:
                    m3u8_link = "https://b-hls-01.strpst.com/hls/{}/{}.m3u8".format(
                        id, id)
                    m3u8_links.append(m3u8_link)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(m3u8_link_recorder, m3u8_links[:models_to_record],
                     usernames[:models_to_record])


"""invoke method for stitching together videos in each subdirectory of "vids_preprocessed"
-directory which is instatiated by m3u8_link_recorder"""


def video_processor():
    pass


"""change list of models to surveil"""


def model_surveillance_list_changer():
    pass


"""DBs needed: model surveillance list/m3u8 links/surveillance on-off switch table, json 
response model lists, recorded videos, processed videos"""


def main():
    # pass
    while True:
        stuff1, stuff2 = model_list_grabber()
        stuff3, stuff4 = stream_download_decider(stuff1, stuff2)
        concurrent_stream_recording(stuff3, stuff4)
        sleep(600)


if __name__ == "__main__":
    main()


# add logging
