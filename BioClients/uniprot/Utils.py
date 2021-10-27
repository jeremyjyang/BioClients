#!/usr/bin/env python3
##############################################################################
### uniprot_utils.py - utility functions for access to Uniprot REST API.
### UniprotKB = Uniprot Knowledge Base
##############################################################################
import sys,os,re,logging
#
from ..util import rest
#
#############################################################################
def GetData(base_uri, uids, ofmt, fout):
  """Need to handle xml, rdf better (merge)."""
  n_prot=0; n_err=0;
  for uid in uids:
    rval=rest.GetURL(base_uri+'/%s.%s'%(uid, ofmt))
    if not rval:
      n_err+=1
      continue
    if ofmt=='tab':
      lines=[];
      for line in rval.splitlines():
        vals=re.split(r'\t', line)
        lines.append('\t'.join(vals))
      for i,line in enumerate(lines):
        if n_prot>0 and i==0: continue #Skip duplicate headers.
        fout.write(line+'\n')
    else:
      fout.write(rval+'\n')
    n_prot+=1
  logging.info('n_in: %d; n_prot: %d; n_err: %d'%(len(uids), n_prot, n_err))

#############################################################################
def UIDs2JSON(base_uri, uids, fout):
  """ Uses uniprot library from Bosco Ho (https://github.com/boscoh/uniprot)."""
  import uniprot ## Bosco Ho (https://github.com/boscoh/uniprot)
  uniprot_data=uniprot.batch_uniprot_metadata(uids, None)
  for uid in uniprot_data.keys():
    for key in uniprot_data[uid].keys():
      if key in ('accs', 'sequence', 'go', 'description'):  #keep simple
        del uniprot_data[uid][key]
  json_txt=json.dumps(uniprot_data, sort_keys=True, indent=2)
  fout.write(json_txt+'\n')
  return
