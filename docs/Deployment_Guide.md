# Ръководство за Внедряване - NCM Платформа

Този документ предоставя пълни инструкции за внедряване (deployment) на NCM Платформата в производствена среда с фокус върху висока наличност, сигурност и резервно копиране.

## 1. Контейнеризация с Docker Compose
За производствено внедряване силно се препоръчва използването на представения в корена `docker-compose.yml`, който оркестрира:
1. **База данни:** PostgreSQL 15 за съхранение на транзакционни данни.
2. **Брокер:** Redis за разпределение на асинхронни задачи (Celery).
3. **Бекенд:** FastAPI контейнер за обработка на REST заявки.
4. **Celery Worker:** Контейнер за изпълнение на дълготрайни мрежови бекъпи и автоматизация.
5. **Фронтенд:** Компилирани React активи, обслужвани от високопроизводителен Nginx.

### Стартиране в продукция:
```bash
docker-compose up -d --build
```

---

## 2. Подсилване на Сигурността (Security Hardening)
При пускане на платформата в реална мрежа задължително спазвайте следните правила за подсилване:
1. **SECRET_KEY:** Сменете стойността на `SECRET_KEY` в `.env` файла с уникален криптографски сигурен хеш:
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```
2. **Пароли на БД:** Никога не използвайте пароли по подразбиране за PostgreSQL (`POSTGRES_PASSWORD`).
3. **HTTPS / TLS:** Конфигурирайте Nginx (`frontend/nginx.conf`) да използва SSL/TLS сертификати (напр. Let's Encrypt), за да се предотврати прехващане на пароли по мрежата.
4. **Secrets Vault Key:** Сменете криптографския ключ за Secrets Vault, за да подсигурите шифрирането на паролите на устройствата.

---

## 3. Процедура за Резервни Копия на Базата Данни (Database Backup)
Регулярното архивиране на PostgreSQL базата данни е критично. По-долу е представен скрипт, предназначен да се изпълнява ежедневно чрез `cron`:

### Автоматизиран Бекъп Скрипт (`backup_db.sh`):
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/ncm"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATABASE_NAME="ncm_db"
DB_USER="ncm_user"

mkdir -p $BACKUP_DIR

# Изпълнение на pg_dump за бекъп на PostgreSQL контейнера
docker-compose exec -T db pg_dump -U $DB_USER $DATABASE_NAME > "$BACKUP_DIR/ncm_backup_$TIMESTAMP.sql"

# Изтриване на архиви по-стари от 30 дни
find $BACKUP_DIR -type f -mtime +30 -name "*.sql" -delete

echo "Успешно архивиране на базата данни в $BACKUP_DIR/ncm_backup_$TIMESTAMP.sql"
```

Настройте изпълнението му в cron:
```bash
0 2 * * * /bin/bash /path/to/backup_db.sh
```
За да възстановите архив:
```bash
cat backup.sql | docker-compose exec -T db psql -U ncm_user -d ncm_db
```
