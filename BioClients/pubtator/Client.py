#!/usr/bin/env python3
#############################################################################
### Pubtator REST API client
### https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/tmTools/RESTfulAPIs.html
### Formats: JSON, PubTator, BioC.
#############################################################################
### NOTE that the API does NOT provide keyword search capability like
### webapp https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/PubTator/index.cgi
#############################################################################
### Nomenclatures:
###   Gene : NCBI Gene
###	e.g. https://www.ncbi.nlm.nih.gov/sites/entrez?db=gene&term=145226
###   Disease : MEDIC (CTD, CTD_diseases.csv)
###	e.g. http://ctdbase.org/basicQuery.go?bqCat=disease&bq=C537775
###   Chemical : MESH
###	e.g. http://www.nlm.nih.gov/cgi/mesh/2014/MB_cgi?field=uid&term=D000596
###   Species : NCBI Taxonomy
###	e.g. https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?name=10090
###   Mutation : tmVar
###	https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/PubTator/tutorial/tmVar.html
#############################################################################
import sys,os,time,json,argparse,re,logging
#
from ..util import rest_utils
#
API_HOST="www.ncbi.nlm.nih.gov"
API_BASE_PATH="/CBBresearch/Lu/Demo/RESTful/tmTool.cgi"
#
#
#############################################################################
def GetAnnotations(base_url, mode, pmids, fout):
  n_assn=0; n_hit=0;
  fout.write('sourcedb\tsourceid\tbegin\tend\tobj_type\tobj\n')
  for pmid in pmids:
    url = base_url+'/%s/%s/JSON'%(mode, pmid)
    rval = rest_utils.GetURL(url, parse_json=True)
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
if __name__=='__main__':
  parser = argparse.ArgumentParser(
	description='Pubtator REST API client utility',
	epilog='Reports PubMed NER annotations for specified PMID[s].')
  ops=['get_annotations']
  modes = ['Gene', 'Chemical', 'BioConcept']
  parser.add_argument("op", choices=ops, help="operation")
  parser.add_argument("--mode", choices=modes, help='mode', default='BioConcept')
  parser.add_argument("--ids", help="PubMed IDs, comma-separated (ex:25533513)")
  parser.add_argument("--i", dest="ifile", help="input file, PubMed IDs")
  parser.add_argument("--nmax", help="list: max to return")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("-v", "--verbose", default=0, action="count")

  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  BASE_URL='https://'+args.api_host+args.api_base_path

  if args.ofile:
    fout = open(args.ofile, "w+")
  else:
    fout = sys.stdout

  ids=[];
  if args.ifile:
    fin=open(args.ifile)
    while True:
      line=fin.readline()
      if not line: break
      ids.append(line.rstrip())
    logging.info('input IDs: %d'%(len(ids)))
    fin.close()
  elif args.ids:
    ids = re.split(r'[\s,]+', args.ids.strip())

  if args.op == 'get_annotations':
    if not ids:
      logging.error('input PMIDs required.')
    GetAnnotations(BASE_URL, args.mode, ids, fout)

  else:
    logging.error('Invalid operation: %s'%args.op)
