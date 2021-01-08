import numpy as np
from numpy.linalg import  *
from itertools import combinations
def coplan(a,b,c,d):
    #print(a)
    x1=a-b
    x2=a-c
    x3=a-d
    mat=np.vstack((x1,x2,x3))
    #print(mat)
    result=det(mat)
    return result


if __name__ == "__main__":
    a=np.array([1,2,2],dtype=np.float64)
    b=np.array([2,3,2],dtype=np.float64)
    c=np.array([3,5,2],dtype=np.float64)
    d=np.array([2,3,2],dtype=np.float64)
    val=coplan(a,b,c,d)
    print(val)
    h=np.array([0,1,2,3,4,5,6,7],dtype=np.float64)
    comb=tuple(combinations(h,4))
    print(comb[1][3])
    tag=np.ones([8,8,8,8])
    print(tag[1][1][1][1])
    comb=tuple(((0,1,2,3),(0,1,4,5),(0,1,6,7),(2,3,4,5),(2,3,6,7),(4,5,6,7)))
    print(comb[1][2])
    l1 = ['b','c','d','b','c','a','a']
    l2 = list(set(l1))
    l2.sort(key=l1.index)
    print(l2)