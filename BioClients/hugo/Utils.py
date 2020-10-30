#!/usr/bin/env python3
##############################################################################
### hugo_utils.py - utility functions for HUGO REST API.
### See: http://www.genenames.org/help/rest-web-service-help
##############################################################################
import sys,os,re,json,time,logging
import pandas as pd

from ..util import rest
#
API_HOST='rest.genenames.org'
API_BASE_PATH=''
BASE_URL='http://'+API_HOST+API_BASE_PATH
#
OFMTS={'XML':'application/xml','JSON':'application/json'}
#
HEADERS={'Accept':OFMTS['JSON']}
#
GENE_TAGS=[
	"alias_symbol",
	"ena",
	"ensembl_gene_id",
	"entrez_id",
	"gene_family",
	"hgnc_id",
	"location",
	"locus_group",
	"locus_type",
	"name",
	"prev_name",
	"prev_symbol",
	"refseq_accession",
	"status",
	"symbol",
	"ucsc_id",
	"uniprot_ids",
	"uuid",
	"vega_id"
	]
#
##############################################################################
def GetGene(qry, ftype, base_url=BASE_URL):
  rval = rest.Utils.GetURL(base_url+'/fetch/{}/{}'.format(ftype.lower(), qry), headers=HEADERS, parse_json=True)
  if type(rval) is not dict: return None
  return rval

##############################################################################
def GetGenes(qrys, ftypes, found_only, skip, base_url=BASE_URL, fout=None):
  '''The API can return multiple hits for each query, though should not 
for exact SYMBOL fetch.  One case is for RPS15P5, status "Entry Withdrawn".'''
  n_in=0;	#queries
  n_found=0;	#queries found (1+ genes)
  n_notfound=0;	#queries not found
  n_ambig=0;	#ambiguous queries
  n_gene=0;	#total gene records returned
  logging.debug('ftypes[%d]: %s'%(len(ftypes), (','.join(ftypes))))
  fout.write(','.join(['query', 'query_type']+GENE_TAGS)+'\n')
  for qry in qrys:
    n_in+=1
    if n_in<skip: continue
    logging.debug('%d. query: %s'%(n_in, qry))
    numFound=0; genes=[];
    ftype_hit=None
    for ftype in ftypes:
      rval = GetGene(qry, ftype, base_url)
      ftype_hit=ftype
      responseHeader = rval['responseHeader']
      logging.debug('response status = %d'%(responseHeader['status']))
      response = rval['response'] 
      numFound = response['numFound'] if 'numFound' in response else 0
      genes = response['docs']
      if numFound>0: break

    if numFound==0:
      n_notfound+=1
      logging.debug('Not found: %s = %s'%(ftype_hit, qry))
      if not found_only:
        fout.write(','.join(map(lambda s:'"%s"'%s, [qry, ('|'.join(ftypes))]+['' for j in range(len(GENE_TAGS))]))+'\n')
      continue
    elif numFound>0:
      n_found+=1

    if len(genes)>1:
      logging.debug('Warning: multiple (%d) hits, %s = %s (Duplicate may be status=withdrawn.)'%(len(genes), ftype_hit, qry))
      n_ambig+=1

    for gene in genes:
      vals=[qry, ftype_hit]
      for tag in GENE_TAGS:
        val = gene[tag] if tag in gene else ''
        if type(val) is list: val = ';'.join(val)
        vals.append(val)
      fout.write(','.join(map(lambda s:'"%s"'%s, vals))+'\n')
      n_gene+=1

  logging.info('queries: %d ; found: %d ; not found: %d ; ambiguous: %d ; total genes returned: %d'%(n_in-skip, n_found, n_notfound, n_ambig, n_gene))
  return n_in-skip, n_found

##############################################################################
def SearchGenes(qrys, ftypes, base_url=BASE_URL, fout=None):
  n_in=0; n_found=0; tags=[]; df=None;
  for qry in qrys:
    n_in+=1
    logging.debug('{}. query: {}'.format(n_in, qry))
    found_this=False
    for ftype in ftypes:
      url = (base_url+'/search{}/*{}*'.format((('/'+ftype.lower()) if ftype else ''), qry))
      rval = rest.Utils.GetURL(url, headers=HEADERS, parse_json=True)
      responseHeader = rval['responseHeader']
      logging.debug('response status = {}'.format(responseHeader['status']))
      response = rval['response'] 
      numFound = response['numFound'] if 'numFound' in response else 0
      if numFound==0: continue
      found_this=True
      logging.debug(json.dumps(response, sort_keys=True, indent=2)+'\n')
      if not tags: tags = list(response.keys())
      df_this = pd.DataFrame({tags[j]:[response[tags[j]]] for j in range(len(tags))})
      df = pd.concat([df, df_this])
    if found_this: n_found+=1
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info('queries: {}; found: {}'.format(n_in, n_found))
  return df

##############################################################################
def ListSearchableFields(base_url=BASE_URL, fout=None):
  rval = rest.Utils.GetURL(base_url+'/info', headers=HEADERS, parse_json=True)
  fields = rval['searchableFields'] if 'searchableFields' in rval else None
  fields.sort()
  df = pd.DataFrame({'fields':fields})
  if fout: df.to_csv(fout, "\t", index=False)
  return df

