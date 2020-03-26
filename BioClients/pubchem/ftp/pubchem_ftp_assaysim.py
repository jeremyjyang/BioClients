#!/usr/bin/env python
#############################################################################
### pubchem_assaysim.py - assay similarity based on activity profiles
### from PubChem CSV assay file[s]
#############################################################################
import os,sys,re,getopt,gzip,zipfile,tempfile
#try:
#  import gdbm
#except:
#  import dbm as gdbm

from ... import pubchem

PROG=os.path.basename(sys.argv[0])
DATADIR="/home/data/pubchem/bioassay/csv/data"

SCRATCHDIR='/tmp/'+PROG+'_SCRATCHDIR'

#############################################################################
if __name__=='__main__':
  usage='''
  %(PROG)s - assay similarity based on activity profiles (A vs. B)

  required:
  --aidA=<AID> ... assay ID A
  --aidB=<AID> ... assay ID B

  options:

  --v            ... verbose
  --vv           ... very verbose
  --h            ... this help
'''%{'PROG':PROG,'DATADIR':DATADIR}

  def ErrorExit(msg):
    print >>sys.stderr,msg
    sys.exit(1)

  indir=DATADIR;
  infile=None; verbose=0;
  aidA=None; aidB=None; 
  opts,pargs = getopt.getopt(sys.argv[1:],'',['h','v','vv','indir=',
  'aidA=','aidB=','infile=' ])
  if not opts: ErrorExit(usage)
  for (opt,val) in opts:
    if opt=='--h': ErrorExit(usage)
    elif opt=='--indir': indir=val
    elif opt=='--aidA': aidA=val
    elif opt=='--aidB': aidB=val
    elif opt=='--vv': verbose=2
    elif opt=='--v': verbose=1
    else: ErrorExit('Illegal option: %s'%val)

  if not (aidA and aidB):
    ErrorExit('--aidA and --aidB required\n'+usage)

  try:
    aidA=int(aidA)
    aidB=int(aidB)
  except:
    ErrorExit('aidA and aidB must be integers.\n'+usage)

###

  fpath_csv_gzA=None; fpath_csv_gzB=None;
  for fname_zip in os.listdir(indir):
    if not re.search('\.zip',fname_zip): continue
    fpath_zip=indir+'/'+fname_zip
    try:
      zf=zipfile.ZipFile(fpath_zip,'r')
    except:
      print >>sys.stderr, 'ERROR: cannot read fpath_zip: "%s"'%fpath_zip
      continue
    flist_csv_gz=zf.namelist()
    zf.close()
    for fpath_csv_gz in flist_csv_gz:
      if not re.search('\.csv\.gz',fpath_csv_gz): continue
      try:
        if re.search(r'/',fpath_csv_gz):
          txt=re.sub(r'^.*/(\d*)\.csv\.gz',r'\1',fpath_csv_gz)
        else:
          txt=re.sub(r'\.csv\.gz','',fpath_csv_gz)
        aid=int(txt)
      except:
        print >>sys.stderr, 'cannot parse AID: "%s"'%fpath_csv_gz
        print >>sys.stderr, 'DEBUG txt: "%s"'%txt
        continue
      if aid==aidA:
        fpath_zipA=fpath_zip
        fpath_csv_gzA=fpath_csv_gz
        if verbose>1:
          print >>sys.stderr, '\tA: %s: %s (%s)'%(aidA,fpath_zipA,fpath_csv_gzA)
      if aid==aidB:
        fpath_zipB=fpath_zip
        fpath_csv_gzB=fpath_csv_gz
        if verbose>1:
          print >>sys.stderr, '\tB: %s: %s (%s)'%(aidB,fpath_zipB,fpath_csv_gzB)
      if fpath_csv_gzA and fpath_csv_gzB: break
    if fpath_csv_gzA and fpath_csv_gzB: break

  if not fpath_csv_gzA:
    ErrorExit('ERROR: could not find file for AID %s'%(aidA))
  if not fpath_csv_gzB:
    ErrorExit('ERROR: could not find file for AID %s'%(aidB))


  if not os.access(SCRATCHDIR,os.R_OK):
    try:
      os.mkdir(SCRATCHDIR)
    except:
      print >>sys.stderr, 'ERROR: failed to create SCRATCHDIR %s'%SCRATCHDIR
      sys.exit(1)


  zfA=zipfile.ZipFile(fpath_zipA,'r')
  cwd=os.getcwd()
  os.chdir(SCRATCHDIR)
  zfA.extract(fpath_csv_gzA)
  os.chdir(cwd)
  zfA.close()
  f_csvA=gzip.open(SCRATCHDIR+'/'+fpath_csv_gzA)
  csvA=f_csvA.read()
  f_csvA.close()
  if not csvA:
    ErrorExit('ERROR: file empty: AID %d: %s'%(aidA,fpath_csv_gzA))

  zfB=zipfile.ZipFile(fpath_zipB,'r')
  cwd=os.getcwd()
  os.chdir(SCRATCHDIR)
  zfB.extract(fpath_csv_gzB)
  os.chdir(cwd)
  zfB.close()
  f_csvB=gzip.open(SCRATCHDIR+'/'+fpath_csv_gzB)
  csvB=f_csvB.read()
  f_csvB.close()
  if not csvB:
    ErrorExit('ERROR: file empty: AID %d: %s'%(aidB,fpath_csv_gzB))


  sids_active=[]; sids_inactive=[]; sids_inconclusive=[]; sids_unspecified=[];
  sids_discrepant=[]; sids_tested=[];
  sidset={};
  n_datapoints_total=0
  use_cids=False;

  sidsA=pubchem.ftp.Utils.ExtractOutcomes(csvA,sidset,use_cids)

  sidsB=pubchem.ftp.Utils.ExtractOutcomes(csvB,sidset,use_cids)

  print >>sys.stderr, '\t  aidA, SIDs total: %3d'%(len(sidsA.keys()))
  print >>sys.stderr, '\t  aidB, SIDs total: %3d'%(len(sidsB.keys()))

  sids_all=(set(sidsA.keys()) | set(sidsB.keys()))
  sids_common=(set(sidsA.keys()) & set(sidsB.keys()))
  print >>sys.stderr, '\t  aidA | aidB, SIDs total: %3d'%(len(sids_all))
  print >>sys.stderr, '\t  aidA & aidB, SIDs common: %3d'%(len(sids_common))


  n_activeA=0; n_inactiveA=0; n_inconclusiveA=0; n_unspecifiedA=0; n_discrepantA=0;
  n_activeB=0; n_inactiveB=0; n_inconclusiveB=0; n_unspecifiedB=0; n_discrepantB=0;
  n_active_common=0
  for sid in sids_all:
    outcomeA=None;
    outcomeB=None;
    if sidsA.has_key(sid):
      outcomeA=sidsA[sid]['outcome']
      if outcomeA==2: n_activeA+=1
      elif outcomeA==1: n_inactiveA+=1
      elif outcomeA==3: n_inconclusiveA+=1
      elif outcomeA==4: n_unspecifiedA+=1
      elif outcomeA==5: n_discrepantA+=1
      else: print >>sys.stderr, 'ERROR: outcomeA=%d'%(sidsA[sid]['outcome'])
    if sidsB.has_key(sid):
      outcomeB=sidsB[sid]['outcome']
      if outcomeB==2: n_activeB+=1
      elif outcomeB==1: n_inactiveB+=1
      elif outcomeB==3: n_inconclusiveB+=1
      elif outcomeB==4: n_unspecifiedB+=1
      elif outcomeB==5: n_discrepantB+=1
      else: print >>sys.stderr, 'ERROR: outcomeB=%d'%(sidsB[sid]['outcome'])
    if outcomeA==2 and outcomeB==2:
      n_active_common+=1

  if verbose>1:
    print >>sys.stderr, '\tA:       active: %3d'%(n_activeA)
    print >>sys.stderr, '\tA:     inactive: %3d'%(n_inactiveA)
    print >>sys.stderr, '\tA: inconclusive: %3d'%(n_inconclusiveA)
    print >>sys.stderr, '\tA:  unspecified: %3d'%(n_unspecifiedA)
    print >>sys.stderr, '\tA:   discrepant: %3d'%(n_discrepantA)
    print >>sys.stderr, '\tA:        total: %3d'%(len(sidsA.keys()))
    print >>sys.stderr, '\tB:       active: %3d'%(n_activeB)
    print >>sys.stderr, '\tB:     inactive: %3d'%(n_inactiveB)
    print >>sys.stderr, '\tB: inconclusive: %3d'%(n_inconclusiveB)
    print >>sys.stderr, '\tB:  unspecified: %3d'%(n_unspecifiedB)
    print >>sys.stderr, '\tB:   discrepant: %3d'%(n_discrepantB)
    print >>sys.stderr, '\tB:        total: %3d'%(len(sidsB.keys()))
    print >>sys.stderr, '\t  common active: %3d'%(n_active_common)

  sim = float(n_active_common) / len(sids_common)
  print >>sys.stderr, '\t  Tanimoto similarity: %.3f'%(sim)
