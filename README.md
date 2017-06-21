# Zika_Data2LinkedData
This reopository contains a python script that converts tabular data on observed Zika cases in the americas. The data is converted to RDF using the Wikidata namespace. 
Having the data being described in the Wikidata namespaces allows rapid integration with data from Wikidata using federated SPARQL queries. 

The script `zika_data_bot.py` builds on Zika data provided by the [Zika cdc dashboard](https://chendaniely.shinyapps.io/zika_cdc_dashboard/).
1. First both the listed countries and their provinces are mapped to their Wikidata IRIs. 
(e.g Argentina maps to [wd:Q414](https://www.wikidata.org/wiki/Q414).)
2. Then the appropriate wikidata properties are selected. These are:
* [country - wdt:P17](http://www.wikidata.org/prop/direct/P17)
* [frequency of event - wdt:P2257](http://www.wikidata.org/prop/direct/P2257)
* [point in time - wdt:P585](http://www.wikidata.org/prop/direct/P585)
* [located in the administrative territorial entity - P131](http://www.wikidata.org/prop/direct/P131)
3. Metadata on the source is added using the [template](https://oncoxl.fair-dtls.surf-hosted.nl/editor/#!/) provided by [The GoFAIR initiative](https://www.dtls.nl/fair-data/go-fair/)

Finally a linked data file is generated which can be loaded in a triple store, such as [blazegraph](https://www.blazegraph.com/). 

Once loaded a federated SPARQL query can be applied to integrate the CDC data with data from Wikidata. 
The following example enriches the CDC data with the known latitude and longitude for the mapped administrative locations, the english wikipedia article on the administrative region and known academic institutes in the region. 

```sparql
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX ps: <http://www.wikidata.org/prop/statement/>
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
PREFIX schema: <http://schema.org/>

SELECT DISTINCT ?report_date ?country ?countryLabel ?country_coordinates ?administrative_entity ?administrative_entityLabel ?location_coordinates ?sitelink ?academic_institute ?institute_name ?value  WHERE {
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

```
Running this query on a locally installed sparql endpoint, returns the following results:

![example1](screendumps/cdc_zika_location_coordinates.png?raw=true)
![example2](screendumps/cdc_zika_wikipedia_acadamic_institute.png?raw=true)
### Disclaimer
The script is for demonstration purposes only. Mapping regions and provinces to theis Wikdiata identifier
is done by text search, which is error prone. Provinces like Sao Paolo or Buenos Aires have identicical names as cities. 
This is solved when existing identifiers, such as ISO codes, are used to describe the regions. 

## Installation
To be able to do similar or more complex integration with Zika data and other resources such as Wikidata, a local SPARQL endpoint is needed. 
In this exercise [blazegraph](https://www.blazegraph.com/) is used. Blazegraph can be 
downloaded[here](https://downloads.sourceforge.net/project/bigdata/bigdata/2.1.1/blazegraph.jar?r=https%3A%2F%2Fwww.blazegraph.com%2Fdownload%2F&ts=1498056181&use_mirror=netix).

1. Start blazegraph:
  
  ```java -server -Xmx4g -jar blazegraph.jar```
  
  2. Run the python script zika_data_bot.py:
  
  ```python3 zika_data_bot.py```
  
  3. Upload the resulting zika.ttl file to blazegraph, following the upload [instructions](https://wiki.blazegraph.com/wiki/index.php/Quick_Start#Load_Data)
  
  4. Run SPARQL queries in the query interface of your blazegraph instance. 


## License
The MIT License (MIT)
=====================

Copyright © 2017 

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the “Software”), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
