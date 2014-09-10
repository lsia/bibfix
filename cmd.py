import bibtool,string,json,re,pdfextract,os

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
	
		#print self.authors	
		#print self.keywords	

	def addkeyword(self,key,keyword):
		self.bib.addKeyword(key,keyword)

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
	
	def put(self,id,field,data):
		if ',' in id:
			ids=id.split(',')
			for id in ids:
				self.bib.set(id,field,data)
		else:
			self.bib.set(id,field,data)

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

	def capkeywords(self,keys):
		for key in keys:
			s=key.split('-')
			if len(s)==2:
				(start,end)=s
				self.capkeywords(['k%d' % k for k in range(int(start[1:]),int(end))])
			else:
				line=self.cap_priv(key,string.capwords,self.keywords)
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
	
	def save(self):
		self.bib.save(self.file)
	
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
			self.bib.renameKey(fr,to)
		self.rehash()

	def check(self):
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
			print ' * %-7s: %s' % bad_name
		print "- Serialized in the wrong way"
		for (key,keylist) in data['bad_serial']:
			print ' * %-7s:' % key
			for d in keylist:
				print '  * %-7s -> %s' % d
		print "- Bad titles"
		titles=self.bib.checkTitles()
		for key in titles:
			(v,wrong,right)=titles[key]
			print ' * %-7s: (%3.2f) %s -> %s' % (key,v,wrong,right)
		entries=self.bib.getEntries()
		for k in ['abstract','language','title','keywords']:
			print "- Missing %s" % k
			for id in entries:
				data=self.bib.get(id).fields
				if not k in data:
					print " * %s" % id
	
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
		print pdfextract.getAbstract('pdf/%s.pdf' % file,all)

	def pdfFile(self,file):
		print pdfextract.fullFile('pdf/%s.pdf' % file)

	def pdfMetadata(self,file):
		meta=pdfextract.getMetadata('pdf/%s.pdf' % file)
		for k in meta:
			if k in ['keywords','Keywords']:
				print "* Keywords:"
				for keyword in bibtool.bibtool.readKeywords(meta[k]):
					print " * %s" % keyword
			else:
				print "* %s: %s" % (k,meta[k])

#affiliations. TODO: move to pdfextract
	def make(self):
		entries=self.bib.getEntries()
		for id in entries:
			data=self.bib.get(id).fields
			try:
				afs=bibtool.bibtool.readKeywords(data['affiliations'])
			except(KeyError):
				afs=[]
			for af in afs:
				print id,af
				#if file exists
				if not os.path.exists("affiliations/%s" % af):
					os.makedirs("affiliations/%s" % af)
				#cp "pdf/%s.pdf" % id , "affiliations/%s/%s.pdf" % (af,id)
				#TODO: process pdf and metadata
				if not 'url' in data:
					self.put(id,'url','http://lsia.fi.uba.ar/papers/%s.pdf' % id) #TODO: read from config/affiliation

