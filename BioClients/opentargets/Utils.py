#!/usr/bin/env python3
"""
OpenTargets REST API client, using the Python client package.

https://www.targetvalidation.org/documentation/api/
http://opentargets.readthedocs.io/
https://docs.targetvalidation.org/programmatic-access/python-client
https://docs.targetvalidation.org/programmatic-access/rest-api
https://docs.targetvalidation.org/data-sources/genetic-associations
https://platform-api.opentargets.io/v3/platform
https://platform-api.opentargets.io/v3/platform/docs/swagger-ui
"""
import sys,os,re,json,csv,logging

import opentargets

#############################################################################
def SearchAssociations(otclient, ids, idtype, minscore, skip, nmax, fout):
  csvWriter = csv.writer(fout, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
  tags=None;
  n_id=0; n_assn=0; n_id_found=0;
  for id_this in ids:
    n_id+=1
    if n_id<=skip: continue
    logging.debug('%s:'%id_this)
    try:
      if idtype=="disease":
        assns = otclient.get_associations_for_disease(id_this)
      else:
        assns = otclient.get_associations_for_target(id_this)
    except Exception as e:
      logging.error(str(e))
      continue
    if assns:
      n_id_found+=1
    for assn in assns:
      logging.debug(json.dumps(assn, sort_keys=True, indent=2))
      if not tags:
        tags=["id","is_direct","target_id","gene_name","gene_symbol","disease_id","disease_efo_label","score_overall"]
        tags_assn_score_sources = list(assn['association_score']['datasources'].keys())
        tags_assn_score_types = list(assn['association_score']['datatypes'].keys())
        tags_evidence_count_sources = list(assn['evidence_count']['datasources'].keys())
        tags_evidence_count_types = list(assn['evidence_count']['datatypes'].keys())
        csvWriter.writerow(tags+
		list(map(lambda t:'assn_score_source.%s'%t, tags_assn_score_sources))+
		list(map(lambda t:'assn_score_type.%s'%t, tags_assn_score_types))+
		list(map(lambda t:'evidence_count_source.%s'%t, tags_evidence_count_sources))+
		list(map(lambda t:'evidence_count_type.%s'%t, tags_evidence_count_types)))
      assn_id = assn['id'] if 'id' in assn else ''
      is_direct = assn['is_direct'] if 'is_direct' in assn else ''
      target_id = assn['target']['id'] if 'target' in assn and 'id' in assn['target'] else ''
      gene_name = assn['target']['gene_info']['name'] if 'target' in assn and 'gene_info' in assn['target'] and 'name' in assn['target']['gene_info'] else ''
      gene_symbol = assn['target']['gene_info']['symbol'] if 'target' in assn and 'gene_info' in assn['target'] and 'symbol' in assn['target']['gene_info'] else ''
      disease_id = assn['disease']['id'] if 'disease' in assn and 'id' in assn['disease'] else ''
      disease_efo_label = assn['disease']['efo_info']['label'] if 'disease' in assn and 'efo_info' in assn['disease'] and 'label' in assn['disease']['efo_info'] else ''
      score_overall = assn['association_score']['overall'] if 'association_score' in assn and 'overall' in assn['association_score'] else ''
      vals=[assn_id, is_direct, target_id, gene_name, gene_symbol, disease_id, disease_efo_label, score_overall]
      for tag in tags_assn_score_sources:
        vals.append(assn['association_score']['datasources'][tag] if tag in assn['association_score']['datasources'] else '')
      for tag in tags_assn_score_types:
        vals.append(assn['association_score']['datatypes'][tag] if tag in assn['association_score']['datatypes'] else '')
      for tag in tags_evidence_count_sources:
        vals.append(assn['evidence_count']['datasources'][tag] if tag in assn['evidence_count']['datasources'] else '')
      for tag in tags_evidence_count_types:
        vals.append(assn['evidence_count']['datatypes'][tag] if tag in assn['evidence_count']['datatypes'] else '')

      for i in range(len(vals)):
        if type(vals[i]) is float:
          vals[i] = round(vals[i], 5)
      csvWriter.writerow(vals)
      n_assn+=1
    logging.debug('n_id=%d ; skip=%d ; nmax=%d'%(n_id, skip, nmax))
    if nmax and n_id-skip>=nmax: break
  logging.info('n_id = %d; n_id_found = %d; n_assn = %d'%(n_id-skip, n_id_found, n_assn))

#############################################################################
