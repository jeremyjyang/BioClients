#!/usr/bin/env python3
"""
Utility for ChEBI SOAP API -- DEPRECATED.

* https://www.ebi.ac.uk/chebi/webServices.do
"""
###
import sys,os,re,json,argparse,time,logging
import pandas as pd
#
#from .. import chebi
##############################################################################
# Utility functions for ChEBI SOAP API.
###
import time,urllib.parse
import requests
import collections
import xmltodict
#
NCHUNK=100
#
API_HOST="www.ebi.ac.uk"
API_BASE_PATH="/webservices/chebi/2.0/test"
BASE_URL="https://"+API_HOST+API_BASE_PATH
#
##############################################################################
def GetEntity(ids, base_url=BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  for id_this in ids:
    response = requests.get(f"{base_url}/getCompleteEntity?chebiId={id_this}")
    rval_dict = xmltodict.parse(response.content)
    logging.debug(json.dumps(rval_dict, indent=2))
    try:
      result = rval_dict["S:Envelope"]["S:Body"]["getCompleteEntityResponse"]["return"]
    except Exception as e:
      continue
    if result is None: continue
    logging.debug(json.dumps(result, indent=2))
    if not tags:
      tags = [tag for tag in result.keys() if type(result[tag]) not in (list, dict, collections.OrderedDict)]
    df_this = pd.DataFrame({tag:[result[tag] if tag in result else ''] for tag in tags})
    if fout is None: df = pd.concat([df, df_this])
    else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
    n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  return df

##############################################################################
def GetEntityChildren(ids, base_url=BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  for id_this in ids:
    response = requests.get(f"{base_url}/getOntologyChildren?chebiId={id_this}")
    rval_dict = xmltodict.parse(response.content)
    logging.debug(json.dumps(rval_dict, indent=2))
    try:
      result = rval_dict["S:Envelope"]["S:Body"]["getOntologyChildrenResponse"]["return"]
    except Exception as e:
      continue
    if result is None: continue
    logging.debug(json.dumps(result, indent=2))
    children = result["ListElement"] if "ListElement" in result else []
    if type(children) is collections.OrderedDict: children = [children]
    for child in children:
      if not tags:
        tags = [tag for tag in child.keys() if type(child[tag]) not in (list, dict, collections.OrderedDict)]
      df_this = pd.DataFrame({tag:[child[tag] if tag in child else ''] for tag in tags})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  return df

##############################################################################
def GetEntityParents(ids, base_url=BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  for id_this in ids:
    response = requests.get(f"{base_url}/getOntologyParents?chebiId={id_this}")
    rval_dict = xmltodict.parse(response.content)
    logging.debug(json.dumps(rval_dict, indent=2))
    try:
      result = rval_dict["S:Envelope"]["S:Body"]["getOntologyParentsResponse"]["return"]
    except Exception as e:
      continue
    if result is None: continue
    logging.debug(json.dumps(result, indent=2))
    parents = result["ListElement"] if "ListElement" in result else []
    if type(parents) is collections.OrderedDict: parents = [parents]
    for parent in parents:
      if not tags:
        tags = [tag for tag in parent.keys() if type(parent[tag]) not in (list, dict, collections.OrderedDict)]
      df_this = pd.DataFrame({tag:[parent[tag] if tag in parent else ''] for tag in tags})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  return df

#############################################################################
##############################################################################
if __name__=='__main__':
  epilog="Example entity IDs: 30273,33246,24433"
  parser = argparse.ArgumentParser(description='ChEBI SOAP API client -- DEPRECATED', epilog=epilog)
  ops = [ 
	"get_entity",
	"get_entity_children",
	"get_entity_parents",
	"search"
	]
  parser.add_argument("op", choices=ops, help='OPERATION (select one)')
  parser.add_argument("--ids", help="input IDs")
  parser.add_argument("--i", dest="ifile", help="input file, IDs")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--query", help="search query (SMILES)")
  parser.add_argument("--skip", type=int, default=0)
  parser.add_argument("--nmax", type=int, default=None)
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("-v","--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url='https://'+args.api_host+args.api_base_path

  fout = open(args.ofile, 'w') if args.ofile else sys.stdout

  ids=[];
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

  if args.op[:3]=="get" and not (args.ifile or args.ids):
    parser.error(f"--i or --ids required for operation {args.op}.")

  if args.op == "get_entity":
    GetEntity(ids, base_url, fout)

  elif args.op == "get_entity_children":
    GetEntityChildren(ids, base_url, fout)

  elif args.op == "get_entity_parents":
    GetEntityParents(ids, base_url, fout)

  elif args.op == "search":
    parser.error(f'Not yet implemented: {args.op}')
    #Search(args.query, base_url, fout)

  else:
    parser.error(f'Invalid operation: {args.op}')
