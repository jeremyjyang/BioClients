#!/usr/bin/env python3
"""
https://py2neo.org/
https://py2neo.org/v4/database.html
"""
import sys,os,json,logging
import pandas as pd
import py2neo

DBHOST="localhost"
DBPORT=7687
DBSCHEME="bolt"
DBUSR="neo4j"
DBPW="neo4j"

#############################################################################
def DbConnect(dbhost=DBHOST, dbport=DBPORT, dbscheme=DBSCHEME, dbusr=DBUSR, dbpw=DBPW, secure=False):
  db=None;
  try:
    db = py2neo.GraphService(host=dbhost, port=dbport, scheme=dbscheme, secure=secure, user=dbusr, password=dbpw)
  except Exception as e:
    logging.error(f"{e}")
  return db

#############################################################################
def DbInfo(db, fout):
  logging.debug(f"db.config: {db.config}")
  df = pd.DataFrame({"uri": [db.uri],
	"kernel_version": [db.kernel_version],
	"default_graph": [db.default_graph],
	"product": [db.product]})
  df.transpose().to_csv(fout, sep="\t")

#############################################################################
def DbSummary(db, fout):
  g = db.default_graph
  df = pd.DataFrame({"nodes": [len(g.nodes)],
	"relationships": [len(g.relationships)],
	"schema": [g.schema],
	})
  df.transpose().to_csv(fout, sep="\t")

#############################################################################
def DbQuery(db, cql, fmt, fout):
  n_out=0;
  g = db.default_graph
  result = g.run(cql)
  if fmt.upper()=='JSON':
    rows = result.data()
    n_out = len(rows)
    fout.write(json.dumps(rows, indent=2)+'\n')
  else: #TSV
    df = result.to_data_frame()
    n_out = df.shape[0]
    df.to_csv(fout, '\t', index=False)
  logging.info(f"rows: {n_out}")

#############################################################################
