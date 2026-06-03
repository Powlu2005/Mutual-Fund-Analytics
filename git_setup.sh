#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════
#  git_setup.sh — Initialise Git repo and push to GitHub
#  Run once from the project root:
#      chmod +x git_setup.sh && ./git_setup.sh
# ═══════════════════════════════════════════════════════════

set -e  # exit on first error

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║   Mutual Fund Analytics — Git Setup                  ║"
echo "╚══════════════════════════════════════════════════════╝"

# ── 1. Configure Git identity (edit these) ──────────────────
GIT_NAME="Your Name"
GIT_EMAIL="you@email.com"
GITHUB_USERNAME="your-github-username"
REPO_NAME="mutual-fund-analytics"

git config --global user.name  "$GIT_NAME"
git config --global user.email "$GIT_EMAIL"

# ── 2. Initialise repo ───────────────────────────────────────
echo ""
echo "  [1/5] Initialising Git repository..."
git init
git branch -M main

# ── 3. Stage all files ───────────────────────────────────────
echo "  [2/5] Staging files..."
git add .gitignore
git add README.md
git add requirements.txt
git add data_ingestion.py
git add live_nav_fetch.py
git add git_setup.sh
# Add empty .gitkeep placeholders so empty folders are tracked
touch data/raw/.gitkeep
touch data/processed/.gitkeep
touch notebooks/.gitkeep
touch sql/.gitkeep
touch dashboard/.gitkeep
touch reports/.gitkeep
git add data/raw/.gitkeep data/processed/.gitkeep \
        notebooks/.gitkeep sql/.gitkeep \
        dashboard/.gitkeep reports/.gitkeep

# ── 4. First commit ──────────────────────────────────────────
echo "  [3/5] Creating first commit..."
git commit -m "Day 1: Data ingestion complete

- Added project folder structure (data/raw, data/processed,
  notebooks, sql, dashboard, reports)
- Created requirements.txt with all dependencies
- data_ingestion.py: loads all datasets, inspects shape/dtypes/head,
  flags anomalies, explores fund_master, validates AMFI codes
- live_nav_fetch.py: fetches live NAV from mfapi.in for
  HDFC Top 100 (125497) and 5 key bluechip schemes
- README.md with setup instructions and progress log"

# ── 5. Push to GitHub ────────────────────────────────────────
echo "  [4/5] Adding remote origin..."
echo ""
echo "  ─────────────────────────────────────────────────────"
echo "  BEFORE this script pushes, create an empty repo on"
echo "  GitHub named: $REPO_NAME"
echo "  URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo "  (Do NOT initialise with README — keep it empty)"
echo "  ─────────────────────────────────────────────────────"
echo ""
read -p "  Press ENTER once the GitHub repo is created..."

git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"

echo "  [5/5] Pushing to GitHub..."
git push -u origin main

echo ""
echo "  ✔  Repository live at:"
echo "     https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo ""
echo "  Next: Run python data_ingestion.py"
echo "        Run python live_nav_fetch.py"
