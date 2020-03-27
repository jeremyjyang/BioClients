#!/usr/bin/env python3
#############################################################################
### For accessing files via FTP site; ftp://ftp.ncbi.nlm.nih.gov/pubchem/
#############################################################################
import sys,os,re,time,argparse,logging

from ... import pubchem

FTP_URL='ftp://ftp.ncbi.nlm.nih.gov/pubchem'
POLL_WAIT=10
MAX_WAIT=600

#############################################################################
if __name__=='__main__':
  epilog="""
FTP_URL: {0}""".format(FTP_URL)
  parser = argparse.ArgumentParser(description="access PubChem FTP site", epilog=epilog)
  parser.add_argument("--ftp_get", help="path of file")
  parser.add_argument("--ftp_ls", help="path of dir")
  parser.add_argument("--ftp_url", default=FTP_URL)
  parser.add_argument("--skip", type=int, default=0)
  parser.add_argument("--nmax", type=int, default=0)
  parser.add_argument("--ftp_ntries", type=int, default=20, help="max tries per ftp-get")
  parser.add_argument("--sdf2smi", action="store_true", help="convert SDF to SMILES")
  parser.add_argument("--o", dest="ofile", help="output file")
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  if not (args.ftp_get or args.ftp_ls):
    parser.error("--ftp_get or --ftp_ls required.")

  if args.ofile:
    fout = open(args.ofile, "w")
  else:
    fout = sys.stdout

  if args.ftp_get:
    url=("%s%s"%(args.ftp_url, args.ftp_get))
    if args.sdf2smi:
      nbytes = pubchem.ftp.Utils.GetUrlSDF2SMI(url, fout, ntries=args.ftp_ntries, poll_wait=10)
    else:
      nbytes = pubchem.ftp.Utils.GetUrl(url, fout, ntries=args.ftp_ntries, poll_wait=10)
    logging.info("bytes: %.2fMB"%(nbytes/1e6))
  elif args.ftp_ls:
    url=("%s%s"%(args.ftp_url, args.ftp_ls))
    pubchem.ftp.Utils.GetUrl(url, fout, ntries=args.ftp_ntries, poll_wait=10)
