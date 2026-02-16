import xml.etree.ElementTree as ET
import pandas as pd
import sys
import os
from lxml import etree  # Added for RelaxNG validation

def get_full_text(element):
    if element is None: return ''
    text = element.text or ''
    for child in element:
        text += get_full_text(child)
        text += child.tail or ''
    return text.strip()


def element_to_string(element):
    if element is None: return 'n/a'
    return ET.tostring(element, encoding='unicode', method='xml').strip()


def control_quality(original_xml, enriched_xml, validated_excel, schema_rng, output_excel):
    col_enr = os.path.basename(enriched_xml)
    conformity_problems = []

    # --- 1. CONFORMITY CHECKS (Well-formedness & Schema) ---
    print(f"Checking conformity for {enriched_xml}...")

    # Check A: Well-formedness (Syntaxe XML)
    try:
        parser = etree.XMLParser(recover=False)
        doc = etree.parse(enriched_xml, parser)
    except etree.XMLSyntaxError as e:
        conformity_problems.append({'check': 'well-formedness', 'status': 'FAILED', 'error': str(e)})
        # If the XML is broken, we can't continue the rest of the script
        print(f"CRITICAL ERROR: {enriched_xml} is not well-formed.")
    else:
        conformity_problems.append({'check': 'well-formedness', 'status': 'PASSED', 'error': ''})

        # Check B: RelaxNG Validation
        if os.path.exists(schema_rng):
            try:
                with open(schema_rng, 'rb') as f:
                    rng_doc = etree.parse(f)
                    relaxng = etree.RelaxNG(rng_doc)
                    if not relaxng.validate(doc):
                        for error in relaxng.error_log:
                            conformity_problems.append({
                                'check': 'dico-topo.rng',
                                'status': 'INVALID',
                                'error': f"Line {error.line}: {error.message}"
                            })
                    else:
                        conformity_problems.append({'check': 'dico-topo.rng', 'status': 'VALID', 'error': ''})
            except Exception as e:
                conformity_problems.append(
                    {'check': 'dico-topo.rng', 'status': 'ERROR', 'error': f"Schema error: {str(e)}"})
        else:
            conformity_problems.append(
                {'check': 'dico-topo.rng', 'status': 'SKIPPED', 'error': f"Schema file {schema_rng} not found"})

    # --- 2. LOAD DATA & SOURCE OF TRUTH ---
    df_truth = pd.read_excel(validated_excel)
    df_truth['id'] = df_truth['id'].astype(str)
    truth_map = {}
    for _, row in df_truth.iterrows():
        is_com = str(row['is_commune']).upper() in ['VRAI', 'TRUE', '1']
        code = str(row['insee_code']).split('.')[0].strip()
        truth_map[row['id']] = {'is_commune': is_com, 'insee': code}

    root_orig = ET.parse(original_xml).getroot()
    root_enr = ET.parse(enriched_xml).getroot()
    articles_enr = root_enr.findall('.//article')
    orig_map = {art.get('id'): art for art in root_orig.findall('.//article')}

    integrity_problems = []
    validity_problems = []

    # --- 3. PROCESSING ARTICLES (Your existing logic) ---
    for enr in articles_enr:
        art_id = enr.get('id')
        if art_id not in truth_map: continue

        truth = truth_map[art_id]
        expected_insee = truth['insee']

        # Delta Check
        if art_id in orig_map:
            orig = orig_map[art_id]
            for field in ['vedette', 'typologie', 'definition', 'localisation']:
                o_f, e_f = orig.find(field), enr.find(field)
                if " ".join(get_full_text(o_f).split()) != " ".join(get_full_text(e_f).split()):
                    integrity_problems.append(
                        {'id': art_id, 'input': element_to_string(o_f), 'output': element_to_string(e_f)})

        # Enrichment Check
        if truth['is_commune']:
            if enr.get('type') != 'commune':
                validity_problems.append(
                    {'id': art_id, 'problem': 'attribut_type_missing', col_enr: f'<article id="{art_id}">',
                     'correction': 'add type="commune"'})

            insee_tag = enr.find('insee')
            if insee_tag is None:
                validity_problems.append({'id': art_id, 'problem': 'balise_insee_missing', col_enr: 'n/a',
                                            'correction': f'<insee>{expected_insee}</insee>'})
            elif (insee_tag.text or '').strip() != expected_insee:
                validity_problems.append(
                    {'id': art_id, 'problem': 'insee_invalid', col_enr: element_to_string(insee_tag),
                     'correction': f'<insee>{expected_insee}</insee>'})

        else:
            commune_tags = enr.findall('.//commune')
            if not commune_tags:
                validity_problems.append({'id': art_id, 'problem': 'balise_commune_missing', col_enr: 'n/a',
                                            'correction': f'<commune insee="{expected_insee}">'})
            else:
                for c_tag in commune_tags:
                    actual_insee = c_tag.get('insee')
                    if actual_insee is None:
                        validity_problems.append(
                            {'id': art_id, 'problem': 'attribut_insee_missing', col_enr: element_to_string(c_tag),
                             'correction': f'insee="{expected_insee}"'})
                    elif actual_insee.strip() != expected_insee:
                        validity_problems.append(
                            {'id': art_id, 'problem': 'insee_invalid', col_enr: f'insee="{actual_insee}"',
                             'correction': f'insee="{expected_insee}"'})

    # --- 4. EXPORT ALL TABS ---
    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        pd.DataFrame(integrity_problems).to_excel(writer, sheet_name='integrity', index=False)
        pd.DataFrame(validity_problems).to_excel(writer, sheet_name='validity', index=False)
        pd.DataFrame(conformity_problems).to_excel(writer, sheet_name='conformity', index=False)

if __name__ == "__main__":
    # Updated signature: added dico-topo.rng path
    control_quality(
        '1_DT03.xml',
        '7_DT03_enriched.xml',
        '6_DT03_validated.xlsx',
        'dico-topo.rng',
        '8_DT03_controlled.xlsx'
    )