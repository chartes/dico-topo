
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs"
    version="2.0">
    
    <xsl:template match="/">
        <xsl:text>ID,NomCommune,NomCanton</xsl:text> 
        <xsl:apply-templates/>
    </xsl:template>
    <!-- Récupère les commune dont la précisation est donnée dans la typologie  -->
    <xsl:template match="article">
        <xsl:if test="contains(definition/typologie,'commune')">
            <xsl:value-of select="@id"/>
            <xsl:text>,</xsl:text>  
            <xsl:value-of select="vedette/sm"/>
            <xsl:text>,</xsl:text>  
            <xsl:value-of select="definition/localisation"/>
        </xsl:if>
        <!-- Récupère les commune qui sont chef-lieu d'un arrondissement, de canton ou du département  -->
        <xsl:if test="contains(definition/typologie,'chef-lieu')">    
            <xsl:value-of select="@id"/>
            <xsl:text>,</xsl:text>  
            <xsl:value-of select="vedette/sm"/>
            <xsl:text>,</xsl:text>  
            <xsl:value-of select="definition/typologie"/>
        </xsl:if>
        <!-- Récupère les commune qui sont uniquement membres d'un canton  -->
        <xsl:if test="contains(definition/localisation,'canton d')">
            <xsl:value-of select="@id"/>
            <xsl:text>,</xsl:text>  
            <xsl:value-of select="vedette/sm"/>
            <xsl:text>,</xsl:text>  
            <xsl:value-of select="definition/localisation"/>
        </xsl:if>
        <xsl:if test="contains(definition/typologie,'arrondissement')">
            <xsl:value-of select="@id"/>
            <xsl:text>,</xsl:text>  
            <xsl:value-of select="vedette/sm"/>
            <xsl:text>,</xsl:text>  
            <xsl:value-of select="definition/localisation"/>
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>

