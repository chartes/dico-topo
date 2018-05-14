<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:xs="http://www.w3.org/2001/XMLSchema"
  exclude-result-prefixes="xs"
  version="1.0">
  <xsl:output method="text"
    encoding="UTF-8"
    omit-xml-declaration="yes"
    indent="no"/>
  
  <!--
    entités
      pleiades:Place = 
  -->
  
  <xsl:variable name="lt"><xsl:text disable-output-escaping="yes">&lt;</xsl:text></xsl:variable>
  <xsl:variable name="ghsPref"><xsl:value-of select="$lt"/><xsl:text>http://datageotir.ensg.eu/vocab</xsl:text></xsl:variable>
  <xsl:variable name="slash"><xsl:text>/</xsl:text></xsl:variable>
  <xsl:variable name="lb"><xsl:text>
</xsl:text></xsl:variable>
  <xsl:variable name="indent"><xsl:text>    </xsl:text></xsl:variable>
  
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
    
    <!-- Définition des concepts -->
    <!--
      skos:concept
      * suppose d’avoir l’arbre SKOS de nos concepts, non ? encore pas mal de travail de ce côté
      * pour les communes, on déclenche au template insee ?
      * TODO: revoir aussi la syntaxe ttl
    -->
<xsl:value-of select="$ghsPref"/>
<xsl:text>/commune> a skos:Concept;
    rdfs:label "commune".</xsl:text>
    
    <!-- appel des toponymes -->
    <xsl:apply-templates/>
  </xsl:template>
  
  <xsl:template match="//article">
    <xsl:value-of select="$lb"/>
    <xsl:value-of select="$ghsPref"/>
    <xsl:value-of select="$slash"/>
    <!-- TODO: revoir la logique d’identification des entités dans le modèle ; ici, on privilégie l’id au label -->
    <xsl:value-of select="@id"/>
    <xsl:text>></xsl:text>
    <xsl:text> a pleiades:Place;</xsl:text>
    <!-- rdfs:label -->
    <xsl:apply-templates select="vedette"/>
    <!-- pleiades:hasName / je ne comprends pas la logique ici: on forge des URI… de quoi ? lien vers quoi ? -->
    <!-- pleiades:hasFeatureType -->
    <xsl:apply-templates select="definition[typologie]"/>
    <!-- owl:sameAs -->
    <xsl:apply-templates select="insee"/>
    <!-- skos:altLabel
      * labels des formes rejetées anciennes…
      * problème de leur identification:  on crée une entité pour chaque forme ?
      * ne pas confondre avec la déclaration du nom et de sa documentation historique (pleiades:Name et dcterms:bibliographicCitation)
      * ne comprends pas la relation dans l’exemple d’Ancretteville-sur-Mer entre skos:altLabel et pleiades:hasName
    -->
    <xsl:if test="forme_ancienne">
      <xsl:value-of select="$lb"/>
      <xsl:value-of select="$indent"/><xsl:text>skos:altLabel</xsl:text>
      <xsl:value-of select="$lb"/>
      <xsl:for-each select="forme_ancienne">
        <xsl:value-of select="$indent"/>
        <xsl:value-of select="$indent"/>
        <xsl:text>"</xsl:text>
        <!-- toujours ce bordel dans la ponctuation -->
        <xsl:apply-templates select="i[1]" mode="trim"/>
        <xsl:text>"</xsl:text>
        <xsl:choose>
          <xsl:when test="position() != last()">
            <xsl:text>,</xsl:text><xsl:value-of select="$lb"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:text>;</xsl:text>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:for-each>
    </xsl:if>
    
    <!-- déclaration pleiades:Name, puis dcterms:bibliographicCitation -->
    <!-- appel du mode pour générer la liste des formes anciennes au format pleiades:Name (lourd…) -->
    <xsl:if test="forme_ancienne">
      <xsl:apply-templates select="." mode="pleiades_hasName"/>
    </xsl:if>
  </xsl:template>
  
  
  
  
  <!--
    rdfs:label
    * on a parfois plusieurs vedette parfois (sm[1])
    * ponctuation mal normalisée (cf test foireux)
  -->
  <xsl:template match="vedette">
    <xsl:value-of select="$lb"/>
    <xsl:value-of select="$indent"/><xsl:text>rdfs:label "</xsl:text>
    <xsl:apply-templates select="sm[1]" mode="trim"/>
    <xsl:choose>
      <xsl:when test="../definition/typologie or ../forme_ancienne">
        <xsl:text>";</xsl:text>
      </xsl:when>
      <xsl:otherwise>".</xsl:otherwise>
    </xsl:choose>
    
  </xsl:template>
  
  <!--
    owl:sameAS
    * comment produire les alignements avec GHD ?
    * comment gérer les approximations ("près de") ? cf article/definition/localisation/commune/@insee
  -->
  <xsl:template match="insee">
    <xsl:value-of select="$lb"/>
    <xsl:value-of select="$indent"/>
    <xsl:text>owl:sameAs </xsl:text>
    <xsl:value-of select="$lt"/>
    <xsl:text>http://id.insee.fr/geo/commune/</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>>;</xsl:text>
  </xsl:template>
  
  <!--
    TEMPLATE LOURD (GROS PBS DE PERF – revoir)
    pleiades:hasFeatureType
    pleiades:Name
    dcterms:bibliographicCitation
    pleiades:during | geotir:dateunique (=> UNIQDATE ?) | geotir:Interval (comprends pas, revoir doc)
    * on a besoin de règles et d’un référentiel pour extraire ce type ; pour l’instant on sort les choses brutes -->
  <xsl:template match="definition">
    <xsl:value-of select="$lb"/>
    <xsl:value-of select="$indent"/><xsl:text>pleiades:hasFeatureType </xsl:text>
    <xsl:value-of select="$ghsPref"/>
    <xsl:text>/</xsl:text>
    <xsl:value-of select="translate(typologie, ' ', '_')"/>
    <xsl:choose>
      <xsl:when test="../forme_ancienne">
        <xsl:text>>;</xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>>.</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  
  <xsl:template match="article" mode="pleiades_hasName">
    <xsl:variable name="id" select="@id"/>
    <xsl:value-of select="$lb"/>
    <xsl:value-of select="$indent"/>
    <xsl:text>pleiades:hasName </xsl:text>
    <xsl:value-of select="$lb"/>

    <!-- 1. Déclaration des Noms -->
    <xsl:for-each select="forme_ancienne">
      <!-- RUINE LES PERFS !!!!!!!! -->
      <xsl:variable name="label">
        <xsl:apply-templates select="i" mode="trim"/>
      </xsl:variable>
      <xsl:value-of select="$indent"/>
      <xsl:value-of select="$indent"/>
      <xsl:value-of select="$ghsPref"/>
      <xsl:text>/</xsl:text>
      <xsl:value-of select="$id"/>
      <xsl:text>/</xsl:text>
      <xsl:value-of select="translate($label, ' ', '_')"/>
      <xsl:text>></xsl:text>
      <xsl:choose>
        <xsl:when test="position() != last()">
          <xsl:text>,</xsl:text><xsl:value-of select="$lb"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>.</xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each>
    
    <!-- 2. enrichissement des entités ; très redondant, mais compliqué de ne faire qu’une passe en l’état -->
    <xsl:for-each select="forme_ancienne">
      <xsl:variable name="label">
        <xsl:apply-templates select="i" mode="trim"/>
      </xsl:variable>
      <xsl:value-of select="$lb"/>
      <xsl:value-of select="$ghsPref"/>
      <xsl:text>/</xsl:text>
      <xsl:value-of select="$id"/>
      <xsl:text>/</xsl:text>
      <xsl:value-of select="translate($label, ' ', '_')"/>
      <xsl:text>> a pleiades:Name;</xsl:text>
      <xsl:value-of select="$lb"/>
      <xsl:value-of select="$indent"/>
      <xsl:text>dcterms:bibliographicCitation "</xsl:text>
      <xsl:apply-templates select="reference"/>
      <xsl:text>";</xsl:text>
      <xsl:value-of select="$lb"/>
      <xsl:value-of select="$indent"/>
      <xsl:choose>
        <xsl:when test="number(date)">
          <xsl:text>geotir:dateunique "</xsl:text>
          <xsl:value-of select="date"/>
          <xsl:text>-01-01T00:00:00"^^xsd:dateTime.</xsl:text>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>pleiades:during </xsl:text>
          <xsl:value-of select="$lt"/>
          <xsl:text>http://datageotir.ensg.eu/vocab/interval/</xsl:text>
          <xsl:value-of select="translate(normalize-space(date),' ','_')"/>
          <xsl:text>>.</xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each>
        
  </xsl:template>
  
  <!--
    Un peu de traitement générique des vedettes
    Très pénible: la ponctuation est incluse dans la vedette
    À revoir dans les sources…
  -->
  <xsl:template match="*" mode="trim">
    <xsl:choose>
      <xsl:when test="substring(., string-length(.), 1) = ','">
        <xsl:value-of select="substring(., 1, string-length(.)-1)"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates select="."/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  
</xsl:stylesheet>