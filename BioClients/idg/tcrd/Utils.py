#!/usr/bin/env python3
"""
TCRD MySql db client utilities.
"""
import os,sys,re,time,json,logging,yaml
import pandas as pd
from pandas.io.sql import read_sql_query
import mysql.connector as mysql

TDLS = ['Tdark', 'Tbio', 'Tchem', 'Tclin']

#############################################################################
def ReadParamFile(fparam):
  params={};
  with open(fparam, 'r') as fh:
    for param in yaml.load_all(fh, Loader=yaml.BaseLoader):
      for k,v in param.items():
        params[k] = v
  return params

#############################################################################
def Info(dbcon, fout=None):
  sql = 'SELECT * FROM dbinfo'
  df = read_sql_query(sql, dbcon)
  if fout:
    df.to_csv(fout, "\t", index=False)
  return df

#############################################################################
def ListTables(dbcon, fout=None):
  sql = 'SHOW TABLES'
  df = read_sql_query(sql, dbcon)
  if fout:
    df.to_csv(fout, "\t", index=False)
  return df

#############################################################################
def DescribeTables(dbcon, fout=None):
  n_table=0; df=None;
  for table in ListTables(dbcon).iloc[:,0]:
    n_table+=1
    sql = ('DESCRIBE '+table)
    df_this = read_sql_query(sql, dbcon)
    cols = list(df_this.columns.values)
    df_this['table'] = table
    df_this = df_this[['table']+cols]
    if n_table==1:
      df = df_this
    else:
      df = pd.concat([df, df_this])
  if fout:
    df.to_csv(fout, "\t", index=False)
  return df

#############################################################################
def TableRowCounts(dbcon, fout):
  n_table=0;
  for table in ListTables(dbcon).iloc[:,0]:
    n_table+=1
    sql = ('SELECT count(*) AS row_count FROM '+table)
    df_this = read_sql_query(sql, dbcon)
    cols = list(df_this.columns.values)
    df_this['table'] = table
    df_this = df_this[['table']+cols]
    if n_table==1:
      df = df_this
    else:
      df = pd.concat([df, df_this])
  if fout:
    df.to_csv(fout, "\t", index=False)
  return df

#############################################################################
def TDLCounts(dbcon, fout=None):
  sql="SELECT tdl, COUNT(id) AS target_count FROM target GROUP BY tdl"
  df = read_sql_query(sql, dbcon)
  if fout:
    df.to_csv(fout, "\t", index=False)
  return df

#############################################################################
def AttributeCounts(dbcon, fout=None):
  sql='SELECT ga.type, COUNT(ga.id) FROM gene_attribute ga GROUP BY ga.type'
  df = read_sql_query(sql, dbcon)
  if fout:
    df.to_csv(fout, "\t", index=False)
  return df

#############################################################################
def XrefCounts(dbcon, fout=None):
  sql = ('SELECT xtype, COUNT(DISTINCT value) FROM xref GROUP BY xtype ORDER BY xtype')
  df = read_sql_query(sql, dbcon)
  if fout:
    df.to_csv(fout, "\t", index=False)
  return df

#############################################################################
def ListXreftypes(dbcon, fout=None):
  sql='SELECT DISTINCT xtype FROM xref ORDER BY xtype'
  df = read_sql_query(sql, dbcon)
  if fout:
    df.to_csv(fout, "\t", index=False)
  return df

#############################################################################
def ListXrefs(dbcon, qtype, fout):
  cols=['value','target_id','protein_id']
  sql='''\
SELECT DISTINCT %(COLS)s
FROM xref
WHERE xtype = '%(QTYPE)s'
'''%{	'COLS':(','.join(cols)),
	'QTYPE':qtype }
  df = read_sql_query(sql, dbcon)
  if fout:
    df.to_csv(fout, "\t", index=False)
  return df

#############################################################################
def ListTargets(dbcon, tdl, pfam, fout):
  sql='''
SELECT
	target.id AS "tcrdTargetId",
	target.name AS "tcrdTargetName",
	target.fam AS "tcrdTargetFamily",
	target.tdl AS "TDL",
	target.ttype AS "tcrdTargetType",
	target.idg AS "idgList",
	protein.id AS "tcrdProteinId",
	protein.sym AS "tcrdGeneSymbol",
	protein.family AS "tcrdProteinFamily",
	protein.geneid AS "ncbiGeneId",
	protein.uniprot AS "uniprotId",
	protein.up_version AS "uniprotVersion",
	protein.chr,
	protein.description AS "tcrdProteinDescription",
	protein.dtoid AS "dtoId",
	protein.dtoclass AS "dtoClass",
	protein.stringid AS "ensemblProteinId",
	xref.value AS "ensemblGeneId"
FROM
	target
JOIN
	t2tc ON t2tc.target_id = target.id
JOIN
	protein ON protein.id = t2tc.protein_id
JOIN
	xref ON xref.protein_id = protein.id
'''
  wheres=["xref.xtype = 'Ensembl'", "xref.value REGEXP '^ENSG'"]
  if tdl:
    wheres.append('target.tdl = \'%s\''%tdl)
  if pfam:
    wheres.append('target.fam = \'%s\''%pfam)
  if wheres:
    sql+=(' WHERE '+(' AND '.join(wheres)))
  df = read_sql_query(sql, dbcon)
  if tdl: logging.info('TDL: %s'%(tdl))
  if pfam: logging.info('Pfam: %s'%(pfam))
  logging.info('rows: %d'%(df.shape[0]))
  logging.info('Target count: %d'%(df.tcrdTargetId.nunique()))
  logging.info('Protein count: %d'%(df.tcrdProteinId.nunique()))
  logging.info('Uniprot count: %d'%(df.uniprotId.nunique()))
  logging.info('ENSP count: %d'%(df.ensemblProteinId.nunique()))
  logging.info('ENSG count: %d'%(df.ensemblGeneId.nunique()))
  logging.info('GeneSymbol count: %d'%(df.tcrdGeneSymbol.nunique()))
  if fout:
    df.to_csv(fout, "\t", index=False)
  return df

#############################################################################
def GetTargets(dbcon, qs, qtype, fout):
  if not qs:
    logging.error('No query IDs.')
    return
  cols=[
	'target.description',
	'target.id',
	'target.fam',
	'target.name',
	'target.tdl',
	'target.ttype',
	'protein.chr',
	'protein.description',
	'protein.family',
	'protein.geneid',
	'protein.id',
	'protein.name',
	'protein.sym',
	'protein.uniprot'
	]
  #if fout: fout.write('query,qtype,'+('%s\n'%(','.join(cols))))

  n_query=0; n_hit=0;
  for qid in qs:
    n_query+=1
    sql='''\
SELECT
	%(COLS)s
FROM
	target
JOIN
	t2tc ON target.id = t2tc.target_id
JOIN
	protein ON protein.id = t2tc.protein_id
'''%{'COLS':(','.join(map(lambda s: '%s AS %s'%(s, s.replace('.', '_')), cols)))}
    wheres=[]
    if qtype.lower()=='tid':
      wheres.append('target.id = %d'%int(qid))
    elif qtype.lower()=='uniprot':
      wheres.append('protein.uniprot = \'%s\''%qid)
    elif qtype.lower() in ('gid', 'geneid'):
      wheres.append('protein.geneid = \'%s\''%qid)
    elif qtype.lower() in ('genesymb', 'genesymbol'):
      wheres.append('protein.sym = \'%s\''%qid)
    elif qtype.lower() == 'ensp':
      wheres.append('protein.stringid = \'%s\''%qid)
    elif qtype.lower() == 'ncbi_gi':
      sql+=('\nJOIN\n\txref ON xref.protein_id = protein.id')
      wheres.append('xref.xtype = \'NCBI GI\'')
      wheres.append('xref.value = \'%s\''%qid)
      wheres.append('xref.protein_id = protein.id')
    else:
      logging.info('ERROR: unknown query type: %s'%qtype)
      return
    sql+=(' WHERE '+(' AND '.join(wheres)))
    logging.debug('"%s"'%sql)
    logging.debug('query: %s = "%s" ...'%(qtype, qid))
    df = read_sql_query(sql, dbcon)
    if fout:
      df.to_csv(fout, "\t", index=False, header=bool(n_query=1))
    if df.shape[0]>0:
      n_hit+=1
  logging.info("n_query: {}; n_hit: {}".format(n_query, n_hit))
  return df

#############################################################################
def GetPathways(dbcon, tids, fout):
  n_query=0;
  cols=[
	't2p.target_id',
	't2p.id',
	't2p.source',
	't2p.id_in_source',
	't2p.name',
	't2p.description',
	't2p.url'
	]
  n_hit=0;
  pids_all=set();
  for tid in tids:
    n_query+=1
    sql='''\
SELECT
	%(COLS)s
FROM
	target2pathway t2p
JOIN
	target t ON t.id = t2p.target_id
WHERE
	t.id = %(TID)s
ORDER BY
	t2p.target_id,
	t2p.id
'''%{	'COLS':(','.join(map(lambda s: '%s AS %s'%(s,s.replace('.','_')),cols))),
	'TID':str(tid)
	}
    logging.debug('"%s"'%sql)
    logging.debug('query: %s ...'%(tid))
    df = read_sql_query(sql, dbcon)
    if fout:
      df.to_csv(fout, "\t", index=False, header=bool(n_query=1))
    if df.shape[0]>0:
      n_hit+=1

  logging.info("n_query: {}; n_hit: {}".format(n_query, n_hit))
  return df

#############################################################################
