import pygame
import sys
import math
import random

# Oyun Ayarları ve Sabitler
GENISLIK = 1000
YUKSEKLIK = 740
FPS = 60

# Renk Paleti
ARKAPLAN = (248, 249, 250)      # Temiz mat beyaz
KOYU_GRI = (33, 37, 41)         # Ana yazılar ve kenarlıklar
MAVI = (9, 132, 227)            # Sol parça / Aktif mod
TURUNCU = (225, 112, 85)        # Çizilen/Tamamlanan parça
KIRMIZI = (214, 48, 49)         # Simetri doğruları
YESIL = (46, 204, 113)          # Başarı durumları
BEYAZ = (255, 255, 255)         # Panel içleri
GRI_ACIK = (220, 224, 230)      # Pasif elemanlar
GRI_GRID = (200, 200, 200)      # Grid çizgileri

# Konfeti Sınıfı (Her iki oyun modu için de ortak görsel ödül)
class Konfeti:
    def __init__(self):
        self.x = random.randint(0, GENISLIK)
        self.y = random.randint(-100, -10)
        self.renk = random.choice([(255, 99, 71), (46, 204, 113), (9, 132, 227), (241, 196, 15), (155, 89, 182)])
        self.boyut = random.randint(5, 12)
        self.hiz_y = random.uniform(2, 6)
        self.hiz_x = random.uniform(-2, 2)

    def hareket_et(self):
        self.y += self.hiz_y
        self.x += self.hiz_x

    def ciz(self, ekran):
        pygame.draw.rect(ekran, self.renk, (self.x, self.y, self.boyut, self.boyut))

class SimetriAtolyesi:
    def __init__(self):
        pygame.init()
        pygame.mixer.init() # Ses sistemi
        self.ekran = pygame.display.set_mode((GENISLIK, YUKSEKLIK))
        pygame.display.set_caption("Matematik Atölyesi: Simetri Avcıları v1.0")
        self.saat = pygame.time.Clock()
        
        # Alkış sesini yükle
        try:
            self.alkis_sesi = pygame.mixer.Sound("alkis.mp3")
            self.ses_yuklendi = True
        except:
            print("Uyarı: 'alkis.mp3' dosyası bulunamadı! Ses devre dışı.")
            self.ses_yuklendi = False
        
        # Fontlar
        self.baslik_font = pygame.font.SysFont("Trebuchet MS", 24, bold=True)
        self.alt_font = pygame.font.SysFont("Trebuchet MS", 18, bold=True)
        self.yazi_font = pygame.font.SysFont("Trebuchet MS", 15)
        
        self.aktif_modul = 1
        self.konfetiler = [] # Ortak konfeti havuzu
        
        # --- MODÜL 1 DEĞİŞKENLERİ (Doğruyu Bul) ---
        self.m1_sekil = "kare"
        self.m1_dogrular = {
            "dikey": {"aktif": False, "cozuldu": False, "rect": None},
            "yatay": {"aktif": False, "cozuldu": False, "rect": None},
            "kosegen1": {"aktif": False, "cozuldu": False, "rect": None},
            "kosegen2": {"aktif": False, "cozuldu": False, "rect": None}
        }
        
        # --- MODÜL 2 DEĞİŞKENLERİ (Oyun / Şıklı) ---
        self.m2_sekil = "kare"
        self.m2_yon = "dikey"
        self.m2_secenekler = [0, 1, 2]
        self.m2_secilen = None
        self.m2_durum_mesaji = "Katlandığında üst üste gelen TAM EŞ olan parçayı seçin."
        self.m2_mesaj_renk = KOYU_GRI
        self.m2_secenek_rectleri = []
        self.m2_btn_yeni = pygame.Rect(100, 470, 200, 45)
        self.m2_yeni_soru()

        # --- MODÜL 3 DEĞİŞKENLERİ (Grid Boyama - 10 Şablon) ---
        self.grid_boyut = 8
        self.hucre_boyutu = 40
        self.grid_sol_x = 200
        self.grid_ust_y = 220
        self.m3_simetri_ekseni = "dikey" 
        self.grid_verisi = [[0 for _ in range(self.grid_boyut)] for _ in range(self.grid_boyut)]
        self.m3_durum_mesaji = "Analiz: Simetri doğrusuna olan mesafeleri sayarak diğer yarıyı boya!"
        self.m3_mesaj_renk = KOYU_GRI
        self.m3_tamamlandi = False
        self.m3_aktif_ornek_index = 0
        self.ses_calindi = False
        
        # 10 Kültürel ve Çocuk Dostu Şablon İsmi
        self.m3_ornek_isimleri = [
            "Kelebek", "Elma", "Robot", "Araba", "Ev", 
            "Çam Ağacı", "Kalp", "Uçak", "Lale Çiçeği", "Kedi"
        ]
        self.m3_ornek_yukle()

        # --- MODÜL 4 DEĞİŞKENLERİ ---
        self.m4_cizilen_acilar = []
        
        self.calisiyor = True

    def m2_yeni_soru(self):
        self.m2_sekil = random.choice(["kare", "dikdortgen"])
        self.m2_yon = random.choice(["dikey", "yatay"])
        self.m2_secilen = None
        self.konfetiler.clear() # Konfetileri yeni soruda sıfırla
        self.m2_durum_mesaji = "Katlandığında üst üste gelen TAM EŞ olan parçayı seçin."
        self.m2_mesaj_renk = KOYU_GRI
        random.shuffle(self.m2_secenekler)
        
        self.m2_secenek_rectleri = []
        start_x = 640
        start_y = 190
        box_w, box_h = 280, 70
        for i in range(3):
            r = pygame.Rect(start_x, start_y + i * (box_h + 15), box_w, box_h)
            self.m2_secenek_rectleri.append(r)

    def m3_ornek_yukle(self):
        self.m3_tamamlandi = False
        self.ses_calindi = False
        self.konfetiler.clear() # Konfetileri yeni soruda sıfırla
        self.m3_durum_mesaji = "Analiz: Simetri doğrusuna olan mesafeleri sayarak diğer yarıyı boya!"
        self.m3_mesaj_renk = KOYU_GRI
        self.grid_verisi = [[0 for _ in range(self.grid_boyut)] for _ in range(self.grid_boyut)]
        
        idx = self.m3_aktif_ornek_index % 10
        
        dikey_sablonlar = [
            [[0,1,1,0],[1,1,1,1],[1,1,1,1],[0,1,1,0],[0,1,1,1],[1,1,1,1],[0,1,1,0],[0,0,0,0]], # Kelebek
            [[0,0,1,0],[0,1,1,0],[1,1,1,1],[1,1,1,1],[1,1,1,1],[1,1,1,1],[0,1,1,0],[0,0,0,0]], # Elma
            [[0,1,1,1],[0,1,0,1],[0,1,1,1],[0,0,1,1],[1,1,1,1],[1,1,1,1],[1,0,1,1],[1,0,0,0]], # Robot
            [[0,0,0,0],[0,0,1,1],[0,1,1,1],[1,1,1,1],[1,1,1,1],[1,0,1,1],[0,1,1,0],[0,0,0,0]], # Araba
            [[0,0,0,1],[0,0,1,1],[0,1,1,1],[1,1,1,1],[0,1,1,1],[0,1,0,1],[0,1,1,1],[0,1,1,1]], # Ev
            [[0,0,0,1],[0,0,1,1],[0,1,1,1],[0,0,1,1],[0,1,1,1],[1,1,1,1],[0,0,0,1],[0,0,0,1]], # Çam Ağacı
            [[0,1,1,0],[1,1,1,1],[1,1,1,1],[0,1,1,1],[0,0,1,1],[0,0,0,1],[0,0,0,0],[0,0,0,0]], # Kalp
            [[0,0,0,1],[0,0,0,1],[0,0,1,1],[1,1,1,1],[0,0,1,1],[0,0,1,1],[0,1,1,1],[0,0,0,0]], # Uçak
            [[0,1,0,1],[0,1,1,1],[0,1,1,1],[0,0,1,1],[0,1,1,0],[0,0,1,1],[0,0,1,0],[0,0,1,0]], # Lale Çiçeği
            [[0,1,0,0],[0,1,1,1],[1,1,1,1],[1,0,1,1],[1,1,1,1],[0,1,1,1],[0,0,1,1],[0,0,0,0]]  # Kedi
        ]
        
        yatay_sablonlar = [
            [[1,1,0,0,0,0,1,1],[1,1,1,0,0,1,1,1],[0,1,1,1,1,1,1,0],[0,0,1,1,1,1,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]],
            [[0,0,0,1,1,0,0,0],[0,1,1,1,1,1,1,0],[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]],
            [[0,1,1,0,0,1,1,0],[0,1,1,1,1,1,1,0],[0,1,0,1,1,0,1,0],[0,1,1,1,1,1,1,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]],
            [[0,0,1,1,1,1,0,0],[0,1,1,1,1,1,1,0],[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]],
            [[0,0,0,1,1,0,0,0],[0,0,1,1,1,1,0,0],[0,1,1,1,1,1,1,0],[1,1,1,1,1,1,1,1],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]],
            [[0,0,0,1,1,0,0,0],[0,0,1,1,1,1,0,0],[0,1,1,1,1,1,1,0],[1,1,1,1,1,1,1,1],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]],
            [[0,1,1,0,0,1,1,0],[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1],[0,1,1,1,1,1,1,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]],
            [[0,0,0,1,1,0,0,0],[1,1,1,1,1,1,1,1],[0,0,0,1,1,0,0,0],[0,0,1,1,1,1,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]],
            [[1,0,0,0,0,0,0,1],[1,1,0,0,0,0,1,1],[0,1,1,1,1,1,1,0],[0,0,1,1,1,1,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]],
            [[1,0,0,0,0,0,0,1],[1,1,0,0,0,0,1,1],[1,1,1,1,1,1,1,1],[0,1,1,1,1,1,1,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]]
        ]
        
        if self.m3_simetri_ekseni == "dikey":
            sablon = dikey_sablonlar[idx]
            for r in range(self.grid_boyut):
                for c in range(4):
                    self.grid_verisi[r][c] = sablon[r][c]
        else:
            sablon = yatay_sablonlar[idx]
            for r in range(4):
                for c in range(self.grid_boyut):
                    self.grid_verisi[r][c] = sablon[r][c]

    def m3_kontrol_et(self):
        hata_var = False
        eksik_var = False
        
        if self.m3_simetri_ekseni == "dikey":
            for r in range(self.grid_boyut):
                for c in range(4):
                    sol_deger = self.grid_verisi[r][c]
                    sag_deger = self.grid_verisi[r][7 - c]
                    if sol_deger == 1 and sag_deger != 2:
                        eksik_var = True
                    elif sol_deger == 0 and sag_deger == 2:
                        hata_var = True
        else:
            for r in range(4):
                for c in range(self.grid_boyut):
                    ust_deger = self.grid_verisi[r][c]
                    alt_deger = self.grid_verisi[7 - r][c]
                    if ust_deger == 1 and alt_deger != 2:
                        eksik_var = True
                    elif ust_deger == 0 and alt_deger == 2:
                        hata_var = True
                        
        if hata_var:
            self.m3_durum_mesaji = "İnceleme: Bazı boyadığın kareler simetri eksenine eşit mesafede değil!"
            self.m3_mesaj_renk = KIRMIZI
            self.m3_tamamlandi = False
        elif eksik_var:
            self.m3_durum_mesaji = "İnceleme: Şeklin tüm eş parçaları henüz tamamlanmadı."
            self.m3_mesaj_renk = MAVI
            self.m3_tamamlandi = False
        else:
            self.m3_durum_mesaji = "TEBRİKLER! Şekli simetri doğrusuna göre kusursuz tamamladın! 🌟"
            self.m3_mesaj_renk = YESIL
            self.m3_tamamlandi = True
            
            if self.ses_yuklendi and not self.ses_calindi:
                self.alkis_sesi.play()
                self.ses_calindi = True

    def olaylari_yonet(self):
        for olay in pygame.event.get():
            if olay.type == pygame.QUIT:
                self.calisiyor = False
                
            elif olay.type == pygame.MOUSEBUTTONDOWN:
                pos = olay.pos
                
                # Sekme Seçimleri
                if self.tab1_rect.collidepoint(pos):
                    self.aktif_modul = 1
                    self.konfetiler.clear()
                elif self.tab2_rect.collidepoint(pos):
                    self.aktif_modul = 2
                    self.m2_yeni_soru()
                elif self.tab3_rect.collidepoint(pos):
                    self.aktif_modul = 3
                    self.m3_ornek_yukle()
                elif self.tab4_rect.collidepoint(pos):
                    self.aktif_modul = 4
                    self.konfetiler.clear()

                # Modüllere Özel Tıklama Olayları
                if self.aktif_modul == 1:
                    self.m1_tiklama_kontrol(pos)
                elif self.aktif_modul == 2:
                    self.m2_tiklama_kontrol(pos)
                elif self.aktif_modul == 3:
                    self.m3_tiklama_kontrol(pos)
                elif self.aktif_modul == 4:
                    self.m4_tiklama_kontrol(pos)

    def m1_tiklama_kontrol(self, pos):
        if self.m1_btn_kare.collidepoint(pos):
            self.m1_sekil = "kare"
            self.m1_sifirla()
        elif self.m1_btn_dik.collidepoint(pos):
            self.m1_sekil = "dikdortgen"
            self.m1_sifirla()
            
        for anahtar, deger in self.m1_dogrular.items():
            if self.m1_sekil == "dikdortgen" and "kosegen" in anahtar:
                continue
            if deger["rect"] and deger["rect"].collidepoint(pos):
                deger["cozuldu"] = True
                deger["aktif"] = not deger["aktif"]

    def m1_sifirla(self):
        for k in self.m1_dogrular:
            self.m1_dogrular[k]["aktif"] = False
            self.m1_dogrular[k]["cozuldu"] = False

    def m2_tiklama_kontrol(self, pos):
        if self.m2_secilen is None:
            for i, rect in enumerate(self.m2_secenek_rectleri):
                if rect.collidepoint(pos):
                    self.m2_secilen = i
                    gercek_kimlik = self.m2_secenekler[i]
                    if gercek_kimlik == 0:
                        self.m2_durum_mesaji = "Doğru! Simetri doğrusu şekli birebir eş iki parçaya ayırır."
                        self.m2_mesaj_renk = YESIL
                        if self.ses_yuklendi:
                            self.alkis_sesi.play()
                    elif gercek_kimlik == 1:
                        self.m2_durum_mesaji = "Hata: Parçanın yönü yanlış. Simetrik parçalar birbirinin yansımasıdır!"
                        self.m2_mesaj_renk = KIRMIZI
                    else:
                        self.m2_durum_mesaji = "Hata: Boyutlar farklı. Simetrik iki parça birebir eş olmalıdır!"
                        self.m2_mesaj_renk = KIRMIZI
        else:
            if self.m2_btn_yeni.collidepoint(pos):
                self.m2_yeni_soru()

    def m3_tiklama_kontrol(self, pos):
        if pygame.Rect(640, 220, 140, 40).collidepoint(pos):
            self.m3_simetri_ekseni = "dikey"
            self.m3_ornek_yukle()
            return
        elif pygame.Rect(790, 220, 140, 40).collidepoint(pos):
            self.m3_simetri_ekseni = "yatay"
            self.m3_ornek_yukle()
            return

        if pygame.Rect(640, 420, 140, 40).collidepoint(pos):
            self.m3_ornek_yukle()
            return
            
        if pygame.Rect(640, 475, 290, 40).collidepoint(pos):
            self.m3_aktif_ornek_index += 1
            self.m3_ornek_yukle()
            return
        
        x, y = pos
        col = (x - self.grid_sol_x) // self.hucre_boyutu
        row = (y - self.grid_ust_y) // self.hucre_boyutu
        
        if 0 <= col < self.grid_boyut and 0 <= row < self.grid_boyut:
            if self.m3_simetri_ekseni == "dikey" and col >= 4:
                mevcut = self.grid_verisi[row][col]
                self.grid_verisi[row][col] = 2 if mevcut == 0 else 0
                self.m3_kontrol_et()
            elif self.m3_simetri_ekseni == "yatay" and row >= 4:
                mevcut = self.grid_verisi[row][col]
                self.grid_verisi[row][col] = 2 if mevcut == 0 else 0
                self.m3_kontrol_et()

    def m4_tiklama_kontrol(self, pos):
        cx, cy = 500, 380
        r = 160
        dx = pos[0] - cx
        dy = pos[1] - cy
        mesafe = (dx**2 + dy**2)**0.5
        
        if mesafe <= r and mesafe > 10:
            aci = math.atan2(dy, dx)
            aci_derece = math.degrees(aci)
            
            benzer_var = False
            for a in self.m4_cizilen_acilar:
                if abs(a - aci_derece) < 5 or abs(abs(a - aci_derece) - 180) < 5:
                    benzer_var = True
                    break
            if not benzer_var:
                self.m4_cizilen_acilar.append(aci_derece)
                
        if pygame.Rect(50, 640, 160, 40).collidepoint(pos):
            self.m4_cizilen_acilar.clear()

    def arayuz_ciz(self):
        self.ekran.fill(ARKAPLAN)
        baslik = self.baslik_font.render("GEOMETRİK ŞEKİLLERDE SİMETRİ LABORATUVARI", True, KOYU_GRI)
        self.ekran.blit(baslik, (30, 20))
        
        self.tab1_rect = pygame.Rect(15, 80, 235, 45)
        self.tab2_rect = pygame.Rect(260, 80, 235, 45)
        self.tab3_rect = pygame.Rect(505, 80, 235, 45)
        self.tab4_rect = pygame.Rect(750, 80, 235, 45)
        
        pygame.draw.rect(self.ekran, MAVI if self.aktif_modul == 1 else GRI_ACIK, self.tab1_rect, border_radius=5)
        pygame.draw.rect(self.ekran, MAVI if self.aktif_modul == 2 else GRI_ACIK, self.tab2_rect, border_radius=5)
        pygame.draw.rect(self.ekran, MAVI if self.aktif_modul == 3 else GRI_ACIK, self.tab3_rect, border_radius=5)
        pygame.draw.rect(self.ekran, MAVI if self.aktif_modul == 4 else GRI_ACIK, self.tab4_rect, border_radius=5)
        
        txt1 = self.yazi_font.render("1. Simetri Ekseni Bul", True, BEYAZ if self.aktif_modul == 1 else KOYU_GRI)
        txt2 = self.yazi_font.render("2. Eş Parçayı Seç (Oyun)", True, BEYAZ if self.aktif_modul == 2 else KOYU_GRI)
        txt3 = self.yazi_font.render("3. Kendin Çiz & Tamamla", True, BEYAZ if self.aktif_modul == 3 else KOYU_GRI)
        txt4 = self.yazi_font.render("4. Dairede Sonsuz Simetri", True, BEYAZ if self.aktif_modul == 4 else KOYU_GRI)
        
        self.ekran.blit(txt1, (self.tab1_rect.centerx - txt1.get_width()//2, self.tab1_rect.centery - txt1.get_height()//2))
        self.ekran.blit(txt2, (self.tab2_rect.centerx - txt2.get_width()//2, self.tab2_rect.centery - txt2.get_height()//2))
        self.ekran.blit(txt3, (self.tab3_rect.centerx - txt3.get_width()//2, self.tab3_rect.centery - txt3.get_height()//2))
        self.ekran.blit(txt4, (self.tab4_rect.centerx - txt4.get_width()//2, self.tab4_rect.centery - txt4.get_height()//2))

    def mod1_ciz(self):
        self.m1_btn_kare = pygame.Rect(50, 160, 120, 40)
        self.m1_btn_dik = pygame.Rect(180, 160, 150, 40)
        
        pygame.draw.rect(self.ekran, MAVI if self.m1_sekil == "kare" else GRI_ACIK, self.m1_btn_kare, border_radius=5)
        pygame.draw.rect(self.ekran, MAVI if self.m1_sekil == "dikdortgen" else GRI_ACIK, self.m1_btn_dik, border_radius=5)
        
        t_kare = self.alt_font.render("Kare", True, BEYAZ if self.m1_sekil == "kare" else KOYU_GRI)
        t_dik = self.alt_font.render("Dikdörtgen", True, BEYAZ if self.m1_sekil == "dikdortgen" else KOYU_GRI)
        self.ekran.blit(t_kare, (self.m1_btn_kare.centerx - t_kare.get_width()//2, self.m1_btn_kare.centery - t_kare.get_height()//2))
        self.ekran.blit(t_dik, (self.m1_btn_dik.centerx - t_dik.get_width()//2, self.m1_btn_dik.centery - t_dik.get_height()//2))
        
        yonerge = self.yazi_font.render("Görev: Şeklin üzerine tıklayarak tüm geçerli simetri doğrularını aktif edin.", True, KOYU_GRI)
        self.ekran.blit(yonerge, (50, 220))
        
        cx, cy = 500, 420
        w, h = (240, 240) if self.m1_sekil == "kare" else (360, 200)
        rect_coords = (cx - w//2, cy - h//2, w, h)
        
        pygame.draw.rect(self.ekran, BEYAZ, rect_coords)
        pygame.draw.rect(self.ekran, KOYU_GRI, rect_coords, 3)
        
        self.m1_dogrular["dikey"]["rect"] = pygame.Rect(cx - 15, cy - h//2 - 30, 30, h + 60)
        if self.m1_dogrular["dikey"]["aktif"]:
            pygame.draw.rect(self.ekran, MAVI, (cx - w//2, cy - h//2, w//2, h), 0)
            pygame.draw.rect(self.ekran, TURUNCU, (cx, cy - h//2, w//2, h), 0)
            pygame.draw.rect(self.ekran, KOYU_GRI, rect_coords, 3)
            pygame.draw.line(self.ekran, KIRMIZI, (cx, cy - h//2 - 30), (cx, cy + h//2 + 30), 4)

        self.m1_dogrular["yatay"]["rect"] = pygame.Rect(cx - w//2 - 30, cy - 15, w + 60, 30)
        if self.m1_dogrular["yatay"]["aktif"]:
            pygame.draw.rect(self.ekran, MAVI, (cx - w//2, cy - h//2, w, h//2), 0)
            pygame.draw.rect(self.ekran, TURUNCU, (cx - w//2, cy, w, h//2), 0)
            pygame.draw.rect(self.ekran, KOYU_GRI, rect_coords, 3)
            pygame.draw.line(self.ekran, KIRMIZI, (cx - w//2 - 30, cy), (cx + w//2 + 30, cy), 4)
            
        if self.m1_sekil == "kare":
            self.m1_dogrular["kosegen1"]["rect"] = pygame.Rect(cx - w//2 - 20, cy - h//2 - 20, 40, 40)
            self.m1_dogrular["kosegen2"]["rect"] = pygame.Rect(cx + w//2 - 20, cy - h//2 - 20, 40, 40)
            
            if self.m1_dogrular["kosegen1"]["aktif"]:
                pts_mavi = [(cx - w//2, cy - h//2), (cx - w//2, cy + h//2), (cx + w//2, cy + h//2)]
                pts_turuncu = [(cx - w//2, cy - h//2), (cx + w//2, cy - h//2), (cx + w//2, cy + h//2)]
                pygame.draw.polygon(self.ekran, MAVI, pts_mavi)
                pygame.draw.polygon(self.ekran, TURUNCU, pts_turuncu)
                pygame.draw.rect(self.ekran, KOYU_GRI, rect_coords, 3)
                pygame.draw.line(self.ekran, KIRMIZI, (cx - w//2 - 30, cy - h//2 - 30), (cx + w//2 + 30, cy + h//2 + 30), 4)
                
            if self.m1_dogrular["kosegen2"]["aktif"]:
                pts_mavi = [(cx - w//2, cy - h//2), (cx + w//2, cy - h//2), (cx - w//2, cy + h//2)]
                pts_turuncu = [(cx - w//2, cy + h//2), (cx + w//2, cy - h//2), (cx + w//2, cy + h//2)]
                pygame.draw.polygon(self.ekran, MAVI, pts_mavi)
                pygame.draw.polygon(self.ekran, TURUNCU, pts_turuncu)
                pygame.draw.rect(self.ekran, KOYU_GRI, rect_coords, 3)
                pygame.draw.line(self.ekran, KIRMIZI, (cx + w//2 + 30, cy - h//2 - 30), (cx - w//2 - 30, cy + h//2 + 30), 4)
                
            pygame.draw.circle(self.ekran, GRI_ACIK, (cx - w//2, cy - h//2), 12)
            pygame.draw.circle(self.ekran, GRI_ACIK, (cx + w//2, cy - h//2), 12)
            
        pygame.draw.circle(self.ekran, GRI_ACIK, (cx, cy - h//2), 12)
        pygame.draw.circle(self.ekran, GRI_ACIK, (cx - w//2, cy), 12)
        
        bilgi_rect = pygame.Rect(50, 610, 900, 80)
        pygame.draw.rect(self.ekran, BEYAZ, bilgi_rect, border_radius=8)
        pygame.draw.rect(self.ekran, KOYU_GRI, bilgi_rect, 2, border_radius=8)
        
        if self.m1_sekil == "kare":
            b_satir1 = "• KARE: Tam 4 adet simetri doğrusuna sahiptir (1 dikey, 1 yatay, 2 köşegen)."
            b_satir2 = "• Köşegenler boyunca katlandığında oluşan üçgenler birbirine TAM EŞTİR."
        else:
            b_satir1 = "• DİKDÖRTGEN: Sadece 2 adet simetri doğrusuna sahiptir (1 dikey, 1 yatay)."
            b_satir2 = "• ÖNEMLİ: Dikdörtgenin köşegenleri birer simetri doğrusu değildir!"
            
        self.ekran.blit(self.yazi_font.render(b_satir1, True, KOYU_GRI), (70, 625))
        self.ekran.blit(self.yazi_font.render(b_satir2, True, KIRMIZI if self.m1_sekil == "dikdortgen" else KOYU_GRI), (70, 652))

    def mod2_ciz(self):
        self.ekran.blit(self.alt_font.render(self.m2_durum_mesaji, True, self.m2_mesaj_renk), (50, 150))
        
        cx, cy = 350, 320
        w, h = (200, 200) if self.m2_sekil == "kare" else (260, 160)
        
        pygame.draw.rect(self.ekran, BEYAZ, (100, 190, 500, 260), border_radius=8)
        pygame.draw.rect(self.ekran, KOYU_GRI, (100, 190, 500, 260), 2, border_radius=8)
        
        dogru_secildi = False
        if self.m2_secilen is not None:
            dogru_secildi = (self.m2_secenekler[self.m2_secilen] == 0)
            
        if self.m2_yon == "dikey":
            pygame.draw.rect(self.ekran, MAVI, (cx - w//2, cy - h//2, w//2, h))
            pygame.draw.rect(self.ekran, KOYU_GRI, (cx - w//2, cy - h//2, w//2, h), 3)
            if dogru_secildi:
                pygame.draw.rect(self.ekran, TURUNCU, (cx, cy - h//2, w//2, h))
                pygame.draw.rect(self.ekran, KOYU_GRI, (cx, cy - h//2, w//2, h), 3)
            pygame.draw.line(self.ekran, KIRMIZI, (cx, cy - h//2 - 20), (cx, cy + h//2 + 20), 4)
        else:
            pygame.draw.rect(self.ekran, MAVI, (cx - w//2, cy - h//2, w, h//2))
            pygame.draw.rect(self.ekran, KOYU_GRI, (cx - w//2, cy - h//2, w, h//2), 3)
            if dogru_secildi:
                pygame.draw.rect(self.ekran, TURUNCU, (cx - w//2, cy, w, h//2))
                pygame.draw.rect(self.ekran, KOYU_GRI, (cx - w//2, cy, w, h//2), 3)
            pygame.draw.line(self.ekran, KIRMIZI, (cx - w//2 - 20, cy), (cx + w//2 + 20, cy), 4)
            
        sw, sh = (50, 50) if self.m2_sekil == "kare" else (70, 42)
        
        for i, kimlik in enumerate(self.m2_secenekler):
            r = self.m2_secenek_rectleri[i]
            k_renk = BEYAZ
            if self.m2_secilen is not None:
                if kimlik == 0:
                    k_renk = (212, 239, 223)
                elif self.m2_secilen == i:
                    k_renk = (242, 215, 213)
                    
            pygame.draw.rect(self.ekran, k_renk, r, border_radius=6)
            pygame.draw.rect(self.ekran, KOYU_GRI, r, 2, border_radius=6)
            
            harf = ["A", "B", "C"][i]
            self.ekran.blit(self.alt_font.render(f"{harf} Seçeneği", True, KOYU_GRI), (r.x + 15, r.y + 22))
            
            scx, scy = r.x + 210, r.centery
            if self.m2_yon == "dikey":
                if kimlik == 0:
                    pygame.draw.rect(self.ekran, TURUNCU, (scx - sw//4, scy - sh//2, sw//2, sh))
                    pygame.draw.rect(self.ekran, KOYU_GRI, (scx - sw//4, scy - sh//2, sw//2, sh), 2)
                elif kimlik == 1:
                    pygame.draw.rect(self.ekran, TURUNCU, (scx - sh//2, scy - sw//4, sh, sw//2))
                    pygame.draw.rect(self.ekran, KOYU_GRI, (scx - sh//2, scy - sw//4, sh, sw//2), 2)
                elif kimlik == 2:
                    pygame.draw.rect(self.ekran, TURUNCU, (scx - sw//6, scy - sh//3, sw//3, sh//1.5))
                    pygame.draw.rect(self.ekran, KOYU_GRI, (scx - sw//6, scy - sh//3, sw//3, sh//1.5), 2)
            else:
                if kimlik == 0:
                    pygame.draw.rect(self.ekran, TURUNCU, (scx - sw//2, scy - sh//4, sw, sh//2))
                    pygame.draw.rect(self.ekran, KOYU_GRI, (scx - sw//2, scy - sh//4, sw, sh//2), 2)
                elif kimlik == 1:
                    pygame.draw.rect(self.ekran, TURUNCU, (scx - sh//4, scy - sw//2, sh//2, sw))
                    pygame.draw.rect(self.ekran, KOYU_GRI, (scx - sh//4, scy - sw//2, sh//2, sw), 2)
                elif kimlik == 2:
                    pygame.draw.rect(self.ekran, TURUNCU, (scx - sw//3, scy - sh//6, sw//1.5, sh//3))
                    pygame.draw.rect(self.ekran, KOYU_GRI, (scx - sw//3, scy - sh//6, sw//1.5, sh//3), 2)
                    
        if self.m2_secilen is not None:
            pygame.draw.rect(self.ekran, MAVI, self.m2_btn_yeni, border_radius=6)
            txt = self.alt_font.render("Sonraki Örnek", True, BEYAZ)
            self.ekran.blit(txt, (self.m2_btn_yeni.centerx - txt.get_width()//2, self.m2_btn_yeni.centery - txt.get_height()//2))

        # Modül 2 Konfeti Yağmuru
        if dogru_secildi:
            if len(self.konfetiler) < 120:
                self.konfetiler.append(Konfeti())
            for k in self.konfetiler:
                k.hareket_et()
                k.ciz(self.ekran)
            
        bilgi_rect = pygame.Rect(50, 540, 900, 150)
        pygame.draw.rect(self.ekran, BEYAZ, bilgi_rect, border_radius=8)
        pygame.draw.rect(self.ekran, KOYU_GRI, bilgi_rect, 2, border_radius=8)
        
        self.ekran.blit(self.alt_font.render("💡 Simetri Kuralı ve Eşlik İlişkisi:", True, MAVI), (70, 555))
        self.ekran.blit(self.yazi_font.render("1. Bir şeklin simetri doğrusuna göre oluşan iki parçası birbirine tam olarak EŞTİR.", True, KOYU_GRI), (70, 590))
        self.ekran.blit(self.yazi_font.render("2. Eş parçaların boyutları (alanları) ve biçimleri aynıdır; fakat yönleri simetri eksenine göre terstir.", True, KOYU_GRI), (70, 615))
        self.ekran.blit(self.yazi_font.render("3. Doğru şıkkı seçtiğinizde şekil otomatik tamamlanacak ve konfetiler patlayacaktır!", True, YESIL), (70, 640))

    def mod3_ciz(self):
        self.ekran.blit(self.alt_font.render(self.m3_durum_mesaji, True, self.m3_mesaj_renk), (50, 150))
        
        btn_dikey = pygame.Rect(640, 220, 140, 40)
        btn_yatay = pygame.Rect(790, 220, 140, 40)
        
        pygame.draw.rect(self.ekran, MAVI if self.m3_simetri_ekseni == "dikey" else GRI_ACIK, btn_dikey, border_radius=5)
        pygame.draw.rect(self.ekran, MAVI if self.m3_simetri_ekseni == "yatay" else GRI_ACIK, btn_yatay, border_radius=5)
        
        self.ekran.blit(self.yazi_font.render("Dikey Simetri", True, BEYAZ if self.m3_simetri_ekseni == "dikey" else KOYU_GRI), (665, 230))
        self.ekran.blit(self.yazi_font.render("Yatay Simetri", True, BEYAZ if self.m3_simetri_ekseni == "yatay" else KOYU_GRI), (815, 230))
        
        for r in range(self.grid_boyut):
            for c in range(self.grid_boyut):
                x = self.grid_sol_x + c * self.hucre_boyutu
                y = self.grid_ust_y + r * self.hucre_boyutu
                hucre_rect = pygame.Rect(x, y, self.hucre_boyutu, self.hucre_boyutu)
                
                durum = self.grid_verisi[r][c]
                if durum == 1:
                    pygame.draw.rect(self.ekran, MAVI, hucre_rect)
                elif durum == 2:
                    pygame.draw.rect(self.ekran, TURUNCU, hucre_rect)
                else:
                    pygame.draw.rect(self.ekran, BEYAZ, hucre_rect)
                    
                pygame.draw.rect(self.ekran, GRI_GRID, hucre_rect, 1)

        if self.m3_simetri_ekseni == "dikey":
            mid_x = self.grid_sol_x + 4 * self.hucre_boyutu
            pygame.draw.line(self.ekran, KIRMIZI, (mid_x, self.grid_ust_y - 20), (mid_x, self.grid_ust_y + 8 * self.hucre_boyutu + 20), 4)
        else:
            mid_y = self.grid_ust_y + 4 * self.hucre_boyutu
            pygame.draw.line(self.ekran, KIRMIZI, (self.grid_sol_x - 20, mid_y), (self.grid_sol_x + 8 * self.hucre_boyutu + 20, mid_y), 4)

        btn_reset = pygame.Rect(640, 420, 140, 40)
        pygame.draw.rect(self.ekran, KIRMIZI, btn_reset, border_radius=5)
        self.ekran.blit(self.yazi_font.render("Tümünü Sıfırla", True, BEYAZ), (665, 430))

        btn_ornek_degis = pygame.Rect(640, 475, 290, 40)
        pygame.draw.rect(self.ekran, YESIL if self.m3_tamamlandi else KOYU_GRI, btn_ornek_degis, border_radius=5)
        self.ekran.blit(self.alt_font.render("➡️ Başka Şablona Geç", True, BEYAZ), (710, 485))

        analiz_rect = pygame.Rect(640, 280, 290, 120)
        pygame.draw.rect(self.ekran, BEYAZ, analiz_rect, border_radius=8)
        pygame.draw.rect(self.ekran, KOYU_GRI, analiz_rect, 2, border_radius=8)
        self.ekran.blit(self.alt_font.render("🕵️ MANTIKSAL ANALİZ", True, KOYU_GRI), (655, 295))
        
        aktif_sablon_ismi = self.m3_ornek_isimleri[self.m3_aktif_ornek_index % 10]
        
        if self.m3_simetri_ekseni == "dikey":
            info1 = "- Sol taraftaki şeklin sağ yarısını"
            info2 = "  simetri eksenine göre boya."
            info3 = f"- Şekil: {aktif_sablon_ismi} ({self.m3_aktif_ornek_index % 10 + 1}/10)"
        else:
            info1 = "- Üst taraftaki şeklin alt yarısını"
            info2 = "  simetri eksenine göre boya."
            info3 = f"- Şekil: {aktif_sablon_ismi} ({self.m3_aktif_ornek_index % 10 + 1}/10)"
            
        self.ekran.blit(self.yazi_font.render(info1, True, KOYU_GRI), (655, 325))
        self.ekran.blit(self.yazi_font.render(info2, True, KOYU_GRI), (655, 345))
        self.ekran.blit(self.yazi_font.render(info3, True, MAVI), (655, 370))

        # Modül 3 Konfeti Yağmuru
        if self.m3_tamamlandi:
            if len(self.konfetiler) < 120:
                self.konfetiler.append(Konfeti())
            for k in self.konfetiler:
                k.hareket_et()
                k.ciz(self.ekran)

        bilgi_rect = pygame.Rect(50, 580, 900, 110)
        pygame.draw.rect(self.ekran, BEYAZ, bilgi_rect, border_radius=8)
        pygame.draw.rect(self.ekran, KOYU_GRI, bilgi_rect, 2, border_radius=8)
        self.ekran.blit(self.alt_font.render("💡 Çizim Rehberi:", True, MAVI), (70, 595))
        self.ekran.blit(self.yazi_font.render("• 'Başka Şablona Geç' butonuna basarak kedi, robot, kelebek veya lale çiçeğini dikey/yatay modda tamamlayabilirsin.", True, KOYU_GRI), (70, 625))
        self.ekran.blit(self.yazi_font.render("• Doğru tamamladığında konfetiler patlayacak ve alkış sesi gelecektir!", True, YESIL), (70, 650))

    def mod4_ciz(self):
        self.ekran.blit(self.alt_font.render("Dairenin üzerine tıklayarak yeni simetri doğruları çizin.", True, KOYU_GRI), (50, 150))
        self.ekran.blit(self.yazi_font.render(f"Çizilen Simetri Doğrusu Sayısı: {len(self.m4_cizilen_acilar)}", True, MAVI), (50, 185))
        
        cx, cy = 500, 380
        r = 160
        pygame.draw.circle(self.ekran, BEYAZ, (cx, cy), r)
        pygame.draw.circle(self.ekran, KOYU_GRI, (cx, cy), r, 3)
        pygame.draw.circle(self.ekran, KIRMIZI, (cx, cy), 6)
        
        for aci in self.m4_cizilen_acilar:
            rad = math.radians(aci)
            x1 = cx + (r + 30) * math.cos(rad)
            y1 = cy + (r + 30) * math.sin(rad)
            x2 = cx - (r + 30) * math.cos(rad)
            y2 = cy - (r + 30) * math.sin(rad)
            pygame.draw.line(self.ekran, KIRMIZI, (x1, y1), (x2, y2), 3)
            
        btn_temizle = pygame.Rect(50, 640, 160, 40)
        pygame.draw.rect(self.ekran, KIRMIZI, btn_temizle, border_radius=5)
        txt = self.alt_font.render("Tümünü Temizle", True, BEYAZ)
        self.ekran.blit(txt, (btn_temizle.centerx - txt.get_width()//2, btn_temizle.centery - txt.get_height()//2))
        
        bilgi_rect = pygame.Rect(230, 580, 720, 100)
        pygame.draw.rect(self.ekran, BEYAZ, bilgi_rect, border_radius=8)
        pygame.draw.rect(self.ekran, KOYU_GRI, bilgi_rect, 2, border_radius=8)
        
        d_satir1 = "• DAİRE: Merkezinden geçen HER DOĞRU birer simetri doğrusudur."
        d_satir2 = "• Dairenin SONSUZ sayıda simetri doğrusu vardır."
        
        self.ekran.blit(self.yazi_font.render(d_satir1, True, KOYU_GRI), (250, 595))
        self.ekran.blit(self.yazi_font.render(d_satir2, True, MAVI), (250, 620))

    def calistir(self):
        while self.calisiyor:
            self.olaylari_yonet()
            self.arayuz_ciz()
            
            if self.aktif_modul == 1:
                self.mod1_ciz()
            elif self.aktif_modul == 2:
                self.mod2_ciz()
            elif self.aktif_modul == 3:
                self.mod3_ciz()
            elif self.aktif_modul == 4:
                self.mod4_ciz()
                
            self.saat.tick(FPS)
            pygame.display.flip()
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    atolye = SimetriAtolyesi()
    atolye.calistir()