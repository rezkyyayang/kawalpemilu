# Sirekap KPU vs KawalPemilu.org
Merupakan aplikasi sederhana yang dibuat dengan Python untuk membantu mempermudah mendeteksi kesalahan perhitungan suara pada Pemilihan Umum Presiden dan Wakil Presiden 2024. Akses melalui [**pemilu.streamlit.app**](https://pemilu.streamlit.app)

<img src="https://github.com/rezkyyayang/kawalpemilu/assets/60925883/e7efa2d0-c43d-4406-bd38-1a74d1b884d4" width="512px">

## Cara Kerja:
- Masukkan Wilayah sampai tingkat Desa/Kelurahan atau Masukkan ID Desa/Kelurahan.
- Sistem akan mengambil data suara setiap TPS di desa terpilih dari **Sirekap KPU** dan **KawalPemilu.org** kemudian akan mencocokannya, berdasarkan ID TPS.
- Sistem akan menampilkan warna-warna dengan arti sebagai berikut:
  - **HIJAU**: perhitungan suara telah sesuai/cocok antara Sirekap dengan KawalPemilu dengan status **"SESUAI"** <br>
  - **MERAH**: perhitungan suara tidak sesuai (berbeda) antara Sirekap dengan KawalPemilu dengan status **"TIDAK SESUAI"** atau jumlah perolehan suara paslon 01 + paslon 02 + paslon 03 > (DPT + 2% * DPT) dengan status **"MARKUP"** <br>
  - **ABU-ABU**: data belum lengkap antara kedua sistem atau keduanya dengan status **"BELUM DIKAWAL"** <br>
- Jika menemukan perhitungan dengan status **MARKUP** atau **TIDAK SESUAI**, kamu bisa berkontribusi melaporkannya di kawalpemilu.org dengan mencantumkan foto C1 dan input hasil perhitungan yang benar.
- Dengan data, mari bersama jaga suara Indonesia.

## Menu:
Saat ini, terdapat 3 menu/fitur yang bisa dicoba, yaitu:
- **SUARA TPS**: Menampilkan data perolehan suara (Real Count) setiap TPS di Desa/Kelurahan terpilih
- **SUARA WILAYAH**: Menampilkan data perolehan suara (Real Count) setiap wilayah Provinsi, Kab/Kota, Kecamatan, dan Desa/Kelurahan
- **PROFIL PASLON**: Menampilkan pasangan calon presiden dan calon wakil presiden beserta visi misinya.

## Sumber Data:
Data yang digunakan berasal dari [**KawalPemilu.org**](https://kawalpemilu.org) dan [**Sirekap KPU**](https://pemilu2024.kpu.go.id)

*Source code sistem ini dibagikan secara terbuka sebagai bahan pembelajaran dan pengembangan lebih lanjut.
