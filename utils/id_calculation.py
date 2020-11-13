from lxml import etree
import string
import unidecode

dt_id = 'DT72'
dt_path = '../data/'+dt_id+'/output6.xml'
dpt = dt_id[2:4]
tree = etree.parse(dt_path)

def get_letter_numeric_val(character):
    """ renvoyer le numéro d’une lettre (a=0, b=1, c=2, etc.) """
    # des cas particuliers, pénibles
    if character in ('œ','Œ'):
        return(26)
    elif character.isalpha():
        return(string.ascii_lowercase.index(unidecode.unidecode(character.lower())))
    else:
        return(26)

def check_character_generator(id):
    """ dériver le carcatère de contrôle de l’id calculé, adaptation du NOID Tool """
    # https://en.wikisource.org/wiki/User:Inductiveload/BnF_ARK_format
    xdigits = "0123456789bcdfghjkmnpqrstvwxz"
    index_sum = 0
    i = 1
    for digit in id:
        index_sum += xdigits.index(digit.lower())*i
        i += 1
    return(xdigits[index_sum % 29])

def id_generator(dpt, dfn, pos):
    """ calculer un id pour chaque entrée d’un DT, à partir du dpt, de la vedette et sa position dans le DT """
    dfn_l1_val = get_letter_numeric_val(dfn[0:1])
    dfn_l2_val = get_letter_numeric_val(dfn[1:2])
    dfn_l3_val = get_letter_numeric_val(dfn[2:3])
    """
    dfn_l1_val = get_letter_numeric_val(dfn[-3:-2])
    dfn_l2_val = get_letter_numeric_val(dfn[-4:-3])
    dfn_l3_val = get_letter_numeric_val(dfn[-5:-4])
    """
    if pos % 2 == 0:
        id = (dfn_l1_val*dfn_l2_val*dfn_l3_val//(pos//2)) + pos
    else:
        id = (dfn_l1_val*dfn_l2_val*dfn_l3_val//pos) + pos
    zobi = id % len(dfn)
    # ramener sur 6 chiffres
    id = '0'*(6-len(str(id))) + str(id)
    id = 'P'+dpt+id
    id = id+str(check_character_generator(id))
    return(id, zobi, len(dfn))


i = 1
for entry in tree.xpath('/DICTIONNAIRE/article'):
    place_id = entry.get('id')
    dfn = entry.xpath('vedette/sm[1]')[0].text
    print(id_generator(dpt, dfn, i))
    i += 1
