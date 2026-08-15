#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# rapor oluşturma modülü
# osint sonuçlarını json ve html formatında dışa aktarır

import json
import os
from datetime import datetime
from typing import Dict, Optional

from rich.console import Console
from rich.panel import Panel

konsol = Console()


class RaporOlusturucu:
    """osint sonuçlarını rapor formatında dışa aktaran sınıf"""

    def __init__(self):
        # raporlar klasörünü oluştur
        self.rapor_dizini = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "raporlar"
        )
        os.makedirs(self.rapor_dizini, exist_ok=True)

    def json_kaydet(self, veri: Dict, dosya_adi: Optional[str] = None) -> str:
        """sonuçları json formatında kaydeder"""
        if not dosya_adi:
            zaman_damgasi = datetime.now().strftime("%Y%m%d_%H%M%S")
            dosya_adi = f"enquiry_rapor_{zaman_damgasi}.json"

        tam_yol = os.path.join(self.rapor_dizini, dosya_adi)

        try:
            with open(tam_yol, "w", encoding="utf-8") as dosya:
                json.dump(veri, dosya, ensure_ascii=False, indent=2, default=str)

            konsol.print(
                Panel(
                    f"[bold green][+] JSON raporu kaydedildi![/]\n"
                    f"[white]Konum:[/] {tam_yol}",
                    title="[bold cyan] JSON Raporu[/]",
                    border_style="green",
                )
            )
            return tam_yol
        except Exception as hata:
            konsol.print(f"[bold red][-] JSON raporu kaydedilemedi: {hata}[/]")
            return ""

    def html_kaydet(self, veri: Dict, baslik: str = "Enquiry OSINT Raporu", dosya_adi: Optional[str] = None) -> str:
        """sonuçları html rapor formatında kaydeder"""
        if not dosya_adi:
            zaman_damgasi = datetime.now().strftime("%Y%m%d_%H%M%S")
            dosya_adi = f"enquiry_rapor_{zaman_damgasi}.html"

        tam_yol = os.path.join(self.rapor_dizini, dosya_adi)

        html_icerik = self._html_olustur(veri, baslik)

        try:
            with open(tam_yol, "w", encoding="utf-8") as dosya:
                dosya.write(html_icerik)

            konsol.print(
                Panel(
                    f"[bold green][+] HTML raporu kaydedildi![/]\n"
                    f"[white]Konum:[/] {tam_yol}",
                    title="[bold cyan] HTML Raporu[/]",
                    border_style="green",
                )
            )
            return tam_yol
        except Exception as hata:
            konsol.print(f"[bold red][-] HTML raporu kaydedilemedi: {hata}[/]")
            return ""

    def _html_olustur(self, veri: Dict, baslik: str) -> str:
        """html rapor içeriğini oluşturur"""
        zaman = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{baslik}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1100px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            padding: 40px 20px;
            background: linear-gradient(135deg, rgba(0, 255, 136, 0.1), rgba(0, 136, 255, 0.1));
            border: 1px solid rgba(0, 255, 136, 0.2);
            border-radius: 16px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }}
        .header h1 {{
            font-size: 2.5em;
            background: linear-gradient(135deg, #00ff88, #0088ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        .header .subtitle {{
            color: #888;
            font-size: 0.95em;
        }}
        .section {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            backdrop-filter: blur(5px);
            transition: border-color 0.3s ease;
        }}
        .section:hover {{
            border-color: rgba(0, 255, 136, 0.3);
        }}
        .section h2 {{
            font-size: 1.3em;
            color: #00ff88;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(0, 255, 136, 0.2);
        }}
        .section h3 {{
            font-size: 1.1em;
            color: #0088ff;
            margin: 16px 0 8px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }}
        th {{
            background: rgba(0, 255, 136, 0.1);
            color: #00ff88;
            padding: 10px 14px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid rgba(0, 255, 136, 0.2);
        }}
        td {{
            padding: 8px 14px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            word-break: break-all;
        }}
        tr:hover td {{
            background: rgba(0, 255, 136, 0.03);
        }}
        .badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
        }}
        .badge-found {{
            background: rgba(0, 255, 136, 0.15);
            color: #00ff88;
            border: 1px solid rgba(0, 255, 136, 0.3);
        }}
        .badge-not-found {{
            background: rgba(255, 68, 68, 0.15);
            color: #ff4444;
            border: 1px solid rgba(255, 68, 68, 0.3);
        }}
        .badge-info {{
            background: rgba(0, 136, 255, 0.15);
            color: #0088ff;
            border: 1px solid rgba(0, 136, 255, 0.3);
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #555;
            font-size: 0.85em;
            margin-top: 30px;
        }}
        .footer a {{
            color: #00ff88;
            text-decoration: none;
        }}
        a {{
            color: #0088ff;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .warning {{
            background: rgba(255, 170, 0, 0.1);
            border: 1px solid rgba(255, 170, 0, 0.3);
            border-radius: 8px;
            padding: 12px 16px;
            margin: 10px 0;
            color: #ffaa00;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> ENQUIRY</h1>
            <p class="subtitle">Sosyal Medya OSINT Raporu — {zaman}</p>
        </div>

        <div class="warning">
            [!] Bu rapor yalnızca yasal ve etik amaçlarla kullanılmalıdır. Herkese açık veriler üzerinden oluşturulmuştur.
        </div>
"""

        # veri bölümlerini ekle
        html += self._veri_bolumlerini_olustur(veri)

        html += f"""
        <div class="footer">
            <p>Enquiry OSINT v1.0 — Eren tarafından oluşturuldu — {zaman}</p>
            <p>[!] Bu rapor yalnızca bilgilendirme amaçlıdır.</p>
        </div>
    </div>
</body>
</html>"""

        return html

    def _veri_bolumlerini_olustur(self, veri: Dict) -> str:
        """veri sözlüğünden html bölümleri oluşturur"""
        html = ""

        for anahtar, deger in veri.items():
            if isinstance(deger, dict):
                html += self._bolum_olustur(anahtar, deger)
            elif isinstance(deger, list):
                html += self._liste_bolumu_olustur(anahtar, deger)
            else:
                # basit değer
                html += f"""
        <div class="section">
            <h2>{self._baslik_formatla(anahtar)}</h2>
            <p>{str(deger)}</p>
        </div>
"""

        return html

    def _bolum_olustur(self, baslik: str, veri: Dict) -> str:
        """tek bir veri bölümünü html'e dönüştürür"""
        html = f"""
        <div class="section">
            <h2>{self._baslik_formatla(baslik)}</h2>
            <table>
                <thead>
                    <tr><th>Alan</th><th>Değer</th></tr>
                </thead>
                <tbody>
"""
        for anahtar, deger in veri.items():
            if isinstance(deger, dict):
                # iç içe sözlük
                ic_html = "<br>".join(
                    f"<strong>{k}:</strong> {v}" for k, v in deger.items()
                )
                html += f"<tr><td>{self._baslik_formatla(anahtar)}</td><td>{ic_html}</td></tr>\n"
            elif isinstance(deger, list):
                if deger and isinstance(deger[0], dict):
                    ic_html = "<br>".join(
                        " | ".join(f"{k}: {v}" for k, v in oge.items())
                        for oge in deger[:10]
                    )
                else:
                    ic_html = ", ".join(str(v) for v in deger[:20])
                html += f"<tr><td>{self._baslik_formatla(anahtar)}</td><td>{ic_html}</td></tr>\n"
            elif isinstance(deger, bool):
                rozet = "badge-found" if deger else "badge-not-found"
                metin = "[+] Evet" if deger else "[-] Hayır"
                html += f'<tr><td>{self._baslik_formatla(anahtar)}</td><td><span class="badge {rozet}">{metin}</span></td></tr>\n'
            else:
                # url ise link yap
                str_deger = str(deger)
                if str_deger.startswith("http"):
                    str_deger = f'<a href="{str_deger}" target="_blank">{str_deger}</a>'
                html += f"<tr><td>{self._baslik_formatla(anahtar)}</td><td>{str_deger}</td></tr>\n"

        html += """
                </tbody>
            </table>
        </div>
"""
        return html

    def _liste_bolumu_olustur(self, baslik: str, veri: list) -> str:
        """liste verisini html bölümüne dönüştürür"""
        if not veri:
            return ""

        html = f"""
        <div class="section">
            <h2>{self._baslik_formatla(baslik)}</h2>
"""

        if isinstance(veri[0], dict):
            # sözlük listesi - tablo olarak göster
            anahtarlar = list(veri[0].keys())
            html += "<table><thead><tr>"
            for a in anahtarlar:
                html += f"<th>{self._baslik_formatla(a)}</th>"
            html += "</tr></thead><tbody>"

            for oge in veri[:50]:
                html += "<tr>"
                for a in anahtarlar:
                    deger = oge.get(a, "-")
                    str_deger = str(deger)
                    if str_deger.startswith("http"):
                        str_deger = f'<a href="{str_deger}" target="_blank"> Link</a>'
                    elif isinstance(deger, bool):
                        rozet = "badge-found" if deger else "badge-not-found"
                        str_deger = f'<span class="badge {rozet}">{"[+]" if deger else "[-]"}</span>'
                    html += f"<td>{str_deger}</td>"
                html += "</tr>"

            html += "</tbody></table>"
        else:
            # basit liste
            html += "<ul>"
            for oge in veri[:50]:
                html += f"<li>{str(oge)}</li>"
            html += "</ul>"

        html += "</div>\n"
        return html

    @staticmethod
    def _baslik_formatla(metin: str) -> str:
        """alt çizgi ve kısaltmaları okunabilir başlığa dönüştürür"""
        ozel_kelimeler = {
            "ip": "IP",
            "dns": "DNS",
            "url": "URL",
            "mx": "MX",
            "gps": "GPS",
            "isp": "ISP",
            "api": "API",
            "html": "HTML",
            "json": "JSON",
            "exif": "EXIF",
            "as": "AS",
        }

        kelimeler = metin.replace("_", " ").split()
        sonuc = []
        for kelime in kelimeler:
            if kelime.lower() in ozel_kelimeler:
                sonuc.append(ozel_kelimeler[kelime.lower()])
            else:
                sonuc.append(kelime.capitalize())

        return " ".join(sonuc)
