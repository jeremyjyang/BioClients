#!/usr/bin/env python
#############################################################################
### pubchem_ftp_assay_results.py - input AID, SIDs, output CSV outcomes.
#############################################################################
import os,sys,re,time,getopt,gzip,zipfile,tempfile,shutil

from ... import pubchem

PROG=os.path.basename(sys.argv[0])

DATADIR='/home/data/pubchem/bioassay/csv/data'

#############################################################################
if __name__=='__main__':
  def ErrorExit(msg):
    print >>sys.stderr,msg
    sys.exit(1)

  usage='''
  %(PROG)s - assay csvs from AIDs (from local mirror)

  required:
  --aid AID ............ AID
  and
  --i SIDFILE .......... SID file
  or
  --sids SIDS .......... SIDs, comma-separated

  options:
  --o OFILE ............ assay results CSV
  --datadir DATADIR .... [%(DATADIR)s]
  --v .................. verbose
  --h .................. this help
'''%{'PROG':PROG,
	'DATADIR':DATADIR
	}
  ifile=None;
  aid=None;
  verbose=0;
  ofile=None;
  opts,pargs = getopt.getopt(sys.argv[1:],'',['h','v','vv','i=','o=',
	'aid=','sids='])
  if not opts: ErrorExit(usage)
  for (opt,val) in opts:
    if opt=='--h': ErrorExit(usage)
    elif opt=='--i': ifile=val
    elif opt=='--o': ofile=val
    elif opt=='--aid': aid=int(val)
    elif opt=='--sids': sids=set(map(lambda x:int(x),(re.split(r'[\s,]',val.strip()))))
    elif opt=='--vv': verbose=2
    elif opt=='--v': verbose=1
    else: ErrorExit('Illegal option: %s'%val)

  if not os.access(DATADIR,os.R_OK):
    ErrorExit('cannot find: %s'%DATADIR)

  if ifile:
    sids=set()
    fsids=file(ifile)
    if not fsids:
      ErrorExit('cannot open: %s\n%s'%(ifile,usage))
    i=0;
    while True:
      line=fsids.readline()
      if not line: break
      line=line.strip()
      if not line: continue
      i+=1
      try:
        field=re.sub('[,\s].*$','',line)   ## may be addl field[s]
        sid=int(field)
        sids.add(sid)
      except:
        print >>sys.stderr,'cannot parse sid: "%s"'%line
        continue
    print >>sys.stderr,'sids read: %d'%len(sids)
  elif not sids:
    ErrorExit('-i or -sids required\n'+usage)

  if ofile:
    fout=open(ofile,"w+")
  else:
    fout=sys.stdout

  t0=time.time()

  tmpdir=tempfile.mkdtemp(prefix='pubchem_ftp',suffix='')

  n_out=0; n_not_found=0;

  if verbose:
    print >>sys.stderr, '%d:'%(aid),
  is_found=False
  for fname_zip in os.listdir(DATADIR):
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
      print >>sys.stderr, '(%s)'%(fname_zip)
    fpath_zip=DATADIR+'/'+fname_zip
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
        os.chdir(tmpdir)
        zf.extract(fpath_csv_gz)
        n_out+=1
        is_found=True
        os.chdir(cwd)
        zf.close()
        fpath=(tmpdir+"/"+fpath_csv_gz)
        #print >>sys.stderr, 'DEBUG: %s'%(fpath)
        try:
          fin=gzip.open(fpath)
        except:
          print >>sys.stderr, 'ERROR: could not open %s'%(fpath)
        pubchem.ftp.Utils.ExtractResults(fin,aid,sids,fout,verbose)
        fin.close()
        break
    if verbose and not is_found:
      print >>sys.stderr, ''

  fout.close()

  shutil.rmtree(tmpdir)

