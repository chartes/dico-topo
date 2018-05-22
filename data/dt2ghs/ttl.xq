import module namespace ghs="https://github.com/geoTirroirs/ghs" at "dt2ghs.xq";
import module namespace functx = "http://www.functx.com" at "functx.xq";

(: TODO: reprendre, http://docs.basex.org/wiki/Serialization  :)

(: imprimer des sauts de ligne :)
declare variable $local:lb := codepoints-to-string(10);

(: SÉRIALISER plusieurs valeurs d’une propriété
  NB: ghs:getPlaceProps($article[@id="DT02-05424"]) renvoie:
  map {
    "skos:altLabel": ("Sancti-Lazari", "Saint-Lazdre-de-Chauny", "Ladres", "Sainct-Ladre"),
    "uri": "<http://datageotir.ensg.eu/vocab/DT02-05424>",
    "owl:sameAs": (),
    "Class": "pleiades:Place",
    "rdfs:label": "Saint-Lazare",
    "pleiades:hasName": ("<http://datageotir.ensg.eu/vocab/DT02-05424/Sancti-Lazari>", etc.),
    "pleiades:hasFeatureType": ("moulin à eau", "scierie mécanique")
  }
:)
declare function local:prop2ttl($propsMap as item()*, $propLabel as xs:string) {
  (: separator selon URI ou string :)
  let $sep :=
    if(starts-with($propsMap($propLabel)[1], '<')) then ''
    else '"'
  return
    if(empty($propsMap($propLabel))) then ()
    else
      $propLabel || ' '||$sep
      || string-join(map:get($propsMap, $propLabel), $sep||','||$local:lb||'    '||$sep)
      || $sep||';'||$local:lb||'  '
};

declare function local:Names2ttl($Names as item()*) as item()* {
  for $Name in $Names
  return
    map:get($Name, "uri")|| " a pleiades:Name;"
    || $local:lb||'  '
    || local:prop2ttl($Name, "dcterms:bibliographicCitation")
    || map:get($Name, "date")
    || "."
};


(: PRINT PREFIXES :)
"@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
@prefix xsd: <http://www.w3.org/2001/XMLSchema#>.
@prefix xml: <http://www.w3.org/XML/1998/namespace>.
@prefix owl: <http://www.w3.org/2002/07/owl#>.
@prefix foaf: <http://xmlns.com/foaf/0.1/>.
@prefix dcterms: <http://purl.org/dc/terms/>.
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>.
@prefix skos: <http://www.w3.org/2004/02/skos/core#>.
@prefix cc: <http://creativecommons.org/ns#>.
@prefix vann: <http://purl.org/vocab/vann/>.
@prefix osspr: <http://data.ordnancesurvey.co.uk/ontology/spatialrelations/>.
@prefix lsc: <http://linkedscience.org/lsc/ns#>.

@prefix tisc: <http://observedchange.com/tisc/ns/#>.
@prefix rlsp: <http://data.ign.fr/def/relationsspatiales#>.
@prefix pleiades: <https://pleiades.stoa.org/places/vocab#>.
@prefix geo: <http://www.opengis.net/ont/geosparql#>.
@prefix geom: <http://data.ign.fr/def/geometrie#>.
@prefix xysemantics: <http://data.ign.fr/def/xysemantics>.

@prefix geotir: <http://datageotir.ensg.eu/vocab>.

",

(:for $article in collection($ghs:dbname)/DICTIONNAIRE/article:)
(:for $article in collection($ghs:dbname)/DICTIONNAIRE[@dep="02"]/article:)
(:for $article in doc($ghs:dbname||"/DT02/DT02.xml")//article[@id="DT02-00011"]:)
for $article in doc($ghs:dbname||"/DT02/DT02.xml")//article
  let $props := ghs:getPlaceProps($article)
  return
  (
    map:get($props, "uri")|| " a pleiades:Place;"
    || $local:lb||'  '
    || local:prop2ttl($props, "rdfs:label")
    || local:prop2ttl($props, "owl:sameAs")
    || local:prop2ttl($props, "skos:altLabel")
    || local:prop2ttl($props, "pleiades:hasFeatureType")
    (: revoir la logique **skos:Concept** / pleiades:hasFeatureType :)
    || local:prop2ttl($props, "pleiades:hasName")||'.'
  ,
    local:Names2ttl(map:get($props, "Names"))
  )
  