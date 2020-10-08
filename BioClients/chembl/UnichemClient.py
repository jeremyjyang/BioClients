#!/usr/bin/env python3
"""
unichem_query.py - command line utility for UniChem REST API.
See: https://www.ebi.ac.uk/unichem/info/webservices

Source IDs:
1: ChEMBL
7: ChEBI
15: SureChEMBL
22: PubChem
"""
import sys,os,re,argparse,time,logging,json

from ..util import rest
#
PROG=os.path.basename(sys.argv[0])
#
API_HOST='www.ebi.ac.uk'
API_BASE_PATH='/unichem/rest'
#
#
##############################################################################
def GetMapping(base_url, ids, src_id, dst_id, fout):
  n_qry=0; n_unmapped=0; n_ambig=0; n_out=0; 
  src_info = GetSourceInfo(base_url, src_id)
  src_name = src_info['name'] if 'name' in src_info else ''
  dst_info = GetSourceInfo(base_url, dst_id)
  dst_name = dst_info['name'] if 'name' in dst_info else ''
  fout.write('%s_id\t%s_id\n'%(src_name, dst_name))
  for id_query in ids:
    n_qry+=1
    logging.info('query: "%s"'%id_query)
    rval=rest.Utils.GetURL(base_url+'/src_compound_id/%s/%d/%d'%(id_query, src_id, dst_id), parse_json=True)
    logging.debug('%s'%json.dumps(rval, sort_keys=True, indent=2))
    mols = rval
    ok=False
    hits_this=0
    for mol in mols:
      id_dst = mol['src_compound_id'] if 'src_compound_id' in mol else ''
      if id_dst:
        ok=True
        hits_this+=1
      fout.write('%s\t%s\n'%(id_query, id_dst))
      n_out+=1
    if not ok:
      n_unmapped+=1
    if hits_this>1:
      n_ambig+=1

  logging.info('n_qry: %d'%(n_qry))
  logging.info('n_unmapped: %d'%(n_unmapped))
  logging.info('n_ambig: %d'%(n_ambig))
  logging.info('n_out: %d'%(n_out))
  
##############################################################################
def GetStructure(base_url, ids, src_id, fout):
  n_qry=0; n_unmapped=0; n_ambig=0; n_out=0; 
  src_info = GetSourceInfo(base_url, src_id)
  src_name = src_info['name'] if 'name' in src_info else ''
  mol_tags=None;
  for id_query in ids:
    n_qry+=1
    logging.info('query: "%s"'%id_query)
    rval = rest.Utils.GetURL(base_url+'/structure/%s/%d'%(id_query, src_id), parse_json=True)
    logging.debug('%s'%json.dumps(rval, sort_keys=True, indent=2))
    mols = rval
    ok=False
    hits_this=0
    for mol in mols:
      if n_out==0 or not mol_tags:
        mol_tags = mol.keys()
        fout.write('\t'.join(['%s_id'%src_name]+mol_tags)+'\n')
      vals = [id_query]
      for tag in mol_tags:
        vals.append(mol[tag] if tag in mol else '')
      fout.write('\t'.join(vals)+'\n')
      n_out+=1

  logging.info('n_qry: %d'%(n_qry))
  logging.info('n_out: %d'%(n_out))

##############################################################################
def GetByInchikeys(base_url, inchikeys, fout):
  n_qry=0; n_out=0; tags=[];
  fout.write('inchikey\tchembl_id\n')
  for inchikey in inchikeys:
    n_qry+=1
    rval=None; chemb_id='';
    inchikey = re.sub(r'^InChIKey=', '', inchikey)
    logging.info('query: "%s"'%inchikey)
    rval = rest.Utils.GetURL(base_url+'/inchikey/%s'%inchikey, parse_json=True)
    chembl_id = None
    if rval:
      logging.debug('%s'%json.dumps(rval, sort_keys=True, indent=2))
      for s in rval:
        if 'src_id' in s and s['src_id']=='1':
          chembl_id = s['src_compound_id']
    if chembl_id:
      fout.write('%s\t%s\n'%(inchikey, chembl_id))
      n_out+=1

  logging.info('n_qry: %d'%(n_qry))
  logging.info('n_out: %d'%(n_out))

#############################################################################
def ListSources(base_url):
  rval = rest.Utils.GetURL(base_url+'/src_ids', parse_json=True)
  src_ids=[]
  for s in rval:
    if 'src_id' in s :
      src_ids.append(int(s['src_id']))
  for src_id in src_ids:
    info = GetSourceInfo(base_url, src_id)
    name = info['name'] if 'name' in info else ''
    name_label = info['name_label'] if 'name_label' in info else ''
    name_long = info['name_long'] if 'name_long' in info else ''
    logging.info('%2d: %s (%s)'%(src_id, name_label, name_long))
    for key in sorted(info.keys()):
      logging.debug('\t%14s: %s'%(key, info[key]))
  logging.info('source count: %d'%len(src_ids))

##############################################################################
def GetSourceInfo(base_url, src_id):
  rval=rest.Utils.GetURL(base_url+'/sources/%s'%src_id, parse_json=True)
  logging.debug(json.dumps(rval, sort_keys=True, indent=2))
  info = rval[0] if (rval and len(rval)==1) else {}
  return info

##############################################################################
if __name__=='__main__':
  epilog='''\
operations:
list_sources: all sources,
get_mapping: get mapping from src_id to dst_id,
get_by_inchikey: input IDs are InChIKeys,
get_structure: get Inchi, InchiKey from src_id,
'''
  parser = argparse.ArgumentParser(description='UniChem REST API client', epilog=epilog)
  ops=['list_sources', 'get_mapping', 'get_by_inchikey', 'get_structure']
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--i", dest="ifile", help="input file of IDs")
  parser.add_argument("--ids", help="ID list (comma-separated)")
  parser.add_argument("--o", dest="ofile", help="output file (TSV)")
  parser.add_argument("--src_id", help="from-source ID code")
  parser.add_argument("--dst_id", help="to-source ID code")
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("-v", "--verbose", default=0, action="count")

  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  BASE_URL='https://'+API_HOST+API_BASE_PATH

  if args.ofile:
    fout = open(args.ofile, "w")
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

  if args.op == "list_sources":
    ListSources(BASE_URL)

  elif args.op == "get_mapping":
    if not ids: parser.error('--i or --ids required.')
    if not (src_id and dst_id): parser.error('--src_id and --dst_id required.')
    GetMapping(BASE_URL, ids, src_id, dst_id, fout)

  elif args.op == "get_structure":
    if not ids: parser.error('--i or --ids required.')
    if not src_id: parser.error('--src_id required.')
    GetStructure(BASE_URL, ids, src_id, fout)

  elif args.op == "get_by_inchikey":
    if not ids: parser.error('--i or --ids required.')
    GetByInchikeys(BASE_URL, ids, fout)

  else:
    parser.error('Invalid operation: %s'%(args.op))
