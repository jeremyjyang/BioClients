#!/usr/bin/env python3
#############################################################################
### pubchem_mols2ids.py - From PubChem PUG REST API, 
### 
### Input:
###   SMILES|InChI [NAME]
### Output:
###   SMILES|InChI<TAB>[CID|SID]<TAB>[NAME]
###
### ref: http://pubchem.ncbi.nlm.nih.gov/pug_rest/
#############################################################################
### TODO: fix/improve the errors
### "Error (Exception): 'NoneType' object has no attribute '__getitem__'"
### "HTTP Error: HTTP Error 400: Bad Request"
#############################################################################
import os,sys,re,argparse,time,logging

import time_utils
import pubchem_utils

API_HOST="pubchem.ncbi.nlm.nih.gov"
API_BASE_PATH="/rest/pug"

#############################################################################
def main():
  global PROG,SCRATCHDIR
  PROG=os.path.basename(sys.argv[0])
  SCRATCHDIR=os.getcwd()+'/data/scratch'

  ifmts = ['smiles', 'inchi']
  logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
  parser = argparse.ArgumentParser(description="fetch CIDs for input SMILES or InChI (PUG REST client)")
  parser.add_argument("--i", dest="ifile", help="input molecule file")
  parser.add_argument("--ifmt", choices=ifmts, default="smiles", help="input format")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("--skip", type=int, default=0)
  parser.add_argument("--nmax", type=int, default=0)
  parser.add_argument("--nchunk", type=int, default=50, help="IDs per PUG request")
  parser.add_argument("--o", dest="ofile", help="output IDs file")
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  BASE_URL = 'https://'+args.api_host+args.api_base_path

  if not args.ifile:
    parser.error('input file required.')

  fin = open(args.ifile)
  if not fin:
    parser.error('cannot open: %s'%(args.ifile))
  if args.ofile:
    fout = open(args.ofile, 'w')
  else:
    fout = sys.stdout

  logging.info(time.asctime())

  t0=time.time()

  ### For each SMILES, query using URI like:
  ### http://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/CCCC/cids/TXT

  nmol=0; nmol_notfound=0
  n_id=0; n_id_out=0; 
  while True:
    line=fin.readline()
    if not line: break
    nmol+=1
    if args.skip and nmol<=args.skip:
      continue
    if args.nmax and nmol>(args.nmax+args.skip): break
    line=line.rstrip()
    fields=line.split()
    if len(fields)<1:
      logging.info('Warning: bad line; no SMILES [%d]: %s'%(nmol,line))
      continue
    qry=fields[0]
    if len(fields)>1:
      name=re.sub(r'^[^\s]*\s','',line)
    else:
      name='%s'%nmol

    try:
      if args.ifmt == 'inchi':
        cids=pubchem_utils.Inchi2Cids(BASE_URL, qry, args.verbose)
      else:
        cids=pubchem_utils.Smi2Cids(BASE_URL, qry, args.verbose)
    except Exception as e:
      logging.info('ERROR: REST request failed (%s): %s %s'%(e, qry, name))
      nmol_notfound+=1
      fout.write("%s\tNA\t%s\n"%(qry, name))
      continue

    cids_str=(';'.join(map(lambda x:str(x),cids)))
    fout.write("%s\t%s\t%s\n"%(qry, cids_str, name))
    if len(cids)==1 and cids[0]==0:
      nmol_notfound+=1
    else:
      n_id+=len(cids)
      n_id_out+=n_id

    if nmol>0 and (nmol%100)==0:
      logging.info(("nmol = %d ; elapsed time: %s\t[%s]"%(nmol, time_utils.NiceTime(time.time()-t0), time.asctime())))
    if nmol==args.nmax:
      break

  fout.close()

  logging.info('mols read: %d'%(nmol))
  logging.info('mols not found: %d'%(nmol_notfound))
  logging.info('ids found: %d'%(n_id))
  logging.info('ids out: %d'%(n_id_out))
  logging.info(("total elapsed time: %s"%(time_utils.NiceTime(time.time()-t0))))

#############################################################################
if __name__=='__main__':
  #import cProfile
  #cProfile.run('main()')
  main()

