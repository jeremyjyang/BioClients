#!/usr/bin/env python3
"""
Client for SLAP REST API.

See: http://slapfordrugtargetprediction.wikispaces.com/API
"""
###
import sys,os,re,argparse,time,logging
#
from ... import chem2bio2rdf as c2b2r
#
##############################################################################
if __name__=='__main__':
  API_HOST='cheminfov.informatics.indiana.edu'
  API_BASE_PATH='/rest/Chem2Bio2RDF/slap'
  epilog="""\
D2T: drug-to-target associations;
T2D: target-to-drug associations;
DTP: drug-target paths, subnet;
DSS: drug-to-bio-similar-drugs search;
DDS: drug-drug similarity;
Examples: CIDs: 5591 TIDs: PPARG
"""
  parser = argparse.ArgumentParser(description="SLAP REST API client)", epilog=epilog)
  ops = [ "D2T", "T2D", "DTP", "DSS", "DDS" ]
  parser.add_argument("op", choices=ops, help="operation")
  parser.add_argument("--i_cid", dest="ifile_cid", help="input CIDs")
  parser.add_argument("--i_tid", dest="ifile_tid", help="input TIDs")
  parser.add_argument("--cids", help="CIDs (comma-separated)")
  parser.add_argument("--cid2s", help="CID #2 (comma-separated)")
  parser.add_argument("--tids", help="TIDs (e.g. gene symbol) (comma-separated)")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--odir", help="output dir (for auto-named GraphML subnets)")
  parser.add_argument("--cid_skip", type=int, default=0)
  parser.add_argument("--cid_nmax", type=int, default=None)
  parser.add_argument("--tid_skip", type=int, default=0)
  parser.add_argument("--tid_nmax", type=int, default=None)
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url = 'http://'+args.api_host+args.api_base_path

  fout = open(args.ofile, "w") if args.ofile else sys.stdout

  cids=[]; cid2s=[];
  if args.ifile_cid:
    fin = open(args.ifile_cid)
    while True:
      line = fin.readline()
      if not line: break
      cids.append(line.strip())
  elif args.cids:
    cids = re.split('[, ]+', args.cids.strip())
  elif args.cid2s:
    cid2s = re.split('[, ]+', args.cid2s.strip())

  tids=[];
  if args.ifile_tid:
    fin = open(args.ifile_tid)
    while True:
      line = fin.readline()
      if not line: break
      tids.append(line.strip())
  elif args.tids:
    tids = re.split('[, ]+', args.tids.strip())

  t0=time.time()

  if args.op=="D2T":
    c2b2r.slap.Utils.Drug2Targets(base_url, cids, fout)

  elif args.op=="T2D":
    c2b2r.slap.Utils.Target2Drugs(base_url, tids, fout)

  elif args.op=="DTP":
    c2b2r.slap.Utils.DrugTargetPaths(base_url, cids, tids, args.cid_skip, args.cid_nmax, args.tid_skip, args.tid_nmax, args.odir, fout)

  elif args.op=="DSS":
    c2b2r.slap.Utils.Drug2BioSimilarDrugs(base_url, cids, fout)

  elif args.op=="DDS":
    c2b2r.slap.Utils.DDSimilarity(base_url, cid, cid2, fout)

  else:
    parser.error('Unknown operation: %s'%args.op)

  logging.info('Elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))))
