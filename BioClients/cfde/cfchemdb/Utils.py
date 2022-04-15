#!/usr/bin/env python3
"""
CFChemDb utility functions.
"""
import os,sys,re,json,logging,yaml,tqdm
import pandas as pd
import psycopg2,psycopg2.extras

NCHUNK=100

#############################################################################
def Connect(dbhost, dbport, dbname, dbusr, dbpw):
  """Connect to db; specify default cursor type DictCursor."""
  dsn = (f"host='{dbhost}' port='{dbport}' dbname='{dbname}' user='{dbusr}' password='{dbpw}'")
  dbcon = psycopg2.connect(dsn)
  dbcon.cursor_factory = psycopg2.extras.DictCursor
  return dbcon

#############################################################################
def Version(dbcon, dbschema="public", fout=None):
  sql = (f"SELECT * FROM {dbschema}.dbversion")
  logging.debug(f"SQL: {sql}")
  df = pd.read_sql(sql, dbcon)
  if fout: df.to_csv(fout, "\t", index=False)
  return df

#############################################################################
def MetaListdbs(dbcon, fout=None):
  """Pg meta-command: list dbs from pg_database."""
  sql = ("SELECT pg_database.datname, pg_shdescription.description FROM pg_database LEFT OUTER JOIN pg_shdescription on pg_shdescription.objoid = pg_database.oid WHERE pg_database.datname ~ '^drug'")
  logging.debug(f"SQL: {sql}")
  df = pd.read_sql(sql, dbcon)
  if fout: df.to_csv(fout, "\t", index=False)
  return df

#############################################################################
def ListColumns(dbcon, dbschema="public", fout=None):
  df=None;
  sql1 = (f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{dbschema}'")
  df1 = pd.read_sql(sql1, dbcon)
  for tname in df1.table_name:
    sql2 = (f"SELECT column_name,data_type FROM information_schema.columns WHERE table_schema = '{dbschema}' AND table_name = '{tname}'")
    df_this = pd.read_sql(sql2, dbcon)
    df_this["schema"] = dbschema
    df_this["table"] = tname
    df = df_this if df is None else pd.concat([df, df_this])
  df = df[["schema", "table", "column_name", "data_type"]]
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

#############################################################################
def ListTables(dbcon, dbschema="public", fout=None):
  '''Listing the tables.'''
  sql = (f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{dbschema}'")
  df = pd.read_sql(sql, dbcon)
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

#############################################################################
def ListTablesRowCounts(dbcon, dbschema="public", fout=None):
  '''Listing the table rowcounts.'''
  df=None;
  sql1 = (f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{dbschema}'")
  df1 = pd.read_sql(sql1, dbcon)
  for tname in df1.table_name:
    sql2 = (f"SELECT COUNT(*) AS rowcount FROM {dbschema}.{tname}")
    df_this = pd.read_sql(sql2, dbcon)
    df_this["schema"] = dbschema
    df_this["table"] = tname
    df = df_this if df is None else pd.concat([df, df_this])
  df = df[["schema", "table", "rowcount"]]
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

#############################################################################
def ListStructures(dbcon, dbschema="public", fout=None):
  sql = (f"SELECT id,name,cansmi FROM {dbschema}.mols")
  logging.debug(f"SQL: {sql}")
  df = pd.read_sql(sql, dbcon)
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

#############################################################################
def ListStructures2Smiles(dbcon, dbschema="public", fout=None):
  sql = (f"SELECT cansmi, id, name FROM {dbschema}.mols WHERE cansmi IS NOT NULL")
  logging.debug(f"SQL: {sql}")
  df = pd.read_sql(sql, dbcon)
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

#############################################################################
def GetStructure(dbcon, ids, fout=None):
  df=None; n_out=0;
  sql = ("""SELECT id,name,cansmi FROM mols WHERE id = '{}'""")
  for id_this in ids:
    logging.debug(sql.format(id_this))
    df_this = pd.read_sql(sql.format(id_this), dbcon)
    if fout is not None: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
    else: df = df_this if df is None else pd.concat([df, df_this])
    n_out+=1
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"n_out: {n_out}/{len(ids)}")
  return df

#############################################################################
def GetStructureBySmiles(dbcon, smis, fout=None):
  """Casting smiles to MOL canonicalizes molecular graph for isomorphism eval."""
  df=None; n_out=0; n_not_found=0;
  sql = ("""SELECT id,name,cansmi FROM mols WHERE mols.molecule = '{}'::MOL""")
  for smi_this in smis:
    smi_this = re.sub(r'\s.*$', '', smi_this)
    logging.debug(sql.format(smi_this))
    try:
      df_this = pd.read_sql(sql.format(smi_this), dbcon)
    except Exception as e:
      logging.error(f"{e}")
      continue
    if fout is not None: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
    else: df = df_this if df is None else pd.concat([df, df_this])
    if df_this.shape[0]==0:
      n_not_found+=1
    n_out+=df_this.shape[0]
  logging.info(f"n_found: {len(smis)-n_not_found}/{len(smis)}; n_not_found: {n_not_found}/{len(smis)}; n_out: {n_out}")
  return df

#############################################################################
