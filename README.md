# NexaTel Customer Churn Analytics

Public, privacy-sanitized version of the NexaTel telecom analytics dashboard. It explores churn, customer segments, service, network experience, retention campaigns and recurring revenue.

## Run locally

```bash
python -m pip install -r requirements-dashboard.txt
streamlit run app.py
```

The app loads only the dashboard tables in `data/clean/`. The public release omits raw source files and direct customer identifiers. Customer IDs have been replaced with random IDs so the dashboard can still join customer-level records.

## Sections

- Executive overview
- Customer and segments
- Service and support
- Network and regions
- Campaigns and revenue

The Dockerfile is included for container hosting. Metric definitions and limitations appear in the dashboard's Metric definitions & data notes section.
