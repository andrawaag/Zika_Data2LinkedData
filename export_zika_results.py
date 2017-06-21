
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import pprint

local_sparql = SPARQLWrapper("http://127.0.0.1:9999/blazegraph/namespace/zika/sparql")
query = """
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX ps: <http://www.wikidata.org/prop/statement/>
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
PREFIX schema: <http://schema.org/>

SELECT DISTINCT ?report_date ?country ?countryLabel ?administrative_entity ?administrative_entityLabel ?location_coordinates ?sitelink ?academic_institute ?value  WHERE {
       ?measurement wdt:P17 ?country ;
       				wdt:P585 ?report_date ;
                    wdt:P2257 ?value ;
                    wdt:P131 ?administrative_entity .
       FILTER (?value > 0)

   SERVICE <https://query.wikidata.org/bigdata/namespace/wdq/sparql> {
       ?administrative_entity wdt:P625 ?location_coordinates ;
                              rdfs:label ?administrative_entityLabel .
       ?sitelink schema:about ?administrative_entity ;
                 schema:inLanguage "en" .
       ?country wdt:P625 ?country_coordinates ;
                rdfs:label ?countryLabel .
       OPTIONAL { ?academic_institute wdt:P31/wdt:P279 wd:Q4671277 ;
         wdt:P131 ?administrative_entity ;
                rdfs:label ?institute_name .
                FILTER (lang(?institute_name)="en")}
       FILTER(lang(?countryLabel) = "en")
       FILTER(lang(?administrative_entityLabel) = "en")
       FILTER(REGEX(str(?sitelink), "wikipedia", "i"))
    }
  }

ORDER BY desc(?value)
"""
local_sparql.setQuery(query)
local_sparql.setReturnFormat(JSON)
results = local_sparql.query().convert()
csv = open("/tmp/testfile.txt","w")
for result in results["results"]["bindings"]:
    row = []
    for key in result.keys():
        row.append(result[key]["value"])
    print(', '.join('"{0}"'.format(w) for w in row))
