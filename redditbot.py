import requests
import json
from time import sleep
from throttle import Throttle


class Bot(object):

    def __init__(self, throttle, username, password):
        self.subreddit = 'http://www.reddit.com/r/movies/'
        self.throttle = throttle
        self.username = username
        self.password = password
        self.user_cred_dict = {'user': self.username, 'passwd': self.password, 'api_type': 'json'}
        self.headers = {'user-agent': '/u/itg_probot\'s python API test'}
        self.client = requests.session()
        self.client.headers = self.headers
        self.updated_fullnames = []
        self.link_titles = []
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
            return

        # set modhash as header
        self.client.headers['X-Modhash'] = login_response.json()['json']['data']['modhash']

    def post_comment(self, thing_id, text):
        comment_data = {'thing_id': thing_id, 'text': text, 'api_type': 'json'}
        self.comment_response = self.client.post('http://www.reddit.com/api/comment', params=comment_data)

        # only continue if response is good
        if self.comment_response.status_code != 200:
            self.post_comment(thing_id, text)

    def get_new_links(self):
        """Gets the 25 newest links in specified subreddit and creates a lists of link fullnames"""

        request_data = {'api_type': 'json'}
        if self.throttle.request_allowed():
            new_links = self.client.get(self.subreddit + 'new.json', data=request_data).json()['data']['children']
        else:
            return
        self.updated_fullnames = []
        for new_link_info_list in new_links:
            self.updated_fullnames.append((new_link_info_list['data']['name']))
            self.link_titles.append((new_link_info_list['data']['title']))
        self.compare_fullnames()

    def compare_fullnames(self):
        """Compare updated and non-updated link fullnames"""

        self.read_old_fullnames()
        for fullname in self.updated_fullnames:
            if fullname + '\n' in self.old_fullnames:
                print('fullname already in list')
                sleep(2)
            else:
                print('fullname not in list')
                if self.throttle.request_allowed():
                    current_link_title = self.link_titles[self.updated_fullnames.index(fullname)]
                    if 'nicolas cage' in current_link_title:
                        self.post_comment(fullname, '**This thread could use a dose of The Cage \n [All hail The Cage](http://i.imgur.com/EXikTLC.png)**')

                        # only add fullname to fullname file if not affected by ratelimit
                        if 'ratelimit' not in json.loads(self.comment_response.content.decode('utf8'))['json']:
                            self.add_fullname_to_old_fullnames_file(fullname)
                            print('comment posted')
                            sleep(2)
                        else:
                            print('ratelimit')
                            sleep(2)
                    else:
                        self.add_fullname_to_old_fullnames_file(fullname)
                        print('link name does not contain correct string')
                        sleep(2)
                else:
                    return

    def add_fullname_to_old_fullnames_file(self, fullname):
        """Writes link fullnames of current loop cycle to a file"""

        with open("fullnames.txt", "a") as fullnames_file:
            fullnames_file.write(fullname + '\n')


request_limit = 30
throttle = Throttle(request_limit, 60)

while True:
    bot = Bot(throttle, "cage_bot", "cage_bot")
    bot.login()
    bot.get_new_links()
