import json
import requests
import pandas as pd
import numpy as np
import streamlit as st

def compare(id,tingkat):
    #get data from api kawalpemilu.org
    
    if tingkat == 'desa':
        data = requests.get("https://kp24-fd486.et.r.appspot.com/h?id="+str(id)).json()
    elif tingkat == 'kec':
        data = requests.get("https://kp24-fd486.et.r.appspot.com/h?id="+str(id)[0:6]).json()
    elif tingkat == 'kab':
        data = requests.get("https://kp24-fd486.et.r.appspot.com/h?id="+str(id)[0:4]).json()
    elif tingkat == 'prov':
        data = requests.get("https://kp24-fd486.et.r.appspot.com/h?id="+str(id)[0:2]).json()
    elif tingkat == 'nas':
        data = requests.get("https://kp24-fd486.et.r.appspot.com/h?id=").json()

    aggregated_data = data["result"]["aggregated"]

    dfs = []
    for key, values in aggregated_data.items():
        df = pd.DataFrame(values)
        dfs.append(df)

    df = pd.concat(dfs,ignore_index=True)

    if tingkat == 'desa':
        df = df[['idLokasi', 'pas1', 'pas2', 'pas3', 'dpt', 'name']].drop_duplicates(subset=['idLokasi'],keep='first')
    else: 
        df = df[['idLokasi', 'pas1', 'pas2', 'pas3', 'totalTps', 'name']].drop_duplicates(subset=['idLokasi'],keep='first')
    df['status'] = np.where((df['pas1'] == 0) & (df['pas2'] == 0) & (df['pas3'] == 0), 0, 1)
    if tingkat == 'desa':
        df['idLokasi'] = id*1000 + df['name'].astype(int)
    df['idLokasi'] = df['idLokasi'].astype(str)
    kawalpemilu = df

    #get data from api sirekap kpu
    if tingkat == 'desa':
        data = requests.get("https://sirekap-obj-data.kpu.go.id/pemilu/hhcw/ppwp/"+str(id)[0:2]+"/"+str(id)[0:4]+"/"+str(id)[0:6]+"/"+str(id)+".json").json()
    elif tingkat == 'kec':
        data = requests.get("https://sirekap-obj-data.kpu.go.id/pemilu/hhcw/ppwp/"+str(id)[0:2]+"/"+str(id)[0:4]+"/"+str(id)[0:6]+".json").json()
    elif tingkat == 'kab':
        data = requests.get("https://sirekap-obj-data.kpu.go.id/pemilu/hhcw/ppwp/"+str(id)[0:2]+"/"+str(id)[0:4]+".json").json()
    elif tingkat == 'prov':
        data = requests.get("https://sirekap-obj-data.kpu.go.id/pemilu/hhcw/ppwp/"+str(id)[0:2]+".json").json()
    elif tingkat == 'nas':
        data = requests.get("https://sirekap-obj-data.kpu.go.id/pemilu/hhcw/ppwp.json").json()

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

    if tingkat == 'desa':
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
    else:
        #merge data sirekap kpu with kawalpemilu.org
        compared = pd.merge(kawalpemilu, kpu, left_on='idLokasi', right_on='id', how='inner')
        compared.columns = ['idLokasi', 'pas1_kawal', 'pas2_kawal', 'pas3_kawal', 'totalTps', 'name', 'status_kawal',
               'id', 'pas1_kpu', 'pas2_kpu', 'pas3_kpu', 'status_kpu']
        compared = compared[['name','totalTps','pas1_kawal', 'pas2_kawal', 'pas3_kawal','status_kawal','pas1_kpu', 'pas2_kpu', 'pas3_kpu', 'status_kpu']]

        #compare sirekap kpu with kawalpemilu.org
        def check(row):
            if row['status_kawal'] == 1 and row['status_kpu'] == 1:
                if row['pas1_kawal'] == row['pas1_kpu'] and row['pas2_kawal'] == row['pas2_kpu'] and row['pas3_kawal'] == row['pas3_kpu']:
                    return 'sesuai' #detect ketidaksesuaian dengan kawalpemilu
                else: return 'tidak sesuai' #detect ketidaksesuaian dengan kawalpemilu
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

tab1, tab2, tab3 = st.tabs(["Suara TPS","Suara Wilayah","Profil Paslon"])

with tab1:
    st.header("Sirekap KPU vs KawalPemilu.org")
    st.markdown("Dokumentasi: [**github.com/rezkyyayang/kawalpemilu**](https://github.com/rezkyyayang/kawalpemilu)")

    c1, c2, c3, c4 = st.columns(4)

    #Dropdown options PROVINSI
    opsi_prov = tps[tps.index.astype(str).str.len() == 2]['id2name']
    nm_prov = c1.selectbox('Pilih Provinsi:', opsi_prov)
    id_prov = tps[(tps.index.astype(str).str.len() == 2) & (tps['id2name'] == nm_prov)].index[0]

    #Dropdown options KABUPATEN/KOTA
    opsi_kab = tps[(tps.index.astype(str).str.len() == 4) & (tps.index.astype(str).str.startswith(str(id_prov)))]['id2name']
    nm_kab = c2.selectbox('Pilih Kabupaten/Kota:', opsi_kab)
    id_kab = tps[(tps.index.astype(str).str.len() == 4) & (tps.index.astype(str).str.startswith(str(id_prov))) & (tps['id2name'] == nm_kab)].index[0]

    #Dropdown options KECAMATAN
    opsi_kec = tps[(tps.index.astype(str).str.len() == 6) & (tps.index.astype(str).str.startswith(str(id_kab)))]['id2name']
    nm_kec = c3.selectbox('Pilih Kecamatan:', opsi_kec)
    id_kec = tps[(tps.index.astype(str).str.len() == 6) & (tps.index.astype(str).str.startswith(str(id_kab))) & (tps['id2name'] == nm_kec)].index[0]

    #Dropdown options DESA/KELURAHAN
    opsi_desa = tps[(tps.index.astype(str).str.len() == 10) & (tps.index.astype(str).str.startswith(str(id_kec)))]['id2name']
    nm_desa = c4.selectbox('Pilih Desa/Kelurahan:', opsi_desa)
    id_desa = tps[(tps.index.astype(str).str.len() == 10) & (tps.index.astype(str).str.startswith(str(id_kec))) & (tps['id2name'] == nm_desa)].index[0]

    # Menggunakan st.text_input() untuk memasukkan teks
    id = st.text_input("**Masukkan 10 digit ID Desa/Kel:** ",id_desa)

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
    df = compare(id, tingkat = 'desa')
    st.dataframe(df.style.apply(row_color, axis=1),use_container_width = True)
    #Menampilkan diagram batang
    st.subheader('Diagram Suara:')
    c8, c9 = st.columns(2)
    c8.subheader('🔢 Kawal Pemilu')
    c8.bar_chart(df[['id','pas1_kawal','pas2_kawal','pas3_kawal']].rename(columns={'id': 'id_tps'}), 
                 x='id_tps',
                 color=['#CCFFCC','#CCCCFF','#FFCCCC'])
    c9.subheader('🗳️ Sirekap KPU')
    c9.bar_chart(df[['id','pas1_kpu','pas2_kpu','pas3_kpu']].rename(columns={'id': 'id_tps'}), 
                 x='id_tps', 
                 color=['#CCFFCC','#CCCCFF','#FFCCCC'])

with tab2:
    st.header("Sirekap KPU vs KawalPemilu.org")
    st.markdown("Dokumentasi: [**github.com/rezkyyayang/kawalpemilu**](https://github.com/rezkyyayang/kawalpemilu)")

    d1, d2, d3 = st.columns(3)

    #Dropdown options PROVINSI
    opsi_prov = tps[tps.index.astype(str).str.len() == 2]['id2name']
    nm_prov = d1.selectbox('Pilih Provinsi:', opsi_prov, key='d_prov')
    id_prov = tps[(tps.index.astype(str).str.len() == 2) & (tps['id2name'] == nm_prov)].index[0]

    #Dropdown options KABUPATEN/KOTA
    opsi_kab = tps[(tps.index.astype(str).str.len() == 4) & (tps.index.astype(str).str.startswith(str(id_prov)))]['id2name']
    nm_kab = d2.selectbox('Pilih Kabupaten/Kota:', opsi_kab, key='d_kab')
    id_kab = tps[(tps.index.astype(str).str.len() == 4) & (tps.index.astype(str).str.startswith(str(id_prov))) & (tps['id2name'] == nm_kab)].index[0]

    #Dropdown options KECAMATAN
    opsi_kec = tps[(tps.index.astype(str).str.len() == 6) & (tps.index.astype(str).str.startswith(str(id_kab)))]['id2name']
    nm_kec = d3.selectbox('Pilih Kecamatan:', opsi_kec, key='d_kec')
    id_kec = tps[(tps.index.astype(str).str.len() == 6) & (tps.index.astype(str).str.startswith(str(id_kab))) & (tps['id2name'] == nm_kec)].index[0]

    id_wil = id_kec

    tab_nasional, tab_provinsi, tab_kabkot, tab_kecamatan = st.tabs(['Nasional','Provinsi','Kab/Kota','Kecamatan'])

    with tab_nasional:
        st.subheader('Suara Nasional')
        w1, w2, w3 = st.columns([1,1,6])
        w1.link_button("🗳️ SIREKAP KPU", "https://pemilu2024.kpu.go.id/pilpres/hitung-suara/",use_container_width = True)
        w2.link_button("🔢 KAWAL PEMILU", "https://kawalpemilu.org/h/",use_container_width = True)
        w3.write(f"""<b>  NASIONAL</b>
                 """, unsafe_allow_html=True)
        id = int(id_wil)
        # Menampilkan dataframe
        df = compare(id_wil, tingkat = 'nas')
        st.dataframe(df.style.apply(row_color, axis=1),use_container_width = True)
        #Menampilkan diagram batang
        st.subheader('Diagram Suara:')
        w4, w5 = st.columns(2)
        w4.subheader('🔢 Kawal Pemilu')
        w4.bar_chart(df[['name','pas1_kawal','pas2_kawal','pas3_kawal']].rename(columns={'name': 'provinsi'}), 
                     x='provinsi',
                     color=['#CCFFCC','#CCCCFF','#FFCCCC'])
        w5.subheader('🗳️ Sirekap KPU')
        w5.bar_chart(df[['name','pas1_kpu','pas2_kpu','pas3_kpu']].rename(columns={'name': 'provinsi'}), 
                     x='provinsi', 
                     color=['#CCFFCC','#CCCCFF','#FFCCCC'])

    with tab_provinsi:
        st.subheader('Suara Provinsi:')
        x1, x2, x3 = st.columns([1,1,6])
        x1.link_button("🗳️ SIREKAP KPU", "https://pemilu2024.kpu.go.id/pilpres/hitung-suara/"+str(id_wil)[0:2],use_container_width = True)
        x2.link_button("🔢 KAWAL PEMILU", "https://kawalpemilu.org/h/"+str(id_wil),use_container_width = True)
        x3.write(f"""<b>  PROVINSI:</b> {tps.loc[int(str(id_wil)[0:2]),'id2name']}
                 """, unsafe_allow_html=True)
        id = int(id_wil)
        # Menampilkan dataframe
        df = compare(id_wil, tingkat = 'prov')
        st.dataframe(df.style.apply(row_color, axis=1),use_container_width = True)
        #Menampilkan diagram batang
        st.subheader('Diagram Suara:')
        x4, x5 = st.columns(2)
        x4.subheader('🔢 Kawal Pemilu')
        x4.bar_chart(df[['name','pas1_kawal','pas2_kawal','pas3_kawal']].rename(columns={'name': 'kabupaten_kota'}), 
                     x='kabupaten_kota',
                     color=['#CCFFCC','#CCCCFF','#FFCCCC'])
        x5.subheader('🗳️ Sirekap KPU')
        x5.bar_chart(df[['name','pas1_kpu','pas2_kpu','pas3_kpu']].rename(columns={'name': 'kabupaten_kota'}), 
                     x='kabupaten_kota', 
                     color=['#CCFFCC','#CCCCFF','#FFCCCC'])

    with tab_kabkot:
        st.subheader('Suara Kab/Kota:')
        y1, y2, y3 = st.columns([1,1,6])
        y1.link_button("🗳️ SIREKAP KPU", "https://pemilu2024.kpu.go.id/pilpres/hitung-suara/"+str(id_wil)[0:2]+"/"+str(id_wil)[0:4],use_container_width = True)
        y2.link_button("🔢 KAWAL PEMILU", "https://kawalpemilu.org/h/"+str(id_wil),use_container_width = True)
        y3.write(f"""<b>  PROVINSI:</b> {tps.loc[int(str(id_wil)[0:2]),'id2name']} | 
                 <b>  KAB/KOTA:</b> {tps.loc[int(str(id_wil)[0:4]),'id2name']}
                 """, unsafe_allow_html=True)
        id = int(id_wil)
        # Menampilkan dataframe
        df = compare(id_wil, tingkat = 'kab')
        st.dataframe(df.style.apply(row_color, axis=1),use_container_width = True)
        #Menampilkan diagram batang
        st.subheader('Diagram Suara:')
        y4, y5 = st.columns(2)
        y4.subheader('🔢 Kawal Pemilu')
        y4.bar_chart(df[['name','pas1_kawal','pas2_kawal','pas3_kawal']].rename(columns={'name': 'kecamatan'}), 
                     x='kecamatan',
                     color=['#CCFFCC','#CCCCFF','#FFCCCC'])
        y5.subheader('🗳️ Sirekap KPU')
        y5.bar_chart(df[['name','pas1_kpu','pas2_kpu','pas3_kpu']].rename(columns={'name': 'kecamatan'}), 
                     x='kecamatan', 
                     color=['#CCFFCC','#CCCCFF','#FFCCCC'])

    with tab_kecamatan:
        st.subheader('Suara Kecamatan:')
        z1, z2, z3 = st.columns([1,1,6])
        z1.link_button("🗳️ SIREKAP KPU", "https://pemilu2024.kpu.go.id/pilpres/hitung-suara/"+str(id_wil)[0:2]+"/"+str(id_wil)[0:4]+"/"+str(id_wil),use_container_width = True)
        z2.link_button("🔢 KAWAL PEMILU", "https://kawalpemilu.org/h/"+str(id),use_container_width = True)
        z3.write(f"""<b>  PROVINSI:</b> {tps.loc[int(str(id_wil)[0:2]),'id2name']} | 
                 <b>  KAB/KOTA:</b> {tps.loc[int(str(id_wil)[0:4]),'id2name']} |
                 <b>  KECAMATAN:</b> {tps.loc[int(str(id_wil)),'id2name']}
                 """, unsafe_allow_html=True)
        id = int(id_wil)
        # Menampilkan dataframe
        df = compare(id_wil, tingkat = 'kec')
        st.dataframe(df.style.apply(row_color, axis=1),use_container_width = True)
        #Menampilkan diagram batang
        st.subheader('Diagram Suara:')
        z4, z5 = st.columns(2)
        z4.subheader('🔢 Kawal Pemilu')
        z4.bar_chart(df[['name','pas1_kawal','pas2_kawal','pas3_kawal']].rename(columns={'name': 'desa_kelurahan'}), 
                     x='desa_kelurahan',
                     color=['#CCFFCC','#CCCCFF','#FFCCCC'])
        z5.subheader('🗳️ Sirekap KPU')
        z5.bar_chart(df[['name','pas1_kpu','pas2_kpu','pas3_kpu']].rename(columns={'name': 'desa_kelurahan'}), 
                     x='desa_kelurahan', 
                     color=['#CCFFCC','#CCCCFF','#FFCCCC'])


with tab3:
    st.header("Profil Pasangan Capres-Cawapres")
    st.markdown("Dokumentasi: [**github.com/rezkyyayang/kawalpemilu**](https://github.com/rezkyyayang/kawalpemilu)")

    c8, c9, c10 = st.columns(3)

    with c8:
        st.header("01")
        st.image("https://asset.kompas.com/data/2023/10/25/kompascom/widget/bacapres/images/paslon/Anies-Muhaimin.png", width=250)
        st.subheader("H. ANIES RASYID BASWEDAN, Ph.D. - Dr. (H.C.) H. A. MUHAIMIN ISKANDAR")
        with st.expander("Lihat Visi Misi Paslon 01"):
            st.write("<b>VISI</b> <br> Indonesia Adil Makmur Untuk Semua", unsafe_allow_html= True)
            st.write("""<b>MISI</b> <br>
                     1. Memastikan Ketersediaan Kebutuhan Pokok dan Biaya Hidup Murah melalui Kemandirian Pangan, Ketahanan Energi, dan Kedaulatan Air.
                     <br> 2. Mengentaskan Kemiskinan dengan Memperluas Kesempatan Berusaha dan Menciptakan Lapangan Kerja, Mewujudkan Upah Berkeadilan, Menjamin Kemajuan Ekonomi Berbasis Kemandirian dan Pemerataan, serta Mendukung Korporasi Indonesia Berhasil di Negeri Sendiri dan Bertumbuh di Kancah Global.
                     <br> 3. Mewujudkan Keadilan Ekologis Berkelanjutan untuk Generasi Mendatang.
                     <br> 4. Membangun Kota dan Desa Berbasis Kawasan yang Manusiawi, Berkeadilan dan Saling Memajukan.
                     <br> 5. Mewujudkan Manusia Indonesia yang Sehat, Cerdas, Produktif, Berakhlak, dan Berbudaya.
                     <br> 6. Mewujudkan Keluarga Indonesia yang Sejahtera dan Bahagia sebagai Akar Kekuatan Bangsa.
                     <br> 7. Memperkuat Sistem Pertahanan dan Keamanan Negara, serta Meningkatkan Peran dan Kepemimpinan Indonesia dalam Arena Politik Global untuk Mewujudkan Kepentingan Nasional dan Perdamaian Dunia.
                     <br> 8. Memulihkan Kualitas Demokrasi, Menegakkan Hukum dan HAM, Memberantas Korupsi Tanpa Tebang Pilih, serta Menyelenggarakan Pemerintahan yang Berpihak pada Rakyat
                     """, unsafe_allow_html= True)
        st.link_button("📄 Unduh Visi Misi Lengkap", "https://drive.google.com/file/d/1BOfwwq9NHMwiGJIaeDOCoko5Y9HRwnkQ/view",use_container_width = True)
        
    
    with c9:
        st.header("02")
        st.image("https://asset.kompas.com/data/2023/10/25/kompascom/widget/bacapres/images/paslon/Prabowo-Gibran.png", width=250)
        st.subheader("H. PRABOWO SUBIANTO - GIBRAN RAKABUMING RAKA")
        with st.expander("Lihat Visi Misi Paslon 02"):
            st.write("<b>VISI</b> <br> Bersama Indonesia Maju Menuju Indonesia Emas 2045", unsafe_allow_html= True)
            st.write("""<b>MISI</b> <br>
                     1. Memperkokoh ideologi Pancasila, demokrasi, dan hak asasi manusia (HAM).
                     <br> 2. Memantapkan sistem pertahanan keamanan negara dan mendorong kemandirian bangsa melalui swasembada pangan, energi, air, ekonomi syariah, ekonomi digital, ekonomi hijau, dan ekonomi biru.
                     <br> 3. Melanjutkan pengembangan infrastruktur dan meningkatkan lapangan kerja yang berkualitas, mendorong kewirausahaan, mengembangkan industri kreatif serta mengembangkan agro-maritim industri di sentra produksi melalui peran aktif koperasi.
                     <br> 4. Memperkuat pembangunan sumber daya manusia (SDM), sains, teknologi, pendidikan, kesehatan, prestasi olahraga, kesetaraan gender, serta penguatan peran perempuan, pemuda (generasi milenial dan generasi Z), dan penyandang disabilitas.
                     <br> 5. Melanjutkan hilirisasi dan mengembangkan industri berbasis sumber daya alam untuk meningkatkan nilai tambah di dalam negeri.
                     <br> 6. Membangun dari desa dan dari bawah untuk pertumbuhan ekonomi, pemerataan ekonomi, dan pemberantasan kemiskinan.
                     <br> 7. Memperkuat reformasi politik, hukum, dan birokrasi, serta memperkuat pencegahan dan pemberantasan korupsi, narkoba, judi, dan penyelundupan.
                     <br> 8. Memperkuat penyelarasan kehidupan yang harmonis dengan lingkungan, alam dan budaya, serta peningkatan toleransi antarumat beragama untuk mencapai masyarakat yang adil dan makmur.
                     """, unsafe_allow_html= True)
        st.link_button("📄 Unduh Visi Misi Lengkap", "https://drive.google.com/file/d/17UaC5XwNuplXe_riHNrB7jb1STHvRWg-/view?usp=sharing",use_container_width = True)
        
    
    with c10:
        st.header("03")
        st.image("https://asset.kompas.com/data/2023/10/25/kompascom/widget/bacapres/images/paslon/Ganjar-Mahfud.png", width=250)
        st.subheader("H. GANJAR PRANOWO, S.H., M.I.P. - Prof. Dr. H. M. MAHFUD MD")
        with st.expander("Lihat Visi Misi Paslon 03"):
            st.write("<b>VISI</b> <br> Gerak Cepat Menuju Indonesia Unggul", unsafe_allow_html= True)
            st.write("""<b>MISI</b> <br>
                     1. Manusia Indonesia yang sehat, terdidik, dan sejahtera
                     <br> 2. Indonesia unggul dalam bidang inovasi dan teknologi
                     <br> 3. Ekonomi yang tangguh dan berdikari
                     <br> 4. Hilangnya kemiskinan dan ketimpangan antarwilayah dari akarnya
                     <br> 5. Ekosistem digital yang mengutamakan akses internet cepat dan terjangkau
                     <br> 6. Pembangunan ekonomi yang memperhatikan kelestarian lingkungan
                     <br> 7. Demokrasi terjaga melalui pemberantasan korupsi dan pemerintahan inklusif berlandaskan supremasi hukum
                     <br> 8. Indonesia bangsa terhormat di kancah internasional, serta pertahanan yang tangguh dan modern
                     """, unsafe_allow_html= True)
        st.link_button("📄 Unduh Visi Misi Lengkap", "https://drive.google.com/file/d/1ey8BwGJhDNcZXXSCkHgn621KdWRRbNWN/view?usp=sharing",use_container_width = True)
        
