# Decision Advisor: A Thinking Framework for Managerial Judgment

## Project Overview
This app transforms raw business data (e.g., sales, HR, or operational CSV files) into structured decision support for managers and analysts. It is designed for decision-making under uncertainty, translating data into insights, trade-offs, and conditional decision paths—without predicting outcomes.

The goal is decision support, not automation. The app emphasizes reasoning and judgment over black-box analytics.

## How the App Works
The app follows a structured decision narrative:

- **Context** – Establishes the data foundation and ethical assumptions.
- **Evidence** – Extracts key metrics (trends, averages, outliers) with transparent calculations.
- **Uncertainty** – Highlights confidence levels, data gaps, and limitations.
- **Choice** – Presents conditional decision paths with explicit trade-offs, risks, and assumptions.

Throughout, the app reinforces that final decisions remain with the human decision-maker.

## Key Design Principles
- **Explainability over Prediction** – All insights are rule-based and transparent.
- **Judgment under Uncertainty** – Data limitations and confounders are explicitly surfaced.
- **Managerial Ownership** – The tool supports decisions; it does not prescribe them.
- **Ethical Data Usage** – Uses synthetic or user-provided data only, with clear assumptions.

## Tech Stack
- **Python**
- **Streamlit** (UI & interaction)
- **Pandas / NumPy** (data handling)
- **Plotly** (visualization)

## How to Run Locally
```bash
pip install streamlit pandas numpy plotly
streamlit run app.py
