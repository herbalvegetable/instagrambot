from instabot import Bot

import os
import shutil
from shutil import copyfile
from PIL import Image

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup as bs
import threading
import random
from decouple import config

print(os.getcwd())

def set_interval(func, sec):
    def func_wrapper():
    	set_interval(func, sec) 
    	func()  
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t
def init():
	try:
		shutil.rmtree('config')
		if not os.path.exists('media'): #create media dir if not exist
		    os.makedirs('media')
		else:
			for filename in os.listdir('./media'):
				os.remove(f'./media/{filename}')
	except:
		pass
init()

def renameMedia():
	for filename in os.listdir('./media'):
		if 'REMOVE_ME' in filename:
			name = '.'.join(filename.split('.')[:2])
			os.rename(f'./media/{filename}', f'./media/{name}')
renameMedia()

class InstaBot:
	def __init__(self, u, p):
		self.bot = Bot()
		self.username = u
		self.password = p
		self.bot.login(username=u, password=p)
	def upload(self, filename, caption):
		return self.bot.upload_photo(filename, caption=caption)

class Post:
	posts = []
	def scrape_reddit():
		url = 'https://www.reddit.com/r/memes/'
		chrome_options = Options()
		chrome_options.add_argument("--headless")
		driver = webdriver.Chrome('C:\\Users\\User\\Downloads\\chromedriver_win32\\chromedriver', options=chrome_options)
		driver.get(url)
		html = driver.page_source

		soup = bs(html, 'html.parser')

		posts = soup.find_all('div', {'class', 'Post'})
		for post in posts:
			if len(post.find_all('span', {'class': 'rewiG9XNj_xqkQDcyR88j'})) > 0: continue; # check for posts pinned by moderators
			p = {}
			
			try:
				p['title'] = post.find('h3').get_text()
				p['filename'] = f"./media/{''.join([str(random.randint(0, 9)) for i in range(10)])}.jpg"
			except:
				pass
			try:
				p['src'] = post.find('img', {'alt': 'Post image'}).get('src')
			except:
				pass
			try:
				p['op'] = post.find('a', {'class', '_2tbHP6ZydRpjI44J3syuqC'}).get_text()
			except:
				pass
			Post.posts.append(p)
			print('\n')

		print(Post.posts)
		print(len(Post.posts))
		driver.close()
	post_sizes = [
		[1080, 1080],
		[1080, 608],
		[1080, 1350],
	]
	def download_posts():
		for post in Post.posts:
			try:
				r = requests.get(post['src'], stream=True)
				r.raw.decode_content = True
				with open(post['filename'], 'wb') as f:
					shutil.copyfileobj(r.raw, f)
			except:
				print('Image source not found.')
	def upload_posts(bot):
		# Resize img if aspect ratio not compatible
		# https://stackoverflow.com/questions/65609981/python-instabot-error-photo-does-not-have-a-compatible-photo-aspect-ratio
		for post in Post.posts:
			try:
				caption = f'{post["title"]}\n\nPosted by: {post["op"]}\n\nSubreddit: r/memes'
				if not bot.upload(post['filename'], caption):
					with Image.open(post['filename']) as im:
						im.resize([1080, 1080]).convert("RGB").save(post['filename'])
					bot.upload(post['filename'], caption)
			except Exception as e:
				print(e)

Post.scrape_reddit()

Post.download_posts()

bot = InstaBot(config('ACC_USERNAME'), config('ACC_PASSWORD'))

Post.upload_posts(bot)

renameMedia()

