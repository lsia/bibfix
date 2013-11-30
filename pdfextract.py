import subprocess,re,json

def getPipe(file):
	return subprocess.Popen("pdftotext %s -|iconv -f 'latin1' -t 'utf8'" % file, shell=True, stdout=subprocess.PIPE).stdout

def getExifPipe(file):
	return subprocess.Popen("exiftool %s -json|iconv -f 'latin1' -t 'utf8'" % file, shell=True, stdout=subprocess.PIPE).stdout

def processPdf(file,regexp,all=False):
	pipe = getPipe(file)
	next=False
	result=[]
	for line in pipe.readlines():
		if re.match(regexp,line):
			next=True
		if re.match(r"^[\n\r ]*$",line) and not all:
			next=False
		if next:
			result.append(line)
	pipe.close()
	return "\n".join(result)

def fullFile(file):
	pipe = getPipe(file)
	out="\n".join(pipe.readlines())
	pipe.close()
	return out

def getAbstract(file,all=False):
	return processPdf(file,r"([aA][bB][sS][tT][rR][aA][cC][tT]|[rR]esumen)",all)

def getMetadata(file):
	pipe=getExifPipe(file)
	result=json.load(pipe)
	pipe.close()
	return result[0]

#print processPdf(sys.argv[1],r"([aA][bB][sS][tT][rR][aA][cC][tT]|[rR]esumen)")
#print processPdf(sys.argv[1],r"(eference|ibliogra|EFEREN|IBLIOGRA)")

