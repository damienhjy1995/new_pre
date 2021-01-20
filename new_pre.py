import time
import re
import numpy as np
from numpy.linalg import *
from collections import defaultdict
import os

def coplan(a,b,c,d):#function to judge if the 4 points are coplan(not used)
    x1=a-b
    x2=a-c
    x3=a-d
    mat=np.vstack((x1,x2,x3))
    result=det(mat)
    return result

start = time.process_time()
nnode=1
ncell=1
face_max=1000000

curdir=os.getcwd()
curdir=curdir.strip('new_pre')
newdir=curdir+'data'#enter data directory
os.chdir(newdir)

with open('input.txt','r') as g:#read file path and cell type
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
    f.seek(0)   #return to the top of file
    for i in range(1, count + 1):
        line = f.readline()
        find_blank = bool(re.match(' ',line))#delete space
        if find_blank == True:
            line=line.strip(' ')
        float_re = re.compile('^([-+]?([0-9]+(\.[0-9]*)?|\.[0-9]+)([eE][-+][0-9]+)?[\s]+){6}$')#find float(coordinate) in the file
        find_float = bool(float_re.match(line))
        find_nnode = bool(re.match('Nodes',line))#total number of nodes and elements
        if cell_type == 6:
            cell_re = re.compile('^([0-9]*[\s]+){8}$')#cell node connectivity
        elif cell_type == 4:
            cell_re = re.compile('^([0-9]*[\s]+){4}$')
        find_cell = bool(cell_re.match(line))

        if find_nnode == True:
            line=line.split(' ',2)
            num_nodes=line[0].strip('Nodes=')
            num_nodes=int(num_nodes.strip(','))
            num_cells=line[1].strip('Elements=')
            num_cells=int(num_cells.strip(','))
            node_info=np.zeros((num_nodes+1,6))
            cell_node=np.zeros((num_cells+1,cell_num_node),dtype=np.int)

        if find_cell == True:
            if cell_type == 6:
                line=line.split(' ',7)
            elif cell_type == 4:
                line=line.split(' ',3)
            for i in range(1,cell_num_node+1):
                cell_node[ncell][i-1]=int(line[i-1])#cell_node connectivity
            ncell=ncell+1

#nodal value to cell-centered value
cell_info=np.zeros((num_cells+1,6))
for i in range(1,num_cells+1):
    for j in range(cell_num_node):
        tag_node=int(cell_node[i][j])
        for k in range(6):
            cell_info[i][k] += node_info[tag_node][k]
cell_info[:][:]=cell_info[:][:]/cell_num_node

face_info=np.zeros((face_max,face_type),dtype=np.int)#face node connectivity
face_cell=np.zeros((face_max,2),dtype=np.int)#neighbour cell
tag_=set()

if cell_type == 6:
    comb=tuple(((0,1,2,3),(0,1,4,5),(1,2,5,6),(0,3,4,7),(2,3,6,7),(4,5,6,7)))#list of face in one cell(default connectivity in tecplot)
elif cell_type == 4:
    comb=tuple(((0,1,2),(0,1,3),(0,2,3),(1,2,3)))

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

tag2=list(tag_)
for i in tag2:
    if len(d[i]) == 1:
        d[i].append(0)


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

num_faces=len(tag2)
#cell_face=np.zeros((num_cells+1,cell_type),dtype=np.int)
cell_face=[[] for i in range(num_cells+1)]
for i in range(1,num_faces+1):
    for j in range(2):
        #np.append(cell_face[face_cell[i][j]],i)
        cell_face[face_cell[i][j]].append(i)

#print(cell_face)


meshdim=3
with open('intermediate/1.msh','w') as c:#store modified .msh file
    print(meshdim,file=c)
    print(num_nodes,file=c)
    for i in range(1,num_nodes+1):
        print(node_info[i][0],node_info[i][1],node_info[i][2],file=c)
    print(num_cells,file=c)
    print(num_faces,file=c)
    for i in range(1,num_faces+1):
        print(' '.join(map(str,face_info[i,:])),' '.join(map(str,face_cell[i,:])),file=c)

with open('INFILES/internal_field/temp.in','w') as d:#temperature field
    for i in range(1,num_cells+1):
        print(i,cell_info[i][3],file=d)

with open('INFILES/internal_field/concentration_co2.in','w') as e:#species concentration field
    for i in range(1,num_cells+1):
        print(i,cell_info[i][4],file=e)

with open('INFILES/internal_field/concentration_h2o.in','w') as f:
    for i in range(1,num_cells+1):
        print(i,cell_info[i][5],file=f)

with open('INFILES/mesh/cell2face.in','w') as g:
    for i in range(1,num_cells+1):
        print(i,' '.join(map(str,cell_face[i][:])),file=g)

end=time.process_time()
print(' Data conversion time:',end-start)