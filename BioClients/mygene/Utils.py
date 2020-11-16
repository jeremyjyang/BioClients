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
  df=pd.DataFrame();
  mgi = mg.MyGeneInfo()
  ichunk=0;
  while ichunk*NCHUNK<len(ids):
    df_this = mgi.getgenes(ids[ichunk*NCHUNK:((ichunk+1)*NCHUNK)], fields, as_dataframe=True)
    df = pd.concat([df, df_this])
    ichunk+=1
  if fout: df.to_csv(fout, "\t", index=False)
  return df

#############################################################################
def SearchGenes(queries, species, fout=None):
  """Search genes by symbol, etc. using MyGene syntax."""
  df=pd.DataFrame();
  mgi = mg.MyGeneInfo()
  for qry in queries:
    df_this = mgi.query(qry, species=species, as_dataframe=True)
    df = pd.concat([df, df_this])
  if fout: df.to_csv(fout, "\t", index=False)
  return df

#############################################################################
