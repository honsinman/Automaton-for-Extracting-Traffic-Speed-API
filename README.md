# Central Traffic Worst-Speed Monitor

This package uses your shapefile and shows **23 lines** and **46 route-directions**.

It keeps only the **worst congestion** record for each direction:
- A→B
- B→A

Worst congestion is defined as the **lowest saved speed**.

## Files
- `docs/index.html` — website
- `docs/data/routes.json` — routes extracted from the shapefile
- `docs/data/latest.json` — saved worst-speed results
- `scripts/update_data.py` — script that calls the TDAS API
- `.github/workflows/update.yml` — runs every 5 minutes on GitHub Actions

## How to use

### 1. Create a GitHub repository
Create a new repository on GitHub.

### 2. Upload these files
Upload everything in this folder to the repository.

### 3. Turn on GitHub Pages
Open:
- **Settings**
- **Pages**
- Under **Build and deployment**
  - Source: **Deploy from a branch**
  - Branch: **main**
  - Folder: **/docs**

GitHub will give you a website URL.

### 4. Allow the automatic updater
Open:
- **Actions**
- Enable workflows if GitHub asks.

The workflow runs every 5 minutes and updates `docs/data/latest.json`.

### 5. Open the website
The website reads the latest saved results and shows:
- English Name
- Chinese Name
- Direction
- Speed
- Distance
- ETA
- Extract Time
- Lane
- Capacity
- Start / End coordinates
- Last API status

## Notes
- The website itself does not call the TDAS API.
- GitHub Actions calls the API and writes the result file.
- This avoids browser CORS problems.
- If you want to start from empty saved data, replace `docs/data/latest.json` with:
  ```json
  {"updated_at": null, "records": []}
  ```
