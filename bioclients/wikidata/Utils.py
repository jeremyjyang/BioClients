#!/usr/bin/env python3
"""
https://www.wikidata.org/wiki/User:ProteinBoxBot/SPARQL_Examples

PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX bd: <http://www.bigdata.com/rdf#>
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX uniprotkb:<http://purl.uniprot.org/uniprot/>
"""
###
import sys,os,logging
import pandas as pd
from wikidataintegrator import wdi_core, wdi_login

#############################################################################
def Rq2Df(rq):
  logging.debug(f"{rq}")
  r = wdi_core.WDItemEngine.execute_sparql_query(rq)['results']['bindings']
  df = pd.DataFrame([{k:v['value'] for k,v in item.items()} for item in r])
  logging.debug(f"rows: {df.shape[0]}; cols: {df.shape[1]}")
  return(df)

#############################################################################
def Query(rq, fout=None):
  df = Rq2Df(rq)
  if fout is not None: df.to_csv(fout, '\t', index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

#############################################################################
def ListDrugTargetPairs(fout=None):
  "List drugs with known targets."
  rq = """SELECT DISTINCT ?drug ?drugLabel ?gene_product ?gene_productLabel
WHERE {
  ?drug wdt:P129 ?gene_product . 
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
}"""
  df = Rq2Df(rq)
  if fout is not None: df.to_csv(fout, '\t', index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

#############################################################################
def ListGeneDiseasePairs(fout=None):
  "List genes with associated diseases."
  rq = """SELECT DISTINCT ?gene ?geneLabel ?disease ?diseaseLabel
WHERE {
  ?gene wdt:P2293 ?disease . 
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
}"""
  df = Rq2Df(rq)
  if fout is not None: df.to_csv(fout, '\t', index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

#############################################################################
def Test(fout=None):
  rq = """SELECT ?item ?itemLabel
WHERE {
  ?item wdt:P279 wd:Q1049021 .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
}"""
  df = Rq2Df(rq)
  if fout is not None: df.to_csv(fout, '\t', index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

#############################################################################
