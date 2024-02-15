# Sirekap KPU vs KawalPemilu.org
Merupakan aplikasi sederhana yang dibuat dengan Python untuk membantu mempermudah mendeteksi kesalahan perhitungan suara pada Pemilihan Umum Presiden dan Wakil Presiden 2024. Akses melalui [**pemilu.streamlit.io**](https://pemilu.streamlit.io)

<img src="https://github.com/rezkyyayang/kawalpemilu/assets/60925883/ced249ff-a867-4c47-8392-01c369fd9d1c" width="512px">

- Ketahui ID Desa/Kelurahan yang ingin kamu pantau di **pemilu2024.kpu.go.id** atau di **kawalpemilu.org** dengan memilih dari tingkat PROVINSI > KABUPATEN/KOTA > KECAMATAN > DESA/KELURAHAN
- ID Desa/Kelurahan merupakan angka 10 digit, biasanya dapat ditemukan di URL/alamat halaman website.
- Masukkan ID Desa/Kelurahan, dan pantau TPS di Desa/Kelurahan yang kamu pilih.
- Sistem akan mengambil data dari Sirekap KPU dan KawalPemilu.org kemudian akan mencocokannya, berdasarkan ID TPS.
- Sistem akan menampilkan warna-warna dengan arti sebagai berikut:
  - **HIJAU**: perhitungan suara telah sesuai/cocok antara Sirekap dengan KawalPemilu dengan status **"SESUAI"** <br>
  - **MERAH**: perhitungan suara tidak sesuai (berbeda) antara Sirekap dengan Kawal Pemilu dengan status **"TIDAK SESUAI"** atau jumlah suara paslon 01 + paslon 02 + paslon 03 > (DPT + 2% * DPT) dengan status **"MARKUP"** <br>
  - **ABU-ABU**: data belum lengkap antara kedua sistem atau keduanya dengan status **"BELUM DIKAWAL"** <br>
- Jika menemukan perhitungan dengan status **MARKUP** atau **TIDAK SESUAI**, kamu bisa berkontribusi melaporkannya di kawalpemilu.org dengan mencantumkan foto C1 dan input hasil perhitungan yang benar.
- Dengan data, mari bersama jaga suara Indonesia.

*Source code sistem ini dibagikan secara terbuka sebagai bahan pembelajaran dan pengembangan lebih lanjut.
