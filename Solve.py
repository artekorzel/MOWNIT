#/usr/bin/env python

'''
Created on May 29, 2012

@author: andrzej&artur
'''

from subprocess import Popen,PIPE
import sys
from os import environ

env = dict(environ)
env['LD_LIBRARY_PATH'] = '.'

s1=r'''option solver "./donlp2";
model "./Model.mod";
data "'''
s2=r'''";
solve;
printf "@";
for{i in drives} 
{
for{j in apps}
{
printf "%f ", zuzycie[i,j];
}
printf "\n";
}
'''
def python_solver(file_name):
	global s1,s2
	global env
	#with open('./amplscript', 'r') as p:
		#out=Popen(['./ampl'],stdout=PIPE,stdin=p).communicate()
	po=Popen(['./ampl'],stdout=PIPE,stdin=PIPE,env=env)
	out=po.communicate(s1+file_name+s2)
	return out[0].split('@')[1]

def parser(solver_str):
	tab=[]	#dane dla graphera
	tmp=solver_str.split('\n')[:-1]
	for i in tmp:
		tab.append(i.split(' ')[:-1])
	for i in range(len(tab)):
		for j in range(len(tab[i])):
			tab[i][j]=float(tab[i][j])
	return tab	

if __name__=='__main__':
	print parser(python_solver(sys.argv[1])) #input file name .dat
