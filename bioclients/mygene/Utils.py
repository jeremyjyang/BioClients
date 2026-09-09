#!/usr/bin/env python3
"""
https://mygene.info/
https://mygene.info/v3/api
https://pypi.org/project/mygene/
"""
###
#
import sys,os
import pandas as pd
import mygene as mg
#
FIELDS = 'HGNC,symbol,name,taxid,entrezgene,ensemblgene'
NCHUNK=100;
#
#############################################################################
def GetGenes(ids, fields=FIELDS, fout=None):
  """Get genes by Entrez or Ensembl gene ID."""
  ichunk=0; n_out=0; df=None;
  mgi = mg.MyGeneInfo()
  while ichunk*NCHUNK<len(ids):
    df_this = mgi.getgenes(ids[ichunk*NCHUNK:((ichunk+1)*NCHUNK)], fields, as_dataframe=True)
    if fout is not None: df.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
    else: df = pd.concat([df, df_this])
    n_out+=df_this.shape[0]
    ichunk+=1
  return df

#############################################################################
def SearchGenes(queries, species, fout=None):
  """Search genes by symbol, etc. using MyGene syntax."""
  ichunk=0; n_out=0; df=None;
  mgi = mg.MyGeneInfo()
  for qry in queries:
    df_this = mgi.query(qry, species=species, as_dataframe=True)
    if fout is not None: df.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
    else: df = pd.concat([df, df_this])
    n_out+=df_this.shape[0]
    ichunk+=1
  return df

#############################################################################
