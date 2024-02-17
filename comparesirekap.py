import json
import requests
import pandas as pd
import numpy as np
import streamlit as st

def compare(id):
    #get data from api kawalpemilu.org
    data = requests.get("https://kp24-fd486.et.r.appspot.com/h?id="+str(id)).json()

    aggregated_data = data["result"]["aggregated"]

    dfs = []
    for key, values in aggregated_data.items():
        df = pd.DataFrame(values)
        dfs.append(df)

    df = pd.concat(dfs,ignore_index=True)

    df = df[['idLokasi', 'pas1', 'pas2', 'pas3', 'dpt', 'name']].drop_duplicates(keep='last')
    df['status'] = np.where((df['pas1'] == 0) & (df['pas2'] == 0) & (df['pas3'] == 0), 0, 1)
    df['idLokasi'] = id*1000 + df['name'].astype(int)
    df['idLokasi'] = df['idLokasi'].astype(str)
    kawalpemilu = df

    #get data from api sirekap kpu
    data = requests.get("https://sirekap-obj-data.kpu.go.id/pemilu/hhcw/ppwp/"+str(id)[0:2]+"/"+str(id)[0:4]+"/"+str(id)[0:6]+"/"+str(id)+".json").json()
    rows = []

    for id_, values in data['table'].items():
        row = {
            'id': id_,
            'psu': values['psu'],
            'persen': values['persen'],
            'status_progress': values['status_progress']
        }

        if '100025' in values:
            row['100025'] = int(values['100025'])
        else: row['100025'] = 0
        if '100026' in values:
            row['100026'] = int(values['100026'])
        else: row['100026'] = 0  
        if '100027' in values:
            row['100027'] = int(values['100027'])
        else: row['100027'] = 0
        rows.append(row)

    df = pd.DataFrame(rows)

    df['id'] = df['id'].astype(str)
    df = df.rename(columns={'100025':'pas1','100026':'pas2','100027':'pas3'})
    df = df[['id','pas1','pas2','pas3']].fillna(0)
    df['pas1'] = df['pas1'].astype(int)
    df['pas2'] = df['pas2'].astype(int)
    df['pas3'] = df['pas3'].astype(int)
    df['status'] = np.where((df['pas1'] == 0) & (df['pas2'] == 0) & (df['pas3'] == 0), 0, 1)
    kpu = df

    #merge data sirekap kpu with kawalpemilu.org
    compared = pd.merge(kawalpemilu, kpu, left_on='idLokasi', right_on='id', how='inner')
    compared.columns = ['idLokasi', 'pas1_kawal', 'pas2_kawal', 'pas3_kawal', 'dpt', 'name', 'status_kawal',
           'id', 'pas1_kpu', 'pas2_kpu', 'pas3_kpu', 'status_kpu']
    compared = compared[['id','dpt','pas1_kawal', 'pas2_kawal', 'pas3_kawal','status_kawal','pas1_kpu', 'pas2_kpu', 'pas3_kpu', 'status_kpu']]

    #compare sirekap kpu with kawalpemilu.org
    def check(row):
        if row['status_kawal'] == 1 and row['status_kpu'] == 1:
            if row['pas1_kawal'] == row['pas1_kpu'] and row['pas2_kawal'] == row['pas2_kpu'] and row['pas3_kawal'] == row['pas3_kpu']:
                return 'sesuai' #detect ketidaksesuaian dengan kawalpemilu
            elif row['pas1_kpu'] + row['pas2_kpu'] + row['pas3_kpu'] > row['dpt']*1.02 or row['pas1_kawal'] + row['pas2_kawal'] + row['pas3_kawal'] > row['dpt']*1.02:
                return 'markup' #detect markup suara
            else: return 'tidak sesuai' #detect ketidaksesuaian dengan kawalpemilu
        elif row['pas1_kpu'] + row['pas2_kpu'] + row['pas3_kpu'] > row['dpt']*1.02 or row['pas1_kawal'] + row['pas2_kawal'] + row['pas3_kawal'] > row['dpt']*1.02:
            return 'markup' #detect markup suara
        else: 
            return 'belum dikawal' #detect tps belum dikawal/data belum ada di kawalpemilu
    compared['check'] = compared.apply(check, axis=1)
    return compared

# Fungsi untuk menambahkan warna baris berdasarkan kondisi
def row_color(row):
    color = '#8DE3D1' if row['check'] == 'sesuai' else '#EC7063' if row['check'] == 'markup' or row['check'] == 'tidak sesuai' else '#e3e3e3'
    return [f'background-color: {color}'] * len(row)

tps = pd.read_json("tps2.json",dtype=False)

st.set_page_config(layout="wide")

st.header("Sirekap KPU vs KawalPemilu.org")
st.markdown("Dokumentasi: [**github.com/rezkyyayang/kawalpemilu**](https://github.com/rezkyyayang/kawalpemilu)")

c1, c2, c3, c4 = st.columns(4)

#Dropdown options PROVINSI
opsi_prov = tps[tps.index.astype(str).str.len() == 2]['id2name']
nm_prov = c1.selectbox('Pilih Provinsi:', opsi_prov)
id_prov = tps[tps['id2name'] == nm_prov].index[0]

#Dropdown options KABUPATEN/KOTA
opsi_kab = tps[(tps.index.astype(str).str.len() == 4) & (tps.index.astype(str).str.startswith(str(id_prov)))]['id2name']
nm_kab = c2.selectbox('Pilih Kabupaten/Kota:', opsi_kab)
id_kab = tps[tps['id2name'] == nm_kab].index[0]

#Dropdown options KECAMATAN
opsi_kec = tps[(tps.index.astype(str).str.len() == 6) & (tps.index.astype(str).str.startswith(str(id_kab)))]['id2name']
nm_kec = c3.selectbox('Pilih Kecamatan:', opsi_kec)
id_kec = tps[tps['id2name'] == nm_kec].index[0]

#Dropdown options DESA/KELURAHAN
opsi_desa = tps[(tps.index.astype(str).str.len() == 10) & (tps.index.astype(str).str.startswith(str(id_kec)))]['id2name']
nm_desa = c4.selectbox('Pilih Desa/Kelurahan:', opsi_desa)
id_desa = tps[(tps.index.astype(str).str.len() == 10) & (tps['id2name'] == nm_desa)].index[0]

#Input manual ID Desa/Kelurahan
id = st.text_input("**Masukkan 10 digit ID Desa/Kel:** ",id_desa)

#Button menuju web Sirekap dan KawalPemilu
c5, c6, c7 = st.columns([1,1,6])
c5.link_button("🗳️ SIREKAP KPU", "https://pemilu2024.kpu.go.id/pilpres/hitung-suara/"+str(id)[0:2]+"/"+str(id)[0:4]+"/"+str(id)[0:6]+"/"+str(id),use_container_width = True)
c6.link_button("🔢 KAWAL PEMILU", "https://kawalpemilu.org/h/"+str(id),use_container_width = True)
c7.write(f"""<b>  PROVINSI:</b> {tps.loc[int(str(id)[0:2]),'id2name']} | 
             <b>  KAB/KOTA:</b> {tps.loc[int(str(id)[0:4]),'id2name']} |
             <b>  KECAMATAN:</b> {tps.loc[int(str(id)[0:6]),'id2name']} | 
             <b>  DESA/KEL:</b> {tps.loc[int(id),'id2name']}
             """, unsafe_allow_html=True)
id = int(id)
# Menampilkan dataframe
df = compare(id)
df = df.style.apply(row_color, axis=1)
st.dataframe(df, use_container_width = True)
