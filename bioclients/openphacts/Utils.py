#!/usr/bin/env python3
##############################################################################
### Utility functions for OpenPHACTS REST API.
###
### formats: JSON, XML, TSV
###
### Ref: https://dev.openphacts.org/docs
###      https://dev.openphacts.org/docs/1.5
###      https://dev.openphacts.org/docs/2.0
###
### Top level resources:
###    /assay
###    /compound
###    /disease
###    /getConceptDescription
###    /mapUri
###    /pathway
###    /pharmacology
###    /search
###    /sources
###    /structure
###    /target
###    /tissue
###    /tree
##############################################################################
### From https://dev.openphacts.org/docs/develop
#  ?oidd_assay_uri a ?bao_type ;
#     skos:exactMatch ?pubchem_assay ;
#     void:inDataset <http://rdf.ncats.nih.gov/opddr> .
###
#  /assay?uri=http%3A%2F%2Fopeninnovation.lilly.com%2Fbioassay%2329"
##############################################################################
import sys,os,re,time,logging
import requests,json,urllib.parse
import pandas as pd
#
API_HOST='beta.openphacts.org'
API_BASE_PATH='/2.1'
#
##############################################################################
def ShowCounts(user_id, user_key, base_url):
  countpaths=[
	'/assay/members/count',
	'/pathways/count',
	'/pharmacology/filters/activities/count'
	]
  for countpath in countpaths:
    url = f"{base_url}{countpath}?app_id={user_id}&app_key={user_key}"
    response = requests.get(url)
    logging.debug(json.dumps(response.json(), sort_keys=True, indent=2))
    logging.info(f"{countpath}: {response.content}")
#
##############################################################################
def ListPathways(user_id, user_key, base_url, fout):
  url = base_url+'/pathways?'
  url+=('&app_id=%s&app_key=%s'%(user_id,user_key))
  url+=('&_format=tsv')
  response = requests.get(url)
  logging.debug(json.dumps(response.json(), sort_keys=True, indent=2))
  lines = response.content.splitlines()
  tags = re.split('\t', lines[0])
  tags = [csv_utils.ToStringForCSV(tag) for tag in tags]
  fout.write((','.join(tags))+'\n')
  n_pth=0; n_out=0;
  for line in lines[1:]:
    vals = re.split('\t', line)
    vals = [csv_utils.ToStringForCSV(val) for val in vals]
    fout.write((','.join(vals))+'\n')
    n_pth+=1
    n_out+=1
  logging.info('n_col: %d'%len(tags))
  logging.info('n_pth: %d'%n_pth)
  logging.info('n_out: %d'%n_out)

#############################################################################
def ListSources(user_id, user_key, base_url,fout):
  url=base_url+'/sources?'
  url+=('&app_id=%s&app_key=%s'%(user_id,user_key))
  url+=('&_format=json')
  response = requests.get(url)
  result = response.json()

  if type(result) is not dict:
    return

  logging.debug(json.dumps(result, indent=2))

  SRC_TAGS=['title','description','homepage','landingPage']
  SRC_SUB_TAGS=['url','title','type','description','landingPage','dataDump']
  fout.write('i,'+(','.join(SRC_TAGS+['sub:'+tag for tag in SRC_SUB_TAGS]))+'\n')

  result = result['result'] if result.has_key('result') else {}
  primaryTopic = result['primaryTopic'] if result.has_key('primaryTopic') else {}
  dbs = primaryTopic['subset'] if primaryTopic.has_key('subset') else []

  logging.debug('len(dbs) = %d '%len(dbs))

  n_db=0; n_out=0; n_err=0; n_subdb=0;
  for db in dbs:
    n_db+=1
    title = db['title'] if db.has_key('title') else ''
    logging.debug('db title = "%s"'%title)
    vals=[]
    for tag in SRC_TAGS:
      vals.append(csv_utils.ToStringForCSV(db[tag]) if db.has_key(tag) else '')

    subdbs  = db['subset'] if db.has_key('subset') else []

    if type(subdbs) is not list:
      logging.error('subdbs="%s"'%str(subdbs))
      n_err+=1
      continue

    n_subdb_this=0;
    for subdb in subdbs:
      n_subdb_this+=1
      if type(subdb) is not dict:
        logging.error('subdb="%s"'%str(subdb))
        fout.write(('%d.%d,'%(n_db,n_subdb_this))+(','.join(vals+['' for tag in SRC_SUB_TAGS[1:]]))+'\n')
        n_out+=1
        continue

      title = subdb['title'] if subdb.has_key('title') else ''
      logging.debug('subdb title = "%s"'%title)

      vals_this = vals[:]
      for tag in SRC_SUB_TAGS:
        vals_this.append(csv_utils.ToStringForCSV(subdb[tag]) if subdb.has_key(tag) else '')

      fout.write(('%d.%d,'%(n_db,n_subdb_this))+(','.join(vals_this))+'\n')
      n_out+=1

    if not subdbs and title:
      fout.write(('%d,'%n_db)+(','.join(vals+['' for tag in SRC_SUB_TAGS]))+'\n')
      n_out+=1
    n_subdb+=n_subdb_this

  logging.info( 'n_db: %d'%n_db)
  logging.info( 'n_subdb: %d'%n_subdb)
  logging.info( 'n_out: %d'%n_out)
  logging.info( 'n_err: %d'%n_err)

##############################################################################
def ListTargetTypes(user_id, user_key, base_url,fout):
  url=base_url+'/target/types?'
  url+=('&app_id=%s&app_key=%s'%(user_id,user_key))
  url+=('&_format=json')
  response = requests.get(url)
  result = response.json()

  if type(result) is not dict:
    logging.error('result not dict')
    return

  result = result['result']
  if type(result) is not dict:
    logging.error('result not dict')
    return

  pt = result['primaryTopic']
  if type(pt) is not dict:
    logging.error('primaryTopic not dict')
    return

  ttyps = result['result']['primaryTopic']['hasTargetType']

  n_typ=0; n_out=0; tags=[];
  for ttyp in  ttyps:
    if n_typ==0 or not tags:
      tags = ttyp.keys()
      fout.write(','.join([csv_utils.ToStringForCSV(tag) for tag in tags])+'\n')
    vals=[]
    for tag in tags:
      vals.append(ttyp[tag] if ttyp.has_key(tag) else '')

    fout.write(','.join([csv_utils.ToStringForCSV(val) for val in vals])+'\n')
    n_typ+=1
    n_out+=1

  logging.info( 'n_col: %d'%len(tags))
  logging.info( 'n_typ: %d'%n_typ)
  logging.info( 'n_out: %d'%n_out)

##############################################################################
def ListTargets(uri_qry,user_id, user_key, base_url,fout):
  '''URL must be from supported hierarchy such as Chembl.  http://purl.uniprot.org/enzyme/6.2.-.-'''
  url=base_url+'/target/members/pages?uri=%s'%urllib2.quote(uri_qry).replace('/','%2F')
  url+=('&app_id=%s&app_key=%s'%(user_id,user_key))
  url+=('&_format=json')
  pagesize=10;
  url+=('&_pageSize=%d'%pagesize)

  page=0;
  n_tgt=0; n_out=0; tags=[];

  while True:
    page+=1
    url_this = url+('&_page=%d'%page)
    response = requests.get(url_this)
    result = response.json()

    if not result: break

    if type(result) is not dict:
      logging.error('result not dict')
      break

    result = result['result']
    if type(result) is not dict:
      logging.error('result not dict')
      break

    tgts = result['result']['items']

    for tgt in  tgts:
      if n_tgt==0 or not tags:
        tags = tgt.keys()
        fout.write(','.join([csv_utils.ToStringForCSV(tag) for tag in tags])+'\n')
      vals=[]
      for tag in tags:
        vals.append(tgt[tag] if tgt.has_key(tag) else '')

      fout.write(','.join([csv_utils.ToStringForCSV(val) for val in vals])+'\n')
      n_tgt+=1
      n_out+=1

  logging.info( 'n_col: %d'%len(tags))
  logging.info( 'n_tgt: %d'%n_tgt)
  logging.info( 'n_out: %d'%n_out)

##############################################################################
def GetAssay(uri_qry, user_id, user_key, base_url,fout):
  url=base_url+'/assay?uri=%s'%urllib.parse.quote(uri_qry).replace('/','%2F')
  url+=('&app_id=%s&app_key=%s'%(user_id,user_key))
  url+=('&_format=tsv')
  response = requests.get(url)
  result = response.content

  lines = result.splitlines()
  tags = re.split('\t', lines[0])
  tags = [csv_utils.ToStringForCSV(tag) for tag in tags]
  fout.write((','.join(tags))+'\n')
  n_ass=0; n_out=0;
  for line in lines[1:]:
    vals = re.split('\t', line)
    vals = [csv_utils.ToStringForCSV(val) for val in vals]
    fout.write((','.join(vals))+'\n')
    n_ass+=1
    n_out+=1

  logging.info( 'n_col: %d'%len(tags))
  logging.info( 'n_ass: %d'%n_ass)
  logging.info( 'n_out: %d'%n_out)

#############################################################################
def GetInstance(resource, uri_qry, user_id, user_key, base_url, fout):
  url=base_url+'/%s?uri=%s'%(resource,urllib2.quote(uri_qry).replace('/','%2F'))
  url+=('&app_id=%s&app_key=%s'%(user_id,user_key))
  url+=('&_format=tsv')
  response = requests.get(url)
  result = response.content

  lines = result.splitlines()
  tags = re.split('\t', lines[0])
  tags = [csv_utils.ToStringForCSV(tag) for tag in tags]
  fout.write((','.join(tags))+'\n')
  n=0; n_out=0;
  for line in lines[1:]:
    n+=1
    vals = re.split('\t', line)
    vals = [csv_utils.ToStringForCSV(val) for val in vals]
    fout.write((','.join(vals))+'\n')
    n_out+=1

  logging.info( 'n_col: %d'%len(tags))
  logging.info( 'n: %d'%n)
  logging.info( 'n_out: %d'%n_out)

#############################################################################
