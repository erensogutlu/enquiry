#!/bin/bash
# enquiry osint aracı - kali linux kurulum betiği
# bu betik tüm bağımlılıkları otomatik olarak kurar

set -e

# renkli çıktı fonksiyonları
YESIL='\033[0;32m'
KIRMIZI='\033[0;31m'
SARI='\033[1;33m'
MAVI='\033[0;34m'
SIFIRLAMA='\033[0m'

bilgi() {
    echo -e "${MAVI}[*]${SIFIRLAMA} $1"
}

basari() {
    echo -e "${YESIL}[[+]]${SIFIRLAMA} $1"
}

uyari() {
    echo -e "${SARI}[!]${SIFIRLAMA} $1"
}

hata() {
    echo -e "${KIRMIZI}[[-]]${SIFIRLAMA} $1"
}

echo ""
echo -e "${YESIL}"
echo "    ███████╗███╗   ██╗ ██████╗ ██╗   ██╗██╗██████╗ ██╗   ██╗"
echo "    ██╔════╝████╗  ██║██╔═══██╗██║   ██║██║██╔══██╗╚██╗ ██╔╝"
echo "    █████╗  ██╔██╗ ██║██║   ██║██║   ██║██║██████╔╝ ╚████╔╝ "
echo "    ██╔══╝  ██║╚██╗██║██║▄▄ ██║██║   ██║██║██╔══██╗  ╚██╔╝  "
echo "    ███████╗██║ ╚████║╚██████╔╝╚██████╔╝██║██║  ██║   ██║   "
echo "    ╚══════╝╚═╝  ╚═══╝ ╚══▀▀═╝  ╚═════╝ ╚═╝╚═╝  ╚═╝   ╚═╝   "
echo -e "${SIFIRLAMA}"
echo -e "${MAVI}    Sosyal Medya OSINT Aracı (Geliştirici: Eren) — Kurulum Betiği${SIFIRLAMA}"
echo ""

# root kontrolü
if [ "$EUID" -ne 0 ]; then
    uyari "bu betik root yetkileri gerektirebilir."
    uyari "gerekirse 'sudo bash kurulum.sh' ile çalıştırın."
    echo ""
fi

# python3 kontrolü
bilgi "python3 kontrol ediliyor..."
if command -v python3 &> /dev/null; then
    PYTHON_SURUM=$(python3 --version 2>&1)
    basari "python3 bulundu: $PYTHON_SURUM"
else
    hata "python3 bulunamadı!"
    bilgi "python3 kuruluyor..."
    apt-get update && apt-get install -y python3 python3-pip python3-venv
    basari "python3 kuruldu."
fi

# pip3 kontrolü
bilgi "pip3 kontrol ediliyor..."
if command -v pip3 &> /dev/null; then
    basari "pip3 bulundu."
else
    uyari "pip3 bulunamadı, kuruluyor..."
    apt-get install -y python3-pip
    basari "pip3 kuruldu."
fi

# proje dizinine geç
BETIK_DIZINI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BETIK_DIZINI"
bilgi "proje dizini: $BETIK_DIZINI"

# sanal ortam oluştur (isteğe bağlı)
echo ""
read -p "$(echo -e ${SARI}'sanal ortam (venv) oluşturulsun mu? [E/h]: '${SIFIRLAMA})" VENV_SECIM
VENV_SECIM=${VENV_SECIM:-E}

if [[ "$VENV_SECIM" =~ ^[Ee]$ ]]; then
    bilgi "sanal ortam oluşturuluyor..."
    python3 -m venv venv
    source venv/bin/activate
    basari "sanal ortam oluşturuldu ve aktif edildi."
    bilgi "aktif etmek için: source venv/bin/activate"
fi

# bağımlılıkları kur
echo ""
bilgi "python bağımlılıkları kuruluyor..."
pip3 install -r requirements.txt --quiet
basari "tüm bağımlılıklar başarıyla kuruldu."

# çalıştırma izinleri
bilgi "çalıştırma izinleri ayarlanıyor..."
chmod +x enquiry.py
chmod +x kurulum.sh
basari "izinler ayarlandı."

# raporlar klasörünü oluştur
mkdir -p raporlar
basari "raporlar klasörü oluşturuldu."

# kurulum tamamlandı
echo ""
echo -e "${YESIL}══════════════════════════════════════════════════${SIFIRLAMA}"
echo -e "${YESIL}  [+] Kurulum başarıyla tamamlandı!${SIFIRLAMA}"
echo -e "${YESIL}══════════════════════════════════════════════════${SIFIRLAMA}"
echo ""
echo -e "  ${MAVI}kullanım:${SIFIRLAMA}"
echo -e "    python3 enquiry.py                    ${SARI}# interaktif mod${SIFIRLAMA}"
echo -e "    python3 enquiry.py -k kullanici_adi    ${SARI}# kullanıcı adı ara${SIFIRLAMA}"
echo -e "    python3 enquiry.py -e email@ornek.com  ${SARI}# e-posta analizi${SIFIRLAMA}"
echo -e "    python3 enquiry.py -t +905551234567    ${SARI}# telefon analizi${SIFIRLAMA}"
echo -e "    python3 enquiry.py -i example.com      ${SARI}# domain analizi${SIFIRLAMA}"
echo -e "    python3 enquiry.py --yardim            ${SARI}# yardım${SIFIRLAMA}"
echo ""
echo -e "  ${KIRMIZI}[!]  yalnızca yasal ve etik amaçlarla kullanın!${SIFIRLAMA}"
echo ""
