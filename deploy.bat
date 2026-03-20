@echo off
REM ═══════════════════════════════════════════════════════════════════
REM  LifeLine AI — Google Cloud Run Deployment Script
REM ═══════════════════════════════════════════════════════════════════
REM
REM  Prerequisites:
REM    1. Install Google Cloud CLI: https://cloud.google.com/sdk/docs/install
REM    2. Run: gcloud auth login
REM    3. Run: gcloud config set project YOUR_PROJECT_ID
REM    4. Enable required APIs (first-time only):
REM       gcloud services enable run.googleapis.com
REM       gcloud services enable cloudbuild.googleapis.com
REM       gcloud services enable artifactregistry.googleapis.com
REM
REM  Usage:
REM    deploy.bat YOUR_PROJECT_ID YOUR_GEMINI_KEY YOUR_MAPS_KEY
REM ═══════════════════════════════════════════════════════════════════

SET PROJECT_ID=%1
SET GEMINI_KEY=%2
SET MAPS_KEY=%3
SET SERVICE_NAME=lifeline-ai
SET REGION=us-central1

IF "%PROJECT_ID%"=="" (
    echo ERROR: Missing PROJECT_ID
    echo Usage: deploy.bat PROJECT_ID GEMINI_API_KEY GOOGLE_MAPS_API_KEY
    exit /b 1
)
IF "%GEMINI_KEY%"=="" (
    echo ERROR: Missing GEMINI_API_KEY
    echo Usage: deploy.bat PROJECT_ID GEMINI_API_KEY GOOGLE_MAPS_API_KEY
    exit /b 1
)

echo.
echo ══════════════════════════════════════════════════════
echo  🚀 Deploying LifeLine AI to Google Cloud Run
echo ══════════════════════════════════════════════════════
echo  Project:  %PROJECT_ID%
echo  Service:  %SERVICE_NAME%
echo  Region:   %REGION%
echo ══════════════════════════════════════════════════════
echo.

REM Step 1: Set the project
echo [1/3] Setting project...
gcloud config set project %PROJECT_ID%

REM Step 2: Build and push using Cloud Build (no local Docker needed)
echo [2/3] Building container with Cloud Build...
gcloud builds submit --tag gcr.io/%PROJECT_ID%/%SERVICE_NAME%

REM Step 3: Deploy to Cloud Run
echo [3/3] Deploying to Cloud Run...
gcloud run deploy %SERVICE_NAME% ^
    --image gcr.io/%PROJECT_ID%/%SERVICE_NAME% ^
    --port 8080 ^
    --region %REGION% ^
    --allow-unauthenticated ^
    --memory 512Mi ^
    --cpu 1 ^
    --min-instances 0 ^
    --max-instances 3 ^
    --set-env-vars "GEMINI_API_KEY=%GEMINI_KEY%,GOOGLE_MAPS_API_KEY=%MAPS_KEY%"

echo.
echo ══════════════════════════════════════════════════════
echo  ✅ Deployment complete!
echo  Run: gcloud run services describe %SERVICE_NAME% --region %REGION%
echo  to get your app URL.
echo ══════════════════════════════════════════════════════
