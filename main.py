from miner import run_miner
import threading
import time
import yaml

def load_settings():
    settings_file = open('settings.yaml')
    s = yaml.safe_load(settings_file)
    settings_file.close()
    return s['uris'], s['miner_name'], s['engine_uri'], s['interval']


uris, miner_name, engine_uri, interval = load_settings()


def run_miner_every_interval():
    while True:
        run_miner(miner_name, uris, engine_uri)
        time.sleep(interval)


miner_thread = threading.Thread(target=run_miner_every_interval)
miner_thread.start()