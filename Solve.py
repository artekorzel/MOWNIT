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
printf "%s ", i; 
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
	out=Popen(['./ampl'],stdout=PIPE,stdin=PIPE,env=env).communicate(s1+file_name+s2)
	return out[0].split('@')[1]

if __name__=='__main__':
	print python_solver(sys.argv[1]) #input file name .dat
