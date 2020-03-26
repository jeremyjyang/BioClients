#!/usr/bin/env python
#############################################################################
### pubchem_gini_index.py - for specified SIDs and AIDs, generate Gini Index
### and relevant data for each compound.
###
### Each assay is an individual.  For each assay, Gini default "wealth" 
### function = 
###     1.0 if active 
###     0.0 if inactive 
###     0.5 if inconclusive 
###     avg if multiple
###
#############################################################################
### activity outcomes: 
###   1 = inactive
###   2 = active
###   3 = inconclusive
###   4 = unspecified
###   multiple, differing 1, 2 or 3 = discrepant
###   not 4 = tested
#############################################################################
### Jeremy Yang
###  28 Apr 2009
#############################################################################
import os,sys,re,getopt,gzip,tempfile
try:
  import gdbm
except:
  import dbm as gdbm

from ... import pubchem
from ...util import gini_utils

PROG=os.path.basename(sys.argv[0])
DATADIR="/pangolin_home/data/pubchem/bioassay/csv/data"

#############################################################################
if __name__=='__main__':
  usage='''
  %(PROG)s - Gini selectivity analysis from assay CSV files

  options:
  --indir=<DIR>   ... dir w/ csv.gz assay data [%(DATADIR)s]
  or
  --infile=<FILE>   ... input csv.gz assay data

  --aids=<AIDS> ... list of AIDs to select within --indir dir
  --aidfile=<AIDFILE> ... file of AIDs to select within --indir dir

  --sids=<SIDS> ... list of SIDs to select
  --sidfile=<SIDFILE> ... file of SIDs to select (ignore others)

  --out_gini=<outfile> ... SIDs w/ activity counts and Gini
  --out_raw=<outfile> ... SIDs w/ scores per assay

  --use_cids     ... use CIDs instead of SIDs (all i/o)
  --resume_gdbm_file=<gdbm_file> ... resume job with existing gdbm file
  --v            ... verbose
  --vv           ... very verbose
  --h            ... this help
'''%{'PROG':PROG,'DATADIR':DATADIR}

  def ErrorExit(msg):
    print >>sys.stderr,msg
    sys.exit(1)

  indir=DATADIR;
  infile=None; verbose=0;
  out_gini_file=None;
  out_raw_file=None;
  aids=None; aidfile=None; sids=None; sidfile=None;
  use_cids=False; resume_gdbm_file=None;
  opts,pargs = getopt.getopt(sys.argv[1:],'',['h','v','vv','indir=',
  'aids=','aidfile=','infile=','out_gini=','resume_gdbm_file=',
  'out_raw=',
  'sids=','sidfile=','use_cids'])
  if not opts: ErrorExit(usage)
  for (opt,val) in opts:
    if opt=='--h': ErrorExit(usage)
    elif opt=='--indir': indir=val
    elif opt=='--infile': infile=val
    elif opt=='--out_gini': out_gini_file=val
    elif opt=='--out_raw': out_raw_file=val
    elif opt=='--aids': aids=val
    elif opt=='--aidfile': aidfile=val
    elif opt=='--sids': sids=val
    elif opt=='--sidfile': sidfile=val
    elif opt=='--use_cids': use_cids=True
    elif opt=='--resume_gdbm_file': resume_gdbm_file=val
    elif opt=='--vv': verbose=2
    elif opt=='--v': verbose=1
    else: ErrorExit('Illegal option: %s'%val)

  idtag='SID'
  if use_cids: idtag='CID'

  if not (indir or infile):
    ErrorExit('input dir or file required\n'+usage)

  aidset=[]
  if aids:
    for val in re.split('[\s,]+',aids):
      if not val.strip(): continue
      aidset.append(int(val.strip()))
  elif aidfile:
    f=open(aidfile)
    if not f:
      ErrorExit('cannot open: %s'%aidfile)
    lines=f.readlines()
    for line in lines:
      if not line.strip(): continue
      aidset.append(int(line.strip()))

  sidset={}	## use a hash for speed (could be many sids)
  if sids:
    for val in re.split('[\s,]+',sids):
      if not val.strip(): continue
      sidset[int(val.strip())]=True
  elif sidfile:
    f=open(sidfile)
    if not f:
      ErrorExit('cannot open: %s'%sidfile)
    lines=f.readlines()
    for line in lines:
      if not line.strip(): continue
      line=re.sub('\s.*$','',line)
      sidset[int(line.strip())]=True
  if len(sidset.keys())==0: sidset=None
  else:
    print >>sys.stderr, '%s: total %ss selected: %d'%(PROG,idtag,len(sidset.keys()))

  files=[]
  if infile:
    try:
      aid=int(re.sub('\.csv\.gz','',os.path.basename(infile)))
    except:
      ErrorExit('cannot parse AID: "%s"'%infile)
    files.append((infile,aid))
  else:
    aidset_foundfile=[]
    for file in os.listdir(indir):
      if not re.search('\.csv\.gz',file): continue
      try:
        aid=int(re.sub('\.csv\.gz','',file))
      except:
        print >>sys.stderr, 'cannot parse AID: "%s"'%file
        continue
      if aidset and (aid not in aidset): continue
      fpath=indir+'/'+file
      files.append((fpath,aid))
      aidset_foundfile.append(aid)
    if aidset:
      for aid in aidset:
        if aid not in aidset_foundfile:
          print >>sys.stderr, 'ERROR: no file for AID: "%d"'%aid

  fout_gini=None
  if out_gini_file:
    fout_gini=open(out_gini_file,'w')
    if not fout_gini:
      ErrorExit('cannot open: %s'%out_gini_file)
  fout_raw=None
  if out_raw_file:
    fout_raw=open(out_raw_file,'w')
    if not fout_raw:
      ErrorExit('cannot open: %s'%out_raw_file)

  if resume_gdbm_file:
    sids_db_path=resume_gdbm_file
    sids_db=gdbm.open(sids_db_path,'w')
  else:
    tempfile.tempdir=os.environ['HOME']+'/Downloads'
    fd,sids_db_path = tempfile.mkstemp('_sids_db',PROG)
    os.close(fd)
    sids_db=gdbm.open(sids_db_path,'n')
  sids_list=[]

  if fout_gini:
    fout_gini.write('SID\tn_inactive\tn_active\tn_inconclusive\tn_unspecified\tn_discrepant\tn_tested\tgini\n')

  sids_active=[]; sids_inactive=[]; sids_inconclusive=[]; sids_unspecified=[];
  sids_discrepant=[]; sids_tested=[];
  n_datapoints_total=0
  i_file=0
  for fpath,aid in files:
    i_file+=1
    print >>sys.stderr, '%d. [%d]: %s'%(i_file,aid,fpath)
    if sids_db.has_key('AID_DONE_FLAG_%d'%aid):
      continue
    f=gzip.open(fpath)
    ftxt=f.read()
    sids_this=pubchem.ftp.Utils.ExtractOutcomes(ftxt,sidset,use_cids)
    n_active=0; n_inactive=0; n_inconclusive=0; n_unspecified=0; n_discrepant=0;
    for sid in sids_this.keys():

      if not sids_db.has_key('%d'%sid):
        sids_db['%d'%sid]=''
        sids_list.append(sid)

      outcome=sids_this[sid]['outcome']

      sids_db['%d_%d'%(sid,aid)]=('%d'%outcome)
      aids_this=pubchem.ftp.Utils.Str2Ints(sids_db['%d'%(sid)])
      if aid not in aids_this:
        aids_this.append(aid)
      sids_db['%d'%(sid)]=pubchem.ftp.Utils.Ints2Str(aids_this)

      n_datapoints_total+=1
      if outcome==2: n_active+=1
      elif outcome==1: n_inactive+=1
      elif outcome==3: n_inconclusive+=1
      elif outcome==4: n_unspecified+=1
      elif outcome==5: n_discrepant+=1
      else: print >>sys.stderr, 'ERROR: outcome=%d'%(sids_this[sid]['outcome'])

    f.close()
    n_total=n_active+n_inactive+n_inconclusive+n_unspecified+n_discrepant
    n_tested=n_total-n_unspecified
    if verbose>1:
      print >>sys.stderr, '\t       active: %3d'%(n_active)
      print >>sys.stderr, '\t     inactive: %3d'%(n_inactive)
      print >>sys.stderr, '\t inconclusive: %3d'%(n_inconclusive)
      print >>sys.stderr, '\t   discrepant: %3d'%(n_discrepant)
      print >>sys.stderr, '\t(total tested: %3d)'%(n_tested)
      print >>sys.stderr, '\t  unspecified: %3d'%(n_unspecified)
      print >>sys.stderr, '\t        total: %3d'%(n_total)

    sids_db['AID_DONE_FLAG_%d'%aid]='done'	#file done; for resume


  n_ginis=0;
  for sid in sids_list:
    if fout_raw:
      fout_raw.write('%d'%(sid))
    aids_this=pubchem.ftp.Utils.Str2Ints(sids_db['%d'%(sid)])
    if not aids_this:
      pass	#?
    scores=[]
    n_total=0; n_active=0; n_inactive=0; n_inconclusive=0;
    n_unspecified=0; n_discrepant=0;
    for aid in aids_this:
      outcome=sids_db['%d_%d'%(sid,aid)]
      if outcome=='1':
        score=0.0 # 1:inactive
        n_inactive+=1
      elif outcome=='2':
        score=1.0 # 2:active
        n_active+=1
      elif outcome=='3':
        score=0.5 # 3:inconclusive
        n_inconclusive+=1
      elif outcome=='4':
        n_unspecified+=1
      elif outcome=='5':
        score=0.5 # 5:discrepant
        n_discrepant+=1
      else: continue	#error
      scores.append(score)
      if fout_raw:
        fout_raw.write(',%d:%.1f'%(aid,score))
    if fout_raw:
      fout_raw.write('\n')

    n_total=n_active+n_inactive+n_inconclusive+n_unspecified+n_discrepant
    n_tested=n_total-n_unspecified

    if not scores:
      pass	#?

    gini=gini_utils.GiniProcessor(scores)
    n_ginis+=1
    if fout_gini:
      fout_gini.write('%d\t%d\t%d\t%d\t%d\t%d\t%d\t%.2f\n'%(sid,n_inactive,n_active,n_inconclusive,n_unspecified,n_discrepant,n_tested,gini))


  if fout_gini: fout_gini.close()
  if fout_raw: fout_raw.close()

  os.unlink(sids_db_path)
  print >>sys.stderr, 'DEBUG: gdbm file: %s'%(sids_db_path)

  print >>sys.stderr, '%s: number of assay files: %d'%(PROG,len(files))
  print >>sys.stderr, '%s: total %ss: %d'%(PROG,idtag,len(sids_list))
  print >>sys.stderr, '%s: total Gini Indices: %d'%(PROG,n_ginis)
  print >>sys.stderr, '%s: total datapoints: %d'%(PROG,n_datapoints_total)

