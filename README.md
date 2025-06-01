# Tugas-Besar-Strategi-Algoritma-2025-Placeholder

## Pemanfaatan Algoritma Greedy dalam Pembuatan Bot Permainan Diamonds

## Catatan

Algoritma Greedy final kami diimplementasikan pada file greedy12.py yang terdapat pada folder src/tubes1-IF2211-bot-starter-pack-1.0.1/game/logic

## Table of Contents

- [General Info](#general-information)
- [Team Members](#team-members)
- [How to Run](#how-to-run)
- [Program Structure](#program-structure)

## General Information

Pada tugas pertama Strategi Algoritma ini, dibuat sebuah bot yang nantinya akan dipertandingkan satu sama lain. Bot tersebut akan menggunakan strategi greedy dalam melakukan pergerakan. Secara singkat dan sederhana, strategi greedy yang kami gunakan adalah memilih diamond berdasarkan perhitugan jarak terdakat dikurangi oleh weight kumulatif dari diamond dan sekitarnya.

Berikut adalah deskripsi Program permainan Diamonds:

1. Game engine, yang secara umum berisi:
   Kode backend permainan, yang berisi logic permainan secara keseluruhan serta API yang disediakan untuk berkomunikasi dengan frontend dan program bot
   Kode frontend permainan, yang berfungsi untuk memvisualisasikan permainan

2. Bot starter pack, yang secara umum berisi:
   Program untuk memanggil API yang tersedia pada backend
   Program bot logic (bagian ini yang akan kalian implementasikan dengan algoritma greedy untuk bot kelompok kalian)
   Program utama (main) dan utilitas lainnya

## How to Run

1. Pemasangan Persyaratan:

- Python 3 (https://www.python.org/downloads/)
- Node.js (https://nodejs.org/en)
- Docker desktop (https://www.docker.com/products/docker-desktop/)
- Yarn

2. Clone repository ini.

```
$ git clone https://github.com/Protoflicker/greedyalgorithmbot-diamonds
```

```
npm install --global yarn
```

3. Masuk ke root directory dari project.

```
cd tubes1-IF2110-game-engine-1.1.0
```

4. Install dependencies menggunakan Yarn.

```
yarn
```

5. Setup default environment variable dengan menjalankan script berikut
   Untuk Windows

```
./scripts/copy-env.bat
```

Untuk Linux / (possibly) macOS

```
chmod +x ./scripts/copy-env.sh
./scripts/copy-env.sh
```

6.  Setup local database (buka aplikasi docker desktop terlebih dahulu, lalu jalankan command berikut di terminal)

```
docker compose up -d database
```

Untuk Windows

```
./scripts/setup-db-prisma.bat
```

Untuk Linux / (possibly) macOS

```
chmod +x ./scripts/setup-db-prisma.sh
./scripts/setup-db-prisma.s
```

7. Build

```
npm run build
```

8. Run

```
npm run start
```

9. Masuk ke root directory dari projec

```
cd tubes1-IF2110-bot-starter-pack-1.0.1
```

10. Install dependencies menggunakan pip

```
pip install -r requirements.txt
```

11. Untuk menjalankan beberapa bot sekaligus (pada contoh ini, kita menjalankan 4 bot dengan logic yang sama, yaitu game/logic/random.py)

Untuk windows

```
./run-bots.bat
```

Untuk Linux / (possibly) macOS

```
./run-bots.sh
```

## Team Members

| **NIM**   |            **Nama**           |
| :------:  | :---------------------------: |
| 123140021 |        Adi Septriansyah       |
| 122140126 |  Alfino Pardiansyah Hutahean  |
| 123140105 |     Ariq Ramadhinov Ronny     |

## Program Structure

```bash
Placeholder
├── doc
│   └── Placeholder.pdf
├── src (front-end)
│   ├── __pycache__ (decode.cpython-311.pyc)
│   ├── game
│   │   ├── __pycache__
│   │   ├── logic
│   │   │   ├── __pycache__
│   │   │   ├── __init__.py
│   │   │   ├── astarbot.py.py
│   │   │   ├── base.py
│   │   │   ├── desktop.ini
│   │   │   ├── greedy12.py (MainLogic)
│   │   │   ├── greedyredwork.py
│   │   │   ├── original10.py
│   │   │   └── random.py
│   │   ├── __init__.py
│   │   ├── api.py
│   │   ├── board_handler.py
│   │   ├── bot_handler.py
│   │   ├── models.py
│   │   └── util.py
│   ├── .gitignore
│   ├── decode.py
│   ├── main.py
│   ├── run-bots.bat
│   ├── run-bots.sh
│   └── README.md  
└── README.md
```
