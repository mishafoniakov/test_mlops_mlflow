# my_mlflow

Docker-стек для оркестрации ML-пайплайнов: **Apache Airflow** управляет обучением моделей, **MLflow** хранит эксперименты и артефакты, **MinIO** выступает S3-хранилищем, **PostgreSQL** — базой метаданных, **Redis** — промежуточным буфером между задачами.

Демонстрационный DAG `mlflow_iris_demo` обучает `LogisticRegression` на датасете Iris и логирует метрики и модель в MLflow.

## Архитектура

```mermaid
flowchart LR
    subgraph Airflow
        DAG[mlflow_iris_demo]
    end

    subgraph Storage
        PG[(PostgreSQL)]
        Redis[(Redis)]
        MinIO[(MinIO S3)]
    end

    MLflow[MLflow Server]

    DAG -->|preprocess| Redis
    DAG -->|train| MLflow
    MLflow --> PG
    MLflow --> MinIO
    Airflow --> PG
```

| Сервис | Назначение | UI (по умолчанию) |
|---|---|---|
| Airflow | Оркестрация DAG-ов | http://localhost:8080 |
| MLflow | Трекинг экспериментов | http://localhost:5001 |
| MinIO | Хранение артефактов (S3) | http://localhost:9002 (API), http://localhost:9001 (Console) |
| PostgreSQL | Метаданные Airflow и MLflow | localhost:5435 |
| Redis | Передача данных между задачами | localhost:6379 |

## Структура проекта

```
my_mlflow/
├── dags/
│   └── mlflow_iris_demo.py   # DAG: preprocess → train
├── docker-compose.yml        # Описание стека
├── Dockerfile                # Образ Airflow с mlflow, scikit-learn
├── .env.example              # Шаблон переменных окружения
├── Makefile                  # Команды restart / push
├── .gitlab-ci.yml            # CI/CD pipeline
└── README.md
```

## Быстрый старт

### Требования

- Docker и Docker Compose v2
- `make` (Git Bash, WSL или `choco install make`)

### Запуск

```bash
cp .env.example .env
# Отредактируйте .env — подставьте реальные значения вместо фейковых из шаблона

docker compose up -d --build
# или
make restart
```

После старта:

- **Airflow UI** — http://localhost:8080 (логин/пароль из `.env`)
- **MLflow UI** — http://localhost:5001
- **MinIO Console** — http://localhost:9001

Включите DAG `mlflow_iris_demo` в Airflow и запустите вручную (schedule отключён).

### Остановка

```bash
docker compose down
```

## Переменные окружения

Секреты и хост-порты вынесены в `.env`. Шаблон — `.env.example`.

| Группа | Переменные |
|---|---|
| PostgreSQL | `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST_PORT` |
| MinIO | `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`, `MINIO_API_HOST_PORT`, `MINIO_CONSOLE_HOST_PORT` |
| Redis | `REDIS_HOST_PORT` |
| MLflow | `MLFLOW_HOST_PORT` |
| Airflow | `AIRFLOW_WEBSERVER_HOST_PORT`, `AIRFLOW_ADMIN_USERNAME`, `AIRFLOW_ADMIN_PASSWORD`, `AIRFLOW_ADMIN_EMAIL` |

Файл `.env` не коммитится в git.

## Makefile

| Команда | Описание |
|---|---|
| `make restart` | Пересобрать и перезапустить весь стек |
| `make push MSG="текст"` | `git add` → `commit` → `push` в текущую ветку |

## CI/CD

Pipeline в `.gitlab-ci.yml` запускается при merge request и push в `master` / `main`.

| Stage | Job | Действие |
|---|---|---|
| validate | `validate:compose` | Проверка `docker-compose.yml` |
| validate | `validate:dags` | Проверка синтаксиса DAG-файлов |
| build | `build` | Сборка Docker-образов |
| deploy | `deploy` | SSH-деплой на сервер (`git pull` + `make restart`), ручной запуск |

Переменные GitLab CI/CD (`Settings → CI/CD → Variables`):

- `SSH_PRIVATE_KEY`
- `DEPLOY_HOST`
- `DEPLOY_USER`
- `DEPLOY_PATH`

## Демо-пайплайн

DAG `mlflow_iris_demo` состоит из двух задач:

1. **preprocess** — загружает Iris, делит на train/test, сохраняет в Redis
2. **train** — читает данные из Redis, обучает `LogisticRegression`, логирует accuracy и модель в MLflow

Результаты эксперимента доступны в MLflow UI (эксперимент `iris_demo`).

## Стек технологий

- Apache Airflow 2.8.1
- MLflow 2.14.1
- scikit-learn 1.3.2
- PostgreSQL 17
- MinIO (S3-compatible)
- Redis 7
- GitLab CI/CD
