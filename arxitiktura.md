# 💰 MOLIYAVIY BOT — TO'LIQ ARXITEKTURA HUJJATI

> **Versiya:** 2.0.0  
> **Yaratilgan:** 2026-yil  
> **Muallif:** Senior Bot Architect (20 yillik tajriba, 10M+ bot yaratilgan)  
> **Maqsad:** Shaxsiy va biznes moliyasini to'liq boshqarish

---

## 📋 MUNDARIJA

1. [Loyiha haqida umumiy ma'lumot](#1-loyiha-haqida)
2. [Funksiyalar ro'yxati (20+)](#2-funksiyalar)
3. [Arxitektura diagrammasi](#3-arxitektura)
4. [Ma'lumotlar bazasi sxemasi](#4-database)
5. [Bot buyruqlari](#5-buyruqlar)
6. [Hisobot modullari](#6-hisobotlar)
7. [Texnologiyalar steki](#7-texnologiyalar)
8. [Xavfsizlik](#8-xavfsizlik)
9. [Deployment](#9-deployment)
10. [Kelajakdagi rejalar](#10-roadmap)

---

## 1. LOYIHA HAQIDA

### 1.1 Vazifa (Mission)
Foydalanuvchiga o'z moliyaviy ahvolini real vaqtda kuzatish, tahlil qilish va boshqarishga yordam beruvchi aqlli Telegram boti yaratish.

### 1.2 Ko'rish (Vision)
Har bir o'zbek foydalanuvchi uchun **shaxsiy moliyaviy maslahatchi** vazifasini bajaruvchi, 7/24 ishlayotgan, ko'p valyutali, AI-powered bot.

### 1.3 Asosiy muammo (Pain Points) — Raqobatchi botlar tahlili
Mavjud moliya botlarini tahlil qilganda quyidagi kamchiliklar aniqlandi:

| Muammo | Eski botlar | Bizning bot |
|--------|-------------|-------------|
| Faqat oddiy kirim/chiqim | ✅ | ✅ |
| Ko'p valyuta qo'llab-quvvatlash | ❌ | ✅ |
| AI tahlil va maslahat | ❌ | ✅ |
| Maqsad va byudjet tizimi | ❌ | ✅ |
| Guruh/oilaviy hisob | ❌ | ✅ |
| Eslatmalar tizimi | ❌ | ✅ |
| To'liq hisobot (kun/hafta/oy/yil) | ⚠️ | ✅ |
| Grafik va diagrammalar | ❌ | ✅ |
| Eksport (Excel/PDF) | ❌ | ✅ |
| Qarz boshqaruvi | ❌ | ✅ |

---

## 2. FUNKSIYALAR (20+ ta)

### 🟢 BLOK A — ASOSIY MOLIYA (Core Finance)

#### F-01: Kirim Qo'shish
```
Funksiya nomi : add_income()
Buyruq        : /kirim yoki "Kirim" tugmasi
Parametrlar   : miqdor, kategoriya, tavsif, sana, valyuta
Misol         : /kirim 500000 maosh "Iyun oylik"
Xususiyat     : Avtomatik valyuta konvertatsiya
```

#### F-02: Chiqim Qo'shish
```
Funksiya nomi : add_expense()
Buyruq        : /chiqim yoki "Chiqim" tugmasi
Parametrlar   : miqdor, kategoriya, tavsif, sana, valyuta
Misol         : /chiqim 50000 oziq-ovqat "Non va sut"
Xususiyat     : Byudjet chegarasini tekshiradi, ogohlantiradi
```

#### F-03: Balans Ko'rish
```
Funksiya nomi : show_balance()
Buyruq        : /balans
Ko'rsatadi    : Jami balans, har bir hisob balansi, valyuta bo'yicha
Yangilanadi   : Real vaqtda
```

#### F-04: Tez Tranzaksiya
```
Funksiya nomi : quick_transaction()
Buyruq        : /t 50000 taksi
Vazifasi      : Minimal matn bilan tezkor yozuv
Kategoriya    : Avtomatik AI bilan aniqlaydi
```

---

### 🔵 BLOK B — HISOBOT TIZIMI (Reports)

#### F-05: Kunlik Hisobot
```
Funksiya nomi : daily_report()
Buyruq        : /kun yoki /today
Ko'rsatadi    :
  - Bugungi barcha tranzaksiyalar
  - Kirim vs Chiqim grafigi
  - Kategoriyalar bo'yicha taqsimot
  - Kecha bilan taqqoslash (% farq)
  - Eng katta xarajat
  - Balans o'zgarishi
Yuborish vaqti: Har kuni kechqurun 21:00 (avtomatik)
```

#### F-06: Haftalik Hisobot
```
Funksiya nomi : weekly_report()
Buyruq        : /hafta yoki /week
Ko'rsatadi    :
  - 7 kunlik trend grafigi (chiziqli)
  - Hafta byudjeti bajarilishi
  - Eng ko'p xarajat qilingan kun
  - Kategoriyalar doirasi (pie chart)
  - O'tgan hafta bilan taqqoslash
  - Tejash koeffitsienti
  - Top-5 xarajat
Yuborish vaqti: Har dushanba 09:00 (avtomatik)
```

#### F-07: Oylik Hisobot
```
Funksiya nomi : monthly_report()
Buyruq        : /oy yoki /month
Ko'rsatadi    :
  - 30 kunlik to'liq grafik
  - Daromad manbalari tahlili
  - Xarajat kategoriyalari (% va miqdor)
  - Byudjet bajarilish hisoboti
  - Maqsadlarga erishish holati
  - Qarz/ssuda holati
  - Net tejash summasi
  - Prognoz (keyingi oyga)
Yuborish vaqti: Har oyning 1-kuni 08:00 (avtomatik)
```

#### F-08: Yillik Hisobot
```
Funksiya nomi : yearly_report()
Buyruq        : /yil yoki /year
Ko'rsatadi    :
  - 12 oylik trend tahlili
  - Yillik daromad o'sishi
  - Eng yaxshi/yomon oy
  - Kategoriyalar bo'yicha yillik xarajat
  - Moliyaviy sog'liqlik balli (0-100)
  - Kelgusi yilga prognoz
  - Moliyaviy maslahatlar (AI)
Yuborish vaqti: 31-dekabr 23:00 (avtomatik)
```

#### F-09: Maxsus Davr Hisoboti
```
Funksiya nomi : custom_report()
Buyruq        : /hisobot [boshlanish] [tugash]
Misol         : /hisobot 01.05.2026 31.05.2026
```

---

### 🟡 BLOK C — BYUDJET TIZIMI (Budget Management)

#### F-10: Byudjet Belgilash
```
Funksiya nomi : set_budget()
Buyruq        : /byudjet
Qo'llaniladi  : Kategoriya bo'yicha oylik limit
Misol         : /byudjet oziq-ovqat 800000
Ogohlantirish : 80% ga yetganda va 100% da xabar
```

#### F-11: Byudjet Tahlili
```
Funksiya nomi : budget_analysis()
Buyruq        : /byudjet_holat
Ko'rsatadi    : 
  - Progress bar (har kategoriya uchun)
  - Qolgan summa
  - Oshib ketgan kategoriyalar (qizil)
  - Samarali kategoriyalar (yashil)
```

---

### 🟠 BLOK D — MAQSAD TIZIMI (Goals)

#### F-12: Moliyaviy Maqsad
```
Funksiya nomi : set_goal()
Buyruq        : /maqsad
Qo'llaniladi  : Yig'ish maqsadi qo'yish
Misol         : /maqsad "Yangi telefon" 5000000 2026-12-31
Ko'rsatadi    :
  - Progress bar
  - Kunlik yig'ish kerak bo'lgan miqdor
  - Taxminiy erishish sanasi
  - Motivatsion xabarlar
```

#### F-13: Maqsadlar Ro'yxati
```
Funksiya nomi : list_goals()
Buyruq        : /maqsadlar
```

---

### 🔴 BLOK E — QARZ BOSHQARUVI (Debt Management)

#### F-14: Qarz Berish
```
Funksiya nomi : add_debt_given()
Buyruq        : /berdim
Misol         : /berdim Akbar 200000 "Avtobus uchun"
Eslatma       : Belgilangan sanada avtomatik eslatma
```

#### F-15: Qarz Olish
```
Funksiya nomi : add_debt_received()
Buyruq        : /oldim
Misol         : /oldim Bobur 500000 "Biznes uchun"
```

#### F-16: Qarz Holati
```
Funksiya nomi : debt_status()
Buyruq        : /qarzlar
Ko'rsatadi    :
  - Menga qarzlilar ro'yxati
  - Men qarzli bo'lganlar ro'yxati
  - Jami qarz balansi
```

---

### 🟣 BLOK F — HISOBLAR TIZIMI (Accounts)

#### F-17: Ko'p Hisob
```
Funksiya nomi : manage_accounts()
Buyruq        : /hisoblar
Tur           : Naqd, Bank kartasi, Elektron hamyon (Payme, Click, Uzum)
Valyuta       : UZS, USD, EUR, RUB
```

#### F-18: Hisob Transferi
```
Funksiya nomi : transfer()
Buyruq        : /transfer
Misol         : /transfer naqd karta 1000000
```

---

### ⚪ BLOK G — QIDIRUV VA FILTR (Search & Filter)

#### F-19: Tranzaksiya Qidirish
```
Funksiya nomi : search_transactions()
Buyruq        : /qidir [matn]
Misol         : /qidir taksi
Filtrlar      : Sana, Kategoriya, Miqdor oralig'i, Hisoblar
```

#### F-20: Kategoriyalar Boshqaruvi
```
Funksiya nomi : manage_categories()
Buyruq        : /kategoriyalar
Standart      : Oziq-ovqat, Transport, Maosh, Ijara, Sog'liqqa...
Maxsus        : Foydalanuvchi o'z kategoriyasini qo'sha oladi
```

---

### 🌟 BLOK H — AI VA PREMIUM FUNKSIYALAR

#### F-21: AI Moliyaviy Maslahat
```
Funksiya nomi : ai_advice()
Buyruq        : /maslahat
Tahlil qiladi :
  - Xarajat odatlarini
  - Isrof qilinayotgan sohalarni
  - Tejash imkoniyatlarini
  - Moliyaviy sog'liqni
Natija        : Shaxsiylashtirilgan 5 ta maslahat
```

#### F-22: Eksport
```
Funksiya nomi : export_data()
Buyruq        : /eksport
Format        : Excel (.xlsx), PDF, CSV
Davr          : Kunlik, Haftalik, Oylik, Yillik, Maxsus
```

#### F-23: Valyuta Konvertatsiya
```
Funksiya nomi : currency_convert()
Buyruq        : /kurs yoki /valyuta
Ma'lumot      : Real vaqt kursi (API orqali)
Valyutalar    : USD, EUR, RUB, KZT → UZS
```

#### F-24: Eslatmalar (Reminders)
```
Funksiya nomi : set_reminder()
Buyruq        : /eslatma
Tur           : To'lov eslatmasi, Byudjet tekshiruvi, Maqsad eslatmasi
Misol         : /eslatma "Internet to'lovi" har-oy 25
```

#### F-25: Statistik Tahlil
```
Funksiya nomi : statistics()
Buyruq        : /statistika
Ko'rsatadi    :
  - O'rtacha kunlik xarajat
  - Eng ko'p xarajat qilinadigan kun/soat
  - Xarajat trendlari
  - Anomal tranzaksiyalar (g'ayrioddiy katta)
  - Tejash ko'rsatkichi
```

#### F-26: Guruh/Oilaviy Hisob
```
Funksiya nomi : family_account()
Buyruq        : /guruh
Funksiya      : Bir nechta foydalanuvchi bitta umumiy hisob yurita oladi
Ruxsatlar     : Admin, Editor, Viewer
```

---

## 3. ARXITEKTURA

```
┌─────────────────────────────────────────────────────────┐
│                    FOYDALANUVCHI                        │
│                  (Telegram Client)                      │
└─────────────────────┬───────────────────────────────────┘
                      │  HTTPS / WebSocket
                      ▼
┌─────────────────────────────────────────────────────────┐
│              TELEGRAM BOT API                           │
│           (api.telegram.org)                            │
└─────────────────────┬───────────────────────────────────┘
                      │  Webhook / Long Polling
                      ▼
┌─────────────────────────────────────────────────────────┐
│                  BOT CORE (Python)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────────┐  │
│  │  Dispatcher │  │  Middleware │  │  State Manager │  │
│  │  (Router)   │  │  (Logging)  │  │  (FSM)         │  │
│  └──────┬──────┘  └──────┬──────┘  └───────┬────────┘  │
│         └────────────────┼─────────────────┘           │
│                          ▼                              │
│  ┌────────────────────────────────────────────────────┐ │
│  │              HANDLER LAYER                         │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │ │
│  │  │ Income   │ │ Expense  │ │ Reports Handler  │   │ │
│  │  │ Handler  │ │ Handler  │ │ (Kun/Hafta/Oy)   │   │ │
│  │  └──────────┘ └──────────┘ └──────────────────┘   │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │ │
│  │  │ Budget   │ │ Goals    │ │ Debt Handler     │   │ │
│  │  │ Handler  │ │ Handler  │ │                  │   │ │
│  │  └──────────┘ └──────────┘ └──────────────────┘   │ │
│  └────────────────────────────────────────────────────┘ │
│                          ▼                              │
│  ┌────────────────────────────────────────────────────┐ │
│  │              SERVICE LAYER                         │ │
│  │  ┌──────────────┐  ┌──────────────────────────┐   │ │
│  │  │ Finance Svc  │  │ Report Generator Service │   │ │
│  │  │ - CRUD ops   │  │ - Chart generation       │   │ │
│  │  │ - Validation │  │ - PDF/Excel export       │   │ │
│  │  └──────────────┘  └──────────────────────────┘   │ │
│  │  ┌──────────────┐  ┌──────────────────────────┐   │ │
│  │  │ Currency Svc │  │ AI Advisor Service       │   │ │
│  │  │ - Rate fetch │  │ - Pattern analysis       │   │ │
│  │  │ - Convert    │  │ - Recommendations        │   │ │
│  │  └──────────────┘  └──────────────────────────┘   │ │
│  │  ┌──────────────┐  ┌──────────────────────────┐   │ │
│  │  │ Notif. Svc   │  │ Scheduler Service        │   │ │
│  │  │ - Reminders  │  │ - Daily/Weekly/Monthly   │   │ │
│  │  │ - Alerts     │  │   auto-reports           │   │ │
│  │  └──────────────┘  └──────────────────────────┘   │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
    ┌──────────┐ ┌─────────┐ ┌──────────┐
    │PostgreSQL│ │  Redis  │ │ External │
    │ Database │ │ Cache   │ │   APIs   │
    │          │ │         │ │ -Currency│
    │ -Users   │ │ -Session│ │ -AI      │
    │ -Transact│ │ -Cache  │ │ -Charts  │
    │ -Budgets │ │ -Queue  │ └──────────┘
    │ -Goals   │ └─────────┘
    │ -Debts   │
    └──────────┘
```

---

## 4. MA'LUMOTLAR BAZASI SXEMASI

### 4.1 Jadvallar

```sql
-- Foydalanuvchilar
CREATE TABLE users (
    id              BIGINT PRIMARY KEY,          -- Telegram user_id
    username        VARCHAR(50),
    full_name       VARCHAR(100),
    language        VARCHAR(5) DEFAULT 'uz',
    currency        VARCHAR(3) DEFAULT 'UZS',
    timezone        VARCHAR(50) DEFAULT 'Asia/Tashkent',
    is_premium      BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT NOW(),
    last_active     TIMESTAMP
);

-- Hisoblar (Naqd, Karta, Hamyon)
CREATE TABLE accounts (
    id              SERIAL PRIMARY KEY,
    user_id         BIGINT REFERENCES users(id),
    name            VARCHAR(100),               -- "Naqd", "Payme", "Karta"
    type            VARCHAR(20),                -- cash | card | wallet
    currency        VARCHAR(3) DEFAULT 'UZS',
    balance         DECIMAL(15,2) DEFAULT 0,
    color           VARCHAR(7),                 -- UI uchun rang (#FF5733)
    icon            VARCHAR(50),
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Kategoriyalar
CREATE TABLE categories (
    id              SERIAL PRIMARY KEY,
    user_id         BIGINT REFERENCES users(id),  -- NULL = standart
    name            VARCHAR(100),
    type            VARCHAR(10),                  -- income | expense
    icon            VARCHAR(50),
    color           VARCHAR(7),
    is_default      BOOLEAN DEFAULT FALSE
);

-- Tranzaksiyalar (asosiy jadval)
CREATE TABLE transactions (
    id              SERIAL PRIMARY KEY,
    user_id         BIGINT REFERENCES users(id),
    account_id      INT REFERENCES accounts(id),
    category_id     INT REFERENCES categories(id),
    type            VARCHAR(10),                  -- income | expense | transfer
    amount          DECIMAL(15,2),
    currency        VARCHAR(3) DEFAULT 'UZS',
    amount_uzs      DECIMAL(15,2),               -- UZSda saqlangan miqdor
    description     TEXT,
    date            DATE DEFAULT CURRENT_DATE,
    created_at      TIMESTAMP DEFAULT NOW(),
    is_recurring    BOOLEAN DEFAULT FALSE,
    recurring_id    INT                           -- Takroriy to'lov bog'lanishi
);

-- Byudjetlar
CREATE TABLE budgets (
    id              SERIAL PRIMARY KEY,
    user_id         BIGINT REFERENCES users(id),
    category_id     INT REFERENCES categories(id),
    amount          DECIMAL(15,2),
    period          VARCHAR(10),                  -- monthly | weekly
    month           INT,
    year            INT,
    alert_80        BOOLEAN DEFAULT TRUE,
    alert_100       BOOLEAN DEFAULT TRUE
);

-- Moliyaviy maqsadlar
CREATE TABLE goals (
    id              SERIAL PRIMARY KEY,
    user_id         BIGINT REFERENCES users(id),
    name            VARCHAR(200),
    target_amount   DECIMAL(15,2),
    current_amount  DECIMAL(15,2) DEFAULT 0,
    currency        VARCHAR(3) DEFAULT 'UZS',
    deadline        DATE,
    is_achieved     BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Qarzlar
CREATE TABLE debts (
    id              SERIAL PRIMARY KEY,
    user_id         BIGINT REFERENCES users(id),
    person_name     VARCHAR(100),
    amount          DECIMAL(15,2),
    currency        VARCHAR(3) DEFAULT 'UZS',
    type            VARCHAR(10),                  -- given | received
    description     TEXT,
    due_date        DATE,
    is_settled      BOOLEAN DEFAULT FALSE,
    date            DATE DEFAULT CURRENT_DATE,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Eslatmalar
CREATE TABLE reminders (
    id              SERIAL PRIMARY KEY,
    user_id         BIGINT REFERENCES users(id),
    title           VARCHAR(200),
    amount          DECIMAL(15,2),
    schedule        VARCHAR(50),                  -- "monthly:25", "weekly:1"
    is_active       BOOLEAN DEFAULT TRUE,
    last_sent       TIMESTAMP,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Guruh hisoblar
CREATE TABLE group_accounts (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100),
    owner_id        BIGINT REFERENCES users(id),
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE group_members (
    group_id        INT REFERENCES group_accounts(id),
    user_id         BIGINT REFERENCES users(id),
    role            VARCHAR(10),                  -- admin | editor | viewer
    PRIMARY KEY (group_id, user_id)
);
```

---

## 5. BOT BUYRUQLARI

### 5.1 Asosiy Buyruqlar

| Buyruq | Tavsif | Misol |
|--------|--------|-------|
| `/start` | Botni ishga tushirish | `/start` |
| `/yordam` | Barcha buyruqlar ro'yxati | `/yordam` |
| `/balans` | Joriy balans | `/balans` |
| `/kirim` | Kirim qo'shish | `/kirim 500000 maosh` |
| `/chiqim` | Chiqim qo'shish | `/chiqim 50000 non` |
| `/t` | Tezkor tranzaksiya | `/t 20000 taksi` |

### 5.2 Hisobot Buyruqlari

| Buyruq | Tavsif |
|--------|--------|
| `/kun` | Bugungi hisobot |
| `/kecha` | Kechagi hisobot |
| `/hafta` | Joriy hafta |
| `/oy` | Joriy oy |
| `/yil` | Joriy yil |
| `/hisobot DD.MM.YYYY DD.MM.YYYY` | Maxsus davr |

### 5.3 Boshqaruv Buyruqlari

| Buyruq | Tavsif |
|--------|--------|
| `/byudjet` | Byudjet boshqaruvi |
| `/maqsad` | Maqsad qo'shish |
| `/maqsadlar` | Maqsadlar ro'yxati |
| `/qarzlar` | Qarzlar holati |
| `/hisoblar` | Hisoblar boshqaruvi |
| `/transfer` | Hisoblar orasida o'tkazma |
| `/kategoriyalar` | Kategoriyalar |
| `/kurs` | Valyuta kurslari |
| `/statistika` | To'liq statistika |
| `/maslahat` | AI moliyaviy maslahat |
| `/eksport` | Ma'lumotlarni eksport qilish |
| `/eslatmalar` | Eslatmalar boshqaruvi |
| `/sozlamalar` | Bot sozlamalari |

---

## 6. HISOBOT MODULLARI

### 6.1 Kunlik Hisobot Namunasi
```
📊 BUGUNGI HISOBOT — 22.06.2026
━━━━━━━━━━━━━━━━━━━━━━
💰 Kirim:    1,500,000 so'm
💸 Chiqim:     450,000 so'm
💵 Balans:   1,050,000 so'm
━━━━━━━━━━━━━━━━━━━━━━
📌 KATEGORIYALAR:
🍞 Oziq-ovqat    150,000 (33%)
🚗 Transport      80,000 (18%)
☕ Kafe           60,000 (13%)
🛒 Xarid         160,000 (36%)
━━━━━━━━━━━━━━━━━━━━━━
📈 Kecha bilan: +5% yaxshi
🎯 Byudjet: 67% bajarildi
```

### 6.2 Oylik Hisobot Namunasi
```
📅 IYUN 2026 — OYLIK HISOBOT
━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 Jami kirim:    8,500,000 so'm
💸 Jami chiqim:   6,200,000 so'm
💎 Tejaldi:       2,300,000 so'm
📊 Tejash %:            27%
━━━━━━━━━━━━━━━━━━━━━━━━━━
🏆 ENG KO'P XARAJAT:
1. Oziq-ovqat    2,100,000 (34%)
2. Transport       950,000 (15%)
3. Kommunal        600,000 (10%)
4. Kiyim           500,000  (8%)
5. Ko'ngilochar    350,000  (6%)
━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 O'tgan oyga nisbatan: +12%
🎯 Maqsad: Telefon 45% tayyor
⚠️  Kafe byudjeti 110% oshdi!
━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 AI MASLAHAT:
Kafe xarajatlaringiz normadan
30% yuqori. Uyda qahva qilsangiz
oyiga ~200,000 tejaysiz!
```

---

## 7. TEXNOLOGIYALAR STEKI

### 7.1 Backend
```yaml
Dasturlash tili  : Python 3.11+
Bot Framework    : Aiogram 3.x (asinxron, zamonaviy)
Database ORM     : SQLAlchemy 2.0 (asinxron)
Ma'lumot bazasi  : PostgreSQL 15
Kesh             : Redis 7.x
Task Scheduler   : APScheduler / Celery
```

### 7.2 Grafik va Vizualizatsiya
```yaml
Grafik           : Matplotlib + Seaborn
Chart            : Plotly (interaktiv)
PDF yaratish     : ReportLab
Excel yaratish   : openpyxl
```

### 7.3 Tashqi API'lar
```yaml
Valyuta kurslari : exchangeratesapi.io yoki fixer.io
AI maslahat      : OpenAI GPT-4 / Anthropic Claude API
```

### 7.4 Deployment
```yaml
Server           : Ubuntu 22.04 LTS
Container        : Docker + Docker Compose
Reverse Proxy    : Nginx
SSL              : Let's Encrypt (Certbot)
CI/CD            : GitHub Actions
Monitoring       : Prometheus + Grafana
Logs             : Elasticsearch + Kibana
```

### 7.5 Xavfsizlik
```yaml
Ma'lumot shifrlash : AES-256 (maxfiy ma'lumotlar)
Transport          : HTTPS/TLS 1.3
Auth               : Telegram OAuth (built-in)
Rate Limiting      : Redis-based
Input Validation   : Pydantic v2
SQL Injection      : SQLAlchemy ORM (himoyalangan)
```

---

## 8. XAVFSIZLIK

### 8.1 Ma'lumotlarni Himoyalash
- Barcha moliyaviy ma'lumotlar shifrlangan holda saqlanadi
- Foydalanuvchi ma'lumotlari hech qachon uchinchi tomonlarga uzatilmaydi
- Parol yoki maxfiy kalitlar environment variable'da saqlanadi

### 8.2 Rate Limiting
```python
# Har foydalanuvchi uchun:
# - 60 ta so'rov/daqiqa
# - 1000 ta so'rov/kun
# - Oshib ketsa: 5 daqiqa ban
```

### 8.3 Backup Strategiyasi
```
Avtomatik backup: Har kuni 03:00 da
Saqlash muddati: 30 kun
Joy: Amazon S3 yoki lokal server
```

---

## 9. DEPLOYMENT (O'rnatish)

### 9.1 Minimal Talablar
```
RAM    : 512 MB (tavsiya: 1 GB)
CPU    : 1 vCPU (tavsiya: 2 vCPU)
Disk   : 10 GB SSD
OS     : Ubuntu 22.04 / Debian 11
Python : 3.11+
```

### 9.2 Tezkor O'rnatish
```bash
# 1. Repozitoriyani clone qilish
git clone https://github.com/yourname/finance-bot.git
cd finance-bot

# 2. .env faylini sozlash
cp .env.example .env
nano .env  # TOKEN, DATABASE_URL, va boshqalarni to'ldiring

# 3. Docker bilan ishga tushirish
docker-compose up -d

# 4. Ma'lumot bazasini yaratish
docker-compose exec bot python -m alembic upgrade head

# 5. Bot ishlayapti! ✅
```

### 9.3 .env Namunasi
```env
# Telegram
BOT_TOKEN=1234567890:ABCdef...
ADMIN_ID=123456789

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/financebot

# Redis
REDIS_URL=redis://localhost:6379

# Valyuta API
CURRENCY_API_KEY=your_api_key_here

# AI (ixtiyoriy)
OPENAI_API_KEY=sk-...
```

---

## 10. KELAJAKDAGI REJALAR (Roadmap)

### v2.1 — Q3 2026
- [ ] Investitsiya portfeli kuzatuvi
- [ ] Kriptovalyuta qo'llab-quvvatlash (BTC, ETH)
- [ ] Chek/kvitansiya skaneri (AI OCR)
- [ ] Bank kartasi avtomatik sinxronizatsiyasi

### v2.2 — Q4 2026
- [ ] Web panel (dashboard.finance-bot.uz)
- [ ] iOS / Android ilovasi
- [ ] Oilaviy premium rejim
- [ ] Moliyaviy trening kurslar

### v3.0 — 2027
- [ ] Bank API integratsiyasi (Kapitalbank, Hamkor Bank)
- [ ] Payme / Click avtomatik to'lov tranzaksiyalari import
- [ ] Shaxsiy moliyaviy AI assistant (full LLM)
- [ ] NFT/DeFi integratsiyasi

---

## 📁 LOYIHA FAYL TUZILMASI

```
finance-bot/
├── 📄 README.md
├── 📄 docker-compose.yml
├── 📄 Dockerfile
├── 📄 .env.example
├── 📄 requirements.txt
│
├── 📁 bot/
│   ├── 📄 main.py                  # Bot ishga tushirish
│   ├── 📄 config.py                # Konfiguratsiya
│   │
│   ├── 📁 handlers/                # Barcha handler'lar
│   │   ├── 📄 start.py
│   │   ├── 📄 income.py
│   │   ├── 📄 expense.py
│   │   ├── 📄 reports.py
│   │   ├── 📄 budget.py
│   │   ├── 📄 goals.py
│   │   ├── 📄 debts.py
│   │   ├── 📄 accounts.py
│   │   └── 📄 settings.py
│   │
│   ├── 📁 services/                # Biznes logika
│   │   ├── 📄 finance_service.py
│   │   ├── 📄 report_service.py
│   │   ├── 📄 currency_service.py
│   │   ├── 📄 ai_service.py
│   │   ├── 📄 chart_service.py
│   │   └── 📄 scheduler_service.py
│   │
│   ├── 📁 models/                  # Database modellari
│   │   ├── 📄 user.py
│   │   ├── 📄 transaction.py
│   │   ├── 📄 account.py
│   │   ├── 📄 budget.py
│   │   ├── 📄 goal.py
│   │   └── 📄 debt.py
│   │
│   ├── 📁 keyboards/               # Telegram klaviaturalar
│   │   ├── 📄 main_menu.py
│   │   ├── 📄 categories.py
│   │   └── 📄 reports.py
│   │
│   └── 📁 utils/                   # Yordamchi funksiyalar
│       ├── 📄 formatters.py
│       ├── 📄 validators.py
│       └── 📄 helpers.py
│
├── 📁 migrations/                  # Alembic migratsiyalar
│   └── 📁 versions/
│
└── 📁 tests/                       # Testlar
    ├── 📄 test_finance.py
    ├── 📄 test_reports.py
    └── 📄 test_currency.py
```

---

## 📊 LOYIHA METRIKALARI

| Ko'rsatkich | Qiymat |
|-------------|--------|
| Jami funksiya | 26 ta |
| Hisobot turi | 5 ta (kun/hafta/oy/yil/maxsus) |
| Qo'llab-quvvatlanadigan valyuta | 10+ |
| Buyruqlar soni | 35+ |
| Ma'lumotlar bazasi jadvallari | 10 ta |
| Standart kategoriyalar | 30+ |
| Maksimal foydalanuvchi | 100,000+ |
| Javob vaqti | < 500ms |
| Uptime maqsadi | 99.9% |

---

## ✅ YAKUNIY XULOSA

Bu bot **O'zbekistondagi eng to'liq moliyaviy Telegram boti** bo'lishi uchun loyihalashtirilgan:

1. **26+ funksiya** — oddiy kirim/chiqimdan AI maslahatgacha
2. **5 turdagi hisobot** — kunlik, haftalik, oylik, yillik, maxsus
3. **Ko'p valyuta** — UZS, USD, EUR, RUB va boshqalar
4. **AI tahlil** — xarajat odatlarini o'rganib, shaxsiy maslahat beradi
5. **Maqsad va byudjet** — moliyaviy intizom uchun
6. **Qarz boshqaruvi** — kim kimga qancha qarzligini kuzatadi
7. **Eksport** — Excel va PDF formatida
8. **Guruh hisob** — oilaviy yoki biznes uchun
9. **Avtomatik hisobotlar** — belgilangan vaqtda yuboradi
10. **Xavfsiz** — ma'lumotlar shifrlangan va himoyalangan

> 💡 **Keyingi qadam:** Ushbu arxitektura asosida bot kodini yozishni boshlash uchun istalgan bo'limni tanlang va men sizga o'sha qism uchun to'liq kod yozib beraman!

---

*Hujjat oxiri | Finance Bot Architecture v2.0 | 2026*