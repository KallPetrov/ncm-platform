#!/bin/bash
# NCM Platform - Автоматизиран Бекъп на Базата Данни (SQLite / PostgreSQL)
# Този скрипт поддържа както локални инсталации, така и Docker-базирани контейнери.

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="./storage/backups"
mkdir -p "$BACKUP_DIR"

echo "=== [NCM Backup Process Started: $(date)] ==="

# 1. Архивиране на SQLite база данни (ако се използва локално)
if [ -f "test.db" ]; then
    echo "[SQLite] Архивиране на локална SQLite база данни..."
    sqlite3 test.db ".backup '$BACKUP_DIR/sqlite_backup_$TIMESTAMP.db'"
    echo "[SQLite] Успешен архив: $BACKUP_DIR/sqlite_backup_$TIMESTAMP.db"
fi

# 2. Архивиране на PostgreSQL база данни (ако е активен в docker-compose)
if command -v docker-compose &> /dev/null; then
    if docker-compose ps | grep -q "db"; then
        echo "[PostgreSQL] Открит е работещ PostgreSQL контейнер. Извличане на архив..."
        docker-compose exec -T db pg_dump -U ncm_user ncm_db > "$BACKUP_DIR/postgres_backup_$TIMESTAMP.sql"
        echo "[PostgreSQL] Успешен архив: $BACKUP_DIR/postgres_backup_$TIMESTAMP.sql"
    fi
fi

# 3. Почистване на стари резервни копия (по-стари от 30 дни)
echo "Почистване на стари резервни копия..."
find "$BACKUP_DIR" -type f -mtime +30 \( -name "*.db" -o -name "*.sql" \) -exec rm -f {} \;
echo "Всички архиви, по-стари от 30 дни, бяха премахнати."

echo "=== [NCM Backup Process Completed Successfully] ==="
