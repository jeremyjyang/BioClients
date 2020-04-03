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
        "list_substancesources", "list_assaysources",
        "name2sid", "name2cid", "name2synonyms",
        "smi2cid",
        "cid2smi", "cid2smiles", "cid2sdf", "cid2properties", "cid2inchi",
        "cid2synonyms", "cid2sid", "cid2assaysummary",
        "sid2cid", "sid2sdf", "sid2assaysummary",
        "aid2name", "assaydescriptions", "assayresults" ]
  parser = argparse.ArgumentParser(description="PubChem PUG REST client")
  parser.add_argument("op",choices=ops,help='operation')
  parser.add_argument("--i", dest="ifile", help="input IDs file (CID|SID)")
  parser.add_argument("--o", dest="ofile", help="output (usually TSV)")
  parser.add_argument("--ids", help="input IDs (CID|SID) (comma-separated)")
  parser.add_argument("--aids", help="input AIDs (comma-separated)")
  parser.add_argument("--iaid", dest="ifile_aid", help="input AIDs file")
  parser.add_argument("--names", help="name queries (comma-separated)")
  parser.add_argument("--smiles", help="SMILES query")
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

  if args.ifile:
    fin = open(args.ifile)
    ids=[]
    while True:
      line=fin.readline()
      if not line: break
      try:
        ids.append(int(line.rstrip()))
      except:
        logging.error('Bad input ID: %s'%line)
        continue
    logging.info('Input IDs: %d'%(len(ids)))
    fin.close()
  elif args.ids:
    ids = re.split(r'[,\s]+', args.ids)
  else:
    ids=[]

  if args.ifile_aid:
    fin = open(args.ifile_aid)
    aids=[]
    while True:
      line=fin.readline()
      if not line: break
      try:
        aids.append(int(line.rstrip()))
      except:
        logging.error('Bad input AID: %s'%line)
        continue
    logging.info('Input AIDs: %d'%(len(aids)))
    fin.close()
  elif args.aids:
    aids = re.split(r'[,\s]+', args.aids)
  else:
    aids=[]

  names = re.split(r'[,\s]+', args.names) if args.names else []

  t0=time.time()

  if args.op == 'list_assaysources':
    pubchem.Utils.ListAssaySources(BASE_URL, fout)

  elif args.op == 'list_substancesources':
    pubchem.Utils.ListSubstanceSources(BASE_URL, fout)

  elif args.op == 'cid2synonyms':
    pubchem.Utils.CID2Synonyms(BASE_URL, ids, args.skip, args.nmax, args.nmax_per_cid, fout)

  elif args.op == 'cid2properties':
    pubchem.Utils.CID2Properties(BASE_URL, ids, fout)

  elif args.op == 'cid2inchi':
    pubchem.Utils.CID2Inchi(BASE_URL, ids, fout)

  elif args.op == 'cid2sid':
    pubchem.Utils.CID2SID(BASE_URL, ids, fout)

  elif args.op == 'cid2smiles':
    pubchem.Utils.CID2Smiles(BASE_URL, ids, args.isomeric, fout)

  elif args.op == 'cid2sdf':
    pubchem.Utils.CID2SDF(BASE_URL, ids, fout)

  elif args.op == 'cid2assaysummary':
    pubchem.Utils.CID2AssaySummary(BASE_URL, ids, fout)

  elif args.op == 'sid2cid':
    pubchem.Utils.SID2CID(BASE_URL, ids, fout)

  elif args.op == 'sid2assaysummary':
    pubchem.Utils.SID2Assaysummary(BASE_URL, ids, fout)

  elif args.op == 'sid2sdf':
    pubchem.Utils.SID2SDF(BASE_URL, ids, fout, args.skip, args.nmax)

  elif args.op == 'smi2cid':
    if not args.smiles: parser.error('--smiles required.')
    pubchem.Utils.Smiles2CID(BASE_URL, args.smiles, fout)

  elif args.op == 'name2sid':
    pubchem.Utils.Name2SID(BASE_URL, names, fout)

  elif args.op == 'name2cid':
    pubchem.Utils.Name2CID(BASE_URL, names, fout)

  elif args.op == 'name2synonyms':
    pubchem.Utils.Name2Synonyms(BASE_URL, names, fout)

  elif args.op == 'aid2name':
    pubchem.Utils.AID2Name(BASE_URL, aids, fout)

  elif args.op == 'assaydescriptions':
    pubchem.Utils.AssayDescriptions(BASE_URL, aids, fout)

  elif args.op == 'assayresults':
    #Requires AIDs and SIDs.
    pubchem.Utils.GetAssaySIDResults(BASE_URL, aids, ids, args.skip, args.nmax, fout)

  else:
    parser.error('Invalid operation: %s'%args.op)

  logging.info(('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0)))))

