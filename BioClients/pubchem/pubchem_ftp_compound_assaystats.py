#!/usr/bin/env python
#############################################################################
### pubchem_compound_assaystats.py - From PubChem CSV assay files, determine
### compound activity stats.
### activity outcomes: 
###   1 = inactive
###   2 = active
###   3 = inconclusive
###   4 = unspecified
###   multiple, differing 1, 2 or 3 = discrepant
###   not 4 = tested
###
#############################################################################
### This program is a memory hog (700MB for 380k mols).  Use with care.
#############################################################################
###     aTested - how many assays where that cpd has been tested
###     aActive - how many assays where that cpd has been tested active
###     sTested - how many samples with that cpd have been tested
###     sActive - how many samples with that cpd have been tested active
#############################################################################
### Jeremy Yang
###  5 Jul 2012
#############################################################################
import os,sys,re,getopt,gzip,zipfile

import hier_scaffolds_assaystats  ## for ExtractOutcomes()

#############################################################################
def main():
  global PROG,SCRATCHDIR
  PROG=os.path.basename(sys.argv[0])
  SCRATCHDIR=os.getcwd()+'/data/scratch'

  usage='''
  %(PROG)s - 

  required:
  --inmols=<INMOLS> ... mols w/ cids (smiles)
  --csvdir=<DIR>   ... dir containing input csv.gz assay data
  --zipdir=<DIR>   ... dir containing zipfiles containing input csv.gz assay data
  --csvfile=<FILE>   ... input csv.gz assay data
  --o=<OUTSCAFS> ... output mols with data (smiles)

  options:
  --aids=<AIDS> ... list of AIDs to select within --csvdir dir
  --aidfile=<AIDFILE> ... file of AIDs to select within --csvdir dir
  --cidfile=<CIDFILE> ... file of CIDs to select (ignore others)

  --use_sids     ... use SIDs instead of CIDs (all i/o)
  --n_max_aids=<N> ... mostly for debugging
  --v            ... verbose
  --vv           ... very verbose
  --h            ... this help
'''%{'PROG':PROG}

  def ErrorExit(msg):
    print >>sys.stderr,msg
    sys.exit(1)

  #csvdir="/home/data/pubchem/bioassay/csv/data";
  csvdir=None
  zipdir="/home/data/pubchem/bioassay/csv/data";
  csvfile=None; verbose=0;
  ofile=None; inmolsfile=None;
  aids=None; aidfile=None; cidfile=None;
  use_sids=False;
  n_max_aids=None;
  opts,pargs = getopt.getopt(sys.argv[1:],'',['h','v','vv','csvdir=','zipdir=',
  'aids=','aidfile=','csvfile=','o=','inmols=','n_max_aids=',
  'cidfile=','use_sids'])
  if not opts: ErrorExit(usage)
  for (opt,val) in opts:
    if opt=='--h': ErrorExit(usage)
    elif opt=='--inmols': inmolsfile=val
    elif opt=='--o': ofile=val
    elif opt=='--csvdir': csvdir=val
    elif opt=='--zipdir': zipdir=val
    elif opt=='--csvfile': csvfile=val
    elif opt=='--aids': aids=val
    elif opt=='--aidfile': aidfile=val
    elif opt=='--cidfile': cidfile=val
    elif opt=='--use_sids': use_sids=True
    elif opt=='--n_max_aids': n_max_aids=int(val)
    elif opt=='--vv': verbose=2
    elif opt=='--v': verbose=1
    else: ErrorExit('Illegal option: %s'%val)

  if not (csvdir or zipdir or csvfile):
    ErrorExit('csvdir or zipdir or file required\n'+usage)
  if not ofile:
    ErrorExit('output file required\n'+usage)
  if not (inmolsfile):
    ErrorExit('--inmols file required\n'+usage)

  finmols=file(inmolsfile)
  if not finmols: ErrorExit('cannot open: %s'%inmolsfile)
  fout=file(ofile,'w')
  if not fout: ErrorExit('cannot open: %s'%ofile)

  aidset=[]
  if aids:
    for val in re.split('[\s,]+',aids):
      if not val.strip(): continue
      aidset.append(int(val.strip()))
  if aidfile:
    f=file(aidfile)
    if not f:
      ErrorExit('cannot open: %s'%aidfile)
    lines=f.readlines()
    for line in lines:
      if not line.strip(): continue
      aidset.append(int(line.strip()))
  cidset={}	## use a hash for speed (could be many cids)
  if cidfile:
    f=file(cidfile)
    if not f:
      ErrorExit('cannot open: %s'%cidfile)
    lines=f.readlines()
    for line in lines:
      if not line.strip(): continue
      line=re.sub('\s.*$','',line)
      cidset[int(line.strip())]=True
  if len(cidset.keys())==0: cidset=None

  files=[]
  if csvdir:
    for fname_csv_gz in os.listdir(csvdir):
      if not re.search('\.csv\.gz',fname_csv_gz): continue
      try:
        aid=int(re.sub('\.csv\.gz','',fname_csv_gz))
      except:
        print >>sys.stderr, 'cannot parse AID: "%s"'%fname_csv_gz
        continue
      if aidset and (aid not in aidset): continue
      fpath_csv_gz=csvdir+'/'+fname_csv_gz
      files.append((fpath_csv_gz,aid))
  elif zipdir:
    for fname_zip in os.listdir(zipdir):
      if not re.search('\.zip',fname_zip): continue
      fpath_zip=zipdir+'/'+fname_zip
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
        if aidset and (aid not in aidset): continue
        files.append((fpath_zip,fpath_csv_gz,aid))
  else:
    try:
      aid=int(re.sub('\.csv\.gz','',os.path.basename(csvfile)))
    except:
      ErrorExit('cannot parse AID: "%s"'%csvfile)
    files.append((csvfile,aid))

  n_mols=0; cidlist=[]; cid2smi={}; 
  while True:
    line=finmols.readline()
    if not line: break
    n_mols+=1
    line=line.rstrip()
    fields=line.split()
    if len(fields)<3:
      print >>sys.stderr, 'Aaak! bad line:', line
      continue
    smiles=fields[0]
    cid=int(fields[1])
    cidlist.append(cid)
    cid2smi[cid]=smiles

  print >>sys.stderr, 'mols read: %d'%(n_mols,)

  if not (os.path.isdir(SCRATCHDIR) and os.access(SCRATCHDIR,os.W_OK)):
    try:
      os.mkdir(SCRATCHDIR)
    except:
      ErrorExit('SCRATCHDIR does not exist or is not writeable, and cannot be created: "%s"'%SCRATCHDIR)

  ### Read all [selected] assay csv files.  For each cid, create map of 
  ### aids and outcomes.
  ### (Non-active may be inactive, discrepant, etc.).
  ### Problem: if using sid, may be duplicates in a single assay, that is 
  ### multiple samples for one sid.
  cids={}; cids_active=[]; 
  for i_file,f in enumerate(files):
    if csvdir:
      fpath_csv,aid = f
      f_csv=gzip.open(fpath_csv)
    elif zipdir:
      fpath_zip,fpath_csv_gz,aid = f
      zf=zipfile.ZipFile(fpath_zip,'r')
      cwd=os.getcwd()
      os.chdir(SCRATCHDIR)
      zf.extract(fpath_csv_gz)
      os.chdir(cwd)
      zf.close()
      del zf #maybe free memory?
      f_csv=gzip.open(SCRATCHDIR+'/'+fpath_csv_gz)

    ftxt=f_csv.read()
    f_csv.close()
    del f_csv #maybe free memory?
    cids_this=hier_scaffolds_assaystats.ExtractOutcomes(ftxt,cidset,use_sids)
    del ftxt #maybe free memory?
    n_active=0;
    for cid in cids_this.keys():
      if not cid2smi.has_key(cid): continue
      if not cids.has_key(cid): cids[cid]={}
      cids[cid][aid]=cids_this[cid]['outcome']
      if cids[cid][aid]==2: n_active+=1
    if verbose:
      sys.stderr.write('%3d. AID %4d: '%(i_file,aid))
      sys.stderr.write('active/total: %6d /%6d\n'%(n_active,len(cids_this.keys())))
      if not i_file%10:
        sys.stderr.write('done %3d / %3d (%.1f%%)'%(i_file,len(files),100.0*i_file/len(files)))
    del cids_this #maybe free memory?

    os.unlink(SCRATCHDIR+'/'+fpath_csv_gz)


    if n_max_aids and i_file==n_max_aids:
      print >>sys.stderr, 'n_max_aids limit reached: %d'%n_max_aids
      break

  print >>sys.stderr, 'assay files read: %d'%i_file

  n_cid_notfound=0
  fout.write("#smiles cid aTested aActive sTested sActive\n")
  ### For each cid, generate stats.
  for cid in cidlist:
    aids_tested=[]; aids_active=[];
    n_samples=0; n_samples_active=0;
    smiles=cid2smi[cid]

    if not cids.has_key(cid):
      print >>sys.stderr, 'NOTE: cannot find cid %d in any assay.'%(cid)
      n_cid_notfound+=1
      continue

    for aid in cids[cid].keys():
      if aid not in aids_tested: aids_tested.append(aid)
      n_samples+=1
      if cids[cid][aid]==2:	#outcome
        n_samples_active+=1
        if aid not in aids_active: aids_active.append(aid)

    fout.write("%s %d %d %d %d %d\n"%(
	smiles,
	cid,
	len(aids_tested),
	len(aids_active),
	n_samples,
	n_samples_active))
    if verbose>1:
      sys.stderr.write(
	"cid=%d,aTested=%d,aActive=%d,sTested=%d,sActive%d\n"%(
	cid,
	len(aids_tested),
	len(aids_active),
	n_samples,
	n_samples_active))

  fout.close()

  id='CID'
  if use_sids: id='SID'
  print >>sys.stderr, '%s: number of assay files: %d'%(PROG,len(files))
  print >>sys.stderr, '%s: total %ss: %d'%(PROG,id,len(cids.keys()))
  print >>sys.stderr, '%s: number of %ss: %d'%(PROG,id,len(cidlist))
  print >>sys.stderr, '%s: number of %ss not found in any assay: %d'%(PROG,id,n_cid_notfound)

#############################################################################
if __name__=='__main__':
  #import cProfile
  #cProfile.run('main()')
  main()

