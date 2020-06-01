#!/usr/bin/env python3
"""
PubChem/PUG-SOAP sub|sim|exact search.
Originally pug_search.py (~2010)
https://pubchem.ncbi.nlm.nih.gov/pug_soap/pug_soap.cgi?wsdl
"""
import sys,os,re,urllib,time,argparse,tempfile,logging

from ... import pubchem
from ...pubchem.soap import Utils

#############################################################################
def ElapsedTime(t0):
  return (time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0)))

#############################################################################
if __name__=='__main__':
  PUGURL='https://pubchem.ncbi.nlm.nih.gov/pug/pug.cgi';
  POLL_WAIT=10; MAX_WAIT=300;
  SIM_CUTOFF=0.80;
  NMAX=100;
  SEARCHTYPES = ["substructure", "similarity", "exact"]

  parser = argparse.ArgumentParser(description="PubChem PUG SOAP client: sub|sim|exact search, fetch smiles|sdfs")
  parser.add_argument("--o", dest="ofile", help="output smiles|sdf file (w/ CIDs)")
  parser.add_argument("--qsmi", help="input query smiles (or smarts)")
  parser.add_argument("--fmt", choices=["smiles", "sdf"], help="[or via filename]")
  parser.add_argument("--gz", action="store_true", help="output gzipped [default via filename]")
  parser.add_argument("--out_cids", action="store_true", help="output CIDs (only w/ smiles output)")
  parser.add_argument("--searchtype", choices=SEARCHTYPES, default="exact", help="search type")
  parser.add_argument("--sim_cutoff", type=float, default=SIM_CUTOFF, help="similarity cutoff, Tanimoto")
  parser.add_argument("--active", help="active mols only (in any assay)")
  parser.add_argument("--mlsmr", help="MLSMR mols only")
  parser.add_argument("--nmax", type=int, default=NMAX, help="max hits returned")
  parser.add_argument("--max_wait", type=int, default=MAX_WAIT, help="max wait for query")
  parser.add_argument("--pugurl", default=PUGURL)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  if not args.qsmi:
    parser.error('SMILES required\n'+usage)
  logging.info('query: "%s"'%args.qsmi)

  fmt = args.fmt if args.fmt else None

  do_gz = args.gz if args.gz else False

  fout = open(args.ofile, 'wb') if args.ofile else sys.stdout

  if args.ofile:
    if (args.ofile[-3:]=='.gz'):
      do_gz = True
      ext = re.sub('^.*\.', '', args.ofile[:-3])
    else:
      ext = re.sub('^.*\.', '', args.ofile)
    if not args.fmt: fmt = ext

  if not fmt: fmt = "smiles"
  elif fmt[:3].lower()=='smi': fmt='smiles'
  elif fmt[:3].lower() in ('sdf', 'mol', 'mdl'): fmt='sdf'

  t0=time.time()	## start timer

  status,reqid,qkey,wenv,error = pubchem.soap.Utils.QueryPug_struct(args.pugurl, args.qsmi, args.searchtype, args.sim_cutoff, args.active, args.mlsmr, args.nmax)

  if status not in ('success', 'queued', 'running'):
    parser.error('Query failed; quitting (status=%s,error="%s").'%(status, error))
  logging.info('Query status: %s'%status)

  if not reqid and not qkey:
    parser.error('Query ok but no ID.')

  i_poll=0
  while not qkey:
    if time.time()-t0>args.max_wait:
      pubchem.soap.Utils.PollPug(args.pugurl, reqid, 'cancel')
      logging.error('Max wait exceeded ({} sec); quitting.'.format(args.max_wait))
    logging.info('Polling PUG [ID={}]...'.format(reqid))
    status,reqid_new,url,qkey,wenv,error = pubchem.soap.Utils.PollPug(args.pugurl, reqid, 'status')
    if reqid_new: reqid=reqid_new
    if qkey: break
    logging.info('{} elapsed; {} sec wait; status={}'.format(ElapsedTime(t0), POLL_WAIT, status))
    logging.info(error)
    if re.search('No result found', error, re.I):
      sys.exit()
    time.sleep(POLL_WAIT)
    i_poll+=1

  status,reqid,url,qkey,wenv,error = pubchem.soap.Utils.QueryPug_qkey(args.pugurl, qkey, wenv, fmt, do_gz)
  i_poll=0
  while not url:
    if time.time()-t0>args.max_wait:
      pubchem.soap.Utils.PollPug(args.pugurl, reqid, 'cancel')
      logging.error('Max wait exceeded ({} sec); quitting.'.format(args.max_wait))
    logging.info('Polling PUG [ID={}]...'.format(reqid))
    status,reqid,url,qkey,wenv,error = pubchem.soap.Utils.PollPug(args.pugurl, reqid, 'status')
    if url: break
 
    logging.info('{} elapsed; {} sec wait; status={}'.format(ElapsedTime(t0), POLL_WAIT, status))
    time.sleep(POLL_WAIT)
    i_poll+=1

  logging.info('Query elapsed time: {}'.format(ElapsedTime(t0)))
  if args.ofile:
    logging.info('URL: {}'.format(url))
    logging.info('Downloading to {}...'.format(args.ofile))

  nbytes = pubchem.soap.Utils.DownloadUrl(url, fout)

  logging.info('Format: {}{}'.format( fmt, (' (gzipped)' if do_gz else '')))

  if args.ofile:
    nbytes = os.stat(args.ofile).st_size
    logging.info('{} ({:.2f}MB)'.format(args.ofile, nbytes/1e6))
  fout.close()

  logging.info('Elapsed time: {}'.format(time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0))))

