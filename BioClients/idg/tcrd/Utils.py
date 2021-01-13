#!/usr/bin/env python3
"""
TCRD MySql db client utilities.
"""
import os,sys,re,time,json,logging,yaml
import pandas as pd
from pandas.io.sql import read_sql_query

TDLS = ['Tdark', 'Tbio', 'Tchem', 'Tclin']

#############################################################################
def Info(dbcon, fout=None):
  sql = 'SELECT * FROM dbinfo'
  df = read_sql_query(sql, dbcon)
  if fout: df.to_csv(fout, "\t", index=False)
  return df

#############################################################################
def ListTables(dbcon, fout=None):
  sql = 'SHOW TABLES'
  df = read_sql_query(sql, dbcon)
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info("n_table: {}".format(df.shape[0]))
  return df

#############################################################################
def ListDatasets(dbcon, fout=None):
  sql = 'SELECT * FROM dataset'
  df = read_sql_query(sql, dbcon)
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info("n_table: {}".format(df.shape[0]))
  return df

#############################################################################
def DescribeTables(dbcon, fout=None):
  return ListColumns(dbcon, fout)

#############################################################################
def ListColumns(dbcon, fout=None):
  n_table=0; df=pd.DataFrame();
  for table in ListTables(dbcon).iloc[:,0]:
    n_table+=1
    sql = ('DESCRIBE '+table)
    df_this = read_sql_query(sql, dbcon)
    cols = list(df_this.columns.values)
    df_this['table'] = table
    df_this = df_this[['table']+cols]
    df = pd.concat([df, df_this])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info("n_columns: {}; n_tables: {}".format(df.shape[0], df.table.nunique()))
  return df

#############################################################################
def TableRowCounts(dbcon, fout):
  n_table=0; df=pd.DataFrame();
  for table in ListTables(dbcon).iloc[:,0]:
    n_table+=1
    sql = ('SELECT count(*) AS row_count FROM '+table)
    df_this = read_sql_query(sql, dbcon)
    cols = list(df_this.columns.values)
    df_this['table'] = table
    df_this = df_this[['table']+cols]
    df = pd.concat([df, df_this])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info("n_table: {}".format(df.shape[0]))
  return df

#############################################################################
def TDLCounts(dbcon, fout=None):
  sql="SELECT tdl, COUNT(id) AS target_count FROM target GROUP BY tdl"
  df = read_sql_query(sql, dbcon)
  if fout: df.to_csv(fout, "\t", index=False)
  return df

#############################################################################
def AttributeCounts(dbcon, fout=None):
  sql='SELECT ga.type, COUNT(ga.id) FROM gene_attribute ga GROUP BY ga.type'
  df = read_sql_query(sql, dbcon)
  if fout: df.to_csv(fout, "\t", index=False)
  return df

#############################################################################
def XrefCounts(dbcon, fout=None):
  sql = ('SELECT xtype, COUNT(DISTINCT value) FROM xref GROUP BY xtype ORDER BY xtype')
  df = read_sql_query(sql, dbcon)
  if fout: df.to_csv(fout, "\t", index=False)
  return df

#############################################################################
def ListXrefTypes(dbcon, fout=None):
  sql='SELECT DISTINCT xtype FROM xref ORDER BY xtype'
  df = read_sql_query(sql, dbcon)
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info("n_xreftypes: {}".format(df.shape[0]))
  return df

#############################################################################
def ListXrefs(dbcon, xreftypes, fout):
  if xreftypes and type(xreftypes) not in (list, tuple):
    xreftypes = [xreftypes]
  cols=['target_id', 'protein_id', 'xtype', 'value'] 
  sql = "SELECT DISTINCT {} FROM xref".format(", ".join(cols))
  if xreftypes:
    sql += " WHERE xtype IN ({})".format("'"+("','".join(xreftypes)+"'"))
  logging.debug("SQL: \"{}\"".format(sql))
  df = read_sql_query(sql, dbcon)
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info('Target count: %d'%(df.target_id.nunique()))
  logging.info('Protein count: %d'%(df.protein_id.nunique()))
  logging.info('XrefType count: %d'%(df.xtype.nunique()))
  logging.info('Xref count: %d'%(df.value.nunique()))
  return df

#############################################################################
def ListTargetFamilies(dbcon, fout=None):
  sql='SELECT DISTINCT fam TargetFamily FROM target ORDER BY fam'
  df = read_sql_query(sql, dbcon)
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info("n_tfams: {}".format(df.shape[0]))
  return df

#############################################################################
def ListTargets(dbcon, tdls, tfams, fout):
  sql='''
SELECT
	target.id tcrdTargetId,
	target.name tcrdTargetName,
	target.fam tcrdTargetFamily,
	target.tdl TDL,
	target.ttype tcrdTargetType,
	target.idg idgList,
	protein.id tcrdProteinId,
	protein.sym tcrdGeneSymbol,
	protein.family tcrdProteinFamily,
	protein.geneid ncbiGeneId,
	protein.uniprot uniprotId,
	protein.up_version uniprotVersion,
	protein.chr,
	protein.description tcrdProteinDescription,
	protein.dtoid dtoId,
	protein.dtoclass dtoClass,
	protein.stringid ensemblProteinId,
	xref.value ensemblGeneId
FROM
	target
JOIN
	t2tc ON t2tc.target_id = target.id
JOIN
	protein ON protein.id = t2tc.protein_id
JOIN
	xref ON xref.protein_id = protein.id
'''
  wheres = ["xref.xtype = 'Ensembl'", "xref.value REGEXP '^ENSG'"]
  if tdls:
    wheres.append("target.tdl IN ({})".format("'"+("','".join(tdls))+"'"))
  if tfams:
    wheres.append("target.fam IN ({})".format("'"+("','".join(tfams))+"'"))
  if wheres:
    sql+=(' WHERE '+(' AND '.join(wheres)))
  df = read_sql_query(sql, dbcon)
  if tdls: logging.info('TDLs: {}'.format(",".join(tdls)))
  if tfams: logging.info('TargetFamilies: {}'.format(",".join(tfams)))
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info('rows: {}'.format(df.shape[0]))
  logging.info('Target count: {}'.format(df.tcrdTargetId.nunique()))
  logging.info('Protein count: {}'.format(df.tcrdProteinId.nunique()))
  logging.info('Uniprot count: {}'.format(df.uniprotId.nunique()))
  logging.info('ENSP count: {}'.format(df.ensemblProteinId.nunique()))
  logging.info('ENSG count: {}'.format(df.ensemblGeneId.nunique()))
  logging.info('GeneSymbol count: {}'.format(df.tcrdGeneSymbol.nunique()))
  return df

#############################################################################
def GetTargetPage(dbcon, tid, fout):
  df = GetTargets(dbcon, [tid], "TID", None)
  target = df.to_dict(orient='records')
  fout.write(json.dumps(target, indent=2))

#############################################################################
def GetTargets(dbcon, ids, idtype, fout):
  cols=[
	'target.id',
	'target.name',
	'target.description',
	'target.fam',
	'target.tdl',
	'target.ttype',
	'protein.id',
	'protein.sym',
	'protein.uniprot',
	'protein.geneid',
	'protein.name',
	'protein.description',
	'protein.family',
	'protein.chr']
  sql='''\
SELECT
	{}
FROM
	target
JOIN
	t2tc ON target.id = t2tc.target_id
JOIN
	protein ON protein.id = t2tc.protein_id
'''.format(','.join(map(lambda s: '{} {}'.format(s, s.replace('.', '_')), cols)))

  n_id=0; n_hit=0; df=pd.DataFrame();
  for id_this in ids:
    n_id+=1
    wheres=[]
    if idtype.lower()=='tid':
      wheres.append('target.id = {}'.format(int(id_this)))
    elif idtype.lower()=='uniprot':
      wheres.append("protein.uniprot = '{}'".format(id_this))
    elif idtype.lower() in ('gid', 'geneid'):
      wheres.append("protein.geneid = '{}'".format(id_this))
    elif idtype.lower() in ('genesymb', 'genesymbol'):
      wheres.append("protein.sym = '{}'".format(id_this))
    elif idtype.lower() == 'ensp':
      wheres.append("protein.stringid = '{}'".format(id_this))
    else:
      logging.error('Unknown ID type: {}'.format(idtype))
      return
    sql_this = sql+(' WHERE '+(' AND '.join(wheres)))
    logging.debug('SQL: "{}"'.format(sql_this))
    logging.debug('ID: {} = "{}"'.format(idtype, id_this))
    df_this = read_sql_query(sql_this, dbcon)
    if df_this.shape[0]>0: n_hit+=1
    df = pd.concat([df, df_this])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info("n_id: {}; n_hit: {}".format(n_id, n_hit))
  return df

#############################################################################
def GetTargetsByXref(dbcon, ids, xreftypes, fout):
  if xreftypes and type(xreftypes) not in (list, tuple):
    xreftypes = [xreftypes]
  cols=[ 'target.description',
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
	'protein.uniprot',
	'xref.xtype',
	'xref.value']
  sql='''\
SELECT
	{}
FROM
	target
JOIN
	t2tc ON target.id = t2tc.target_id
JOIN
	protein ON protein.id = t2tc.protein_id
JOIN
	xref ON xref.protein_id = protein.id
'''.format(','.join(map(lambda s: '{} {}'.format(s, s.replace('.', '_')), cols)))

  n_id=0; n_hit=0; df=pd.DataFrame();
  for id_this in ids:
    n_id+=1
    wheres=[]
    wheres.append("xref.xtype IN ({})".format("'"+("','".join(xreftypes))+"'"))
    wheres.append("xref.value = '{}'".format(id_this))
    sql_this = sql+('WHERE '+(' AND '.join(wheres)))
    logging.debug('SQL: "{}"'.format(sql_this))
    df_this = read_sql_query(sql_this, dbcon)
    if df_this.shape[0]>0:
      n_hit+=1
    df = pd.concat([df, df_this])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info("n_id: {}; n_hit: {}".format(n_id, n_hit))
  return df

#############################################################################
def GetPathways(dbcon, ids, fout):
  n_id=0; n_hit=0; df=pd.DataFrame();
  cols=[ 't2p.target_id',
	't2p.id',
	't2p.source',
	't2p.id_in_source',
	't2p.name',
	't2p.description',
	't2p.url' ]
  sql = "SELECT {} FROM target2pathway t2p JOIN target t ON t.id = t2p.target_id".format(','.join(map(lambda s: '{} {}'.format(s, s.replace('.', '_')), cols)))
  pids_all=set();
  for id_this in ids:
    n_id+=1
    sql_this = sql+("WHERE t.id = {}".format(id_this))
    logging.debug('SQL: "{}"'.format(sql_this))
    df_this = read_sql_query(sql_this, dbcon)
    if df_this.shape[0]>0: n_hit+=1
    df = pd.concat([df, df_this])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info("n_query: {}; n_hit: {}".format(n_query, n_hit))
  return df

#############################################################################
