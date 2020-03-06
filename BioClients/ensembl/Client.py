#!/usr/bin/env python3
"""
	Access to Ensembl REST API.
	http://rest.ensembl.org/documentation/info/lookup
	http://rest.ensembl.org/lookup/id/ENSG00000157764?expand=1;content-type=application/json
"""
import sys,os,re,argparse,time,json,logging,requests
#
API_HOST='rest.ensembl.org'
API_BASE_PATH=''
#
##############################################################################
def GetInfo(base_url, ids, fout):
  n_gene=0; n_out=0; n_err=0; tags=[];
  for id_this in ids:
    url_this = base_url+'/lookup/id/'+id_this+'?content-type=application/json&expand=0'
    logging.debug(url_this)
    rval = requests.get(url_this, headers={"Content-Type":"application/json"})
    if not rval.ok:
      logging.error('{0} : "{1}"'.format(rval.status_code, id_this))
      n_err+=1
      continue
    gene = rval.json()
    if not tags:
      for tag in gene.keys():
        if type(gene[tag]) not in (list, dict): tags.append(tag) #Only simple metadata.
      fout.write('\t'.join(tags)+'\n')
    n_gene+=1
    vals = [str(gene[tag]).replace('\n', ' ') if tag in gene and gene[tag] is not None else '' for tag in tags]
    fout.write('\t'.join(vals)+'\n')
    n_out+=1
  logging.info('n_ids: {0}'.format(len(ids)))
  logging.info('n_gene: {0}'.format(n_gene))
  logging.info('n_out: {0}'.format(n_out))
  logging.info('n_err: {0}'.format(n_err))

##############################################################################
def GetXrefs(base_url, ids, fout):
  n_out=0; n_err=0; dbcounts={};
  tags = ['ensembl_id', 'xref_dbname', 'xref_id', 'xref_description']
  fout.write('\t'.join(tags)+'\n')
  for id_this in ids:
    url_this = base_url+'/xrefs/id/'+id_this
    rval = requests.get(url_this, headers={"Content-Type":"application/json"})
    if not rval.ok:
      #rval.raise_for_status()
      logging.error('{0} : "{1}"'.format(rval.status_code, id_this))
      n_err+=1
      continue
    xrefs = rval.json()
    for xref in xrefs:
      if not (type(xref) is dict and 'dbname' in xref): continue
      dbname = xref['dbname']
      if dbname not in dbcounts: dbcounts[dbname]=0
      dbcounts[dbname]+=1
      vals = []
      for tag in ['dbname', 'primary_id', 'description']:
        vals.append(xref[tag] if tag in xref and xref[tag] is not None else '')
      fout.write('\t'.join([id_this]+vals)+'\n')
      n_out+=1
  for key in sorted(dbcounts.keys()):
    logging.info('Xref counts, db = %12s: %5d'%(key, dbcounts[key]))
  logging.info('n_ids: %d'%(len(ids)))
  logging.info('n_out: %d'%(n_out))
  logging.info('errors: %d'%(n_err))
#
##############################################################################
if __name__=='__main__':
  PROG=os.path.basename(sys.argv[0])
  parser = argparse.ArgumentParser(description='Ensembl REST API client')
  ops = ['getXrefs','getInfo']
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--ids", help="Ensembl_IDs, comma-separated (ex:ENSG00000000003)")
  parser.add_argument("--i", dest="ifile", help="input file, Ensembl_IDs")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("-v", "--verbose", action="count", default=0)

  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  BASE_URL='http://'+args.api_host+args.api_base_path

  if args.ofile:
    fout=open(args.ofile, "w")
    if not fout: logging.error('Cannot open outfile: %s'%args.ofile)
  else:
    fout=sys.stdout

  t0=time.time()

  if args.ifile:
    fin=open(args.ifile)
    if not fin: logging.error('Failed to open input file: %s'%args.ifile)
    ids=[]
    while True:
      line=fin.readline()
      if not line: break
      ids.append(line.strip())
  elif args.ids:
    ids=re.split(r'\s*,\s*', args.ids.strip())
  else:
    parser.error('--i or --ids required.')

  if args.op=='getInfo':
    GetInfo(BASE_URL, ids, fout)

  elif args.op=='getXrefs':
    GetXrefs(BASE_URL, ids, fout)

  else:
    parser.error('No operation specified.')

  logging.info(('%s: elapsed time: %s'%(PROG, time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0)))))

