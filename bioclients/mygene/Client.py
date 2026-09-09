#!/usr/bin/env python3
###
# https://mygene.info/
# https://pypi.org/project/mygene/
###
import sys,os,re,argparse,time,logging
import pandas as pd
import mygene as mg
#
from .. import mygene as bc_mygene
#
#############################################################################
if __name__=='__main__':
  epilog = "See https://mygene.info/, https://pypi.org/project/mygene/.  Example queries: 'cdk2', 'symbol:cdk2', 'symbol:cdk*'"
  ops = ["get", "search"]
  parser = argparse.ArgumentParser(description='MyGene API client', epilog=epilog)
  parser.add_argument("op", choices=ops, help="OPERATION")
  parser.add_argument("--i", dest="ifile", help="input gene IDs or queries")
  parser.add_argument("--ids", help="input gene IDs or queries, comma-separated")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--species", default="human", help="species name or taxonomy ID")
  parser.add_argument("--fields", default=bc_mygene.FIELDS, help="requested fields")
  parser.add_argument("-v", "--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  fout = open(args.ofile, 'w') if args.ofile else sys.stdout

  t0 = time.time()
  logging.info('Python: {}; mygene: {}'.format(sys.version.split()[0], mg.__version__))

  if args.ifile:
    genes = pd.read_table(args.ifile, header=None, names=["ID"])
    ids = list(genes.ID)
  elif args.ids:
    ids = re.split(r'[,\s]+', args.ids)
  else:
    parser.error("Input IDs required via --i or --ids.")

  fields = re.split(r'[,\s]+', args.fields)

  if args.op=="get":
    bc_mygene.GetGenes(ids, fields, fout)

  elif args.op=="search":
    bc_mygene.SearchGenes(ids, args.species, fout)

  else:
    parser.error(f"Invalid operation: {args.op}")

  logging.info(('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0)))))

