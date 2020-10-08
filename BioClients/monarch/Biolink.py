#!/usr/bin/env python3
"""
Monarch BioLink REST API client
https://api.monarchinitiative.org/api/
https://github.com/monarch-initiative/biolink-api/
"""
###
import sys,os,argparse,json,csv,logging
#
from ..util import rest
#
API_HOST='api.monarchinitiative.org'
API_BASE_PATH='/api'
#
#############################################################################
def GetDisease(base_url, ids, args, fout):
  csvWriter = csv.writer(fout, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
  tags=None;
  i_ent=0; n_assn=0; n_ent_found=0;
  url_params={}
  if args.nmax: url_params['rows'] = args.nmax
  if args.use_compact_associations: url_params['use_compact_associations'] = True
  if args.exclude_automatic_assertions: url_params['exclude_automatic_assertions'] = True
  if args.unselect_evidence: url_params['unselect_evidence'] = True
  url_params_str = ('&'.join(['%s=%s'%(k,str(v)) for k,v in list(url_params.items())]))
  for entid in ids:
    i_ent+=1
    if i_ent<=args.skip: continue
    print('%s:'%entid, file=sys.stderr)
    url_this = (base_url+'/bioentity/disease/%s?%s'%(entid,url_params_str))
    try:
      ent = rest.Utils.GetURL(url_this, parse_json=True)
    except Exception as e:
      if e.args:
        print(str(e.args), file=sys.stderr)
    if ent:
      n_ent_found+=1
      #print(json.dumps(ent, sort_keys=True, indent=2))
      if not tags:
        tags = sorted(ent.keys())
        csvWriter.writerow(tags)
      row_this=[]
      for tag in tags:
        if tag in ent:
          if isinstance(ent[tag], list):
            val = len(ent[tag])
          else:
            val = str(ent[tag])
        else:
          val = ''
        row_this.append(val)
    csvWriter.writerow(row_this)

  print('DEBUG: n_entities = %d'%n_ent_found, file=sys.stderr)


#############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(description='Monarch BioLink REST API client utility')
  ops = ['get_disease', 'get_association']
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--ifile", help="input file, IDs")
  parser.add_argument("--ids", help="IDs (comma-separated) e.g. DOID:678, OMIM:605543")
  parser.add_argument("--nmax", type=int, help="max results")
  parser.add_argument("--skip", type=int, help="skip results", default=0)
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--use_compact_associations", action="store_true")
  parser.add_argument("--exclude_automatic_assertions", action="store_true")
  parser.add_argument("--unselect_evidence", action="store_true")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  BASE_URL = 'https://'+args.api_host+args.api_base_path

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  ids=[];
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      if line.rstrip(): ids.append(line.rstrip())
    fin.close()
  elif args.ids:
    ids = re.split(r'[,\s]+', args.ids)

  if args.op=='get_disease':
    GetDisease(BASE_URL, ids, args, fout)

  elif args.op=='get_association':
    parser.error("Invalid operation: {0}".format(args.op))

  else:
    parser.error("Invalid operation: {0}".format(args.op))

