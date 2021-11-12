from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import json
from collections import Counter
import subprocess
from datetime import datetime
import requests
import concurrent.futures

"""copypasta from a blog that shows how to extract network events from webdriver in python. 
Currently cannot find link but need to add in future"""


def process_browser_logs_for_network_events(logs):
    asdf = []
    for entry in logs:
        log = json.loads(entry["message"])["message"]
        try:
            if (
                ".m3u8" in log["params"]["response"]["url"]
            ):
                asdf.append(str(log["params"]["response"]["url"]))
        except Exception:
            continue
    return asdf


"""gets m3u8 link from model_username which is part of the url that selenium will call
to extract and return m3u8_link. In further actions m3u8_link will be saved in 
m3u8_dictionary"""


def m3u8_link_grabber(model_username: str):
    url = "https://xhamsterlive.com/{}".format(model_username)

    # initialising webdriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("window-size=1400,900")
    chrome_options.add_argument("--mute-audio")
    capabilities = DesiredCapabilities.CHROME.copy()
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
    driver = webdriver.Chrome(
        "./chromedriver",
        desired_capabilities=capabilities,
        options=chrome_options
    )

    # get to stream by clicking away landing widget, and changing streaming-protocol
    url = "https://xhamsterlive.com/{}".format(model_username)
    driver.get(url)
    sleep(1)
    btn_box = driver.find_element(By.CLASS_NAME, "content-container")
    btn_box.find_element(By.TAG_NAME, "button").click()
    sleep(2)
    options_button = driver.find_element(By.CLASS_NAME, "controls-low-latency")
    hover = ActionChains(driver).move_to_element(options_button).click()
    hover.perform()
    sleep(2)
    driver.find_element(By.CLASS_NAME, "switcher-label").click()
    sleep(6)

    # record network traffic and extract m3u8 out
    logs = driver.get_log("performance")

    try:
        events = process_browser_logs_for_network_events(logs)
        event, freq = Counter(events).most_common(1)[0]
        print("found {} for {}".format(event, model_username))
    except Exception as e:
        print("m3u8_link_grabber cannot extract event from network logs: " + str(e))

    # finish off
    driver.close()
    return event


# gets m3u8_link to record stream. This try-except decider doesn't seem to work.
def m3u8_link_recorder(m3u8_link: str, model_username: str, m3u8_link_alternative: str):
    try:
        tag = datetime.now().strftime("%y%m%d_%H%M%S")
        subprocess.run(
            ["mkdir", "vids_preprocessed/{}".format(model_username)])
        subprocess.run(["ffmpeg", "-i", m3u8_link, "-c", "copy",
                       "vids_preprocessed/{}/{}.mkv".format(model_username, tag)])
        sleep(5)
    except subprocess.CalledProcessError as e:
        print(model_username + e)
        tag = datetime.now().strftime("%y%m%d_%H%M%S")
        subprocess.run(
            ["mkdir", "vids_preprocessed/{}".format(model_username)])
        subprocess.run(["ffmpeg", "-i", m3u8_link_alternative, "-c", "copy",
                       "vids_preprocessed/{}/{}.mkv".format(model_username, tag)])
        sleep(5)


def m3u8_link_saver():
    pass

# ask xhamsterlive.com which models are online (with all sorts of other data)


def model_list_grabber():
    url = "https://xhamsterlive.com/api/front/v2/models?topLimit=10000&primaryTag=girls"
    r = requests.get(url, stream=True)
    req = json.loads(r.content)
    models = req.get("blocks")[5].get("models")
    unames_online = []
    ids_online = []
    for model in models:
        unames_online.append(model.get("username"))
        ids_online.append(str(model.get("id")))

    models_online = dict(zip(unames_online, ids_online))

    return models_online


def model_list_saver():
    pass


"""takes dict of all models online with model uname as key and model id as value. Will 
decide according to models_followed.txt list rank which four models to record"""


def stream_download_decider(all_model_names_ids: dict):
    models_followed_online = []
    ids_followed_online = []
    with open("models_followed.txt", "r") as f:
        for line in f.readlines():
            model_followed = line.replace("\n", "")
            for model_online in all_model_names_ids.keys():
                if model_followed == model_online.lower():
                    models_followed_online.append(model_followed)
                    ids_followed_online.append(
                        all_model_names_ids.get(model_online))

    print(dict(zip(models_followed_online, ids_followed_online)))
    return dict(zip(models_followed_online, ids_followed_online))


"""no need for m3u8_link_recorder here because takes dict straight away."""


def concurrent_stream_recording(usernames_ids_to_record):
    models_to_record = 8
    usernames = list(usernames_ids_to_record.keys())
    ids = list(usernames_ids_to_record.values())
    m3u8_links = []
    m3u8_links_alternative = []
    for id in ids:
        m3u8_link = "https://b-hls-01.strpst.com/hls/{}/{}_480p.m3u8".format(
            id, id)
        m3u8_links.append(m3u8_link)
        m3u8_link_alternative = "https://b-hls-01.strpst.com/hls/{}/{}.m3u8".format(
            id, id)
        m3u8_links_alternative.append(m3u8_link_alternative)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(m3u8_link_recorder, m3u8_links[:models_to_record],
                     usernames[:models_to_record], m3u8_links_alternative[:models_to_record])


"""invoke method for stitching together videos in each subdirectory of "vids_preprocessed"
-directory which is instatiated by m3u8_link_recorder"""


def video_processor():
    pass


def model_surveillance_list_changer():
    pass


"""DBs needed: model surveillance list/m3u8 links/surveillance on-off switch table, json 
response model lists, recorded videos, processed videos"""


def main():
    # pass
    while True:
        concurrent_stream_recording(
            stream_download_decider(model_list_grabber()))
        sleep(600)


if __name__ == "__main__":
    main()


# add logging
