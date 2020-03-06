#!/usr/bin/env python3
##############################################################################
### hugo_utils.py - utility functions for HUGO REST API.
### See: http://www.genenames.org/help/rest-web-service-help
##############################################################################
import sys,os,re,json,time,logging

from ..util import rest_utils
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
def GetGene(qry, ftype, base_url):
  rval=None
  try:
    rval=rest_utils.GetURL(base_url+'/fetch/%s/%s'%(ftype.lower(), qry), headers=HEADERS, parse_json=True)
  except Exception as e:
    logging.error('%s'%(e))
  if type(rval) is not dict: return None
  return rval

##############################################################################
def GetGenes(qrys, ftypes, base_url, fout, found_only, skip):
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

      try:
        responseHeader = rval['responseHeader']
        logging.debug('response status = %d'%(responseHeader['status']))
        response = rval['response'] 
        numFound = response['numFound'] if 'numFound' in response else 0
        genes = response['docs']
      except Exception as e:
        logging.error('%s'%(e))

      if numFound>0:
        break

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
def SearchGenes(qrys, ftype, base_url, fout):
  n_in=0; n_found=0;
  for qry in qrys:
    n_in+=1
    logging.debug('%d. query: %s'%(n_in, qry))
    url = (base_url+'/search%s/*%s*'%((('/'+ftype.lower()) if ftype else ''), qry))
    try:
      rval=rest_utils.GetURL(url, headers=HEADERS, parse_json=True)
    except Exception as e:
      logging.error('%s'%(e))

    responseHeader = rval['responseHeader']
    logging.debug('response status = %d'%(responseHeader['status']))
    response = rval['response'] 
    numFound = response['numFound'] if 'numFound' in response else 0
    if numFound>0:
      n_found+=1
    fout.write(json.dumps(response, sort_keys=True, indent=2)+'\n')

  return n_in,n_found

##############################################################################
def SearchableFieldsList(base_url):
  try:
    rval=rest_utils.GetURL(base_url+'/info', headers=HEADERS, parse_json=True)
  except Exception as e:
    logging.error('%s'%(e))
  fields = rval['searchableFields'] if 'searchableFields' in rval else None
  fields.sort()
  return fields

