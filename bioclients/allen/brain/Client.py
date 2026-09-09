#!/usr/bin/env python3
#############################################################################
### See: http://www.brain-map.org/api/index.html
### http://help.brain-map.org/display/api/RESTful+Model+Access+%28RMA%29
### 
###  http://api.brain-map.org/api/v2/data/[Model]/[Model.id].[json|xml|csv]
###
###  http://api.brain-map.org/api/v2/data/Organism/1.xml
###  http://api.brain-map.org/api/v2/data/Gene/15.xml
###  http://api.brain-map.org/api/v2/data/Chromosome/12.json
###  http://api.brain-map.org/api/v2/data/Structure/4005.xml
###
### http://api.brain-map.org/api/v2/data/Organism/query.json
### http://api.brain-map.org/api/v2/data/Gene/describe.json
### http://api.brain-map.org/api/v2/data/enumerate.json
###
###  http://api.brain-map.org/api/v2/data/Gene/
###  http://api.brain-map.org/api/v2/data/Gene/18376.json
### 
###  &num_rows=[#]&start_row=[#]&order=[...]
#############################################################################
import sys,os,re,argparse,time,json,logging

from ... import allen
#
##############################################################################
if __name__=='__main__':
  API_HOST='api.brain-map.org'
  API_BASE_PATH='/api/v2'
  PROG=os.path.basename(sys.argv[0])
  ftype='SYMBOL';
  ops = ["show_info", "list_probes"]
  parser = argparse.ArgumentParser( description='AllenBrainAtlas REST API client')
  parser.add_argument("op", choices=ops, help='OPERATION (select one)')
  parser.add_argument("--i", dest="ifile", help="input file")
  parser.add_argument("--ids", help="input IDs")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("-v", "--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  api_base_url='https://'+args.api_host+args.api_base_path

  fout = open(args.ofile, "w") if args.ofile else sys.stdout

  ids=[]
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.rstrip())
    fin.close()
  elif args.ids:
    ids = re.split('[, ]+', args.ids.strip())
  if len(ids)>0: logging.info('Input IDs: %d'%(len(ids)))

  t0=time.time()

  if args.op=="show_info":
    allen.brain.Utils.ShowInfo(api_base_url, fout)

  elif args.op=="list_probes":
    allen.brain.Utils.ListProbes(api_base_url, ids, fout)

  else:
    parser.error('Invalid operation: {0}'.format(args.op))

  logging.info('Elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0))))
