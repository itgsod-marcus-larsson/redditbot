from time import sleep
from datetime import datetime


class Throttle():

    def __init__(self, max_requests, timelimit_in_seconds):
        self.max_requests = max_requests
        self.tokens = max_requests
        self.timelimit = timelimit_in_seconds
        self.time_tokens_refilled = datetime.now()

    def request_allowed(self):
        self.refill_tokens()
        if self.tokens > 0:
            self.request_sent()
            return True
        else:
            sleep(3)
            print('Throttled')
            return False

    def request_sent(self):
        self.tokens -= 1

    def refill_tokens(self):
        time_now = datetime.now()
        if (time_now - self.time_tokens_refilled).total_seconds() > self.timelimit:
            self.tokens = self.max_requests
            self.time_tokens_refilled = datetime.now()