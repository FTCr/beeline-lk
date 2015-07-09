#!/usr/bin/env python3

import pycurl
from optparse import OptionParser
from io import BytesIO
from urllib.parse import urlencode
from html.parser import HTMLParser

class Parser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.__table = False
		self.__row = False
		self.__col = False
		self.__value = False
		self.__counter = 0

		self.__last_k = str()
		self.__last_v = str()
		self.__data = dict()

	def handle_starttag(self, tag, attrs):
		if not self.__table:
			if tag == 'table':
				for attr in attrs:
					if attr[0] == 'class' and attr[1] == 'personal_html_inner':
						self.__table = True
		else:
			if len(self.__data) < 6 and self.__counter < 2:
				if not self.__row:
					if tag == 'tr':
						self.__row = True
				else:
					if not self.__col:
						if tag == 'td':
							self.__col = True
					else:
						if tag == 'span':
							self.__value = True

	def handle_endtag(self, tag):
		if self.__table:
			if len(self.__data) < 6:
				if tag == 'table':
					self.__table = False
				elif tag == 'tr':
					self.__row = False
					self.__counter = 0
					self.__data.setdefault(self.__last_k, self.__last_v)
				elif tag == 'td':
					self.__col = False
				elif tag == 'span':
					self.__value = False

	def handle_data(self, data):
		if self.__value:
			if self.__counter == 0:
				self.__last_k = data
			elif self.__counter == 1:
				self.__last_v = data
			self.__counter += 1

	def get(self):
		return self.__data



class Beeline:
	def __init__(self):
		self.curl = pycurl.Curl()
		self.curl.setopt(pycurl.COOKIEFILE, "")
		self.curl.setopt(pycurl.HTTPHEADER, ['Host: lk.beeline.ru'])
		# self.curl.setopt(pycurl.VERBOSE, True)
		self.io = BytesIO()
		self.curl.setopt(pycurl.WRITEDATA, self.io)

	def login(self, username, password):
		self.curl.setopt(pycurl.URL, 'https://lk.beeline.ru')
		self.curl.setopt(pycurl.POST, True)

		params = {
			'login': username,
			'password': password,
		}
		params = urlencode(params)
		self.curl.setopt(pycurl.POSTFIELDS, params)
		self.curl.perform()

	def info(self):
		self.curl.setopt(pycurl.URL, 'https://lk.beeline.ru/personal/')
		self.curl.setopt(pycurl.POST, False)
		self.curl.perform()
		response = self.io.getvalue().decode('utf-8')
		parser = Parser()
		parser.feed(response)
		return parser.get()

if __name__ == '__main__':
	parser = OptionParser()
	parser.add_option('-u', '--username', type='string', default="")
	parser.add_option('-p', '--password', type='string', default="")

	(options, args) = parser.parse_args()
	options = options.__dict__
	username = options['username']
	password = options['password']

	if not username:
		username = input('Введи имя пользователя:')
	if not password:
		password = input('Введите пароль:')

	beeline = Beeline()
	beeline.login(username, password)
	info = beeline.info()
	if info:
		for k, v in info.items():
			print(k +': ', v)
	else:
		print('Не удалось получить информацию о счете')