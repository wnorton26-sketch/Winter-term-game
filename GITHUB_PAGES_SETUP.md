# GitHub Pages Setup Guide

This guide will help you set up GitHub Pages for your Card Battler game.

## Quick Setup

### Step 1: Push to GitHub

If you haven't already, push your repository to GitHub:

```bash
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/card-battler.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 2: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click on **Settings** (top menu)
3. Scroll down to **Pages** (left sidebar)
4. Under **Source**, select:
   - **Deploy from a branch**
   - Branch: `main`
   - Folder: `/docs`
5. Click **Save**

### Step 3: Update Repository Links

Before pushing, update the links in `docs/index.html`:

1. Replace `YOUR_USERNAME` with your actual GitHub username in:
   - GitHub repository links
   - Any other references

### Step 4: Deploy

The GitHub Actions workflow will automatically deploy your site when you push to the `main` branch.

Alternatively, you can manually trigger deployment:
- Go to **Actions** tab in your repository
- Select **Deploy GitHub Pages** workflow
- Click **Run workflow**

## Access Your Site

After deployment (usually takes 1-2 minutes), your site will be available at:

```
https://YOUR_USERNAME.github.io/card-battler/
```

## Manual Deployment (Alternative)

If you prefer not to use GitHub Actions:

1. Go to repository **Settings** → **Pages**
2. Under **Source**, select:
   - **Deploy from a branch**
   - Branch: `main` or `gh-pages`
   - Folder: `/docs`
3. Click **Save**

## Custom Domain (Optional)

To use a custom domain:

1. Add a `CNAME` file in the `docs/` folder with your domain name
2. Configure DNS settings with your domain provider
3. Update GitHub Pages settings with your custom domain

## Troubleshooting

### Site not updating?
- Check GitHub Actions for any errors
- Ensure `docs/index.html` exists
- Wait a few minutes for changes to propagate

### 404 Error?
- Verify the branch and folder settings in Pages settings
- Check that `docs/index.html` is committed and pushed

### Want to preview locally?
```bash
cd docs
python3 -m http.server 8000
# Then open http://localhost:8000
```

## File Structure

```
.
├── docs/
│   └── index.html          # GitHub Pages site
├── .github/
│   └── workflows/
│       └── pages.yml       # Auto-deployment workflow
└── ... (other game files)
```

The `docs/` folder contains the static HTML site that will be served on GitHub Pages.

