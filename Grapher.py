'''
Created on Jun 13, 2012

@author: andrzej
'''

#0 - apps 1 - drvies 2- users 3- table with ampl solve data
def graph(graph_data):
    solve_data=graph_data[3]
    i=0
    for drive in solve_data:
        mult=graph_data[1][i].size
        j=0
        for app in solve_data[i]:
            solve_data[i][j]*=mult
            j+=1
        i+=1
    print solve_data