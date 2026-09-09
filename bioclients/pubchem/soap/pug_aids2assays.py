#!/usr/bin/env python
"""
pug_aids2assays.py - retrieve bioassays by AID from PubChem/PUG (circa 2010)
"""
import sys,os,re,urllib,time,getopt,tempfile,gzip
import pug_utils

PROG=os.path.basename(sys.argv[0])

PUGURL='http://pubchem.ncbi.nlm.nih.gov/pug/pug.cgi'
POLL_WAIT=10
MAX_WAIT=600

#############################################################################
def QueryPug_fetchassays(aids,format='csv',verbose=0):
  qxml='''\
<PCT-Data><PCT-Data_input><PCT-InputData>
  <PCT-InputData_query><PCT-Query><PCT-Query_type><PCT-QueryType>
    <PCT-QueryType_bas><PCT-QueryAssayData>
'''
  if format=='xml':
    qxml+='<PCT-QueryAssayData_output value="assay-xml">1</PCT-QueryAssayData_output>'
  else:
    qxml+='<PCT-QueryAssayData_output value="csv">4</PCT-QueryAssayData_output>'
  qxml+='''\
        <PCT-QueryAssayData_aids><PCT-QueryUids><PCT-QueryUids_ids>
          <PCT-ID-List>
            <PCT-ID-List_db>pcassay</PCT-ID-List_db>
            <PCT-ID-List_uids>
'''
  for aid in aids:
    qxml+=('<PCT-ID-List_uids_E>%d</PCT-ID-List_uids_E>\n'%aid)
  qxml+='''\
            </PCT-ID-List_uids>
          </PCT-ID-List>
        </PCT-QueryUids_ids></PCT-QueryUids></PCT-QueryAssayData_aids>
      <PCT-QueryAssayData_dataset value="complete">0</PCT-QueryAssayData_dataset>
      <PCT-QueryAssayData_focus>
        <PCT-Assay-FocusOption>
          <PCT-Assay-FocusOption_group-results-by value="substance">4</PCT-Assay-FocusOption_group-results-by>
        </PCT-Assay-FocusOption>
      </PCT-QueryAssayData_focus>
    </PCT-QueryAssayData></PCT-QueryType_bas>
  </PCT-QueryType></PCT-Query_type></PCT-Query></PCT-InputData_query>
</PCT-InputData></PCT-Data_input></PCT-Data>
'''

  # <PCT-Assay-FocusOption_group-results-by value="compound">0</PCT-Assay-FocusOption_group-results-by>

  if verbose:
    print >>sys.stderr,'connecting %s...'%PUGURL
    print >>sys.stderr,'submitting query for %d bioassays...'%len(aids)
  f=pug_utils.UrlOpenTry(PUGURL,qxml)
  pugxml=f.read()
  f.close()
  status,reqid,url,qkey,wenv,error=pug_utils.ParsePugXml(pugxml)
  return status,reqid,url,error

#############################################################################
if __name__=='__main__':
  n_chunk=1000;
  usage='''
  %(PROG)s - fetch PubChem bioassay files (CSV or XML) for AIDs

  required:
  --i=<infile>   ... input IDs file
  or
  --aids=<IDs>   ... input IDs, comma-separated
  and
  --o=<outfile>  ... output file

  options:
  --format=<FMT> ... csv|xml [default via filename]
  --nmax=<N>     ... maximum N IDs
  --skip=<N>     ... skip 1st N IDs in file
  --n_chunk=<N>  ... IDs per PUG request [%(N_CHUNK)d]
  --gz           ... output gzipped [default via filename]
  --v            ... verbose
  --vv           ... very verbose
  --h            ... this help
'''%{'PROG':PROG,'N_CHUNK':n_chunk}

  ifile=None; iaids=None; ofile=None; verbose=0; skip=0; nmax=0;
  format=None; gz=False; 
  opts,pargs = getopt.getopt(sys.argv[1:],'',['h','v','vv','i=','in=',
  'aids=','o=','out=','fmt=','format=','gz','gz','skip=','nmax=','n=',
  'n_chunk='])
  if not opts: pug_utils.ErrorExit(usage)
  for (opt,val) in opts:
    if opt=='--h': pug_utils.ErrorExit(usage)
    elif opt in ('--i','--in'): ifile=val
    elif opt=='--aids': iaids=val
    elif opt in ('--o','--out'): ofile=val
    elif opt in ('--n','--nmax'): nmax=int(val)
    elif opt in ('--format','--fmt'): format=val
    elif opt in ('--gzip','--gz'): gz=True
    elif opt=='--skip': skip=int(val)
    elif opt=='--n_chunk': n_chunk=int(val)
    elif opt=='--vv': verbose=2
    elif opt=='--v': verbose=1
    else: pug_utils.ErrorExit('Illegal option: %s'%val)

  if not ofile:
    pug_utils.ErrorExit('--o required\n'+usage)
  if not (ifile or iaids):
    pug_utils.ErrorExit('--i or --aids required\n'+usage)
  if (ofile[-3:]=='.gz'):
    gz=True
    ext=re.sub('^.*\.','',ofile[:-3])
  else:
    ext=re.sub('^.*\.','',ofile)
  if not format: format=ext
  if format not in ('csv','xml'):
    pug_utils.ErrorExit('format "csv" or "xml" required\n'+usage)

  if ifile:
    faids=file(ifile)
    if not faids:
      pug_utils.ErrorExit('cannot open: %s\n%s'%(ifile,usage))
    i=0; aids=[];
    while True:
      line=faids.readline()
      if not line: break
      line=line.strip()
      if not line: continue
      i+=1
      if skip and i<=skip: continue
      if nmax and i>nmax: break
      try:
        field=re.sub('\s.*$','',line)	## may be addl field
        aid=int(field)
        aids.append(aid)
      except:
        print >>sys.stderr,'cannot parse aid: "%s"'%line
        continue
  else:
    buff=iaids
    try:
      buff=re.sub('\s','',buff)
      aids=map(lambda x:int(x),re.split(',',buff))
    except:
      pug_utils.ErrorExit('cannot parse "--aids %s"'%iaids)
  print >>sys.stderr,'aids read: %d'%len(aids)

  if not gz:
    fd,ofile_tmp=tempfile.mkstemp('.'+format+'.gz',PROG)
    os.close(fd)
    fout=file(ofile_tmp,'w')
  else:
    fout=file(ofile,'w')

  if not fout:
    pug_utils.ErrorExit('cannot open: %s\n%s'%(ofile,usage))

  n=0; i_query=0; nbytes_total=0; n_query_total=0;
  while n<len(aids):
    i_query+=1
    n_query=len(aids[n:n+n_chunk])
    print >>sys.stderr,'Q%d. [%d-%d] of %d'%(i_query,n+1,n+n_query,len(aids))

    status,reqid,url,error=QueryPug_fetchassays(aids[n:n+n_chunk],format,verbose)
    pug_utils.CheckStatus(status,error)

    if verbose:
      print >>sys.stderr,'query submit status: %s'%status

    if not url and not reqid:
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
    print >>sys.stderr,'assays: %d (%.2fMB)'%(n_query,nbytes/1e6)
    n_query_total+=n_query
    n+=n_chunk

  fout.close()
  if not gz:
    ftmp=gzip.open(ofile_tmp,'rb')
    fout=file(ofile,'w')
    fout.write(ftmp.read())
    ftmp.close()
    fout.close()
    os.unlink(ofile_tmp)

  print >>sys.stderr,'%s: total assays: %d (%.2fMB)'%(PROG,n_query_total,nbytes_total/1e6)
  sys.stderr.write('%s: format: %s'%(PROG,format))
  if gz: sys.stderr.write('(gzipped)')
  sys.stderr.write('\n')
