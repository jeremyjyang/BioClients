#!/usr/bin/env python3
###
# https://mygene.info/
# https://pypi.org/project/mygene/
###
import sys,os,re,argparse,time,logging
import pandas as pd
import mygene as mg
#
from .. import mygene
#
#############################################################################
if __name__=='__main__':
  FIELDS = 'HGNC,symbol,name,taxid,entrezgene,ensemblgene'
  epilog = "See https://mygene.info/, https://pypi.org/project/mygene/"
  parser = argparse.ArgumentParser(description='MyGene API client', epilog=epilog)
  parser.add_argument("--i", dest="ifile", required=True, help="input gene IDs")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--fields", default=FIELDS, help="requested fields")
  parser.add_argument("-v", "--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  fout = open(args.ofile, 'w') if args.ofile else sys.stdout

  t0 = time.time()
  logging.info('Python: %s; pandas: %s; mygene: %s'%(sys.version.split()[0], pd.__version__, mg.__version__))

  genes = pd.read_table(args.ifile, header=None, names=["ID"])
  fields = re.split(r'\s*,\s*', args.fields)
  mgi = mg.MyGeneInfo()
  mygene.Utils.Mygene2TSV(mgi, genes, fields, fout)

  logging.info("Elapsed: %ds"%(time.time()-t0))
