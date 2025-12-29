from tugasstrukdis.sidebarui import set_sidebar_background
from tugasstrukdis.parser import *
from tugasstrukdis.graph import Graph
import streamlit as st
import graphviz
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'expanded'
if 'sudah_submit' not in st.session_state:
    st.session_state.sudah_submit = False

# State untuk menyimpan kode sementara
if 'code_cache' not in st.session_state:
    st.session_state.code_cache = ""
# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Java Code Visualizer", layout="wide",initial_sidebar_state=st.session_state.sidebar_state)
def saat_tombol_ditekan():
    # Ini dipanggil HANYA saat tombol diklik
    st.session_state.sidebar_state = 'collapsed' # Perintah tutup sidebar
    st.session_state.sudah_submit = True         # Izinkan analisis berjalan

def saat_file_berubah():
    # Jika user ganti file/upload ulang, reset status submit
    # Jadi sidebar tidak menutup dulu, dan hasil lama hilang
    st.session_state.sudah_submit = False
    st.session_state.sidebar_state = 'expanded'
try:
    set_sidebar_background("./assets/bluewpp.jpg")
except FileNotFoundError:
    pass
with (
    st.sidebar
):  # menggunakan sidebar untuk mengelompokan submit dan textfield di bagian kiri
    st.header("Upload/Tulis kode java kamu")
    uploaded_file = st.file_uploader(
        "**Pilih file (java)**", type=["java"],
        on_change=saat_file_berubah
    )  # membatasi agar file yang dapat diupload hanya bertipe java
    file_ada = uploaded_file is not None  # boolean jika file ada atau tidak ada
    java_code_input=""
    if file_ada:  # jika ada
        # Menampilkan informasi file
        st.success(f" File berhasil diterima: {uploaded_file.name}")

        # Menampilkan detail ukuran file
        st.write(f"Ukuran file: {uploaded_file.size} bytes")
        stringio = uploaded_file.getvalue().decode("utf-8")
        java_code = stringio
        st.markdown("---")  # pembatas agar rapi

    # TEXT FIELD
    user_text = st.text_area(  # text field untuk copy paste code
        "**Paste kode java:**",
        height=150,
        disabled=file_ada,  # jika ada file maka textfield ini di disabeld
        placeholder="public class Main{...}",
    )
    if not file_ada:
        java_code = user_text
    # Logika untuk mengatur  submit bisa di enabled /disabled saat file ada maka textfield di disabled dan begitu sebaliknya

    tombol_submit = st.button("Submit", type="primary", use_container_width=True, on_click=saat_tombol_ditekan)


# ----- UI Main (Node)
if st.session_state.sudah_submit:
   
    if not java_code.strip():
        st.warning("Silahkan upload file/ketik code terlebih dahulu")
    else:
      col_result, col_source = st.columns([5, 5])
      with col_source:
          st.subheader("Java Source Code")
            # Menampilkan kode dengan syntax highlighting dan nomor baris
          st.code(java_code, language='java', line_numbers=True)
      with col_result:
        st.header("Hasil Visualisasi Node")

        # panggil method analyze java code
        hasil = JavaCode(java_code)
        classes = hasil.classes
        if not classes:
            st.info("Tidak ditemukan")
            # tampilkan hasil
        for cls in classes:
            with st.expander(f"Class {cls.name}", expanded=True):
                

                for idx, method in enumerate(cls.methods):
                   
                        st.subheader(f"{method.name}()")

                        matrix = method.interference_matrix
                        if method.variables:
                            graph = Graph(method.interference_matrix)
                            st.info(
                                f"**Chromatic Number (Min Register): {graph.get_chromatic_number()}**"
                            )
                            st.caption(
                                "Warna yang berbeda menandakan variabel harus disimpan di register memori yang berbeda."
                            )
                            register_map=graph.get_colors()#ambil dict 
                            df_registers = pd.DataFrame(
                            list(register_map.items()), 
                            columns=['Nama Variabel', 'Register ID (Warna)']
                            )# buat tabelnya dan isi

                            #sorting dengan valuenya
                            df_registers = df_registers.sort_values(by='Register ID (Warna)')

                            st.write("### Detail Pembagian Register")
                            st.dataframe(
                            df_registers, 
                            use_container_width=True, 
                            hide_index=True # Sembunyikan index angka 0,1,2 di kiri tabel
                            )
                            fig = graph.get_figure() ### <--- SIMPAN KE VARIABLE
                            st.pyplot(fig)
                            plt.close(fig)
                            with st.popover("Lihat Matriks Interferensi"):
                                st.dataframe(pd.DataFrame(matrix).astype(bool))
                        else:
                            st.caption("Tidak ada variabel lokal.")
