from pybtex.database.input import bibtex as bibtexin
import re,datetime
from pybtex.database.output import bibtex as bibtexout
from pybtex.core import Person
from pybtex.utils import OrderedCaseInsensitiveDict
from pybtex.database import Entry
import io
import difflib,string
#pybtex.core.Person
import months

class bibtool:
	def __init__(self,file):
		#open a bibtex file
		parser = bibtexin.Parser()
		self.bibdata = parser.parse_file(file) #"../plan.bib")
		self.months=months.months()

	def showEntries(self):
		aux=[]
		for bib_id in self.bibdata.entries:
			try:
				aux.append("%-10s: %s" % (bib_id,self.bibdata.entries[bib_id].fields['title']))
			except(KeyError):
				aux.append("%s-> ERROR: fix missing title" % (bib_id))
		aux.sort()
		for line in aux:
			print line

	def getAuthors(self):
		authors=set()
		for bib_id in self.bibdata.entries:
			b=self.bibdata.entries[bib_id]
			try:
				#authors=authors|set([unicode(p) for p in b.persons["author"]])
				for person in b.persons["author"]:
					authors=authors|set([unicode(person)])
			except(KeyError):
				continue
		return authors

	def addEntry(self,k,v):
		p={}
		for pf in ['author','editor']:
			if pf in v:
				p[pf]=[Person(aux) for aux in v[pf].split(';')]
				del v[pf]
		self.bibdata.add_entry(k,Entry(k, fields=v, persons=p))

	def renameAuthor(self,old,target):
		old=Person(old)
		target=Person(target)

		for bib_id in self.bibdata.entries:
			b=self.bibdata.entries[bib_id]
			try:
				if old in b.persons["author"]:
					b.persons["author"]=[target if p==old else p for p in b.persons["author"]]
			except(KeyError):
				continue
		
	def get(self,key):
		return self.bibdata.entries[key]

	def set(self,key,kid,val):
		if (val!='' and val!=None):
			self.bibdata.entries[key].fields[kid]=val
		else:
			del self.bibdata.entries[key].fields[kid]

	def checkAuthors(self):
		authors=self.getAuthors()
		print "Checking incomplete names:"
		for author in authors:
			if re.match(r'^(.* )?[A-Za-z][.]?( .*)?$', author):
				print '* %s' % author

	def showAuthors(self):
		authors=[a for a in self.getAuthors()]
		authors.sort()
		for author in authors:
			print author

	def suggestLanguage(self,key):
		fields=self.bibdata.entries[key].fields
		checkfrom=['title','abstract']
		import langid
		(lang,val)=langid.classify(' '.join([fields[ty] if ty in fields else '' for ty in checkfrom]))
		return lang

	def suggestMonth(self,key,number=False):
		fields=self.bibdata.entries[key].fields
		if 'month' in fields:
			return self.months.cmp_number(fields['month']) if number else self.months.cmp(fields['month'])
		return None

	@staticmethod
	def readKeywords(string):
		return [kw for kw in string.replace(';',',').replace(':',',').replace(', ',',').split(',') if kw[0:5]!='lsia-']

	def addKeyword(self,key,keyword):
		old=self.bibdata.entries[key].fields['keywords']
		self.bibdata.entries[key].fields['keywords']="%s, %s" % (old,keyword)

	def getKeywords(self):
		keywords=set()
		for bib_id in self.bibdata.entries:
			try:
				keywords=keywords|set(bibtool.readKeywords(self.bibdata.entries[bib_id].fields['keywords']))
			except(KeyError):
				continue
		return keywords

	def getAffiliations(self): #TODO: common factor here
		keywords=set()
		for bib_id in self.bibdata.entries:
			try:
				keywords=keywords|set(bibtool.readKeywords(self.bibdata.entries[bib_id].fields['affiliations']))
			except(KeyError):
				continue
		return keywords

	def processKeywords(self,rules=[],replace=[]):
		if not rules:
			rules=[
				{'author':Person('Calot, Enrique P.'),'apply':'author-ecalot'},
				{'author':Person('Merlino, Hernan'),'apply':'author-hmerlino'},
				{'author':Person('Ierache, Jorge Salvador'),'apply':'author-jierache'},
				{'author':Person('Pirra, Francisco'),'apply':'author-fpirra'},
				{'author':Person('Rodriguez, Juan Manuel'),'apply':'author-jmrodriguez'},
				{'author':Person('Liguori, Ariel'),'apply':'author-aliguori'},
				{'author':Person("Gonz{\\'a}lez, Nahuel"),'apply':'author-ngonzalez'}
			]
		for bib_id in self.bibdata.entries:
			try:
				#self.bibdata.entries[bib_id].fields['keywords']=k
				keywords=bibtool.readKeywords(self.bibdata.entries[bib_id].fields['keywords'])
				for rule in rules:
					if 'author' in rule:
						if rule['author'] in self.bibdata.entries[bib_id].persons["author"]:
							keywords.append('lsia-'+rule['apply'])
					#TODO...
				for (f,t) in replace:
					keywords=[t if keyword==f else keyword for keyword in keywords]
				keywords=[k for k in set(keywords) if k!='.']
				keywords.sort()
				self.bibdata.entries[bib_id].fields['keywords']=', '.join(keywords)
			except(KeyError):
				continue
		





	def showKeywords(self):
		keywords=[a for a in self.getKeywords()]
		keywords.sort()
		for keyword in keywords:
			print keyword

	@staticmethod
	def formatConvert(text,frm,to):
		import pypandoc
		return pypandoc.convert(text,to,format=frm)

	def save(self,file,fmt):
		#TODO: perform conversion using fmt
		#print file,fmt
		#for bib_id in self.bibdata.entries:
		#	for f_id in self.bibdata.entries[bib_id].fields:
		#		v=self.bibdata.entries[bib_id].fields[f_id]
		#		print "-----"
		#		print bib_id,f_id
		#		print v
		#		print bibtool.formatConvert(v,'latex','plain')
		
		#return
		writer=bibtexout.Writer()
		stream=io.open(file, mode='w')
		writer.write_stream(self.bibdata, stream)

	def checkKeys(self):
		result={}
		for bib_id in self.bibdata.entries:
			b = self.bibdata.entries[bib_id].fields
			try:
				au=re.sub('[^a-z]', '',''.join(self.bibdata.entries[bib_id].persons["author"][0].last()).lower())
				yr=b['year'][2:]
				key=au+yr
				if key in result:
					result[key].append(bib_id)
				else:
					result[key]=[bib_id]
			except(KeyError):
				print "Author/year missing: %s" % bib_id
		bad_name=[]
		bad_serial=[]
		for key in result:
			papers=result[key]
			if len(papers)!=1:
				papers.sort()
				error=[]
				start=ord('a')
				for key2 in papers:
					c=chr(start) if start!=ord('a') else ''
					if key2!=(key+c):
						error.append((key2,key+c))
					start=start+1
				if error:
					bad_serial.append((key,error))
			else:
				if key!=papers[0]:
					bad_name.append((key,papers[0]))
		return {'bad names':bad_name,'bad_serial':bad_serial}

	def checkTitles(self):
		result={}
		for bib_id in self.bibdata.entries:
			b = self.bibdata.entries[bib_id].fields
			try:
				tit=b['title']
				uptit=tit.upper()
				ratio=difflib.SequenceMatcher(None, tit,uptit).ratio()
				if ratio>0.7:
					result[bib_id]=(ratio,tit,string.capwords(tit))
			except(KeyError):
				print "Missing title: %s" % bib_id
		return result

	def checkDates(self):
		result=[]
		for bib_id in self.bibdata.entries:
			b = self.bibdata.entries[bib_id].fields
			if 'date' in b:
				try:
					c=datetime.datetime.strptime(b['date'], "%Y-%m-%d")
					for checking in ['year','month']: #,'day']:
						if not checking in b:
							result.append(('missing',"Missing %s for %s, should be %d", (checking,bib_id,getattr(c,checking)),bib_id))
				except:
					result.append(('wrong',"Wrong date for %s: %s" , (bib_id,b['date']),bib_id))
			else:
				if 'day' in b:
					m=self.suggestMonth(bib_id,True)
					result.append(('fix',"Missing date for %s, but day is present: %s-%02d-%s" , (bib_id,b['year'] if 'year' in b else 'error', m or 0, b['day']),bib_id))
		return result

	def renameKey(self,oldKey,newKey):
		self.bibdata.entries=OrderedCaseInsensitiveDict([(k if k!=oldKey else newKey,v) for (k,v) in self.bibdata.entries.items()])

	def capitalizeTitle(self,key):
		b = self.bibdata.entries[key].fields
		try:
			b['title']=string.capwords(b['title'])
			return b['title']
		except(KeyError):
			print "Missing title"

	def isAuthor(self,key,author):
		try:
			for a in self.bibdata.entries[key].persons["author"]:
				if unicode(a)==unicode(author):
					return True
		except(KeyError):
			pass
		return False

	def getEntries(self):
		return self.bibdata.entries.keys()

	def suggestKeywords(self,key):
		b=self.bibdata.entries[key]
		keywords=set(bibtool.readKeywords(b.fields['keywords']))
		try:
			authors=set([unicode(person) for person in b.persons["author"]])
	
			#Check the papers and add 1 to their keywords for each matching author
			suggestions={}
			for bib_id in self.bibdata.entries:
				val=0
				try:
					paperKeys=bibtool.readKeywords(self.bibdata.entries[bib_id].fields['keywords'])
				except(KeyError):
					paperKeys=[]
				for a in authors:
					if self.isAuthor(bib_id,a):
						val=val+1
				for k in keywords:
					if k in paperKeys:
						val=val+1
				if val:
					for paperKey in paperKeys:
						if paperKey in suggestions:
							suggestions[paperKey]+=val
						else:
							suggestions[paperKey]=val
			for k in keywords:
				if k in suggestions:
					del suggestions[k]
			return suggestions
		except(KeyError):
			print "Key Error"
		

#
##loop through the individual references
#for bib_id in bibdata.entries:
#	b = bibdata.entries[bib_id].fields
#	try:
#		# change these lines to create a SQL insert
#		#print b
#		print b["title"]
#		#print b["journal"]
#		#print b["year"]
#		#deal with multiple authors
#		#for author in bibdata.entries[bib_id].persons["author"]:
#		#	print author
#		#	print author.first(), author.last()
#	# field may not exist for a reference
#	except(KeyError):
#		continue
#

