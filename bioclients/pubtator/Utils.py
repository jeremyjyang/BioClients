#!/usr/bin/env python3
###
import sys,os,time,json,argparse,re,logging
#
from ..util import rest
#
#############################################################################
def GetAnnotations(base_url, mode, pmids, fout):
  n_assn=0; n_hit=0;
  fout.write('sourcedb\tsourceid\tbegin\tend\tobj_type\tobj\n')
  for pmid in pmids:
    url = base_url+'/%s/%s/JSON'%(mode, pmid)
    rval = rest.GetURL(url, parse_json=True)
    if not rval:
      logging.info('not found: %s'%(pmid))
      continue

    n_assn_this=0
    sources = rval if type(rval) is list else [rval]
    for source in sources:
      sourceDb = source['sourcedb'] if 'sourcedb' in source else ''
      sourceId = source['sourceid'] if 'sourceid' in source else ''
      anns = source['denotations'] if (type(source) is dict and 'denotations') in source else []

      for ann in anns:
        obj = ann['obj'] if 'obj' in ann else None
        begin = ann['span']['begin'] if 'span' in ann and 'begin' in ann['span'] else ''
        end = ann['span']['end'] if 'span' in ann and 'end' in ann['span'] else ''
        if obj and begin and end:
          obj_type,obj_id = re.split(':', obj, 1)
          fout.write('%s\t%s\t%d\t%d\t%s\t%s\n'%(sourceDb, sourceId, begin, end, obj_type, obj_id))
          n_assn_this+=1
    if n_assn_this: n_hit+=1
    n_assn+=n_assn_this

  logging.info('n_in = %d (PMIDs)'%(len(pmids)))
  logging.info('n_hit = %d (PMIDs with associations)'%(n_hit))
  logging.info('n_miss = %d (PMIDs with NO associations)'%(len(pmids)-n_hit))
  logging.info('n_assn = %d (total associations)'%(n_assn))

#############################################################################
