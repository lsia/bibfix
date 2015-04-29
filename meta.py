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

def showMetas(url):
	soup = BeautifulSoup(urllib.urlopen(url))
	for z in [(tag.get('name'),tag.get('content')) for tag in soup.find_all('meta')]:
		print "-----------------\n%s: %s\n" % z
	


def analyzeMetas():
	urls={
		'SeDiCi':'http://sedici.unlp.edu.ar/handle/10915/32428',
		'SpringerLink':'http://link.springer.com/chapter/10.1007/978-0-387-09695-7_16',
		'ieee Xplore':'http://ieeexplore.ieee.org/xpl/articleDetails.jsp?arnumber=5329098',
		'Journal generico con DOI 1':'http://www.ccsenet.org/journal/index.php/cis/article/view/15766',
		'Journal generico con DOI 2':'http://www.nejm.org/doi/full/10.1056/NEJMoa1404505',
		'ScienceDirect':'http://www.sciencedirect.com/science/article/pii/S0378113505001112',
		'nature':('/tmp/nature.html',u'Esta URL no es accesible por m\xe9todos automatizables como CURL debido a una protecci\xf3n de hotlink, sin embargo funciona con plugins del browser o mintiendo en los headers HTTP: \\url{http://www.nature.com/nature/journal/vaop/ncurrent/full/nature14442.html}'.encode('utf-8')),
		'Biblioteca Digital FCEN-UBA':'http://digital.bl.fcen.uba.ar/gsdl-282/cgi-bin/library.cgi?a=d&c=publicaciones/exactamente&d=003_Exactamente_048',
		'Scielo':'http://www.scielo.org.ar/scielo.php?script=sci_arttext&pid=S1668-70272011000200004&lng=es&nrm=iso',
		'arXiv.org':'http://arxiv.org/abs/astro-ph/0612749',
		'ACM Digital Library':'http://dl.acm.org/citation.cfm?doid=2370216.2370414',
		'Journal generico con DOI 3':'http://www.j-biomed-inform.com/article/S1532-0464(08)00013-0/abstract',
		'Biblioteca Digital UCA':'http://bibliotecadigital.uca.edu.ar/greenstone/cgi-bin/library.cgi?a=d&c=investigacion&d=24-hour-rhythm-gene-expression'
	}
	result=[]
	empty=[]
	all_tags=set()
	for name in sorted(urls.keys()):
		url=urls[name]
		if type(url)==type((1,2)):
			(gurl,url)=url
		else:
			gurl=url
			url='URL: \\url{%s}' % url
		#print name,url
		soup = BeautifulSoup(urllib.urlopen(gurl))
		s=set([tag.get('name').encode('utf8').replace('-', '_') for tag in soup.find_all('meta') if tag.get('name')])
		tag_count=len(s)
		if tag_count:
			result.append({
				'tags':s,
				'name':name,
				'url':url,
				'tag_count':tag_count
			})
			all_tags=all_tags | s
		else:
			empty.append({
				'name':name,
				'url':url,
			})
	#print result
	#print "tags"
	#print all_tags
	print '\\begin{longtable}[c]{|l|%s|}' % '|'.join(['c']*len(result))
	all_tags_count=len(all_tags)
	print '\\toprule'
	print 'Repositorio ',
	for z in result:
		print '& \\begin{sideways}%s\\end{sideways}' % z['name'],
	print '\\\\\n\\midrule'
	print '\\endhead'
	print '\\caption{Comparacion de tags meta entre varios sitios}'
	print '\\endlastfoot'
	print '\\hline'
	for tag in sorted(all_tags):
		print '\\verb!%s! ' % tag,
		for z in result:
			print '& %s ' % ('\\checkmark' if tag in z['tags'] else ''),
		print '\\\\\n\\hline'
	print '\\midrule'
	print 'Meta-tags totales',
	for z in result:
		print '& %d' % z['tag_count'],
	print '\\\\\n',
	print '\\midrule'
	print 'Meta-tags en $\%$',
	for z in result:
		print '& %d ' % (100*z['tag_count']/all_tags_count),
	print '\\\\\n',
	print '\\bottomrule'
	print '\\end{longtable}'
	print u'Los sitios evaluados que no utilizaron tags meta son %s. Mientras que los sitios que s\xed lo hicieron fueron %s.\\'.encode('utf8') % (
		', '.join(['%s\\footnote{%s}' % (z['name'],z['url']) for z in empty]),
		', '.join(['%s\\footnote{%s}' % (z['name'],z['url']) for z in result])
	)


#for url in ['http://sedici.unlp.edu.ar/handle/10915/19798','http://link.springer.com/chapter/10.1007/978-0-387-09695-7_16','http://ieeexplore.ieee.org/xpl/articleDetails.jsp?arnumber=5329098']:
#	print "**************************\n* %s\n**************************" % url
#	result=read(url)
#	for k,v in result.items():
#		print "* %s: %s"% (k,';'.join(v))
