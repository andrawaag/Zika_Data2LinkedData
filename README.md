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
The script is for demonstration purposes only. The different data values 
are mapped to the Wikidata namespace using freetext search.  
## Installation
TODO: Describe the installation process
## Usage
TODO: Write usage instructions
## Contributing
1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D
## History
TODO: Write history
## Credits
TODO: Write credits
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
