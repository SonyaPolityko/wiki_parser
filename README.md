# Wiki-Parser
_Проект создан в рамках тестового задания._

## Установка и запуск

### Предварительные требования
- Python 3.12+
- [uv](https://github.com/astral-sh/uv#installation)

### 1. Установка uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Клонирование и установка зависимостей
``` bash
git clone https://github.com/SonyaPolityko/wiki_parser.git
cd wiki_parser
uv sync
```
### 3. Настройка окружения
Создайте файл .env в корне проекта и заполните своими данными:
```env
EMAIL_SENDER=your_email@yandex.ru
EMAIL_PASSWORD=your_app_password  # Пароль приложения, не основной!
EMAIL_RECIPIENT=recipient@example.com
```

### 4. Настройка страницы мониторинга
По умолчанию стоит в project/config.py:
``` python
PAGE_PATH = "wiki/Deaths_in_2025"
```
Если вы не хотите инициализировать хранилище текущими ссылками без отправки уведомлений, то поставьте:

``` python
INIT_REPO = False
```

### 5. Запуск демона
```bash
# Запуск
uv run run_daemon.py start

# Остановка
uv run run_daemon.py stop

# Проверка запущенных процессов
ps aux | grep daemon.py

# Проверка логов
tail -f .log/log.json

# Проверка PID-файла
cat /tmp/daemon-example.pid

# Принудительная остановка (если завис) и удаление файла
kill $(cat /tmp/daemon-example.pid)
rm /tmp/daemon-example.pid
```
## Первый запуск
1. Демон при запуске инициализирует локальную базу, сканируя текущий список
2. Все существующие записи сохраняются в ~/.wiki_info/december.json
3. Дальнейшие проверки будут выявлять только новые записи и те, на которые появились ссылки


# Мини-эссе находится в файлу ESSAY.md


