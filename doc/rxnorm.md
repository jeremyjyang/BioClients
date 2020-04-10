# BioClients

##  RxNorm

From the NIH National Library of Medicine (NLM).

* <https://www.nlm.nih.gov/research/umls/rxnorm/>

### Usage examples

```
python3 -m BioClients.rxnorm.Client -h
python3 -m BioClients.rxnorm.Client list_sourcetypes
python3 -m BioClients.rxnorm.Client list_relationtypes
python3 -m BioClients.rxnorm.Client list_termtypes
python3 -m BioClients.rxnorm.Client list_propnames
python3 -m BioClients.rxnorm.Client list_propcategories
python3 -m BioClients.rxnorm.Client list_idtypes
python3 -m BioClients.rxnorm.Client list_class_types
python3 -m BioClients.rxnorm.Client list_classes
python3 -m BioClients.rxnorm.Client list_classes --class_types 'MESHPA,ATC1-4'
```

Requiring names:

```
python3 -m BioClients.rxnorm.Client get_name --ids "prozac,tamiflu"
python3 -m BioClients.rxnorm.Client get_name2rxcui --ids "prozac,tamiflu"
```

Requiring external IDs:
```
python3 -m BioClients.rxnorm.Client get_id2rxcui --ids "C2709711" --idtype UMLSCUI
```

Requiring RxCUI IDs:
```
python3 -m BioClients.rxnorm.Client get_rxcui_status --ids "131725,213269"
python3 -m BioClients.rxnorm.Client get_rxcui_properties --ids "131725,213269"
python3 -m BioClients.rxnorm.Client get_rxcui_ndcs --ids "131725,213269"
python3 -m BioClients.rxnorm.Client get_rxcui_allrelated --ids "131725,213269"
```

