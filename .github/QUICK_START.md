# 🚀 StreamPulse CI/CD - Quick Reference

## What Happens When You Push Code?

### Every Push (Any Branch)
```
You: git push origin feature-branch

GitHub Actions automatically runs:
├── 🔍 Lint Python code (ruff + black)
├── 🔍 Type-check TypeScript (Next.js)
├── 🐳 Build keyword_extractor (Docker)
├── 🐳 Build related_fetcher (Docker)
├── 🐳 Build api_gateway (Docker)
├── 🐳 Build normalizer (Docker)
├── 🐳 Build trending_store (Docker)
├── 🐳 Build trending_ingestor (Docker)
├── 🧪 Run pytest tests
└── ✅ Show green checkmark on GitHub if all pass
```

**Time:** ~5-10 minutes
**Cost:** $0 (free tier)

---

### Push to `main` Branch
```
You: git push origin main

GitHub Actions runs:
├── All the above (CI + tests)
└── 🌐 Deploy frontend to Vercel (if configured)
    └── Live at: https://your-app.vercel.app
```

**Time:** ~7-12 minutes
**Cost:** $0 (free tier)

---

## GitHub Status Checks

On every commit, you'll see:
- ✅ **CI - Build & Test** — Linting + Docker builds
- ✅ **Run Tests** — pytest execution
- ⏳ **Deploy Frontend** — Only on `main` branch

Click any check to see detailed logs.

---

## Local Development (No Changes)

Your local workflow stays the same:
```bash
# Still works exactly as before
docker-compose up -d
cd frontend && npm run dev
```

CI/CD runs in the cloud — **nothing changes locally**.

---

## When CI Fails

### ❌ Lint errors
```bash
# Fix locally, then push
ruff check services/ --fix
black services/ libs/
git add . && git commit -m "Fix linting" && git push
```

### ❌ Docker build failed
```bash
# Test locally first
docker-compose build <service-name>
# Fix the Dockerfile or dependencies, then push
```

### ❌ Tests failed
```bash
# Run tests locally
pytest tests/ -v
# Fix failing tests, then push
```

---

## Deployment Options

### Option 1: CI Only (Current - FREE)
- ✅ Validates builds on every push
- ✅ Catches errors early
- ❌ Does NOT deploy anywhere
- **Cost: $0/month**

### Option 2: Frontend Deployment (FREE)
- ✅ All of Option 1
- ✅ Auto-deploys Next.js to Vercel
- ❌ Backend still runs locally
- **Cost: $0/month**

### Option 3: Full Deployment (Paid)
- ✅ All of Option 2
- ✅ Backend on Railway/DigitalOcean
- **Cost: ~$5-25/month**

**Current setup:** Option 1 (CI only)
**To enable Option 2:** Follow `.github/CI_CD_SETUP.md`

---

## FAQ

**Q: Will this break my local setup?**
A: No! CI/CD runs on GitHub's servers, not your machine.

**Q: Do I need to do anything differently?**
A: Nope. Just `git push` as normal. CI runs automatically.

**Q: What if CI fails?**
A: Your code won't be deployed (if configured), but you can still work locally. Fix errors and push again.

**Q: Can I disable CI?**
A: Yes. Delete `.github/workflows/` folder or disable in repo settings.

**Q: How do I see what went wrong?**
A: Go to GitHub → Actions tab → Click the failed run → View logs.

---

## Next Steps

1. ✅ **Push your code** — CI will run automatically
2. ✅ **Check Actions tab** on GitHub to see results
3. ✅ **(Optional)** Set up Vercel for free frontend deployment
4. ✅ **(Optional)** Add more tests to `tests/` folder

**That's it!** You're now running professional CI/CD for free 🎉
