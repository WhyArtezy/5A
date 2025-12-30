import requests
import pytesseract
from PIL import Image, ImageEnhance
import io
import base64
import uuid
import time
import random

def get_random_proxy():
    try:
        with open("proxy.txt", "r") as f:
            proxies = [line.strip() for line in f if line.strip()]
        if not proxies: return None
        proxy_url = random.choice(proxies)
        return {"http": proxy_url, "https": proxy_url}
    except Exception: return None

def generate_random_phone():
    return "8" + "".join([str(random.randint(0, 9)) for _ in range(10)])

def jalankan_bot():
    # --- INPUT USER ---
    print("="*40)
    print("      BOT AUTO REG CATAPULT")
    print("="*40)
    invite_code = input("Masukkan Kode Invite: ").strip()
    try:
        max_target = int(input("Berapa akun yang ingin dibuat?: "))
    except ValueError:
        print("[!] Input jumlah harus angka. Default: 1")
        max_target = 1
    print("-" * 40)

    berhasil_count = 0
    attempt = 1
    nomor_target = generate_random_phone()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36",
        "Content-Type": "application/json",
        "Referer": "https://www.5a.fund/"
    }

    while berhasil_count < max_target:
        current_proxy = get_random_proxy()
        try:
            with requests.Session() as session:
                if current_proxy: session.proxies.update(current_proxy)
                
                # 1. Ambil Captcha
                res_cap = session.get("https://www.5a.fund/api/v1/captchas", headers=headers, timeout=10).json()
                data_c = res_cap.get("data", {})
                captcha_key = data_c.get("captcha_key")
                img_b64 = data_c.get("captcha_image_content")

                if not img_b64: continue

                # 2. OCR
                if "," in img_b64: img_b64 = img_b64.split(",")[1]
                image = Image.open(io.BytesIO(base64.b64decode(img_b64))).convert('L')
                image = ImageEnhance.Contrast(image).enhance(2.5)
                
                kode_ocr = pytesseract.image_to_string(image, config='--psm 8').strip()
                kode_ocr = "".join(e for e in kode_ocr if e.isalnum())

                if len(kode_ocr) != 4:
                    print(f"\r[ Mencari Captcha ] Berhasil: {berhasil_count}/{max_target} | OCR: {kode_ocr}...", end="")
                    continue
                
                # 3. Kirim Pendaftaran
                payload = {
                    "area": "62", "phone": nomor_target,
                    "captcha_code": kode_ocr, "captcha_key": captcha_key,
                    "country": "ID", "device_number": str(uuid.uuid4()),
                    "invite_code": invite_code, # Menggunakan input user
                    "password": "Alwi!1202",
                    "reg_type": "phone", "repassword": "Alwi!1202"
                }

                res_reg = session.post("https://www.5a.fund/api/v1/users", json=payload, headers=headers, timeout=15).json()
                
                code = res_reg.get("code")
                has_token = "access_token" in str(res_reg.get("data", ""))

                if code == 0 or has_token:
                    berhasil_count += 1
                    print(f"\n[!!!] BERHASIL KE-{berhasil_count}: 62{nomor_target}")
                    with open("hasil_reg.txt", "a") as f:
                        f.write(f"62{nomor_target}|Alwi!1202|Reff:{invite_code}\n")
                    
                    nomor_target = generate_random_phone() # Ganti nomor untuk akun selanjutnya
                
                elif "30003" in str(code):
                    pass # Captcha salah, biarkan loop berjalan ulang
                elif "10050" in str(code):
                    nomor_target = generate_random_phone() # Ganti nomor jika duplikat
                else:
                    # Menampilkan pesan error lain jika ada (misal: invite code salah)
                    msg = res_reg.get("msg", "Error tidak dikenal")
                    print(f"\n[-] Respon: {msg}")
                    if "invite" in str(msg).lower():
                        print("[!] Kode Invite salah/tidak valid. Berhenti.")
                        break

        except Exception:
            pass
        
        attempt += 1

    print("\n" + "="*40)
    print(f" SELESAI! Berhasil membuat {berhasil_count} akun.")
    print("="*40)

if __name__ == "__main__":
    jalankan_bot()
