# Author: Andra Waagmeester

import pandas as pd
import numpy as np
import pprint
import sys
from SPARQLWrapper import SPARQLWrapper, JSON
import pprint
from rdflib import Namespace, Graph, URIRef, BNode, Literal
from rdflib.namespace import DCTERMS, RDFS, RDF, DC, XSD

zikaGraph = Graph()
wdt = Namespace("http://www.wikidata.org/prop/direct/")
wd = Namespace("http://www.wikidata.org/entity/")

zikaGraph.bind("wdt", wdt)
zikaGraph.bind("wd", wd)
countryMapping = dict()
secondarylocation = dict()
wikidata_sparql = SPARQLWrapper("https://query.wikidata.org/bigdata/namespace/wdq/sparql")

country = dict()
query = """SELECT ?item ?itemLabel
                    WHERE
                    {
	    ?item wdt:P31 wd:Q6256 ;
              rdfs:label ?label .
        FILTER (lang(?label)=\"en\")
	    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en" }
        }"""
print(query)
wikidata_sparql.setQuery(query)
wikidata_sparql.setReturnFormat(JSON)
results = wikidata_sparql.query().convert()
for result in results["results"]["bindings"]:
    country[result["itemLabel"]["value"]] = result["item"]["value"]



df_core = pd.read_csv("/Users/andra/Downloads/cdc_parsed_location.csv")
pprint.pprint(df_core["country"])

for tuple in df_core.itertuples():
    #print(tuple)
    if type(tuple.country) == str:
        print(tuple.country)
        if tuple.country.replace("_", " ") in country.keys():
            print(country[tuple.country.replace("_", " ")])
            zikaGraph.add((URIRef(country[tuple.country.replace("_", " ")]), RDFS.label, Literal(tuple.country)))

    if type(tuple.location2) == str:
        print(tuple.location2)
        if tuple.country.replace("_", " ") not in secondarylocation.keys():
            secondarylocation[tuple.country.replace("_", " ")] = dict()
        if tuple.location2.replace("_", " ") not in secondarylocation[tuple.country.replace("_", " ")].keys():
            query = """
                SELECT * WHERE {
                    ?item   rdfs:label """
            query += "\"" +tuple.location2.replace("_", " ")
            query += " Province\"@en ; wdt:P17 ?country ."
            query += "?country rdfs:label \"" + tuple.country.replace("_", " ") +"\"@en . }"

            print(query)
            wikidata_sparql.setQuery(query)
            wikidata_sparql.setReturnFormat(JSON)
            results = wikidata_sparql.query().convert()
            for result in results["results"]["bindings"]:
                secondarylocation[tuple.country.replace("_", " ")][tuple.location2.replace("_", " ")] = {"wikidata_qid": result["item"]["value"]}
            if tuple.location2.replace("_", " ") not in secondarylocation[tuple.country.replace("_", " ")] :
                secondarylocation[tuple.country.replace("_", " ")][tuple.location2.replace("_", " ")] = {"wikidata_qid": None}
        # if tuple.location2.replace("_", " ") in secondarylocation[tuple.country.replace("_", " ")].keys():
        secondarylocation[tuple.country.replace("_", " ")][tuple.location2.replace("_", " ")][tuple.report_date] = {"value":tuple.value, "unit": tuple.unit}





pprint.pprint(country)
pprint.pprint(secondarylocation)

for land in secondarylocation.keys():
    for location in secondarylocation[land].keys():
        print(land)
        if secondarylocation[land][location]["wikidata_qid"] != None:
            for date in secondarylocation[land][location].keys():
                measurementIRI = URIRef("http://cdc_parsed_location.csv/"+land.replace(" ", "_")+location.replace(" ", "_")+date)
                zikaGraph.add((measurementIRI, RDF.type, wd.Q12453))
                if land in country.keys():
                    zikaGraph.add((measurementIRI, wdt.P17, URIRef(country[land.replace("_", " ")])))
                zikaGraph.add((measurementIRI, wdt.P2257, Literal(tuple.value, datatype=XSD.integer)))
                if date != "wikidata_qid":
                    zikaGraph.add((measurementIRI, wdt.P585, Literal(date, datatype=XSD.dateTime)))

zikaGraph.serialize(destination="zika.ttl", format='turtle')

