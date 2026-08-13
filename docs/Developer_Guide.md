# Ръководство за Разработчици - LANi-Platform

Този документ е предназначен за софтуерни инженери, които искат да разширяват, тестват и допринасят за разработката на LANi-Platform.

## 1. Архитектура на Системата
Платформата е изградена по модерна трислойна архитектура:
* **База Данни:** SQLAlchemy ORM (поддържа SQLite за локално развитие и PostgreSQL/Docker за производство).
* **Бекенд (Backend):** FastAPI (Python 3.12+), Celery за асинхронни задачи, Redis за брокер на задачи.
* **Фронтенд (Frontend):** React (TypeScript), Vite, TailwindCSS, shadcn/ui.

---

## 2. Структура на Проекта
```text
/
├── app/                  # FastAPI Бекенд приложение
│   ├── api/              # API рутери и ендпоинти
│   ├── core/             # Конфигурации, база данни, сигурност
│   ├── models/           # SQLAlchemy DB модели
│   ├── schemas/          # Pydantic валидационни схеми
│   └── services/         # Бизнес логика (AI, SSH, Git, Secrets Vault, Topology)
├── frontend/             # React Фронтенд приложение
│   ├── src/
│   │   ├── components/   # UI компоненти (вкл. AIAssistantPanel)
│   │   └── lib/          # API клиент и помощни функции
├── tests/                # Комплексни автоматизирани тестове
```

---

## 3. Локално Стартиране за Разработка

### 3.1 Инициализиране на Бекенда
1. Създайте и активирайте Python виртуална среда:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Копирайте примера за променливи на средата:
   ```bash
   cp .env.example .env
   ```
3. Инициализирайте локалната SQLite база данни:
   ```bash
   DATABASE_URL=sqlite:///./test.db python3 scripts/init_db.py
   ```
4. Стартирайте FastAPI сървъра:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### 3.2 Стартиране на Фронтенда
1. Отидете в папка `frontend/`:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
2. Приложението ще бъде достъпно на `http://localhost:5173`.

---

## 4. Писане и Изпълнение на Тестове
Всички нови услуги и промени задължително трябва да съдържат unit/integration тестове в директория `tests/`.
* За да изпълните пълния пакет от тестове локално с реална изолация:
  ```bash
  TESTING=1 pytest
  ```
* За тестване на конкретен модул (напр. новия AI асистент):
  ```bash
  TESTING=1 pytest tests/test_ai_assistant.py -v
  ```
