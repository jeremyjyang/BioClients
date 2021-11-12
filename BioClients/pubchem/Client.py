#!/usr/bin/env python3
"""
Utility app for the PubChem PUG REST API.
"""
###
import sys,os,re,argparse,time,logging
#
from .. import pubchem
#
##############################################################################
if __name__=='__main__':
  ops = [
        "list_sources_substance", "list_sources_assay",
        "get_name2sid", "get_name2cid", "get_name2synonyms",
        "get_smi2cid",
        "get_cid2smiles", "get_cid2sdf",
        "get_cid2properties", "get_cid2inchi",
        "get_cid2synonyms", "get_cid2sid", "get_cid2assaysummary",
        "get_sid2cid", "get_sid2sdf", "get_sid2assaysummary",
        "get_assayname", "get_assaydescriptions",
	"get_assaysubstances",
	"get_assaysubstanceresults",]
  parser = argparse.ArgumentParser(description="PubChem PUG REST client")
  parser.add_argument("op",choices=ops,help='operation')
  parser.add_argument("--i", dest="ifile", help="input IDs file (CID|SID|SMILES|name)")
  parser.add_argument("--ids", help="input IDs (CID|SID|SMILES|name) (comma-separated)")
  parser.add_argument("--aids", help="input AIDs (comma-separated)")
  parser.add_argument("--iaid", dest="ifile_aid", help="input AIDs file")
  parser.add_argument("--o", dest="ofile", help="output (usually TSV)")
  parser.add_argument("--api_host", default=pubchem.API_HOST)
  parser.add_argument("--api_base_path", default=pubchem.API_BASE_PATH)
  parser.add_argument("--skip", type=int, default=0)
  parser.add_argument("--nmax", type=int, default=0)
  parser.add_argument("--nmax_per_cid", type=int, default=20)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url = 'https://'+args.api_host+args.api_base_path

  fout = open(args.ofile, "w") if args.ofile else sys.stdout

  ids=[]
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.rstrip())
    fin.close()
  elif args.ids:
    ids = re.split(r'[,\s]+', args.ids)
  logging.info(f"Input IDs: {len(ids)}")

  aids=[]
  if args.ifile_aid:
    fin = open(args.ifile_aid)
    while True:
      line = fin.readline()
      if not line: break
      aids.append(line.rstrip())
    fin.close()
  elif args.aids:
    aids = re.split(r'[,\s]+', args.aids)
  if len(aids)>0: logging.info(f"Input AIDs: {len(aids)}")

  t0=time.time()

  if args.op == 'list_sources_assay':
    pubchem.ListSources("assay", base_url, fout)

  elif args.op == 'list_sources_substance':
    pubchem.ListSources("substance", base_url, fout)

  elif args.op == 'get_cid2synonyms':
    pubchem.GetCID2Synonyms(ids, args.skip, args.nmax,
args.nmax_per_cid, base_url, fout)

  elif args.op == 'get_cid2properties':
    pubchem.GetCID2Properties(ids, base_url, fout)

  elif args.op == 'get_cid2inchi':
    pubchem.GetCID2Inchi(ids, base_url, fout)

  elif args.op == 'get_cid2sid':
    pubchem.GetCID2SID(ids, base_url, fout)

  elif args.op == 'get_cid2smiles':
    pubchem.Utils.GetCID2Smiles(ids, base_url, fout)

  elif args.op == 'get_cid2sdf':
    pubchem.GetCID2SDF(ids, base_url, fout)

  elif args.op == 'get_cid2assaysummary':
    pubchem.GetCID2AssaySummary(ids, base_url, fout)

  elif args.op == 'get_sid2cid':
    pubchem.GetSID2CID(ids, base_url, fout)

  elif args.op == 'get_sid2assaysummary':
    pubchem.GetSID2AssaySummary(ids, base_url, fout)

  elif args.op == 'get_sid2sdf':
    pubchem.GetSID2SDF(ids, fout, args.skip, args.nmax, base_url)

  elif args.op == 'get_smi2cid':
    pubchem.GetSmiles2CID(ids, base_url, fout)

  elif args.op == 'get_name2sid':
    pubchem.GetName2SID(ids, args.skip, args.nmax, base_url, fout)

  elif args.op == 'get_name2cid':
    pubchem.GetName2CID(ids, args.skip, args.nmax, base_url, fout)

  elif args.op == 'get_name2synonyms':
    pubchem.GetName2Synonyms(ids, args.skip, args.nmax, base_url, fout)

  elif args.op == 'get_assayname':
    pubchem.GetAssayName(aids, base_url, fout)

  elif args.op == 'get_assaydescriptions':
    pubchem.GetAssayDescriptions(aids, args.skip, args.nmax, base_url, fout)

  elif args.op == 'get_assaysubstances':
    pubchem.Utils.GetAssaySIDs(aids, args.skip, args.nmax, base_url, fout)

  elif args.op == 'get_assaysubstanceresults':
    if not (aids and ids): parser.error('Input AIDs and SIDs required.')
    pubchem.GetAssaySIDResults(aids, ids, args.skip, args.nmax, base_url, fout)

  else:
    parser.error(f"Invalid operation: {args.op}")

  logging.info(('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0)))))

