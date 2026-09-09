#!/usr/bin/env python3
###

import sys,os,time,argparse,logging
import numpy as np
import pandas as pd
import h5py

###
def h5_type(ob):
  return "Group" if type(ob) is h5py.Group else "Dataset" if type(ob) is h5py.Dataset else type(ob)

###
def list_all(name, ob):
  logging.info(f"{ob.name} ({h5_type(ob)})")
  if type(ob) is h5py.Dataset:
    logging.info(f"Dataset dtype: {ob.dtype}; shape: {ob.shape}; size: {ob.size}; ndim: {ob.ndim}; nbytes: {ob.nbytes}")
  return None

#############################################################################
def Summary(f):
  logging.debug(list(f.keys()))
  for k in list(f.keys()):
    if type(f[k]) is h5py.Group:
      logging.debug(f"{f.name}:{f[k].name}")
      f[k].visititems(list_all)
    else:
      logging.info(f"{f[k].name} ({h5_type(f[k])})")

#############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(description='H5 file operations', epilog="")
  OPS = ['summary']
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
    Summary(finh5)

  else:
    parser.error(f"Unsupported operation: {args.op}")

  logging.info(f"Elapsed: {time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0))}")

