# NexaTel Customer Intelligence Dashboard

An interactive Streamlit dashboard for exploring customer churn, segments, support experience, network quality, retention campaigns, and recurring revenue. It uses the project's cleaned CSV tables and applies shared segment, region, and city-tier filters across all five dashboard views.

## Start the dashboard

Run these commands from this folder in PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

The app opens in your browser. Keep the `data\clean` folder beside `app.py`. If that folder is unavailable, the app can also read the existing `cleaned_data` folder.

## Publish a public web version

The project includes a `Dockerfile` for container hosting and a lightweight `requirements-dashboard.txt` for the dashboard runtime. For a public URL, put this project in a GitHub repository and connect that repository to a Streamlit hosting service, selecting `app.py` as the app entry point. Keep `data/clean` in the repository so the hosted app can load its tables. The public URL is created by the hosting service after deployment; it cannot be generated from a local ZIP file alone.

## Dashboard sections

1. **Executive overview** — customer base, churn share, active recurring charges, segment comparison, and recorded exits by month.
2. **Customer & segments** — churn share, active tenure, plan charges, and segment profile.
3. **Service & support** — support ticket outcomes, first contact resolution, resolution time, complaints, and complaint counts by customer status.
4. **Network & regions** — churned customer counts by state and network experience by region.
5. **Campaigns & revenue** — campaign response and retained flags, active MRR, and invoice value over time.

## Metric notes

- Customer churn share is the proportion of customer records marked `Churned` in the selected view. It is a base snapshot, not a monthly churn rate.
- Active MRR sums monthly charges on subscriptions marked `Active`.
- Churn timeline counts records by their recorded churn month. The supplied snapshot does not provide a monthly opening-base denominator.
- Terminated subscription charges are presented as a reference measure, not realized revenue loss.
- Campaign retained flags are reported as supplied; they do not establish incremental campaign impact.
- Regional and service comparisons show associations in the available records, not causal effects.
