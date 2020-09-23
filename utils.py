import os, time

def log(text, verbosity=0):
	if verbosity > log.verbosity:
		return
	if not os.path.exists('logs'):
		os.makedirs('logs')
	if log.filename is None:
		date = time.strftime('%Y_%m_%d-%H_%M_%S')
		log.filename = f'logs/{date}.log'
	with open(log.filename, 'a+') as f:
		date = time.strftime('%m/%d/%Y %H:%M:%S')
		f.write(f'[{date}] {text}\n')
log.filename = None
log.verbosity = 0

def getWords():
	if getWords.words is None:
		with open('words.txt') as f:
			getWords.words = f.read().splitlines()
	return getWords.words
getWords.words = None