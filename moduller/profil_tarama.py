#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# sosyal medya profil tarama modülü
# herkese açık api'ler üzerinden profil bilgilerini toplar

import json
from typing import Dict, List, Optional

import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.columns import Columns
from rich.text import Text

try:
    # pyrefly: ignore [missing-import]
    from bs4 import BeautifulSoup
    BS4_MEVCUT = True
except ImportError:
    BS4_MEVCUT = False

konsol = Console()


class ProfilTarama:
    """sosyal medya profillerinden bilgi toplayan sınıf"""

    def __init__(self):
        self.sonuclar: Dict = {}
        self.basliklar = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Accept": "application/json, text/html",
            "Accept-Language": "tr-TR,tr;q=0.9",
        }

    def tara(self, kullanici_adi: str) -> Dict:
        """birden fazla platformda kullanıcı profilini tarar"""
        konsol.print(
            Panel(
                f"[bold white]Kullanıcı Adı:[/] [bold green]{kullanici_adi}[/]",
                title="[bold cyan] Profil Tarama[/]",
                border_style="cyan",
            )
        )

        self.sonuclar = {
            "kullanici_adi": kullanici_adi,
            "github": {},
            "reddit": {},
            "steam": {},
            "lichess": {},
            "hacker_news": {},
        }

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold cyan]{task.description}"),
            console=konsol,
        ) as ilerleme:
            # github profili
            gorev1 = ilerleme.add_task(" github profili taranıyor...", total=None)
            self._github_tara(kullanici_adi)
            ilerleme.update(gorev1, description="[green][+] github profili tarandı[/]")

            # reddit profili
            gorev2 = ilerleme.add_task(" reddit profili taranıyor...", total=None)
            self._reddit_tara(kullanici_adi)
            ilerleme.update(gorev2, description="[green][+] reddit profili tarandı[/]")

            # steam profili
            gorev3 = ilerleme.add_task(" steam profili taranıyor...", total=None)
            self._steam_tara(kullanici_adi)
            ilerleme.update(gorev3, description="[green][+] steam profili tarandı[/]")

            # lichess profili
            gorev4 = ilerleme.add_task("  lichess profili taranıyor...", total=None)
            self._lichess_tara(kullanici_adi)
            ilerleme.update(gorev4, description="[green][+] lichess profili tarandı[/]")

            # hacker news profili
            gorev5 = ilerleme.add_task(" hacker news profili taranıyor...", total=None)
            self._hacker_news_tara(kullanici_adi)
            ilerleme.update(gorev5, description="[green][+] hacker news profili tarandı[/]")

        self._sonuclari_goster()
        return self.sonuclar

    def _github_tara(self, kullanici_adi: str):
        """github api ile kullanıcı profilini tarar"""
        url = f"https://api.github.com/users/{kullanici_adi}"
        basliklar = {
            "User-Agent": "enquiry-osint",
            "Accept": "application/vnd.github.v3+json"
        }

        try:
            yanit = requests.get(url, headers=basliklar, timeout=10)
            if yanit.status_code == 200:
                veri = yanit.json()
                self.sonuclar["github"] = {
                    "bulundu": True,
                    "kullanici_adi": veri.get("login", "-"),
                    "isim": veri.get("name", "-"),
                    "bio": veri.get("bio", "-"),
                    "konum": veri.get("location", "-"),
                    "sirket": veri.get("company", "-"),
                    "blog": veri.get("blog", "-"),
                    "twitter": veri.get("twitter_username", "-"),
                    "acik_repo_sayisi": veri.get("public_repos", 0),
                    "acik_gist_sayisi": veri.get("public_gists", 0),
                    "takipci": veri.get("followers", 0),
                    "takip_edilen": veri.get("following", 0),
                    "hesap_olusturma": veri.get("created_at", "-"),
                    "son_guncelleme": veri.get("updated_at", "-"),
                    "profil_url": veri.get("html_url", "-"),
                    "avatar_url": veri.get("avatar_url", "-"),
                    "email": veri.get("email", "-"),
                    "kiralabilir": veri.get("hireable", False),
                }

                # son repolarını da çek
                repo_url = f"https://api.github.com/users/{kullanici_adi}/repos?sort=updated&per_page=5"
                repo_yanit = requests.get(repo_url, headers=basliklar, timeout=10)
                if repo_yanit.status_code == 200:
                    repolar = repo_yanit.json()
                    self.sonuclar["github"]["son_repolar"] = [
                        {
                            "isim": r.get("name", "-"),
                            "aciklama": r.get("description", "-"),
                            "dil": r.get("language", "-"),
                            "yildiz": r.get("stargazers_count", 0),
                            "fork": r.get("forks_count", 0),
                            "url": r.get("html_url", "-"),
                        }
                        for r in repolar
                    ]
            elif yanit.status_code == 404:
                self.sonuclar["github"] = {"bulundu": False}
            else:
                self.sonuclar["github"] = {"bulundu": False, "durum": yanit.status_code}
        except requests.RequestException:
            self.sonuclar["github"] = {"bulundu": False, "hata": "bağlantı hatası"}

    def _reddit_tara(self, kullanici_adi: str):
        """reddit api ile kullanıcı profilini tarar"""
        url = f"https://www.reddit.com/user/{kullanici_adi}/about.json"
        basliklar = {
            "User-Agent": "enquiry-osint/1.0 (osint tool)"
        }

        try:
            yanit = requests.get(url, headers=basliklar, timeout=10)
            if yanit.status_code == 200:
                veri = yanit.json().get("data", {})
                self.sonuclar["reddit"] = {
                    "bulundu": True,
                    "kullanici_adi": veri.get("name", "-"),
                    "toplam_karma": veri.get("total_karma", 0),
                    "yorum_karma": veri.get("comment_karma", 0),
                    "paylasim_karma": veri.get("link_karma", 0),
                    "hesap_olusturma": veri.get("created_utc", 0),
                    "dogrulanmis_eposta": veri.get("has_verified_email", False),
                    "premium": veri.get("is_gold", False),
                    "moderator": veri.get("is_mod", False),
                    "profil_url": f"https://www.reddit.com/user/{kullanici_adi}",
                    "avatar_url": veri.get("icon_img", "-"),
                }
            else:
                self.sonuclar["reddit"] = {"bulundu": False}
        except requests.RequestException:
            self.sonuclar["reddit"] = {"bulundu": False, "hata": "bağlantı hatası"}

    def _steam_tara(self, kullanici_adi: str):
        """steam profil sayfasından bilgi toplar"""
        url = f"https://steamcommunity.com/id/{kullanici_adi}"

        try:
            yanit = requests.get(url, headers=self.basliklar, timeout=10)
            if yanit.status_code == 200 and BS4_MEVCUT:
                soup = BeautifulSoup(yanit.text, "html.parser")

                # profil var mı kontrolü
                hata_div = soup.find("div", class_="error_ctn")
                if hata_div:
                    self.sonuclar["steam"] = {"bulundu": False}
                    return

                # profil bilgileri
                profil_isim = soup.find("span", class_="actual_persona_name")
                profil_durum = soup.find("div", class_="profile_in_game_header")

                self.sonuclar["steam"] = {
                    "bulundu": True,
                    "kullanici_adi": kullanici_adi,
                    "gorunen_isim": profil_isim.text.strip() if profil_isim else "-",
                    "durum": profil_durum.text.strip() if profil_durum else "bilinmiyor",
                    "profil_url": url,
                }
            elif yanit.status_code == 200 and not BS4_MEVCUT:
                self.sonuclar["steam"] = {
                    "bulundu": True,
                    "profil_url": url,
                    "not": "beautifulsoup4 yüklü değil, detaylı bilgi çıkarılamadı"
                }
            else:
                self.sonuclar["steam"] = {"bulundu": False}
        except requests.RequestException:
            self.sonuclar["steam"] = {"bulundu": False, "hata": "bağlantı hatası"}

    def _lichess_tara(self, kullanici_adi: str):
        """lichess api ile kullanıcı profilini tarar"""
        url = f"https://lichess.org/api/user/{kullanici_adi}"

        try:
            yanit = requests.get(url, headers={"Accept": "application/json"}, timeout=10)
            if yanit.status_code == 200:
                veri = yanit.json()
                self.sonuclar["lichess"] = {
                    "bulundu": True,
                    "kullanici_adi": veri.get("username", "-"),
                    "baslik": veri.get("title", "-"),
                    "bio": veri.get("profile", {}).get("bio", "-"),
                    "ulke": veri.get("profile", {}).get("country", "-"),
                    "oynanan_oyunlar": veri.get("count", {}).get("all", 0),
                    "kazanma": veri.get("count", {}).get("win", 0),
                    "kaybetme": veri.get("count", {}).get("loss", 0),
                    "berabere": veri.get("count", {}).get("draw", 0),
                    "online": veri.get("online", False),
                    "profil_url": f"https://lichess.org/@/{kullanici_adi}",
                }

                # dereceler
                dereceler = veri.get("perfs", {})
                derecelendirme = {}
                for mod, bilgi in dereceler.items():
                    if isinstance(bilgi, dict) and "rating" in bilgi:
                        derecelendirme[mod] = bilgi["rating"]
                self.sonuclar["lichess"]["dereceler"] = derecelendirme
            else:
                self.sonuclar["lichess"] = {"bulundu": False}
        except requests.RequestException:
            self.sonuclar["lichess"] = {"bulundu": False, "hata": "bağlantı hatası"}

    def _hacker_news_tara(self, kullanici_adi: str):
        """hacker news api ile kullanıcı profilini tarar"""
        url = f"https://hacker-news.firebaseio.com/v0/user/{kullanici_adi}.json"

        try:
            yanit = requests.get(url, timeout=10)
            if yanit.status_code == 200:
                veri = yanit.json()
                if veri:
                    self.sonuclar["hacker_news"] = {
                        "bulundu": True,
                        "kullanici_adi": veri.get("id", "-"),
                        "hakkinda": veri.get("about", "-"),
                        "karma": veri.get("karma", 0),
                        "hesap_olusturma": veri.get("created", 0),
                        "profil_url": f"https://news.ycombinator.com/user?id={kullanici_adi}",
                    }
                else:
                    self.sonuclar["hacker_news"] = {"bulundu": False}
        except requests.RequestException:
            self.sonuclar["hacker_news"] = {"bulundu": False, "hata": "bağlantı hatası"}

    def _sonuclari_goster(self):
        """sonuçları terminal ekranında gösterir"""
        konsol.print()

        # github
        github = self.sonuclar.get("github", {})
        if github.get("bulundu"):
            github_tablo = Table(
                title=" GitHub Profili",
                show_header=True,
                header_style="bold white on dark_green",
                border_style="green",
            )
            github_tablo.add_column("Bilgi", style="bold white", min_width=18)
            github_tablo.add_column("Değer", style="green", min_width=40)

            alanlar = {
                "isim": " İsim",
                "bio": " Bio",
                "konum": " Konum",
                "sirket": " Şirket",
                "blog": " Blog",
                "twitter": " Twitter",
                "email": " E-Posta",
                "profil_url": " Profil URL",
            }
            for anahtar, baslik in alanlar.items():
                deger = github.get(anahtar, "-")
                if deger and str(deger) != "-" and str(deger) != "None":
                    github_tablo.add_row(baslik, str(deger))

            # istatistikler
            github_tablo.add_row(
                " İstatistikler",
                f" {github.get('acik_repo_sayisi', 0)} repo  |  "
                f" {github.get('takipci', 0)} takipçi  |  "
                f" {github.get('takip_edilen', 0)} takip"
            )
            github_tablo.add_row(" Hesap Oluşturma", str(github.get("hesap_olusturma", "-"))[:10])

            konsol.print(github_tablo)

            # son repolar
            son_repolar = github.get("son_repolar", [])
            if son_repolar:
                repo_tablo = Table(
                    title=" Son Güncel Repolar",
                    show_header=True,
                    header_style="bold cyan",
                    border_style="cyan",
                )
                repo_tablo.add_column("Repo", style="bold green", min_width=20)
                repo_tablo.add_column("Dil", style="yellow", min_width=10)
                repo_tablo.add_column("", style="white", min_width=5)
                repo_tablo.add_column("Açıklama", style="dim", min_width=30)

                for repo in son_repolar:
                    repo_tablo.add_row(
                        repo.get("isim", "-"),
                        str(repo.get("dil", "-")),
                        str(repo.get("yildiz", 0)),
                        str(repo.get("aciklama", "-"))[:40],
                    )

                konsol.print(repo_tablo)
        else:
            konsol.print("[dim] github profili bulunamadı.[/]")

        # reddit
        reddit = self.sonuclar.get("reddit", {})
        if reddit.get("bulundu"):
            konsol.print(
                Panel(
                    f"[bold white]Kullanıcı:[/] u/{reddit.get('kullanici_adi', '-')}\n"
                    f"[bold white]Toplam Karma:[/] [green]{reddit.get('toplam_karma', 0):,}[/]\n"
                    f"[bold white]Yorum Karma:[/] {reddit.get('yorum_karma', 0):,}\n"
                    f"[bold white]Paylaşım Karma:[/] {reddit.get('paylasim_karma', 0):,}\n"
                    f"[bold white]Premium:[/] {'[+]' if reddit.get('premium') else '[-]'}\n"
                    f"[bold white]Moderatör:[/] {'[+]' if reddit.get('moderator') else '[-]'}\n"
                    f"[bold white]E-Posta Doğrulanmış:[/] {'[+]' if reddit.get('dogrulanmis_eposta') else '[-]'}\n"
                    f"[bold white]Profil:[/] {reddit.get('profil_url', '-')}",
                    title="[bold orange3] Reddit Profili[/]",
                    border_style="orange3",
                )
            )
        else:
            konsol.print("[dim] reddit profili bulunamadı.[/]")

        # steam
        steam = self.sonuclar.get("steam", {})
        if steam.get("bulundu"):
            konsol.print(
                Panel(
                    f"[bold white]Görünen İsim:[/] {steam.get('gorunen_isim', '-')}\n"
                    f"[bold white]Durum:[/] {steam.get('durum', '-')}\n"
                    f"[bold white]Profil:[/] {steam.get('profil_url', '-')}",
                    title="[bold blue] Steam Profili[/]",
                    border_style="blue",
                )
            )
        else:
            konsol.print("[dim] steam profili bulunamadı.[/]")

        # lichess
        lichess = self.sonuclar.get("lichess", {})
        if lichess.get("bulundu"):
            dereceler = lichess.get("dereceler", {})
            derece_str = "  |  ".join(
                f"{mod}: {puan}" for mod, puan in list(dereceler.items())[:5]
            ) if dereceler else "derece bilgisi yok"

            konsol.print(
                Panel(
                    f"[bold white]Kullanıcı:[/] {lichess.get('kullanici_adi', '-')}\n"
                    f"[bold white]Oyunlar:[/] {lichess.get('oynanan_oyunlar', 0):,} "
                    f"(W:{lichess.get('kazanma', 0)} / L:{lichess.get('kaybetme', 0)} / D:{lichess.get('berabere', 0)})\n"
                    f"[bold white]Dereceler:[/] {derece_str}\n"
                    f"[bold white]Çevrimiçi:[/] {'[+] evet' if lichess.get('online') else '[-] hayır'}\n"
                    f"[bold white]Profil:[/] {lichess.get('profil_url', '-')}",
                    title="[bold white] Lichess Profili[/]",
                    border_style="white",
                )
            )
        else:
            konsol.print("[dim] lichess profili bulunamadı.[/]")

        # hacker news
        hn = self.sonuclar.get("hacker_news", {})
        if hn.get("bulundu"):
            konsol.print(
                Panel(
                    f"[bold white]Kullanıcı:[/] {hn.get('kullanici_adi', '-')}\n"
                    f"[bold white]Karma:[/] [green]{hn.get('karma', 0):,}[/]\n"
                    f"[bold white]Profil:[/] {hn.get('profil_url', '-')}",
                    title="[bold yellow] Hacker News Profili[/]",
                    border_style="yellow",
                )
            )
        else:
            konsol.print("[dim] hacker news profili bulunamadı.[/]")
