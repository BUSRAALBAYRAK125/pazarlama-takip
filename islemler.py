from vtclass import Db
import os, shutil
import mysql.connector
pazarlama = Db("pazarlama2")
pazarlama.vt_baglanti()


class MusteriIslemleri:
    def __init__(self):
        self.musteri_id = None

    def musteri_ekleme(self, ad, soyad, tel, adres, isturu, marka,durum):
        if not ad or not soyad or not tel or not adres or not isturu or not marka or not durum:
          raise ValueError("Lütfen bütün alanları doldurun ")
        data = {
            "musteri_ad": ad,
            "musteri_soyad": soyad,
            "musteri_telefon": str(tel).strip(),
            "adres": adres,
            "is_turu": isturu,
            "marka": marka,
            "durum":durum
        }

        pazarlama.kayit_ekle("pazarlama2", "musteri", data)

        sonuc = pazarlama.satir_al("SELECT LAST_INSERT_ID()")
        if not sonuc:
            raise Exception("Müşteri ID alınamadı")

        self.musteri_id = sonuc[0]
    def musteri_id_getir(self, telefon):
        sql = """
    SELECT musteri_id
    FROM musteri
    WHERE musteri_telefon = %s
    """

        sonuc = pazarlama.satir_al(sql, (telefon,))

        if not sonuc:
          return None

        return sonuc[0]
    def fiyat_ekleme(self, fiyat):
        data = {
            "musteri_id": self.musteri_id,
            "tutar_alinacak": fiyat
        }
        pazarlama.kayit_ekle("pazarlama2", "odemeler", data)

    def fiyat_guncelle(self, tutar_alinan, telefon):
        sonuc = pazarlama.satir_al(
            "SELECT musteri_id FROM musteri WHERE musteri_telefon = %s",
            (telefon,)
        )

        if not sonuc:
            raise Exception("Bu telefon numarasına ait müşteri bulunamadı")

        musteri_id = sonuc[0]

        sql = """
        UPDATE odemeler
        SET tutar_alindi = %s
        WHERE musteri_id = %s
        """
        pazarlama.sorgu_calistir(sql, (tutar_alinan, musteri_id))

    def calisan_ekle(self, ad, ):
        data = {
            "calisan_adi": ad,
        }
        pazarlama.kayit_ekle("pazarlama2", "calisanlar", data)

    def is_ekleme(self, pazarlamaci_adi, telefon):
    # 1️⃣ Müşteri ID'yi telefondan al
        sonuc = pazarlama.satir_al(
        "SELECT musteri_id FROM musteri WHERE musteri_telefon = %s",
        (telefon,)
    )

        if not sonuc:
         raise Exception("Bu telefon numarasına ait müşteri bulunamadı")

        musteri_id = sonuc[0]

    # 2️⃣ Pazarlamacı ID
        pazarlamaci = pazarlama.satir_al(
        "SELECT calisan_id FROM calisanlar WHERE calisan_adi = %s",
        (pazarlamaci_adi,)
    )

        if not pazarlamaci:
          raise Exception("Pazarlamacı bulunamadı")

    # 3️⃣ İş ekle
        data = {
        "musteri_id": musteri_id,
        "pazarlamaci_id": pazarlamaci[0]
    }

        pazarlama.kayit_ekle("pazarlama2", "isler", data)


    def musteri_bilgileri_getir(self, telefon):
     sql = """
    SELECT 
        m.musteri_ad,
        m.musteri_soyad,
        m.musteri_telefon,
        m.adres,
        m.is_turu,
        m.marka,
        m.durum,

        o.tutar_alinacak,
        o.tutar_alindi,
        o.kalan_tutar,

        i.tarih,

        c.calisan_adi AS pazarlamaci_adi

    FROM musteri m
    LEFT JOIN odemeler o ON m.musteri_id = o.musteri_id
    LEFT JOIN isler i ON m.musteri_id = i.musteri_id
    LEFT JOIN calisanlar c ON i.calisan_id = c.calisan_id

    WHERE m.musteri_telefon = %s
    """

     rows = pazarlama.satirlari_al(sql, (telefon,))
     if not rows:
        return []

     columns = [c[0] for c in pazarlama._cursor.description]
     return [dict(zip(columns, r)) for r in rows]


    def musterileri_getir(self, adsoyad="", telefon="", marka="", is_turu="", pazarlamaci=""):
     sorgu = """
        SELECT
            CONCAT(m.musteri_ad, ' ', m.musteri_soyad) AS adsoyad,
            m.musteri_telefon AS telefon,
            m.marka,
            m.is_turu,
            c.calisan_adi AS pazarlamaci_adi
        FROM musteri m
        LEFT JOIN isler i ON m.musteri_id = i.musteri_id
        LEFT JOIN calisanlar c ON i.pazarlamaci_id = c.calisan_id
        WHERE 1=1
    """

     parametreler = []

     if adsoyad:
        sorgu += " AND CONCAT(m.musteri_ad, ' ', m.musteri_soyad) LIKE %s"
        parametreler.append(f"%{adsoyad}%")

     if telefon:
        sorgu += " AND m.musteri_telefon LIKE %s"
        parametreler.append(f"%{telefon}%")

     if marka:
        sorgu += " AND m.marka LIKE %s"
        parametreler.append(f"%{marka}%")

     if is_turu:
        sorgu += " AND m.is_turu LIKE %s"
        parametreler.append(f"%{is_turu}%")

     if pazarlamaci:
        sorgu += " AND c.calisan_adi LIKE %s"
        parametreler.append(f"%{pazarlamaci}%")

     return pazarlama.satirlari_al_dict(sorgu, tuple(parametreler))


    def dekontlari_getir(self, musteri_id):
        sql = """
        SELECT 
            dekont_id,
            dosya_yolu,
            yukleme_tarihi
        FROM dekontlar
        WHERE musteri_id = %s
        ORDER BY yukleme_tarihi DESC
    """

        return pazarlama.satirlari_al_dict(sql, (musteri_id,))
    
    def dekont_kaydet(self, musteri_id, secilen_dosya):
        os.makedirs("dekontlar", exist_ok=True)

        dosya_adi = f"{musteri_id}_{os.path.basename(secilen_dosya)}"
        hedef_yol = os.path.join("dekontlar", dosya_adi)

        shutil.copy(secilen_dosya, hedef_yol)

        sql = """
        INSERT INTO dekontlar (musteri_id, dosya_yolu)
        VALUES (%s, %s)
        """
        pazarlama.sorgu_calistir(sql, (musteri_id, hedef_yol))
    def pazarlamacilari_getir(self):
        sorgu="SELECT calisan_adi FROM calisanlar"
        sonuc=pazarlama.satirlari_al(sorgu)
        return [x[0] for x in sonuc]
    def musteri_bilgi_guncelle(self, telefon, ad=None, soyad=None, adres=None, isturu=None, marka=None, durum=None):
  
     data = {}
     if ad is not None:
        data["musteri_ad"] = ad
     if soyad is not None:
        data["musteri_soyad"] = soyad
     if adres is not None:
        data["adres"] = adres
     if isturu is not None:
        data["is_turu"] = isturu
     if marka is not None:
        data["marka"] = marka
     if durum is not None:
        data["durum"] = durum

     if not data:
        return

 
     try:
        pazarlama.guncelle(
            db_name="pazarlama2",
            table_name="musteri",
            data=data,
            kosul="musteri_telefon = %s",
            params=(telefon,)
        )
     except mysql.connector.Error as e:
        raise ValueError(f"Veritabanı hatası: {str(e)}")

    
