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
import sys,os,re,time,logging
import urllib.parse,json

from ...util import rest
#
##############################################################################
def ShowInfo(base_url, fout):
  rval = rest.Utils.GetURL(base_url+'/data/enumerate.json', parse_json=True)
  print(json.dumps(rval, sort_keys=True, indent=2))


##############################################################################
def ListProbes(base_url, qrys, fout):
  n_probe=0;
  num_rows=0; start_row=0; total_rows=0;
  for qry in qrys:
    while True:
      logging.debug('start_row = %d, num_rows = %d, total_rows = %d'%(start_row, num_rows, total_rows))
      url_this = (base_url+"/data/query.json?start_row=%d&criteria=model::Probe,rma::criteria,gene[acronym$eq'%s']"%(start_row+num_rows, qry))
      try:
        rval = rest.Utils.GetURL(url_this, parse_json=True)
      except Exception as e:
        logging.error(e)
        continue
      success = rval['success'] if 'success' in rval else False
      if not success:
        break
      id_this = rval['id'] if 'id' in rval else None
      total_rows = rval['total_rows'] if 'total_rows' in rval else None
      num_rows = rval['num_rows'] if 'num_rows' in rval else None
      start_row = rval['start_row'] if 'start_row' in rval else None
      probes = rval['msg'] if 'msg' in rval else []
      for probe in probes:
        n_probe+=1
        if n_probe==1:
          tags = sorted(probe.keys()) ##1st probe defines fields
          fout.write('%s\n'%('\t'.join(['query','id']+tags)))
        vals = [qry, id_this]+[(probe[tag] if tag in probe else '') for tag in tags]
        fout.write('%s\n'%('\t'.join(vals)))
      if start_row+num_rows >= total_rows:
        break
  logging.info('probes: %d'%n_probe)

##############################################################################
