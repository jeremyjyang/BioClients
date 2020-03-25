#!/usr/bin/env python
#############################################################################
### pubchem_ids2mols.py - 
### 
### ref: http://pubchem.ncbi.nlm.nih.gov/pug_rest/
#############################################################################
### Jeremy Yang
### 10 Apr 2015
#############################################################################
import os,sys,re,getopt,time
import csv,urllib2

import time_utils
import pubchem_utils

#############################################################################
def main():
  global PROG,SCRATCHDIR
  PROG=os.path.basename(sys.argv[0])
  SCRATCHDIR=os.getcwd()+'/data/scratch'
  idtype='CID';
  global API_HOST, API_BASE_PATH
  API_HOST='pubchem.ncbi.nlm.nih.gov'
  API_BASE_PATH='rest/pug'
  nchunk=50;

  usage='''
  %(PROG)s - fetch molecule files (SD or SMI) for IDs (PUG REST client)

  required:
  --i INFILE ........................ input IDs file
  --o OUTFILE ....................... output molecule file

  options:
  --idtype CID|SID .................. [default=%(IDTYPE)s]
  --fmt FMT ......................... smiles|sdf [default via filename]
  --nmax NMAX ....................... maximum N IDs
  --skip NSKIP ...................... skip N IDs
  --nchunk NCHUNK ................... IDs per PUG request [%(NCHUNK)s]
  --ftp_ntries NTRIES ............... max tries per ftp-get
  --gz .............................. output gzipped [default via filename]
  --api_host API_HOST ............... [%(API_HOST)s]
  --api_base_path API_BASE_PATH ..... [%(API_BASE_PATH)s]
  --v[v[v]] ......................... verbose [very [very]]
  --h ............................... this help
'''%{'PROG':PROG,
	'API_HOST':API_HOST,
	'API_BASE_PATH':API_BASE_PATH,
	'IDTYPE':idtype,
	'NCHUNK':nchunk}

  def ErrorExit(msg):
    print >>sys.stderr,msg
    sys.exit(1)

  ifile=None; ofile=None;
  verbose=0; nskip=0; nmax=0;
  ftp_ntries=20;
  fmt=None;
  gzip=False;
  opts,pargs = getopt.getopt(sys.argv[1:],'',['h','v','vv','vvv',
	'i=','in=','ftp_ntries=',
	'o=','out=','fmt=','gz','gzip',
	'skip=','nmax=','n=','nchunk=',
	'api_host=','api_base_path=','idtype='])
  if not opts: ErrorExit(usage)
  for (opt,val) in opts:
    if opt=='--h': ErrorExit(usage)
    elif opt=='--i': ifile=val
    elif opt=='--o': ofile=val
    elif opt=='--nmax': nmax=int(val)
    elif opt=='--idtype': idtype=val
    elif opt=='--api_host': API_HOST=val
    elif opt=='--api_base_path': API_BASE_PATH=val
    elif opt=='--nchunk': nchunk=int(val)
    elif opt=='--ftp_ntries': ftp_ntries=int(val)
    elif opt=='--fmt': fmt=val
    elif opt=='--gz': gzip=True
    elif opt=='--skip': nskip=int(val)
    elif opt=='--v': verbose=1
    elif opt=='--vv': verbose=2
    elif opt=='--vvv': verbose=3
    else: ErrorExit('Illegal option: %s'%val)

  BASE_URI='http://'+API_HOST+'/'+API_BASE_PATH

  if not ifile:
    ErrorExit('--i input file required\n'+usage)

  if ofile:

    if (ofile[-3:]=='.gz'):
      gzip=True
      ext=re.sub('^.*\.','',ofile[:-3])
    else:
      ext=re.sub('^.*\.','',ofile)

    if not fmt: fmt=ext
    if fmt=='smi': fmt='smiles'
    if fmt not in ('smiles','sdf'):
      ErrorExit('format "smiles" or "sdf" required\n'+usage)

    fout=open(ofile,'w+')

    if not fout:
      ErrorExit('cannot open: %s\n%s'%(ofile,usage))

  else:
    fout=sys.stdout

  if idtype not in ('SID','CID'):
    ErrorExit('idtype "SID" or "CID" required\n'+usage)

  fids=file(ifile)
  if not fids:
    ErrorExit('cannot open: %s\n%s'%(ifile,usage))
  print >>sys.stderr, time.asctime()

  t0=time.time()

  ### For each CID|SID, query using URI like:
  ### http://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/1001/property/IsomericSMILES
  ### or
  ### http://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/1001/SDF

  n_id=0; 
  n_id_notfound=0;
  n_out=0;
  while True:
    line=fids.readline()
    if not line: break
    n_id+=1
    if nskip and n_id<=nskip:
      continue
    if nmax and n_id>nmax: break
    line=line.rstrip()
    fields=line.split()
    if len(fields)<1:
      print >>sys.stderr, 'Warning: bad line; no %s [%d]: %s'%(idtype,n_id,line)
      continue
    id_query=int(fields[0])

    smi=None; sdf=None;
    if idtype=='SID':
      if fmt=='sdf':
        sdf=pubchem_utils.Sid2SDF(BASE_URI,id_query,verbose)
      else:
        smi=pubchem_utils.Sid2Smiles(BASE_URI,id_query,verbose)
    else:
      if fmt=='sdf':
        sdf=pubchem_utils.Cid2SDF(BASE_URI,id_query,verbose)
      else:
        smi=pubchem_utils.Cid2Smiles(BASE_URI,id_query,verbose)

    if fmt=='sdf':
      if not sdf:
        n_id_notfound+=1
        print >>sys.stderr, 'Error: not found [%s=%d]'%(idtype,id_query)
      else:
        fout.write(sdf) ## includes trailing newline
        n_out+=1
    else:
      if not smi:
        n_id_notfound+=1
        print >>sys.stderr, 'Error: not found [%s=%d]'%(idtype,id_query)
      else:
        fout.write("%s %d\n"%(smi,id_query))
        n_out+=1

    if 0==(n_id%100):
      print >>sys.stderr, ("n_id = %d ; elapsed time: %s\t[%s]"%(n_id,time_utils.NiceTime(time.time()-t0),time.asctime()))
    if n_id==nmax:
      break

  fout.close()
  print >>sys.stderr, 'ids in: %d'%(n_id)
  print >>sys.stderr, 'mols out: %d'%(n_out)
  print >>sys.stderr, ("total elapsed time: %s"%(time_utils.NiceTime(time.time()-t0)))
  print >>sys.stderr, time.asctime()

#############################################################################
if __name__=='__main__':
  #import cProfile
  #cProfile.run('main()')
  main()

