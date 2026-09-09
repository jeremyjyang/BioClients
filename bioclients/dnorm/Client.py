#!/usr/bin/env python3
"""
NCBI CBB REST client (Computational Biology Branch)
/CBBresearch/Lu/Demo/RESTful/tmTool.cgi/Disease/19894120/JSON
"""
### 
import sys,os,re,json,argparse,time,logging
#
from .. import rest
#
API_HOST='www.ncbi.nlm.nih.gov'
API_BASE_PATH='/CBBresearch/Lu/Demo/RESTful/tmTool.cgi'
#
OFMTS={'XML':'application/xml','JSON':'application/json'}
#
HEADERS={'Accept':OFMTS['JSON']}
#
#
##############################################################################
def GetLinks(pmids, bioconcept, base_url, fout):
  '''One TSV row per unique str.  Count multiple occurances.'''
  n_out=0;
  fout.write('pmid\tsourcedb\tbioconcept\ttext\tcount\n')
  for pmid in pmids:
    try:
      rval=rest.GetURL(base_url+'/%s/%d/JSON'%(bioconcept, pmid), headers=HEADERS, parse_json=True)
    except Exception as e:
      logging.error('%s'%(e))
      continue
    if not type(rval) is dict:
      logging.info('%s'%(str(rval)))
      continue

    sourceid = rval['sourceid'] if 'sourceid' in rval else None
    if not sourceid or pmid!=int(sourceid):
      logging.error('(%s;%d) PMID != sourceid (%s)'%(bioconcept, pmid, sourceid))
      continue
    dens = rval['denotations'] if 'denotations' in rval else []
    source = rval['sourcedb'] if 'sourcedb' in rval else ''
    text = rval['text'] if 'text' in rval else ''
    strs={};
    for den in dens:
      obj = den['obj'] if 'obj' in den else None
      span = den['span'] if 'span' in den and 'begin' in den['span'] and 'end' in den['span'] else None
      if obj and obj.startswith(bioconcept):
        if not text.strip() or not span or span['begin']>=len(text) or  span['end']>len(text):
          logging.error('(%s;%d) span [%s] out of range for text: "%s"'%(bioconcept, pmid, str(span), text))
          continue
        s=text[(span['begin']):span['end']]
        if s in strs:
          if obj in strs[s]:
            strs[s][obj]+=1
          else:
            strs[s][obj]=1
        else:
          strs[s]={obj:1}
    for s in sorted(strs.keys()):
      for obj in sorted(strs[s].keys()):
        fout.write('%d\t"%s"\t"%s"\t"%s"\t%d\n'%(pmid, source, obj, s, strs[s][obj]))
        n_out+=1
    logging.debug((json.dumps(rval, indent=2, sort_keys=False)))
  logging.info('(%s) PMIDs in: %d ; records out: %d'%(bioconcept, len(pmids), n_out))

##############################################################################
if __name__=='__main__':
  BIOCONCEPTS=['Disease','Gene','Chemical','Species','Mutation']
  parser = argparse.ArgumentParser(description='NCBI CBB Bioconcepts NER in PubMed docs REST API client', epilog='')
  ops = ['getlinks']
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--ids", help="query PubMed IDs (comma-separated)")
  parser.add_argument("--i", dest="ifile", help="input query PubMed IDs")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--bioconcept", choices=BIOCONCEPTS, default="Disease", help="")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url='https://'+args.api_host+args.api_base_path

  if args.ofile:
    fout=open(args.ofile,"w")
    if not fout: parser.error('cannot open outfile: %s'%args.ofile)
  else:
    fout=sys.stdout

  t0=time.time()

  if args.ifile:
    fin=open(args.ifile)
    if not fin: parser.error('cannot open pmidfile: %s'%args.ifile)
    pmids=[];
    while True:
      line=fin.readline()
      if not line: break
      try:
        pmid=int(line.rstrip())
      except Exception as e:
        logging.error('invalid PMID: "%s"'%(line.rstrip()))
        continue
      if line.rstrip(): pmids.append(pmid)
    logging.info('%s: input queries: %d'%(PROG, len(pmids)))
    fin.close()
  elif args.ids:
    pmids = re.split('[,\s]+', args.ids.strip())

  if args.op == "getlinks":
    GetLinks(ids, args.bioconcept, base_url, fout)

  else:
    parser.error("Invalid operation: %s"%args.op)

  logging.info(('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0)))))
