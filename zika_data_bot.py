# Author: Andra Waagmeester

import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON
import pprint
from rdflib import Namespace, Graph, URIRef, BNode, Literal
from rdflib.namespace import DCTERMS, RDFS, RDF, DC, XSD
import datetime

zikaGraph = Graph()
wdt = Namespace("http://www.wikidata.org/prop/direct/")
wd = Namespace("http://www.wikidata.org/entity/")
dcat = Namespace("http://www.w3.org/ns/dcat#")
fdp = Namespace("http://rdf.biosemantics.org/ontologies/fdp-o#")
datacite = Namespace("http://purl.org/spar/datacite/")

zikaGraph.bind("wdt", wdt)
zikaGraph.bind("wd", wd)
zikaGraph.bind("dcat", dcat)
zikaGraph.bind("fdp", fdp)
zikaGraph.bind("datacite", datacite)

# capture metadata template used: https://oncoxl.fair-dtls.surf-hosted.nl/editor/#!/
thisFile = URIRef("http://localhost/zika.ttl")
zikaGraph.add((thisFile, RDF.type, dcat.Distribution))
zikaGraph.add((thisFile, DCTERMS.title, Literal("CDC Zika Data", lang="en")))
zikaGraph.add((thisFile, DCTERMS.hasVersion, Literal(str(datetime.datetime.now()))))
zikaGraph.add((thisFile, dcat.accessURL, URIRef("https://chendaniely.shinyapps.io/zika_cdc_dashboard/")))
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

        # if isinstance(tuple.value, float):
        if pd.notnull(tuple.value):
            try:
                secondarylocation[tuple.country.replace("_", " ")][tuple.location2.replace("_", " ")][
                    tuple.report_date] = {"value": int(tuple.value), "unit": tuple.unit}
            except ValueError:
                print("boe")
                pass

pprint.pprint(secondarylocation)

for land in secondarylocation.keys():
    for location in secondarylocation[land].keys():
        # print(land)
        # if secondarylocation[land][location]["wikidata_qid"] != None:
        for date in secondarylocation[land][location].keys():
                if date != "wikidata_qid":
                    measurementIRI = URIRef("http://cdc_parsed_location.csv/"+land.replace(" ", "_")+location.replace(" ", "_")+date)
                    zikaGraph.add((measurementIRI, RDF.type, wd.Q12453))
                    if land in country.keys():
                        zikaGraph.add((measurementIRI, wdt.P17, URIRef(country[land.replace("_", " ")])))
                    #print(type(tuple.value), tuple.value)

                    zikaGraph.add((measurementIRI, wdt.P2257, Literal(secondarylocation[land][location][date]["value"], datatype=XSD.integer)))
                    zikaGraph.add((measurementIRI, wdt.P585, Literal(date, datatype=XSD.dateTime)))
                    if secondarylocation[land][location]["wikidata_qid"] != None:
                        zikaGraph.add((measurementIRI, wdt.P131, URIRef(secondarylocation[land][location]["wikidata_qid"])))

zikaGraph.serialize(destination="zika.ttl", format='turtle')

