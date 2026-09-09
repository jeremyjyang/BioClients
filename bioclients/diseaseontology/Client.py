#!/usr/bin/env python3
#############################################################################
### - Disease Ontology REST client 
#############################################################################
import sys,os,re,json,argparse,time,logging
#
from ..util import rest
#
API_HOST='www.disease-ontology.org'
API_BASE_PATH='/api'
#
OFMTS={'XML':'application/xml','JSON':'application/json'}
#
HEADERS={'Accept':OFMTS['JSON']}
#
##############################################################################
def GetMetadata(ids,base_url,fout):
  n_out=0;
  fout.write('doid,name,definition,child_count,parent_count,meshid\n')
  for doid in ids:
    try:
      rval=rest.GetURL(base_url+'/metadata/%s'%(doid),headers=HEADERS,parse_json=True)
    except Exception as e:
      logging.error('%s'%(e))
      continue
    if not type(rval)==types.DictType:
      logging.info('Error: %s'%(str(rval)))
      continue

    name = rval['name'] if rval.has_key('name') else ''
    definition = rval['definition'] if rval.has_key('definition') else ''
    parents = rval['parents'] if rval.has_key('parents') else []
    children = rval['children'] if rval.has_key('children') else []
    synonyms = rval['synonyms'] if rval.has_key('synonyms') else []
    subsets = rval['subsets'] if rval.has_key('subsets') else []
    xrefs = rval['xrefs'] if rval.has_key('xrefs') else []
    meshid=''
    for xref in xrefs:
      if re.match('MSH:',xref): meshid=xref[4:]
      break
    fout.write('"%s","%s","%s",%d,%d,"%s"\n'%(doid,name,definition,len(children),len(parents),meshid))
    n_out+=1

    logging.info((json.dumps(rval,indent=2,sort_keys=False)))
  logging.info('DOIDs in: %d ; records out: %d'%(len(ids),n_out))

##############################################################################
def ListTopClasses(base_url,fout):
  n_out=0;
  rval=rest.GetURL(base_url+'/metadata/DOID:4',headers=HEADERS,parse_json=True)
  children = rval['children'] if rval.has_key('children') else []
  for c in children:
    desc,doid = c
    fout.write('\t%-14s:\t"%s"\n'%(doid,desc))

##############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(description="Disease Ontology REST client")
  ops = ['get_metadata', 'list_topclasses']
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--ids", help="query DOIDs, comma-separated")
  parser.add_argument("--i", dest="ifile", help="query file, DOIDs")
  parser.add_argument("--o", dest="ofile", help="output (CSV|TSV)")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  base_url='https://'+args.api_host+args.api_base_path

  if len(set(fields_vals) - set(fields_allowed))>0:
    parser.error('disallowed fields: %s'%str(set(fields_vals) - set(fields_allowed)))

  if args.ofile:
    fout=open(args.ofile,"w")
    if not fout: parser.error('cannot open outfile: %s'%args.ofile)
  else:
    fout=sys.stdout

  t0=time.time()

  ids=[];
  if args.ifile:
    fin=open(args.ifile)
    if not fin: parser.error('cannot open args.ifile: %s'%args.ifile)
    while True:
      line=fin.readline()
      if not line: break
      try:
        doid=line.rstrip()
      except Exception as e:
        logging.error('invalid DOID: "%s"'%(line.rstrip()))
        continue
      if line.rstrip(): ids.append(doid)
    logging.info('input queries: %d'%(len(ids)))
    fin.close()
  elif args.ids:
    ids = re.split('[,\s]+', args.ids.strip())

  if args.op == "get_metadata":
    GetMetadata(ids, base_url,fout)

  elif args.op == "list_topclasses":
    ListTopClasses( base_url,fout)

  else:
    parser.error("No operation specified.")

  logging.info(('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0)))))
