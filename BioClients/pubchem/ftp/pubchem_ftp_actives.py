#!/usr/bin/env python
#############################################################################
### pubchem_actives.py - extract SIDs from PubChem CSV assay file[s]
### activity outcomes: 
###   1 = inactive
###   2 = active
###   3 = inconclusive
###   4 = unspecified
###   multiple, differing 1, 2 or 3 = discrepant
###   not 4 = tested
###
### If a single assay is under consideration, compounds are separated into
### all five defined categories.
###
### If multiple assays are under consideration, a compound active in ANY
### assay is considered active by this program, and all other compounds
### are considered inactive.
#############################################################################
###  WARNING: This program is a RAM HOG!  3GB when used for ~900 assays
###  and ~400k SIDs.
#############################################################################
###  July 2010: The format of the downloaded csv files has changed.  Today
###  I count 189947 .csv.gz files in bioassay/csv/data/ subdirs.
###  Running the program with
### entrez_assay_search.pl \
###         -v \
###         -mlpcn \
###         -out_aids data/pubchem_mlpcn.aid
#### (1998 assays)
### pubchem_actives.py \
###         --aidfile data/pubchem_mlpcn.aid \
###         --out_all data/pubchem_mlpcn.cid  
### 
### still working after >1week.
#############################################################################
###  to do:
###    [x] use tmp db (dbm? gdbm?) instead of huge Python containers.
###        dbm seems to have some problems.
###        REPLACED sids hash with sids_db database.
###        Use sids_list for iteration.
###        Don't use /tmp due to size (5+GB).
###
###    [x] allow jobs to be resumed using gdbm file
###    [ ] output compound ids with activity stats on one line
###    [ ] fix  --out_all_stats
#############################################################################
import os,sys,re,getopt,gzip,tempfile
try:
  import gdbm
except:
  import dbm as gdbm
from ... import pubchem

PROG=os.path.basename(sys.argv[0])
DATADIR="/home/data/pubchem/bioassay/csv/data"

#############################################################################
if __name__=='__main__':
  usage='''
  %(PROG)s - extract SIDs from assay CSV files

  options:
  --indir=<DIR>   ... dir w/ csv.gz assay data [%(DATADIR)s]
  or
  --infile=<FILE>   ... input csv.gz assay data

  --aids=<AIDS> ... list of AIDs to select within --indir dir
  --aidfile=<AIDFILE> ... AIDs to select within --indir dir
  --sidfile=<SIDFILE> ... SIDs to select (ignore others)

  --out_active=<outfile> ... active SIDs
  --out_inactive=<outfile> ... inactive SIDs
  --out_all=<outfile> ... all SIDs

  --out_all_stats=<outfile> ... all SIDs, w/ inac,act,incon,unsp

  only valid for single assay:
  --out_inconclusive=<outfile> ... output file of inconclusive SIDs
  --out_unspecified=<outfile> ... output file of unspecified SIDs
  --out_tested=<outfile> ... output file of not unspecified SIDs
  --out_discrepant=<outfile> ... output file of discrepant SIDs

  --inc_aids     ... append <tab>N_AIDS<tab>AIDs to SIDs
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
  out_active_file=None; out_inactive_file=None;
  out_inconclusive_file=None; out_unspecified_file=None;
  out_tested_file=None; out_discrepant_file=None; out_all_file=None;
  out_all_stats_file=None;
  inc_aids=False; aids=None; aidfile=None; sidfile=None;
  use_cids=False; resume_gdbm_file=None;
  opts,pargs = getopt.getopt(sys.argv[1:],'',['h','v','vv','indir=',
  'aids=','aidfile=','infile=','inc_aids',
  'out_active=','out_inactive=',
  'out_inconclusive=','out_unspecified=','out_tested=',
  'out_discrepant=','out_all=','out_all_stats=','resume_gdbm_file=',
  'sidfile=','use_cids'])
  if not opts: ErrorExit(usage)
  for (opt,val) in opts:
    if opt=='--h': ErrorExit(usage)
    elif opt=='--indir': indir=val
    elif opt=='--infile': infile=val
    elif opt=='--out_active': out_active_file=val
    elif opt=='--out_inactive': out_inactive_file=val
    elif opt=='--out_inconclusive': out_inconclusive_file=val
    elif opt=='--out_unspecified': out_unspecified_file=val
    elif opt=='--out_discrepant': out_discrepant_file=val
    elif opt=='--out_tested': out_tested_file=val
    elif opt=='--out_all': out_all_file=val
    elif opt=='--out_all_stats': out_all_stats_file=val
    elif opt=='--inc_aids': inc_aids=True
    elif opt=='--aids': aids=val
    elif opt=='--aidfile': aidfile=val
    elif opt=='--sidfile': sidfile=val
    elif opt=='--use_cids': use_cids=True
    elif opt=='--resume_gdbm_file': resume_gdbm_file=val
    elif opt=='--vv': verbose=2
    elif opt=='--v': verbose=1
    else: ErrorExit('Illegal option: %s'%val)

  if not (indir or infile):
    ErrorExit('input dir or file required\n'+usage)

  fout_active=None
  if out_active_file:
    fout_active=open(out_active_file,'w')
    if not fout_active:
      ErrorExit('cannot open: %s'%out_active_file)
  fout_inactive=None
  if out_inactive_file:
    fout_inactive=open(out_inactive_file,'w')
    if not fout_inactive:
      ErrorExit('cannot open: %s'%out_inactive_file)

  aidset=[]
  if aids:
    for val in re.split('[\s,]+',aids):
      if not val.strip(): continue
      aidset.append(int(val.strip()))
  if aidfile:
    f=open(aidfile)
    if not f:
      ErrorExit('cannot open: %s'%aidfile)
    lines=f.readlines()
    for line in lines:
      if not line.strip(): continue
      aidset.append(int(line.strip()))
  sidset={}	## use a hash for speed (could be many sids)
  if sidfile:
    f=open(sidfile)
    if not f:
      ErrorExit('cannot open: %s'%sidfile)
    lines=f.readlines()
    for line in lines:
      if not line.strip(): continue
      line=re.sub('\s.*$','',line)
      sidset[int(line.strip())]=True
  if len(sidset.keys())==0: sidset=None

  files=[]
  if infile:
    try:
      aid=int(re.sub('\.csv\.gz','',os.path.basename(infile)))
    except:
      ErrorExit('cannot parse AID: "%s"'%infile)
    files.append((infile,aid))
  else:
    for root,dirs,fs in os.walk(indir):
      for dir in dirs:
        for f in os.listdir(os.path.join(root,dir)):
          if not re.search('\.csv\.gz',f): continue
          try:
            aid=int(re.sub('\.csv\.gz','',f))
          except:
            print >>sys.stderr, 'cannot parse AID: "%s"'%f
            continue
          if aidset and (aid not in aidset): continue
          fpath=os.path.join(root,dir,f)
          files.append((fpath,aid))

  if aidset:
    print >>sys.stderr, ('%d / %d files found (%.1f%%)'%
	(len(files),len(aidset),(100.0*len(files)/len(aidset))))

  for fpath,aid in files: #DEBUG
    print >>sys.stderr, aid, fpath #DEBUG
  sys.exit() #DEBUG

  if len(files)>1 and (out_inconclusive_file or out_unspecified_file or out_discrepant_file or out_tested_file):
    ErrorExit('--out_inconclusive/out_unspecified/out_discrepant/out_tested only valid for single assay.')
  fout_inconclusive=None
  if out_inconclusive_file:
    fout_inconclusive=open(out_inconclusive_file,'w')
    if not fout_inconclusive:
      ErrorExit('cannot open: %s'%out_inconclusive_file)
  fout_unspecified=None
  if out_unspecified_file:
    fout_unspecified=open(out_unspecified_file,'w')
    if not fout_unspecified:
      ErrorExit('cannot open: %s'%out_unspecified_file)
  fout_discrepant=None
  if out_discrepant_file:
    fout_discrepant=open(out_discrepant_file,'w')
    if not fout_discrepant:
      ErrorExit('cannot open: %s'%out_discrepant_file)
  fout_tested=None
  if out_tested_file:
    fout_tested=open(out_tested_file,'w')
    if not fout_tested:
      ErrorExit('cannot open: %s'%out_tested_file)
  fout_all=None
  if out_all_file:
    fout_all=open(out_all_file,'w')
    if not fout_all:
      ErrorExit('cannot open: %s'%out_all_file)
  fout_all_stats=None
  if out_all_stats_file:
    fout_all_stats=open(out_all_stats_file,'w')
    if not fout_all_stats:
      ErrorExit('cannot open: %s'%out_all_stats_file)

  if resume_gdbm_file:
    sids_db_path=resume_gdbm_file
    sids_db=gdbm.open(sids_db_path,'w')
  else:
    tempfile.tempdir=os.environ['HOME']+'/Downloads'
    fd,sids_db_path = tempfile.mkstemp('_sids_db',PROG)
    os.close(fd)
    sids_db=gdbm.open(sids_db_path,'n')
  sids_list=[]

  sids_active=[]; sids_inactive=[]; sids_inconclusive=[]; sids_unspecified=[];
  sids_discrepant=[]; sids_tested=[];
  n_datapoints_total=0
  i_file=0
  for fpath,aid in files:
    i_file+=1
    print >>sys.stderr, '%d. [%d]: %s'%(i_file,aid,fpath)
    if sids_db.has_key('AID_DONE_FLAG_%d'%aid):
      continue
    try:
      f=gzip.open(fpath)
    except:
      print >>sys.stderr, 'ERROR: could not open %s'%(fpath)
      continue
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
    if verbose>1:
      print >>sys.stderr, '\t      active: %3d'%(n_active)
      print >>sys.stderr, '\t    inactive: %3d'%(n_inactive)
      print >>sys.stderr, '\tinconclusive: %3d'%(n_inconclusive)
      print >>sys.stderr, '\t unspecified: %3d'%(n_unspecified)
      print >>sys.stderr, '\t  discrepant: %3d'%(n_discrepant)
      print >>sys.stderr, '\t       total: %3d'%(len(sids_this.keys()))

    sids_db['AID_DONE_FLAG_%d'%aid]='done'	#file done; for resume

  for sid in sids_list:
    sid_is_active=False

    for aid in pubchem.ftp.Utils.Str2Ints(sids_db['%d'%(sid)]):
      if sids_db['%d_%d'%(sid,aid)]=='2':
        sids_active.append(sid)
        sid_is_active=True
        break

    if not sid_is_active:
      if len(files)==1:
        if sids_this[sid]['outcome']==1:
          sids_inactive.append(sid)
        elif sids_this[sid]['outcome']==3:
          sids_inconclusive.append(sid)
        elif sids_this[sid]['outcome']==4:
          sids_unspecified.append(sid)
        elif sids_this[sid]['outcome']==5:
          sids_discrepant.append(sid)
      else:
        sids_inactive.append(sid)

  if fout_active:
    f=fout_active
    if verbose:
      print >>sys.stderr, 'sorting %d active SIDs...'%(len(sids_active))
    sids_active.sort()
    for sid in sids_active:
      f.write('%d'%sid)
      if inc_aids:
        aids=[]

        for aid in pubchem.ftp.Utils.Str2Ints(sids_db['%d'%(sid)]):
          if sids_db['%d_%d'%(sid,aid)]=='2': aids.append(aid)

        f.write('\t%d\t%s'%(len(aids),pubchem.ftp.Utils.Ints2Str(aids)))
      f.write('\n')
    f.close()

  if fout_inactive:
    f=fout_inactive
    if verbose:
      print >>sys.stderr, 'sorting %d inactive SIDs...'%(len(sids_inactive))
    sids_inactive.sort()
    for sid in sids_inactive:
      f.write('%d'%sid)
      if inc_aids:
        aids=[]

        for aid in pubchem.ftp.Utils.Str2Ints(sids_db['%d'%(sid)]):
          if sids_db['%d_%d'%(sid,aid)]=='1': aids.append(aid)

        f.write('\t%d\t%s'%(len(aids),pubchem.ftp.Utils.Ints2Str(aids)))
      f.write('\n')
    f.close()

  if fout_inconclusive:
    f=fout_inconclusive
    if verbose:
      print >>sys.stderr, 'sorting %d inconclusive SIDs...'%(len(sids_inconclusive))
    sids_inconclusive.sort()
    for sid in sids_inconclusive:
      f.write('%d'%sid)
      f.write('\n')
    f.close()

  if fout_unspecified:
    f=fout_unspecified
    if verbose:
      print >>sys.stderr, 'sorting %d unspecified SIDs...'%(len(sids_unspecified))
    sids_unspecified.sort()
    for sid in sids_unspecified:
      f.write('%d'%sid)
      f.write('\n')
    f.close()

  if fout_discrepant:
    f=fout_discrepant
    if verbose:
      print >>sys.stderr, 'sorting %d discrepant SIDs...'%(len(sids_discrepant))
    sids_discrepant.sort()
    for sid in sids_discrepant:
      f.write('%d'%sid)
      f.write('\n')
    f.close()

  if fout_tested:
    f=fout_tested
    if verbose:
      print >>sys.stderr, 'sorting %d tested SIDs...'%(len(sids_tested))
    sids_tested=sids_active+sids_inactive+sids_inconclusive+sids_discrepant
    sids_tested.sort()
    for sid in sids_tested:
      f.write('%d'%sid)
      f.write('\n')
    f.close()

  if fout_all:
    f=fout_all
    sids_all=sids_active+sids_inactive+sids_inconclusive+sids_unspecified+sids_discrepant
    if verbose:
      print >>sys.stderr, 'sorting %d all SIDs...'%(len(sids_all))
    sids_all.sort()
    for sid in sids_all:
      f.write('%d'%sid)
      if inc_aids:

        aids=pubchem.ftp.Utils.Str2Ints(sids_db['%d'%(sid)])

        f.write('\t%d\t%s'%(len(aids),pubchem.ftp.Utils.Ints2Str(aids)))
      f.write('\n')
    f.close()

  if fout_all_stats:
    f=fout_all_stats
    sids_all=sids_active+sids_inactive+sids_inconclusive+sids_unspecified+sids_discrepant
    if verbose:
      print >>sys.stderr, 'sorting %d all SIDs...'%(len(sids_all))
    sids_all.sort()
    f.write('id,n_inactive,n_active,n_inconclusive,n_unspecified\n')
    for sid in sids_all:
      nact,nina,ninc,nuns = 0,0,0,0
      for aid in pubchem.ftp.Utils.Str2Ints(sids_db['%d'%(sid)]):
        if sids_db['%d_%d'%(sid,aid)]=='1': nina+=1
        elif sids_db['%d_%d'%(sid,aid)]=='2': nact+=1
        elif sids_db['%d_%d'%(sid,aid)]=='3': ninc+=1
        elif sids_db['%d_%d'%(sid,aid)]=='4': nuns+=1
      f.write('%d,%d,%d,%d,%d\n'%(sid,nina,nact,ninc,nuns))
    f.close()

  os.unlink(sids_db_path)
  print >>sys.stderr, 'DEBUG: gdbm file: %s'%(sids_db_path)

  id='SID'
  if use_cids: id='CID'
  print >>sys.stderr, '%s: number of assay files: %d'%(PROG,len(files))
  print >>sys.stderr, '%s: active %ss: %d'%(PROG,id,len(sids_active))
  print >>sys.stderr, '%s: inactive %ss: %d'%(PROG,id,len(sids_inactive))
  if len(files)==1:
    print >>sys.stderr, '%s: inconclusive %ss: %d'%(PROG,id,len(sids_inconclusive))
    print >>sys.stderr, '%s: unspecified %ss: %d'%(PROG,id,len(sids_unspecified))
    print >>sys.stderr, '%s: discrepant %ss: %d'%(PROG,id,len(sids_discrepant))
    print >>sys.stderr, '%s: total %ss: %d'%(PROG,id,len(sids_active)+len(sids_inactive)+len(sids_inconclusive)+len(sids_unspecified)+len(sids_discrepant))
  else:
    print >>sys.stderr, '%s: total %ss: %d'%(PROG,id,len(sids_active)+len(sids_inactive))
  print >>sys.stderr, '%s: total datapoints: %d'%(PROG,n_datapoints_total)

