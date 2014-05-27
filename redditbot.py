import requests
import json
from time import sleep
from throttle import Throttle


class Bot(object):

    def __init__(self, throttle, username, password):
        self.subreddit = 'http://www.reddit.com/r/probot2k14/'
        self.throttle = throttle
        self.username = username
        self.password = password
        self.user_cred_dict = {'user': self.username, 'passwd': self.password, 'api_type': 'json'}
        self.headers = {'user-agent': '/u/itg_probot\'s python API test'}
        self.client = requests.session()
        self.client.headers = self.headers
        self.updated_fullnames = []
        self.old_fullnames = self.read_old_fullnames()

    def read_old_fullnames(self):
        """Reads link fullnames from last loop cycle from file to a list"""

        with open('fullnames.txt') as f:
            return f.readlines()

    def login(self):
        """Login and retrieve a modhash"""

        if self.throttle.request_allowed():
            login_response = self.client.post('http://www.reddit.com/api/login', data=self.user_cred_dict)
            print('Logged in')
        else:
            self.login()

        # set modhash as header
        self.client.headers['X-Modhash'] = login_response.json()['json']['data']['modhash']

    def post_comment(self, thing_id, text):
        comment_data = {'thing_id': thing_id, 'text': text, 'api_type': 'json'}
        self.comment_response = self.client.post('http://www.reddit.com/api/comment', params=comment_data)

        # only continue if response is good
        if self.comment_response.status_code != 200:
            self.post_comment(thing_id, text)
        print('comment posted')

    def get_new_links(self):
        """Gets the 25 newest links in specified subreddit and creates a lists of link fullnames"""

        request_data = {'api_type': 'json'}
        if self.throttle.request_allowed():
            new_links = self.client.get(self.subreddit + 'new.json', data=request_data).json()['data']['children']
        else:
            self.get_new_links()
        self.updated_fullnames = []
        for new_link_info_list in new_links:
            self.updated_fullnames.append((new_link_info_list['data']['name']))
        self.compare_fullnames()

    def compare_fullnames(self):
        """Compare updated and non-updated link fullnames"""

        self.read_old_fullnames()
        for fullname in self.updated_fullnames:
            if fullname + '\n' in self.old_fullnames:
                print('fullname already in list')
                sleep(1)
            else:
                print('fullname not in list')
                if self.throttle.request_allowed():
                    self.post_comment(fullname, '### BONY KNEES ###')

                    # only add fullname to fullname file if not affected by ratelimit
                    if 'ratelimit' not in json.loads(self.comment_response.content.decode('utf8'))['json']:
                        self.add_fullname_to_old_fullnames_file(fullname)
                    sleep(1)
                else:
                    self.get_new_links()

    def add_fullname_to_old_fullnames_file(self, fullname):
        """Prints link fullnames of current loop cycle to a file"""

        with open("fullnames.txt", "a") as fullnames_file:
            fullnames_file.write(fullname + '\n')


request_limit = 30
throttle = Throttle(request_limit, 60)

while True:
    bot = Bot(throttle, "itg_probot", "itg_probot")
    bot.login()
    bot.get_new_links()
