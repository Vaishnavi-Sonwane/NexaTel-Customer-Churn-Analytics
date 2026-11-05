from __future__ import annotations

from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="NexaTel | Customer Intelligence", page_icon="◈", layout="wide", initial_sidebar_state="expanded")
ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "clean"
if not DATA.exists():
    DATA = ROOT / "cleaned_data"

COLORS = ["#16B8A6", "#4C7CF3", "#F3A642", "#8A72E8", "#E56F82", "#44A7D8"]
px.defaults.color_discrete_sequence = COLORS
PLOT = dict(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=44, b=10), font=dict(family="Inter, Segoe UI, sans-serif", color="#344054"))


@st.cache_data(show_spinner="Preparing the customer view…")
def load_data():
    names = ["customers", "subscriptions", "plans", "billing", "support_tickets", "complaints", "network_quality", "retention_campaigns", "cities", "states", "usage_data", "contracts"]
    frames = {}
    for name in names:
        path = DATA / f"{name}.csv"
        if path.exists():
            frames[name] = pd.read_csv(path, low_memory=False)
    return frames


def date_col(frame, column, fmt="%d-%m-%Y"):
    if column in frame:
        frame[column] = pd.to_datetime(frame[column], format=fmt, errors="coerce")
    return frame


def inr(value):
    if pd.isna(value):
        return "—"
    return f"₹{value:,.0f}"


def pct(value):
    return "—" if pd.isna(value) else f"{value:.1f}%"


def polish(fig, height=350):
    fig.update_layout(**PLOT, height=height, legend_title_text="")
    fig.update_xaxes(showgrid=False, linecolor="#EAECF0")
    fig.update_yaxes(gridcolor="#EEF1F5", zeroline=False)
    return fig


def section_title(title, sub):
    st.markdown(f'<div class="section-head"><div><h2>{title}</h2><p>{sub}</p></div></div>', unsafe_allow_html=True)


def metric(label, value, note=""):
    st.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>', unsafe_allow_html=True)


st.markdown("""<style>
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;color:#182230}
.stApp{background:#F5F7FA}.block-container{padding-top:1.6rem;max-width:1500px}
section[data-testid="stSidebar"]{background:#111D35} section[data-testid="stSidebar"] *{color:#E8EDF6}
.brand{padding:8px 4px 22px;border-bottom:1px solid #34425B;margin-bottom:20px}.brand small{color:#AAB8D0;letter-spacing:.13em;font-weight:700;font-size:10px}.brand h2{font:800 24px Manrope;margin:7px 0 2px;color:white}.brand p{margin:0;color:#AAB8D0;font-size:12px}
.eyebrow{font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#61718A;margin-bottom:5px}.hero-title{font:800 31px Manrope;color:#182230;margin:0}.hero-sub{font-size:14px;color:#667085;margin:5px 0 24px}
.metric{background:white;border:1px solid #EAECF0;border-radius:15px;padding:18px 19px;min-height:126px;box-shadow:0 2px 7px rgba(16,24,40,.025)}.metric-label{font-size:12px;color:#667085;font-weight:600}.metric-value{font:800 27px Manrope;color:#182230;margin:8px 0 3px}.metric-note{font-size:11px;color:#98A2B3}
.section-head{display:flex;align-items:end;justify-content:space-between;margin:22px 0 10px}.section-head h2{font:700 19px Manrope;margin:0;color:#182230}.section-head p{margin:4px 0 0;font-size:12px;color:#667085}
.insight{background:#ECF8F6;border-left:3px solid #16B8A6;border-radius:8px;padding:13px 16px;color:#344054;font-size:13px;margin:10px 0 18px}.note{font-size:11px;color:#7A8699}
div[data-testid="stPlotlyChart"]{background:white;border:1px solid #EAECF0;border-radius:14px;padding:8px 8px 0}
div[data-testid="stDataFrame"]{border-radius:12px;overflow:hidden}
</style>""", unsafe_allow_html=True)

data = load_data()
if "customers" not in data:
    st.error(f"Customer data was not found. Expected cleaned CSV files in `{DATA}`.")
    st.stop()

customers = data["customers"].copy()
if "states" in data and "state_id" in customers:
    state_table = data["states"]
    state_name_col = next((col for col in ["state_name", "state", "name"] if col in state_table.columns), None)
    if state_name_col and "state_id" in state_table.columns:
        state_names = state_table[["state_id", state_name_col]].drop_duplicates("state_id").rename(columns={state_name_col: "state_name_lookup"})
        customers = customers.merge(state_names, on="state_id", how="left")
        if "state_name" not in customers:
            customers = customers.rename(columns={"state_name_lookup": "state_name"})
        else:
            customers["state_name"] = customers["state_name"].fillna(customers["state_name_lookup"])
            customers = customers.drop(columns="state_name_lookup")
for frame_name, col in [("customers", "acquisition_date"), ("customers", "churn_date"), ("billing", "billing_date"), ("support_tickets", "created_date"), ("complaints", "complaint_date"), ("retention_campaigns", "contact_date"), ("contracts", "end_date")]:
    if frame_name in data:
        date_col(data[frame_name], col)

st.sidebar.markdown('<div class="brand"><small>NEXATEL · CUSTOMER INTELLIGENCE</small><h2>◈ NexaTel</h2><p>Retention & experience workspace</p></div>', unsafe_allow_html=True)
page = st.sidebar.radio("WORKSPACE", ["Executive overview", "Customer & segments", "Service & support", "Network & regions", "Campaigns & revenue"], label_visibility="visible")
st.sidebar.markdown("---")
st.sidebar.markdown("#### Refine the view")
segments = sorted(customers["customer_segment"].dropna().astype(str).unique()) if "customer_segment" in customers else []
regions = sorted(customers["region_id"].dropna().astype(str).unique()) if "region_id" in customers else []
selected_segments = st.sidebar.multiselect("Customer segment", segments, placeholder="All segments")
selected_regions = st.sidebar.multiselect("Region", regions, placeholder="All regions")
city_tiers = sorted(customers["city_tier"].dropna().astype(str).unique()) if "city_tier" in customers else []
selected_tiers = st.sidebar.multiselect("City tier", city_tiers, placeholder="All city tiers")

view = customers.copy()
for col, choices in [("customer_segment", selected_segments), ("region_id", selected_regions), ("city_tier", selected_tiers)]:
    if choices and col in view:
        view = view[view[col].astype(str).isin(choices)]
ids = set(view["customer_id"].dropna())
st.sidebar.caption(f"Showing {len(view):,} of {len(customers):,} customers")
st.sidebar.caption("Data source: cleaned project tables")

churned = view[view.get("customer_status", pd.Series(index=view.index, dtype=str)).astype(str).str.casefold().eq("churned")]
active = view[view.get("customer_status", pd.Series(index=view.index, dtype=str)).astype(str).str.casefold().eq("active")]
churn_rate = len(churned) / len(view) * 100 if len(view) else float("nan")
subs = data.get("subscriptions", pd.DataFrame()).copy()
if len(subs) and "customer_id" in subs:
    subs = subs[subs["customer_id"].isin(ids)]
active_subs = subs[subs.get("subscription_status", pd.Series(index=subs.index, dtype=str)).astype(str).str.casefold().eq("active")]
mrr = pd.to_numeric(active_subs.get("monthly_charge_inr", pd.Series(dtype=float)), errors="coerce").sum()
rev_risk = pd.to_numeric(subs.loc[subs.get("subscription_status", pd.Series(index=subs.index, dtype=str)).astype(str).str.casefold().eq("terminated")].get("monthly_charge_inr", pd.Series(dtype=float)), errors="coerce").sum()

st.markdown('<div class="eyebrow">RETENTION PERFORMANCE</div>', unsafe_allow_html=True)
st.markdown(f'<h1 class="hero-title">{page}</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">A decision-ready view of customer health, service quality and revenue exposure.</p>', unsafe_allow_html=True)


if page == "Executive overview":
    section_title("Business pulse", "Current customer base and recurring revenue exposure")
    cols = st.columns(4)
    with cols[0]: metric("Customers in view", f"{len(view):,}", "Filtered customer base")
    with cols[1]: metric("Customer churn share", pct(churn_rate), f"{len(churned):,} churned customers")
    with cols[2]: metric("Active subscribers", f"{len(active):,}", "Current customer status")
    with cols[3]: metric("Active MRR", inr(mrr), "Sum of active subscription charges")
    c1, c2 = st.columns([1.15, .85])
    with c1:
        section_title("Customer mix", "Active and churned customers in the filtered base")
        mix = pd.DataFrame({"Status": ["Active", "Churned"], "Customers": [len(active), len(churned)]})
        st.plotly_chart(polish(px.bar(mix, x="Status", y="Customers", color="Status", text_auto=True)), use_container_width=True)
    with c2:
        section_title("Churn by segment", "Share of customers marked churned")
        if "customer_segment" in view:
            grp = view.assign(_churn=view["customer_status"].astype(str).str.casefold().eq("churned")).groupby("customer_segment", dropna=False)["_churn"].mean().mul(100).reset_index(name="Churn share")
            st.plotly_chart(polish(px.bar(grp, x="customer_segment", y="Churn share", color="customer_segment", text_auto=".1f")), use_container_width=True)
    section_title("Churn timeline", "Customer exits by recorded churn month · customer counts")
    timeline = churned.copy()
    if "churn_date" in timeline:
        timeline["churn_date"] = pd.to_datetime(timeline["churn_date"], errors="coerce", dayfirst=True)
        series = timeline.dropna(subset=["churn_date"]).assign(Month=lambda d: d["churn_date"].dt.to_period("M").dt.to_timestamp()).groupby("Month").size().reset_index(name="Customers churned")
        if len(series):
            st.plotly_chart(polish(px.area(series, x="Month", y="Customers churned", markers=True)), use_container_width=True)
        else: st.info("No usable churn dates are available in this filtered view.")
    st.markdown('<div class="insight">Read the churn timeline as recorded customer exits. This snapshot does not include a monthly opening customer base, so it does not represent a monthly churn rate.</div>', unsafe_allow_html=True)

elif page == "Customer & segments":
    section_title("Who is leaving?", "Compare churn, tenure and customer value across the filtered base")
    cols = st.columns(3)
    with cols[0]: metric("Churn share", pct(churn_rate), "Share of filtered customer records")
    with cols[1]: metric("Average active tenure", f"{pd.to_numeric(active.get('tenure_months', pd.Series(dtype=float)), errors='coerce').mean():.0f} mo" if len(active) else "—", "Current active customers")
    with cols[2]: metric("Average active plan charge", inr(pd.to_numeric(active_subs.get("monthly_charge_inr", pd.Series(dtype=float)), errors="coerce").mean()), "Across active subscriptions")
    left, right = st.columns(2)
    with left:
        section_title("Churn by segment", "Rates use the customer status field")
        seg = view.assign(_churn=view["customer_status"].astype(str).str.casefold().eq("churned")).groupby("customer_segment")["_churn"].mean().mul(100).reset_index(name="Churn share")
        st.plotly_chart(polish(px.bar(seg, x="customer_segment", y="Churn share", color="customer_segment", text_auto=".1f")), use_container_width=True)
    with right:
        section_title("Customer tenure", "Active customer count by tenure band")
        t = active.copy()
        t["tenure_months"] = pd.to_numeric(t.get("tenure_months"), errors="coerce")
        t["Tenure band"] = pd.cut(t["tenure_months"], [-1, 3, 12, 36, float("inf")], labels=["0–3 months", "4–12 months", "1–3 years", "3+ years"])
        tenure = t.groupby("Tenure band", observed=False).size().reset_index(name="Customers")
        st.plotly_chart(polish(px.bar(tenure, x="Tenure band", y="Customers", color="Tenure band", text_auto=True)), use_container_width=True)
    section_title("Segment profile", "Customer counts and average tenure")
    profile = view.groupby("customer_segment", dropna=False).agg(Customers=("customer_id", "nunique"), Avg_tenure_months=("tenure_months", "mean")).reset_index().rename(columns={"customer_segment": "Segment", "Avg_tenure_months": "Average tenure (months)"})
    st.dataframe(profile, hide_index=True, use_container_width=True)

elif page == "Service & support":
    tickets = data.get("support_tickets", pd.DataFrame()).copy()
    complaints = data.get("complaints", pd.DataFrame()).copy()
    if len(tickets) and "customer_id" in tickets: tickets = tickets[tickets["customer_id"].isin(ids)]
    if len(complaints) and "customer_id" in complaints: complaints = complaints[complaints["customer_id"].isin(ids)]
    fcr = tickets.get("first_contact_resolution", pd.Series(dtype=str)).astype(str).str.casefold().isin(["yes", "true", "1"]).mean() * 100 if len(tickets) else float("nan")
    resolved_hours = pd.to_numeric(tickets.loc[tickets.get("status", pd.Series(index=tickets.index, dtype=str)).astype(str).str.casefold().eq("resolved")].get("resolution_hours", pd.Series(dtype=float)), errors="coerce").mean() if len(tickets) else float("nan")
    section_title("Service experience", "Support outcomes among customers in the filtered base")
    cols = st.columns(4)
    with cols[0]: metric("Support tickets", f"{len(tickets):,}", "Filtered ticket records")
    with cols[1]: metric("First contact resolution", pct(fcr), "Ticket records marked Yes")
    with cols[2]: metric("Mean resolution time", f"{resolved_hours:.1f} hrs" if pd.notna(resolved_hours) else "—", "Resolved tickets with a recorded duration")
    with cols[3]: metric("Complaints", f"{len(complaints):,}", "Filtered complaint records")
    left, right = st.columns(2)
    with left:
        section_title("Ticket status", "Support workload by current status")
        if len(tickets): st.plotly_chart(polish(px.histogram(tickets, x="status", color="status")), use_container_width=True)
        else: st.info("No support ticket data found.")
    with right:
        section_title("Complaint status", "Resolution progress by complaint record")
        if len(complaints): st.plotly_chart(polish(px.histogram(complaints, x="status", color="status")), use_container_width=True)
        else: st.info("No complaint data found.")
    if len(complaints):
        unresolved = complaints[complaints["status"].astype(str).str.casefold().isin(["unresolved", "pending"])]
        rates = view[["customer_id", "customer_status"]].copy()
        unresolved_n = unresolved.groupby("customer_id").size().rename("Open complaints")
        rates = rates.merge(unresolved_n, on="customer_id", how="left").fillna({"Open complaints": 0})
        rates["Churn status"] = rates["customer_status"].astype(str).str.casefold().eq("churned").map({True: "Churned", False: "Active"})
        rates["Complaint band"] = rates["Open complaints"].clip(upper=3).astype(int).astype(str).replace({"3": "3+"})
        comp = rates.groupby(["Complaint band", "Churn status"]).size().reset_index(name="Customers")
        section_title("Open complaints and customer status", "Association in this snapshot; not evidence of cause")
        st.plotly_chart(polish(px.bar(comp, x="Complaint band", y="Customers", color="Churn status", barmode="group")), use_container_width=True)
    st.markdown('<div class="insight">Support and complaint records are events, so a customer may appear more than once. FCR and resolution time are calculated at ticket level.</div>', unsafe_allow_html=True)

elif page == "Network & regions":
    net = data.get("network_quality", pd.DataFrame()).copy()
    if len(net) and "customer_id" in net: net = net[net["customer_id"].isin(ids)]
    section_title("Regional service health", "Find locations where customer experience and retention need a closer look")
    left, right = st.columns(2)
    with left:
        section_title("Churned customers by state", "Absolute customer count in the filtered base")
        if "state_name" in view:
            by_state = churned.groupby("state_name").size().nlargest(12).sort_values().reset_index(name="Churned customers")
            st.plotly_chart(polish(px.bar(by_state, x="Churned customers", y="state_name", orientation="h", color="Churned customers", color_continuous_scale=["#B7E6DF", "#12877D"])), use_container_width=True)
        elif "state_id" in view:
            by_state = churned.groupby("state_id").size().nlargest(12).sort_values().reset_index(name="Churned customers")
            st.plotly_chart(polish(px.bar(by_state, x="Churned customers", y="state_id", orientation="h", color="Churned customers")), use_container_width=True)
        else: st.info("State field is not available in customer data.")
    with right:
        section_title("Network experience by region", "Mean dropped-call rate from network quality records")
        if len(net) and "city_id" in net and "cities" in data:
            city = data["cities"][[c for c in ["city_id", "region_id", "state_name", "city_name"] if c in data["cities"]]].drop_duplicates("city_id")
            nq = net.merge(city, on="city_id", how="left")
            if selected_regions and "region_id" in nq: nq = nq[nq["region_id"].astype(str).isin(selected_regions)]
            dim = "region_id" if "region_id" in nq else "state_name"
            if dim in nq:
                chart = nq.groupby(dim)["dropped_call_rate_pct"].mean().sort_values(ascending=False).head(12).reset_index()
                st.plotly_chart(polish(px.bar(chart, x="dropped_call_rate_pct", y=dim, orientation="h", color="dropped_call_rate_pct", color_continuous_scale=["#C8D8FF", "#4C7CF3"])), use_container_width=True)
            else: st.info("Regional labels are not available for the network records.")
        elif len(net):
            st.plotly_chart(polish(px.histogram(net, x="dropped_call_rate_pct", nbins=24, labels={"dropped_call_rate_pct": "Dropped-call rate (%)"})), use_container_width=True)
        else: st.info("No network quality data found.")
    if len(net):
        section_title("Network quality indicators", "Distribution of recorded customer experience")
        net_cols = st.columns(3)
        for i, (column, label, agg) in enumerate([("dropped_call_rate_pct", "Avg dropped-call rate", "%"), ("avg_download_speed_mbps", "Avg download speed", "Mbps"), ("network_downtime_hours", "Avg downtime", "hrs")]):
            with net_cols[i]:
                val = pd.to_numeric(net.get(column, pd.Series(dtype=float)), errors="coerce").mean()
                metric(label, f"{val:.1f} {agg}" if pd.notna(val) else "—", "Mean across available network records")
    st.markdown('<div class="insight">Network readings are averaged from customer-month records. Regional comparisons summarize experience; they do not establish that network quality caused churn.</div>', unsafe_allow_html=True)

else:
    campaigns = data.get("retention_campaigns", pd.DataFrame()).copy()
    if len(campaigns) and "customer_id" in campaigns: campaigns = campaigns[campaigns["customer_id"].isin(ids)]
    section_title("Retention investment & revenue", "Campaign responses and recurring subscription value")
    accepted = campaigns.get("response", pd.Series(dtype=str)).astype(str).str.casefold().eq("accepted").sum() if len(campaigns) else 0
    retained = campaigns.get("retained_flag", pd.Series(dtype=str)).astype(str).str.casefold().isin(["yes", "true", "1"]).mean() * 100 if len(campaigns) else float("nan")
    cols = st.columns(4)
    with cols[0]: metric("Campaign contacts", f"{len(campaigns):,}", "Filtered retention records")
    with cols[1]: metric("Accepted offers", f"{accepted:,}", "Response marked Accepted")
    with cols[2]: metric("Retained flag share", pct(retained), "Campaign records marked retained")
    with cols[3]: metric("Active MRR", inr(mrr), "Sum of active subscription charges")
    left, right = st.columns(2)
    with left:
        section_title("Campaign response", "How customers responded to retention outreach")
        if len(campaigns):
            response = campaigns["response"].fillna("No response").value_counts().rename_axis("Response").reset_index(name="Contacts")
            st.plotly_chart(polish(px.pie(response, names="Response", values="Contacts", hole=.64)), use_container_width=True)
        else: st.info("No retention campaign data found.")
    with right:
        section_title("Campaign results", "Retained flag by response label")
        if len(campaigns) and "retained_flag" in campaigns:
            campaigns["Retained"] = campaigns["retained_flag"].astype(str).str.casefold().isin(["yes", "true", "1"]).map({True: "Retained", False: "Not marked retained"})
            by_response = campaigns.groupby(["response", "Retained"], dropna=False).size().reset_index(name="Records")
            st.plotly_chart(polish(px.bar(by_response, x="response", y="Records", color="Retained", barmode="group")), use_container_width=True)
        else: st.info("Campaign outcome fields are not available.")
    bills = data.get("billing", pd.DataFrame()).copy()
    if len(bills) and "customer_id" in bills: bills = bills[bills["customer_id"].isin(ids)]
    if len(bills) and "billing_date" in bills:
        bills["billing_date"] = pd.to_datetime(bills["billing_date"], errors="coerce", dayfirst=True)
        monthly = bills.dropna(subset=["billing_date"]).assign(Month=lambda d: d["billing_date"].dt.to_period("M").dt.to_timestamp()).groupby("Month")["total_amount_inr"].sum().reset_index(name="Invoiced amount (₹)")
        section_title("Billing trend", "Total invoice value by billing month")
        if len(monthly): st.plotly_chart(polish(px.area(monthly, x="Month", y="Invoiced amount (₹)", markers=True)), use_container_width=True)
    st.markdown(f'<div class="insight">Terminated subscription charges in this filtered dataset sum to <b>{inr(rev_risk)}</b>. This is a reference measure of terminated recurring charges, not verified realized revenue loss. Campaign retention flags report observed outcomes and do not establish incremental campaign impact.</div>', unsafe_allow_html=True)

with st.expander("Metric definitions & data notes"):
    st.markdown("""
    - **Customer churn share:** customers marked `Churned` divided by customer records in the current filter selection.
    - **Active MRR:** sum of monthly charges for subscriptions marked `Active`.
    - **Churn timeline:** count of customer records by recorded churn month. This snapshot has no monthly opening-base denominator.
    - **FCR:** share of support ticket records marked Yes for first contact resolution.
    - **Campaign retained share:** share of campaign contact records marked retained in the source field.
    - All figures reflect the cleaned project data and update with the segment, region and city-tier filters.
    """)
st.markdown('<div class="note" style="text-align:center;margin:34px 0 10px">NexaTel Customer Intelligence · Internal analytics workspace</div>', unsafe_allow_html=True)
