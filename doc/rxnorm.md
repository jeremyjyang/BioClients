# `BioClients.rxnorm`

##  RxNorm

From the NIH National Library of Medicine (NLM).

* <https://www.nlm.nih.gov/research/umls/rxnorm/>
* <https://www.nlm.nih.gov/research/umls/rxnorm/docs/>
* <https://mor.nlm.nih.gov/RxNav/>
* <https://mor.nlm.nih.gov/download/rxnav/RxNormAPIs.html>
* <https://rxnav.nlm.nih.gov/RxNormAPIs.html>
* <https://rxnav.nlm.nih.gov/RxNormAPIREST.html>

 TERM TYPES
 TTY    Name
 IN     Ingredient
 PIN    Precise Ingredient
 MIN    Multiple Ingredients
 SCDC   Semantic Clinical Drug Component
 SCDF   Semantic Clinical Drug Form
 SCDG   Semantic Clinical Dose Form Group
 SCD    Semantic Clinical Drug
 GPCK   Generic Pack
 BN     Brand Name
 SBDC   Semantic Branded Drug Component
 SBDF   Semantic Branded Drug Form
 SBDG   Semantic Branded Dose Form Group
 SBD    Semantic Branded Drug
 BPCK   Brand Name Pack
 PSN    Prescribable Name
 SY     Synonym
 TMSY   Tall Man Lettering Synonym
 DF     Dose Form
 ET     Dose Form Entry Term
 DFG    Dose Form Group

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
python3 -m BioClients.rxnorm.Client get_name --ids "metformin"
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
python3 -m BioClients.rxnorm.Client get_rxcui_allproperties --ids "6809,131725,213269"
python3 -m BioClients.rxnorm.Client get_rxcui_ndcs --ids "131725,213269"
python3 -m BioClients.rxnorm.Client get_rxcui_allrelated --ids "131725,213269"
```

