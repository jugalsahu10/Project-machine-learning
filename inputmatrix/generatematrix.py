try:
    import json
except ImportError:
    import simplejson as json
# import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
import string
import re
import xlrd
from pprint import pprint
import re

matrix = {}

def get_config(configfile):
	config = []
	try:
		File = open(configfile,'r')
		config = json.load(File)
	except Exception as e:
		print(str(e))
	else:
		File.close()
	return config

def getwords(config):
	words = {}
	try:
		File = open(config["words"],'r')
		words = json.load(File)
	except Exception as e:
		print("config catch : "+str(e))
	else:
		File.close()
	return words

def getjds(config):
	jds =[]
	for jd in config["jds"]:
		try:
			File = open(jd,'r')
			jds.append(json.load(File))
		except Exception as e:
			print("jds catch : "+str(e))
		else:
			File.close()
	return jds

def process_txts(config, words, jd):
	filenames = []
	try:
		File = open(config['txts_filename'],'r')
		filenames = File.read().split('\n')
		genMatrix(filenames)
		if len(filenames)>0:	
			for txtfile in filenames:
				features = get_features(config, txtfile, words, jd)
				update_matrix(config, features, txtfile)
			print('** all files processed **')
		else:
			print('** no txt files in txts_filename **')
	except Exception as e:
		print('** Process catch **'+str(e))
		# print(e.)
	else:
		File.close()
		return filenames

def get_features(config, txtfile, words, jd):
	row = {}
	row = extractfeaturescore_words(config,txtfile,words, row)
	row = extractfeaturescore_jd(config, txtfile, jd, row)
	row = extractfeaturescore_companies(config, txtfile, row)
	row = extractfeaturescore_target(config, txtfile, row)
	return row

def extractfeaturescore_words(config,txtfile,words, row):
	File = open(config['txts_folder']+txtfile,'r')
	txt = File.read()
	File.close()
	punctuation = list(string.punctuation)
	stop_words = set(stopwords.words('english') + punctuation)
	word_tokens = []

	try:
		word_tokens = word_tokenize(txt)
	except Exception as e:
		print("\n\n"+txtfile+" and error: "+str(e))

	filtered_txt = [w for w in word_tokens if not w in stop_words]
	for cat in words:
		acc = 0
		for word in words[cat]:
			if word in filtered_txt:
				acc +=1
		row[cat] = acc
	return row

def wordtokenize(jd):
	word_tokens = []
	try:
		word_tokens = word_tokenize(jd)
	except Exception as e:
		print("\n\n"+txtfile+" jd c ++++++ and error: "+str(e))
	return word_tokens

def senttokenize(txt):
	sents = []
	try:
		sents = sent_tokenize(txt)
	except Exception as e:
		print("\n\n"+txtfile+" sents ****** and error: "+str(e))
	return sents

def counter(jddict, word):
	count = 0
	for wrd in jddict:
				if wrd == word:
					count +=1
	return count

def extractfeaturescore_jd(config, txtfile, jd, row):
	File = open(config['txts_folder']+txtfile,'r')
	txt = File.read()
	File.close()

	punctuation = list(string.punctuation)
	stop_words = set(stopwords.words('english') + punctuation)
	
	sents = []
	sents = senttokenize(txt)

	word_tokens = []
	jddict ={}

	c_feature = senttokenize(jd["c_feature"])
	# c_feature = wordtokenize(jd["c_feature"])
	# c_feature = [w for w in c_feature if not w in stop_words]
	jddict['c_feature'] = c_feature

	Technical = senttokenize(jd["Technical"])
	# Technical = wordtokenize(jd["Technical"])
	# Technical = [w for w in Technical if not w in stop_words]
	jddict['Technical'] = Technical

	Role = senttokenize(jd["Role"])
	# Role = wordtokenize(jd["Role"])
	# Role = [w for w in Role if not w in stop_words]
	jddict['Role'] = Role

	c_count = 0
	r_count = 0
	t_count = 0

	for sent1 in sents:
		word1 = wordtokenize(sent1)
		word1 = [w for w in word1 if not w in stop_words]

		for sent2 in c_feature:
			word2 = wordtokenize(sent2)
			word2 = [w for w in word2 if not w in stop_words]
			s = 0
			for w1 in word1:
				for w2 in word2:
					if w1 == w2:
						s+=1
						break
				else:
					continue  # executed if the loop ended normally (no break)
				break					
			if s > 0:
				c_count+=1

		for sent2 in Technical:
			word2 = wordtokenize(sent2)
			word2 = [w for w in word2 if not w in stop_words]
			s = 0
			for w1 in word1:
				for w2 in word2:
					if w1 == w2:
						s+=1
						break
				else:
					continue  # executed if the loop ended normally (no break)
				break						
			if s > 0:
				t_count+=1

		for sent2 in Role:
			word2 = wordtokenize(sent2)
			word2 = [w for w in word2 if not w in stop_words]
			s = 0
			for w1 in word1:
				for w2 in word2:
					if w1 == w2:
						s+=1
						break
				else:
					continue  # executed if the loop ended normally (no break)
				break
			if s > 0:
				r_count+=1		
	row['c_count'] = (c_count/ (len(sents) * 1.0)) if len(sents) > 0 else c_count
	row['r_count'] = (r_count/ (len(sents) * 1.0)) if len(sents) > 0 else r_count
	row['t_count'] = (t_count/ (len(sents) * 1.0)) if len(sents) > 0 else t_count
	return row

def extractfeaturescore_companies(config, txtfile, row):
	companies = []
	words = []
	with open(config['companies'], 'r') as f:
		for line in f:
			for word in line.split():
				companies.append(word.lower())

	file = open(config['txts_folder']+txtfile, 'r')
	text = file.read().lower()
	file.close()
	text = re.sub('[^a-z\ \']+', " ", text)
	words = list(text.split())

	cmpscore = 0.0
	cmplen = len(companies)
	for i in range(cmplen):
		if companies[i] in words:
			cmpscore += cmplen-i+1
	row['cmp_score'] = cmpscore
	return row

details = {}
def getdetail():
	cnt = 0
	workbook = xlrd.open_workbook(config['details'])
	sheet_names = workbook.sheet_names()
	sheet = workbook.sheet_by_name(sheet_names[0])
	for row_idx in range(sheet.nrows):
		detail = []
		for col_idx in range(sheet.ncols):
			cell = sheet.cell(row_idx, col_idx)
			detail.append(cell.value)
		details[cnt] = detail
		cnt += 1
	sheet = workbook.sheet_by_name(sheet_names[1])
	for row_idx in range(sheet.nrows):
		detail = []
		for col_idx in range(sheet.ncols):
			cell = sheet.cell(row_idx, col_idx)
			detail.append(cell.value)
		details[cnt] = detail
		cnt += 1

def extractfeaturescore_target(config, txtfile, row):
	accept = ['Joined', 'OfferAccepted']
	cnt = 0
	row['target'] = -1
	txtfile = re.sub('[^a-zA-Z0-9]', '',txtfile[:-4])
	for detail in details:
		tstr8 = re.sub('[^a-zA-Z0-9]', '',details[detail][8])
		tstr6 = re.sub('[^a-zA-Z0-9]', '',details[detail][6])
		# print(txtfile)
		if txtfile==tstr8:
			# print('file1:'+txtfile)
			# print('file2:'+tstr8)
			if tstr6 in accept:
				# print(details[detail])
				row['target'] = 1
				row['experience'] = details[detail][4]
				row['testscore'] = details[detail][5]
			else:
				# print(details[detail])
				row['target'] = 0
				row['experience'] = details[detail][4]
				row['testscore'] = details[detail][5]
			break
	return row


def genMatrix(filenames):
	global matrix
	for file in filenames:
		matrix[file]=[]

def update_matrix(config,features, txtfile):
	global matrix
	matrix[txtfile] = features
	return

def dump_matrix():
	global matrix
	file = open(config['matrix'],"w")
	json.dump(matrix, file)
	file.close()

def test():
	filenames = process_txts(config,words,jds[0])


config = get_config('config.json')
words = getwords(config)
jds = getjds(config)
getdetail()

test()


count = 0
for file in matrix:
	if count ==0:
		print([tag for tag in matrix[file]])
	print([matrix[file][tag] for tag in matrix[file]])
	count+=1

dump_matrix()
# print(count+1)












