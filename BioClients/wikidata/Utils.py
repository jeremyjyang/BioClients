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
from wikidataintegrator.wdi_core import WDItemEngine

#############################################################################
def Rq2Df(rq):
  r = WDItemEngine.execute_sparql_query(rq)['results']['bindings']
  df = pd.DataFrame([{k:v['value'] for k,v in item.items()} for item in r])
  logging.debug("df.shape: {},{}".format(df.shape[0], df.shape[1]))
  return(df)

#############################################################################
def ListDrugTargetPairs(fout):
  "List drugs with known targets."
  rq="""SELECT DISTINCT ?drug ?drugLabel ?gene_product ?gene_productLabel WHERE {
  ?drug wdt:P129 ?gene_product . 
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
}"""
  df = Rq2Df(rq)
  df.to_csv(fout, '\t', index=False)

#############################################################################
def ListGeneDiseasePairs(fout):
  "List genes with associated diseases."
  rq="""SELECT DISTINCT ?gene ?geneLabel ?disease ?diseaseLabel WHERE {
  ?gene wdt:P2293 ?disease . 
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
}"""
  df = Rq2Df(rq)
  df.to_csv(fout, '\t', index=False)

#############################################################################
def Test(fout):
  rq="""SELECT ?item ?itemLabel WHERE {
  ?item wdt:P279 wd:Q1049021 .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
}"""
  df = Rq2Df(rq)
  df.to_csv(fout, '\t', index=False)

#############################################################################
