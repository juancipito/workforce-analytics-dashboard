# GitHub Push — Exact Commands

> Run these commands in order. Replace [YOUR_GITHUB_USERNAME] with your actual GitHub username.
> Working directory: `C:\Users\juanm\ai-career-ops\05_portfolio_projects\workforce_analytics_dashboard`

---

## Step 1 — Initialize the local Git repository

Open PowerShell or Git Bash and run:

```powershell
cd "C:\Users\juanm\ai-career-ops\05_portfolio_projects\workforce_analytics_dashboard"
git init
git branch -M main
```

---

## Step 2 — Create the repository on GitHub (manual step)

1. Go to: https://github.com/new
2. Fill in:
   - **Repository name:** `workforce-analytics-dashboard`
   - **Description:** `End-to-end workforce analytics pipeline for BPO contact centers — Python, Pandas, Matplotlib, Power BI. Portfolio project.`
   - **Visibility:** Public
3. **IMPORTANT — leave these UNCHECKED:**
   - Do NOT add a README
   - Do NOT add a .gitignore
   - Do NOT add a license
   *(The repo must be empty so it accepts the local push)*
4. Click **Create repository**
5. GitHub will show you the repo URL — copy it. It will look like:
   `https://github.com/[YOUR_GITHUB_USERNAME]/workforce-analytics-dashboard.git`

---

## Step 3 — Connect local repo to GitHub

```powershell
git remote add origin https://github.com/[YOUR_GITHUB_USERNAME]/workforce-analytics-dashboard.git
```

---

## Step 4 — Stage all files

```powershell
git add .
git status
```

Review the output of `git status`. Confirm you see files like:
- `README.md`
- `requirements.txt`
- `scripts/` files
- `data/workforce_bpo_simulated_data.csv`
- `assets/charts/` PNGs
- `reports/` CSVs and markdown files
- `notebooks/workforce_analytics_eda.ipynb`
- `LINKEDIN_FEATURED_TEXT.md`
- `GITHUB_PUSH_STEPS.md`

Confirm you do NOT see:
- Any `.env` file
- Any file with passwords, tokens, or API keys
- `assets/screenshots_pending.md` (excluded by .gitignore)

---

## Step 5 — Create the initial commit

```powershell
git commit -m "Initial commit: workforce analytics dashboard — Python + Power BI portfolio project"
```

---

## Step 6 — Push to GitHub

```powershell
git push -u origin main
```

If prompted, sign in with your GitHub credentials (or use a Personal Access Token if you have 2FA enabled).

---

## Step 7 — Verify the result

1. Open your browser and go to:
   `https://github.com/[YOUR_GITHUB_USERNAME]/workforce-analytics-dashboard`
2. Confirm:
   - README renders correctly with badges and embedded charts
   - All 6 PNG charts are visible in the README preview
   - Folder structure matches the project structure section of the README
   - No sensitive files are visible

---

## Optional — Add GitHub repo topics (tags)

On your GitHub repo page:
1. Click the gear icon next to **About** (top right of the repo page)
2. Add these topics:
   `python` `workforce-management` `bpo` `contact-center` `pandas` `matplotlib` `power-bi` `data-analytics` `portfolio` `wfm` `rta`
3. Also add the description from Step 2 if you haven't already.

---

## Troubleshooting

**Error: `src refspec main does not match any`**
Run `git add .` and `git commit` before pushing.

**Error: `remote origin already exists`**
Run `git remote remove origin` then repeat Step 3.

**Error: `failed to push, authentication required`**
GitHub no longer accepts password auth. Use a Personal Access Token:
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate token with `repo` scope
3. Use the token as your password when prompted

**Error: `rejected, non-fast-forward`**
The remote repo is not empty. Go to GitHub, delete the repo, and re-create it empty (Step 2).

---

*After a successful push, proceed to LINKEDIN_FEATURED_TEXT.md for the LinkedIn publication steps.*
