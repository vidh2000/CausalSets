#!/usr/bin/env python
"""
Created on 13 Oct 2022

@author: Stefano Veroni
"""
#%%
from __future__ import annotations
from typing import List, Tuple 

from causets.causetevent import CausetEvent
from causets.causet import Causet
from causets.sprinkledcauset import SprinkledCauset
from causets.shapes import CoordinateShape
from causets.spacetimes import *
import causets.causetplotting as cplt

import numpy as np
import random
from tqdm import tqdm
import matplotlib.pyplot as plt

st   = [FlatSpacetime, deSitterSpacetime, 
       AntideSitterSpacetime, BlackHoleSpacetime]
dims = [  [1,2,3,4],       [2,3,4],            
           [2,3,4],          [2]       ]

#%% CHECK THAT INTERVAL AND ORDRING FRACTION WORK CORRECTLY

#%%%CHAIN-LIKE CAUSET SHOULD HAVE 1
N = 8
Cm = np.zeros([N,N])
for i in range(N-1):
    for j in range(i+1, N):
        Cm[i,j] = 1
print("CMatrix")
print(Cm)
print("\nDifference between retrieved and original Cmatrix")
C = Causet().FromCausalMatrix(Cm)
print(C.CMatrix(method = "label") - Cm)
print("\nChain Link Matrix\n", C.LMatrix())
Clist = C.nlist()
print("Has ordering Frac = ", C.ord_fr_A(C.Interval(Clist[3], Clist[6],
                                                disjoin = True)))
print("Should have 1\n")
print("Has ordering Frac = ", C.ord_fr_ab(Clist[3], Clist[6]))
print("Should have 1\n")
del N, i, j
#%%%TRY A KNOWN CAUSET
# Between 3 and 8 should have 0.9
# Betwewn 2 and 8 should have 0.93
# Between 3 and 9 should have 1

Cm = np.array([[0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
               [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
               [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
               [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1],
               [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
               [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])
C = Causet().FromCausalMatrix(Cm)
print("\nChain Link Matrix\n", C.LMatrix())
Clist = C.nlist(method="label")
#print("Clist:\n",Clist)

A = C.Interval(Clist[3], Clist[8], disjoin = True)
print(f"Cardinality is {len(A)}")
print("Has ordering Frac = ", C.ord_fr_A(A))
print("Has ordering Frac = ", C.ord_fr_ab(Clist[3], Clist[8]))
print("Should have 0.9\n")
A = C.Interval(Clist[2], Clist[8], disjoin = True)
print(f"Cardinality is {len(A)}")
print("Has ordering Frac = ", C.ord_fr_A(A))
print("Has ordering Frac = ", C.ord_fr_ab(Clist[2], Clist[8]))
print("Should have 0.93\n")
A = C.Interval(Clist[3], Clist[9], disjoin = True)
print(f"Cardinality is {len(A)}")
print("Has ordering Frac = ", C.ord_fr_A(A))
print("Has ordering Frac = ", C.ord_fr_ab(Clist[3], Clist[9]))
print("Should have 1\n")
""" 
A = C.Interval(Clist[2], Clist[8], disjoin = True)
print(Clist[2], " preceeds ", Clist[3], " ? ",Clist[2]<=Clist[3])
print(Clist[3], " preceeds ", Clist[4], " ? ",Clist[3]<=Clist[4])
print(Clist[4], " preceeds ", Clist[5], " ? ",Clist[4]<=Clist[5])
print(Clist[5], " preceeds ", Clist[8], " ? ",Clist[5]<=Clist[8])
print(Clist[2], " preceeds ", Clist[8], " ? ",Clist[2]<=Clist[8])
print(f"Cardinality is {len(A)}")
try:
    print("Has ordering Frac = ", C.ord_fr(A))
except ZeroDivisionError:
    print("There was a division by zero in ordering fraction")
"""
del Cm, C, Clist

#%% CHECK DIMESNION ESTIMATOR IN FLAT SPACETIME FOR ALL COORDINATES
Ns = [512, 384, 256, 192,  128, 64, 32,  24, 16, 8]
repetitions = 10
cuts = np.array([0]+Ns[:-1])-np.array([0]+Ns[1:])
radius = 1
dim_est = []
dim_std = []
for i in range(len(dims[0])):
    d = dims[0][i]
    dim_est.append([])
    dim_std.append([])
    for r in range(repetitions):
        dim_est[i].append([])
        dim_std[i].append([])
        S: CoordinateShape = CoordinateShape(d, 'cylinder', 
                                            radius = radius,
                                            duration=5, 
                                            hollow=0)
        try:
            C: SprinkledCauset = SprinkledCauset(card=Ns[0],
                                            spacetime=FlatSpacetime(d), 
                                            shape=S)
        except ZeroDivisionError:
            print(f"At dimension {d} did NOT use cylinder shape")
            C: SprinkledCauset = SprinkledCauset(card=Ns[0],
                                            spacetime=FlatSpacetime(d))
        for cut in tqdm(cuts, f"Dimension {d}"):
            if cut != 0:
                C.coarsegrain(card = cut)
            MMd = C.MMdim_est(Nsamples = 50, 
                                ptime_constr=lambda t:t<2*radius,
                                size_min = min(50, int(len(C)/3)),
                                full_output = True)
            dim_est[i][r].append(MMd[0]) # add to rth repetition 
            #dim_std[i][r].append(MMd[1]) # in ith dimension
    #Average over repetitions:
    try:
        dim_std[i] = np.nanstd (dim_est[i], axis = 0)
        dim_est[i] = np.nanmean(dim_est[i], axis = 0)
    except (TypeError, ZeroDivisionError):
        beforeerror = dim_est[i]
        dim_std[i] = np.nanstd (np.array(dim_est[i], dtype=np.float64),
                                 axis = 0)
        dim_est[i] = np.nanmean(np.array(dim_est[i], dtype=np.float64),
                                 axis = 0)

del d, i, r, cut
del S, radius, repetitions

plt.figure("MMFlatDim")
Ns.reverse()
for i in range(len(dims[0])):
    plt.errorbar(Ns, np.flip(dim_est[i]), yerr = np.flip(dim_std[i]),
                    fmt = ".", capsize = 4, 
                    label = f"Dimension {dims[0][i]}")
plt.title("Testing Myrheim-Mayers Estimator in Minkowski")
plt.xlabel("Cardinality")
plt.ylabel("Dimension")
plt.legend()
plt.xscale('log')
plt.show()


# %%
from scipy.optimize import fsolve
from scipy.special import gamma as spgamma

def MM_drelation(d):
            a = spgamma(d+1)
            b = spgamma(d/2)
            c = 4 * spgamma(3*d/2)
            return a*b/c
        
def MM_to_solve(d, ord_fr):
    return MM_drelation(d) - ord_fr/2

print("Ordering Fraction -> d")
print("1.00 -> ",fsolve(MM_to_solve, 2, 1))
print("0.50 -> ",fsolve(MM_to_solve, 2, 0.5))
print("0.40 -> ",fsolve(MM_to_solve, 2, 0.40))
print("0.35 -> ",fsolve(MM_to_solve, 2, 0.35))
print("0.30 -> ",fsolve(MM_to_solve, 2, 0.3))
print("0.23 -> ",fsolve(MM_to_solve, 2, 8/35, full_output=1)[0])
print("0.15 -> ",fsolve(MM_to_solve, 2, 0.15))
print("0.12 -> ",fsolve(MM_to_solve, 2, 0.12))
print("0.10 -> ",fsolve(MM_to_solve, 2, 0.1))
print("0.08 -> ",fsolve(MM_to_solve, 2, 0.08))
print("0.05 -> ",fsolve(MM_to_solve, 2, 0.05))

# %%
print(np.nanstd(beforeerror, dtype = np.float64, axis = 0))
# %%
