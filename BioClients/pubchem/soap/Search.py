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
  SEARCHTYPES = ["substructure", "similarity", "exact", "standardize"]

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
  parser.add_argument("--poll_wait", type=int, default=POLL_WAIT, help="polling wait interval")
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

  pugreq = pubchem.soap.Utils.SubmitQuery_Structural(args.pugurl, args.qsmi, args.searchtype, args.sim_cutoff, args.active, args.mlsmr, args.nmax)

  ### error status values include: "input-error", "server-error"
  if pugreq.status not in ("success", "queued", "running"):
    logging.error("""Query failed; quitting (status={}, error="{}").""".format(pugreq.status, pugreq.error))
    sys.exit()
  logging.info("Query status: {}".format(pugreq.status))

  if not pugreq.reqid and not pugreq.qkey:
    parser.error('Query ok but no ID.')

  i_poll=0
  while not pugreq.qkey:
    if time.time()-t0>args.max_wait:
      pugreq.cancel()
      logging.error('Max wait exceeded ({} sec); quitting.'.format(args.max_wait))
    logging.info('Polling PUG [{}]...'.format(pugreq.reqid))
    pugreq.getStatus()
    if pugreq.qkey: break
    logging.info('{} elapsed; {} sec wait; status={}'.format(ElapsedTime(t0), args.poll_wait, pugreq.status))
    logging.info(pugreq.error)
    if re.search('No result found', pugreq.error, re.I):
      sys.exit()
    time.sleep(args.poll_wait)
    i_poll+=1

  pugreq2 = pubchem.soap.Utils.MonitorQuery(args.pugurl, pugreq.qkey, pugreq.wenv, fmt, do_gz)
  i_poll=0
  while not pugreq2.url:
    if time.time()-t0>args.max_wait:
      pugreq2.cancel()
      logging.error('Max wait exceeded ({} sec); quitting.'.format(args.max_wait))
    logging.info('Polling PUG [{}]...'.format(pugreq2.reqid))
    pugreq2.getStatus()
    if pugreq2.url: break
    logging.info('{} elapsed; {} sec wait; status={}'.format(ElapsedTime(t0), args.poll_wait, pugreq2.status))
    time.sleep(args.poll_wait)
    i_poll+=1

  pubchem.soap.Utils.DownloadResults(pugreq2.url, fout)

  if args.ofile:
    logging.info('URL: {} downloaded to {} ({:.2f}MB)'.format(pugreq2.url, args.ofile, os.stat(args.ofile).st_size/1e6))
  fout.close()
  logging.info('Format: {}{}'.format(fmt, (' (gzipped)' if do_gz else '')))

  logging.info('Elapsed time: {}'.format(time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0))))

