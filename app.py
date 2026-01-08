import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import StringIO

# Ethical Note (displayed prominently)
ETHICS_NOTE = """
**Data Ethics and Assumptions**  
This app is for demonstration purposes only and uses synthetic data. In real-world use:  
- Ensure data privacy (e.g., GDPR compliance).  
- Verify data accuracy and avoid bias.  
- Assumptions: Metrics are based on uploaded data; insights are rule-based and not predictive. No real company data is used or claimed.
"""

# Function to generate synthetic data for demo
def generate_synthetic_data():
    np.random.seed(42)
    dates = pd.date_range(start='2022-01-01', end='2023-12-31', freq='M')
    regions = ['A', 'B', 'C']
    data = []
    for date in dates:
        for region in regions:
            sales = np.random.randint(1000, 5000) + (region == 'A') * -500  # Decline in A
            volume = sales / np.random.uniform(10, 20)
            price = sales / volume
            data.append([date, region, sales, volume, price])
    df = pd.DataFrame(data, columns=['date', 'region', 'sales', 'volume', 'price'])
    return df

# Context Section: Establish data foundation
def context_section():
    st.header("1. Context")
    st.write("Establish the data foundation for decision-making.")
    st.write(ETHICS_NOTE)
    
    uploaded_file = st.file_uploader("Upload a CSV file (e.g., sales, survey, HR, operational data)", type="csv")
    use_synthetic = st.button("Use Synthetic Data for Demo")
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    elif use_synthetic:
        df = generate_synthetic_data()
    else:
        st.info("Upload a file or click 'Use Synthetic Data' to proceed.")
        return None
    
    # Overview
    st.subheader("Data Overview")
    st.write(f"**Rows:** {len(df)}, **Columns:** {len(df.columns)}")
    missing = df.isnull().sum().sum()
    st.write(f"**Missing Values:** {missing} (imputed if any)")
    
    # Impute missing values
    for col in df.select_dtypes(include=[np.number]).columns:
        df[col].fillna(df[col].mean(), inplace=True)
    for col in df.select_dtypes(include=['object']).columns:
        df[col].fillna(df[col].mode()[0], inplace=True)
    
    return df

# Evidence Section: Extract key patterns and metrics
def evidence_section(df):
    st.header("2. Evidence")
    st.write("Extract key patterns and metrics from the data.")
    
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
    
    metrics = {}
    
    if 'sales' in df.columns:
        metrics['avg_sales'] = df['sales'].mean()
        metrics['sales_trend'] = df.groupby(df['date'].dt.to_period('M'))['sales'].mean().pct_change().mean() * 100 if 'date' in df.columns else 0
        metrics['trend_variability'] = df.groupby(df['date'].dt.to_period('M'))['sales'].mean().pct_change().std() if 'date' in df.columns else 0
        st.write(f"**Average Sales:** {metrics['avg_sales']:.2f} – Calculated as the mean across all data points.")
        st.write(f"**Sales Trend:** {metrics['sales_trend']:.2f}% monthly change – Derived from percentage changes in monthly averages; negative indicates decline.")
    
    if 'sales' in df.columns and 'region' in df.columns:
        region_sales = df.groupby('region')['sales'].sum()
        metrics['region_comparison'] = region_sales.to_dict()
        st.write(f"**Region Comparison:** {metrics['region_comparison']} – Total sales summed by region; identifies performance gaps.")
    
    if 'sales' in df.columns:
        Q1 = df['sales'].quantile(0.25)
        Q3 = df['sales'].quantile(0.75)
        IQR = Q3 - Q1
        outliers = df[(df['sales'] < (Q1 - 1.5 * IQR)) | (df['sales'] > (Q3 + 1.5 * IQR))]
        metrics['outliers'] = len(outliers)
        st.write(f"**Outliers:** {metrics['outliers']} – Detected using IQR method (values beyond 1.5x interquartile range); flags anomalies.")
    
    # Additional for confidence
    metrics['data_volume'] = len(df)
    metrics['time_coverage'] = (df['date'].max() - df['date'].min()).days / 365 if 'date' in df.columns else 0
    
    # Simple Charts (supportive, unchanged)
    if 'date' in df.columns and 'sales' in df.columns:
        fig = px.line(df, x='date', y='sales', title="Sales Trend Over Time")
        st.plotly_chart(fig)
        st.write("Explanation: This line chart shows sales trends. Look for upward/downward slopes indicating growth or decline.")
    
    if 'region' in df.columns and 'sales' in df.columns:
        region_sales = df.groupby('region')['sales'].sum().reset_index()
        fig = px.bar(region_sales, x='region', y='sales', title="Sales by Region")
        st.plotly_chart(fig)
        st.write("Explanation: Bar chart compares sales across regions. Lower bars highlight underperforming areas.")
    
    return metrics

# Uncertainty Section: Highlight insights, confidence, and data gaps
def uncertainty_section(df, metrics):
    st.header("3. Uncertainty")
    st.write("Highlight insights, their confidence, and data gaps.")
    
    # Insights with Confidence and Reasoning
    insights = []
    
    def calculate_confidence(metric_key, trend_var):
        volume_score = 1 if metrics.get('data_volume', 0) > 1000 else 0.5
        time_score = 1 if metrics.get('time_coverage', 0) > 1 else 0.5
        consistency_score = 1 if trend_var < 0.2 else 0.5
        total = (volume_score + time_score + consistency_score) / 3
        if total > 0.8:
            return "High", "Based on large data volume, long time coverage, and consistent trends."
        elif total > 0.5:
            return "Medium", "Based on moderate data volume or time coverage, with some trend variability."
        else:
            return "Low", "Based on limited data volume, short time coverage, or inconsistent trends."
    
    if 'sales_trend' in metrics:
        trend_var = metrics.get('trend_variability', 0)
        conf_level, conf_reason = calculate_confidence('sales_trend', trend_var)
        if metrics['sales_trend'] < -5:
            insights.append({
                "text": "Sales are declining overall, indicating potential market challenges.",
                "confidence": conf_level,
                "reason": conf_reason + " Trend calculated as average monthly % change; decline flagged if below -5%."
            })
        elif metrics['sales_trend'] > 5:
            insights.append({
                "text": "Sales are growing steadily, suggesting strong performance.",
                "confidence": conf_level,
                "reason": conf_reason + " Trend calculated as average monthly % change; growth flagged if above 5%."
            })
    
    if 'region_comparison' in metrics:
        min_region = min(metrics['region_comparison'], key=metrics['region_comparison'].get)
        conf_level, conf_reason = calculate_confidence('region_comparison', 0)
        insights.append({
            "text": f"Sales are lowest in Region {min_region}, possibly due to regional factors.",
            "confidence": conf_level,
            "reason": conf_reason + " Comparison based on summed sales by region; lowest identified via min value."
        })
    
    if 'outliers' in metrics and metrics['outliers'] > 0:
        conf_level, conf_reason = calculate_confidence('outliers', 0)
        insights.append({
            "text": f"There are {metrics['outliers']} outlier sales values, which may indicate anomalies or opportunities.",
            "confidence": conf_level,
            "reason": conf_reason + " Outliers detected via IQR; count reflects data points outside 1.5x range."
        })
    
    if 'volume' in df.columns and 'price' in df.columns and 'region' in df.columns:
        region_a = df[df['region'] == 'A']
        if not region_a.empty:
            volume_change = region_a['volume'].pct_change().mean()
            price_change = region_a['price'].pct_change().mean()
            conf_level, conf_reason = calculate_confidence('volume_price', 0)
            if volume_change < price_change:
                insights.append({
                    "text": "Sales declined in Region A mainly due to reduced volume, not pricing.",
                    "confidence": conf_level,
                    "reason": conf_reason + " Volume/price changes calculated as average % shifts; volume decline prioritized if steeper."
                })
    
    for insight in insights:
        st.write(f"- **{insight['text']}** (Confidence: {insight['confidence']}) - {insight['reason']}")
    
    # Data Limitations & Assumptions
    st.subheader("Data Limitations & Assumptions")
    st.write("**What Variables Are Missing?** Marketing spend, competitor actions, customer demographics, and macroeconomic factors (e.g., inflation) are not in the data.")
    st.write("**What the Data Cannot Explain?** It cannot account for external events like economic downturns, regulatory changes, or supply chain disruptions.")
    st.write("**Potential Confounders?** Seasonality (e.g., holiday spikes), external shocks (e.g., pandemics), and unmeasured internal factors (e.g., employee turnover) could distort trends.")
    st.write("**Assumptions:** Trends are linear and based on available data; outliers may not represent systemic issues.")
    
    return insights

# Choice Section: Explore conditional paths and trade-offs
def choice_section(insights):
    st.header("4. Choice")
    st.write("Explore conditional paths and trade-offs. This app supports decision-makers—it does not decide. Final judgment rests with the manager, informed by context and evidence.")
    
    declining = any("declining" in i["text"].lower() for i in insights)
    
    options = {
        "Stability-Focused Path": {
            "Condition": "If the objective is short-term margin stability and risk minimization...",
            "Description": "Prioritize cost controls and operational efficiency to protect current profits.",
            "Gained": "Improved short-term cash flow and reduced volatility.",
            "Sacrificed": "Potential slower long-term growth due to limited investments.",
            "Accepted Risks": "Missed market opportunities if competitors expand aggressively."
        },
        "Growth-Focused Path": {
            "Condition": "If the objective is long-term revenue expansion and market share...",
            "Description": "Invest in targeted initiatives like regional marketing or product development.",
            "Gained": "Higher sales potential and competitive positioning.",
            "Sacrificed": "Increased short-term costs and potential profit dilution.",
            "Accepted Risks": "Investment failures if market conditions worsen unexpectedly."
        },
        "Balanced Path": {
            "Condition": "If the objective is steady progress without extreme risks...",
            "Description": "Implement incremental changes, such as optimizing underperforming regions.",
            "Gained": "Moderate improvements in efficiency and sales without major disruptions.",
            "Sacrificed": "No dramatic gains or losses; slower pace of change.",
            "Accepted Risks": "Stagnation if external factors accelerate industry shifts."
        }
    }
    
    for opt_name, opt in options.items():
        st.subheader(opt_name)
        st.write(f"**Condition:** {opt['Condition']}")
        st.write(f"**Description:** {opt['Description']}")
        st.write(f"**What is Gained:** {opt['Gained']}")
        st.write(f"**What is Sacrificed:** {opt['Sacrificed']}")
        st.write(f"**Risks Consciously Accepted:** {opt['Accepted Risks']}")
    
    # Assumption Stress Awareness
    st.subheader("What Would Change This Recommendation?")
    st.write("- **If marketing spend data were added:** It could reveal if declines are due to underinvestment, shifting preference toward growth paths.")
    st.write("- **If competitor pricing data were included:** It might show pricing pressure, altering stability-focused trade-offs.")
    st.write("- **If longer time coverage (e.g., 5+ years) were available:** It could increase confidence in trends, reducing perceived uncertainty.")
    
    return options

# Executive Summary: Board-briefing style overview
def executive_summary(insights, options):
    st.header("5. Executive Summary")
    st.write("This summary supports decision-making—it does not prescribe actions. Managers must weigh evidence against their judgment.")
    st.subheader("Situation")
    st.write("Sales data indicates mixed performance, with potential declines in key regions and outlier events suggesting underlying variability.")
    
    st.subheader("Implication")
    st.write("Without action, declining trends could erode margins; however, opportunities exist in stable or growing areas. Uncertainty arises from data gaps and external factors.")
    
    st.subheader("Decision Paths")
    for opt_name, opt in options.items():
        st.write(f"- **{opt_name}**: {opt['Condition']} {opt['Description']} (Gains: {opt['Gained']}; Sacrifices: {opt['Sacrificed']})")
    
    st.subheader("Constraints")
    st.write("Limited by data scope (e.g., no external variables); decisions must account for unmeasured risks like seasonality or shocks. Proceed with monitoring and flexibility.")

# Portfolio Footer: Signals skills and purpose
def portfolio_footer():
    st.markdown("---")
    st.subheader("About This Project")
    st.write("**Purpose:** A thinking framework for data-driven decision support under uncertainty, transforming raw data into reasoned choices.")
    st.write("**Intended Audience:** Managers, analysts, and consultants seeking structured guidance without over-reliance on data.")
    st.write("**Skills Demonstrated:** Structured thinking, data interpretation, trade-off analysis, and communication of uncertainty.")

# Main App
def main():
    st.title("Decision Advisor – Built by Drishti Chitkara")
    st.markdown("This app guides decision-making by framing context, evidence, uncertainty, and choices. It emphasizes reasoning over automation—final decisions remain with you.")
    
    df = context_section()
    if df is None:
        return
    
    metrics = evidence_section(df)
    insights = uncertainty_section(df, metrics)
    options = choice_section(insights)
    executive_summary(insights, options)
    portfolio_footer()

if __name__ == "__main__":
    main()