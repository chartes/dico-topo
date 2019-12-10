<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs"
    version="2.0">
    <xsl:template match="node() | @*"> <!-- Copie à l'identique du fichier
XML -->
        <xsl:copy>
            <xsl:apply-templates select="node() | @*"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="article">
        <xsl:copy>
            <!-- Nécessite un fichier xml qui comprent l'intégralité des données dictionnaire et article signifie 
                les deux étages nécessaires pour atteindre ID -->
            <xsl:if test="insee">
                <xsl:attribute name="type">commune</xsl:attribute>
              </xsl:if>
            <xsl:copy-of select="node() | @*"/>
        </xsl:copy>
    </xsl:template>
</xsl:stylesheet>