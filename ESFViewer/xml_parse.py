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
        self.bilans_data = self.data_list(self._bilans)
        self.rzis_data = self.data_list(self._rzis)
        self.zestawienie_zmian_data = self.convert_to_dict(self._zestawienie_zmian)
        self.rachunek_przeplywow_data = self.convert_to_dict(self._rachunek_przeplywow)
        self.method = self.get_method()

        if self.get_entity_type() in self.__class__.AVAILABLE_TYPES:
            self.wprowadzenie_data = self.wprowadzenie_data_PKD()
        else:
            self.wprowadzenie_data = self.wprowadzenie_data_wo_PKD()


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

    def get_mapping_dic(self):
        if self.get_method() == 'RZiSPor':
            return element_mappings.bilans_rzis_dict
        return element_mappings.bilans_rzis_kalk
       
    def data_list(self, main_node):
        data = []
        unit = []
        if main_node is self._bilans or main_node is self._rzis:
            dictionary = self.get_mapping_dic()
        if main_node is self._zestawienie_zmian:
            dictionary = element_mappings.zmiany_dict
        if main_node is self._rachunek_przeplywow:
            dictionary = element_mappings.rachunek_dict
        if self.get_entity_type() in ['JednostkaMikro'] and main_node is self._rzis:
            dictionary = element_mappings.rzis_male_mikro 
        for node in main_node.descendants:
            if node.name is not None:
                if node.string is None:
                    unit = list((dictionary.get(node.name, node.name),))
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
                if re.match(r'P_1[A]', node.name) or re.match(r'Adres.?', node.name) or re.match(r'P_[35678]$', node.name):
                    for n in node.descendants:
                        if n.name and n.string:
                            inner_dict[n.name] = inner_dict.get(n.name, "") + n.string.strip().replace(u'\xa0', u' ') + " "
                    main_dict[mapp.get(node.name, node.name)] = inner_dict
        return main_dict


    def dict_lookup(self, dictionary, value):
        lookup_value = dictionary.get(value, None)
        if lookup_value is not None:
            return float(lookup_value.get('KwotaA'))
        return 0

    def marzy_wariant_porownawczy(self):
        rzis_dictionary = self.convert_to_dict(self._rzis)
        if self.get_entity_type() not in ['JednostkaMikro']:
            zysk_dz_op =  self.dict_lookup(rzis_dictionary,'Zysk (strata) z działalności operacyjnej (C+D–E)')
            przych_net_sprz = self.dict_lookup(rzis_dictionary, 'Przychody netto ze sprzedaży i zrównane z nimi, w tym:' )
            zmiana_stanu_prod = self.dict_lookup(rzis_dictionary, '● Zmiana stanu produktów (zwiększenie – wartość dodatnia, zmniejszenie – wartość ujemna)')
            koszt_wytw_swiad = self.dict_lookup(rzis_dictionary, '● Koszt wytworzenia produktów na własne potrzeby jednostki') ## make sure it is the right node    
            poz_przych_op = self.dict_lookup(rzis_dictionary, 'Pozostałe przychody operacyjne')
            
            
            zysk_str_br = self.dict_lookup(rzis_dictionary, 'Zysk (strata) brutto (F+G–H)')
            przych_fin = self.dict_lookup(rzis_dictionary, 'Przychody finansowe')    
            zysk_strata_netto = self.dict_lookup(rzis_dictionary, 'Zysk (strata) netto (I–J–K)')
        else:
            przych_net_sprz = self.dict_lookup(rzis_dictionary, 'Przychody podstawowej działalności operacyjnej i zrównane z nimi')
            zmiana_stanu_prod = self.dict_lookup(rzis_dictionary, '● Zmiana stanu produktów, zwiększenie - wartość dodatnia, zmniejszenie - wartość ujemna')
            koszt_wytw_swiad = self.dict_lookup(rzis_dictionary, '● Koszt wytworzenia produktów na własne potrzeby jednostki')
            poz_przych_op = self.dict_lookup(rzis_dictionary, 'Pozostałe przychody operacyjne')
            zysk_str_br = self.dict_lookup(rzis_dictionary, 'Zysk (strata) brutto (F+G–H)')
            przych_fin = self.dict_lookup(rzis_dictionary, 'Przychody finansowe')  
            
            zysk_strata_netto = self.dict_lookup(rzis_dictionary, 'Zysk/strata netto (A-B+C-D-E) (dla jednostek mikro, o których mowa w art. 3 ust. 1a pkt 1, 3 i 4 oraz ust. 1b ustawy)')

        
        divider = przych_net_sprz - zmiana_stanu_prod - koszt_wytw_swiad + poz_przych_op
        try:
            marza_operacyjna = (zysk_dz_op *100) / divider
        except:
            marza_operacyjna = None

        try: 
            marza_brutto = (zysk_str_br*100)/ (divider + przych_fin)
        except: 
            marza_brutto = None


        return marza_operacyjna, marza_brutto, zysk_strata_netto 

    def marzy_wariant_kalkulacujny(self):
        rzis_dictionary = self.convert_to_dict(self._rzis)
        zysk_dz_op = self.dict_lookup(rzis_dictionary, 'Zysk (strata) z działalności operacyjnej (F+G–H)')
        przych_net_sprz = self.dict_lookup(rzis_dictionary, 'Przychody netto ze sprzedaży produktów, towarów i materiałów, w tym:')
        poz_przych_op = self.dict_lookup(rzis_dictionary, 'Pozostałe przychody operacyjne')
        divider = przych_net_sprz + poz_przych_op

        zysk_str_br = self.dict_lookup(rzis_dictionary, 'Zysk (strata) brutto (I+J–K)')
        przych_fin = self.dict_lookup(rzis_dictionary, 'Przychody finansowe')
        
        if self.get_entity_type() not in ['JednostkaMala','JednostkaMikro']:
            zysk_strata_netto = self.dict_lookup(rzis_dictionary, 'Zysk (strata) netto (L–M–N)')
        else:
            zysk_strata_netto = self.dict_lookup(rzis_dictionary, 'Zysk/strata netto (A-B+C-D-E) (dla jednostek mikro, o których mowa w art. 3 ust. 1a pkt 1, 3 i 4 oraz ust. 1b ustawy)')
    
        
        try:
            marza_operacyjna =  (zysk_dz_op*100) / divider

        except:
            marza_operacyjna = None

        try:
            marza_brutto = (zysk_str_br*100) /(divider + przych_fin)
        except: 
            marza_brutto = None

        return marza_operacyjna, marza_brutto, zysk_strata_netto



    def rentownosc(self):
        bilans_dic = self.convert_to_dict(self._bilans)
      
        
        aktywa_razem = self.dict_lookup(bilans_dic, 'Aktywa')


        kapital_fundusz_wlasny = self.dict_lookup(bilans_dic, '● Kapitał (fundusz) własny')
        if self.method == 'RZiSPor':
            zysk_strata_net = self.marzy_wariant_porownawczy()[2]
        else:
            zysk_strata_net = self.marzy_wariant_kalkulacujny()[2]

        try:
            rentownosc_aktywow = (zysk_strata_net*100)/ aktywa_razem
        except:
            rentownosc_aktywow = None

        try:
            rentownosc_kapilu_wlasnego = (zysk_strata_net*100)/kapital_fundusz_wlasny
        except:
            rentownosc_kapilu_wlasnego = None
        
        return rentownosc_aktywow, rentownosc_kapilu_wlasnego

    def marza_operacyjna(self):
        if self.method == "RZiSPor":
            return self.marzy_wariant_porownawczy()[0]
        return self.marzy_wariant_kalkulacujny()[0]   

    def marza_zysku_brutto(self):
        if self.method == "RZiSPor":
            return self.marzy_wariant_porownawczy()[1]
        return self.marzy_wariant_kalkulacujny()[1]
    
    def rentownosc_aktywow(self):
        return self.rentownosc()[0]

    def rentownosc_kapilu_wlasnego(self):
        return self.rentownosc()[1]
    

    def data(self):
        el = {}
        el['Naglowek'] = self.naglowek_data
        el['Wprowadzenie'] = self.wprowadzenie_data
        el['Bilans'] = self.bilans_data
        el['RZiS'] = self.rzis_data
        el['ZestawienieZmian'] = self.zestawienie_zmian_data 
        el['RachunekPrzeplywow'] = self.rachunek_przeplywow_data
        return el


       



def parse_txt(text):
    
    instance = FinancialStatement(text)
    #print(instance.get_entity_type())
    data = instance.data()
    data['marza_operacyjna'] = instance.marza_operacyjna()
    data['marza_zysku_brutto'] = instance.marza_zysku_brutto()
    data['rentownosc_aktywow'] = instance.rentownosc_aktywow()
    data['rentownosc_kapitalu_wlasnego'] = instance.rentownosc_kapilu_wlasnego()
    return data



