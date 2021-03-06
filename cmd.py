import bibtool,string,json,re,pdfextract,os

PDF_PATH='library/%s.pdf'

class toolLayer():

	def getListFromSet(self,specialList,id):
		specialList=[a for a in specialList]
		specialList.sort()
		i=1
		aux=[]
		for a in specialList:
			aux.append(('%s%d'%(id,i),a))
			i=i+1
		return aux

	def __init__(self,file):
		self.bib=bibtool.bibtool(file)
		self.file=file
		self.rehash()

	def rollback(self):
		self.rehash()
		print "All changes undone"

	def rehash(self):
		self.authors=self.getListFromSet(self.bib.getAuthors(),'a')
		self.keywords=self.getListFromSet(self.bib.getKeywords(),'k')
		self.affiliations=self.getListFromSet(self.bib.getAffiliations(),'f')
		self.action_authors=[]
		self.action_keywords=[]
		self.action_titles=[]
		self.action_keys=[]

		self.action_add={}
	
		#print self.authors	
		#print self.keywords	

	def addkeyword(self,key,keyword):
		self.bib.addKeyword(key,keyword)

	def createPaper(self,key,fields):
		self.action_add[key]=fields

	def showkeywords(self):
		for keyword in self.keywords:
			print "%-7s: %s" % keyword
	
	def showaffiliations(self):
		for keyword in self.affiliations:
			print "%-7s: %s" % keyword

	def showauthors(self):
		for author in self.authors:
			print "%-7s: %s" % author
	
	def showtitles(self):
		self.bib.showEntries()

	def getkeys(self):
		return self.bib.getEntries()

	def suggestLanguage(self,key):
		sug=self.bib.suggestLanguage(key)
		paper_f=self.bib.get(key).fields
		current=paper_f['language'] if 'language' in paper_f else ''
		return (sug,current)

	def suggestMonth(self,key):
		sug=self.bib.suggestMonth(key)
		paper_f=self.bib.get(key).fields
		current=paper_f['month'] if 'month' in paper_f else None
		return (sug,current)

	def suggestWrongCaseKeywords(self):
		return [(kw,kwok) for (kw,kwok) in [(kw,toolLayer.title(kw)) for kw in self.bib.getKeywords()] if kw!=kwok]

	def suggestSimilarKeywords(self,factor=0.3):
		import distance
		kw=set(self.bib.getKeywords())
		result=[]
		while len(kw):
			k=kw.pop()
			result+=[(distance.nlevenshtein(k,v),v,k) for (n,v) in distance.ilevenshtein(k, kw, max_dist=int(len(k)*factor))]
		return sorted(result)
	
	def put(self,id,field,data):
		if ',' in id:
			ids=id.split(',')
			for id in ids:
				self.bib.set(id,field,data)
		else:
			self.bib.set(id,field,data)

	def get(self,id,field):
		data=self.bib.get(id).fields
		if field in data:
			return data[field]
		else:
			return None

	def showpaper(self,key):
		paper=self.bib.get(key)
		b=paper.fields
		try:
			print "* Authors:"
			for author in paper.persons["author"]:
				print " * %s" % unicode(author)
			for k in b:
				if k=='keywords':
					print "* Keywords:"
					for keyword in bibtool.bibtool.readKeywords(b[k]):
						print " * %s" % keyword
				else:
					print "* %s: %s" % (k,b[k])
				
		except(KeyError):
			print "Key error here (%s)" % k
		

	def fixkeywords(self,key,string):
		result=None
		for (k,v) in self.keywords:
			if k==key:
				result=v
		if not result:
			print "Error, key %s not found" % key
		line=(result,string)
		self.action_keywords.append(line)
		print "fix keyw %s -> %s" % line

	def renamekeywords(self,string1,string2):
		self.action_keywords.append((string1,string2))
	
	def fixauthors(self,key,string):
		result=None
		for (k,v) in self.authors:
			if k==key:
				result=v
		if not result:
			print "Error, key %s not found" % key
		line=(result,string)
		self.action_authors.append(line)
		print "fix auth %s -> %s" % line
	
	def fixtitles(self,key,string):
		line=(key,string)
		self.action_titles.append(line)
		print "fix title for %s -> %s" % line

	def fixkeys(self,key,keyto):
		line=(key,keyto)
		self.action_keys.append(line)
		print "fix key for %s -> %s" % line
	
	def cap_priv(self,key,callback,klist):
		result=None
		for (k,v) in klist:
			if k==key:
				result=v
		if not result:
			print "Error, key %s not found" % key
			return False
		return (result,callback(result))

	@staticmethod
	def title(text):
		return ' '.join([word.lower() if len(word)<3 else string.capwords(word) for word in text.split(" ")])

	def capkeywords(self,keys):
		for key in keys:
			s=key.split('-')
			if len(s)==2:
				(start,end)=s
				self.capkeywords(['k%d' % k for k in range(int(start[1:]),int(end))])
			else:
				line=self.cap_priv(key,toolLayer.title,self.keywords)
				#line=self.cap_priv(key,string.capwords,self.keywords)
				self.action_keywords.append(line)
				print "fix keyw %s -> %s" % line
	
	@staticmethod
	def capauth(text):
		for i in range(5):
			text=re.sub(r'^((.* )?)([A-Z])(( .*)?)$','\\1\\3.\\4',text)
		return string.capwords(text)

	def capauthors(self,key):
		line=self.cap_priv(key,toolLayer.capauth,self.authors)
		self.action_authors.append(line)
		print "fix auth %s -> %s" % line
	
	def save(self,file=None,fmt=None):
		self.bib.save(file or self.file,fmt)
	
	def status(self):
		for (fr,to) in self.action_authors:
			print "rename author %s to %s" % (fr,to)
		for (fr,to) in self.action_titles:
			print "rename paper %s to %s" % (fr,to)
		for (fr,to) in self.action_keywords:
			print "rename keyword %s to %s" % (fr,to)
		for (fr,to) in self.action_keys:
			print "rename key %s to %s" % (fr,to)

	def commit(self):
		for (fr,to) in self.action_authors:
			print "renaming author %s to %s" % (fr,to)
			self.bib.renameAuthor(fr,to)
		for (fr,to) in self.action_titles:
			self.bib.set(fr,'title',to)
			print "renaming paper %s to %s" % (fr,to)
		for (fr,to) in self.action_keywords:
			print "renaming keyword %s to %s" % (fr,to)
		self.bib.processKeywords(replace=self.action_keywords)
		for (fr,to) in self.action_keys:
			print "renaming key %s to %s" % (fr,to)
			try:
				os.rename(PDF_PATH%fr,PDF_PATH%to)
				print 'file renamed too'
			except:
				pass
			self.bib.renameKey(fr,to)
		for k,v in self.action_add.items():
			self.bib.addEntry(k,v)

		self.rehash()

	def check(self):
		exceptions={'online','misc'}
		e1=[]
		e2=[]
		for (key,author) in self.authors:
			if re.match(r'^.*[,] (.* )?[A-Za-z][.]?( .*)?$', author):
				if not re.match(r'^.*[,] (.* )?[A-Za-z][A-Za-z][A-Za-z]*( .*)?$', author):
					e1.append((key,author))
				else:
					e2.append((key,author))
		print "- Checking incomplete author names:"
		for v in e2:
			print ' * %-7s: %s' % v
		print "- Checking fully incomplete author names:"
		for v in e1:
			print ' * %-7s: %s' % v
		print "- Checking wrong article keys"
		data=self.bib.checkKeys()
		print "- The name does not comply with the standard"
		for bad_name in data['bad names']:
			print (' * %-7s: %s' % bad_name) + (' cmd: f p %s %s' % tuple(reversed(bad_name)))
		print "- Serialized in the wrong way"
		for (key,keylist) in data['bad_serial']:
			print ' * %-7s:' % key
			for d in keylist:
				print ('  * %-7s -> %s' % d) + (' cmd: f p %s %s' % d)
		print "- Bad titles"
		titles=self.bib.checkTitles()
		for key in titles:
			(v,wrong,right)=titles[key]
			print ' * %-7s: (%3.2f) %s -> %s' % (key,v,wrong,right)
		entries=sorted(self.bib.getEntries())
		for (field,check) in [('abstract',False),('language',True),('title',True),('keywords',False)]:
			print "- Missing %s" % field
			for id in entries:
				data=self.bib.get(id).fields
				if (check or not self.bib.get(id).type.lower() in exceptions) and not field in data: #if (I MUST check or not exception type) and the field does not exists
					print " * %s" % id
		p_bibtex=set(entries)
		p_pdf=set(pdfextract.getPapers())
		print "- Missing pdf"
		for id in sorted(p_bibtex-p_pdf):
			if not self.bib.get(id).type.lower() in exceptions:
				fatal='keywords' in self.bib.get(id).fields and 'lsia-' in self.bib.get(id).fields['keywords']
				print " * %s%s" % (id,'' if not fatal else ' !fatal')
		print "- Missing paper/unmatched pdf"
		for id in sorted(p_pdf-p_bibtex):
			print " * %s" % id
		errs=self.bib.checkDates()
		print "- Date errors"
		for (typ,msg,vals,k) in errs:
			print " * %s" % (msg % vals)
	
	def checkDates(self):
		return self.bib.checkDates()

	def suggestKeywords(self,key):
		sug=self.bib.suggestKeywords(key)
		result=[(k,sug[k]) for k in sug]
		result.sort(key=lambda tup: -tup[1])
		return result

#json
	def loadRules(self):
		fd = open("rules.json", "rt")
		self.rules=json.load(fd)
		fd.close()

	def saveRules(self):
		fd = open("rules.json", "wt")
		json.dump(self.rules,fd)
		fd.close()

	def showRules(self):
		for rule in self.rules:
			label=rules.pop('apply')
			print "* %-15s: %s"%(label,', '.join(["%s:%s"%(k,rule[k]) for k in rule]))

	def addRule(self,label,criteria):
		criteria['apply']=label
		self.rules.append(criteria)

	def delRule(self,label):
		self.rules=[rule for rule in self.rules if rule['apply']!=label]
		

#pdf

	def pdfGetAbstract(self,file,all=False):
		print pdfextract.getAbstract(PDF_PATH % file,all)

	def pdfFile(self,file):
		print pdfextract.fullFile(PDF_PATH % file)

	def pdfMetadata(self,file):
		meta=pdfextract.getMetadata(PDF_PATH % file)
		for k in meta:
			if k in ['keywords','Keywords']:
				print "* Keywords:"
				for keyword in bibtool.bibtool.readKeywords(meta[k]):
					print " * %s" % keyword
			else:
				print "* %s: %s" % (k,meta[k])

	def make(self):
		p_bibtex=set(self.bib.getEntries())
		p_pdf=set(pdfextract.getPapers())
		for id in p_bibtex & p_pdf:
			data=self.bib.get(id).fields
			if not 'url' in data:
				self.put(id,'url','http://lsia.fi.uba.ar/papers/%s.pdf' % id) #TODO: read from config/affiliation
			else:
				if not 'urllsia' in data and data['url']!='http://lsia.fi.uba.ar/papers/%s.pdf' % id:
					self.put(id,'urllsia','http://lsia.fi.uba.ar/papers/%s.pdf' % id)
