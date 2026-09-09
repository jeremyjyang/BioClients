#!/usr/bin/env python3
"""
Access to Ensembl REST API.
http://rest.ensembl.org/documentation/info/lookup
Mostly by gene, except Variant Effect Predictor (VEP) by SNP.
https://ensembl.org/info/docs/tools/vep/
https://rest.ensembl.org/documentation/info/vep_id_get
"""
import sys,os,re,argparse,time,json,logging

from .. import ensembl
#
##############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(prog=sys.argv[0], description="Ensembl REST API client", epilog="Example IDs: ENSG00000157764, ENSG00000160785")
  ops = ["list_species", "get_xrefs", "get_info", "get_vep", "show_version"]
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--ids", help="Ensembl_IDs, comma-separated (ex:ENSG00000000003), or SNP IDs, comma-separated (ex:rs56116432)")
  parser.add_argument("--i", dest="ifile", help="input file, Ensembl IDs or SNP IDs")
  parser.add_argument("--api_host", default=ensembl.API_HOST)
  parser.add_argument("--api_base_path", default=ensembl.API_BASE_PATH)
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--skip", type=int, default=0)
  parser.add_argument("--nmax", type=int)
  parser.add_argument("-v", "--verbose", action="count", default=0)
  parser.add_argument("-q", "--quiet", action="count", default=0)
  args = parser.parse_args()

  # logging.PROGRESS = 15 (custom)
  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>0 else logging.ERROR if args.quiet else 15))

  base_url = 'http://'+args.api_host+args.api_base_path

  fout = open(args.ofile, "w") if args.ofile else sys.stdout

  t0=time.time()

  if args.ifile:
    fin = open(args.ifile)
    ids=[]
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.strip())
  elif args.ids:
    ids = re.split(r'\s*,\s*', args.ids.strip())
  else:
    ids=[]

  if ids:
    logging.info(f"IDs: {len(ids)}")

  if re.match("^get_", args.op) and not ids:
    parser.error('--i or --ids required.')

  if args.op=='list_species':
    ensembl.ListSpecies(base_url, fout)

  elif args.op=='get_info':
    ensembl.GetInfo(ids, args.skip, args.nmax, base_url, fout)

  elif args.op=='get_xrefs':
    ensembl.GetXrefs(ids, args.skip, args.nmax, base_url, fout)

  elif args.op=='get_vep':
    ensembl.GetVariantEffectPredictions(ids, args.skip, args.nmax, base_url, fout)

  elif args.op=='show_version':
    ensembl.ShowVersion(base_url, fout)

  else:
    parser.error(f'Invalid operation: {args.op}')

  logging.info(('%s: elapsed time: %s'%(os.path.basename(sys.argv[0]), time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0)))))
