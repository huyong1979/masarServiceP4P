import sys
from os import listdir
from os.path import isfile, join

import numpy as np

import cothread.catools as ca

def main(mypath):
    pvfiles = [f for f in listdir(mypath) if isfile(join(mypath,f)) ]
    pvs = []
    for pvfile in pvfiles:
        pvtmp = np.loadtxt('/'.join((mypath, pvfile)), dtype=str)
        pvs = list(set(pvs + list(pvtmp)))
    res = ca.caget(pvs, throw = False)
    goodcondition = True
    for r in res:
        if r.ok==False:
            if goodcondition:
               goodcondition = False
            print r.name
    if goodcondition:
        print "All PVs passed testing. Congratuation!"
    else:
        print "All above PVs are not reachable."

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise RuntimeError("Cannnot find root directory of PVs to verify")
    args = sys.argv[1]
    main(args)
