import streamlit as st
st.set_page_config(layout="wide")
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
from streamlit_folium import st_folium
import folium
import geopandas as gpd

sns.set_theme()
sns.set_color_codes("dark")
dfUNHCR = pd.read_csv("UNHCR_Flow_Data.xlsx - DATA.csv", skipinitialspace=True,
                      dtype = {'OriginISO':str,'OriginName':str,'AsylumISO':str,'AsylumName':str,'PT':str,'Year':np.int32,'Count':object}
                      ).query('Year >= 2010 & Year <= 2021 & PT == "ASY"').rename(columns = {'OriginISO':'Country of origin (ISO)',
                    'OriginName':'Country of origin',
                    'AsylumISO':'Country of asylum (ISO)',
                    'AsylumName':'Country of asylum',
                    'Count':'Refugees under UNHCR\'s mandate'})
dfUNHCR['Refugees under UNHCR\'s mandate'] = dfUNHCR['Refugees under UNHCR\'s mandate'].str.strip().str.replace(',','').astype(dtype = np.int32)
origins = np.insert(np.sort(dfUNHCR['Country of origin'].unique().tolist()), 0, 'All')
asylums = np.insert(np.sort(dfUNHCR['Country of asylum'].unique().tolist()), 0, 'All')
countriesJSON = gpd.read_file("lowResCountriesAdjusted.json")[['geometry','iso_a3_eh', 'pop_est']]
chorBins = [0, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000]

st.title('Refugee Flow Visualisation')

leftCol, midCol, rightCol = st.columns(3)

with leftCol:
    origin = st.selectbox(label = 'Country of origin', options = origins)

with midCol:
    yearSel = st.slider('Year',2010, 2021, 2021)

with rightCol:
    asylum = st.selectbox(label = 'Country of asylum', options = asylums)

dualLeftCol, dualRightCol = st.columns(2)

with dualLeftCol:
    if origin == 'All':
        if asylum != 'All':
            st.subheader('Origin countries for asylum in ' + asylum)
            dfChoroOrigin = dfUNHCR.query('`Country of asylum` == @asylum & Year == @yearSel').groupby(['Country of origin (ISO)', 'Country of origin']).agg({'Refugees under UNHCR\'s mandate':sum}).reset_index()
        else:
            st.subheader('Origin countries')
            dfChoroOrigin = dfUNHCR.query('Year == @yearSel').groupby(['Country of origin (ISO)', 'Country of origin']).agg({'Refugees under UNHCR\'s mandate': sum}).reset_index()
        mL = folium.Map(location = [15,0], zoom_start=1)
        cL = folium.Choropleth(
            geo_data=countriesJSON,
            name="choropleth",
            data=dfChoroOrigin,
            columns=['Country of origin (ISO)', 'Refugees under UNHCR\'s mandate'],
            key_on="feature.properties.iso_a3_eh",
            fill_opacity=0.7,
            line_opacity=0.2,
            bins = chorBins
        )
        for key in cL._children:
            if key.startswith('color_map'):
                del (cL._children[key])
        cL.add_to(mL)
        gdfOrigin = countriesJSON.merge(dfChoroOrigin,left_on="iso_a3_eh", right_on="Country of origin (ISO)")
        featureL = folium.features.GeoJson(
            data=gdfOrigin,
            name='originTooltip',
            smooth_factor=2,
            style_function=lambda x: {'color': 'black', 'fillColor': 'transparent', 'weight': 0.5},
            tooltip=folium.features.GeoJsonTooltip(
                fields=['Country of origin', 'Refugees under UNHCR\'s mandate'],
                aliases=['Origin: ', 'Refugees: '],
                localize=True,
                sticky=False,
                labels=True,
                style="""
                                    background-color: #F0EFEF;
                                    border: 2px solid black;
                                    border-radius: 3px;
                                    box-shadow: 3px;
                                """,
                max_width=800, ),
            highlight_function=lambda x: {'weight': 3, 'fillColor': 'grey'},
        ).add_to(mL)
        st_folium(mL, key = 'mL',
                height=420, width = 735, returned_objects=[])
    else:
        if asylum != 'All':
            st.subheader('Plot of refugees from ' + origin + ' for asylum in ' + asylum)
            dfOriginSelect = dfUNHCR.query('`Country of asylum` == @asylum & `Country of origin` == @origin').groupby(['Year']).agg({'Refugees under UNHCR\'s mandate':sum}).reset_index()
        else:
            st.subheader('Refugees from ' + origin)
            dfOriginSelect = dfUNHCR.query('`Country of origin` == @origin').groupby(['Year']).agg({'Refugees under UNHCR\'s mandate': sum}).reset_index()
        fig, ax = plt.subplots(figsize=(16, 9))
        sns.lineplot(x="Year", y="Refugees under UNHCR\'s mandate", data=dfOriginSelect, color="b")
        sns.scatterplot(x="Year", y="Refugees under UNHCR\'s mandate", data=dfOriginSelect, color="b")
        ax.set(ylabel="Refugees",
               xlabel="Year")
        ax.get_yaxis().set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
        ax.set_ylim(0, None)
        st.pyplot(fig)

with dualRightCol:
    if asylum == 'All':
        if origin != 'All':
            st.subheader('Asylum countries for origin from ' + origin)
            dfChoroAsylum = dfUNHCR.query('`Country of origin` == @origin & Year == @yearSel').groupby(['Country of asylum (ISO)', 'Country of asylum']).agg({'Refugees under UNHCR\'s mandate':sum}).reset_index()
        else:
            st.subheader('Asylum countries')
            dfChoroAsylum = dfUNHCR.query('Year == @yearSel').groupby(['Country of asylum (ISO)', 'Country of asylum']).agg({'Refugees under UNHCR\'s mandate': sum}).reset_index()
        mR = folium.Map(location=[15, 0], zoom_start=1)
        cR = folium.Choropleth(
            geo_data=countriesJSON,
            name="choropleth",
            data=dfChoroAsylum,
            columns=['Country of asylum (ISO)', 'Refugees under UNHCR\'s mandate'],
            key_on="feature.properties.iso_a3_eh",
            fill_opacity=0.7,
            line_opacity=0.2,
            bins = chorBins
        )
        for key in cR._children:
            if key.startswith('color_map'):
                del (cR._children[key])
        cR.add_to(mR)
        gdfAsylum = countriesJSON.merge(dfChoroAsylum,left_on="iso_a3_eh", right_on="Country of asylum (ISO)")
        featureR = folium.features.GeoJson(
            data=gdfAsylum,
            name='originTooltip',
            style_function=lambda x: {'color': 'black', 'fillColor': 'transparent', 'weight': 0.5},
            tooltip=folium.features.GeoJsonTooltip(
                fields=['Country of asylum', 'Refugees under UNHCR\'s mandate'],
                aliases=['Asylum: ', 'Refugees: '],
                localize=True,
                sticky=False,
                labels=True,
                style="""
                                    background-color: #F0EFEF;
                                    border: 2px solid black;
                                    border-radius: 3px;
                                    box-shadow: 3px;
                                """,
                max_width=800, ),
            highlight_function=lambda x: {'weight': 3, 'fillColor': 'grey'},
        ).add_to(mR)
        st_folium(mR, key='mR',
                height=420,  width = 735, returned_objects=[])
    else:
        if origin != 'All':
            st.subheader('Table of refugees in ' + asylum + ' originating from ' + origin)
            dfAsylumSelect = dfUNHCR.query('`Country of origin` == @origin & `Country of asylum` == @asylum').groupby(
                ['Year']).agg({'Refugees under UNHCR\'s mandate': sum}).reset_index()
            st.dataframe(dfAsylumSelect, hide_index=True)
        else:
            st.subheader('Refugees in ' + asylum)
            dfAsylumSelect = dfUNHCR.query('`Country of asylum` == @asylum').groupby(['Year']).agg(
                {'Refugees under UNHCR\'s mandate': sum}).reset_index()
            fig, ax = plt.subplots(figsize=(16, 9))
            sns.lineplot(x="Year", y="Refugees under UNHCR\'s mandate", data=dfAsylumSelect, color="b")
            sns.scatterplot(x="Year", y="Refugees under UNHCR\'s mandate", data=dfAsylumSelect, color="b")
            ax.set(ylabel="Refugees",
                   xlabel="Year")
            ax.get_yaxis().set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
            ax.set_ylim(0, None)
            st.pyplot(fig)