import xml.etree.ElementTree as ET
from esprawozdanie import settings
#my_namespaces = dict([node for _, node in ET.iterparse(file, events=['start-ns'])])

my_namespaces = {'tns': 'http://www.mf.gov.pl/schematy/SF/DefinicjeTypySprawozdaniaFinansowe/2018/07/09/JednostkaInnaWTysiacach', 
                'dtsf': 'http://www.mf.gov.pl/schematy/SF/DefinicjeTypySprawozdaniaFinansowe/2018/07/09/DefinicjeTypySprawozdaniaFinansowe/', 
                'jin': 'http://www.mf.gov.pl/schematy/SF/DefinicjeTypySprawozdaniaFinansowe/2018/07/09/JednostkaInnaStruktury', 
                'xsi': 'http://www.w3.org/2001/XMLSchema-instance', 
                'ds': 'http://www.w3.org/2000/09/xmldsig#', 
                'xades': 'http://uri.etsi.org/01903/v1.3.2#'}

def data_list(el_tag, root):
    """
    Finds the first subelement matching el_tag. 
    If element is found in the XML: creates a list of child elements lists. 
    Nested children are appended to the child list.
    Returns None if no element with given el_tag is Found in the document
    """
    element = root.find(el_tag, my_namespaces)
    if element:
        d = list()
        for child in element.iter():
            tag_with_namespace = child.tag
            index = tag_with_namespace.rfind('}')
            tag = tag_with_namespace[index+1:]
            text = child.text.strip()
            if text == "":
                l = list((tag,))
                d.append(l)
            else:
                l.extend(list((tag, text)))
        return d
    else:
        return None

def make_dict(list_data):
    """
    Iterates throught given list and creates dictionary 
    """
    for el in list_data:
        el = el[1:]
        return {el[i]: el[i+1] for i in range(0, len(el), 2)}

def str_to_bool(string):
    """Converts XML boolean values(true, false) to Python bool"""
    return string == 'true'

def calculation_dict(dictionary, key, list_el):
    """
    Matches search elements from list_el with parsed data, creating a dictionary 
    with only searched elements and values needed for calculation, converted to float type
    Returns a dict with data. 
    >>> calculation_data = calculation_dict(elements, 'rzis', ['A', 'A_II', 'A_III'])
    >>> {'A': 11048169.0, 'A_II': 0.0, 'A_III': 0.0 }
    """
    bilans_data = dict()
    for el in dictionary[key]:
        for let in list_el:
            if let in el:
                d = {el[0]: float(el[2])}
                bilans_data.update(d)
    return bilans_data


def parse_txt(text):
    """
    Parses XML string, extracts data needed for calculation, 
    returns a dictionary with data and calculation results
    """
    elements = dict()
    root = ET.fromstring(text)

    #NAGLOWEK SPRAWOZDANIA
    naglowek = data_list('tns:Naglowek', root)
    elements['naglowek'] = make_dict(naglowek)
    
    #WPROWADZENIE DO SPRAWOZDANIA
    intro_element = root.find('tns:WprowadzenieDoSprawozdaniaFinansowego', my_namespaces)
    intro = data_list('tns:WprowadzenieDoSprawozdaniaFinansowego', root)
    for item in intro:
        if "P_1A" in item:
            item = item[1:]
            elements['podmiot'] = {item[i]: item[i+1] for i in range(0, len(item), 2)}
        if "Siedziba" in item:
            item = item[1:]
            elements['siedziba'] = {item[i]: item[i+1] for i in range(0, len(item), 2)}
        if "Adres" in item:
            item = item[1:]
            elements['adres'] = {item[i]: item[i+1] for i in range(0, len(item), 2)}
        if "AdresPrzedsiebiorcyZagranicznego" in item:
            item = item[1:]
            elements['adres_zagran'] = {item[i]: item[i+1] for i in range(0, len(item), 2)}
    #PKD
    pkd_el = root.findall('.//tns:P_1C', my_namespaces)
    if pkd_el:
        for el in pkd_el:
            elements["pkd"] = [pkd.strip() for pkd in el.itertext() if pkd.strip()]

    #NIP
    nip_el = root.findall('.//tns:P_1D', my_namespaces)
    if nip_el:
        elements["nip"] = [el.text.strip() for el in nip_el][0]
    else:
        elements['nip'] = None
    
    #KRS
    krs_el = root.findall('.//tns:P_1E', my_namespaces)
    if krs_el:
        elements["krs"] = [el.text.strip() for el in krs_el][0]
    else:
        elements["krs"] = None

    elements['czas_dzialalnosci_jezeli_ograniczony'] = intro_element.find('tns:P_2', my_namespaces)
    elements['okres_sprawozdania'] = make_dict(data_list('tns:P_3', intro_element))
    elements["dane_laczne"] = str_to_bool(intro_element.find('tns:P_4', my_namespaces).text.strip())
    
    kontynuacja_dzialalnosci = make_dict(data_list('tns:P_5', intro_element))
    kontynuacja_dzialalnosci['P_5A'] = str_to_bool(kontynuacja_dzialalnosci.get('P_5A'))
    kontynuacja_dzialalnosci['P_5B'] = str_to_bool(kontynuacja_dzialalnosci.get('P_5B'))
    elements["kontynuacja_dzialalnosci"] = kontynuacja_dzialalnosci

    info_o_polaczeniu = data_list('tns:P_6', intro_element)
    if info_o_polaczeniu is not None:
        info_o_polaczeniu = make_dict(info_o_polaczeniu)
        info_o_polaczeniu['P_6A'] = str_to_bool(info_o_polaczeniu.get('P_6A'))
        elements["info_o_polaczeniu"] = info_o_polaczeniu

    zasady = intro_element.find('tns:P_7', my_namespaces)
    zasady_text = ""
    for el in zasady.itertext():
        zasady_text = zasady_text + el.strip().replace(u'\xa0', u' ')
    elements["zasady"] = zasady_text
    zalozenia = intro_element.find('tns:P_8', my_namespaces)
    
    zalozenia_text = ""
    if zalozenia is not None:
        for line in zalozenia.itertext():
            zalozenia_text = zalozenia_text + line.strip().replace(u'\xa0', u' ')
    elements['zalozenia'] = zalozenia_text
   
    elements["Bilans"] = data_list('tns:Bilans', root)
    elements['rzis'] = data_list('tns:RZiS', root)
    elements["zmiany"] = data_list('tns:ZestZmianWKapitale', root)
    elements["rachunek"] = data_list('tns:RachPrzeplywow', root)

    ##CALCULATING RESULTS
    bilans_data = calculation_dict(elements, "Bilans", ["Aktywa", "Pasywa_A"])
    aktywa_razem = bilans_data.get("Aktywa", 0)
    kapital_fundusz_wlasny = bilans_data.get("Pasywa_A", 0)

    report_data = calculation_dict(elements, 'rzis',[ "F", "I", "L", "A", "A_II", "A_III", "E", "D", "G"])
    zysk_strata_z_dz_operacyjnej = report_data.get("F", 0)
    zysk_strata_brutto = report_data.get("I", 0)
    zysk_strata_netto = report_data("L", 0)
    przychody_netto_ze_sprzedazy = report_data.get("A", 0)
    zmiana_stanu_produktow = report_data.get("A_II", 0)
    koszt_wytworzenia_na_wlasne_potrzeby = report_data.get("A_III",0)
    pozostale_koszty_operacyjne = report_data.get("E", 0)
    pozostale_przychody_operacyjne = report_data.get("D", 0)
    przychody_finansowe = report_data.get("G", 0)

    ##WARIANT POROWNAWCZY i CALCULACYJNY
    rentownosc_aktywow = (zysk_strata_netto*100) / aktywa_razem
    rentownosc_kapilu_wlasnego = (zysk_strata_netto*100)/kapital_fundusz_wlasny

    if any([el for el in elements['rzis'] if 'RZiSPor' in el]):
        #WARIANT POROWNAWCZY
        divided_by = przychody_netto_ze_sprzedazy-zmiana_stanu_produktow-koszt_wytworzenia_na_wlasne_potrzeby+pozostale_przychody_operacyjne 
        marza_operacyjna = (zysk_strata_z_dz_operacyjnej*100)/divided_by
        div = divided_by + przychody_finansowe
        marza_zysku_brutto = (zysk_strata_brutto*100)/div

        elements['marza_operacyjna'] = marza_operacyjna
        elements['marza_zysku_brutto'] = marza_zysku_brutto
        elements['rentownosc_aktywow'] = rentownosc_aktywow
        elements['rentownosc_kapitalu_wlasnego'] = rentownosc_kapilu_wlasnego
    else:
        #WARIANT CALCULACYJNY
        calc_marza_operacyjna = (zysk_strata_z_dz_operacyjnej*100)/ (przychody_netto_ze_sprzedazy+pozostale_przychody_operacyjne)
        calc_marza_zysku_brutto = (zysk_strata_brutto*100)/(przychody_netto_ze_sprzedazy + pozostale_przychody_operacyjne + przychody_finansowe)
        elements['marza_operacyjna'] = calk_marza_operacyjna
        elements['marza_zysku_brutto'] = calc_marza_zysku_brutto
        elements['rentownosc_aktywow'] = rentownosc_aktywow
        elements['rentownosc_kapitalu_wlasnego'] = rentownosc_kapilu_wlasnego

    return elements