from miner import run_miner
import threading
import time

# settings
uris = ["https://news.ycombinator.com/rss", "http://feeds.bbci.co.uk/news/technology/rss.xml?edition=uk"]
miner_name = "RSS miner one: BBC and Hacker News"
engine_uri = "http://localhost:4000/"
interval = 10 # in seconds

def run_miner_every_interval():
    while True:
        run_miner(miner_name, uris, engine_uri)
        time.sleep(interval)


miner_thread = threading.Thread(target=run_miner_every_interval)
miner_thread.start()