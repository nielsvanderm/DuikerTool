from pydantic import BaseModel
import math
import streamlit as st
import plotly.graph_objects as go
from PIL import Image, ImageDraw, ImageFont
import io

## Duiker tool
# ============================================================================= 
class Duiker(BaseModel):
    diameter: float
    lengte: float
    sliblaag_procent: float
    intreedweerstand: float
    uittreedweerstand: float
    ben_str_nat_opp: float
    manning: float
    bovenwaterstand: float
    benedenwaterstand: float
            
    ## Oppervlak onder de grond:
    # ===================================
    @property
    def sliblaag(self):
        # Straal
        r = self.diameter/2 
        # Afstand midden tot koorde                   
        d = r - (self.diameter * self.sliblaag_procent)
        # Koorde 
        k = 2 * (r**2 - d**2)**0.5
        # Oppervlak onder de grond                      
        opp = r**2 *  math.asin((k/2)/r) - (0.5 * k * d) 
        return opp
   
    ## Hydraulische ruwheid:
    # ===================================
    @property
    def ruwheid(self):
        # Natte oppervlak duiker
        nat_opp_duiker = ((self.diameter/2.0)**2.0 * 3.14) - self.sliblaag
        # Chezy coefficient
        chezy = self.manning * (nat_opp_duiker/(2.0 * 3.14 * (self.diameter/2.0)))**(1.0/6.0)
        # Intreedverlies Ei
        Ei = self.intreedweerstand
        # Uitreedverlies E0
        E0 = self.uittreedweerstand * (1.0-(nat_opp_duiker/self.ben_str_nat_opp))**2.0
        # Wrijvingsverlies Ef
        Ef = (2 * 9.81 * self.lengte) / (chezy**2 * (self.diameter/4))
        # Totaal weerstand
        mu = (Ei + E0 + Ef)**-0.5 
        return mu
    
    ## Opstuwing:
    # ===================================
    @property
    def opstuwing(self):
        opstuwing = self.bovenwaterstand - self.benedenwaterstand
        return opstuwing
    
    ## Debiet:
    # ===================================
    @property
    def debiet(self):
        # Totaal weerstand
        mu = self.ruwheid
        # Natte oppervlak duiker
        nat_opp_duiker = ((self.diameter/2.0)**2.0 * 3.14) - self.sliblaag
        # Opstuwing
        opstuwing = self.opstuwing
        # Debiet
        debiet = mu * nat_opp_duiker * (2.0 * 9.81 * opstuwing)**0.5
        return debiet
    
    ## Stroomsnelheid:
    # ===================================
    @property
    def stroomsnelheid(self):
        # Natte oppervlak duiker
        nat_opp_duiker = ((self.diameter/2.0)**2.0 * 3.14) - self.sliblaag
        # Stroomsnelheid in duiker
        stroomsnelheid = self.debiet/nat_opp_duiker
        return stroomsnelheid

    def plotly_figure(self):
        scale_ratio = self.lengte / self.diameter / 2.0
        fig = go.Figure(layout=go.Layout(autosize=True, width=800, height=400,
                                         margin=dict(l=20, r=20, t=20, b=20),
                                         template='simple_white',
                                         yaxis=dict(scaleanchor="x", scaleratio=scale_ratio)))
        water_x = [-self.lengte/2.0-10.0, -self.lengte/2.0-10.0,
                   -self.lengte/2.0, self.lengte/2.0, self.lengte/2.0+10.0, self.lengte/2.0+10.0,
                   self.lengte/2.0, -self.lengte/2.0, -self.lengte/2.0-10.0]
        water_y = [self.bovenwaterstand-self.diameter, self.bovenwaterstand,
                   self.bovenwaterstand, self.benedenwaterstand, self.benedenwaterstand,
                   self.benedenwaterstand-self.diameter, self.benedenwaterstand-self.diameter,
                   self.bovenwaterstand-self.diameter, self.bovenwaterstand-self.diameter]

        fig.add_trace(dict(x=water_x,
                           y=water_y,
                           name='water',
                           line=dict(color='lightblue'),
                           showlegend=True,
                           hoverlabel=dict(namelength=-1),
                           fill='toself'))

        duiker_x = [-self.lengte/2.0, -self.lengte/2.0, self.lengte/2.0, self.lengte/2.0, -self.lengte/2.0]
        duiker_y = [self.bovenwaterstand-self.diameter, self.bovenwaterstand, self.benedenwaterstand,
                    self.benedenwaterstand-self.diameter, self.bovenwaterstand-self.diameter]
        fig.add_trace(dict(x=duiker_x,
                           y=duiker_y,
                           name=f'duiker = {self.lengte}m',
                           line=dict(color='brown'),
                           showlegend=True,
                           hoverlabel=dict(namelength=-1),
                           fill='toself'))
        fig.add_annotation(dict(x=0.0, y=0.0, text=f'DUIKER: {self.debiet:.2f}m³/s'))
        return fig

## GUI
# =============================================================================
   
## Input:
# ===================================
def invoer_sidebar():
    # Diameter
    diameter = st.number_input(label='Diameter [meter]', 
                               format="%.2f",
                               step=1.00,
                               value=0.50,  
                               min_value=0.10)
    # Lengte
    lengte = st.number_input(label='Lengte [meter]', 
                             format="%.2f",
                             step=1.00,
                             value=21.00, 
                             min_value=0.10, 
                             max_value=999.00)
    
    bovenwaterstand=0.05  
    benedenwaterstand=0
    verval=0.05
    sliblaag_cm=5
    sliblaag_procent=0.1
   
    # percentage ondergronds
    with st.expander('percentage ondergronds'):
        if st.checkbox('Hulp', value=False, key='percentage ondergronds'):
            st.image(Image.open('DiaDuiker.jpg'),
                     caption='Dia Duiker')
        keuze_sliblaag = st.selectbox('Keuze: sliblaag in cm of percentage T.O.V. duiker?',
                                             options=('cm sliblaag', 'percentage T.O.V. duiker'),
                                             index=1,
                                             key='keuze_sliblaag')
        if keuze_sliblaag == 'percentage T.O.V. duiker':
            sliblaag_procent1 = st.number_input(label='percentage T.O.V. duiker [%]',
                                              step = 10,
                                              value=0,
                                              min_value=0,
                                              max_value=100)
            sliblaag_procent = sliblaag_procent1 / 100
        elif keuze_sliblaag == 'cm sliblaag':
            sliblaag_cm1 = st.number_input(label='cm sliblaag [cm]',
                                            step=1,
                                            value=5,
                                            min_value=0,
                                            max_value=int((diameter * 100)))
            sliblaag_cm = float((sliblaag_cm1/100) / diameter)
    # Intreedweerstand
    with st.expander("In- en uitreedweerstand"):
        if st.checkbox('Hulp', value=False, key='intreedweerstand'):
            st.write('Gebuik onderstaand figuur voor het bepalen van de intreedweerstand')
            st.write('Standaardwaarde intreedweerstand = 0.4')
            st.image(Image.open('EiWaardes.jpg'),
                     caption='Ei-waarden')
            st.write('Standaardwaarde uitreedweerstand = 1.0')
        intreedweerstand = st.number_input(label='Intreedweerstand [dimensieloos]',
                                           format="%.2f",
                                           value=0.40)
        uittreedweerstand = st.number_input(label='Uittreedweerstand [dimensieloos]',
                                            format="%.2f",
                                            value=1.00)
        # Natte oppervlak benedenstrooms
    with st.expander("Natte oppervlak benedenstrooms"):
        if st.checkbox('Hulp', value=False, key='BenStrNatOpp'):
            st.write('Schat natte oppervlak O.B.V.profiel watergang en peil')
        ben_str_nat_opp = st.number_input(label='Natte oppervlak benedenstrooms',
                                          format="%.2f",
                                          value=5.00)
    # Manning
    with st.expander("Hydraulische weerstand"):
        if st.checkbox('Hulp', value=False, key='Hydraulische weerstand'):
            st.write('Hydraulische weerstand wordt in Manning uitgedrukt')
            st.write('Gebuik onderstaand tabel voor het bepalen van de hydraulische weerstand')
            st.image(Image.open('kWaardem.jpg'),
                     caption='k-Waardem')
        manning = st.number_input(label='Manning [s∙m ^-1/3]',
                                  value=75)
    with st.expander("Verval over duiker"):
        keuze_verval = st.selectbox('Keuze: Verval of hoogte in +mNAP',
                                    options=('Verval', 'Werkelijke hoogte in +mNAP'),
                                    index=0)
        if keuze_verval == 'Verval':
            # Verval
            verval_cm = st.number_input(label='Verval [cm]',
                                        format="%.1f",
                                        step=1.00,
                                        value=5.00)
            verval = verval_cm/100
            bovenwaterstand=verval
            benedenwaterstand=0
            
        elif keuze_verval == 'Werkelijke hoogte in +mNAP':
            # Bovenwaterstand
            bovenwaterstand = st.number_input(label='Bovenwaterstand [+mNAP]',
                                              format="%.2f",
                                              #step=0.10,
                                              value=0.05)
            # Benedenwaterstand
            benedenwaterstand = st.number_input(label='Benedenwaterstand [+mNAP]',
                                                format="%.2f",
                                                #step=0.10,
                                                value=0.00,
                                                min_value=0.00,
                                                max_value=bovenwaterstand)
    return dict(diameter=diameter,
                lengte=lengte,
                sliblaag_cm=sliblaag_cm,
                sliblaag_procent=sliblaag_procent,
                intreedweerstand=intreedweerstand,
                uittreedweerstand=uittreedweerstand,
                ben_str_nat_opp=ben_str_nat_opp,
                manning=manning,
                verval=verval,
                bovenwaterstand=bovenwaterstand,
                benedenwaterstand=benedenwaterstand,
                keuze_sliblaag=keuze_sliblaag,
                keuze_verval=keuze_verval)



## Visualisatie:
# ===================================
def duiker_visualisatie(diameter: float,
                        lengte: float,
                        sliblaag_cm: float,
                        sliblaag_procent: float,
                        intreedweerstand: float,
                        uittreedweerstand: float,
                        ben_str_nat_opp: float,
                        manning: float,
                        verval: float,
                        bovenwaterstand: float,
                        benedenwaterstand: float,
                        keuze_sliblaag: str,
                        keuze_verval: str,  **kwargs):
    # Upload achtergrondfiguur
    with Image.open("DuikerSchematisch_V2.jpg").convert("RGBA") as base:
    
        # Figuur(box) waar tekst in geschreven wordt, met doorzichtige achtergrond
        txt = Image.new("RGBA", base.size, (255, 255, 255, 0))
    
        # Upload een letertype
        fnt = ImageFont.truetype(font='AllerBd.TTF', size=15, index=0, encoding='', layout_engine=None)
        # Format om makkelijk tekst te schrijven. bij oproepen van d wordt ImageDraw.Draw(Image.new) opgeroepen
        d = ImageDraw.Draw(txt)
    
        # Diameter
        d.text((760, 280), f'Diameter: {diameter} [m]', font=fnt, fill=(0,0,0,1000))
        # Lengte duiker
        d.text((650, 360), f'Lengte: {lengte} [m]', font=fnt, fill=(0,0,0,1000))
        # Keuze "percentage ondergronds" of "cm sliblaag"
        if keuze_sliblaag == 'percentage T.O.V. duiker':
            # Percentage ondergronds
            d.text((1150, 345), f'Sliblaag: {sliblaag_procent * 100} [%]', font=fnt, fill=(0,0,0,1000))
        elif keuze_sliblaag == 'cm sliblaag':
            # cm Sliblaag
            d.text((1150, 345), f'Sliblaag: {sliblaag_cm} [cm]', font=fnt, fill=(0,0,0,1000))
        # Intreedweerstand
        d.text((400, 17),  f'Intreedweerstand: {intreedweerstand}', font=fnt, fill=(0,0,0,1000))
        # Uittreedweerstand
        d.text((950, 17),  f'Uittreedweerstand: {uittreedweerstand}', font=fnt, fill=(0,0,0,1000))
        # Manning
        d.text((670, 17),  f'Manning: {manning}', font=fnt, fill=(0,0,0,1000))
        # Keuze "Verval" of "Werkelijke hoogte in +mNAP"
        if keuze_verval == 'Verval':
            # Bovenwaterstand
            d.text((210, 200), 'Bovenwaterstand: N.V.T.', font=fnt, fill=(0,0,0,1000))
            # Benedenwaterstand              
            d.text((1060, 300), 'Benedenwaterstand: N.V.T.', font=fnt, fill=(0,0,0,1000))
            # Verval Duiker
            d.text((1120, 180), f'Verval: {verval*100} [cm]', font=fnt, fill=(0,0,0,1000))                           
        elif keuze_verval == 'Werkelijke hoogte in +mNAP':
            # Bovenwaterstand
            d.text((110, 200), f'Bovenwaterstand: {bovenwaterstand} [+mNAP]', font=fnt, fill=(0,0,0,1000))      
            # Benedenwaterstand
            d.text((1060, 300), f'Benedenwaterstand: {benedenwaterstand} [+mNAP]', font=fnt, fill=(0,0,0,1000))  
            # Verval Duiker
            d.text((1120, 180), 'Verval: N.V.T', font=fnt, fill=(0,0,0,1000))                                    
            
        out = Image.alpha_composite(base, txt)
        buff = io.BytesIO()
        out.save(buff, format='PNG')
        return buff

## Layout:
# ===================================
st.markdown("<h1 style='text-align: right; color: black; font-size:10px;'>Geproduceerd door: Niels van der Maaden</h1>", unsafe_allow_html=True)
#st.markdown("<h1 style='text-align: right; color: black; font-size:10px;'>In samenwerking met: Harm Nomden</h1>", unsafe_allow_html=True)
st.image(Image.open('WRIJ_Sweco.jpg'))
st.markdown('##')
st.title('Duiker tool')
#st.markdown('##')

with st.sidebar:
    invoer = invoer_sidebar()
    duiker = Duiker(**invoer)
    
## Output:
# ===================================    
wwith st.container():
    st.image(Image.open(duiker_visualisatie(**invoer)))
    st.plotly_chart(duiker.plotly_figure())
    st.markdown("<h1 style='text-align: left; color: black; font-size:30px;'>Resultaten</h1>", unsafe_allow_html=True)
    keuze_eenheid = st.selectbox(label='Eenheid', options = ['m3/h', 'm3/s', 'l/s'])
    if keuze_eenheid == 'm3/h':
        st.markdown(f"<h1 style='text-align: left; color: black; font-size:20px;'>Debiet: {round(duiker.debiet * 60 * 60,3)} [m3/h]</h1>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: left; color: black; font-size:20px;'>Stroomsnelheid: {round(duiker.stroomsnelheid *60 *60,2)} [m/h]</h1>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: left; color: black; font-size:20px;'>Opstuwing: {round(duiker.opstuwing,2)} [m]</h1>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: left; color: black; font-size:20px;'>Hydraulische ruwheid: {round(duiker.ruwheid,3)}</h1>", unsafe_allow_html=True)
    elif keuze_eenheid == 'm3/s':
        st.markdown(f"<h1 style='text-align: left; color: black; font-size:20px;'>Debiet: {round(duiker.debiet,3)} [m3/s]</h1>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: left; color: black; font-size:20px;'>Stroomsnelheid: {round(duiker.stroomsnelheid,2)} [m/s]</h1>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: left; color: black; font-size:20px;'>Opstuwing: {round(duiker.opstuwing,2)} [m]</h1>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: left; color: black; font-size:20px;'>Hydraulische ruwheid: {round(duiker.ruwheid,3)}</h1>", unsafe_allow_html=True)
    elif keuze_eenheid == 'l/s':
        st.markdown(f"<h1 style='text-align: left; color: black; font-size:20px;'>Debiet: {round(duiker.debiet*1000,3)} [l/s]</h1>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: left; color: black; font-size:20px;'>Stroomsnelheid: {round(duiker.stroomsnelheid,2)} [m/s]</h1>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: left; color: black; font-size:20px;'>Opstuwing: {round(duiker.opstuwing,2)} [m]</h1>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: left; color: black; font-size:20px;'>Hydraulische ruwheid: {round(duiker.ruwheid,3)}</h1>", unsafe_allow_html=True)
