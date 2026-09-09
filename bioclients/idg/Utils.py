#!/usr/bin/env python3
"""
Pharos  REST API client
https://pharos.nih.gov/idg/api/v1/targets(589)

THIS PROBABLY OBSOLETED BY GRAPHQL API/CLIENT; SEE pharos/Utils.py.
"""
###
import sys,os,json,re,time,logging
#
from ..util import rest
#
#############################################################################
def GetTargets(base_url, ids, idtype, fout):
  tags=[]; n_out=0;
  for id_this in ids:
    url = base_url+'/targets(%s)'%id_this
    rval = rest.GetURL(url, parse_json=True)
    if not rval:
      logging.debug('Not found: %s'%(id_this))
      continue
    tgt = rval
    if not tags:
      for tag in tgt.keys():
        if not tag.startswith('_') and (type(tgt[tag]) not in (list, dict)):
          tags.append(tag)
      fout.write('\t'.join(tags)+'\n')
    vals = [(str(tgt[tag]) if tag in tgt else '') for tag in tags]
    fout.write('\t'.join(vals)+'\n')
    n_out+=1
  logging.info('n_in: %d; n_out: %d'%(len(ids), n_out))

#############################################################################
def GetTargetProperties(base_url, ids, idtype, fout):
  tags=[]; n_out=0;
  for id_this in ids:
    url = (base_url+'/targets(%s)/properties'%id_this)
    rval = rest.GetURL(url, parse_json=True)
    if not rval:
      logging.debug('Not found: %s'%(id_this))
      continue
    props = rval
    for prop in props:
      if not tags:
        for tag in prop.keys():
          if not tag.startswith('_') and (type(prop[tag]) not in (list, dict)):
            tags.append(tag)
        fout.write('\t'.join([idtype]+tags)+'\n')
      vals = [id_this]+[(str(prop[tag]) if tag in prop else '') for tag in tags]
      fout.write('\t'.join(vals)+'\n')
      n_out+=1
  logging.info('n_in: %d; n_out: %d'%(len(ids), n_out))

#############################################################################
def ListItems(mode, base_url, fout):
  n_out=0; tags=[]; top=100; skip=0;
  while True:
    url = base_url+'/%s?top=%d&skip=%d'%(mode, top, skip)
    rval = rest.GetURL(url, parse_json=True)
    if not rval:
      break
    elif type(rval) is not dict:
      logging.error('rval="%s"'%(str(rval)))
      break
    logging.debug(json.dumps(rval, indent=2))
    count = rval['count'] if 'count' in rval else None
    total = rval['total'] if 'total' in rval else None
    uri = rval['uri'] if 'uri' in rval else None
    logging.debug('uri="%s"'%(uri))
    items = rval['content']
    if not items: break
    for item in items:
      if not tags:
        for tag in item.keys():
          if not tag.startswith('_') and (type(item[tag]) not in (list, dict)):
            tags.append(tag)
        fout.write('\t'.join(tags)+'\n')
      vals = [(str(item[tag]) if tag in item else '') for tag in tags]
      fout.write('\t'.join(vals)+'\n')
      n_out+=1
    skip+=top
  logging.info('n_out = %d'%(n_out))

#############################################################################
