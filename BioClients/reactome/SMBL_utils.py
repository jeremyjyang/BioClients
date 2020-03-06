#!/usr/bin/env python3

import sys,os,re,logging
import brn
import numpy

from .. import reactome.Utils
#
API_HOST='reactomews.oicr.on.ca:8080'
BASE_PATH='/ReactomeRESTfulAPI/RESTfulWS'
API_BASE_URL='http://'+API_HOST+BASE_PATH
#

net = brn.fromSBML("data/reactome_reactions_homo_sapiens.2.sbml")

print('reactions: %d'%len(net.reactions))
print('species: %d'%len(net.species))
print('values: %d'%len(net.values))

n_reac=0;
for r in net.reactions:
  n_reac+=1
  print('%3d. %s'%(n_reac,net.showreact(r,printstr=False)))
logging.info('n_reac: %d'%n_reac)


n_spec=0;
for s in net.species:
  n_spec+=1
  id_spec = re.sub(r'[^\d]','',s)
  spec = reactome.Utils.GetId(API_BASE_URL,id_spec,'PhysicalEntity',verbose)
  displayName = spec['displayName'] if 'displayName' in spec else ''
  schemaClass = spec['schemaClass'] if 'schemaClass' in spec else ''
  print('%3d. %s: (%s) %s'%(n_spec,id_spec,schemaClass,displayName))
logging.info('n_spec: %d'%n_spec)
