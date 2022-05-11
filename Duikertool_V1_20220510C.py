# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 14:39:01 2022

@author: NLNIEM

Duikertool
"""

import math
import streamlit as st
from PIL import Image

## Algemene configuratie streamlit:
# ===================================
st.set_page_config(page_title= 'Duiker Tool',   # Titel
                   page_icon=':bar_chart:',     # Pagina icoon
                   layout='centered')           # wide = full-screen

## Duiker tool
# ============================================================================= 
class DuikerTool:
    
    ## Initialiseren:
    # ===================================
    def __init__(self,diameter,lengte,PerOndergrond,intreedweerstand,
                 uittreedweerstand,BenStrNatOpp,Manning,
                 bovenwaterstand,benedenwaterstand):
        
        # Variabelen ronde duiker
        self.diameter = diameter
        
        # Variabelen Algemeen 
        #self.vorm = vorm
        self.lengte = lengte
        self.PerOndergrond = PerOndergrond
        self.intreedweerstand = intreedweerstand
        self.uittreedweerstand = uittreedweerstand
        self.BenStrNatOpp = BenStrNatOpp
        self.Manning = Manning
        self.bovenwaterstand = bovenwaterstand
        self.benedenwaterstand = benedenwaterstand
         
    ## Oppervlak onder de grond:
    # ===================================
    def Opp(self):
        r = self.diameter/2                             # Straal
        d = r - (self.diameter * self.PerOndergrond)    # Afstand midden tot koorde 
        k = 2 * (r**2 - d**2)**0.5                      # Koorde 
        if d < 0:
            return print('D is kleiner dan 0!')
        else:
            opp = r**2 *  math.asin((k/2)/r) - (0.5 * k * d) # Oppervlak onder de grond
            return opp
   
    ## Hydraulische ruwheid:
    # ===================================
    def Ruw(self):
        NatOppDuiker = ((self.diameter/2)**2 * 3.14) - DuikerTool.Opp(self)         # Natte oppervlak duiker    
        Chezy = self.Manning * (NatOppDuiker/(2 * 3.14 * (self.diameter/2)))**(1/6) # Chezy coefficient
        Ei = self.intreedweerstand                                                  # Intreedverlies
        E0 = self.uittreedweerstand * (1- (NatOppDuiker/self.BenStrNatOpp))**2      # Uitreedverlies
        Ef = (2 * 9.81 * self.lengte) / (Chezy**2 * (self.diameter/4))              # Wrijvingsverlies
        mu = (Ei + E0 + Ef)**-0.5                                                   # Totaal weerstand
        return mu
    
    ## Opstuwing:
    # ===================================
    def Opstuwing(self):
        opstuwing = self.bovenwaterstand - self.benedenwaterstand   # Opstuwing
        return opstuwing
    
    ## Debiet:
    # ===================================
    def Debiet(self):
        mu = DuikerTool.Ruw(self)                                           # Totaal weerstand
        NatOppDuiker = ((self.diameter/2)**2 * 3.14) - DuikerTool.Opp(self) # Natte oppervlak duiker
        opstuwing = DuikerTool.Opstuwing(self)                              # Opstuwing
        debiet = mu * NatOppDuiker * (2 * 9.81 * opstuwing)**0.5            # Debiet
        return debiet
    
    ## Stroomsnelheid:
    # ===================================
    def Stroomsnelheid(self):
        NatOppDuiker = ((self.diameter/2)**2 * 3.14) - DuikerTool.Opp(self) # Natte oppervlak duiker
        stroomsnelheid = DuikerTool.Debiet(self)/NatOppDuiker               # Stroomsnelheid in duiker
        return stroomsnelheid

# =============================================================================
# streamlit run C:/Users/NLNIEM/Desktop/Werk/3_Python/1_DuikerTool/Duikertool_V1_20220511.py
# =============================================================================

## GUI
# =============================================================================

## Input:
# ===================================
def InvoerBox():
    # Diameter
    diameter = st.number_input(label='Diameter [meter]',format="%.2f",
                    value= 0.50, min_value=0.10)
    # Lengte
    lengte = st.number_input(label='Lengte [meter]',format="%.2f",
                    value=21.00, min_value=0.10, max_value=999.00)
    # Percentage ondergronds
    with st.expander("Hulp percentage ondergronds"):
        st.image(Image.open('C:/Users/NLNIEM/Desktop/Werk/3_Python/1_DuikerTool/DiaDuiker.jpg'),
                 caption='Dia Duiker')
    PerOndergrond = st.number_input(label='Percentage ondergronds',format="%.2f",
                    value= 0.10, min_value=0.00, max_value=diameter)
    # Intreedweerstand
    with st.expander("Hulp intreedweerstand"):
        st.write('Gebuik onderstaand figuur voor het bepalen van de intreedweerstand')
        st.write('Standaardwaarde = 0.4')
        st.image(Image.open('C:/Users/NLNIEM/Desktop/Werk/3_Python/1_DuikerTool/EiWaardes.jpg'),
                 caption='Ei-waarden')
    intreedweerstand = st.number_input(label='Intreedweerstand [dimensieloos]',
                                       format="%.2f",value= 0.40)
    # Uittreedweerstand
    with st.expander("Hulp uittreedweerstand"):
        st.write('Standaardwaarde = 1.0')
    uittreedweerstand = st.number_input(label='Uittreedweerstand [dimensieloos]',
                                        format="%.2f",value = 1.00) 
    # Natte oppervlak benedenstrooms
    with st.expander("Hulp natte oppervlak benedenstrooms"):
        st.write('Schat natte oppervlak O.B.V.profiel watergang en peil')
    BenStrNatOpp = st.number_input(label='Natte oppervlak benedenstrooms',
                    format="%.2f", value= 5.00)
    # Manning
    with st.expander("Hulp hydraulische weerstand"):
        st.write('Hydraulische weerstand wordt in Manning uitgedrukt')
        st.write('Gebuik onderstaand tabel voor het bepalen van de hydraulische weerstand')
        st.image(Image.open('C:/Users/NLNIEM/Desktop/Werk/3_Python/1_DuikerTool/kWaardem.jpg'),
                 caption='k-Waardem')
    Manning = st.number_input(label='Manning [s∙m ^-1/3]',step=0.1,format="%.2f",
                    value= 75.00)
    # Bovenwaterstand
    bovenwaterstand = st.number_input(label='Bovenwaterstand',step=0.1,format="%.2f",
                    value= 0.05)
    # Benedenwaterstand
    benedenwaterstand = st.number_input(label='Benedenwaterstand',format="%.2f",
                    value= 0.00, min_value=0.00, max_value=bovenwaterstand)
    return diameter,lengte,PerOndergrond,intreedweerstand,uittreedweerstand,BenStrNatOpp,Manning,bovenwaterstand,benedenwaterstand

## Layout:
# ===================================
st.markdown("<h1 style='text-align: right; color: black; font-size:10px;'>Geproduceerd door: Niels van der Maaden</h1>", unsafe_allow_html=True)
#st.write('Geproduceerd door: Niels van der Maaden')
st.image(Image.open('C:/Users/NLNIEM/Desktop/Werk/3_Python/1_DuikerTool/WRIJ_Sweco.jpg'))
st.markdown('##')
st.title('Duiker tool')
#st.markdown('##')

with st.sidebar:
    invoer = InvoerBox()
    duiker = DuikerTool(invoer[0], invoer[1], invoer[2], 
                        invoer[3], invoer[4], invoer[5], 
                        invoer[6], invoer[7], invoer[8])
## Output:
# ===================================    
with st.container():   
    st.markdown("<h1 style='text-align: left; color: black; font-size:30px;'>Resultaten</h1>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align: left; color: black; font-size:20px;'>Debiet: {round(duiker.Debiet(),3)} [m3/s]</h1>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align: left; color: black; font-size:20px;'>Stroomsnelheid: {round(duiker.Stroomsnelheid(),2)} [m/s]</h1>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align: left; color: black; font-size:20px;'>Opstuwing: {round(duiker.Opstuwing(),2)} [m]</h1>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align: left; color: black; font-size:20px;'>Hydraulische ruwheid: {round(duiker.Ruw(),3)}</h1>", unsafe_allow_html=True)
