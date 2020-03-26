#!/usr/bin/env python3
##############################################################################
### DEPRECATED: Should use package https://github.com/chembl/chembl_webresource_client.
##############################################################################
### See https://www.ebi.ac.uk/chemblws/docs
##############################################################################
import sys,os,re,argparse,time,logging
#
from ..util import rest_utils
#
API_HOST='www.ebi.ac.uk'
API_BASE_PATH='/chemblws'
#
#############################################################################
def GetByInchikey(base_url, id_query):
  rval=None
  rval=rest_utils.GetURL(base_uri+'/compounds/stdinchikey/%s.json'%id_query,{},parse_json=True)
  return rval

##############################################################################
### /chemblws/compounds/stdinchikey/QFFGVLORLPOAEC-SNVBAGLBSA-N
def InchiLookupCompound(base_url, ids, fout):
  tags = ['chemblId',
	'stdInChiKey',
	'smiles',
	'molecularFormula',
	'species',
	'knownDrug',
	'preferredCompoundName',
	'synonyms',
	'molecularWeight'
	]
  n_qry=0; n_out=0; n_err=0; 
  fout.write('\t'.join(tags)+'\n')
  for id_this in ids:
    n_qry+=1
    mol=None
    mol=GetByInchikey(base_url, id_this)
    if not mol or type(mol)!=types.DictType:
      n_err+=1
      continue
    elif not mol.has_key('compound'):
      n_err+=1
      continue
    cpd = mol['compound']

    vals=[]
    for tag in tags:
      vals.append(cpd[tag] if cpd.has_key(tag) else '')
    fout.write('\t'.join([str(val) for val in vals])+'\n')
    n_out+=1

  logging.info('n_qry: %d'%(n_qry))
  logging.info('n_out: %d'%(n_out))
  logging.info('errors: %d'%(n_err))

##############################################################################
if __name__=='__main__':
  asrc=None; atype=None;
  parser = argparse.ArgumentParser(description='ChEMBL REST API client for InChI queries', epilog="")
  parser.add_argument("--i", dest="ifile", help="input file of InChI IDs")
  parser.add_argument("--ids", help="InChI ID list (comma-separated)")
  parser.add_argument("--o", dest="ofile", help="output file (InChI)")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("--skip", type=int, default=0)
  parser.add_argument("--nmax", type=int)
  parser.add_argument("-v", "--verbose", default=0, action="count")

  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  BASE_URL='http://'+args.api_host+args.api_base_path

  if args.ofile:
    fout = open(args.ofile,"w")
  else:
    fout = sys.stdout

  ids=[]
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.rstrip())
    logging.info('input IDs: %d'%(len(ids)))
    fin.close()
  elif args.ids:
    ids = re.split(r'[,\s]+', args.ids.strip())

  if not ids: parser.error('--i or --ids required.')

  InchiLookupCompound(BASE_URL, ids, fout)

