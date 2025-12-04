# GitHub Repository Setup Guide

Your local Git repository is ready! Follow these steps to create and push to GitHub:

## Step 1: Create Repository on GitHub

1. Go to https://github.com/new
2. Repository name: `card-battler` (or any name you prefer)
3. Description: "A Python-based deck-building card battler game inspired by Slay the Spire"
4. Choose **Public** or **Private**
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click **Create repository**

## Step 2: Connect and Push

After creating the repository, GitHub will show you commands. Use these:

```bash
cd "/Users/willnorton/Library/CloudStorage/GoogleDrive-wnorton.26@pomfret.org/My Drive/NortonW - Coding/ADV code/Winter game"

# Add the remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/card-battler.git

# Rename branch to main if needed
git branch -M main

# Push to GitHub
git push -u origin main
```

## Alternative: Using GitHub CLI

If you have GitHub CLI installed:

```bash
gh repo create card-battler --public --source=. --remote=origin --push
```

## Repository Settings

After pushing, consider:
- Adding topics: `python`, `game`, `card-game`, `slay-the-spire`, `tkinter`, `flask`
- Adding a description
- Enabling GitHub Pages (if you want to host the web version)
- Adding a license file (MIT, Apache 2.0, etc.)

## Quick Commands Reference

```bash
# Check status
git status

# Add changes
git add .

# Commit changes
git commit -m "Your commit message"

# Push to GitHub
git push

# Pull from GitHub
git pull
```

