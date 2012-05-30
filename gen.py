from random import seed
from random import randint
from random import randrange
import random

tekst='set apps := '

def dodaj1(doilu):
	global tekst
	for i in xrange(doilu):
		tekst+=str(i+1)
		tekst+=' '

def generuj():
	global tekst
	numapps=45
	numdrives=10
	numusers=15
	dodaj1(numapps)
	tekst+=';\nset drives := '
	dodaj1(numdrives)
	tekst+=';\nset users := '
	dodaj1(numusers)
	tekst+=''';\nset app_params := user gen read time prior;
set user_params := profile read write security access priority;
set drive_params := read_s write_s size;
param applications :
	user gen read time prior :=
'''
	for i in range(1,numapps+1):
		tekst+=str(i)+' '+str(randint(1,numusers))+' '+str(randrange(50,500,10))+' '+str(randrange(50,500,10))+' '+str(randint(1,30))+' '+str(randint(1,3))+'\n'
	tekst+=';\nparam phys_drives :\n\tread_s write_s size :=\n'
	for i in range(1,numdrives+1):
		tekst+=str(i)+' '+str(randrange(50,550,10))+' '+str(randrange(50,550,10))+' '+str(randrange(40000,70000,5000))+' '+'\n'
	tekst+=';\nparam sys_users :\n\tprofile read write security access priority :=\n'
	for i in range(1,numusers+1):
		tekst+=str(i)+' '+str(0)+' '+str(0)+' '+str(0)+' '+str(0)+' '+str(0)+' '+str(0)+'\n'
	with open("./wynik.dat", 'w+') as plik:
		plik.write(tekst)
	
if __name__=='__main__':
	random.seed()
	generuj()
