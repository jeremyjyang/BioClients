#!/usr/bin/env python3
"""
TIGA/TCRD (Target Illumination GWAS Analytics) MySql client utilities
"""
###
import os,sys,re,time,json,logging,yaml,tqdm
import pandas as pd

#############################################################################
def Info(dbcon, fout=None):
  df=None;
  sqls = [
	"SELECT COUNT(DISTINCT study_acc) study_count FROM tiga_provenance",
	"SELECT COUNT(DISTINCT pmid) publication_count FROM tiga_provenance",
	"SELECT COUNT(DISTINCT efoid) trait_count FROM tiga",
	"SELECT COUNT(DISTINCT ensg) gene_count FROM tiga",
	"SELECT COUNT(DISTINCT protein_id) protein_count FROM tiga",
	]
  for sql in sqls:
    df_this = pd.read_sql(sql, dbcon)
    df = pd.concat([df, df_this], axis=1)
  df = df.transpose()
  df.reset_index(drop=False, inplace=True)
  df.columns = ["count", "N"]
  if fout: df.to_csv(fout, "\t", index=False)
  return df

#############################################################################
def ListGenes(dbcon, fout=None):
  df=None;
  sql = """\
SELECT DISTINCT
	tiga.ensg ensemblGeneId,
	tiga.protein_id tcrdProteinId,
	protein.sym,
	protein.description proteinName,
	tiga.geneNtrait,
	tiga.geneNstudy
FROM
	tiga
JOIN
	protein ON protein.id = tiga.protein_id
	;
"""
  df = pd.read_sql(sql, dbcon)
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"n_genes: {df.shape[0]}")
  return df

#############################################################################
def ListTraits(dbcon, fout=None):
  df=None;
  sql = """\
SELECT DISTINCT
	efoid efoId,
	trait efoName,
	traitNgene,
	traitNstudy
FROM
	tiga
	;
"""
  df = pd.read_sql(sql, dbcon)
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"n_traits: {df.shape[0]}")
  return df
