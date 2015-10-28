from miner import run_miner
import threading
import time

# settings
uris = ["https://news.ycombinator.com/rss", "http://feeds.bbci.co.uk/news/technology/rss.xml?edition=uk"]
miner_name = "RSS miner one: BBC and Hacker News"
engine_uri = "http://localhost:4000/"

def run_miner_every_interval():
    run_miner(miner_name, uris, engine_uri)
    time.sleep(100000)


miner_thread = threading.Timer(run_miner_every_interval)