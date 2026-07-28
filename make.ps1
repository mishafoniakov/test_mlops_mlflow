param(
    [Parameter(Position = 0)]
    [string]$Command = "help",

    [Alias("Message")]
    [string]$msg = "update",

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Remaining = @()
)

$ErrorActionPreference = "Stop"
$Compose = "docker compose"

foreach ($arg in $Remaining) {
    if ($arg -match '^(?i)msg=(.+)$') {
        $msg = $Matches[1].Trim().Trim('"').Trim("'")
    }
}

function Show-Help {
    Write-Host ""
    Write-Host "Available commands:"
    Write-Host ""
    Write-Host "  Docker / stack"
    Write-Host "    .\make restart            Stop, rebuild and start all services"
    Write-Host "    .\make down               Stop and remove containers"
    Write-Host "    .\make ps                 Container status"
    Write-Host "    .\make logs               Follow all logs"
    Write-Host "    .\make status             Status + URLs"
    Write-Host "    .\make urls               Service URLs"
    Write-Host ""
    Write-Host "  Container"
    Write-Host "    .\make dags               List DAGs"
    Write-Host ""
    Write-Host "  Git"
    Write-Host "    .\make push msg=`"message`"  Add, commit and push"
    Write-Host ""
}

function Show-Urls {
    $airflowPort = "8080"
    $mlflowPort = "5001"
    $minioApi = "9002"
    $minioConsole = "9001"
    if (Test-Path ".env") {
        Get-Content ".env" | ForEach-Object {
            if ($_ -match "^\s*AIRFLOW_WEBSERVER_HOST_PORT=(.+)$") { $airflowPort = $Matches[1].Trim() }
            if ($_ -match "^\s*MLFLOW_HOST_PORT=(.+)$") { $mlflowPort = $Matches[1].Trim() }
            if ($_ -match "^\s*MINIO_API_HOST_PORT=(.+)$") { $minioApi = $Matches[1].Trim() }
            if ($_ -match "^\s*MINIO_CONSOLE_HOST_PORT=(.+)$") { $minioConsole = $Matches[1].Trim() }
        }
    }
    Write-Host ""
    Write-Host "  Airflow UI:     http://localhost:$airflowPort"
    Write-Host "  MLflow UI:      http://localhost:$mlflowPort"
    Write-Host "  MinIO API:      http://localhost:$minioApi"
    Write-Host "  MinIO Console:  http://localhost:$minioConsole"
    Write-Host "  Credentials:    see .env"
    Write-Host ""
}

function Invoke-GitPush {
    param([string]$Message)

    $env:GIT_AUTHOR_NAME = "Михаил Фоняков"
    $env:GIT_AUTHOR_EMAIL = "fmd@it-expertise.ru"
    $env:GIT_COMMITTER_NAME = "Михаил Фоняков"
    $env:GIT_COMMITTER_EMAIL = "fmd@it-expertise.ru"

    git add .
    $staged = git diff --cached --name-only
    if (-not $staged) {
        Write-Host "Nothing to commit." -ForegroundColor Yellow
        git push -u origin HEAD
        if ($LASTEXITCODE -ne 0) {
            throw "git push failed (exit $LASTEXITCODE)"
        }
        git status -sb
        return
    }

    git commit -m $Message
    if ($LASTEXITCODE -ne 0) {
        throw "git commit failed (exit $LASTEXITCODE)"
    }

    git push -u origin HEAD
    if ($LASTEXITCODE -ne 0) {
        throw "git push failed (exit $LASTEXITCODE)"
    }

    git status -sb
    git log -1 --oneline
}

switch ($Command.ToLower()) {
    "help" { Show-Help }
    "restart" {
        Invoke-Expression "$Compose down"
        Invoke-Expression "$Compose up -d --build"
    }
    "down" { Invoke-Expression "$Compose down" }
    "ps" { Invoke-Expression "$Compose ps" }
    "logs" { Invoke-Expression "$Compose logs -f" }
    "status" {
        Invoke-Expression "$Compose ps"
        Show-Urls
    }
    "urls" { Show-Urls }
    "dags" { Invoke-Expression "$Compose exec airflow-webserver airflow dags list" }
    "push" { Invoke-GitPush -Message $msg }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Show-Help
        exit 1
    }
}
