#!/usr/bin/env python
#############################################################################
### pubchem_ftp_query.py - 
### 
### For accessing files via FTP site; ftp://ftp.ncbi.nlm.nih.gov/pubchem/
### 
### Jeremy J Yang
### 14 Feb 2017
#############################################################################
import sys,os,re,time,getopt
import urllib,urllib2,tempfile

import pubchem_ftp_utils

PROG=os.path.basename(sys.argv[0])

FTPURL='ftp://ftp.ncbi.nlm.nih.gov/pubchem'
POLL_WAIT=10
MAX_WAIT=600

#############################################################################
if __name__=='__main__':
  def ErrorExit(msg):
    print >>sys.stderr,msg
    sys.exit(1)

  usage='''
  %(PROG)s - access PubChem FTP site

  required (one of):
  --ftpget fpath ...... path of file
  --ftpls dpath ....... path of dir

  options:
  --o OFILE ........... 
  --ftp_ntries N ...... max tries per ftp-get
  --sdf2smi ........... convert SDF to SMILES
  --[v]v .............. [very] verbose
  --h ................. this help
'''%{'PROG':PROG}

  ifile=None; ofile=None; verbose=0; skip=0; nmax=0; ftp_ntries=20;
  gzip=False; ftpget=None; ftpls=None;
  sdf2smi=False;
  opts,pargs = getopt.getopt(sys.argv[1:],'',['h','v','vv','i=','ftp_ntries=',
  'ftpget=','ftpls=','o=','sdf2smi','gz','gzip','skip=','nmax=','n='])
  if not opts: ErrorExit(usage)
  for (opt,val) in opts:
    if opt=='--h': ErrorExit(usage)
    elif opt=='--i': ifile=val
    elif opt=='--ftpget': ftpget=val
    elif opt=='--ftpls': ftpls=val
    elif opt=='--o': ofile=val
    elif opt=='--nmax': nmax=int(val)
    elif opt=='--ftp_ntries': ftp_ntries=int(val)
    elif opt=='--skip': skip=int(val)
    elif opt=='--sdf2smi': sdf2smi=True
    elif opt=='--vv': verbose=2
    elif opt=='--v': verbose=1
    else: ErrorExit('Illegal option: %s'%val)


  if ftpget:
    if not ofile: ErrorExit('-o required with -get.')
    url=("%s%s"%(FTPURL,ftpget))
    fout=file(ofile,'w')
    if sdf2smi:
      nbytes = pubchem_ftp_utils.GetUrlSDF2SMI(url,fout,ntries=20,poll_wait=10,verbose=verbose)
    else:
      nbytes = pubchem_ftp_utils.GetUrl(url,fout,ntries=20,poll_wait=10,verbose=verbose)
    print >>sys.stderr, "%s: bytes: %.2fMB"%(PROG,nbytes/1e6)
  elif ftpls!=None:
    url=("%s%s"%(FTPURL,ftpls))
    pubchem_ftp_utils.GetUrl(url,sys.stdout,ntries=20,poll_wait=10,verbose=verbose)
