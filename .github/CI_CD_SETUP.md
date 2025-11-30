# CI/CD Setup Guide

This repository uses GitHub Actions for automated testing, building, and deployment.

## 📋 Workflows

### 1. **CI - Build & Test** (`.github/workflows/ci.yml`)
**Triggers:** Every push and pull request
**What it does:**
- ✅ Lints Python code with `ruff` and `black`
- ✅ Type-checks TypeScript frontend
- ✅ Builds all Docker services to ensure they work
- ✅ Runs ESLint on frontend code

**Status:** ✅ Active (runs automatically)

---

### 2. **Run Tests** (`.github/workflows/test.yml`)
**Triggers:** Every push and pull request
**What it does:**
- ✅ Runs `pytest` for Python services
- ✅ Starts Postgres and Redis for integration tests
- ✅ Tests normalizer, thread builder, and deep dive pipeline

**Status:** ✅ Active (non-blocking - failures won't stop deployment)

---

### 3. **Deploy Frontend** (`.github/workflows/deploy-frontend.yml`)
**Triggers:** Push to `main` branch (only when `frontend/` changes)
**What it does:**
- ✅ Builds Next.js production bundle
- ✅ Deploys to Vercel automatically

**Status:** ⚠️ Requires setup (see below)

---

## 🚀 Quick Start

### Using CI only (no deployment)
**Nothing to do!** Just push your code and GitHub Actions will:
1. Validate builds
2. Run linters
3. Execute tests

Check the **Actions** tab on GitHub to see results.

---

## 🌐 Optional: Deploy Frontend to Vercel (FREE)

### Step 1: Sign up for Vercel
1. Go to [vercel.com](https://vercel.com)
2. Sign in with your GitHub account (free)

### Step 2: Import your project
1. Click **"Add New Project"** in Vercel dashboard
2. Select your `streampulse` repository
3. Set **Root Directory** to `frontend`
4. Click **Deploy**

### Step 3: Get Vercel credentials
1. **Vercel Token:** Go to [vercel.com/account/tokens](https://vercel.com/account/tokens) → Create token
2. **Org ID:** Settings → General → copy "Organization ID"
3. **Project ID:** Project Settings → General → copy "Project ID"

### Step 4: Add GitHub Secrets
1. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"** and add:
   - `VERCEL_TOKEN` = (token from step 3.1)
   - `VERCEL_ORG_ID` = (org ID from step 3.2)
   - `VERCEL_PROJECT_ID` = (project ID from step 3.3)

### Step 5: Push to main
```bash
git add .
git commit -m "Enable CI/CD"
git push origin main
```

Your frontend will auto-deploy on every push! 🎉

---

## 📊 Viewing Results

### GitHub Actions Dashboard
1. Go to your repo on GitHub
2. Click **"Actions"** tab
3. See all workflow runs with ✅ or ❌ status

### Build Status Badges (Optional)
Add to your README.md:
```markdown
![CI](https://github.com/Aryan1patel/streampulse/actions/workflows/ci.yml/badge.svg)
![Tests](https://github.com/Aryan1patel/streampulse/actions/workflows/test.yml/badge.svg)
```

---

## 🔧 Customization

### Add more Docker services to CI
Edit `.github/workflows/ci.yml` and add to the `matrix.service` list:
```yaml
matrix:
  service:
    - keyword_extractor
    - related_fetcher
    - your_new_service  # Add here
```

### Add Python dependencies for tests
Edit `.github/workflows/test.yml` and add to install step:
```yaml
- name: Install dependencies
  run: |
    pip install your-package-here
```

---

## 💰 Cost

**Everything is FREE:**
- ✅ GitHub Actions: 2,000 minutes/month (private repos) or unlimited (public repos)
- ✅ Vercel: Unlimited deploys for hobby projects
- ✅ Total: **$0/month**

---

## 🐛 Troubleshooting

### "Workflow failed on lint-python"
Run locally to fix:
```bash
pip install ruff black
ruff check services/ libs/ --fix
black services/ libs/
```

### "Docker build failed"
Test locally:
```bash
docker-compose build <service-name>
```

### "Tests failed"
Run locally:
```bash
pytest tests/ -v
```

### "Vercel deployment failed"
Check if secrets are set correctly in GitHub repo settings.

---

## 📚 Next Steps

1. ✅ Push code and watch CI run automatically
2. ✅ (Optional) Set up Vercel deployment for frontend
3. ✅ Add more tests in `tests/` directory
4. ✅ Add backend deployment (Railway/DigitalOcean) if needed

**Questions?** Check the comments in each workflow file for details.
