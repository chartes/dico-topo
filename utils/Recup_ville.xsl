<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:xs="http://www.w3.org/2001/XMLSchema"
  exclude-result-prefixes="xs"
  version="1.0">
  
  <xsl:output method="text" encoding="UTF-8"/>
  
  <xsl:variable name="sep">
    <xsl:text>	</xsl:text>
  </xsl:variable>
  <xsl:variable name="lf">
    <xsl:text>
</xsl:text>
  </xsl:variable>
  
  <xsl:template match="/">
    <xsl:text>ID	NomCommune	NomCanton</xsl:text>
    <xsl:value-of select="$lf"/>
    <xsl:apply-templates select="//article"/>
  </xsl:template>
  
  <!-- Récupère les commune dont la précisation est donnée dans la typologie  -->
  <xsl:template match="article">
    <xsl:choose>
      <xsl:when test="contains(definition/typologie,'commune')">
        <xsl:value-of select="@id"/>
        <xsl:value-of select="$sep"/>
        <xsl:value-of select="normalize-space(vedette/sm)"/>
        <xsl:value-of select="$sep"/>
        <xsl:value-of select="normalize-space(definition/localisation)"/>
        <xsl:value-of select="$lf"/>
      </xsl:when>
      <!-- Récupère les commune qui sont chef-lieu d'un arrondissement, de canton ou du département  -->
      <xsl:when test="contains(definition/typologie,'chef-lieu')">    
        <xsl:value-of select="@id"/>
        <xsl:value-of select="$sep"/>
        <xsl:value-of select="normalize-space(vedette/sm)"/>
        <xsl:value-of select="$sep"/>
        <xsl:value-of select="normalize-space(definition/typologie)"/>
        <xsl:value-of select="$lf"/>
      </xsl:when>
      <!-- Récupère les commune qui sont uniquement membres d'un canton  -->
      <xsl:when test="contains(definition/localisation,'canton d')">
        <xsl:value-of select="@id"/>
        <xsl:value-of select="$sep"/>
        <xsl:value-of select="normalize-space(vedette/sm)"/>
        <xsl:value-of select="$sep"/>
        <xsl:value-of select="normalize-space(definition/localisation)"/>
        <xsl:value-of select="$lf"/>
      </xsl:when>
      <xsl:when test="contains(definition/typologie,'arrondissement')">
        <xsl:value-of select="@id"/>
        <xsl:value-of select="$sep"/>
        <xsl:value-of select="normalize-space(vedette/sm)"/>
        <xsl:value-of select="$sep"/>
        <xsl:value-of select="normalize-space(definition/localisation)"/>
        <xsl:value-of select="$lf"/>
      </xsl:when>
      <xsl:otherwise/>
    </xsl:choose>
  </xsl:template>
</xsl:stylesheet>

