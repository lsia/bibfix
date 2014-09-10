class months:
	def __init__(self):
		import os
		path=os.path.dirname(os.path.abspath(__file__))
		with open(path+'/months', 'r') as file:
			l=[e.strip() for e in file.readlines()]
		
		self.original=l[0:12]
		l2=l+[a[0:3] for a in l]
		self.words=[a.lower() for a in l2]
		self.lst=dict(zip(self.words,range(1,13)*(len(l2)/12)))

	def cmp(self,txt):
		import difflib
		m=difflib.get_close_matches(txt.lower(),self.words,1,0.8)
		if m:
			return self.original[self.lst[m[0]]-1]
		else:
			return None

