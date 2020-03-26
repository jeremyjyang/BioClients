#!/usr/bin/env python
#############################################################################
### pubchem_assay_fetch.py - from input AIDs, fetch full dataset
#############################################################################
import os,sys,re,time,getopt,gzip,zipfile

from ... import pubchem

PROG=os.path.basename(sys.argv[0])

ASSAY_DATA_DIR='/home/data/pubchem/bioassay/csv/data'

#############################################################################
def ErrorExit(msg):
  print >>sys.stderr,msg
  sys.exit(1)

#############################################################################
def MergeListIntoHash(hsh,lst):
  for x in lst:
    if not hsh.has_key(x):
      hsh[x]=1
    else:
      hsh[x]+=1
  return

#############################################################################
def ExtractSIDs(fpath_csv_gz):
  try:
    f=gzip.open(fpath_csv_gz)
  except:
    print >>sys.stderr, 'ERROR: could not open %s'%(fpath)
    return []
  ftxt=f.read()
  f.close()
  sids_this=pubchem.ftp.Utils.ExtractOutcomes(ftxt,None,False)
  return sids_this

#############################################################################
if __name__=='__main__':
  usage='''
  %(PROG)s - fetch assay csvs from AIDs (from local mirror)

  required:
  --i AIDFILE .......... AIDs (CSV w/ AID 1st ok)
  or
  --aids AIDS .......... list of AIDs (comma separated)
  and
  --odir ODIR .......... dir for output files

  options:
  --o OFILE ............ SIDs extracted from assay CSVs
  --keep_dirtree ....... output in directory tree (as in PubChem FTP)
  --v .................. verbose
  --h .................. this help
'''%{'PROG':PROG}
  ifile=None; odir=None; verbose=0; ofile=None; aidslist=None; keep_dirtree=False;
  opts,pargs = getopt.getopt(sys.argv[1:],'',['h','v','vv','odir=','i=','o=','aids=','keep_dirtree'])
  if not opts: ErrorExit(usage)
  for (opt,val) in opts:
    if opt=='--h': ErrorExit(usage)
    elif opt=='--i': ifile=val
    elif opt=='--odir': odir=val
    elif opt=='--out_sids': ofile=val
    elif opt=='--aids': aidslist=val
    elif opt=='--keep_dirtree': keep_dirtree=True
    elif opt=='--vv': verbose=2
    elif opt=='--v': verbose=1
    else: ErrorExit('Illegal option: %s'%val)

  if not odir:
    ErrorExit('-odir required\n'+usage)

  if not os.access(ASSAY_DATA_DIR,os.R_OK):
    ErrorExit('cannot find: %s'%ASSAY_DATA_DIR)

  aids=[];
  if aidslist:
    aids=map(lambda x:int(x),(re.split(r'[\s,]',aidslist.strip())))
  elif ifile:
    faids=file(ifile)
    if not faids:
      ErrorExit('cannot open: %s\n%s'%(ifile,usage))
    i=0;
    while True:
      line=faids.readline()
      if not line: break
      line=line.strip()
      if not line: continue
      i+=1
      try:
        field=re.sub('[,\s].*$','',line)   ## may be addl field[s]
        aid=int(field)
        aids.append(aid)
      except:
        print >>sys.stderr,'cannot parse aid: "%s"'%line
        continue
    print >>sys.stderr,'aids read: %d'%len(aids)
  else:
    ErrorExit('-in or -aids required\n'+usage)

  aids.sort()

  sids={}

  t0=time.time()
  n_out=0; n_not_found=0;
  for aid in aids:
    if verbose:
      print >>sys.stderr, '%d:\t'%(aid),
    is_found=False
    for fname_zip in os.listdir(ASSAY_DATA_DIR):
      if not re.search('\.zip',fname_zip): continue
      aid_from=re.sub(r'^([\d]+)_([\d]+)\.zip$',r'\1',fname_zip)
      aid_to=re.sub(r'^([\d]+)_([\d]+)\.zip$',r'\2',fname_zip)
      try:
        aid_from=int(aid_from)
        aid_to=int(aid_to)
      except:
        print >>sys.stderr, 'ERROR: cannot parse AIDs from fname_zip: "%s"'%fname_zip
        continue
      if aid<aid_from or aid>aid_to:
        continue
      if verbose:
        print >>sys.stderr, '(%s)'%(fname_zip),
      fpath_zip=ASSAY_DATA_DIR+'/'+fname_zip
      try:
        zf=zipfile.ZipFile(fpath_zip,'r')
      except:
        print >>sys.stderr, 'ERROR: cannot read fpath_zip: "%s"'%fpath_zip
        continue
      flist_csv_gz=zf.namelist()
      zf.close()
      for fpath_csv_gz in flist_csv_gz:
        aid_this=None
        if not re.search('\.csv\.gz',fpath_csv_gz): continue
        try:
          if re.search(r'/',fpath_csv_gz):
            txt=re.sub(r'^.*/(\d*)\.csv\.gz',r'\1',fpath_csv_gz)
          else:
            txt=re.sub(r'\.csv\.gz','',fpath_csv_gz)
          aid_this=int(txt)
        except:
          print >>sys.stderr, 'cannot parse AID: "%s"'%fpath_csv_gz
          continue
        if aid==aid_this:
          zf=zipfile.ZipFile(fpath_zip,'r')
          cwd=os.getcwd()
          os.chdir(odir)
          zf.extract(fpath_csv_gz)
          if not keep_dirtree:
            d,f = os.path.split(fpath_csv_gz)
            os.rename(fpath_csv_gz,f)
          n_out+=1
          is_found=True
          os.chdir(cwd)
          zf.close()
          if ofile:
            MergeListIntoHash(sids,ExtractSIDs(odir+"/"+fpath_csv_gz))
          break
    if not is_found:
      n_not_found+=1
    if verbose:
      print >>sys.stderr, '\t[%s]'%(is_found)

  if ofile:
    fout_sids=open(ofile,"w+")
    if not fout_sids:
      print >>sys.stderr, 'cannot open: %s'%ofile
    else:
      for sid in sids.keys():
        fout_sids.write("%d\n"%sid)
      fout_sids.close()

  print >>sys.stderr, '%s: input AIDs: %d'%(PROG,len(aids))
  print >>sys.stderr, '%s: output assay csv datafiles: %d'%(PROG,n_out)
  print >>sys.stderr, '%s: assays not found: %d'%(PROG,n_not_found)
  if ofile:
    print >>sys.stderr, '%s: output SIDs: %d'%(PROG,len(sids.keys()))
  print >>sys.stderr, ('%s: total elapsed time: %s'%(PROG,time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))))
