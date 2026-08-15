#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# enquiry - sosyal medya osint aracı
# açık kaynak istihbarat toplama programı
# yalnızca yasal ve etik amaçlarla kullanılmalıdır

import argparse
import sys
import os
import time
from typing import Optional

# modüllerin doğru yüklenmesi için proje dizinini sys.path'e ekle
proje_dizini = os.path.dirname(os.path.abspath(__file__))
if proje_dizini not in sys.path:
    sys.path.insert(0, proje_dizini)

import importlib.util

# sanal ortam (venv) otomatik yönlendirme
venv_python = os.path.join(proje_dizini, "venv", "bin", "python")
if os.path.exists(venv_python) and sys.executable != venv_python and not os.environ.get("VIRTUAL_ENV"):
    if not (importlib.util.find_spec("rich") and importlib.util.find_spec("aiohttp")):
        os.execv(venv_python, [venv_python] + sys.argv)

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, IntPrompt
    from rich.table import Table
    from rich.text import Text
    from rich import box

    # modüller
    from moduller.kullanici_adi import KullaniciAdiArama
    from moduller.eposta import EpostaIstihbarat
    from moduller.telefon import TelefonAnaliz
    from moduller.ip_domain import IpDomainAnaliz
    from moduller.gorsel_meta import GorselMetaAnaliz
    from moduller.profil_tarama import ProfilTarama
    from moduller.rapor import RaporOlusturucu
except ImportError as err:
    print(f"\n[!] Hata: Gerekli kütüphane eksik ({err}).")
    print("[i] Lütfen kurulum betiğini çalıştırın: bash kurulum.sh")
    print("    veya sanal ortamı etkinleştirin: source venv/bin/activate")
    print("    veya doğrudan çalıştırın: ./venv/bin/python enquiry.py\n")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════
#   sabitler ve yapılandırma
# ═══════════════════════════════════════════════════════════

SURUM = "1.0.0"
YAZAR = "Eren"
konsol = Console()

# banner ascii art
BANNER = """[bold green]
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║  ███████╗███╗   ██╗ ██████╗ ██╗   ██╗██╗██████╗ ██╗   ██╗    ║
    ║  ██╔════╝████╗  ██║██╔═══██╗██║   ██║██║██╔══██╗╚██╗ ██╔╝    ║
    ║  █████╗  ██╔██╗ ██║██║   ██║██║   ██║██║██████╔╝ ╚████╔╝     ║
    ║  ██╔══╝  ██║╚██╗██║██║▄▄ ██║██║   ██║██║██╔══██╗  ╚██╔╝      ║
    ║  ███████╗██║ ╚████║╚██████╔╝╚██████╔╝██║██║  ██║   ██║       ║
    ║  ╚══════╝╚═╝  ╚═══╝ ╚══▀▀═╝  ╚═════╝ ╚═╝╚═╝  ╚═╝   ╚═╝       ║
    ║                                                              ║
    ║             [bold cyan]Sosyal Medya OSINT İstihbarat Aracı[/bold cyan]              ║
    ║                        [dim]v{surum} — {yazar}[/dim]                         ║
    ╚══════════════════════════════════════════════════════════════╝
[/bold green]"""

ETIK_UYARI = """[bold yellow]
┌─────────────────────────────────────────────────────────────┐
│  [!]  ETİK KULLANIM UYARISI                                 │
│                                                             │
│  Bu araç yalnızca yasal ve etik amaçlarla kullanılmalıdır.  │
│  Herkese açık (public) veriler üzerinde çalışır.            │
│  Yetkisiz erişim veya kötüye kullanım yasaktır.             │
│  Tüm sorumluluk kullanıcıya aittir.                        │
└─────────────────────────────────────────────────────────────┘
[/bold yellow]"""


def banner_goster():
    """ascii banner'ı gösterir"""
    konsol.print(BANNER.format(surum=SURUM, yazar=YAZAR))
    konsol.print(ETIK_UYARI)


def menu_goster():
    """ana menüyü gösterir"""
    tablo = Table(
        title="[bold cyan] Ana Menü[/]",
        show_header=True,
        header_style="bold white on dark_green",
        border_style="green",
        box=box.DOUBLE_EDGE,
        min_width=55,
    )
    tablo.add_column("No", style="bold cyan", justify="center", min_width=4)
    tablo.add_column("Modül", style="bold white", min_width=28)
    tablo.add_column("Açıklama", style="dim", min_width=20)

    menuler = [
        ("1", " Kullanıcı Adı Arama", "100+ platformda ara"),
        ("2", " E-Posta İstihbaratı", "e-posta analizi"),
        ("3", " Telefon Numarası Analizi", "numara analizi"),
        ("4", " IP / Domain Analizi", "whois, dns, geoip"),
        ("5", " Görsel Metadata (EXIF)", "exif/gps bilgileri"),
        ("6", " Sosyal Medya Profil Tarama", "profil bilgileri"),
        ("7", " Tüm Modüller (Kapsamlı)", "tüm analizler birden"),
        ("8", " Ayarlar ve Bilgi", "versiyon, bağımlılıklar"),
        ("0", " Çıkış", "programı kapat"),
    ]

    for no, modul, aciklama in menuler:
        tablo.add_row(no, modul, aciklama)

    konsol.print()
    konsol.print(tablo)
    konsol.print()


def ayarlar_goster():
    """program ayarları ve bilgilerini gösterir"""
    konsol.print(
        Panel(
            f"[bold cyan]Enquiry OSINT v{SURUM}[/]\n\n"
            f"[bold white]Sürüm:[/] {SURUM}\n"
            f"[bold white]Python:[/] {sys.version}\n"
            f"[bold white]Platform:[/] {sys.platform}\n"
            f"[bold white]Proje Dizini:[/] {proje_dizini}\n\n"
            f"[bold yellow]Yüklü Modüller:[/]",
            title="[bold cyan] Ayarlar ve Bilgi[/]",
            border_style="cyan",
        )
    )

    # bağımlılık kontrolü
    bagimliliklar = {
        "requests": "HTTP istekleri",
        "rich": "terminal arayüzü",
        "aiohttp": "asenkron HTTP",
        "beautifulsoup4 (bs4)": "HTML parsing",
        "phonenumbers": "telefon analizi",
        "Pillow (PIL)": "görsel metadata",
        "python-whois (whois)": "WHOIS sorgusu",
        "dnspython (dns)": "DNS sorgusu",
    }

    tablo = Table(
        show_header=True,
        header_style="bold white",
        border_style="dim",
    )
    tablo.add_column("Kütüphane", style="cyan", min_width=25)
    tablo.add_column("Durum", style="white", min_width=8)
    tablo.add_column("Açıklama", style="dim", min_width=20)

    for kutuphane, aciklama in bagimliliklar.items():
        # import denemesi ile kontrol
        modul_adi = kutuphane.split("(")[-1].rstrip(")").strip() if "(" in kutuphane else kutuphane
        try:
            __import__(modul_adi.replace("-", "_"))
            durum = "[green][+] yüklü[/]"
        except ImportError:
            durum = "[red][-] eksik[/]"

        tablo.add_row(kutuphane, durum, aciklama)

    konsol.print(tablo)


def rapor_sor_ve_kaydet(sonuclar: dict, rapor_olusturucu: RaporOlusturucu):
    """kullanıcıya rapor kaydetmek isteyip istemediğini sorar"""
    konsol.print()
    secim = Prompt.ask(
        "[bold yellow] Sonuçları rapor olarak kaydetmek ister misiniz?[/]",
        choices=["e", "h", "json", "html", "ikisi"],
        default="h"
    )

    if secim == "h":
        return
    elif secim == "e" or secim == "ikisi":
        rapor_olusturucu.json_kaydet(sonuclar)
        rapor_olusturucu.html_kaydet(sonuclar)
    elif secim == "json":
        rapor_olusturucu.json_kaydet(sonuclar)
    elif secim == "html":
        rapor_olusturucu.html_kaydet(sonuclar)


def kullanici_adi_arama_calistir(rapor: RaporOlusturucu):
    """kullanıcı adı arama modülünü çalıştırır"""
    kullanici_adi = Prompt.ask("[bold cyan] Aramak istediğiniz kullanıcı adını girin[/]")
    if not kullanici_adi.strip():
        konsol.print("[red][-] kullanıcı adı boş olamaz![/]")
        return

    arama = KullaniciAdiArama()
    sonuclar = arama.ara(kullanici_adi.strip())
    rapor_sor_ve_kaydet({"kullanici_adi_arama": sonuclar}, rapor)


def eposta_istihbarat_calistir(rapor: RaporOlusturucu):
    """e-posta istihbarat modülünü çalıştırır"""
    eposta = Prompt.ask("[bold cyan] Analiz etmek istediğiniz e-posta adresini girin[/]")
    if not eposta.strip():
        konsol.print("[red][-] e-posta adresi boş olamaz![/]")
        return

    istihbarat = EpostaIstihbarat()
    sonuclar = istihbarat.analiz_et(eposta.strip())
    rapor_sor_ve_kaydet({"eposta_istihbarati": sonuclar}, rapor)


def telefon_analiz_calistir(rapor: RaporOlusturucu):
    """telefon numarası analiz modülünü çalıştırır"""
    numara = Prompt.ask(
        "[bold cyan] Analiz etmek istediğiniz telefon numarasını girin[/]\n"
        "[dim](uluslararası formatta, örn: +905551234567)[/]"
    )
    if not numara.strip():
        konsol.print("[red][-] telefon numarası boş olamaz![/]")
        return

    analiz = TelefonAnaliz()
    sonuclar = analiz.analiz_et(numara.strip())
    rapor_sor_ve_kaydet({"telefon_analizi": sonuclar}, rapor)


def ip_domain_analiz_calistir(rapor: RaporOlusturucu):
    """ip/domain analiz modülünü çalıştırır"""
    hedef = Prompt.ask("[bold cyan] Analiz etmek istediğiniz IP adresi veya domain adını girin[/]")
    if not hedef.strip():
        konsol.print("[red][-] hedef boş olamaz![/]")
        return

    analiz = IpDomainAnaliz()
    sonuclar = analiz.analiz_et(hedef.strip())
    rapor_sor_ve_kaydet({"ip_domain_analizi": sonuclar}, rapor)


def gorsel_meta_calistir(rapor: RaporOlusturucu):
    """görsel metadata analiz modülünü çalıştırır"""
    dosya_yolu = Prompt.ask("[bold cyan]  Analiz etmek istediğiniz görsel dosyasının yolunu girin[/]")
    if not dosya_yolu.strip():
        konsol.print("[red][-] dosya yolu boş olamaz![/]")
        return

    analiz = GorselMetaAnaliz()
    sonuclar = analiz.analiz_et(dosya_yolu.strip())
    rapor_sor_ve_kaydet({"gorsel_metadata": sonuclar}, rapor)


def profil_tarama_calistir(rapor: RaporOlusturucu):
    """profil tarama modülünü çalıştırır"""
    kullanici_adi = Prompt.ask("[bold cyan] Taramak istediğiniz kullanıcı adını girin[/]")
    if not kullanici_adi.strip():
        konsol.print("[red][-] kullanıcı adı boş olamaz![/]")
        return

    tarama = ProfilTarama()
    sonuclar = tarama.tara(kullanici_adi.strip())
    rapor_sor_ve_kaydet({"profil_tarama": sonuclar}, rapor)


def kapsamli_analiz_calistir(rapor: RaporOlusturucu):
    """tüm modülleri tek seferde çalıştırır"""
    konsol.print(
        Panel(
            "[bold white]Kapsamlı analiz bir kullanıcı adı üzerinden tüm uygulanabilir modülleri çalıştırır.\n"
            "Bu işlem birkaç dakika sürebilir.[/]",
            title="[bold cyan] Kapsamlı Analiz[/]",
            border_style="cyan",
        )
    )

    kullanici_adi = Prompt.ask("[bold cyan]Hedef kullanıcı adını girin[/]")
    if not kullanici_adi.strip():
        konsol.print("[red][-] kullanıcı adı boş olamaz![/]")
        return

    kullanici_adi = kullanici_adi.strip()
    tum_sonuclar = {"hedef": kullanici_adi, "analiz_zamani": time.strftime("%Y-%m-%d %H:%M:%S")}

    # 1. kullanıcı adı arama
    konsol.print("\n[bold cyan]━━━ 1/3 Kullanıcı Adı Arama ━━━[/]")
    arama = KullaniciAdiArama()
    tum_sonuclar["kullanici_adi_arama"] = arama.ara(kullanici_adi)

    # 2. profil tarama
    konsol.print("\n[bold cyan]━━━ 2/3 Profil Tarama ━━━[/]")
    tarama = ProfilTarama()
    tum_sonuclar["profil_tarama"] = tarama.tara(kullanici_adi)

    # 3. özet
    konsol.print("\n[bold cyan]━━━ 3/3 Analiz Tamamlandı ━━━[/]")

    bulunan_platform = sum(
        1 for s in tum_sonuclar.get("kullanici_adi_arama", [])
        if s and s.get("bulundu")
    )
    toplam_platform = len(tum_sonuclar.get("kullanici_adi_arama", []))

    konsol.print(
        Panel(
            f"[bold green][+] Kapsamlı analiz tamamlandı![/]\n\n"
            f"[bold white]Hedef:[/] {kullanici_adi}\n"
            f"[bold white]Bulunan Platformlar:[/] {bulunan_platform}/{toplam_platform}\n"
            f"[bold white]Taranan Profiller:[/] GitHub, Reddit, Steam, Lichess, HN",
            title="[bold cyan] Analiz Özeti[/]",
            border_style="green",
        )
    )

    rapor_sor_ve_kaydet(tum_sonuclar, rapor)


def interaktif_mod():
    """interaktif menü modunu çalıştırır"""
    banner_goster()
    rapor = RaporOlusturucu()

    while True:
        menu_goster()
        try:
            secim = Prompt.ask(
                "[bold green]> Seçiminiz[/]",
                choices=["0", "1", "2", "3", "4", "5", "6", "7", "8"],
                default="0"
            )
        except KeyboardInterrupt:
            konsol.print("\n[bold yellow] Çıkış yapılıyor...[/]")
            break

        if secim == "0":
            konsol.print(
                Panel(
                    "[bold green] Enquiry'den çıkış yapılıyor.\n"
                    "İyi günler ve etik kullanımı unutmayın! [/]",
                    border_style="green",
                )
            )
            break
        elif secim == "1":
            kullanici_adi_arama_calistir(rapor)
        elif secim == "2":
            eposta_istihbarat_calistir(rapor)
        elif secim == "3":
            telefon_analiz_calistir(rapor)
        elif secim == "4":
            ip_domain_analiz_calistir(rapor)
        elif secim == "5":
            gorsel_meta_calistir(rapor)
        elif secim == "6":
            profil_tarama_calistir(rapor)
        elif secim == "7":
            kapsamli_analiz_calistir(rapor)
        elif secim == "8":
            ayarlar_goster()

        # bir sonraki işlem öncesi bekle
        konsol.print()
        try:
            Prompt.ask("[dim]devam etmek için enter'a basın...[/]", default="")
        except KeyboardInterrupt:
            konsol.print("\n[bold yellow] Çıkış yapılıyor...[/]")
            break


def komut_satiri_modu():
    """argparse ile komut satırı modunu çalıştırır"""
    ayrıstirici = argparse.ArgumentParser(
        prog="enquiry",
        description="Enquiry — Sosyal Medya OSINT İstihbarat Aracı",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
örnekler:
  python enquiry.py                          # interaktif mod
  python enquiry.py -k johndoe               # kullanıcı adı arama
  python enquiry.py -e user@example.com      # e-posta istihbaratı
  python enquiry.py -t +905551234567         # telefon analizi
  python enquiry.py -i example.com           # ip/domain analizi
  python enquiry.py -g resim.jpg             # görsel metadata
  python enquiry.py -p johndoe               # profil tarama
  python enquiry.py --kapsamli johndoe       # kapsamlı analiz
        """
    )

    ayrıstirici.add_argument(
        "-k", "--kullanici",
        metavar="KULLANICI_ADI",
        help="kullanıcı adını platformlarda ara"
    )
    ayrıstirici.add_argument(
        "-e", "--eposta",
        metavar="E_POSTA",
        help="e-posta adresi üzerinde istihbarat topla"
    )
    ayrıstirici.add_argument(
        "-t", "--telefon",
        metavar="NUMARA",
        help="telefon numarasını analiz et"
    )
    ayrıstirici.add_argument(
        "-i", "--ip",
        metavar="IP_DOMAIN",
        help="ip adresi veya domain analizi yap"
    )
    ayrıstirici.add_argument(
        "-g", "--gorsel",
        metavar="DOSYA_YOLU",
        help="görsel dosyasının metadata bilgilerini çıkar"
    )
    ayrıstirici.add_argument(
        "-p", "--profil",
        metavar="KULLANICI_ADI",
        help="sosyal medya profillerini tara"
    )
    ayrıstirici.add_argument(
        "--kapsamli",
        metavar="KULLANICI_ADI",
        help="tüm modüllerle kapsamlı analiz yap"
    )
    ayrıstirici.add_argument(
        "-r", "--rapor",
        choices=["json", "html", "ikisi"],
        default=None,
        help="sonuçları otomatik rapor olarak kaydet"
    )
    ayrıstirici.add_argument(
        "--surum",
        action="version",
        version=f"enquiry v{SURUM}"
    )

    return ayrıstirici


def main():
    """ana giriş noktası"""
    ayrıstirici = komut_satiri_modu()
    argumanlar = ayrıstirici.parse_args()

    # hiçbir argüman verilmediyse interaktif moda geç
    herhangi_arguman = any([
        argumanlar.kullanici,
        argumanlar.eposta,
        argumanlar.telefon,
        argumanlar.ip,
        argumanlar.gorsel,
        argumanlar.profil,
        argumanlar.kapsamli,
    ])

    if not herhangi_arguman:
        interaktif_mod()
        return

    # komut satırı modu
    banner_goster()
    rapor = RaporOlusturucu()
    sonuclar = {}

    if argumanlar.kullanici:
        arama = KullaniciAdiArama()
        sonuclar["kullanici_adi_arama"] = arama.ara(argumanlar.kullanici)

    if argumanlar.eposta:
        istihbarat = EpostaIstihbarat()
        sonuclar["eposta_istihbarati"] = istihbarat.analiz_et(argumanlar.eposta)

    if argumanlar.telefon:
        analiz = TelefonAnaliz()
        sonuclar["telefon_analizi"] = analiz.analiz_et(argumanlar.telefon)

    if argumanlar.ip:
        analiz = IpDomainAnaliz()
        sonuclar["ip_domain_analizi"] = analiz.analiz_et(argumanlar.ip)

    if argumanlar.gorsel:
        analiz = GorselMetaAnaliz()
        sonuclar["gorsel_metadata"] = analiz.analiz_et(argumanlar.gorsel)

    if argumanlar.profil:
        tarama = ProfilTarama()
        sonuclar["profil_tarama"] = tarama.tara(argumanlar.profil)

    if argumanlar.kapsamli:
        kullanici_adi = argumanlar.kapsamli
        sonuclar["hedef"] = kullanici_adi

        arama = KullaniciAdiArama()
        sonuclar["kullanici_adi_arama"] = arama.ara(kullanici_adi)

        tarama = ProfilTarama()
        sonuclar["profil_tarama"] = tarama.tara(kullanici_adi)

    # otomatik rapor kaydetme
    if argumanlar.rapor and sonuclar:
        if argumanlar.rapor in ("json", "ikisi"):
            rapor.json_kaydet(sonuclar)
        if argumanlar.rapor in ("html", "ikisi"):
            rapor.html_kaydet(sonuclar)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        konsol.print("\n[bold yellow] Program sonlandırıldı.[/]")
        sys.exit(0)
    except Exception as hata:
        konsol.print(f"\n[bold red][-] Beklenmeyen hata: {hata}[/]")
        sys.exit(1)
