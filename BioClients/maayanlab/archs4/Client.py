#!/usr/bin/env python3
###

import sys,os,time,argparse,logging
import numpy as np
import pandas as pd
import h5py

from ...util import hdf
from ... import maayanlab

#############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(description='H5 file operations', epilog="")
  OPS = ['summary', 'list_samples']
  parser.add_argument("op", choices=OPS, help='OPERATION')
  parser.add_argument("--i", dest="ifile", required=True, help="input file")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  t0 = time.time();

  fout = open(args.ofile, "w") if args.ofile else sys.stdout

  finh5 = h5py.File(args.ifile, 'r')

  if args.op == "summary":
    logging.debug(list(finh5.keys()))
    hdf.Utils.Summary(finh5)

  elif args.op == "list_samples":
    maayanlab.archs4.ListSamples(finh5, fout)

  else:
    parser.error(f"Unsupported operation: {args.op}")

  logging.info(f"Elapsed: {time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0))}")

