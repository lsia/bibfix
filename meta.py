from bs4 import BeautifulSoup
import urllib

def read(url):
	soup = BeautifulSoup(urllib.urlopen(url))
	repl=dict([
		('DC.creator','$author'),
		('DC.date','date'),
		('DC.description','description'),
		('DC.identifier','identifier'),
		('DC.language','language'),
		('DC.rights','rights'),
		('DC.subject','*keywords'),
		('DC.title','title'),
		('DC.type','type'),
		('DCTERMS.abstract','abstract'),
		('DCTERMS.extent','pages'),
		('DCTERMS.isPartOf','partof'),
		('DCTERMS.issued','year'),
		('DCTERMS.license','license'),
		('author','author'),
		('citation_abstract_html_url','url'),
		('citation_author','*author'),
		#('citation_author_email','author_email'),
		#('citation_author_institution','author_institution'),
		('citation_conference','conference'),
		('citation_conference_title','conference'),
		('citation_date','date'),
		('citation_doi','doi'),
		('citation_firstpage','firstpage'),
		('citation_inbook_title','inbook_title'),
		('citation_isbn','isbn'),
		('citation_keywords','keywords'),
		('citation_language','language'),
		('citation_lastpage','lastpage'),
		('citation_pdf_url','pdf_url'),
		('citation_publication_date','date'),
		('citation_publisher','publisher'),
		('citation_title','title'),
		('citation_volume','volume')
	])
	aux={}
	out=[]
	for (k,v) in [(repl[tag.get('name')],tag.get('content')) for tag in soup.find_all('meta') if tag.get('name') in repl]:
		if k[0] in ['$','*']:
			if not k in aux:
				aux[k]=v
			else:
				aux[k]="%s; %s" % (aux[k],v)
		else:
			if v!='':
				out.append((k,v))
	aux2={}
	for (k,v) in out+[(k[1:] if k[0] in ['$','*'] else k,v) for k,v in aux.items() if v!='']:
		if not k in aux2:
			aux2[k]=[v]
		else:
			aux2[k].append(v)
	return aux2

	


#for url in ['http://sedici.unlp.edu.ar/handle/10915/19798','http://link.springer.com/chapter/10.1007/978-0-387-09695-7_16','http://ieeexplore.ieee.org/xpl/articleDetails.jsp?arnumber=5329098']:
#	print "**************************\n* %s\n**************************" % url
#	result=read(url)
#	for k,v in result.items():
#		print "* %s: %s"% (k,';'.join(v))
