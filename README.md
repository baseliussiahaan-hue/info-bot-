# Free Fire Info Telegram Bot

Bot Telegram untuk mencari informasi pemain Free Fire. Repo ini berisi kode sumber bot dan daftar dependensi.

- **Repo:** https://github.com/baseliussiahaan-hue/info-bot-
- **Bot Telegram:** https://t.me/fuddjsshedffjfjdjhshsbot
- **Channel:** https://t.me/bsnsztools
- **Owner:** Base — [@bselius](https://t.me/bselius)

## Panduan penggunaan

### 1. Siapkan bot Telegram

1. Buka [@BotFather](https://t.me/BotFather) di Telegram.
2. Buat bot baru dengan perintah `/newbot`, atau pilih bot yang sudah kamu miliki.
3. Salin token bot dari BotFather.
4. **Jangan bagikan token dan jangan menuliskannya langsung di file kode.** Jika token pernah terunggah ke GitHub atau dibagikan kepada orang lain, cabut token lama dan buat token baru melalui BotFather.

### 2. Unduh atau salin repository

Di halaman repo, tekan **Code → Download ZIP** untuk mengunduh semua file. Ekstrak ZIP, lalu buka terminal di folder hasil ekstrak.

File utama:
- `info.py` — kode bot.
- `requirements.txt` — daftar pustaka Python yang diperlukan.
- `README.md` — panduan ini.

### 3. Jalankan di komputer atau Termux

Pastikan Python 3.10 atau lebih baru sudah terpasang. Di Termux, perbarui paket dan pasang Python:

```bash
pkg update && pkg upgrade
pkg install python git
```

Masuk ke folder repository. Jika belum mengunduhnya, kamu bisa mengkloning repo:

```bash
git clone https://github.com/baseliussiahaan-hue/info-bot-.git
cd info-bot-
```

Pasang dependensi:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Atur token sebagai environment variable, kemudian jalankan bot.

**Termux (sesi terminal saat ini):**

```bash
export TELEGRAM_BOT_TOKEN='TEMPEL_TOKEN_BOT_KAMU_DI_SINI'
python info.py
```

Ganti teks `TEMPEL_TOKEN_BOT_KAMU_DI_SINI` dengan token bot milikmu. Jangan kirim perintah yang berisi token ke orang lain atau memasukkannya ke screenshot publik. Token yang diatur dengan `export` berlaku untuk sesi terminal saat ini.

**Windows PowerShell:**

```powershell
$env:TELEGRAM_BOT_TOKEN = "TEMPEL_TOKEN_BOT_KAMU_DI_SINI"
python info.py
```

Biarkan terminal tetap berjalan selama ingin bot aktif. Jika proses dihentikan atau terminal ditutup, bot yang dijalankan dengan cara ini biasanya ikut berhenti.

### 4. Atur token melalui GitHub Secrets (opsional)

Langkah ini diperlukan jika kamu menyiapkan workflow GitHub Actions atau layanan deployment yang membaca GitHub Secrets.

1. Buka [Repository Secrets](https://github.com/baseliussiahaan-hue/info-bot-/settings/secrets/actions).
2. Tekan **New repository secret**.
3. Isi **Name** dengan `TELEGRAM_BOT_TOKEN`.
4. Isi **Secret** dengan token bot yang baru, lalu simpan.

Menambahkan secret saja **tidak otomatis menjalankan bot**. Harus ada workflow atau layanan hosting yang secara eksplisit meneruskan secret tersebut sebagai environment variable `TELEGRAM_BOT_TOKEN`. Jangan menaruh token ke `info.py`, `README.md`, atau file konfigurasi yang dipublikasikan.

### 5. Tes bot

1. Pastikan terminal atau proses hosting menunjukkan bahwa `info.py` sedang berjalan tanpa error.
2. Buka [bot Telegram](https://t.me/fuddjsshedffjfjdjhshsbot).
3. Tekan **Start** atau kirim `/start`.
4. Coba fitur bot sesuai petunjuk yang ditampilkan oleh bot.

## Pemecahan masalah

- **`TELEGRAM_BOT_TOKEN belum diatur`:** atur environment variable sesuai langkah 3, lalu jalankan ulang.
- **`ModuleNotFoundError`:** jalankan `pip install -r requirements.txt` pada environment Python yang sama dengan yang digunakan untuk menjalankan bot.
- **Bot tidak merespons:** pastikan proses masih berjalan, token benar dan belum dicabut, serta periksa pesan error di terminal.
- **Error saat mencari data pemain:** layanan API atau endpoint yang dipakai kode mungkin tidak tersedia. Periksa log; panduan ini tidak menjamin layanan eksternal selalu aktif.

## Catatan

Kode sumber dan dependensi tersedia di repository ini. Keberhasilan instalasi tidak menjamin semua fitur bekerja: endpoint API dan perilaku bot perlu diuji langsung. GitHub Actions juga memiliki batas waktu eksekusi; untuk bot yang harus aktif terus-menerus, gunakan hosting yang mendukung proses persisten.

## Keamanan

- Jangan pernah commit token bot ke repository.
- Jika token terlanjur bocor, cabut melalui [@BotFather](https://t.me/BotFather) dan gunakan token baru.
- Jangan mengunggah log atau screenshot yang memperlihatkan token.
