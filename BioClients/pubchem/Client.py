#!/usr/bin/env python3
"""
Utility app for the PubChem PUG REST API.
"""
###
import sys,os,re,argparse,time,logging
#
from .. import pubchem
#
API_HOST='pubchem.ncbi.nlm.nih.gov'
API_BASE_PATH='/rest/pug'
#
##############################################################################
if __name__=='__main__':
  ops = [
        "list_sources_substance", "list_sources_assay",
        "get_name2sid", "get_name2cid", "get_name2synonyms",
        "get_smi2cid",
        "get_cid2smi", "get_cid2smiles", "get_cid2sdf",
        "get_cid2properties", "get_cid2inchi",
        "get_cid2synonyms", "get_cid2sid", "get_cid2assaysummary",
        "get_sid2cid", "get_sid2sdf", "get_sid2assaysummary",
        "get_assayname", "get_assaydescriptions", "get_assayresults" ]
  parser = argparse.ArgumentParser(description="PubChem PUG REST client")
  parser.add_argument("op",choices=ops,help='operation')
  parser.add_argument("--i", dest="ifile", help="input IDs file (CID|SID|SMILES|name)")
  parser.add_argument("--ids", help="input IDs (CID|SID|SMILES|name) (comma-separated)")
  parser.add_argument("--aids", help="input AIDs (comma-separated)")
  parser.add_argument("--iaid", dest="ifile_aid", help="input AIDs file")
  parser.add_argument("--o", dest="ofile", help="output (usually TSV)")
  parser.add_argument("--isomeric", action="store_true", help="return Isomeric SMILES")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("--skip", type=int, default=0)
  parser.add_argument("--nmax", type=int, default=0)
  parser.add_argument("--nmax_per_cid", type=int, default=20)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  BASE_URL = 'https://'+args.api_host+args.api_base_path

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
  logging.info('Input IDs: %d'%(len(ids)))

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
  logging.info('Input AIDs: %d'%(len(aids)))

  t0=time.time()

  if args.op == 'list_sources_assay':
    pubchem.Utils.ListSources(BASE_URL, "assay", fout)

  elif args.op == 'list_sources_substance':
    pubchem.Utils.ListSources(BASE_URL, "substance", fout)

  elif args.op == 'get_cid2synonyms':
    pubchem.Utils.GetCID2Synonyms(BASE_URL, ids, args.skip, args.nmax, args.nmax_per_cid, fout)

  elif args.op == 'get_cid2properties':
    pubchem.Utils.GetCID2Properties(BASE_URL, ids, fout)

  elif args.op == 'get_cid2inchi':
    pubchem.Utils.GetCID2Inchi(BASE_URL, ids, fout)

  elif args.op == 'get_cid2sid':
    pubchem.Utils.GetCID2SID(BASE_URL, ids, fout)

  elif args.op == 'get_cid2smiles':
    pubchem.Utils.GetCID2Smiles(BASE_URL, ids, args.isomeric, fout)

  elif args.op == 'get_cid2sdf':
    pubchem.Utils.GetCID2SDF(BASE_URL, ids, fout)

  elif args.op == 'get_cid2assaysummary':
    pubchem.Utils.GetCID2AssaySummary(BASE_URL, ids, fout)

  elif args.op == 'get_sid2cid':
    pubchem.Utils.GetSID2CID(BASE_URL, ids, fout)

  elif args.op == 'get_sid2assaysummary':
    pubchem.Utils.GetSID2AssaySummary(BASE_URL, ids, fout)

  elif args.op == 'get_sid2sdf':
    pubchem.Utils.GetSID2SDF(BASE_URL, ids, fout, args.skip, args.nmax)

  elif args.op == 'get_smi2cid':
    pubchem.Utils.GetSmiles2CID(BASE_URL, ids, fout)

  elif args.op == 'get_name2sid':
    pubchem.Utils.GetName2SID(BASE_URL, ids, fout)

  elif args.op == 'get_name2cid':
    pubchem.Utils.GetName2CID(BASE_URL, ids, fout)

  elif args.op == 'get_name2synonyms':
    pubchem.Utils.GetName2Synonyms(BASE_URL, ids, fout)

  elif args.op == 'get_assayname':
    pubchem.Utils.GetAssayName(BASE_URL, aids, fout)

  elif args.op == 'get_assaydescriptions':
    pubchem.Utils.GetAssayDescriptions(BASE_URL, aids, args.skip, args.nmax, fout)

  elif args.op == 'get_assayresults':
    if not (aids and ids): parser.error('Input AIDs and SIDs required.')
    pubchem.Utils.GetAssaySIDResults(BASE_URL, aids, ids, args.skip, args.nmax, fout)

  else:
    parser.error('Invalid operation: %s'%args.op)

  logging.info(('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0)))))

