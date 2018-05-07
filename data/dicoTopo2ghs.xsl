<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:xs="http://www.w3.org/2001/XMLSchema"
  exclude-result-prefixes="xs"
  version="1.0">
  <xsl:output method="text"
    encoding="UTF-8"
    omit-xml-declaration="yes"
    indent="no"/>
  
  <xsl:variable name="lt"><xsl:text disable-output-escaping="yes">&lt;</xsl:text></xsl:variable>
  <xsl:variable name="ghsPref"><xsl:value-of select="$lt"/><xsl:text>http://datageotir.ensg.eu/vocab</xsl:text></xsl:variable>
  <xsl:variable name="slash"><xsl:text>/</xsl:text></xsl:variable>
  <xsl:variable name="lb"><xsl:text>
</xsl:text></xsl:variable>
  <xsl:variable name="indent"><xsl:text>        </xsl:text></xsl:variable>
  
  <xsl:template match="/">
    <!-- déclaration des préfixes -->
@prefix rdfs: <xsl:value-of select="$lt"/>http://www.w3.org/2000/01/rdf-schema#>.
@prefix xsd: <xsl:value-of select="$lt"/>http://www.w3.org/2001/XMLSchema#>.
@prefix xml: <xsl:value-of select="$lt"/>http://www.w3.org/XML/1998/namespace>.
@prefix owl: <xsl:value-of select="$lt"/>http://www.w3.org/2002/07/owl#>.
@prefix foaf: <xsl:value-of select="$lt"/>http://xmlns.com/foaf/0.1/>.
@prefix dcterms: <xsl:value-of select="$lt"/>http://purl.org/dc/terms/>.
@prefix rdf: <xsl:value-of select="$lt"/>http://www.w3.org/1999/02/22-rdf-syntax-ns#>.
@prefix skos: <xsl:value-of select="$lt"/>http://www.w3.org/2004/02/skos/core#>.
@prefix cc: <xsl:value-of select="$lt"/>http://creativecommons.org/ns#>.
@prefix vann: <xsl:value-of select="$lt"/>http://purl.org/vocab/vann/>.
@prefix osspr: <xsl:value-of select="$lt"/>http://data.ordnancesurvey.co.uk/ontology/spatialrelations/>.
@prefix lsc: <xsl:value-of select="$lt"/>http://linkedscience.org/lsc/ns#>.

@prefix tisc: <xsl:value-of select="$lt"/>http://observedchange.com/tisc/ns/#>.
@prefix rlsp: <xsl:value-of select="$lt"/>http://data.ign.fr/def/relationsspatiales#>.
@prefix pleiades: <xsl:value-of select="$lt"/>https://pleiades.stoa.org/places/vocab#>.
@prefix geo: <xsl:value-of select="$lt"/>http://www.opengis.net/ont/geosparql#>.
@prefix geom: <xsl:value-of select="$lt"/>http://data.ign.fr/def/geometrie#>.
@prefix xysemantics: <xsl:value-of select="$lt"/>http://data.ign.fr/def/xysemantics>.
@prefix geotir: <xsl:value-of select="$ghsPref"/>>.
    <!-- appel des toponymes -->
    <xsl:apply-templates/>
  </xsl:template>
  
  <xsl:template match="//article">
    <!-- racine entité -->
    <xsl:value-of select="$ghsPref"/>
    <xsl:value-of select="$slash"/>
    <xsl:value-of select="@id"/>
    <xsl:text>></xsl:text>
    <xsl:text> a pleiades:Place;</xsl:text>
    <xsl:value-of select="$lb"/>
    
    <!-- rdfs:label -->
    <xsl:value-of select="$indent"/><xsl:text>rdfs:label "</xsl:text>
    <!-- Bordel: on a plusieurs vedette parfois ([1], et la ponctuation est mal normalisée (test foireux) -->
    <xsl:choose>
      <xsl:when test="substring(vedette/sm[1], string-length(vedette/sm[1]), 1) = ','">
        <xsl:value-of select="substring(vedette/sm[1], 1, string-length(vedette/sm[1])-1)"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="vedette/sm[1]"/>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:text>";</xsl:text>
    
    <!-- owl:sameAS = alignement avec GHD: comment on produit ça ? -->
    
    <!-- skos:altLabel : les formes rejetées anciennes… ; problème de leur identification… => on crée une entité pour chaque forme ? -->
    <xsl:value-of select="$lb"/>
    <xsl:value-of select="$indent"/><xsl:text>skos:altLabel</xsl:text>
    <xsl:value-of select="$lb"/>
    <xsl:for-each select="forme_ancienne">
      <xsl:value-of select="$indent"/>
      <xsl:value-of select="$indent"/>
      <xsl:text>"</xsl:text>
      <!-- toujours ce bordel dans la ponctuation -->
      <xsl:choose>
        <xsl:when test="substring(i[1], string-length(i[1]), 1) = ','">
          <xsl:value-of select="substring(i[1], 1, string-length(i[1])-1)"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="i"/>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:text>"</xsl:text>
      <xsl:choose>
        <xsl:when test="position() != last()">
          <xsl:text>,</xsl:text><xsl:value-of select="$lb"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>;</xsl:text><xsl:value-of select="$lb"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each>
    
    <!-- pleiades:hasFeatureType : on a besoin de règle et d’un référentiel pour extraire ce type ; pour l’instant on sort les choses brutes -->
    <xsl:value-of select="$indent"/><xsl:text>pleiades:hasFeatureType </xsl:text>
    <xsl:value-of select="$ghsPref"/>
    <xsl:text>/</xsl:text>
    <xsl:apply-templates select="definition/typologie"/>
    <xsl:text>>;</xsl:text>
    <xsl:value-of select="$lb"/>
    
    <!-- pleiades:hasName : je ne comprends pas la logique ici => on forge des URI… de quoi ? lien vers quoi ? -->
    
    <!-- skos:concept => suppose d’avoir l’arbre SKOS de nos concepts, non ? encore pas mal de travail de ce côté -->
  </xsl:template>
  
</xsl:stylesheet>