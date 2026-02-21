# Deploying TernQED to Cloudflare Pages

## Prerequisites
- GitHub account
- Cloudflare account (free tier works)
- Domain: ternqed.com (already registered)

---

## Step 1: Push to GitHub

```bash
cd '/Users/jameseaves/Documents/Python/Code/Automation/ternqed_website/ternqed'

# Add all files
git add .

# Commit
git commit -m "Initial TernQED site with AI agent system"

# Create GitHub repo (via gh CLI or web interface)
gh repo create ternqed --public --source=. --remote=origin --push

# Or manually:
# 1. Create repo at github.com/yourusername/ternqed
# 2. git remote add origin git@github.com:yourusername/ternqed.git
# 3. git push -u origin main
```

---

## Step 2: Connect Cloudflare Pages

### Via Cloudflare Dashboard:

1. **Go to** https://dash.cloudflare.com/
2. **Navigate to:** Pages → Create a project
3. **Connect Git:** Select your GitHub account → Select `ternqed` repository
4. **Configure build:**
   - Framework preset: **Hugo**
   - Build command: `hugo --minify`
   - Build output directory: `public`
   - Root directory: `/`
5. **Environment variables:**
   - `HUGO_VERSION` = `0.156.0` (or your version from `hugo version`)
6. **Click:** Save and Deploy

### Build will take ~1 minute

Cloudflare will give you a URL like: `ternqed.pages.dev`

---

## Step 3: Connect Custom Domain

1. **In Cloudflare Pages project:** Custom domains → Set up a custom domain
2. **Enter:** `ternqed.com` and `www.ternqed.com`
3. **DNS will auto-configure** (since domain is already in Cloudflare)
4. **SSL certificate** will be automatically provisioned (2-5 minutes)

---

## Step 4: Verify Deployment

Visit these URLs:
- https://ternqed.com
- https://ternqed.com/posts/
- https://ternqed.com/posts/jitter-vs-mean-latency/
- https://ternqed.com/about/

Check:
- ✅ Site loads fast (Cloudflare edge)
- ✅ SSL certificate valid
- ✅ RSS feed at /index.xml
- ✅ Sitemap at /sitemap.xml

---

## Automatic Deployments

Every time you push to GitHub:
1. Cloudflare detects the push
2. Runs `hugo --minify`
3. Deploys to edge network
4. Site updates in ~1 minute

---

## Publishing Workflow

### When you finish a new post:

```bash
# 1. Write with AI assistance
python3 run.py assist --research data/research/your-topic.json

# 2. Finalize and verify
python3 run.py finalize --draft content/posts/your-post.md

# 3. Commit and push
git add content/posts/your-post.md
git add data/claims/your-post.json
git commit -m "Add post: Your Title"
git push

# 4. Cloudflare auto-deploys in ~1 minute
```

---

## Advanced: GitHub Actions (Optional)

If you want to run the evidence gate on every commit:

Create `.github/workflows/verify.yml`:

```yaml
name: Evidence Gate

on: [push, pull_request]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - name: Run evidence gate on modified posts
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          for file in $(git diff --name-only HEAD^..HEAD | grep 'content/posts/.*\.md$'); do
            python3 run.py gate --draft "$file" || exit 1
          done
```

This blocks merging PRs with weak claims.

---

## Cost

**Cloudflare Pages:** Free
- Unlimited bandwidth
- Unlimited requests
- 500 builds/month (way more than you need)
- Custom domain included
- SSL included

**Total hosting cost:** $0/month

---

## Next Steps

1. ✅ Push to GitHub
2. ✅ Deploy to Cloudflare Pages
3. ✅ Connect ternqed.com domain
4. 🎉 Site is live!
