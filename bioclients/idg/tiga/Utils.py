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
  if fout: df.to_csv(fout, sep="\t", index=False)
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
  if fout: df.to_csv(fout, sep="\t", index=False)
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
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"n_traits: {df.shape[0]}")
  return df

#############################################################################
def GetGeneTraitAssociations(geneIds, traitIds, dbcon, fout=None):
  df=None; n_out=0;
  sql = """\
SELECT DISTINCT
	efoid efoId,
	trait efoName,
	traitNgene,
	traitNstudy,
	tiga.ensg ensemblGeneId,
	tiga.protein_id tcrdProteinId,
	protein.sym,
	protein.description proteinName,
	tiga.geneNtrait,
	tiga.geneNstudy,
	tiga.n_study,
	tiga.n_snp,
	tiga.n_snpw,
	tiga.pvalue_mlog_median,
	tiga.or_median,
	tiga.n_beta,
	tiga.study_N_mean,
	tiga.rcras,
	tiga.meanRank,
	tiga.meanRankScore
FROM
	tiga
JOIN
	protein ON protein.id = tiga.protein_id
"""
  if geneIds is None:
    for traitId in traitIds:
      sql_this = sql+f"\nWHERE efoid = '{traitId}'"
      df_this = pd.read_sql(sql_this, dbcon)
      if fout is None:
        df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]
  elif traitIds is None:
    for geneId in geneIds:
      sql_this = sql+f"\nWHERE ensg = '{geneId}'"
      df_this = pd.read_sql(sql_this, dbcon)
      if fout is None:
        df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]
  else:
    for geneId in geneIds:
      for traitId in traitIds:
        sql_this = sql+f"\nWHERE efoid = '{traitId}' AND ensg = '{geneId}'"
        df_this = pd.read_sql(sql_this, dbcon)
        if fout is None:
          df = pd.concat([df, df_this])
        else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
        n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  if fout is None:
    return df

#############################################################################
def GetGeneTraitProvenance(geneIds, traitIds, dbcon, fout=None):
  df=None; n_out=0;
  sql = """\
SELECT DISTINCT
	tiga_provenance.ensg,
	tiga_provenance.efoid,
	tiga_provenance.study_acc,
	tiga_provenance.pubmedid,
	pubmed.title,
	pubmed.journal,
	pubmed.date,
	pubmed.authors,
	pubmed.abstract
FROM
	tiga_provenance
JOIN
	pubmed ON pubmed.id = tiga_provenance.pubmedid
WHERE
	tiga_provenance.ensg = '{0}' AND tiga_provenance.efoid = '{1}'
	;
"""
  for geneId in geneIds:
    for traitId in traitIds:
      sql_this = sql.format(geneId, traitId)
      df_this = pd.read_sql(sql_this, dbcon)
      if fout is None:
        df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  if fout is None:
    return df

