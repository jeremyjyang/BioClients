#!/usr/bin/env python
'''
Search for text in assay descriptions (XML)

Jeremy J Yang
22 Oct 2014
'''
import os,sys,re,time,getopt,gzip,zipfile
import xml.dom.minidom

from ..util import xml_utils

PROG=os.path.basename(sys.argv[0])

#ASSAY_DESC_DIR='/home/data/pubchem/bioassay/xml/description'
ASSAY_DESC_DIR='/home/data/pubchem/bioassay/csv/description'

SCRATCHDIR='/tmp/'+PROG+'_SCRATCHDIR'

#############################################################################
def ParseAssayXml(assayxml):
  aname,ameth,adesc,atargs=None,None,None,None
  dom=xml.dom.minidom.parseString(assayxml)
  tag='PC-AssayDescription_name'
  anames=xml_utils.DOM_GetLeafValsByTagName(dom,tag)
  if anames: aname=anames[0]
  tag='PC-AssayDescription_activity-outcome-method'
  ameths=xml_utils.DOM_GetAttr(dom,tag,'value')
  if ameths: ameth=ameths[0]
  tag='PC-AssayDescription_description_E'
  adescs=xml_utils.DOM_GetLeafValsByTagName(dom,tag)
  if adescs: adesc=('\n'.join(adescs))

  tag='PC-AssayTargetInfo_name'
  atargs_names=xml_utils.DOM_GetLeafValsByTagName(dom,tag)
  tag='PC-AssayTargetInfo_molecule-type'
  atargs_types=xml_utils.DOM_GetAttr(dom,tag,'value')
  tag='PC-AssayTargetInfo_mol-id'
  atargs_ids=xml_utils.DOM_GetLeafValsByTagName(dom,tag)
  gids=[]
  if atargs_names:
    atargs=''
    for i,atargs_name in enumerate(atargs_names):
      if i>0: atargs+=';  '
      atargs+=('%d. %s'%(i+1,atargs_name))
      if len(atargs_ids)>i and len(atargs_types)>i:
        atargs+=(' [%s:%s]'%(atargs_types[i],atargs_ids[i]))
      if atargs_types[i]=='protein':
        gids.append(int(atargs_ids[i]))

  return aname,ameth,adesc,atargs,gids

#############################################################################
def ErrorExit(msg):
  print >>sys.stderr,msg
  sys.exit(1)

#############################################################################
if __name__=='__main__':
  usage='''
  %(PROG)s - search assay names and descriptions

  required:
  --string=<STRING>   ... search substring
  or
  --regexp=<REGEXP>   ... search regular expression
  or
  --out_all_aid_file=<out_all_aid_file> ... csv file: aid,name,method,target[s]

  options:
  --desc           ... search descriptions (default only names)
  --casesensitive  ... case sensitive
  --out_aids=<outfile> ... output file of matched AIDs
  --out_all_aid_file=<out_all_aid_file> ... csv file: aid,name,method,target[s]
  --out_all_gid_file=<outfile> ... output file of all protein GIDs
  --v            ... verbose
  --vv           ... very verbose
  --h            ... this help
'''%{'PROG':PROG}
  string=None; regexp=None; out_aids_file=None; out_all_aid_file=None;
  out_all_gid_file=None;
  casesensitive=False; desc=False; verbose=0;
  opts,pargs = getopt.getopt(sys.argv[1:],'',['h','v','vv','string=',
  'out_all_aid_file=', 'out_all_gid_file=',
  'regexp=','out_aids=','casesensitive','desc'])
  if not opts: ErrorExit(usage)
  for (opt,val) in opts:
    if opt=='--h': ErrorExit(usage)
    elif opt=='--string': string=val
    elif opt=='--regexp': regexp=val
    elif opt=='--out_aids': out_aids_file=val
    elif opt=='--out_all_aid_file': out_all_aid_file=val
    elif opt=='--out_all_gid_file': out_all_gid_file=val
    elif opt=='--casesensitive': casesensitive=True
    elif opt=='--desc': desc=True
    elif opt=='--vv': verbose=2
    elif opt=='--v': verbose=1
    else: ErrorExit('Illegal option: %s'%val)

  if not (string or regexp or out_all_aid_file):
    ErrorExit('-string or -regexp or -out_all_aid_file required\n'+usage)

  fout_aid=None
  if out_aids_file:
    fout_aid=open(out_aids_file,'w')
    if not fout_aid:
      ErrorExit('cannot open: %s'%out_aids_file)

  fout_all_aid=None
  if out_all_aid_file:
    fout_all_aid=open(out_all_aid_file,'w')
    if not fout_all_aid:
      ErrorExit('cannot open: %s'%out_all_aid_file)
    fout_all_aid.write('AID,name,method,target')
    if verbose>1: fout_all_aid.write('description')
    fout_all_aid.write('\n')
  fout_all_gid=None
  if out_all_gid_file:
    fout_all_gid=open(out_all_gid_file,'w')
    if not fout_all_gid:
      ErrorExit('cannot open: %s'%out_all_gid_file)

  if not os.access(ASSAY_DESC_DIR,os.R_OK):
    ErrorExit('cannot find: %s'%ASSAY_DESC_DIR)

# files=[]
# for file in os.listdir(ASSAY_DESC_DIR):
#   if not re.search('\.descr\.xml\.gz',file): continue
#   try:
#     aid=int(re.sub('\.descr\.xml\.gz','',file))
#   except:
#     print >>sys.stderr, 'cannot parse AID: "%s"'%file
#     continue
#   fpath=ASSAY_DESC_DIR+'/'+file
#   files.append((fpath,aid))

  if string and not regexp: regexp=string
  if regexp:
    if casesensitive:
      rob=re.compile(regexp)
    else:
      rob=re.compile(regexp,re.I)

  t0=time.time()

  aids={}
  badfiles=[]
  n_gids_out=0

# for fpath,aid in files:
  files=[]
  for fname_zip in os.listdir(ASSAY_DESC_DIR):
    if not re.search('\.zip',fname_zip): continue
    fpath_zip=ASSAY_DESC_DIR+'/'+fname_zip
    try:
      zf=zipfile.ZipFile(fpath_zip,'r')
    except:
      print >>sys.stderr, 'ERROR: cannot read fpath_zip: "%s"'%fpath_zip
      continue
    flist_xml_gz=zf.namelist()
    zf.close()
    for fpath_xml_gz in flist_xml_gz:
      if not re.search('\.descr\.xml\.gz',fpath_xml_gz): continue
      try:
        if re.search(r'/',fpath_xml_gz):
          txt=re.sub(r'^.*/(\d*)\.descr\.xml\.gz',r'\1',fpath_xml_gz)
        else:
          txt=re.sub(r'\.descr\.xml\.gz','',fpath_xml_gz)
        aid=int(txt)
      except:
        print >>sys.stderr, 'cannot parse AID: "%s"'%fpath_xml_gz
        print >>sys.stderr, 'DEBUG txt: "%s"'%txt
        continue
      files.append((fpath_zip,fpath_xml_gz,aid))

  if not os.access(SCRATCHDIR,os.R_OK):
    try:
      os.mkdir(SCRATCHDIR)
    except:
      print >>sys.stderr, 'ERROR: failed to create SCRATCHDIR %s'%SCRATCHDIR
      sys.exit(1)

  for f in files:
    fpath_zip,fpath_xml_gz,aid = f
    if verbose>1: print >>sys.stderr, '%d: %s:%s'%(aid,fpath_zip,fpath_xml_gz)
    zf=zipfile.ZipFile(fpath_zip,'r')
    cwd=os.getcwd()
    os.chdir(SCRATCHDIR)
    zf.extract(fpath_xml_gz)
    os.chdir(cwd)
    zf.close()
    f_xml=gzip.open(SCRATCHDIR+'/'+fpath_xml_gz)
    fxml=f_xml.read()
    f_xml.close()
    if not fxml:
      print >>sys.stderr, 'ERROR: file empty: AID %d: %s'%(aid,fpath)
      badfiles.append(fpath)
      continue

    aname,ameth,adesc,atargs,gids = ParseAssayXml(fxml)
    if fout_all_aid:
      fout_all_aid.write('%d,"%s","%s","%s"'%(aid,aname,ameth,atargs))
      if verbose>1:
        fout_all_aid.write(',"%s"'%(adesc))
      fout_all_aid.write('\n')

    if fout_all_gid:
      for gid in gids:
        fout_all_gid.write('%d\n'%(gid))
        n_gids_out+=1

    ok=False
    if regexp:
      if rob.search(aname):
        if verbose:
          print >>sys.stderr, 'name match: AID %d: %s'%(aid,aname)
        ok=True
      elif desc and rob.search(adesc):
        if verbose: print >>sys.stderr, 'desc match: AID %d: %s'%(aid,adesc)
        ok=True
    if ok:
      aids[aid]=(aname,adesc)
      if fout_aid:
        fout_aid.write('%d\n'%aid)
    os.unlink(SCRATCHDIR+'/'+fpath_xml_gz)

  if fout_aid: fout_aid.close()
  if fout_all_aid: fout_all_aid.close()
  if fout_all_gid: fout_all_gid.close()

  for dir in os.listdir(SCRATCHDIR):
    subdir=SCRATCHDIR+"/"+dir
    for f in os.listdir(subdir):
      os.unlink(subdir+'/'+f)
    os.rmdir(subdir)
  os.rmdir(SCRATCHDIR)

  print >>sys.stderr, '%s: total assays: %d'%(PROG,len(files))
  print >>sys.stderr, '%s: matched assays: %d'%(PROG,len(aids.keys()))
  if n_gids_out:
    print >>sys.stderr, '%s: target protein GIDs written: %d'%(PROG,n_gids_out)
  print >>sys.stderr, '%s: ERRORS: bad files: %d'%(PROG,len(badfiles))
  for badfile in badfiles:
    print >>sys.stderr, '\tbadfile: %s'%(os.path.basename(badfile))
  print >>sys.stderr, ('%s: total elapsed time: %s'%(PROG,time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))))
