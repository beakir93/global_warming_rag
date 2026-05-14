# Развёртывание в GitLab

Этот проект настроен для автоматического развёртывания в GitLab CI/CD.

## Быстрый старт

### 1. Локальный запуск

```bash
# Клонировать репозиторий
git clone <your-repo-url>
cd <project-directory>

# Создать виртуальное окружение
python3.12 -m venv .venv
source .venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Настроить переменные окружения
cp .env.example .env
# Отредактируйте .env и добавьте ваш GIGACHAT_CREDENTIALS

# Запустить приложение
streamlit run app.py
```

### 2. Запуск через Docker

```bash
# Создать .env файл с вашими credentials
cp .env.example .env
# Отредактируйте .env

# Сборка и запуск
docker-compose up --build
```

Приложение будет доступно на `http://localhost:8501`

### 3. Развёртывание в GitLab CI/CD

#### Требования

- GitLab версии 14.0+
- GitLab Runner с поддержкой Docker (рекомендуется)
- Переменные окружения в настройках проекта

#### Настройка переменных окружения

В GitLab UI перейдите в **Settings → CI/CD → Variables** и добавьте:

| Variable | Value | Protected | Masked |
|----------|-------|-----------|--------|
| `GIGACHAT_CREDENTIALS` | Ваш base64 ключ GigaChat | No | Yes |
| `GIGACHAT_SCOPE` | `GIGACHAT_API_B2B` | No | No |

#### Pipeline stages

1. **test** — базовые тесты импорта модулей
2. **deploy** — развёртывание Streamlit приложения
3. **docker_build** (manual) — сборка и push Docker образа

#### Автоматическое развёртывание

Pipeline автоматически запускается при:
- Пуше в ветку `main`
- Создании тега

Для ручного запуска Docker сборки выберите **Manual** в UI pipeline.

#### Доступ к приложению

После успешного деплоя приложение будет доступно по URL, указанному в секции `environment` файла `.gitlab-ci.yml`.

**Примечание:** Для production использования рекомендуется настроить:
- GitLab Pages или внешний reverse proxy (nginx)
- HTTPS сертификат
- Аутентификацию пользователей

## Структура файлов CI/CD

```
.gitlab-ci.yml      # Конфигурация pipeline
Dockerfile          # Docker образ для приложения
docker-compose.yml  # Локальное развёртывание
.env.example        # Шаблон переменных окружения
```

## Подготовка данных

Если в репозитории нет готовых данных (`data/index_meta.json`), раскомментируйте строку в `.gitlab-ci.yml`:

```yaml
python prepare_data.py
```

**Важно:** Для `prepare_data.py` требуется:
- Установленный `deno` (для yt-dlp)
- Куки браузера для доступа к YouTube
- Либо готовый файл `data/transcript.txt`

## Troubleshooting

### Ошибка аутентификации GigaChat

Проверьте что `GIGACHAT_CREDENTIALS` установлен корректно в GitLab CI/CD variables.

### Приложение не запускается

Проверьте логи pipeline:
```bash
# Локально
docker-compose logs rag-app

# В GitLab CI/CD
# См. output джобы deploy в UI
```

### Нет данных в индексе

Убедитесь что файлы `data/transcript.txt`, `data/captions.json` и `chroma_db/` присутствуют в репозитории или создаются в pipeline.

## Безопасность

- Файл `.env` добавлен в `.gitignore` — никогда не коммитьте реальные credentials
- Используйте GitLab CI/CD Variables для чувствительных данных
- Включите опцию **Masked** для секретов
- Рассмотрите возможность использования **Protected Variables** для production
