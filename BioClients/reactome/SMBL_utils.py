#!/usr/bin/env python3
"""
BRN = Biochemical Network Analysis (pybrn)
"""
import sys,os,re,logging
import numpy

from .. import reactome

try:
  import brn
except Exception as e:
  logging.error("pybrn not installed.")
  sys.exit()
#
API_HOST='reactomews.oicr.on.ca:8080'
BASE_PATH='/ReactomeRESTfulAPI/RESTfulWS'
API_BASE_URL='http://'+API_HOST+BASE_PATH
#

net = brn.fromSBML("data/reactome_reactions_homo_sapiens.2.sbml")

logging.info('reactions: %d'%len(net.reactions))
logging.info('species: %d'%len(net.species))
logging.info('values: %d'%len(net.values))

n_reac=0;
for r in net.reactions:
  n_reac+=1
  logging.info('%3d. %s'%(n_reac,net.showreact(r,printstr=False)))
logging.info('n_reac: %d'%n_reac)


n_spec=0;
for s in net.species:
  n_spec+=1
  id_spec = re.sub(r'[^\d]','',s)
  spec = reactome.Utils.GetId(API_BASE_URL,id_spec,'PhysicalEntity')
  displayName = spec['displayName'] if 'displayName' in spec else ''
  schemaClass = spec['schemaClass'] if 'schemaClass' in spec else ''
  logging.info('%3d. %s: (%s) %s'%(n_spec,id_spec,schemaClass,displayName))
logging.info('n_spec: %d'%n_spec)
