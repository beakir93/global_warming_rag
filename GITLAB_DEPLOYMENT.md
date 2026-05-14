# Развёртывание RAG-приложения в GitLab

Это полное руководство по развёртыванию мультимодальной RAG-системы для ответов на вопросы о глобальном потеплении в инфраструктуре GitLab с использованием CI/CD и Docker.

## 📋 Предварительные требования

1. **GitLab аккаунт** с правами на запись в репозиторий (роль Maintainer или выше)
2. **Доступ к GigaChat API**:
   - `GIGACHAT_CREDENTIALS` (логин:пароль или токен аутентификации)
   - `GIGACHAT_SCOPE` (обычно `GIGACHAT_API_B2B`)
3. **Docker** (для локального тестирования)
4. **Git** установлен локально
5. **Python 3.10+** (рекомендуется 3.12)

---

## 🚀 Пошаговая инструкция

### Шаг 1: Настройка переменных окружения в GitLab

1. Откройте ваш проект в GitLab
2. Перейдите в **Settings** → **CI/CD**
3. Раскройте секцию **Variables** и нажмите **Add variable**

Добавьте следующие переменные:

| Ключ | Значение | Тип | Защищённая | Маскированная | Описание |
|------|----------|-----|------------|---------------|----------|
| `GIGACHAT_CREDENTIALS` | ваши_учетные_данные | Variable | ❌ | ✅ | Учётные данные GigaChat (формат: `client_id:client_secret` или токен) |
| `GIGACHAT_SCOPE` | `GIGACHAT_API_B2B` | Variable | ❌ | ❌ | Область доступа API |
| `STREAMLIT_SERVER_PORT` | `8501` | Variable | ❌ | ❌ | Порт Streamlit сервера |
| `DOCKER_REGISTRY_URL` | `registry.gitlab.com/your-group/your-project` | Variable | ❌ | ❌ | URL вашего Container Registry |

> ⚠️ **Важно**: 
> - Переменная `GIGACHAT_CREDENTIALS` должна быть помечена как **Masked**, чтобы не отображать чувствительные данные в логах
> - Убедитесь, что значение не содержит пробелов и специальных символов, которые могут нарушить формат

---

### Шаг 2: Проверка конфигурационных файлов

Убедитесь, что в репозитории присутствуют следующие файлы:

```
project/
├── .gitlab-ci.yml          # Конфигурация CI/CD pipeline
├── Dockerfile              # Инструкция для сборки Docker образа
├── docker-compose.yml      # Конфигурация для локального запуска
├── .env.example            # Шаблон переменных окружения
├── requirements.txt        # Python зависимости
├── app.py                  # Основное приложение Streamlit
└── data/                   # Директория с данными
    ├── chroma_db/          # Векторная база данных
    └── transcripts/        # Транскрипции видео
```

**Критически важные файлы:**
- `.gitlab-ci.yml` — определяет этапы pipeline
- `Dockerfile` — описывает процесс сборки образа
- `data/chroma_db/` — должна существовать и содержать индексированные данные

---

### Шаг 3: Локальное тестирование (рекомендуется)

Перед отправкой в GitLab протестируйте развёртывание локально:

#### 3.1. Подготовка окружения

```bash
# Клонировать репозиторий (если ещё не склонирован)
git clone <your-repo-url>
cd <project-directory>

# Создать виртуальное окружение
python3.12 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate  # Windows

# Установить зависимости
pip install -r requirements.txt
```

#### 3.2. Настройка переменных окружения

```bash
# Создать файл .env на основе шаблона
cp .env.example .env

# Отредактировать файл и добавить credentials
nano .env  # или используйте любой редактор
```

Пример содержимого `.env`:
```bash
GIGACHAT_CREDENTIALS=ваш_client_id:ваш_client_secret
GIGACHAT_SCOPE=GIGACHAT_API_B2B
STREAMLIT_SERVER_PORT=8501
```

#### 3.3. Запуск через Docker (рекомендуется)

```bash
# Сборка образа
docker-compose build

# Запуск контейнера
docker-compose up -d

# Проверка логов
docker-compose logs -f rag-app
```

Приложение будет доступно по адресу: **http://localhost:8501**

#### 3.4. Прямой запуск Streamlit

```bash
# Запуск приложения
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
```

---

### Шаг 4: Отправка кода в GitLab

#### 4.1. Коммит и пуш изменений

```bash
# Добавить все изменения
git add .

# Создать коммит
git commit -m "feat: настроить GitLab CI/CD для развёртывания RAG-приложения"

# Пуш в удалённый репозиторий
git push origin main
```

> 💡 **Совет**: Если вы работаете в feature-ветке, создайте Merge Request и замержите его в `main`. Pipeline запустится автоматически после мерджа.

#### 4.2. Проверка запуска pipeline

1. Перейдите в GitLab → **Build** → **Pipelines** (или **CI/CD** → **Pipelines**)
2. Вы увидите новый pipeline со статусом **Running**
3. Дождитесь завершения всех этапов

---

### Шаг 5: Мониторинг pipeline

#### Этапы pipeline:

1. **test** (автоматически)
   - Проверяет корректность импорта модулей
   - Время выполнения: ~1-2 минуты
   - При ошибке: проверьте логи джобы

2. **deploy** (автоматически при пуше в `main`)
   - Разворачивает приложение Streamlit
   - Время выполнения: ~3-5 минут
   - Создаёт environment "production"

3. **docker_build** (вручную)
   - Собирает Docker образ
   - Push в GitLab Container Registry
   - Требует ручного подтверждения в UI

#### Просмотр логов:

1. Кликните на номер pipeline в списке
2. Выберите нужную джобу (например, `deploy`)
3. Просматривайте вывод в реальном времени

---

### Шаг 6: Доступ к развёрнутому приложению

После успешного завершения стадии `deploy`:

1. Перейдите в **Deploy** → **Environments**
2. Кликните на среду **production**
3. Нажмите на ссылку **External URL** (если настроена) или скопируйте URL из вывода джобы

> 📝 **Примечание**: 
> - По умолчанию GitLab CI/CD не предоставляет публичный URL для приложений
> - Для доступа извне настройте один из вариантов:
>   - **GitLab Pages** (статический контент)
>   - **Внешний сервер** с reverse proxy (nginx)
>   - **Сервисы типа Render/Railway** (деплой из Docker Registry)

---

## 🐳 Работа с Docker Registry

### Сборка и push образа вручную

Если вы хотите собрать Docker образ и сохранить его в GitLab Registry:

1. Перейдите в **CI/CD** → **Pipelines**
2. Найдите последний успешный pipeline
3. Найдите джобу `docker_build` со статусом **manual**
4. Нажмите кнопку ▶️ (Play) для запуска

### Pull образа на внешний сервер

```bash
# Логин в GitLab Registry
docker login registry.gitlab.com -u <your-username> -p <your-access-token>

# Pull образа
docker pull registry.gitlab.com/<your-group>/<your-project>:latest

# Запуск на сервере
docker run -d \
  -p 8501:8501 \
  -e GIGACHAT_CREDENTIALS="ваши_данные" \
  -e GIGACHAT_SCOPE="GIGACHAT_API_B2B" \
  --name rag-app \
  --restart unless-stopped \
  registry.gitlab.com/<your-group>/<your-project>:latest
```

### Получение access token

1. Перейдите в **User Settings** → **Access Tokens**
2. Создайте токен с правами:
   - `read_registry`
   - `write_registry`
3. Скопируйте токен (он показывается только один раз)

---

## 🔧 Troubleshooting

### ❌ Ошибка: "Pipeline failed at test stage"

**Возможные причины:**
- Проблемы с импортом модулей
- Отсутствуют зависимости в `requirements.txt`
- Синтаксические ошибки в коде

**Решение:**
```bash
# Локальная проверка
docker-compose build
docker-compose up
# Проверьте логи на ошибки импорта
docker-compose logs rag-app
```

---

### ❌ Ошибка: "GigaChat authentication failed"

**Возможные причины:**
- Некорректное значение `GIGACHAT_CREDENTIALS`
- Неверный формат учётных данных
- Истёк срок действия токена

**Решение:**
1. Проверьте значение переменной в GitLab (**Settings** → **CI/CD** → **Variables**)
2. Убедитесь в правильности формата (обычно `client_id:client_secret`)
3. При необходимости получите новые credentials в кабинете GigaChat
4. Перезапустите pipeline

---

### ❌ Ошибка: "Streamlit server not reachable"

**Возможные причины:**
- Порт не проброшен в Docker
- Firewall блокирует соединение
- Приложение не успело запуститься до healthcheck

**Решение:**
1. Проверьте `Dockerfile`: должна быть директива `EXPOSE 8501`
2. Проверьте `docker-compose.yml`: порт должен быть замаппен (`8501:8501`)
3. Увеличьте таймаут в healthcheck (если используется)
4. Проверьте логи приложения на наличие ошибок запуска

---

### ❌ Ошибка: "Docker push failed" или "unauthorized: authentication required"

**Возможные причины:**
- Недостаточно прав для записи в Registry
- Не выполнен `docker login`
- Истёк срок действия токена

**Решение:**
1. Убедитесь, что у вашего пользователя есть роль **Maintainer** или **Owner** в проекте
2. Проверьте, что в настройках проекта включён **Container Registry**
3. Создайте новый Access Token с правами `write_registry`
4. В CI/CD настройках убедитесь, что используется правильный `CI_JOB_TOKEN`

---

### ❌ Ошибка: "No such file or directory: data/index_meta.json"

**Возможные причины:**
- Файлы данных отсутствуют в репозитории
- Индекс не был создан заранее

**Решение:**
1. Убедитесь, что директория `data/` и её содержимое закоммичены в репозиторий
2. Если данные генерируются скриптом, раскомментируйте вызов в `.gitlab-ci.yml`:
   ```yaml
   - python prepare_data.py
   ```
3. Для `prepare_data.py` может потребоваться:
   - Установленный `deno` (для yt-dlp)
   - Куки браузера для доступа к YouTube
   - Либо готовый файл `data/transcript.txt`

---

## 🔄 Обновление приложения

Для обновления развёрнутой версии:

1. Внесите необходимые изменения в код
2. Закоммитьте и запушьте в ветку `main`:
   ```bash
   git add .
   git commit -m "fix: описание внесённых изменений"
   git push origin main
   ```
3. Pipeline запустится автоматически
4. После успешного прохождения всех этапов новая версия будет развёрнута

**Время обновления:** обычно 5-10 минут в зависимости от размера изменений и скорости Runner.

---

## 🛡️ Безопасность

### Рекомендации по защите данных:

1. **Никогда не коммитьте** файлы с реальными credentials:
   - `.env`
   - `config.py` с паролями
   - `secrets.toml`
   
2. **Проверьте `.gitignore`**:
   ```
   .env
   *.pyc
   __pycache__/
   .chroma_db/
   .streamlit/secrets.toml
   *.log
   ```

3. **Используйте GitLab Variables**:
   - Все секреты храните в **Settings** → **CI/CD** → **Variables**
   - Включайте опцию **Masked** для скрытия значений в логах
   - Используйте **Protected** для production-переменных

4. **Ограничьте доступ**:
   - Настройте **Protected Branches** для ветки `main`
   - Используйте **Protected Tags** для релизов
   - Ограничьте круг лиц с доступом к pipeline

5. **Регулярно обновляйте зависимости**:
   ```bash
   pip list --outdated
   pip install --upgrade <package>
   ```

---

## 📊 Мониторинг и логирование

### Просмотр логов в GitLab UI:

1. **CI/CD** → **Pipelines** → выберите pipeline
2. Кликните на джобу (например, `deploy`)
3. Прокручивайте вывод для просмотра логов в реальном времени

### Health Check:

Docker-образ включает проверку здоровья:

```bash
# Локальная проверка
curl http://localhost:8501/_stcore/health

# Ожидаемый ответ: ok
```

### Логи приложения:

```bash
# При использовании docker-compose
docker-compose logs -f rag-app

# При прямом запуске Docker
docker logs -f rag-app
```

---

## 📈 Производительность и масштабирование

### Оптимизация:

1. **Кэширование зависимостей** в `.gitlab-ci.yml`:
   ```yaml
   cache:
     paths:
       - .venv/
       - ~/.cache/pip
   ```

2. **Parallel jobs** для ускорения тестирования

3. **Auto-scaling Runners** для обработки нескольких pipeline одновременно

### Масштабирование:

Для production нагрузки рассмотрите:
- Разделение frontend и backend
- Использование отдельного сервера для ChromaDB
- Кэширование ответов LLM
- Rate limiting для API запросов

---

## 🆘 Дополнительная поддержка

### Полезные ссылки:

- [Документация GitLab CI/CD](https://docs.gitlab.com/ee/ci/)
- [GitLab Container Registry](https://docs.gitlab.com/ee/user/packages/container_registry/)
- [Streamlit Deployment](https://docs.streamlit.io/deploy)
- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

### Сообщество:

- GitLab Forum: https://forum.gitlab.com/
- Stack Overflow: тег `gitlab-ci`
- Telegram-чаты по DevOps

---

**Версия документа**: 2.0  
**Дата обновления**: 2026-01-24  
**Поддерживаемые версии**: Python 3.10+, Streamlit 1.28+, Docker 20.10+, GitLab 14.0+
