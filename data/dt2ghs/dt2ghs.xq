module namespace ghs = "https://github.com/geoTirroirs/ghs";
import module namespace functx = "http://www.functx.com" at "functx.xq";

(: inscrire les propriétés GHS des classes Place et Name dans des maps, pour sérialisation (Turtle, etc.) :)

declare variable $ghs:dbname := "dico-topo";
declare variable $ghs:ghsURI := "http://datageotir.ensg.eu/vocab/";

(:::::::::::::::::::::::::::::::::::::::::::::::::::)
(:::::              FUNCTIONS                 ::::::)
(:::::::::::::::::::::::::::::::::::::::::::::::::::)

declare function ghs:lastComma-del($string) {
  if(ends-with($string, ",")) then functx:substring-before-last($string, ",")
  else $string
};

declare function ghs:dateFormat($date) {
  if(matches($date,"[0-9]{4}")) then
    'geotir:dateunique "'||$date||'-01-01T00:00:00"^^xsd:dateTime'
  else if(matches($date,"[0-9]{3}")) then
    'geotir:dateunique "0'||$date||'-01-01T00:00:00"^^xsd:dateTime'
  else
    'pleiades:during <http://datageotir.ensg.eu/vocab/interval/'
    || replace(functx:trim($date), ' ', '_')
    ||'>'
};

(:::::::::::::::::::::::::::::::::::::::::::::::::::)
(:::::                 DATA                   ::::::)
(:::::::::::::::::::::::::::::::::::::::::::::::::::)

(: TODO
  
  pleiades:Place x
    rdfs:label x
    owl:sameAs x
    skos:altLabel x
    pleiades:hasFeatureType x
    pleiades:hasName x
  
  pleiades:Name x
    dcterms:bibliographicCitation x
    pleiades:during x
    geotir:dateunique x
    tisc:fuzzybegin
    tisc:begin
    tisc:end
    tisc:fuzzyend
    Pourquoi pas de rdfs:label ?
  
  skos:Concept
    rdfs:label
  
  NB: plusieurs traitements similaires sur les formes anciennes: FACTORISER!
  ======DEBUG avec les autres volumes======
:)


(: pleiades:Place URI [UNIQ] :)
declare function ghs:PlaceURI($article) {"<"||$ghs:ghsURI||$article/data(@id)||">"};

(: owl:sameAs rdfs:domain pleiades:Place [UNIQ] :)
declare function ghs:PlaceSameAs($article) {
  if(exists($article/data(insee))) then "<http://id.insee.fr/geo/commune/"||$article/data(insee)||">"
  else ()
};

(: rdfs:label rdfs:domain pleiades:Place [SEQ] :)
declare function ghs:getPlace_labels($article) {
  for $label in $article/vedette/sm
  return ghs:lastComma-del($label/text())
};

(: pleiades:hasFeatureType rdfs:domain pleiades:Place [SEQ] :) 
declare function ghs:getFeatureType($article) {
  for $featureType in $article/definition/data(typologie)
  return $featureType
};

(: skos:altLabel rdfs:domain pleiades:Place [SEQ] :)
declare function ghs:getPlace_altLabels($article) {
  for $altLabel in $article/forme_ancienne/i[1]
  return ghs:lastComma-del($altLabel/text())
};

(: pleiades:hasName rdfs:domain pleiades:Place [SEQ] :)
declare function ghs:getHasName($article) {
  for $hasName in $article/forme_ancienne/i[1]
  return
    "<"
    ||$ghs:ghsURI
    ||$article/data(@id)||'/'
    ||replace(functx:trim(ghs:lastComma-del($hasName/text())), ' ', '_')
    ||">"
};

declare function ghs:getPlaceProps($article) {
  map {
    "Class" : "pleiades:Place",
    "uri" : ghs:PlaceURI($article),
    "rdfs:label" : ghs:getPlace_labels($article),
    "skos:altLabel" : ghs:getPlace_altLabels($article),
    "owl:sameAs" : ghs:PlaceSameAs($article),
    "pleiades:hasFeatureType" : ghs:getFeatureType($article),
    "Names" : ghs:getNamesProps($article),
    "pleiades:hasName" : ghs:getHasName($article)
  }
};

declare function ghs:getNamesProps($article) {
  for $name in $article/forme_ancienne
  return map {
    "Class" : "pleiades:Name",
    "rdfs:label" : $name/i[1]/text(),
    "dcterms:bibliographicCitation" : $name/reference/text(),
    "uri" :
      "<"
      ||$ghs:ghsURI
      ||$article/data(@id)||'/'
      ||replace(functx:trim(ghs:lastComma-del($name/i[1]/text())), ' ', '_')
      ||">",
     "date" : ghs:dateFormat($name/data(date[1]))
   }
};
