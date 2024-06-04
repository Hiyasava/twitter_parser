import twitter_scraper
import sched
import time
import argparse

from RabbitThread import RabbitThread
from multiprocessing import Queue
from database import db
from datetime import datetime, timedelta

class Main():

    def __init__(self) -> None:
        self.q = Queue()
        self.db = db()

        self.rabbit = RabbitThread()
        self.rabbit.start_process(self.q)

        
    
    def start(self):
        usernames_ = self.db.usernames()
        usernames = [item[0] for item in usernames_]

        for username in usernames:
            twitter_scraper.main(username=username, limit=100, q=self.q)


    def latest_date(self):
        dates = self.db.GetLastWorkTime()

        dates = [item[0] for item in dates]


        date_times = [datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f") for date in dates]

        latest = max(date_times)

        return latest

    def start_scheduler(self, delay):
        start_time = self.latest_date()

        scheduler = sched.scheduler(time.time, time.sleep)

        delay = timedelta(minutes=delay).total_seconds()
        target_time = (start_time + timedelta(seconds=delay)).timestamp()

        scheduler.enterabs(target_time, 1, self.start, ())

        scheduler.run()


if __name__ == '__main__':

    argparser = argparse.ArgumentParser()
    argparser.add_argument('--delay', '-d', type=int, required=False, help='delay for scheduler in minutes', default=15)
    args = argparser.parse_args()
    delay = args.delay

    main = Main()
    main.start()
    while True:
        main.start_scheduler(delay)
