import xml.etree.ElementTree as ET
from esprawozdanie import settings
#my_namespaces = dict([node for _, node in ET.iterparse(file,
#                                                        events=['start-ns'])])
my_namespaces = {'tns': 'http://www.mf.gov.pl/schematy/SF/DefinicjeTypySprawozdaniaFinansowe/2018/07/09/JednostkaInnaWTysiacach', 
                'dtsf': 'http://www.mf.gov.pl/schematy/SF/DefinicjeTypySprawozdaniaFinansowe/2018/07/09/DefinicjeTypySprawozdaniaFinansowe/', 
                'jin': 'http://www.mf.gov.pl/schematy/SF/DefinicjeTypySprawozdaniaFinansowe/2018/07/09/JednostkaInnaStruktury', 
                'xsi': 'http://www.w3.org/2001/XMLSchema-instance', 
                'ds': 'http://www.w3.org/2000/09/xmldsig#', 
                'xades': 'http://uri.etsi.org/01903/v1.3.2#'}

def child_namespace_removal(child):
    tag_with_namespace = child.tag
    index = tag_with_namespace.rfind('}')
    tag_wo_namespace = tag_with_namespace[index+1:]
    return tag_wo_namespace

def data_list(el_tag, root):
    element = root.find(el_tag, my_namespaces)
    if element:
        d = list()
        for child in element.iter():
            tag = child_namespace_removal(child)
            text = child.text.strip()
            if text == "":
                l = list((tag,))
                d.append(l)
            else:
                l.extend(list((tag, text)))
        return d
    else:
        return None


def simple_element(parent):
    d = dict()
    for child in parent.iter():
        tag = child_namespace_removal(child)
        text = child.text.strip()
        d[tag] = text
    return d


def calculation_dict(dictionary, key, list_el):
    bilans_data = dict()
    for el in dictionary[key]:
        for let in list_el:
            if let in el:
                d = {el[0]: el[1:] for i in range(0, len(list_el))}
                bilans_data.update(d)
    return bilans_data


def make_dict(list_data):
    for el in list_data:
        el = el[1:]
        return {el[i]: el[i+1] for i in range(0, len(el), 2)}

def str_to_bool(string):
        return string == 'true'

def get_value(dic, key):
    value = dic.get(key, None)
    if value is None:
        return 0
    return value[1]

def parse_txt(text):

    elements = {}
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
    nip_el = root.findall('.//tns:P_1D', my_namespaces)

    #NIP
    if nip_el:
        elements["nip"] = [el.text.strip() for el in nip_el][0]
    
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
    bilans_data = calculation_dict(elements, "Bilans", ["Aktywa", "Pasywa_A"])
    aktywa_razem = get_value(bilans_data, "Aktywa")
    kapital_fundusz_wlasny = get_value(bilans_data, "Pasywa_A")
    
    elements['rzis'] = data_list('tns:RZiS', root)
    elements["zmiany"] = data_list('tns:ZestZmianWKapitale', root)
    elements["rachunek"] = data_list('tns:RachPrzeplywow', root)

    ##CALCULATING RESULTS
    report_data = calculation_dict(elements, 'rzis',[ "F", "I", "L", "A", "A_II", "A_III", "E", "D", "G"])
    zysk_strata_z_dz_operacyjnej = get_value(report_data,"F")
    zysk_strata_brutto = get_value(report_data, "I")
    zysk_strata_netto = get_value(report_data,"L")
    przychody_netto_ze_sprzedazy = get_value(report_data, "A")
    zmiana_stanu_produktow = get_value(report_data, "A_II")
    koszt_wytworzenia_na_wlasne_potrzeby = get_value(report_data, "A_III")
    pozostale_koszty_operacyjne = get_value(report_data, "E")
    pozostale_przychody_operacyjne = get_value(report_data, "D")
    przychody_finansowe = get_value(report_data, "G")
    
    divided_by = (float(przychody_netto_ze_sprzedazy)-float(zmiana_stanu_produktow)-float(koszt_wytworzenia_na_wlasne_potrzeby)+float(pozostale_przychody_operacyjne)) 
    marza_operacyjna = (float(zysk_strata_z_dz_operacyjnej)*100)/divided_by
    elements['marza_operacyjna'] = marza_operacyjna

    div = (divided_by + float(przychody_finansowe))
    marza_zysku_brutto = (float(zysk_strata_brutto)*100)/div
    elements['marza_zysku_brutto'] = marza_zysku_brutto

    rentownosc_aktywow = (float(zysk_strata_netto)*100) / float(aktywa_razem)
    elements['rentownosc_aktywow'] = rentownosc_aktywow
    rentownosc_kapilu_wlasnego = (float(zysk_strata_netto)*100/float(kapital_fundusz_wlasny))
    elements['rentownosc_kapitalu_wlasnego'] = rentownosc_kapilu_wlasnego
    
    return elements