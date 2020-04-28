#!/usr/bin/env python3
##############################################################################
### Utility for LincsCloud REST API.
### http://www.lincsproject.org/
### http://api.lincscloud.org/
### http://api.lincscloud.org/a2/usage
### service = cellinfo|geneinfo|instinfo|pertinfo|plateinfo|siginfo
##############################################################################
### "The website lincscloud.org, a Broad Institute developed resource for
### analysis of LINCS Phase 1 (2011-2014) data, will be deprecated in 2015
### as the NIH has recently funded a separate LINCS Data Coordination and
### Integration Center (DCIC)."
##############################################################################
import sys,os,re,json,argparse,time,logging
#
from ..util import rest_utils
#
API_HOST='api.lincscloud.org'
API_BASE_PATH='/a2'
API_KEY="===REPLACE-WITH-KEY==="
#
##############################################################################
def GeneInfo(id_query, base_url, api_key):
  url=base_url+'/geneinfo?q={"pr_gene_symbol":"%s"}'%id_query
  url+='&user_key=%s'%api_key
  logging.debug(url)
  rval=None
  try:
    rval=rest_utils.GetURL(url, parse_json=True)
  except Exception as e:
    logging.info('HTTP Error (%s): %s'%(res,e))
  return rval

##############################################################################
def PertInfo(id_query,base_url,api_key):
  url=base_url+'/pertinfo?q={"pert_iname":"%s"}'%id_query
  url+='&user_key=%s'%api_key
  logging.debug(url)
  rval=None
  try:
    rval=rest_utils.GetURL(url,parse_json=True)
  except Exception as e:
    logging.info('HTTP Error (%s): %s'%(res,e))
  return rval

##############################################################################
def PertList_Bioactive(base_url, api_key, fout, nskip=0, nmax=0, nchunk=100):
  n_all=0; n_out=0; n_err=0;
  t0=time.time()
  url=base_url+'/pertinfo?q={"pert_icollection":"BIOA"}'
  url+='&user_key=%s'%api_key
  fields=[
	"pubchem_cid",
	"canonical_smiles",
	"inchi_string",
	"in_summly",
	"molecular_formula",
	"molecular_wt",
	"num_gold",
	"num_inst",
	"num_sig",
	"pert_collection",
	"pert_id",
	"pert_iname",
	"pert_summary",
	"pert_type",
	"pert_vendor"
	]
  fout.write('\t'.join(fields)+'\n')
  done=False
  while True:
    url_this=url+('&sk=%d&l=%d'%(nskip, nchunk))
    logging.debug(url_this)
    rval=rest_utils.GetURL(url_this, parse_json=True)
    if not rval:
      logging.error('no response: %s'%url)
      break
    perts=rval
    if type(perts) not in (list, tuple):
      logging.debug('perts (%s) = "%s"'%(type(perts),str(perts)))
      nskip+=nchunk
      continue
    for pert in perts:
      if type(pert) is not dict:
        logging.debug('pert (%s) = "%s"'%(type(pert),str(pert)))
        continue
      n_all+=1
      for j,field in enumerate(fields):
        fout.write('%s"%s"'%(('\t' if j>0 else ''),pert[field] if field in pert else ''))
      fout.write('\n')
      n_out+=1
      if nmax>0 and n_out>=nmax:
        done=True
        break
    if done: break
    nskip+=nchunk

  logging.info('n_all: %d  n_out: %d  n_err: %d'%(n_all,n_out,n_err),)
  logging.info('elapsed time: %s'%time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0)))

##############################################################################
if __name__=='__main__':
  epilog='''\
LINCS = Library of Integrated Network-based Cellular Signatures,
http://www.lincsproject.org/.
Examples:
"geneinfo?q={'pr_gene_symbol':'TP53'}", 
"pertinfo?q={'pert_iname':'ketorolac'}", 
"pertinfo?q={'pert_icollection':'BIOA'}&c=true", 
"siginfo?q={'sig_id':'CPC019_A549_24H:BRD-K33720404-001-01-9:10'}".
Gene info ID must be gene name.
Perturbagen info ID must be chemical name.
'''
  parser = argparse.ArgumentParser(description='LINCS REST API client', epilog=epilog)
  ops = ['geneinfo', 'pertinfo', 'pertlist_bioactive'] 
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--i", dest="ifile", help="input file of query IDs")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--str_query", help="search substring")
  parser.add_argument("--ids", help="query IDs, comma-separated")
  parser.add_argument("--rex", help="search regex")
  parser.add_argument("--nmax", type=int, default=None, help="max records")
  parser.add_argument("--skip", type=int, default=0, help="skip 1st SKIP queries")
  parser.add_argument("--nchunk", type=int, default=0)
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("--api_key", default=API_KEY)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url='https://'+args.api_host+args.api_base_path

  if args.ifile:
    fin=open(args.ifile)
    if not fin: parser.error('failed to open input file: %s'%args.ifile)
    ids=[]
    while True:
      line=fin.readline()
      if not line: break
      ids.append(line.strip())
  elif args.ids:
    ids = re.split('[,\s]+', args.ids.strip())

  if args.ofile:
    fout=open(args.ofile,"w")
    if not fout: parser.error('cannot open outfile: %s'%args.ofile)
  else:
    fout=sys.stdout

  t0=time.time()

  if args.op == "geneinfo":
    for id_query in ids:
      rval = GeneInfo(id_query, base_url, args.api_key)
      logging.info(json.dumps(rval,indent=2))

  elif args.op == "pertinfo":
    for id_query in ids:
      rval = PertInfo(id_query, base_url, args.api_key)
      logging.info(json.dumps(rval,indent=2))

  elif args.op == "pertlist_bioa":
      PertList_Bioactive(base_url, args.api_key, fout, args.skip, args.max, args.chunk)

  else:
    parser.error('No operation specified.')

  logging.info(('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0)))))

