from miner import run_miner
import threading
import time

def run_miner_every_interval():
    run_miner()
    time.sleep(1000000)


miner_thread = threading.Timer(run_miner_every_interval)