#!/usr/bin/env python3
###
# https://mygene.info/
#
import sys,os
import mygene as mg
#
#############################################################################
def Mygene2TSV(mgi, genes, fields, fout):
  fout.write('\t'.join(['id']+fields)+'\n')
  for geneid in genes.ID:
    g = mgi.getgene(geneid, fields)
    vals=[geneid]
    if g:
      for key in fields:
        vals.append(str(g[key]) if key in g else '')
    else:
      vals.extend(['' for key in fields])
    fout.write('\t'.join(vals)+'\n')

#############################################################################
