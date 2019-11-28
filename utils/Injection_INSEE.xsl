<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    version="2.0">
    <xsl:output
        method="xml"
        indent="yes"/>
    <xsl:template match="node() | @*"> <!-- Copie à l'identique du fichier
XML -->
        <xsl:copy>
            <xsl:apply-templates select="node() | @*"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="article">
        <xsl:copy>
            <xsl:copy-of select="node() | @*"/>
            <!-- Nécessite un fichier xml qui comprent l'intégralité des données dictionnaire et article signifie 
                les deux étages nécessaires pour atteindre ID -->
            <xsl:if test="document('file:/home/corentink/Bureau/Dicotopo/Tableau_Correction/DT86/DT86_INSEE.xml')/dictionnaire/article/ID=current()/@id">
                <xsl:element name="insee">
                    <xsl:value-of select="document('/home/corentink/Bureau/Dicotopo/Tableau_Correction//DT86/DT86_INSEE.xml')/dictionnaire/article/INSEE[preceding-sibling::ID = current()/@id]"/>
                </xsl:element>
            </xsl:if>
        </xsl:copy>
    </xsl:template>
</xsl:stylesheet>
