#!/usr/bin/env python3
##############################################################################
### utility for BioGRID REST API.
### 
### See: http://wiki.thebiogrid.org/doku.php/biogridrest
### 
### URL form
### Formats:
### 	tab1, tab2, extendedTab2, count, json, jsonExtended
##############################################################################
### EXPERIMENTAL_SYSTEM
###	"Affinity Capture-Luminescence"
###	"Affinity Capture-MS"
###	"Affinity Capture-Western"
###	"Biochemical Activity"
###	"Co-fractionation"
###	"Co-localization"
###	"FRET"
###	"PCA"
###	"Phenotypic Enhancement"
###	"Phenotypic Suppression"
###	"Protein-peptide"
###	"Reconstituted Complex"
###	"Synthetic Growth Defect"
###	"Two-hybrid"
##############################################################################
import sys,os,re,json,argparse,time,logging
#
from ..util import rest_utils
#
API_HOST='webservice.thebiogrid.org'
API_BASE_PATH=''
API_KEY="==SEE $HOME/.biogrid.yaml=="
#
##############################################################################
def ListOrganisms(base_url, api_key, fout):
  n_all=0; n_out=0; n_err=0;
  url=base_url+'/organisms/?accesskey=%s'%api_key
  url+=('&format=tab2')
  rval=rest_utils.GetURL(url, parse_json=False)
  txt = rval
  lines = txt.splitlines()
  fout.write('organism_id, organism"\n')
  for line in lines:
    oid,org = re.split('\t', line)
    fout.write('%s\t"%s"\n'%(oid, org))
    n_out+=1
  logging.info('n_out: %d'%(n_out))

##############################################################################
def ListIdTypes(base_url, api_key, fout):
  n_all=0; n_out=0; n_err=0;
  url=base_url+'/identifiers/?accesskey=%s'%api_key
  url+=('&format=tab2')
  rval=rest_utils.GetURL(url, parse_json=False)
  txt = rval
  lines = txt.splitlines()
  for line in lines:
    fout.write('%s\n'%(line))
    n_all+=1
    n_out+=1
  logging.info('n_out: %d'%(n_out))

##############################################################################
def GetInteractions(base_url, api_key, ids, fout):
  n_all=0; n_out=0; n_err=0;
  t0=time.time()
  tags=[];

  for iid in ids:
    url=base_url+'/interactions/%s?'%iid
    url+=('&accesskey=%s&format=json'%api_key)
    rval=rest_utils.GetURL(url, parse_json=True)
    logging.debug(json.dumps(rval, indent=2, sort_keys=False)+'\n')

    if type(rval) is not dict:
      n_err+=1
      continue
    if not iid in rval :
      n_err+=1
      continue
    intr = rval[iid]
    n_all+=1

    if n_all==1 or not tags:
      tags=intr.keys()
      fout.write('\t'.join(tags)+'\n')

    vals=[intr[tag] if tag in intr else '' for tag in tags]
    fout.write(('\t'.join(vals))+'\n')
    n_out+=1

  logging.info('n_all: %d'%(n_all))
  logging.info('n_out: %d'%(n_out))
  logging.info('n_err: %d'%(n_err))

##############################################################################
def SearchInteractions(base_url, api_key, ids, params, fout):
  n_all=0; n_out=0; n_err=0;
  t0=time.time()
  tags=[];

  url=base_url+('/interactions/?accesskey=%s&format=json'%api_key)
  if ids:
    url+=('&geneList=%s'%('|'.join(ids)))
  url+=('&interSpeciesExcluded=%s'%str(not params['inc_interspecies']).lower())
  url+=('&selfInteractionsExcluded=%s'%str(not params['inc_self']).lower())
  if params['elist']:
    url+=('&includeEvidence=%s'%str(params['inc_evidence']).lower())
    url+=('&evidenceList=%s'%('|'.join(params['elist'])))
  if params['addl_idtypes']:
    url+=('&additionalIdentifierTypes=%s'%('|'.join(params['addl_idtypes'])))
  if params['human']:
    url+=('&taxId=9606')

  skip=0; chunk=1000;

  while True:
    url_this=url+('&start=%d&max=%d'%(skip, chunk))
    rval=rest_utils.GetURL(url_this, parse_json=True)
    logging.debug(json.dumps(rval, indent=2, sort_keys=False)+'\n')
    if not rval: break
    if type(rval) is not dict:
      n_err+=1
      continue
    intrs = rval
    for iid, intr in intrs.items():
      n_all+=1
      if n_all==1 or not tags:
        tags=intr.keys()
        fout.write('\t'.join(tags)+'\n')
      vals=[];
      for tag in tags:
        vals.append(intr[tag] if tag in intr else '')
      fout.write(('\t'.join(vals))+'\n')
      n_out+=1
    skip+=chunk

  logging.info('n_all: %d'%(n_all))
  logging.info('n_out: %d'%(n_out))
  logging.info('n_err: %d'%(n_err))
  logging.info(('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0)))))

##############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(description='BioGrid REST API client', epilog='')
  ops = ['list_organisms', 'list_idtypes', 'get_interactions', 'search_interactions']
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--ids", help="query IDs (comma-separated)")
  parser.add_argument("--i", dest="ifile", help="input query IDs")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--inc_interspecies", type=bool, help="include inter-species interactions")
  parser.add_argument("--inc_self", type=bool, help="include self-interactions")
  parser.add_argument("--inc_evidence", type=bool, help="include only ELIST evidence (else exclude)")
  parser.add_argument("--elist", default="", help="evidence codes (|-separated)")
  parser.add_argument("--addl_idtypes", default="", help="additional ID types (|-separated)")
  parser.add_argument("--human", type=bool, help="human-only")
  parser.add_argument("--rex")
  parser.add_argument("--str_query")
  parser.add_argument("--nmax", type=int)
  parser.add_argument("--skip", type=int)
  parser.add_argument("--nchunk", type=int)
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("--api_key", default=API_KEY)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  search_params = {
	'inc_interspecies': args.inc_interspecies,
	'inc_self': args.inc_self,
	'inc_evidence': args.inc_evidence,
	'elist': re.split('[|\s]+', args.elist.strip()),
	'addl_idtypes': re.split('[|\s]+', args.addl_idtypes.strip()),
	'human': args.human
	}

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url='https://'+args.api_host+args.api_base_path

  ids=[]
  if args.ifile:
    fin=open(args.ifile)
    if not fin: parser.error('failed to open input file: %s'%args.ifile)
    while True:
      line=fin.readline()
      if not line: break
      ids.append(line.strip())
  elif args.ids:
    ids=re.split('[,\s]+', args.ids.strip())

  if args.ofile:
    fout=open(args.ofile, "w")
    if not fout: parser.error('failed to open output file: %s'%args.ofile)
  else:
    fout=sys.stdout

  t0=time.time()

  if args.op =="list_organisms":
    ListOrganisms(base_url, args.api_key, fout)

  elif args.op =="list_idtypes":
    ListIdTypes(base_url, args.api_key, fout)

  elif args.op =="get_interactions":
    GetInteractions(base_url, args.api_key, ids, fout)

  elif args.op =="search_interactions":
    SearchInteractions(base_url, args.api_key, ids, search_params, fout)

  else:
    parser.error('no operation specified.')

  logging.info(('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0)))))

