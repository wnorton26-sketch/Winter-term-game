# How to Add Screenshots

## Screenshot Files Needed

Save your screenshots with these exact names in the `docs/screenshots/` folder:

1. **gameplay-full.png** - Full game interface showing:
   - Left panel with player stats (Floor, HP, Block, Energy, Hand)
   - Enemies section with Goblin 1 and Goblin 2
   - Your hand with cards (DEFEND, STRIKE, etc.)
   - Combat log at the bottom

2. **enemies.png** - Close-up of enemy health bars:
   - Shows Goblin 1 and Goblin 2 with their health bars
   - Displays HP values and health bar visualization

3. **cards.png** - Card display:
   - Shows DEFEND and STRIKE cards
   - Displays card costs and values

## Steps to Add Screenshots

1. **Take screenshots** of your game while it's running
2. **Save them** with the names above in the `docs/screenshots/` folder
3. **Commit and push** to GitHub:
   ```bash
   git add docs/screenshots/*.png
   git commit -m "Add game screenshots"
   git push origin main
   ```

## Recommended Screenshot Settings

- **Format:** PNG (best quality)
- **Size:** 1200-1600px width
- **Aspect Ratio:** 16:9 or 4:3
- **Make sure:** UI elements are clearly visible and readable

The screenshots will automatically appear on your GitHub Pages site once uploaded!

