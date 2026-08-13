#!/usr/bin/env bash

# ==============================================================================
#  LANi-Platform - Стартиращ скрипт за Linux
# ==============================================================================
#  Версия: 01.03.00
#  Описание: Автоматизирано инсталиране, конфигуриране и стартиране на LANi.
# ==============================================================================

set -e

# Цветове за красив конзолен изход
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Функция за показване на логото
show_logo() {
    echo -e "${CYAN}"
    echo "    __    ___    _   _______       ____  __      __  ______                      "
    echo "   / /   /   |  / | / / ___/      / __ \/ /___ _/ /_/ __/ /___  ________ ___     "
    echo "  / /   / /| | /  |/ /\__ \______/ /_/ / / __ \`/ __/ /_/ / __ \/ ___/ __ \`__ \   "
    echo " / /___/ ___ |/ /|  /___/ /_____/ ____/ / /_/ / /_/ __/ / /_/ / /  / / / / / /   "
    echo "/_____/_/  |_/_/ |_//____/     /_/   /_/\__,_/\__/_/ /_/\____/_/  /_/ /_/ /_/    "
    echo -e "${NC}"
    echo -e "${BLUE}==============================================================================${NC}"
    echo -e "       ${GREEN}LANi-Platform — Професионален Контрол на Мрежови Конфигурации${NC}"
    echo -e "${BLUE}==============================================================================${NC}\n"
}

# Функция за проверка на зависимостите
check_dependency() {
    if ! command -v "$1" &> /dev/null; then
        echo -e "${YELLOW}[ПРЕДУПРЕЖДЕНИЕ] Скриптът '$1' не е намерен.${NC}"
        return 1
    fi
    return 0
}

# Функция за стартиране чрез Docker Compose (Препоръчително)
start_docker() {
    echo -e "\n${BLUE}[1/3] Стартиране на LANi-Platform чрез Docker Compose...${NC}"

    if ! check_dependency "docker" || ! check_dependency "docker-compose"; then
        echo -e "${RED}[ГРЕШКА] Docker или Docker Compose не са инсталирани на тази система!${NC}"
        echo -e "${YELLOW}Моля, инсталирайте ги или изберете локално стартиране (опция 2).${NC}"
        exit 1
    fi

    echo -e "${GREEN}[OK] Всички Docker зависимости са налице.${NC}"
    echo -e "${CYAN}Изграждане и стартиране на контейнерите на заден план...${NC}"

    docker-compose up -d --build

    echo -e "\n${GREEN}[УСПЕХ] LANi-Platform се стартира успешно в Docker контейнери!${NC}"
    echo -e "${BLUE}------------------------------------------------------------${NC}"
    echo -e "🔗 Уеб интерфейс (Frontend): ${CYAN}http://localhost:3000${NC}"
    echo -e "🔗 Документация на API (Swagger): ${CYAN}http://localhost:8000/docs${NC}"
    echo -e "🔐 Потребител по подразбиране: ${YELLOW}admin${NC} / Парола: ${YELLOW}admin${NC}"
    echo -e "${BLUE}------------------------------------------------------------${NC}"
    echo -e "За спиране на платформата изпълнете: ${CYAN}docker-compose down${NC}\n"
}

# Функция за стартиране локално с виртуална среда
start_local() {
    echo -e "\n${BLUE}[2/3] Конфигуриране и стартиране на LANi-Platform локално...${NC}"

    check_dependency "python3" || { echo -e "${RED}[ГРЕШКА] Python 3 е задължителен за локално стартиране.${NC}"; exit 1; }
    check_dependency "node" || { echo -e "${RED}[ГРЕШКА] Node.js е задължителен за локално стартиране.${NC}"; exit 1; }
    check_dependency "npm" || { echo -e "${RED}[ГРЕШКА] NPM е задължителен за локално стартиране.${NC}"; exit 1; }

    # 1. Настройка на Бекенд виртуална среда
    echo -e "\n${CYAN}• Настройка на Python виртуална среда (.venv)...${NC}"
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        echo -e "${GREEN}[OK] Създадена е нова виртуална среда .venv${NC}"
    fi

    source .venv/bin/activate
    echo -e "${CYAN}• Инсталиране на Python зависимости...${NC}"
    pip install -r requirements.txt

    # Инициализация на базата данни (SQLite за локални тестове)
    echo -e "${CYAN}• Инициализиране на локалната SQLite база данни...${NC}"
    DATABASE_URL=sqlite:///./test.db python3 scripts/init_db.py

    # 2. Инсталиране на фронтенд зависимости
    echo -e "\n${CYAN}• Инсталиране на фронтенд зависимости (Node.js)...${NC}"
    cd frontend
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    cd ..

    # 3. Стартиране на процесите на заден план
    echo -e "\n${GREEN}[УСПЕХ] Всички зависимости са инсталирани!${NC}"
    echo -e "${YELLOW}Стартиране на бекенда и фронтенда... (Натиснете Ctrl+C за спиране)${NC}"

    # Спиране на вече заето порт блиндиране
    kill $(lsof -t -i :8000) 2>/dev/null || true
    kill $(lsof -t -i :5173) 2>/dev/null || true

    # Стартиране на Бекенда
    source .venv/bin/activate
    TESTING=1 uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
    BACKEND_PID=$!

    # Стартиране на Фронтенда
    cd frontend
    npm run dev -- --host 0.0.0.0 --port 5173 > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..

    echo -e "${BLUE}------------------------------------------------------------${NC}"
    echo -e "🔗 Локален Уеб интерфейс: ${CYAN}http://localhost:5173${NC}"
    echo -e "🔗 Локален API Swagger: ${CYAN}http://localhost:8000/docs${NC}"
    echo -e "📝 Логове: ${YELLOW}backend.log${NC} и ${YELLOW}frontend.log${NC}"
    echo -e "${BLUE}------------------------------------------------------------${NC}"

    # Функция за чисто спиране на процесите
    cleanup() {
        echo -e "\n${YELLOW}Спиране на активните LANi-Platform процеси...${NC}"
        kill $BACKEND_PID 2>/dev/null || true
        kill $FRONTEND_PID 2>/dev/null || true
        echo -e "${GREEN}Всички процеси са спрени успешно.${NC}"
        exit 0
    }

    trap cleanup SIGINT SIGTERM

    # Изчакване за прекъсване от потребителя
    while true; do
        sleep 1
    done
}

# Функция за стартиране на тестовете
run_tests() {
    echo -e "\n${BLUE}[3/3] Стартиране на системните тестове на LANi-Platform...${NC}"
    if [ ! -d ".venv" ]; then
        echo -e "${YELLOW}Няма открита виртуална среда. Създаване на .venv и инсталиране на зависимости...${NC}"
        python3 -m venv .venv
        source .venv/bin/activate
        pip install -r requirements.txt pytest pytest-asyncio pytest-cov
    else
        source .venv/bin/activate
    fi

    echo -e "${CYAN}Стартиране на pytest...${NC}"
    TESTING=1 pytest -v
}

# Главен поток на изпълнение
show_logo

echo -e "Изберете опция за действие:"
echo -e " ${GREEN}1)${NC} Стартиране чрез ${CYAN}Docker Compose${NC} (Препоръчително за Продукция)"
echo -e " ${GREEN}2)${NC} Стартиране ${CYAN}Локално${NC} (За Разработка / Тестове)"
echo -e " ${GREEN}3)${NC} Стартиране на ${CYAN}Автоматизирани Тестове${NC}"
echo -e " ${GREEN}4)${NC} Изход"
echo -ne "\nВъведете опция [1-4]: "
read -r choice

case $choice in
    1)
        start_docker
        ;;
    2)
        start_local
        ;;
    3)
        run_tests
        ;;
    4)
        echo -e "\n${GREEN}Благодарим ви, че използвате LANi-Platform! Довиждане.${NC}\n"
        exit 0
        ;;
    *)
        echo -e "\n${RED}[ГРЕШКА] Невалидна опция! Изход от скрипта.${NC}\n"
        exit 1
        ;;
esac
