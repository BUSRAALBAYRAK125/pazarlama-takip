import mysql.connector

class Db:
    def __init__(self, database):
        self.__host = "localhost"
        self.__user = "root"
        self.__password = ""
        self.__database = database
        self._connection = None
        self._cursor = None
    def vt_baglanti(self):
        """Veritabanına bağlanır ve cursor oluşturur."""
        try:
            self._connection = mysql.connector.connect(
                host=self.__host,
                user=self.__user,
                password=self.__password,
                database=self.__database
            )
            if self._connection.is_connected():
                self._cursor = self._connection.cursor(buffered=True)
                print("Bağlantı başarılı")
        except mysql.connector.Error as e:
            print(f"Bağlantı hatası: {e}")

    def vt_olustur(self, db_name, charset="utf8mb4", collation="utf8mb4_0900_ai_ci"):
        """Yeni veritabanı oluşturur (varsa tekrar oluşturmaz)."""
        sql = f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET {charset} COLLATE {collation}"
        self._cursor.execute(sql)

    def tablo_olustur(self, db_name, table_name, columns):
        """Tablo oluşturur (varsa tekrar oluşturmaz)."""
        self._cursor.execute(f"USE {db_name}")
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns}) ENGINE=InnoDB"
        self._cursor.execute(sql)

    def kayit_ekle(self, db_name, table_name, data: dict):
        """Belirtilen tabloya tek satır ekler."""
        if not data:
            raise ValueError("Eklenecek veri boş olamaz")

        self._cursor.execute(f"USE {db_name}")
        kolonlar = ", ".join(data.keys())
        yertut = ", ".join(["%s"] * len(data))
        degerler = tuple(data.values())
        sql = f"INSERT INTO {table_name} ({kolonlar}) VALUES ({yertut})"
        self._cursor.execute(sql, degerler)
        self._connection.commit()

    def satirlari_al(self, sorgu, params=None):
        """Tüm satırları getirir."""
        self._cursor.execute(sorgu, params or ())
        return self._cursor.fetchall()

    def satir_al(self, sorgu, params=None):
        """Tek satır getirir."""
        self._cursor.execute(sorgu, params or ())
        return self._cursor.fetchone()

    def sorgu_calistir(self, sorgu, params=None):
        """Herhangi bir sorguyu çalıştırır ve commit eder."""
        self._cursor.execute(sorgu, params or ())
        self._connection.commit()
    def guncelle(self, db_name, table_name, data: dict, kosul: str, params: tuple = ()):
     if not data:
        raise ValueError("Güncellenecek veri boş olamaz")

     self._cursor.execute(f"USE {db_name}")
     set_kisim = ", ".join([f"{kolon} = %s" for kolon in data.keys()])
     degerler = tuple(data.values())
     sql = f"UPDATE {table_name} SET {set_kisim} WHERE {kosul}"
     self._cursor.execute(sql, degerler + params)
     self._connection.commit()

    def baglanti_kes(self):
        """Bağlantıyı kapatır."""
        if self._cursor:
            self._cursor.close()
        if self._connection:
            self._connection.close()
            print("Bağlantı kapatıldı")
    def satirlari_al_dict(self, sorgu, params=None):
        cursor = self._connection.cursor(
        buffered=True,
        dictionary=True
      )
        cursor.execute(sorgu, params or ())
        return cursor.fetchall()
