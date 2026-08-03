# F1 Race Analytics Explorer

Interactive Streamlit web application for exploring Formula 1 race telemetry —
built for **BCA306-5 Advanced Python, Lab Exercise P6**.

## Files in this submission

| File | Purpose |
|---|---|
| `app.py` | Main Streamlit application source code |
| `requirements.txt` | Python dependencies for deployment |
| `f1_race_data.csv` | Sample dataset (synthetic F1 lap data, 12 races × 10 drivers) |

## Features demonstrated

- **10 Streamlit widgets**: `file_uploader`, `selectbox` (×2), `multiselect`,
  `slider` (×2), `radio`, `checkbox`, `number_input`, `download_button`
- **Data visualization**: line/scatter/area charts, box plots, stacked bar charts,
  correlation heatmap — all built with Plotly Express for interactivity
- **User interaction**: race selector, driver comparison, lap-range filter,
  tyre-compound filter, live CSV upload, downloadable filtered results
- **4 analysis tabs**: Lap Time Trace, Standings & Pace, Tyre Strategy, Sector Analysis

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL shown in the terminal (usually `http://localhost:8501`).

## Deploy to Streamlit Community Cloud

1. **Create a GitHub repository** and push these 3 files to it:
   ```bash
   git init
   git add app.py requirements.txt f1_race_data.csv
   git commit -m "F1 Race Analytics Explorer - Lab P6"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<repo-name>.git
   git push -u origin main
   ```

2. **Go to** [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.

3. Click **"New app"** → select your repository → set:
   - **Branch**: `main`
   - **Main file path**: `app.py`

4. Click **Deploy**. Streamlit Cloud will install `requirements.txt` automatically
   and give you a public URL like:
   `https://<your-app-name>.streamlit.app`

5. **Submit both links** in your lab report:
   - GitHub Repository: `https://github.com/<your-username>/<repo-name>`
   - Streamlit Cloud App: `https://<your-app-name>.streamlit.app`

## Dataset

`f1_race_data.csv` is a synthetically generated dataset (7,809 rows) simulating
lap-by-lap telemetry for 10 F1 drivers across 12 races, including lap times,
tyre compounds, pit stops, sector splits, and top speeds. You may replace it
with your own CSV via the app's file uploader widget — no code changes needed,
as long as your file has the same column names.

## Screenshots to include in your submission

Take these two screenshots after deploying:
1. **Home page** — the app right after it loads, before selecting filters
2. **Output page** — any tab (e.g. Lap Time Trace) after selecting a race and drivers,
   showing the charts and metrics populated
