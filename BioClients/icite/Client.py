#!/usr/bin/env python3
#############################################################################
### PUbMed iCite  REST API client
### https://icite.od.nih.gov/api
#############################################################################
import sys,os,argparse,logging
import urllib.request,json,re
#
#############################################################################
def GetPmid(base_url, pmids, fout):
  n_out=0;
  tags=None;
  for pmid in pmids:
    url=base_url+'/%s'%pmid
    f = urllib.request.urlopen(url)
    rval=f.read()
    if not rval:
      logging.info('not found: %s'%(pmid))
      continue
    rval=json.loads(rval.decode('utf-8'), encoding='utf-8')
    pub = rval
    if not tags:
      tags = pub.keys()
      fout.write('\t'.join(tags)+'\n')

    vals = [];
    for tag in tags:
      val=(pub[tag] if pub.has_key(tag) else '')
      vals.append(val)
    fout.write('\t'.join([str(vals) for val in vals])+'\n')
    n_out+=1

  logging.info('n_in = %d'%(len(pmids)))
  logging.info('n_out = %d'%(n_out))

#############################################################################
def GetPmids(base_url, pmids, fout):
  n_in=0; n_out=0; tags=None; nchunk=100;

  while True:
    if n_in >= len(pmids):
      break
    pmids_this = pmids[n_in:n_in+nchunk]
    n_in += (nchunk if n_in+nchunk < len(pmids) else len(pmids)-n_in)
    url_this = base_url+'?pmids=%s'%(','.join(pmids_this))
    f = urllib.request.urlopen(url_this)
    rval = f.read()

    if not rval:
      break

    rval = json.loads(rval.decode('utf-8'), encoding='utf-8')
    logging.debug('rval="%s"'%rval.decode('utf-8'))

    logging.info('%s'%url_this)

    url_self = rval['links']['self']
    logging.debug('%s'%url_self)

    pubs = rval['data']
    for pub in pubs:
      if not tags:
        tags = list(pub.keys())
        tags.sort()
        fout.write('\t'.join(tags)+'\n')

      vals=[];
      for tag in tags:
        val = (pub[tag] if tag in pub else '')
        vals.append(val)
      fout.write('\t'.join([str(val) for val in vals])+'\n')
      n_out+=1

  logging.info('n_in = %d'%(len(pmids)))
  logging.info('n_out = %d'%(n_out))

#############################################################################
if __name__=='__main__':
  API_HOST="icite.od.nih.gov"
  API_BASE_PATH="/api/pubs"
  #
  parser = argparse.ArgumentParser(description='PubMed iCite REST API client utility', epilog='Publication metadata.')
  ops = ['get']
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--ids", dest="pmids", help="PubMed IDs, comma-separated (ex:25533513)")
  parser.add_argument("--i", dest="ifile", help="input file, PubMed IDs")
  parser.add_argument("--nmax", help="list: max to return")
  parser.add_argument("--year", help="list: year of publication")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("-v", "--verbose", default=0, action="count")

  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  BASE_URL='https://'+args.api_host+args.api_base_path

  if args.ofile:
    fout = open(args.ofile, "w", encoding="utf-8")
  else:
    fout = sys.stdout

  ids=[];
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.rstrip())
    logging.info('input IDs: %d'%(len(ids)))
    fin.close()
  elif args.ids:
    ids = re.split(r'[\s,]+', args.ids.strip())

  if args.op == 'get':
    if not ids:
      parser.error('get requires PMID[s].')
      parser.exit()
    GetPmids(BASE_URL, ids, fout)

  else:
    parser.error("Invalid operation: %s"%args.op)

