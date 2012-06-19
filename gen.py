#/usr/bin/env jython

'''
Created on May 29, 2012

@author: andrzej&artur
'''

from random import seed
from random import randint
from random import randrange
from random import choice
import random,sys

class app(object):
	def __init__(self,i,us,g_s,r_s,t,pr):
		self.ind=i
		self.user=us
		self.gen_s=g_s
		self.read_s=r_s
		self.time=t
		self.prior=pr
		
class drive(object):
	def __init__(self,i,r_s,w_s,siz):
		self.ind=i
		self.read_s=r_s
		self.write_s=w_s
		self.size=siz
		
class user(object):
	def __init__(self,i,prof,r_s,w_s,sec,acc,pr):
		self.ind=i
		self.profile=prof
		self.read_s=r_s
		self.write_s=w_s
		self.secur=sec
		self.access=acc
		self.prior=pr

def dodaj1(tekst,doilu):
	for i in xrange(doilu):
		tekst+=str(i+1)
		tekst+=' '
	return tekst

def generuj(numapps,numdrives,numusers):
	tekst='set apps := '
	tekst=dodaj1(tekst,numapps)
	tekst+=';\nset drives := '
	tekst=dodaj1(tekst,numdrives)
	tekst+=';\nset users := '
	tekst=dodaj1(tekst,numusers)
	tekst+=''';\nset app_params := user gen read time prior;
set user_params := profile read write security access priority;
set drive_params := read_s write_s size;
param applications :
	user gen read time prior :=
'''
	apps=[]
	drives=[]
	users=[]
	
	for i in range(1,numapps+1):
		a=app(str(i),randint(1,numusers),randrange(50,500,10),randrange(50,500,10),randint(1,30),0)
		apps.append(a)
		
	ap2=range(numapps)
	iloraz=numapps//numdrives
	for i in range(1,numdrives):
		il=randint(iloraz-1,iloraz+1)
		apps2=[]
		for j in range(il):
			if len(ap2) > 0:
				k=choice(ap2)
				ap2.remove(k)
				apps2.append(k)
		if len(apps2) > 0:	
			m_w=[apps[a].gen_s for a in apps2]
			m_s=[apps[a].gen_s*apps[a].time for a in apps2]
			m_r=[apps[a].read_s for a in apps2]
			r=max(m_r)
			w=max(m_w)
			s=sum(m_s,0)
			d=drive(str(i),r,w,s)
			drives.append(d)
		else:
			d=drive(str(numdrives),randrange(50,500,10),randrange(50,500,10),randrange(5000,10000,1000))
			drives.append(d)
	if len(ap2) > 0:
		m_w=[apps[a].gen_s for a in ap2]
		m_s=[apps[a].gen_s*apps[a].time for a in ap2]
		m_r=[apps[a].read_s for a in ap2]
		r=max(m_r)
		w=max(m_w)
		s=sum(m_s,0)
		d=drive(str(numdrives),r,w,s)
		drives.append(d)
	else:
		d=drive(str(numdrives),randrange(50,500,10),randrange(50,500,10),randrange(5000,10000,1000))
		drives.append(d)
		
	for i in range(1,numusers+1):
		a=filter(lambda x: i==x.user,apps)
		pr=randint(1,3)
		for ap in a:
			ap.prior=pr
		u=user(str(i),randint(1,3),reduce(lambda x,y: x+y.read_s,a,0),reduce(lambda x,y: x+y.gen_s,a,0),randint(1,3),randint(1,2),pr)
		users.append(u)
		
	for a in apps:
		tekst+=a.ind+' '+str(a.user)+' '+str(a.gen_s)+' '+str(a.read_s)+' '+str(a.time)+' '+str(a.prior)+'\n'
	tekst+=';\nparam phys_drives :\n\tread_s write_s size :=\n'
	for d in drives:
		tekst+=d.ind+' '+str(d.read_s)+' '+str(d.write_s)+' '+str(d.size)+' '+'\n'
	tekst+=';\nparam sys_users :\n\tprofile read write security access priority :=\n'
	for u in users:
		tekst+=u.ind+' '+str(u.profile)+' '+str(u.read_s)+' '+str(u.write_s)+' '+str(u.secur)+' '+str(u.access)+' '+str(u.prior)+'\n'

	f=open("./wynik.dat", 'w+')
	f.write(tekst)
	f.close()		
	return (apps,drives,users)

def readFile(fileName):
	f=open(fileName,"r")
	apps=[]
	drives=[]
	users=[]
	file=""
	for line in f:
		file+=line
	sets=file.split(";")
	f.close()
	
	ap=sets[6].split("=")[1].split("\n")
	for a in ap:
		if len(a.strip()) > 0:
			spl=a.split()
			apps.append(app(spl[0],spl[1],spl[2],spl[3],spl[4],spl[5]))
		
	dr=sets[7].split("=")[1].split("\n")
	for d in dr:
		if len(d.strip()) > 0:
			spl=d.split()
			drives.append(drive(spl[0],spl[1],spl[2],spl[3]))
		
	us=sets[8].split("=")[1].split("\n")
	#print us
	for u in us:
		if len(u.strip()) > 0:
			spl=u.split()
			users.append(user(spl[0],spl[1],spl[2],spl[3],spl[4],spl[5],spl[6]))
	return apps,drives,users
	
if __name__=='__main__':
	random.seed()
	generuj(int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3])) #apps,drives,users
