# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 14:39:01 2022

@author: NLNIEM

Duikertool
"""

import math
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

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
    with st.expander('Percentage ondergronds'):
        if st.checkbox('Hulp', value=False, key='Percentage ondergronds'):
            st.image(Image.open('DiaDuiker.jpg'),
                     caption='Dia Duiker')
        KeuzePerOndergrond2 = st.selectbox('Keuze: cm sliblaag in duiker of percentage ondergronds?', 
                                          options = ('cm sliblaag','Percentage ondergronds'), 
                                          index=1, key = 'PerOndergrond2')
        if KeuzePerOndergrond2 == 'Percentage ondergronds':
            PerOndergrond1 = st.number_input(label='Percentage ondergronds [%]',
                            value= 10, min_value=0, max_value=100)
            PerOndergrond = PerOndergrond1/100
        elif KeuzePerOndergrond2 == 'cm sliblaag':
            cmOndergrond = st.number_input(label='cm sliblaag [cm]',
                            value= 0, min_value=0, max_value= int(diameter*100))
            PerOndergrond = float((cmOndergrond/100) / diameter)
    # Intreedweerstand
    with st.expander("In- en uitreedweerstand"):
        if st.checkbox('Hulp', value=False, key='intreedweerstand'):
            st.write('Gebuik onderstaand figuur voor het bepalen van de intreedweerstand')
            st.write('Standaardwaarde intreedweerstand = 0.4')
            st.image(Image.open('EiWaardes.jpg'),
                     caption='Ei-waarden')
            st.write('Standaardwaarde uitreedweerstand = 1.0')
        intreedweerstand = st.number_input(label='Intreedweerstand [dimensieloos]',
                                           format="%.2f",value= 0.40)
        uittreedweerstand = st.number_input(label='Uittreedweerstand [dimensieloos]',
                                            format="%.2f",value = 1.00) 
    # Natte oppervlak benedenstrooms
    with st.expander("Natte oppervlak benedenstrooms"):
        if st.checkbox('Hulp', value=False, key='BenStrNatOpp'):
            st.write('Schat natte oppervlak O.B.V.profiel watergang en peil')
        BenStrNatOpp = st.number_input(label='Natte oppervlak benedenstrooms',
                        format="%.2f", value= 5.00)
    # Manning
    with st.expander("Hydraulische weerstand"):
        if st.checkbox('Hulp', value=False, key='Hydraulische weerstand'):
            st.write('Hydraulische weerstand wordt in Manning uitgedrukt')
            st.write('Gebuik onderstaand tabel voor het bepalen van de hydraulische weerstand')
            st.image(Image.open('kWaardem.jpg'),
                     caption='k-Waardem')
        Manning = st.number_input(label='Manning [s∙m ^-1/3]',
                value= 75)
    with st.expander("Verval over duiker"):
        KeuzeVerval = st.selectbox('Keuze: Verval of hoogte in +mNAP', 
                                    options = ('Verval','Werkelijke hoogte in +mNAP'),
                                    index=0)
        if KeuzeVerval == 'Verval':
            # Verval
            verval_cm = st.number_input(label='Verval [cm]',format="%.1f",
                            value= 5.00)
            verval = verval_cm / 100
            # Boven- en benedenwaterstand
            benedenwaterstand = 0
            bovenwaterstand = verval
        elif KeuzeVerval == 'Werkelijke hoogte in +mNAP':
            # Bovenwaterstand
            bovenwaterstand = st.number_input(label='Bovenwaterstand [+mNAP]',format="%.2f",
                            value= 0.05)
            # Benedenwaterstand
            benedenwaterstand = st.number_input(label='Benedenwaterstand [+mNAP]',format="%.2f",
                            value= 0.00, min_value=0.00, max_value=bovenwaterstand)             
    
    return (diameter, lengte, PerOndergrond, intreedweerstand, uittreedweerstand,
            BenStrNatOpp, Manning, bovenwaterstand, benedenwaterstand,
            KeuzePerOndergrond2, KeuzeVerval)

## Visualisatie:
# ===================================
def DuikerVisualisatie(Intreedweerstand, Manning, Uittreedweerstand,
                       Bovenwaterstand, Diameter, Benedenwaterstand,
                       Verval, Lengte, Sliblaag, KeuzePerOndergrond2, 
                       KeuzeVerval):
    # get an image
    with Image.open("DuikerSchematisch_V2.jpg").convert("RGBA") as base:
    
        # make a blank image for the text, initialized to transparent text color
        txt = Image.new("RGBA", base.size, (255, 255, 255, 0))
    
        # get a font
        fnt = ImageFont.truetype(font='arial.TTF', size=20, index=0, encoding='', layout_engine=None)

        # get a drawing context
        d = ImageDraw.Draw(txt)
    
        # draw text, half opacity
        d.text((760, 280), f'Diameter: {Diameter} [m]', font=fnt, fill=(0,0,0,1000))                            # Diameter
        d.text((650, 360), f'Lengte: {Lengte} [m]', font=fnt, fill=(0,0,0,1000))                                # Lengte duiker
        if KeuzePerOndergrond2 == 'Percentage ondergronds':
            d.text((1150, 345), f'Sliblaag: {Sliblaag} [%]', font=fnt, fill=(0,0,0,1000))                        # Sliblaag
        elif KeuzePerOndergrond2 == 'cm sliblaag':
            d.text((1150, 345), f'Sliblaag: {Sliblaag} [cm]', font=fnt, fill=(0,0,0,1000))                       # Sliblaag
        d.text((400, 17),  f'Intreedweerstand: {Intreedweerstand}', font=fnt, fill=(0,0,0,1000))                # Intreedweerstand
        d.text((950, 17),  f'Uittreedweerstand: {Uittreedweerstand}', font=fnt, fill=(0,0,0,1000))              # Uittreedweerstand
        d.text((670, 17),  f'Manning: {Manning}', font=fnt, fill=(0,0,0,1000))                                  # Manning
        if KeuzeVerval == 'Verval':
            d.text((210, 200), 'Bovenwaterstand: N.V.T.', font=fnt, fill=(0,0,0,1000))                          # Bovenwaterstand
            d.text((1120, 180), 'Benedenwaterstand: N.V.T.', font=fnt, fill=(0,0,0,1000))                        # Benedenwaterstand
            d.text((1060, 300), f'Verval: {Verval} [cm]', font=fnt, fill=(0,0,0,1000))                           # Verval Duiker
        elif KeuzeVerval == 'Werkelijke hoogte in +mNAP':
            d.text((210, 200), f'Bovenwaterstand: {Bovenwaterstand} [+mNAP]', font=fnt, fill=(0,0,0,1000))      # Bovenwaterstand
            d.text((1120, 180), f'Benedenwaterstand: {Benedenwaterstand} [+mNAP]', font=fnt, fill=(0,0,0,1000))  # Benedenwaterstand
            d.text((1060, 300), 'Verval: N.V.T', font=fnt, fill=(0,0,0,1000))                                    # Verval Duiker
            
        out = Image.alpha_composite(base, txt)
        buff = io.BytesIO()
        out.save(buff, format='PNG')
        return buff
      
## Layout:
# ===================================
st.markdown("<h1 style='text-align: right; color: black; font-size:10px;'>Geproduceerd door: Niels van der Maaden</h1>", unsafe_allow_html=True)
#st.write('Geproduceerd door: Niels van der Maaden')
st.image(Image.open('WRIJ_Sweco.jpg'))
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
    st.image(Image.open(DuikerVisualisatie(invoer[3], invoer[6], invoer[4],
                                           invoer[7], invoer[0], invoer[8],
                                           invoer[7], invoer[1], invoer[2], 
                                           invoer[9], invoer[10])))
    st.markdown("<h1 style='text-align: left; color: black; font-size:30px;'>Resultaten</h1>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align: left; color: black; font-size:20px;'>Debiet: {round(duiker.Debiet(),3)} [m3/s]</h1>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align: left; color: black; font-size:20px;'>Stroomsnelheid: {round(duiker.Stroomsnelheid(),2)} [m/s]</h1>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align: left; color: black; font-size:20px;'>Opstuwing: {round(duiker.Opstuwing(),2)} [m]</h1>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align: left; color: black; font-size:20px;'>Hydraulische ruwheid: {round(duiker.Ruw(),3)}</h1>", unsafe_allow_html=True)
