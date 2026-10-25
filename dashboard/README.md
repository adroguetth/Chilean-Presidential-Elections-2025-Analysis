# Chilean Presidential Elections 2025 — Analysis Dashboard

An interactive, bilingual (ES/EN) data visualization dashboard analyzing the 2025 Chilean Presidential Elections (first and second rounds). Built with Python, Streamlit, and Plotly.

## 🔗 Live Demo

You can explore the live dashboard here: https://chilean-presidential-election-2025.streamlit.app/

## 📊 Features

The dashboard is divided into two main sections (First Round and Second Round), each with dedicated sub-views:

### First Round

- **Summary**: National KPIs, communes won by candidate, top strongholds, and macrozone results.
- **Territorial Explorer**: A six-level interactive navigator (Macrozone → Region → Circumscription → District → Province → Commune) with a PyDeck map, null/blank vote analysis, and cascading tables.
- **Panorama**: Deep dive into national participation, null/blank votes, ideological blocks, top communes per candidate, regional winners, vote by commune size, recoverable communes for the runoff, and the anti-system vote (Parisi/Kaiser).
- **Historical**: 2021 vs 2025 comparison, including political block evolution, electoral realignment (transition matrix), and political fragmentation (Laakso-Taagepera index).

### Second Round

- **Summary**: Final runoff results (Kast vs Jara), winner block, FR vs SR comparison, and macrozone results.
- **Territorial Explorer**: Same six-level navigator as the first round, but adapted for the runoff.
- **Panorama**: Runoff participation, null/blank vote comparison (1V vs 2V), communes won, regional winners, electoral realignment, and a dedicated section on Parisi's fate (where his votes went) including a K-Means + PCA segmentation of his communes.
- **Jara / Kast**: Candidate-specific analyses, including strongholds, flips, close losses, urban-rural gradients, and protest vote correlations.
- **Historical**: 2021 runoff (Boric vs Kast) vs 2025 runoff (Kast vs Jara), with realignment heatmaps and evolution by commune.

## 🛠️ Tech Stack

- **Framework**: [Streamlit](https://streamlit.io/)
- **Data Processing**: Pandas, NumPy
- **Visualizations**: Plotly, PyDeck
- **Machine Learning**: Scikit-learn (K-Means, PCA)
- **Geospatial**: GeoPandas, Shapely
- **Statistics**: SciPy

## 📁 Project Structure

```text
Chilean-Presidential-Elections-2025-Analysis/
│
├── README.md
├── .gitignore
│
└── dashboard/
    ├── app.py                  # Main entry point
    ├── requirements.txt        # Python dependencies
    ├── .streamlit/
    │   └── config.toml         # Streamlit configuration
    │
    ├── config/                 # Global constants and translations
    ├── components/             # Reusable UI components (titles, layout, charts)
    ├── pages/                  # Page orchestrators (First Round, Second Round)
    ├── utils/                  # Data loaders, calculations, geometries, HTML helpers
    └── views/                  # Specific views for each round and candidate
        ├── first_round/
        └── second_round/
```

## 🚀 How to Run Locally

1. **Clone the repository:**

   bash

   ```
   git clone https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis.git
   cd Chilean-Presidential-Elections-2025-Analysis/dashboard
   ```

   

2. **Create a virtual environment (optional but recommended):**

   bash

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

   

3. **Install the dependencies:**

   bash

   ```
   pip install -r requirements.txt
   ```

   

4. **Run the app:**

   bash

   ```
   streamlit run app.py
   ```

   

5. **Open your browser:**
   The app should automatically open at `http://localhost:8501`.

## 🌐 Deployment

This project is configured to be deployed on **Streamlit Community Cloud**.
To deploy your own version:

1. Fork this repository.
2. Go to [share.streamlit.io](https://share.streamlit.io/).
3. Create a new app pointing to `dashboard/app.py` in your forked repository.

## 📝 Notes on Architecture & Translation

- **Bilingual Support**: All user-facing text is managed through `config/translations.py`. The app supports full ES/EN switching.
- **State Machine Exception**: The territorial navigation core (`LEVELS`, `COLS`, `KEYS`, and related functions in `views/*/territorial*.py`) is intentionally kept in Spanish to avoid breaking the fragile state machine logic. This is documented in the respective files.
- **Technical Debt**: Some user-facing strings (like certain Plotly hover labels and Parisi brackets) are still hardcoded in Spanish and should be migrated to `translations.py` in a future cleanup pass.

## 👤 Author

**Alfonso Droguett**

- GitHub: [@adroguetth](https://github.com/adroguetth)
- Email: adroguett.consultor@gmail.com
