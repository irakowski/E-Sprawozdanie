import re
from bs4 import BeautifulSoup
from . import element_mappings
from . import validators

class FinancialStatement:
    AVAILABLE_TYPES = (
		'JednostkaInna',
		'JednostkaOp', 
	)
    
    def __init__(self, xml_text):
        self.xml_text = xml_text
        self.soup = self._cook()
        #Nodes
        self._naglowek = self.soup.find('Naglowek')
        self._wprowadzenie = self._naglowek.find_next_sibling()
        self._bilans = self._wprowadzenie.find_next_sibling()
        self._rzis = self._bilans.find_next_sibling()
        self._zestawienie_zmian =self.soup.find(re.compile("ZestZmianWKapit.*"))
        self._rachunek_przeplywow = self.soup.find(re.compile("RachPrzeplyw.*"))
        
        #common structure for all documents
        self.naglowek_data = self.simple_dict(self.data_list(self._naglowek))
        self.bilans_data = self.convert_to_dict(self._bilans)
        self.rzis_data = self.convert_to_dict(self._rzis)
        self.zestawienie_zmian_data = self.convert_to_dict(self._zestawienie_zmian)
        self.rachunek_przeplywow_data = self.convert_to_dict(self._rachunek_przeplywow)

        if self.get_entity_type() in self.__class__.AVAILABLE_TYPES:
            self.wprowadzenie_data = self.wprowadzenie_data_PKD()
        else:
            self.wprowadzenie_data = self.wprowadzenie_data_wo_PKD()
        #calculaion method
        self.method = self.get_method()

    def _cook(self):
        soup = BeautifulSoup(self.xml_text, 'lxml-xml')
        return soup
    
    def get_entity_type(self):
        return self.soup.contents[0].name
        #Naglowek.KodSpawozdania ##'SprFinJednostkaInnaWZlotych'

    def get_method(self):   
        porow = re.search(r'((p|P)orówn)|(RZiSPor)',str(self.soup))
        if porow:
            return 'RZiSPor'
        
    def data_list(self, main_node):
        data = []
        unit = []
        for node in main_node.descendants:
            if node.name is not None:
                if node.string is None:
                    unit = list((node.name,))
                    data.append(unit)
                else:
                    unit.extend([node.name, node.string.strip().replace(u'\xa0', u' ')])
        if data:
            return data
        return unit

    def simple_dict(self, lst):
        """
        Iterates throught given list where len(list)%2 == 0 and returns a dictionary  
        """
        return {lst[i]: lst[i + 1] for i in range(0, len(lst), 2)}

    def convert_to_dict(self, node):
        if node is not None:
            l = self.data_list(node)
            container = {}
            for node in l:
                if len(node) > 1:
                    container[node[0]] = self.simple_dict(node[1:])
            return container
        return ""
    
    def wprowadzenie_data_PKD(self):
        """
        Iterates throught wprowadzenie 
        """
        main_dict = dict()
        mapp = {'P_1A': 'Nazwa_siedziba','P_1C': 'PKD','P_1D': 'NIP','P_1E': 'KRS', 'P_2':'OgranicCzasDzialalnosci',
                'P_3':'ZakresDat','P_4': 'SprFinDaneLaczne', 'P_5': 'KontynuacjaDzialalnosci',
                'P_6': 'SprFinPoPolaczeniu', 'P_7': 'Zasady', 
                'P_8': 'Zalożenia'}
        for node in self._wprowadzenie.descendants:
            inner_dict = {}
            if node.name:
                if re.match(r'P_[14][DE]*', node.name):
                    main_dict[mapp.get(node.name, node.name)] = node.string
                if re.match(r'P_1[CA]', node.name) or re.match(r'Adres.?', node.name) or re.match(r'P_[235678]$', node.name):
                    for n in node.descendants:
                        if n.name and n.string:
                            inner_dict[n.name] = inner_dict.get(n.name, "") + n.string.strip().replace(u'\xa0', u' ') + " "
                    main_dict[mapp.get(node.name, node.name)] = inner_dict
        return main_dict

    def wprowadzenie_data_wo_PKD(self):
        """
        Iterates throught wprowadzenie 
        """
        main_dict = dict()
        mapp = {'P_1A': 'Nazwa_siedziba','P_1C': 'NIP','P_1D': 'KRS','P_3':'ZakresDat',
                'P_4': 'Uproszczenia', 'P_5': 'Kontynuacja','P_6': 'Zasady'}
        for node in self._wprowadzenie.descendants:
            inner_dict = {}
            if node.name:
                if re.match(r'P_[14][CD]*', node.name):
                    main_dict[mapp.get(node.name, node.name)] = node.string
                if re.match(r'P_1[A]', node.name) or re.match(r'Adres.?', node.name) or re.match(r'P_[345678]$', node.name):
                    for n in node.descendants:
                        if n.name and n.string:
                            inner_dict[n.name] = inner_dict.get(n.name, "") + n.string.strip().replace(u'\xa0', u' ') + " "
                    main_dict[mapp.get(node.name, node.name)] = inner_dict
        return main_dict

    def data(self):
        el = {}
        el['Naglowek'] = self.naglowek_data
        el['Wprowadzenie'] = self.wprowadzenie_data
        el['Bilans'] = self.bilans_data
        el['RZiS'] = self.rzis_data
        el['ZestawienieZmian'] = self.zestawienie_zmian_data 
        el['RachunekPrzeplywow'] = self.rachunek_przeplywow_data
        return el

    def dict_lookup(self, dictionary, value):
        lookup_value = dictionary.get(value, None)
        if lookup_value is not None:
            return float(lookup_value.get('KwotaA'))
        return 0

    def marzy(self):
        zysk_strata_z_dz_operacyjnej = self.dict_lookup(self.rzis_data, 'F')
        zysk_strata_brutto = self.dict_lookup(self.rzis_data, 'I')
        zysk_strata_netto = self.dict_lookup(self.rzis_data, 'L')
        przychody_netto_ze_sprzedazy = self.dict_lookup(self.rzis_data, 'A')
        zmiana_stanu_produktow = self.dict_lookup(self.rzis_data, 'A_II')
        koszt_wytworzenia_na_wlasne_potrzeby = self.dict_lookup(self.rzis_data, 'A_III')
        pozostale_koszty_operacyjne = self.dict_lookup(self.rzis_data,'E')
        pozostale_przychody_operacyjne = self.dict_lookup(self.rzis_data, 'D')
        przychody_finansowe = self.dict_lookup(self.rzis_data, 'G')
        if self.method == 'RZiSPor':
            divider_1 = przychody_netto_ze_sprzedazy-zmiana_stanu_produktow-koszt_wytworzenia_na_wlasne_potrzeby
            divider_2 = divider_1+pozostale_przychody_operacyjne
            try:
                marza_operacyjna = zysk_strata_z_dz_operacyjnej*100/divider_2
            except:
                marza_operacyjna = None

            try:
                marza_zysku_brutto = (zysk_strata_brutto*100) / (divider_2 + przychody_finansowe)
            except:
                marza_zysku_brutto = None
        else:
            try:
                marza_operacyjna = zysk_strata_z_dz_operacyjnej*100/ (przychody_netto_ze_sprzedazy+pozostale_przychody_operacyjne)
            except:
                marza_operacyjna = None
            try:
                marza_zysku_brutto = (zysk_strata_brutto*100)/(przychody_netto_ze_sprzedazy + pozostale_przychody_operacyjne + przychody_finansowe)
            except:
                marza_zysku_brutto = None
        return marza_operacyjna, marza_zysku_brutto

    def marza_operacyjna(self):
        return self.marzy()[0]
    
    def marza_zysku_brutto(self):
        return self.marzy()[1]

    def rentownosc_aktywow(self):
        zysk_strata_netto = self.dict_lookup(self.rzis_data, 'L')
        aktywa_razem = self.dict_lookup(self.bilans_data, 'Aktywa')
        try:
            return zysk_strata_netto*100/ aktywa_razem
        except:
            return None
    
    def rentownosc_kapilu_wlasnego(self):
        zysk_strata_netto = self.dict_lookup(self.rzis_data, 'L')
        kapital_fundusz_wlasny = self.dict_lookup(self.bilans_data, 'Pasywa_A')
        try:
            return zysk_strata_netto*100/kapital_fundusz_wlasny
        except:
            return None


def parse_txt(text):
    
    instance = FinancialStatement(text)
#    print(instance.get_entity_type())
#    print(instance.method)
    data = instance.data()
    data['marza_operacyjna'] = instance.marza_operacyjna()
    data['marza_zysku_brutto'] = instance.marza_zysku_brutto()
    data['rentownosc_aktywow'] = instance.rentownosc_aktywow()
    data['rentownosc_kapitalu_wlasnego'] = instance.rentownosc_kapilu_wlasnego()
    return data



