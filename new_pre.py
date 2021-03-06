import time
import re
import numpy as np
from numpy.linalg import *
from itertools import combinations
#from mpi4py import MPI
from collections import defaultdict
import os

def coplan(a,b,c,d):#function to judge if the 4 points are coplan(not used)
    #print(a)
    x1=a-b
    x2=a-c
    x3=a-d
    mat=np.vstack((x1,x2,x3))
    #print(mat)
    result=det(mat)
    return result

#comm = MPI.COMM_WORLD
#size = comm.Get_size()
#rank = comm.Get_rank()
#size=int(size)
#print(rank,1)
start = time.process_time()
nnode=1
ncell=1
face_max=1000000

curdir=os.getcwd()
#print(curdir)
curdir=curdir.strip('new_pre')
#print(curdir)
newdir=curdir+'data'
os.chdir(newdir)

with open('input.txt','r') as g:
    g.readline()
    filepath = g.readline()
    filepath = filepath.strip('\n')#filepath
    g.readline()
    cell_type = g.readline()
    cell_type = cell_type.strip('\n')
    cell_type = int(cell_type)#type of cells

if(cell_type==6):
    face_type=4
    cell_num_node=8
elif(cell_type==4): 
    face_type=3
    cell_num_node=4

with open(filepath,'r') as f:
    count = len(f.readlines())  #total number of lines in the mesh file
    #print(count)
    f.seek(0)   #return to the top of file
    for i in range(1, count + 1):
        #print(i)
        line = f.readline()
        #print(line)
        find_blank = bool(re.match(' ',line))#delete space
        if find_blank == True:
            line=line.strip(' ')
        float_re = re.compile('^([-+]?([0-9]+(\.[0-9]*)?|\.[0-9]+)([eE][-+][0-9]+)?[\s]+){6}$')#find float(coordinate) in the file
        find_float = bool(float_re.match(line))
        find_nnode = bool(re.match('Nodes',line))#total number of nodes
        if cell_type == 6:
            cell_re = re.compile('^([0-9]*[\s]+){8}$')
        elif cell_type == 4:
            cell_re = re.compile('^([0-9]*[\s]+){4}$')
        find_cell = bool(cell_re.match(line))

        if find_float == True:
            #print(line)
            line=line.split(' ', 5)
            for i in range(6):
                node_info[nnode][i] = line[i]
            nnode=nnode+1
            #print(nnode)

        if find_nnode == True:
            line=line.split(' ',2)
            #print(line)
            num_nodes=line[0].strip('Nodes=')
            num_nodes=int(num_nodes.strip(','))
            num_cells=line[1].strip('Elements=')
            num_cells=int(num_cells.strip(','))
            #print(num_nodes)
            #print(num_cells)
            node_info=np.zeros((num_nodes+1,6))
            cell_node=np.zeros((num_cells+1,cell_num_node),dtype=np.int)

        if find_cell == True:
            #print(line)
            if cell_type == 6:
                line=line.split(' ',7)
            elif cell_type == 4:
                line=line.split(' ',3)
            for i in range(1,cell_num_node+1):
                #print(i)
                cell_node[ncell][i-1]=int(line[i-1])#cell_node connectivity
            ncell=ncell+1

#print(1)
cell_info=np.zeros((num_cells+1,6))
for i in range(1,num_cells+1):
    for j in range(cell_num_node):
        tag_node=int(cell_node[i][j])
        for k in range(6):
            #print(i,k,tag_node)
            cell_info[i][k] += node_info[tag_node][k]
#print(cell_info[1][3])
cell_info[:][:]=cell_info[:][:]/cell_num_node
#print(cell_info[1][1])

face_info=np.zeros((face_max,face_type),dtype=np.int)
face_cell=np.zeros((face_max,2),dtype=np.int)
tag_=set()
tag=[]

#h=np.array([0,1,2,3,4,5,6,7],dtype=np.int)
if cell_type == 6:
    comb=tuple(((0,1,2,3),(0,1,4,5),(1,2,5,6),(0,3,4,7),(2,3,6,7),(4,5,6,7)))#list of face in one cell(default connectivity in tecplot)
elif cell_type == 4:
    comb=tuple(((0,1,2),(0,1,3),(0,2,3),(1,2,3)))

#print(1)
'''
cell_d=np.zeros((size),dtype=np.int)
cell_f=np.zeros((size),dtype=np.int)
nelem_p=num_cells
nchunck_p=nelem_p//size
nreste_p=nelem_p-nchunck_p*size
nreste_p=int(nreste_p)
cell_d[0]=1
if nchunck_p == 0:
    nchunck_p=1
    cell_f[0]=nchunck_p
    for i in range(1,nreste_p):
        cell_d[i]=cell_f[i-1]+1
        cell_f[i]=cell_d[i]+nchunck_p-1
    size=nreste_p
else:
    cell_f[0]=nchunck_p
    for i in range(1,size-nreste_p):
        cell_d[i]=cell_f[i-1]+1
        cell_f[i]=cell_d[i]+nchunck_p-1
    for i in range(size-nreste_p,size):
        cell_d[i]=cell_f[i-1]+1
        cell_f[i]=cell_d[i]+nchunck_p
'''
#print(rank,1)
d = defaultdict(list)
for i in range(1,num_cells+1):
    for j in comb:
        if cell_type == 6:
            s=frozenset([cell_node[i][j[0]],cell_node[i][j[1]],cell_node[i][j[2]],cell_node[i][j[3]]])
            tag_.add(s)
            d[s].append(i)
        elif cell_type == 4:
            s=frozenset([cell_node[i][j[0]],cell_node[i][j[1]],cell_node[i][j[2]]])
            tag_.add(s)
            d[s].append(i)
#comm.Barrier()
#print(rank,1)
#print(tag_)
#tag = comm.gather(tag_, root=0)
#print(rank,1)
#tag[rank]=comm.bcast(tag[rank],root=rank)
'''
if rank == 0:
    tag3=sum(tag,[])
    print(len(tag3))
'''
#print(d)

#if rank == 0:
#tag2=list(set(tag3))
#tag2.sort(key=tag3.index)
#print(len(tag2))
#print(tag2[1])
tag2=list(tag_)
for i in tag2:
    if len(d[i]) == 1:
        d[i].append(0)

#print(d)

for i in range(len(tag2)):
    if cell_type == 6:
        face=list(tag2[i])
        face_info[i+1][0]=face[0]
        face_info[i+1][1]=face[1]
        face_info[i+1][2]=face[2]
        face_info[i+1][3]=face[3]
        face_cell[i+1][0]=d[tag2[i]][0]
        face_cell[i+1][1]=d[tag2[i]][1]
    elif cell_type == 4:
        face=list(tag2[i])
        face_info[i+1][0]=face[0]
        face_info[i+1][1]=face[1]
        face_info[i+1][2]=face[2]
        face_cell[i+1][0]=d[tag2[i]][0]
        face_cell[i+1][1]=d[tag2[i]][1]


'''
for i in range(1,num_cells+1):
    for j in comb:
        #print(i,j,cell_node[i][j[0]])
        if cell_type == 6:
            if {cell_node[i][j[0]],cell_node[i][j[1]],cell_node[i][j[2]],cell_node[i][j[3]]} not in tag:
                face_info[k][0]=cell_node[i][j[0]]
                face_info[k][1]=cell_node[i][j[1]]
                face_info[k][2]=cell_node[i][j[2]]
                face_info[k][3]=cell_node[i][j[3]]
                face_cell[k][0]=i
                k=k+1
                tag.append({cell_node[i][j[0]],cell_node[i][j[1]],cell_node[i][j[2]],cell_node[i][j[3]]}) 
            elif {cell_node[i][j[0]],cell_node[i][j[1]],cell_node[i][j[2]],cell_node[i][j[3]]} in tag:
                m=tag.index({cell_node[i][j[0]],cell_node[i][j[1]],cell_node[i][j[2]],cell_node[i][j[3]]})
                face_cell[m+1][1]=i
        elif cell_type == 4:
            if {cell_node[i][j[0]],cell_node[i][j[1]],cell_node[i][j[2]]} not in tag:
                face_info[k][0]=cell_node[i][j[0]]
                face_info[k][1]=cell_node[i][j[1]]
                face_info[k][2]=cell_node[i][j[2]]
                face_cell[k][0]=i
                k=k+1
                tag.append({cell_node[i][j[0]],cell_node[i][j[1]],cell_node[i][j[2]]}) 
            elif {cell_node[i][j[0]],cell_node[i][j[1]],cell_node[i][j[2]]} in tag:
                m=tag.index({cell_node[i][j[0]],cell_node[i][j[1]],cell_node[i][j[2]]})
                face_cell[m+1][1]=i

        #if i < 4:
        #print(len(tag))
#print(tag)
'''

#if rank == 0:
meshdim=3
with open('1.msh','w') as c:
    print(meshdim,file=c)
    print(num_nodes,file=c)
    for i in range(1,num_nodes+1):
        print(node_info[i][0],node_info[i][1],node_info[i][2],file=c)
    print(num_cells,file=c)
    print(len(tag2),file=c)
    for i in range(1,len(tag2)+1):
        print(' '.join(map(str,face_info[i,:])),' '.join(map(str,face_cell[i,:])),file=c)

with open('INFILES/internal_field/temp.in','w') as d:
    for i in range(1,num_cells+1):
        print(i,cell_info[i][3],file=d)

with open('INFILES/internal_field/concentration_co2.in','w') as e:
    for i in range(1,num_cells+1):
        print(i,cell_info[i][4],file=e)

with open('INFILES/internal_field/concentration_h2o.in','w') as f:
    for i in range(1,num_cells+1):
        print(i,cell_info[i][5],file=f)


end=time.process_time()
#if rank == 0:
print(' Data conversion time:',end-start)