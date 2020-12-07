import xml.etree.ElementTree as ET

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


def tags_to_dict(parent_node):
    if parent_node:
        data = dict()
        data_1 = dict()
        for child in parent_node.iter():
            tag = child_namespace_removal(child)
            if tag in data:
                data_1[tag] = child.text.strip()
            else:
                data[tag] = child.text.strip()
            if data[tag] == '':
                data.pop(tag, None)
        if data_1:
            return (data, data_1)
        else:
            return (data,)
    return None

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

def parse_txt(text):
    
    root = ET.fromstring(text)
    document_info = root.find('tns:Naglowek', my_namespaces)
    elements = dict()
    elements["naglowek"] = tags_to_dict(document_info)
    intro = root.find('tns:WprowadzenieDoSprawozdaniaFinansowego', my_namespaces)
    

    el_p1 = intro.find('tns:P_1', my_namespaces)
    el_p1A = el_p1.find('tns:P_1A', my_namespaces)
    elements["siedziba"] = tags_to_dict(el_p1A)
    el_p1b = el_p1.find('tns:P_1B', my_namespaces)
    elements['adres'] = tags_to_dict(el_p1b)





    el_p1c = el_p1.find('tns:P_1C', my_namespaces)
    elements["pkd"] = [pkd.strip() for pkd in el_p1c.itertext() if pkd.strip()]
    elements["nip"] = el_p1.find('tns:P_1D', my_namespaces).text.strip()
    krs = el_p1.find('tns:P_1E', my_namespaces)
    if krs is not None:
        elements['krs']= el_p1.find('tns:P_1E', my_namespaces).text.strip()
    else:
        elements['krs'] = None
    elements['czas_dzialalnosci_jezeli_ograniczony'] = intro.find('tns:P_2', my_namespaces)
    okres_sprawozdania = intro.find('tns:P_3', my_namespaces)
    elements["okres_sprawozdania"] = tags_to_dict(okres_sprawozdania)
    dane_laczne = intro.find('tns:P_4', my_namespaces).text.strip()
    if dane_laczne=='true':
        dane_laczne = True
    else:
        dane_laczne=False
    elements["dane_laczne"] = dane_laczne


    kontunuacja_dzialalnosci = intro.find('tns:P_5', my_namespaces)
    kontunuacja_dzialalnosci = tags_to_dict(kontunuacja_dzialalnosci)
    kontunuacja_dzialalnosci = kontunuacja_dzialalnosci[0]
    if kontunuacja_dzialalnosci.get('P_5A') == 'true':
        kontunuacja_dzialalnosci['P_5A'] = True
    else:
        kontunuacja_dzialalnosci['P_5A'] = False

    if kontunuacja_dzialalnosci.get('P_5B') == 'true':
        kontunuacja_dzialalnosci['P_5B'] = True
    else:
        kontunuacja_dzialalnosci['P_5B'] = False

    elements["kontynuacja_dzialalnosci"] = kontunuacja_dzialalnosci


    polaczenie_spolek = intro.find('tns:P_6')
    elements["info_o_polaczeniu"] = tags_to_dict(polaczenie_spolek)
    zasady = intro.find('tns:P_7', my_namespaces)
    zasady_text = ""
    for el in zasady.itertext():
        zasady_text = zasady_text + el.strip().replace(u'\xa0', u' ')

    elements['zasady'] = zasady_text
    zalozenia = intro.find('tns:P_8', my_namespaces)
    elements["zalozenia"] = tags_to_dict(zalozenia)

    #Financial statement data
    elements["Bilans"] = data_list('tns:Bilans', root)
    elements['rzis'] = data_list('tns:RZiS', root)
    elements["zmiany"] = data_list('tns:ZestZmianWKapitale', root)
    elements["rachunek"] = data_list('tns:RachPrzeplywow', root)
    
    return elements

    

