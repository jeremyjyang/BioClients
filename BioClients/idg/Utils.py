#!/usr/bin/env python3
"""
Pharos  REST API client
https://pharos.nih.gov/idg/api/v1/targets(589)
"""
###
import sys,os,json,re,time,logging
#
from ..util import rest_utils
#
#
#############################################################################
def GetTargets(base_url, ids, idtype, fout):
  tags=[]; n_out=0;
  for id_this in ids:
    url=base_url+'/targets(%s)'%id_this
    rval=rest_utils.GetURL(url, parse_json=True)
    if not rval:
      logging.debug('not found: %s'%(id_this))
      continue
    tgt = rval
    if not tags:
      for tag in tgt.keys():
        if not tag.startswith('_') and (type(tgt[tag]) not in (list, dict)):
          tags.append(tag)
      fout.write('\t'.join(tags)+'\n')
    vals=[];
    for tag in tags:
      val=(tgt[tag] if tag in tgt else '')
      vals.append('' if val is None else str(val))
    fout.write('\t'.join(vals)+'\n')
    n_out+=1
  logging.info('n_in: %d; n_out: %d'%(len(ids), n_out))

#############################################################################
def ListItems(mode, base_url, fout):
  n_out=0; tags=[]; top=100; skip=0;
  while True:
    url=base_url+'/%s?top=%d&skip=%d'%(mode, top, skip)
    rval=rest_utils.GetURL(url, parse_json=True)
    if not rval:
      break
    elif type(rval) is not dict:
      logging.info('ERROR: rval="%s"'%(str(rval)))
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
      vals=[];
      for tag in tags:
        val=(item[tag] if tag in item else '')
        vals.append('' if val is None else str(val))
      fout.write('\t'.join(vals)+'\n')
      n_out+=1
    skip+=top
  logging.info('n_out = %d'%(n_out))

#############################################################################
