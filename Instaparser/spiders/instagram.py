import scrapy
from scrapy.http import HtmlResponse
from Instaparser.items import InstaparserItem
import re
import json
from urllib.parse import urlencode
from copy import deepcopy

class InstaSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    inst_login = '*'
    inst_pwd = '*'
    api_url = 'https://i.instagram.com/api/v1/friendships/'

    def __init__(self, query):
        super().__init__()
        self.user_for_parse = query

    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.login,
            formdata={'username': self.inst_login,
                      'enc_password': self.inst_pwd},
            headers={'x-csrftoken': csrf}
        )

    def login(self, response: HtmlResponse):
        j_data = response.json()
        if j_data['authenticated']:
            yield response.follow(
                f'/{self.user_for_parse}',
                callback=self.user_parse,
                cb_kwargs={'username': self.user_for_parse}
            )

    def user_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        params = {'count': 12, 'search_surface': 'follow_list_page'}

        url_followers = f'{self.api_url}{user_id}/followers/?{params}'
        yield response.follow(url_followers,
                              callback=self.user_followers_for_parse,
                              cb_kwargs={'username': username,
                                         'user_id': user_id})

    def user_followers_for_parse(self, response: HtmlResponse, username, user_id):
        j_data_followers = response.json()
        followers_list = []         #список подписчиков
        for user in j_data_followers.get('users'):
                followers_dict = {}
                followers_dict['follower_name'] = user.get('username')
                followers_dict['photo_follower'] = user.get('profile_pic_url')
                followers_dict['follower_id'] = user.get('pk')
                followers_list.append(followers_dict)

        params2 = {'count': 12}
        url_following = f'{self.api_url}{user_id}/following/?{params2}'

        yield response.follow(url_following,
                              callback=self.user_following_for_parse,
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         'params2': deepcopy(params2),
                                         'followers_list': followers_list})



    def user_following_for_parse(self, response: HtmlResponse, username, user_id, followers_list):
        j_data_following = response.json()
        following_list = []      #список подписок
        for user in j_data_following.get('users'):
            following_dict = {}
            following_dict['following_name'] = user.get('username')
            following_dict['photo_following'] = user.get('profile_pic_url')
            following_dict['following_id'] = user.get('pk')
            following_list.append(following_dict)

        item = InstaparserItem(
            user_id=user_id,
            username=username,
            followers_list=followers_list,
            following_list=following_list
            )
        yield item


    def fetch_csrf_token(self, text):
        '''Get csrf-token for auth'''
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')


    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')