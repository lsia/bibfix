#!/usr/bin/python
import cmd, sys
file=sys.argv[1]

tl=cmd.toolLayer(file)

def showhelp():
	print "Commands"
	print "s[how] (k[eywords]|a[uthors]|t[itles]|p[aper] (id)|f)  - Show stuff"
	print "f[ix] (k[eyword]|a[uthor]|t[itle]|p[aper]) (id) (text) - Fix stuff. Reeplace with '.' to delete"
	#print "m[atch] (keyword regexp) (text)          - Fix matched keyword"
	print "p[ut] (id) (field) (raw data)                          - set data or delete field if raw data empty (commited instantly)"
	print "(suggest|sg) (id)                                      - Suggest keywords"
	print "(suglang|sl)                                           - Suggest language"
	print "(sugmonth|sm)                                          - Suggest month"
	print "c[heck]                                                - Integrity Check"
	print "st[atus]                                               - Check Status"
	print "(i|commit)                                             - Commit Changes"
	print "r[ollback]                                             - Undo unocmmited changes"
	print "s[ave]                                                 - Saves %s" % file
	print "(P|pdf) (a[bstarct]|f[ull]|m[eta]) (id)                - Show the contents of the paper"
	print "(capitalize|C) (k[eyword]|a[uthor]|t[itle]) (id)       - CAPITALIZE FIRST WORD -> Capitalize First Word"
	print "make                                                   - Copies pdf papers to public directory"

stay=True
while stay:
	args=raw_input('? ').split(' ')
	if args[0]=='exit' or args[0]=='q' or args[0]=='x':
		stay=False
	elif args[0]=='suggest' or args[0]=='sg':
		tl.showpaper(args[1])
		for (k,w) in tl.suggestKeywords(args[1])[0:6]:
			ask=raw_input("Accept suggested keyword '%s' (%d) in this paper? [Yes/No/Cancel] "%(k,w))
			if (ask=='y'):
				print "adding %s to %s" % (k,args[1])
				tl.addkeyword(args[1],k)
			elif (ask=='c'):
				break
	elif args[0]=='suglang' or args[0]=='sl':
		for k in tl.getkeys():
			(sug,cur)=tl.suggestLanguage(k)
			if (sug!=cur):
				if cur=='':
					ask=raw_input("Accept suggested language '%s' in paper %s? [Yes/No/Cancel] "%(sug,k))
				else:
					ask=raw_input("Accept to change suggested language '%s' to '%s' in paper %s? [Yes/No/Cancel] "%(cur,sug,k))
				if (ask=='y'):
					print "setting lang %s to %s" % (sug,k)
					tl.put(k,'language',sug)
				elif (ask=='c'):
					break
	elif args[0]=='sugmonth' or args[0]=='sm':
		for k in tl.getkeys():
			(sug,cur)=tl.suggestMonth(k)
			if (sug!=cur and sug):
				ask=raw_input("Accept to change suggested month '%s' to '%s' in paper %s? [Yes/No/Cancel] "%(cur,sug,k))
				if (ask=='y'):
					print "setting lang %s to %s" % (sug,k)
					tl.put(k,'month',sug)
				elif (ask=='c'):
					break
	elif args[0]=='sugdate' or args[0]=='sd': #TODO
		errs=tl.checkDates()
		for (typ,msg,vals,k) in errs:
			print "Error found: %s" % (msg % vals)
			toShow=['date','day','month','year']
			current=[]
			for field in ['date','day','month','year']:
				v=tl.get(k,field)
				current.append(v!=None)
				if v:
					print " - %s: %s" % (field,v)
				else:
					print " - %s missing" % field
			current=tuple(current)
			if typ=='fix':
				if current==(False,True,True,True):
					(k,y,m,d)=vals
					newDate="%s-%02d-%s" % (y,m,d)
					ask=raw_input("Accept to change 'day=%s' to 'date=%s' in paper %s? [Yes/No/Cancel] "%(d,newDate,k))
					if (ask=='y'):
						print "unsetting day"
						tl.put(k,'day',None)
						print "setting date to %s" % newDate
						tl.put(k,'date',newDate)
					elif (ask=='c'):
						break
	elif args[0]=='help' or args[0]=='?'  or args[0]=='h':
		showhelp()
	elif args[0]=='show' or args[0]=='s':
		try:
			if args[1]=='keywords' or args[1]=='k':
				tl.showkeywords()
			elif args[1]=='authors' or args[1]=='a':
				tl.showauthors()
			elif args[1]=='affiliation' or args[1]=='f':
				tl.showaffiliations()
			elif args[1]=='titles' or args[1]=='t':
				tl.showtitles()
			elif args[1]=='paper' or args[1]=='p':
				tl.showpaper(args[2])
			else:
				raise IndexError
		except IndexError:
			print "I don't know how to show %s. try show keywords|authors|titles|paper id" % ' '.join(args)
	elif args[0]=='fix' or args[0]=='f':
		if args[1]=='keyword' or args[1]=='k':
			tl.fixkeywords(args[2],' '.join(args[3:]).decode('utf-8'))
		elif args[1]=='author' or args[1]=='a':
			tl.fixauthors(args[2],' '.join(args[3:]).decode('utf-8'))
		elif args[1]=='title' or args[1]=='t':
			tl.fixtitles(args[2],' '.join(args[3:]).decode('utf-8'))
		elif args[1]=='paper' or args[1]=='p':
			tl.fixkeys(args[2],args[3])
		else:
			print "I don't know how to fix %s. try fix keyword|author|title" % args[1]
	elif args[0]=='capitalize' or args[0]=='C':
		if args[1]=='keyword' or args[1]=='k':
			tl.capkeywords(args[2:])
		elif args[1]=='author' or args[1]=='a':
			tl.capauthors(args[2])
		elif args[1]=='title' or args[1]=='t':
			tl.captitles(args[2])
		else:
			print "I don't know how to cap %s. try capitalize keyword|author|title" % args[1]
	elif args[0]=='pdf' or args[0]=='P':
		if args[1]=='abstract' or args[1]=='a':
			all=False
			try:
				if args[2]=='a':
					all=True
			except Error:
				pass
			tl.pdfGetAbstract(args[2],all)
		elif args[1]=='full' or args[1]=='f':
			tl.pdfFile(args[2])
		elif args[1]=='meta' or args[1]=='m':
			tl.pdfMetadata(args[2])
		else:
			print "I don't know how to pdf %s. try help" % args[1]
	elif args[0]=='put' or args[0]=='p':
		tl.put(args[1],args[2],' '.join(args[3:]).decode('utf-8'))
	elif args[0]=='save' or args[0]=='s':
		tl.save()
	elif args[0]=='commit' or args[0]=='ci' or args[0]=='i':
		tl.commit()
	elif args[0]=='status' or args[0]=='st':
		tl.status()
	elif args[0]=='rollback' or args[0]=='r':
		tl.rollback()
	elif args[0]=='check' or args[0]=='c':
		tl.check()
	elif args[0]=='make' or args[0]=='m':
		tl.make()
	elif args[0]=='':
		print "Type 'help' for commands"
	else:
		print "Unsupported command %s" % args[0]
	

print "bye"
