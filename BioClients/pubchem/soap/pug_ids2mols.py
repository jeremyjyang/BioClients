#!/usr/bin/env python
'''
Retrieve compounds by SID or CID from PubChem/PUG (circa 2010).
'''
import sys,os,re,urllib,time,getopt,tempfile
import pug_utils

PROG=os.path.basename(sys.argv[0])

PUGURL='http://pubchem.ncbi.nlm.nih.gov/pug/pug.cgi'
POLL_WAIT=10
MAX_WAIT=600

#############################################################################
def QueryPug_fetchmols(dbname,ids,fmt='smiles',gzip=False,ntries=20,verbose=0):
  if gzip: compres='gzip'
  else: compres='none'
  print >>sys.stderr, 'DEBUG: fmt = "%s"'%fmt
  qxml='''\
<PCT-Data><PCT-Data_input><PCT-InputData>
  <PCT-InputData_download><PCT-Download><PCT-Download_uids>
    <PCT-QueryUids><PCT-QueryUids_ids>
    <PCT-ID-List><PCT-ID-List_db>%(DBNAME)s</PCT-ID-List_db><PCT-ID-List_uids>
'''%{'DBNAME':dbname}
  for id in ids:
    qxml+=('<PCT-ID-List_uids_E>%d</PCT-ID-List_uids_E>\n'%id)
  qxml+='''\
        </PCT-ID-List_uids></PCT-ID-List>
      </PCT-QueryUids_ids></PCT-QueryUids>
    </PCT-Download_uids>
    <PCT-Download_format value="%(FORMAT)s" />
    <PCT-Download_compression value="%(COMPRES)s" />
  </PCT-Download></PCT-InputData_download>
</PCT-InputData></PCT-Data_input></PCT-Data>
'''%{'FORMAT':fmt.lower(),'COMPRES':compres}
  if verbose:
    print >>sys.stderr,'connecting %s...'%PUGURL
    print >>sys.stderr,'submitting query for %d compounds...'%len(ids)
  f=pug_utils.UrlOpenTry(PUGURL,qxml,ntries)
  pugxml=f.read()
  f.close()
  status,reqid,url,qkey,wenv,error=pug_utils.ParsePugXml(pugxml)
  return status,reqid,url,error

#############################################################################
def ReverseFields(ofile):
  '''Fix smiles file from PubChem.'''
  fin=file(ofile)
  fd,ftmp=tempfile.mkstemp('.smi',PROG)
  while True:
    line=fin.readline()
    if not line: break
    os.write(fd,line)
  fin.close()
  os.close(fd)
  fout=file(ofile,"w")
  fin=file(ftmp)
  i=0
  while True:
    line=fin.readline()
    if not line: break
    i+=1
    line=line.rstrip()
    if not line: break
    fields=re.split('\s',line)
    if len(fields)==1:
      smiles='*'
      id=fields[0]
      print >>sys.stderr, 'NOTE: no structure: (line = %d) %s'%(i,line)
    else:
      smiles=fields[1]
      id=fields[0]
    fout.write("%s %s\n"%(smiles,id))
  fout.close()
  fin.close()
  os.unlink(ftmp)

#############################################################################
if __name__=='__main__':
  idtype='SID';
  USAGE='''
  %(PROG)s - fetch PubChem molecule files (SD or SMI) for IDs

  required:
  --i INFILE .......... input IDs file
  --o OUTFILE ......... output molecule file

  options:
  --idtype CID|SID .... [default=%(IDTYPE)s]
  --fmt FMT ........... smiles|sdf [default via filename]
  --nmax N ............ maximum N IDs
  --skip N ............ skip N IDs
  --n_chunk N ......... IDs per PUG request [10000]
  --ftp_ntries N ...... max tries per ftp-get
  --gz ................ output gzipped [default via filename]
  --v[v] .............. verbose [very]
  --h ................. this help
'''%{'PROG':PROG,'IDTYPE':idtype}

  ifile=None; ofile=None; verbose=0; skip=0; nmax=0; ftp_ntries=20;
  fmt=None; gzip=False; n_chunk=10000;
  opts,pargs = getopt.getopt(sys.argv[1:],'',['h','v','vv','i=','ftp_ntries=',
  'o=','fmt=','gz','skip=','nmax=','n_chunk=',
  'idtype='])
  if not opts: pug_utils.ErrorExit(USAGE)
  for (opt,val) in opts:
    if opt=='--h': pug_utils.ErrorExit(USAGE)
    elif opt=='--i': ifile=val
    elif opt=='--o': ofile=val
    elif opt=='--nmax': nmax=int(val)
    elif opt=='--idtype': idtype=val
    elif opt=='--n_chunk': n_chunk=int(val)
    elif opt=='--ftp_ntries': ftp_ntries=int(val)
    elif opt=='--fmt': fmt=val
    elif opt=='--gz': gzip=True
    elif opt=='--skip': skip=int(val)
    elif opt=='--vv': verbose=2
    elif opt=='--v': verbose=1
    else: pug_utils.ErrorExit('Illegal option: %s'%val)

  if not (ifile and ofile):
    pug_utils.ErrorExit('input and output files required\n'+USAGE)
  if (ofile[-3:]=='.gz'):
    gzip=True
    ext=re.sub('^.*\.','',ofile[:-3])
  else:
    ext=re.sub('^.*\.','',ofile)
  if not fmt: fmt=ext
  if fmt=='smi': fmt='smiles'
  if fmt.lower() not in ('smiles','sdf'):
    pug_utils.ErrorExit('format "smiles" or "sdf" required\n'+USAGE)
  if idtype.upper() not in ('SID','CID'):
    pug_utils.ErrorExit('idtype "SID" or "CID" required\n'+USAGE)

  fids=file(ifile)
  if not fids:
    pug_utils.ErrorExit('cannot open: %s\n%s'%(ifile,USAGE))
  fout=file(ofile,'w')
  if not fout:
    pug_utils.ErrorExit('cannot open: %s\n%s'%(ofile,USAGE))
  dbname='pccompound' if idtype.upper()=='CID' else 'pcsubstance'

  ids=[]; n=0;
  while True:
    line=fids.readline()
    if not line: break
    line=line.strip()
    if not line: continue
    n+=1
    if skip and n<=skip: continue
    if nmax and n>nmax: break
    try:
      field=re.sub('\s.*$','',line)	## may be addl field
      id=int(field)
      ids.append(id)
    except:
      print >>sys.stderr,'cannot parse id: "%s"'%line
      continue
  print >>sys.stderr,'ids read: %d'%len(ids)

  n=0; i_query=0; nbytes_total=0; n_query_total=0;
  while n<len(ids):
    i_query+=1
    n_query=len(ids[n:n+n_chunk])
    print >>sys.stderr,'Q%d. [%d-%d] of %d'%(i_query,n+1,n+n_query,len(ids))
    status,reqid,url,error=QueryPug_fetchmols(dbname,ids[n:n+n_chunk],fmt,gzip,ftp_ntries,verbose)
    pug_utils.CheckStatus(status,error)
    if verbose:
      print >>sys.stderr,'query submit status: %s'%status
    if not reqid and not url:
      pug_utils.ErrorExit('query submit ok but no ID; quitting.')
    i_poll=0
    while not url:
      if i_poll*POLL_WAIT>MAX_WAIT:
        pug_utils.PollPug(reqid,'cancel',verbose)
        pug_utils.ErrorExit('max wait exceeded (%d sec); quitting.'%MAX_WAIT)
      print >>sys.stderr,'polling PUG [ID=%d]...'%reqid
      status,reqid,url,qkey,wenv,error = pug_utils.PollPug(reqid,'status',verbose)
      pug_utils.CheckStatus(status,error)
      if url: break
      if verbose:
        print >>sys.stderr,'%d sec wait (status=%s)...'%(POLL_WAIT,status)
      time.sleep(POLL_WAIT)
      i_poll+=1
    if verbose:
      print >>sys.stderr,'URL: %s'%url
      print >>sys.stderr,'downloading to %s...'%ofile
    nbytes=pug_utils.DownloadUrl(url,fout)
    nbytes_total+=nbytes;
    print >>sys.stderr,'%ss: %d (%.2fMB)'%(dbname,n_query,nbytes/1e6)
    n_query_total+=n_query
    n+=n_chunk
  fout.close()
  if fmt.lower()=='smiles': ReverseFields(ofile)

  print >>sys.stderr,'%s: total %ss: %d (%.2fMB)'%(PROG,dbname,n_query_total,nbytes_total/1e6)
  sys.stderr.write('%s: format: %s'%(PROG,fmt))
  if gzip: sys.stderr.write('(gzipped)')
  sys.stderr.write('\n')
