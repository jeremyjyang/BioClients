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
  logging.info(f"n_table: {df.shape[0]}")
  return df

#############################################################################
def ListDatasets(dbcon, fout=None):
  sql = 'SELECT * FROM dataset'
  df = read_sql_query(sql, dbcon)
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"n_table: {df.shape[0]}")
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
  logging.info(f"n_columns: {df.shape[0]}; n_tables: {df.table.nunique()}")
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
  logging.info(f"n_table: {df.shape[0]}")
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
  logging.info(f"n_xreftypes: {df.shape[0]}")
  return df

#############################################################################
def ListXrefs(dbcon, xreftypes, fout):
  if xreftypes and type(xreftypes) not in (list, tuple):
    xreftypes = [xreftypes]
  cols=['target_id', 'protein_id', 'xtype', 'value'] 
  sql = f"""SELECT DISTINCT {(", ".join(cols))} FROM xref"""
  if xreftypes:
    sql += f""" WHERE xtype IN ({("'"+("','".join(xreftypes)+"'"))})"""
  logging.debug(f'SQL: "{sql}"')
  df = read_sql_query(sql, dbcon)
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"Target count: {df.target_id.nunique()}")
  logging.info(f"Protein count: {df.protein_id.nunique()}")
  logging.info(f"XrefType count: {df.xtype.nunique()}")
  logging.info(f"Xref count: {df.value.nunique()}")
  return df

#############################################################################
def ListTargetFamilies(dbcon, fout=None):
  sql="SELECT DISTINCT fam TargetFamily FROM target ORDER BY fam"
  df = read_sql_query(sql, dbcon)
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"n_tfams: {df.shape[0]}")
  return df

#############################################################################
def ListTargets(dbcon, tdls, tfams, fout):
  sql = """
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
	x.value ensemblGeneId
FROM
	target
LEFT OUTER JOIN
	t2tc ON t2tc.target_id = target.id
LEFT OUTER JOIN
	protein ON protein.id = t2tc.protein_id
LEFT OUTER JOIN
	(SELECT * FROM xref WHERE xref.xtype = 'Ensembl' AND xref.value REGEXP '^ENSG'
	) x ON x.protein_id = protein.id
"""
  wheres=[]
  if tdls: wheres.append(f"""target.tdl IN ({("'"+("','".join(tdls))+"'")})""")
  if tfams: wheres.append(f"""target.fam IN ({("'"+("','".join(tfams))+"'")})""")
  if wheres: sql+=(' WHERE '+(' AND '.join(wheres)))
  logging.debug(sql)
  df = read_sql_query(sql, dbcon)
  if tdls: logging.info(f"""TDLs: {",".join(tdls)}""")
  if tfams: logging.info(f"""TargetFamilies: {",".join(tfams)}""")
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"rows: {df.shape[0]}")
  logging.info(f"Target count: {df.tcrdTargetId.nunique()}")
  logging.info(f"Protein count: {df.tcrdProteinId.nunique()}")
  logging.info(f"Uniprot count: {df.uniprotId.nunique()}")
  logging.info(f"ENSP count: {df.ensemblProteinId.nunique()}")
  logging.info(f"ENSG count: {df.ensemblGeneId.nunique()}")
  logging.info(f"GeneSymbol count: {df.tcrdGeneSymbol.nunique()}")
  return df

#############################################################################
def ListTargetsByDTO(dbcon, fout):
  sql = """
SELECT DISTINCT
	target.id tcrdTargetId,
	target.name tcrdTargetName,
	target.fam tcrdTargetFamily,
	protein.id tcrdProteinId,
	protein.sym tcrdGeneSymbol,
	CONVERT(protein.geneid, CHAR) ncbiGeneId,
	protein.uniprot uniprotId,
	p2dto.dtoid dtoId,
	CONVERT(p2dto.generation, CHAR) dtoGeneration,
	dto.name dtoClass
FROM
	target
	JOIN t2tc ON t2tc.target_id = target.id
	JOIN protein ON protein.id = t2tc.protein_id
	LEFT OUTER JOIN p2dto ON p2dto.protein_id = protein.id
	LEFT OUTER JOIN dto ON dto.dtoid = p2dto.dtoid
ORDER BY
	target.id, protein.id, p2dto.generation DESC
"""
  logging.debug(sql)
  df = read_sql_query(sql, dbcon, coerce_float=False)
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"rows: {df.shape[0]}")
  logging.info(f"Target count: {df.tcrdTargetId.nunique()}")
  logging.info(f"Protein count: {df.tcrdProteinId.nunique()}")
  logging.info(f"Uniprot count: {df.uniprotId.nunique()}")
  logging.info(f"GeneSymbol count: {df.tcrdGeneSymbol.nunique()}")
  logging.info(f"DTO_ID count: {df.dtoId.nunique()}")
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
  sql = f"""\
SELECT
	{(','.join(map(lambda s: (s+" "+s.replace('.', '_')), cols)))}
FROM
	target
LEFT OUTER JOIN
	t2tc ON target.id = t2tc.target_id
LEFT OUTER JOIN
	protein ON protein.id = t2tc.protein_id
"""

  n_id=0; n_hit=0; df=pd.DataFrame();
  for id_this in ids:
    n_id+=1
    wheres=[]
    if idtype.lower()=='tid':
      wheres.append(f"target.id = {id_this}")
    elif idtype.lower()=='uniprot':
      wheres.append(f"protein.uniprot = '{id_this}'")
    elif idtype.lower() in ('gid', 'geneid'):
      wheres.append(f"protein.geneid = '{id_this}'")
    elif idtype.lower() in ('genesymb', 'genesymbol'):
      wheres.append(f"protein.sym = '{id_this}'")
    elif idtype.lower() == 'ensp':
      wheres.append(f"protein.stringid = '{id_this}'")
    else:
      logging.error(f'Unknown ID type: {idtype}')
      return
    sql_this = sql+(' WHERE '+(' AND '.join(wheres)))
    logging.debug(f'SQL: "{sql_this}"')
    logging.debug(f'ID: {idtype} = "{id_this}"')
    df_this = read_sql_query(sql_this, dbcon)
    if df_this.shape[0]>0: n_hit+=1
    df = pd.concat([df, df_this])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"n_id: {n_id}; n_hit: {n_hit}")
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
  sql = f"""\
SELECT
	{(','.join(map(lambda s: s+" "+s.replace('.', '_')), cols))}
FROM
	target
JOIN
	t2tc ON target.id = t2tc.target_id
JOIN
	protein ON protein.id = t2tc.protein_id
JOIN
	xref ON xref.protein_id = protein.id
""" 

  n_id=0; n_hit=0; df=pd.DataFrame();
  for id_this in ids:
    n_id+=1
    wheres=[]
    wheres.append(f"""xref.xtype IN ({("'"+("','".join(xreftypes))+"'")})""")
    wheres.append(f"xref.value = '{id_this}'")
    sql_this = sql+('WHERE '+(' AND '.join(wheres)))
    logging.debug(f'SQL: "{sql_this}"')
    df_this = read_sql_query(sql_this, dbcon)
    if df_this.shape[0]>0:
      n_hit+=1
    df = pd.concat([df, df_this])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"n_id: {n_id}; n_hit: {n_hit}")
  return df

#############################################################################
def GetPathways(dbcon, ids, fout):
  n_id=0; n_hit=0; df=pd.DataFrame(); pids_all=set();
  cols=[ 't2p.target_id',
	't2p.id',
	't2p.source',
	't2p.id_in_source',
	't2p.name',
	't2p.description',
	't2p.url' ]
  sql = f"""SELECT {(','.join(map(lambda s: s+" "+s.replace('.', '_')), cols))} FROM target2pathway t2p JOIN target t ON t.id = t2p.target_id"""
  for id_this in ids:
    n_id+=1
    sql_this = sql+(f"WHERE t.id = {id_this}")
    logging.debug(f'SQL: "{sql_this}"')
    df_this = read_sql_query(sql_this, dbcon)
    if df_this.shape[0]>0: n_hit+=1
    df = pd.concat([df, df_this])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"n_query: {n_query}; n_hit: {n_hit}")
  return df

#############################################################################
def ListDiseases(dbcon, fout):
  sql="""
SELECT
	d.dtype,
	dt.description dtype_description,
	d.name diseaseName,
	d.ncats_name ncatsDiseaseName,
	d.did diseaseId,
	d.description diseaseDescription,
	d.reference,
	d.drug_name,
	d.source,
	COUNT(d.protein_id) n_target_associations
FROM
	disease d
	LEFT OUTER JOIN disease_type dt ON dt.name = d.dtype
GROUP BY
	d.dtype,
	dt.description,
	d.name,
	d.ncats_name,
	d.did,
	d.description,
	d.reference,
	d.drug_name,
	d.source
"""
  df = read_sql_query(sql, dbcon)
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"rows: {df.shape[0]}")
  logging.info(f"diseaseIDs: {df.diseaseId.nunique()}")
  logging.info(f"diseaseNames: {df.diseaseName.nunique()}")
  logging.info(f"ncatsDiseaseNames: {df.ncatsDiseaseName.nunique()}")
  for dtype in df.dtype.unique().tolist():
    logging.info(f"[{dtype}] diseaseIDs: {df[df.dtype==dtype].diseaseId.nunique()}")
  return df

#############################################################################
def ListDiseaseTypes(dbcon, fout):
  df = ListDiseases(dbcon, None)
  df = df[["dtype", "dtype_description", "n_target_associations"]]
  df = df.groupby(["dtype", "dtype_description"]).sum()
  df.reset_index(drop=False, inplace=True)
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"rows: {df.shape[0]}")
  return df

#############################################################################
def ListPhenotypes(dbcon, fout):
  sql="""
SELECT
	p.ptype,
        CONCAT(IF(INSTR(IFNULL(p.trait, ""), ';')>0, SUBSTR(IFNULL(p.trait, ""), 1, INSTR(IFNULL(p.trait, ""), ';')-1), IFNULL(p.trait, "")),IFNULL(p.term_id, "")) p_identifier,
        p.term_name,
        p.term_description,
	pt.ontology ptype_ontology,
	pt.description ptype_description,
	COUNT(p.protein_id) n_target_associations
FROM
	phenotype p
	JOIN phenotype_type pt ON pt.name = p.ptype
GROUP BY
	p.ptype,
        p_identifier,
        p.term_name,
        p.term_description,
	pt.ontology,
	pt.description
"""
  df = read_sql_query(sql, dbcon)
  df.loc[((df['ptype']=='OMIM') & ((df['ptype_ontology']=='')|(df['ptype_ontology'].isna()))),'ptype_ontology'] = 'OMIM' # Kludge
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"rows: {df.shape[0]}")
  for ptype in df.ptype.unique().tolist():
    logging.info(f"[{ptype}] phenotype_IDs: {df[df.ptype==ptype].p_identifier.nunique()}")
  return df

#############################################################################
def ListPhenotypeTypes(dbcon, fout):
  df = ListPhenotypes(dbcon, None)
  df = df[["ptype", "ptype_ontology", "n_target_associations"]]
  df = df.groupby(["ptype", "ptype_ontology"]).sum()
  df.reset_index(drop=False, inplace=True)
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"rows: {df.shape[0]}")
  return df

#############################################################################
