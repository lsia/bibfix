import urllib2
from pybtex.database.input import bibtex as bibtexin

def getDOIUrl(doi_url):
	return urllib2.urlopen(urllib2.Request(doi_url,headers={"Accept" : "application/x-bibtex;q=1.0"}))

def getISBN(isbn):
	return urllib2.urlopen('http://manas.tungare.name/software/isbn-to-bibtex/isbn-service?isbn=%s'%isbn)

def getDOI(doi):
	try:
		return getDOIUrl("http://dx.doi.org/%s"%doi)
	except urllib2.HTTPError:
		return None

def getBib(stream):
	if not stream:
		return None
	parser = bibtexin.Parser(encoding='UTF8')
	return parser.parse_stream(stream)


#bibdata= getBib(getDOI('10.1007/978-0-387-09695-7_16'))
#bibdata= getBib(getISBN('9783659033940'))
#bibdata= getBib(getDOIUrl('http://dx.doi.org/10.1007/978-0-387-09695-7_16'))
bibdata= getBib(getDOIUrl('http://www.dblp.org/rec/bibtex/conf/ifip12/CalotBG08'))

if bibdata:
	for bib_id in bibdata.entries:
		b = bibdata.entries[bib_id].fields
		try:
			# change these lines to create a SQL insert
			print b["title"]
			print b["journal"]
			print b["year"]
			#deal with multiple authors
			for author in bibdata.entries[bib_id].persons["author"]:
				print author.first(), author.last()
		# field may not exist for a reference
		except(KeyError):
			continue

