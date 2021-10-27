#!/usr/bin/env python3
"""
Utility functions for TCGA REST API.
"""
import sys,os,re,json,time,logging

from ..util import rest
#
##############################################################################
def ListProjects(base_url, skip, nmax, fout):
  n_out=0; tags=None;
  from_next=skip; size=100;
  while True:
    url_next = (base_url+'/projects?from={0}&size={1}'.format(from_next, size))
    rval = rest.GetURL(url_next, parse_json=True)
    projects = rval["data"]["hits"] if "data" in rval and "hits" in rval["data"] else []
    for project in projects:
      logging.debug(json.dumps(project, indent=2))
      if not tags:
        tags = list(project.keys())
        fout.write("\t".join(tags)+"\n")
      vals = [(str(project[tag]) if tag in project else "") for tag in tags]
      fout.write("\t".join(vals)+"\n")
      n_out+=1
      if n_out>=nmax: break
    if n_out>=nmax: break
    total = rval["data"]["pagination"]["total"] if "data" in rval and "pagination" in rval["data"] and "total" in rval["data"]["pagination"] else None
    count = rval["data"]["pagination"]["count"] if "data" in rval and "pagination" in rval["data"] and "count" in rval["data"]["pagination"] else None
    if not count or count<size: break
    from_next += count
  logging.info("n_out: %d / %d"%(n_out, total))

##############################################################################
def ListCases(base_url, skip, nmax, fout):
  n_out=0; tags=None;
  from_next=skip; size=100;
  while True:
    url_next = (base_url+'/cases?from={0}&size={1}'.format(from_next, size))
    rval = rest.GetURL(url_next, parse_json=True)
    cases = rval["data"]["hits"] if "data" in rval and "hits" in rval["data"] else []
    for case in cases:
      logging.debug(json.dumps(case, indent=2))
      if not tags:
        tags = list(case.keys())
        fout.write("\t".join(tags)+"\n")
      vals = [(str(case[tag]) if tag in case else "") for tag in tags]
      fout.write("\t".join(vals)+"\n")
      n_out+=1
      if n_out>=nmax: break
    if n_out>=nmax: break
    total = rval["data"]["pagination"]["total"] if "data" in rval and "pagination" in rval["data"] and "total" in rval["data"]["pagination"] else None
    count = rval["data"]["pagination"]["count"] if "data" in rval and "pagination" in rval["data"] and "count" in rval["data"]["pagination"] else None
    if not count or count<size: break
    from_next += count
  logging.info("n_out: %d / %d"%(n_out, total))

##############################################################################
def ListFiles(base_url, skip, nmax, fout):
  n_out=0; tags=None;
  from_next=skip; size=100;
  while True:
    url_next = (base_url+'/files?from={0}&size={1}'.format(from_next, size))
    rval = rest.GetURL(url_next, parse_json=True)
    files = rval["data"]["hits"] if "data" in rval and "hits" in rval["data"] else []
    for file_this in files:
      logging.debug(json.dumps(file_this, indent=2))
      if not tags:
        tags = list(file_this.keys())
        fout.write("\t".join(tags)+"\n")
      vals = [(str(file_this[tag]) if tag in file_this else "") for tag in tags]
      fout.write("\t".join(vals)+"\n")
      n_out+=1
      if n_out>=nmax: break
    if n_out>=nmax: break
    total = rval["data"]["pagination"]["total"] if "data" in rval and "pagination" in rval["data"] and "total" in rval["data"]["pagination"] else None
    count = rval["data"]["pagination"]["count"] if "data" in rval and "pagination" in rval["data"] and "count" in rval["data"]["pagination"] else None
    if not count or count<size: break
    from_next += count
  logging.info("n_out: %d / %d"%(n_out, total))

##############################################################################
def ListAnnotations(base_url, skip, nmax, fout):
  n_out=0; tags=None;
  from_next=skip; size=100;
  while True:
    url_next = (base_url+'/annotations?from={0}&size={1}'.format(from_next, size))
    rval = rest.GetURL(url_next, parse_json=True)
    annos = rval["data"]["hits"] if "data" in rval and "hits" in rval["data"] else []
    for anno in annos:
      logging.debug(json.dumps(anno, indent=2))
      if not tags:
        tags = list(anno.keys())
        fout.write("\t".join(tags)+"\n")
      vals = [(str(anno[tag]) if tag in anno else "") for tag in tags]
      fout.write("\t".join(vals)+"\n")
      n_out+=1
      if n_out>=nmax: break
    if n_out>=nmax: break
    total = rval["data"]["pagination"]["total"] if "data" in rval and "pagination" in rval["data"] and "total" in rval["data"]["pagination"] else None
    count = rval["data"]["pagination"]["count"] if "data" in rval and "pagination" in rval["data"] and "count" in rval["data"]["pagination"] else None
    if not count or count<size: break
    from_next += count
  logging.info("n_out: %d / %d"%(n_out, total))

##############################################################################
