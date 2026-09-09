#!/usr/bin/env python3
"""
Access to Ensembl biomart REST API.
https://m.ensembl.org/info/data/biomart/biomart_restful.html
"""
import sys,os,re,time,json,logging,tqdm,io
import pandas as pd
import requests, urllib.parse
#
API_HOST='www.ensembl.org'
API_BASE_PATH='/biomart/martservice'
#
BASE_URL='http://'+API_HOST+API_BASE_PATH
#
ENSG2NCBI_xml="""\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE Query>
<Query  virtualSchemaName = "default" formatter = "TSV" header = "1" uniqueRows = "0" count = "" datasetConfigVersion = "0.6" >

	<Dataset name = "hsapiens_gene_ensembl" interface = "default" >
		<Attribute name = "ensembl_gene_id" />
		<Attribute name = "ensembl_gene_id_version" />
		<Attribute name = "entrezgene_id" />
	</Dataset>
</Query>
"""
#
ENSG2HGNC_xml="""\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE Query>
<Query  virtualSchemaName = "default" formatter = "TSV" header = "1" uniqueRows = "0" count = "" datasetConfigVersion = "0.6" >

	<Dataset name = "hsapiens_gene_ensembl" interface = "default" >
		<Attribute name = "ensembl_gene_id" />
		<Attribute name = "ensembl_gene_id_version" />
		<Attribute name = "hgnc_id" />
		<Attribute name = "hgnc_symbol" />
	</Dataset>
</Query>
"""
#
ENSG2NCBIHGNC_xml="""\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE Query>
<Query  virtualSchemaName = "default" formatter = "TSV" header = "1" uniqueRows = "0" count = "" datasetConfigVersion = "0.6" >

	<Dataset name = "hsapiens_gene_ensembl" interface = "default" >
		<Attribute name = "ensembl_gene_id" />
		<Attribute name = "ensembl_gene_id_version" />
		<Attribute name = "entrezgene_id" />
		<Attribute name = "hgnc_id" />
		<Attribute name = "hgnc_symbol" />
	</Dataset>
</Query>
"""
#
##############################################################################
def XMLQuery(xmltxt, base_url=BASE_URL, fout=None):
  url_this = base_url+f"?query={urllib.parse.quote(xmltxt)}"
  logging.debug(url_this)
  rval = requests.get(url_this)
  if not rval.ok:
    logging.error(f"{rval.status_code}")
    logging.debug(rval.text)
    return None
  df = pd.read_table(io.StringIO(rval.text), sep="\t")
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"Output rows: {df.shape[0]}; cols: {df.shape[1]} ({str(df.columns.tolist())})")
  return df

##############################################################################
def ENSG2NCBI(base_url=BASE_URL, fout=None):
  return XMLQuery(ENSG2NCBI_xml, base_url, fout)

##############################################################################
def ENSG2HGNC(base_url=BASE_URL, fout=None):
  return XMLQuery(ENSG2HGNC_xml, base_url, fout)

##############################################################################
def ENSG2NCBIHGNC(base_url=BASE_URL, fout=None):
  return XMLQuery(ENSG2NCBIHGNC_xml, base_url, fout)

##############################################################################
