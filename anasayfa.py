import customtkinter as ctk
from islemler import MusteriIslemleri   
from vtclass import Db
from tkinter import ttk
import tkinter as tk
from tkinter import filedialog
import os
import platform
import subprocess
from pathlib import Path

pazarlama = Db("pazarlama2")
pazarlama.vt_baglanti()


musteri_islem = MusteriIslemleri()


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

uygulama = ctk.CTk()
uygulama.title("Pazarlama Yönetim Sistemi")
uygulama.geometry("900x600")

ana_cerceve = ctk.CTkFrame(uygulama)
ana_cerceve.pack(fill="both", expand=True)

sayfa_gecmisi = []  

def cerceveyi_temizle():
    for widget in ana_cerceve.winfo_children():
        widget.destroy()

def sayfa_goster(sayfa_fonksiyonu):
    if sayfa_gecmisi and sayfa_gecmisi[-1] != sayfa_fonksiyonu:
        sayfa_gecmisi.append(sayfa_fonksiyonu)
    cerceveyi_temizle()
    sayfa_fonksiyonu()

def geri_git():
    if len(sayfa_gecmisi) > 1:
        sayfa_gecmisi.pop()
        cerceveyi_temizle()
        sayfa_gecmisi[-1]()

# --- Ana Menü ---
def ana_menu():
    cerceveyi_temizle()
    ctk.CTkLabel(ana_cerceve, text="Ana Menü", font=("Arial", 20)).pack(pady=10)
    ctk.CTkButton(ana_cerceve, text="Yeni Ortaklık", command=lambda: sayfa_goster(yeni_ortaklik)).pack(pady=5)
    ctk.CTkButton(ana_cerceve, text="Çalışan Ekle", command=lambda: sayfa_goster(calisan_ekleme)).pack(pady=5)
    ctk.CTkButton(ana_cerceve, text="Ödeme Yönetimi", command=lambda: sayfa_goster(odeme_yonetimi)).pack(pady=5)
    ctk.CTkButton(ana_cerceve, text="Müşteri Yönetimi", command=lambda: sayfa_goster(musteri_yonetimi)).pack(pady=5)
    ctk.CTkButton(ana_cerceve, text="Müşterilerim", command=lambda: sayfa_goster(musteri_getir)).pack(pady=5)
    ctk.CTkButton(ana_cerceve, text="Dekont İşlemleri", command=lambda: sayfa_goster(dekont_islemleri)).pack(pady=5)
def dekont_islemleri():
    cerceveyi_temizle()

    ctk.CTkLabel(
        ana_cerceve,
        text="Dekont İşlemleri",
        font=("Arial", 20)
    ).pack(pady=30)

    ctk.CTkButton(
        ana_cerceve,
        text="Dekont Görüntüle",
        width=200,
        command=lambda: sayfa_goster(dekont_goruntule_sayfa)
    ).pack(pady=10)

    ctk.CTkButton(
        ana_cerceve,
        text="Dekont Yükle",
        width=200,
        command=lambda: sayfa_goster(dekont_yukle_sayfa)
    ).pack(pady=10)

    ctk.CTkButton(
        ana_cerceve,
        text="Geri",
        command=geri_git
    ).pack(pady=20)
BASE_DIR = Path.home() / "pazarlama_dekontlar"
BASE_DIR.mkdir(exist_ok=True)


def dekont_goruntule_sayfa():
    cerceveyi_temizle()

    ctk.CTkLabel(
        ana_cerceve,
        text="Dekont Görüntüle",
        font=("Arial", 18)
    ).pack(pady=10)

    mesaj_label = ctk.CTkLabel(ana_cerceve, text="")
    mesaj_label.pack(pady=5)

    entry_tel = ctk.CTkEntry(
        ana_cerceve,
        placeholder_text="Telefon Numarası"
    )
    entry_tel.pack(pady=5)

    tablo = ttk.Treeview(
        ana_cerceve,
        columns=("dosya", "tarih", "yol"),
        show="headings",
        height=12
    )

    tablo.heading("dosya", text="Dekont Dosyası")
    tablo.heading("tarih", text="Tarih")
    tablo.heading("yol", text="")

    tablo.column("dosya", width=450, anchor="w")
    tablo.column("tarih", width=150, anchor="center")
    tablo.column("yol", width=0, stretch=False)

    tablo.pack(fill="both", expand=True, padx=10, pady=10)

    scrollbar = ttk.Scrollbar(
        ana_cerceve,
        orient="vertical",
        command=tablo.yview
    )
    tablo.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    def dekontlari_goruntule():
        tablo.delete(*tablo.get_children())

        telefon = entry_tel.get().strip()
        if not telefon:
            mesaj_label.configure(text="Telefon giriniz")
            return

        musteri_id = musteri_islem.musteri_id_getir(telefon)
        if not musteri_id:
            mesaj_label.configure(text="Müşteri bulunamadı")
            return

        dekontlar = musteri_islem.dekontlari_getir(musteri_id)
        if not dekontlar:
            mesaj_label.configure(text="Dekont bulunamadı")
            return

        for d in dekontlar:
            tablo.insert(
                "",
                "end",
                values=(
                    os.path.basename(d["dosya_yolu"]),
                    d["yukleme_tarihi"],
                    d["dosya_yolu"]
                )
            )

        mesaj_label.configure(text=f"{len(dekontlar)} dekont listelendi")

    def dekont_ac(event):
        secili = tablo.focus()
        if not secili:
            return

        degerler = tablo.item(secili, "values")
        dosya_yolu = degerler[2]
        dosya_ac(dosya_yolu)

    tablo.bind("<Double-1>", dekont_ac)

    ctk.CTkButton(
        ana_cerceve,
        text="Dekontları Göster",
        command=dekontlari_goruntule
    ).pack(pady=5)

    ctk.CTkButton(
        ana_cerceve,
        text="Geri",
        command=geri_git
    ).pack(pady=10)


def dosya_ac(dosya_yolu):
    yol = Path(dosya_yolu)

    if not yol.exists():
        return

    sistem = platform.system()
    if sistem == "Windows":
        os.startfile(yol)
    elif sistem == "Darwin":  # macOS
        subprocess.call(["open", str(yol)])
    else:  # Linux
        subprocess.call(["xdg-open", str(yol)])


def dekont_yukle_sayfa():
    cerceveyi_temizle()

    ctk.CTkLabel(
        ana_cerceve,
        text="Dekont Yükle",
        font=("Arial", 18)
    ).pack(pady=10)

    mesaj_label = ctk.CTkLabel(ana_cerceve, text="")
    mesaj_label.pack(pady=5)

    entry_tel = ctk.CTkEntry(
        ana_cerceve,
        placeholder_text="Telefon Numarası"
    )
    entry_tel.pack(pady=5)

    def dekont_yukle():
        telefon = entry_tel.get().strip()
        if not telefon:
            mesaj_label.configure(text="Telefon giriniz")
            return

        musteri_id = musteri_islem.musteri_id_getir(telefon)
        if not musteri_id:
            mesaj_label.configure(text="Müşteri bulunamadı")
            return

        dosya = filedialog.askopenfilename(
            title="Dekont Seç",
            filetypes=[("PDF", "*.pdf"), ("Resim", "*.jpg *.png")]
        )

        if not dosya:
            return

        kaynak = Path(dosya)
        hedef = BASE_DIR / kaynak.name

        if hedef.exists():
            hedef = BASE_DIR / f"{kaynak.stem}_1{kaynak.suffix}"

        hedef.write_bytes(kaynak.read_bytes())

        musteri_islem.dekont_kaydet(musteri_id, str(hedef))
        mesaj_label.configure(text="Dekont başarıyla kaydedildi ✅")

    ctk.CTkButton(
        ana_cerceve,
        text="Dekont Seç ve Kaydet",
        command=dekont_yukle
    ).pack(pady=10)

    ctk.CTkButton(
        ana_cerceve,
        text="Geri",
        command=geri_git
    ).pack(pady=10)

def musteri_getir():
    cerceveyi_temizle()

    # ================= FİLTRE ALANI =================
    filtre_cerceve = ctk.CTkFrame(ana_cerceve)
    filtre_cerceve.pack(fill="x", padx=10, pady=5)

    tk.Label(filtre_cerceve, text="Ad Soyad").grid(row=0, column=0)
    tk.Label(filtre_cerceve, text="Telefon").grid(row=0, column=1)
    tk.Label(filtre_cerceve, text="Marka").grid(row=0, column=2)
    tk.Label(filtre_cerceve, text="İş Türü").grid(row=0, column=3)
    tk.Label(filtre_cerceve, text="Pazarlamacı").grid(row=0, column=4)
    adsoyad_var = tk.StringVar()
    telefon_var = tk.StringVar()
    marka_var = tk.StringVar()
    is_turu_var = tk.StringVar()
    pazarlamaci_var = tk.StringVar()
    tk.Entry(filtre_cerceve, textvariable=adsoyad_var, width=20).grid(row=1, column=0, padx=5)
    tk.Entry(filtre_cerceve, textvariable=telefon_var, width=15).grid(row=1, column=1, padx=5)
    tk.Entry(filtre_cerceve, textvariable=marka_var, width=15).grid(row=1, column=2, padx=5)
    tk.Entry(filtre_cerceve, textvariable=is_turu_var, width=15).grid(row=1, column=3, padx=5)
    tk.Entry(filtre_cerceve, textvariable=pazarlamaci_var, width=15).grid(row=1, column=4, padx=5)

    # ================= TABLO =================
    sutunlar = ("adsoyad", "telefon", "marka", "is_turu", "pazarlamaci")

    tablo = ttk.Treeview(
        ana_cerceve,
        columns=sutunlar,
        show="headings",
        height=12
    )

    tablo.heading("adsoyad", text="Ad Soyad")
    tablo.heading("telefon", text="Telefon")
    tablo.heading("marka", text="Marka")
    tablo.heading("is_turu", text="İş Türü")
    tablo.heading("pazarlamaci", text="Pazarlamacı")

    tablo.column("adsoyad", width=180, anchor="w")
    tablo.column("telefon", width=120, anchor="center")
    tablo.column("marka", width=120, anchor="center")
    tablo.column("is_turu", width=150, anchor="center")
    tablo.column("pazarlamaci", width=150, anchor="center")

    tablo.pack(fill="both", expand=True, padx=10, pady=10)

    # ================= SCROLL =================
    scrollbar = ttk.Scrollbar(ana_cerceve, orient="vertical", command=tablo.yview)
    tablo.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # ================= TABLOYU DOLDUR =================
    def tabloyu_doldur(*args):
        for satir in tablo.get_children():
            tablo.delete(satir)

        veriler = musteri_islem.musterileri_getir(
            adsoyad=adsoyad_var.get(),
            telefon=telefon_var.get(),
            marka=marka_var.get(),
            is_turu=is_turu_var.get(),
            pazarlamaci=pazarlamaci_var.get()
        )

        for veri in veriler:
            tablo.insert(
                "",
                "end",
                values=(
                    veri.get("adsoyad", ""),
                    veri.get("telefon", ""),
                    veri.get("marka", ""),
                    veri.get("is_turu", ""),
                    veri.get("pazarlamaci_adi", "-")
                )
            )

    # ================= FİLTRELER =================
    adsoyad_var.trace_add("write", tabloyu_doldur)
    telefon_var.trace_add("write", tabloyu_doldur)
    marka_var.trace_add("write", tabloyu_doldur)
    is_turu_var.trace_add("write", tabloyu_doldur)
    pazarlamaci_var.trace_add("write", tabloyu_doldur)
    # ================= GERİ BUTONU =================
    ctk.CTkButton(
        ana_cerceve,
        text="Geri",
        command=geri_git
    ).pack(pady=10)

    tabloyu_doldur()


    

def yeni_ortaklik():
    cerceveyi_temizle()

    # Başlık
    ctk.CTkLabel(ana_cerceve, text="Yeni Ortaklık", font=("Arial", 18)).pack(pady=10)
    
    # Mesaj label
    mesaj_label = ctk.CTkLabel(ana_cerceve, text="")
    mesaj_label.pack(pady=10)

    # Müşteri bilgileri Entry’leri
    entry_ad = ctk.CTkEntry(ana_cerceve, placeholder_text="Müşteri Adı"); entry_ad.pack(pady=5)
    entry_soyad = ctk.CTkEntry(ana_cerceve, placeholder_text="Müşteri Soyadı"); entry_soyad.pack(pady=5)
    entry_tel = ctk.CTkEntry(ana_cerceve, placeholder_text="Telefon (10 haneli)"); entry_tel.pack(pady=5)
    entry_fiyat = ctk.CTkEntry(ana_cerceve, placeholder_text="Fiyat"); entry_fiyat.pack(pady=5)

    # Pazarlamacı OptionMenu (veritabanından çekilecek)
    pazarlamacilar_listesi = musteri_islem.pazarlamacilari_getir()
    if not pazarlamacilar_listesi:
        mesaj_label.configure(text="Henüz pazarlamacı bulunamadı! Lütfen önce pazarlamacı ekleyin.", text_color="red")
        return

    selected_pazarlamaci = ctk.StringVar(value=pazarlamacilar_listesi[0])
    optionmenu_pazarlamaci = ctk.CTkOptionMenu(ana_cerceve, variable=selected_pazarlamaci, values=pazarlamacilar_listesi)
    optionmenu_pazarlamaci.pack(pady=5)

    # Diğer bilgiler
    entry_isturu = ctk.CTkEntry(ana_cerceve, placeholder_text="İş Türü "); entry_isturu.pack(pady=5)
    entry_marka = ctk.CTkEntry(ana_cerceve, placeholder_text="Marka"); entry_marka.pack(pady=5)
    entry_adres = ctk.CTkEntry(ana_cerceve, placeholder_text="Adres"); entry_adres.pack(pady=5)

    # İş durumu OptionMenu
    durum_secimi = ctk.StringVar(value="pasif")
    ctk.CTkLabel(ana_cerceve, text="İş Durumu:").pack(pady=(10,0))
    optionmenu_durum = ctk.CTkOptionMenu(ana_cerceve, variable=durum_secimi, values=["pasif", "aktif"])
    optionmenu_durum.pack(pady=5)
   # güvenlik için default


    # Kaydetme fonksiyonu
    def kaydet():
        try:
            ad = entry_ad.get().strip()
            soyad = entry_soyad.get().strip()
            telefon = entry_tel.get().strip()
            adres = entry_adres.get().strip()
            isturu = entry_isturu.get().strip()
            marka = entry_marka.get().strip()
            fiyat = entry_fiyat.get().strip()
            pazarlamaci = selected_pazarlamaci.get()
            durum = durum_secimi.get()
            if not durum:
             durum = "pasif"  

            # Boş alan kontrolü
            if not all([ad, soyad, telefon, adres, isturu, marka, fiyat, pazarlamaci]):
                mesaj_label.configure(text="Lütfen tüm alanları doldurun!", text_color="red")
                return

            # Telefon kontrolü (10 haneli, başında sıfır olabilir)
            if not telefon.isdigit() or len(telefon) != 10:
                mesaj_label.configure(text="Telefon 10 haneli sayı olmalı!", text_color="red")
                return

            # Müşteri ekleme ve diğer işlemler
            musteri_islem.musteri_ekleme(ad, soyad, telefon, adres, isturu, marka, durum)
            musteri_islem.fiyat_ekleme(fiyat)

# Eğer durum aktif ise iş tablosuna ekle
            if durum == "aktif":
             musteri_islem.is_ekleme(pazarlamaci,telefon)

            mesaj_label.configure(text="Yeni ortaklık kaydedildi!", text_color="green")

            # Alanları güvenli şekilde temizle
            for entry in [entry_ad, entry_soyad, entry_tel, entry_fiyat, entry_isturu, entry_marka, entry_adres]:
                try:
                    entry.delete(0, tk.END)
                except:
                    pass
            durum_secimi.set("pasif")

        except Exception:
            mesaj_label.configure(
                text="Bir hata oluştu! Lütfen tüm alanları doğru doldurduğunuzdan emin olun.",
                text_color="red"
            )

    # Butonlar
    ctk.CTkButton(ana_cerceve, text="Kaydet", command=kaydet).pack(pady=10)
    ctk.CTkButton(ana_cerceve, text="Geri", command=geri_git).pack(pady=10)

   
# --- İş Atama ---
def calisan_ekleme():
    ctk.CTkLabel(ana_cerceve, text="İş Atama", font=("Arial", 18)).pack(pady=10)

    entry_calisan = ctk.CTkEntry(ana_cerceve, placeholder_text="Çalışan Adı"); entry_calisan.pack(pady=5)
    

    def ekle():
        musteri_islem.calisan_ekle(entry_calisan.get())
        ctk.CTkLabel(ana_cerceve, text="Çalışan eklendi!").pack(pady=10)

    ctk.CTkButton(ana_cerceve, text="Kaydet", command=ekle).pack(pady=10)
    ctk.CTkButton(ana_cerceve, text="Geri", command=geri_git).pack(pady=10)

# --- Ödeme Yönetimi ---
def odeme_yonetimi():
    ctk.CTkLabel(ana_cerceve, text="Ödeme Yönetimi", font=("Arial", 18)).pack(pady=10)
    mesaj_label = ctk.CTkLabel(ana_cerceve, text="")
    mesaj_label.pack(pady=10)
    entry_tel = ctk.CTkEntry(ana_cerceve, placeholder_text="Telefon"); entry_tel.pack(pady=5)
    entry_tutar = ctk.CTkEntry(ana_cerceve, placeholder_text="Tutar"); entry_tutar.pack(pady=5)

    def guncelle():
      try:
        telefon = entry_tel.get().strip()
        tutar = float(entry_tutar.get())

        musteri_islem.fiyat_guncelle(tutar, telefon)

        mesaj_label.configure(text="Ödeme güncellendi!")
      except ValueError:
        mesaj_label.configure(text="Tutar sayısal olmalı")
      except Exception as e:
        mesaj_label.configure(text=str(e))

    ctk.CTkButton(ana_cerceve, text="Kaydet", command=guncelle).pack(pady=10)
    ctk.CTkButton(ana_cerceve, text="Geri", command=geri_git).pack(pady=10)

# --- Müşteri Yönetimi ---
def musteri_yonetimi():
    cerceveyi_temizle()

    # Başlık
    ctk.CTkLabel(
        ana_cerceve,
        text="Müşteri Yönetimi",
        font=("Arial", 18)
    ).pack(pady=10)

    # Butonlar: Getir ve Güncelle
    frame_buttons = ctk.CTkFrame(ana_cerceve)
    frame_buttons.pack(pady=5)

    def temizle_frame(frame):
        for widget in frame.winfo_children():
            widget.destroy()

    frame_icerik = ctk.CTkFrame(ana_cerceve)
    frame_icerik.pack(pady=10, fill="both", expand=True)

    # ------------------ Bilgileri Getir ------------------
    def bilgileri_getir():
        temizle_frame(frame_icerik)

        entry_tel = ctk.CTkEntry(frame_icerik, placeholder_text="Telefon")
        entry_tel.pack(pady=5)

        label_output = ctk.CTkLabel(frame_icerik, text="", justify="left", font=("Arial", 13))
        label_output.pack(pady=10)

        def getir():
            telefon = entry_tel.get().strip()
            if not telefon:
                label_output.configure(text="Lütfen telefon numarası girin!", text_color="red")
                return

            data = musteri_islem.musteri_bilgileri_getir(telefon)
            if not data:
                label_output.configure(text="Müşteri bulunamadı", text_color="red")
                return

            d = data[0]
            metin = (
                f"Ad: {d['musteri_ad']}\n"
                f"Soyad: {d['musteri_soyad']}\n"
                f"Telefon: {d['musteri_telefon']}\n"
                f"Adres: {d['adres']}\n"
                f"İş Türü: {d['is_turu']}\n"
                f"Marka: {d['marka']}\n"
                f"Durum: {d.get('durum', '-')}\n\n"
                f"Alınacak Tutar: {d.get('tutar_alinacak', '-')}\n"
                f"Alınan Tutar: {d.get('tutar_alindi', '-')}\n"
                f"Kalan Tutar: {d.get('kalan_tutar', '-')}\n"
                f"Tarih: {d.get('tarih', '-')}"
                f"Pazarlamacı: {d.get('pazarlamaci_adi', '-')}\n"

            )
            label_output.configure(text=metin, text_color="black")

        ctk.CTkButton(frame_icerik, text="Bilgileri Getir", command=getir).pack(pady=5)

    # ------------------ Bilgileri Güncelle ------------------
    def bilgileri_guncelle():
        temizle_frame(frame_icerik)

        entry_tel = ctk.CTkEntry(frame_icerik, placeholder_text="Telefon")
        entry_tel.pack(pady=5)

        label_output = ctk.CTkLabel(frame_icerik, text="", justify="left", font=("Arial", 13))
        label_output.pack(pady=10)

        def getir():
            telefon = entry_tel.get().strip()
            if not telefon:
                label_output.configure(text="Lütfen telefon numarası girin!", text_color="red")
                return

            data = musteri_islem.musteri_bilgileri_getir(telefon)
            if not data:
                label_output.configure(text="Müşteri bulunamadı", text_color="red")
                return

            d = data[0]
            eski_durum = d.get("durum", "pasif")  # Eski durumu kaydet

            # Mevcut bilgileri Entry’lere yükle
            entry_ad = ctk.CTkEntry(frame_icerik)
            entry_ad.insert(0, d['musteri_ad'])
            entry_ad.pack(pady=2)

            entry_soyad = ctk.CTkEntry(frame_icerik)
            entry_soyad.insert(0, d['musteri_soyad'])
            entry_soyad.pack(pady=2)

            entry_adres = ctk.CTkEntry(frame_icerik)
            entry_adres.insert(0, d['adres'])
            entry_adres.pack(pady=2)

            entry_isturu = ctk.CTkEntry(frame_icerik)
            entry_isturu.insert(0, d['is_turu'])
            entry_isturu.pack(pady=2)

            entry_marka = ctk.CTkEntry(frame_icerik)
            entry_marka.insert(0, d['marka'])
            entry_marka.pack(pady=2)

            # Fiyat Entry
            entry_fiyat = ctk.CTkEntry(frame_icerik)
            entry_fiyat.insert(0, d.get('tutar_alinacak', ''))
            entry_fiyat.pack(pady=2)

            # Durum OptionMenu
            durum_secimi = ctk.StringVar(value=eski_durum)
            ctk.CTkLabel(frame_icerik, text="Durum:").pack(pady=(5,0))
            optionmenu_durum = ctk.CTkOptionMenu(frame_icerik, variable=durum_secimi, values=["pasif", "aktif"])
            optionmenu_durum.pack(pady=5)

            # ------------------ Güncelle Butonu ------------------
            def guncelle():
                try:
                    telefon_val = entry_tel.get().strip()
                    if not telefon_val.isdigit() or len(telefon_val) != 10:
                        label_output.configure(
                            text="Telefon 10 haneli olmalı ve sadece rakam içermeli!",
                            text_color="red"
                        )
                        return

                    yeni_durum = durum_secimi.get()
                    yeni_fiyat = entry_fiyat.get().strip()

                    # Backend güncellemesi (müşteri bilgileri)
                    musteri_islem.musteri_bilgi_guncelle(
                        telefon=telefon_val,
                        ad=entry_ad.get().strip() or None,
                        soyad=entry_soyad.get().strip() or None,
                        adres=entry_adres.get().strip() or None,
                        isturu=entry_isturu.get().strip() or None,
                        marka=entry_marka.get().strip() or None,
                        durum=yeni_durum
                    )

                    # Fiyat güncelleme
                    if yeni_fiyat:
                        try:
                            musteri_islem.fiyat_guncelle(float(yeni_fiyat), telefon_val)
                        except Exception:
                            label_output.configure(text="Fiyat güncellenemedi!", text_color="red")
                            return

                    # Eğer pasiften aktife geçtiyse iş ekle
                    if eski_durum == "pasif" and yeni_durum == "aktif":
                        pazarlamaci = musteri_islem.pazarlamacilari_getir()[0]  # örnek olarak ilkini al
                        musteri_islem.is_ekleme(pazarlamaci,telefon)

                    label_output.configure(
                        text="Müşteri bilgileri ve fiyat güncellendi!",
                        text_color="green"
                    )

                except ValueError as e:
                    label_output.configure(text=str(e), text_color="red")
                except Exception as e:
                    label_output.configure(text="Bir hata oluştu!", text_color="red")

            ctk.CTkButton(frame_icerik, text="Güncelle", command=guncelle).pack(pady=10)

        ctk.CTkButton(frame_icerik, text="Bilgileri Getir", command=getir).pack(pady=5)

    # ------------------ Üstteki iki buton ------------------
    ctk.CTkButton(frame_buttons, text="Bilgileri Getir", command=bilgileri_getir).pack(side="left", padx=5)
    ctk.CTkButton(frame_buttons, text="Bilgileri Güncelle", command=bilgileri_guncelle).pack(side="left", padx=5)

    # Geri butonu
    ctk.CTkButton(ana_cerceve, text="Geri", command=geri_git).pack(pady=10)


# ilk sayfa
sayfa_gecmisi.append(ana_menu)
ana_menu()

uygulama.mainloop()