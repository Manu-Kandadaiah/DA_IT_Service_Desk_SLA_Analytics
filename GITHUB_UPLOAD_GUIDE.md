# GitHub publishing guide — IT Service Desk & SLA Analytics

## Upload
- `README.md`, `.gitignore`, `requirements.txt`
- `python/`, `notebooks/`, `sql/`, `reports/`, `docs/`
- `excel/` dashboards and synthetic CSV files under `data/` (check file sizes and GitHub limits)
- This `GITHUB_UPLOAD_GUIDE.md` is optional for public display.

## Do not upload
- `.venv/`, `venv/`, `.idea/`, `__pycache__/`, `.ipynb_checkpoints/`
- `.env`, passwords, access tokens, private keys, local database files, logs, Excel lock files
- Real customer, employee or supplier records without permission
- Duplicate copies of the same dashboard outside the project folder

## Create an empty repository on GitHub
Suggested repository name: `it-service-desk-sla-analytics`. Do not initialize the remote repository with another README.

From the extracted project folder in PowerShell:

```powershell
git init
git add .
git status
git diff --cached --stat
git commit -m "Add IT Service Desk & SLA Analytics analytics portfolio"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/it-service-desk-sla-analytics.git
git push -u origin main
```

Replace `YOUR_USERNAME`. Verify staged files before committing. GitHub may require authentication via browser or a credential manager. No upload was performed during packaging.

## Make it stand out to recruiters
Capture an authentic screenshot from the Excel dashboard, save it as `assets/dashboard-preview.png`, and add `![Dashboard preview](assets/dashboard-preview.png)` near the top of `README.md`. Only add it after you have verified the screenshot.
