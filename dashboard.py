# dashboard.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Urban Carbon & Air Quality Policy Simulator",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .policy-positive {
        color: #2ecc71;
        font-weight: bold;
    }
    .policy-negative {
        color: #e74c3c;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# API configuration
API_BASE_URL = "http://localhost:8000"

class Dashboard:
    def __init__(self):
        self.cities = [
            "Delhi", "Mumbai", "Bengaluru", "Chennai", "Kolkata",
            "Hyderabad", "Pune", "Ahmedabad", "Surat", "Jaipur"
        ]
        
    def setup_sidebar(self):
        """Setup the sidebar with policy controls."""
        st.sidebar.title("🛠️ Policy Simulation Controls")
        
        # City and Ward Selection
        selected_city = st.sidebar.selectbox("🏙️ Select City", self.cities)
        ward_options = [f"{selected_city}_W{i}" for i in range(1, 6)]
        selected_ward = st.sidebar.selectbox("📍 Select Ward", ward_options)
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("Policy Interventions")
        
        # Traffic Policy
        traffic_reduction = st.sidebar.slider(
            "🚗 Traffic Reduction (%)",
            min_value=0, max_value=50, value=15, step=5,
            help="Simulates Odd-Even rules, congestion pricing, or work-from-home policies"
        )
        
        # Afforestation Policy
        afforestation_increase = st.sidebar.number_input(
            "🌳 Afforestation Increase (sq km)",
            min_value=0.0, max_value=20.0, value=5.0, step=0.5,
            help="Simulates new urban green projects and large-scale planting"
        )
        
        # Fleet Modernization
        bs_upgrade = st.sidebar.slider(
            "🚚 Fleet BS-VI Upgrade (%)",
            min_value=0, max_value=100, value=25, step=5,
            help="Percentage of vehicle fleet upgraded to cleaner BS-VI norms"
        )
        
        # Current Conditions
        st.sidebar.markdown("---")
        st.sidebar.subheader("Current Conditions")
        
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            traffic_index = st.number_input(
                "Traffic Index", 
                min_value=0.0, max_value=100.0, value=75.0
            )
            temperature = st.number_input(
                "Temperature (°C)", 
                min_value=0.0, max_value=45.0, value=32.0
            )
        
        with col2:
            ndvi = st.slider(
                "Vegetation Health (NDVI)", 
                min_value=0.0, max_value=1.0, value=0.45
            )
            humidity = st.slider(
                "Humidity (%)", 
                min_value=0, max_value=100, value=65
            )
        
        return {
            'city': selected_city,
            'ward': selected_ward,
            'traffic_reduction': traffic_reduction,
            'afforestation_increase': afforestation_increase,
            'bs_upgrade': bs_upgrade,
            'traffic_index': traffic_index,
            'temperature': temperature,
            'ndvi': ndvi,
            'humidity': humidity
        }
    
    def call_prediction_api(self, payload):
        """Call the prediction API."""
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/predict_net_impact",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API Error: {e}")
            return None
    
    def display_metrics(self, baseline_data, scenario_data):
        """Display the main metrics and policy impact."""
        st.markdown('<div class="main-header">🌏 Urban Net Pollution Policy Simulator</div>', 
                   unsafe_allow_html=True)
        
        st.markdown("### Policy Impact Analysis")
        
        # Create columns for metrics
        col1, col2, col3 = st.columns(3)
        
        # CO2 Metric
        with col1:
            delta_co2 = scenario_data['net_co2_tonnes_day'] - baseline_data['net_co2_tonnes_day']
            delta_color = "inverse" if delta_co2 > 0 else "normal"
            
            st.metric(
                label="Net CO₂ Impact",
                value=f"{scenario_data['net_co2_tonnes_day']:,.0f} tonnes/day",
                delta=f"{delta_co2:+,.0f} tonnes/day",
                delta_color=delta_color
            )
            
            efficiency = abs(delta_co2) / (scenario_data.get('afforestation_increase_sqkm', 1) or 1)
            st.caption(f"Efficiency: {efficiency:.1f} tonnes CO₂/sq km")
        
        # PM2.5 Metric
        with col2:
            delta_pm25 = scenario_data['net_pm25_tonnes_day'] - baseline_data['net_pm25_tonnes_day']
            
            st.metric(
                label="Net PM₂.₅ Impact",
                value=f"{scenario_data['net_pm25_tonnes_day']:.3f} tonnes/day",
                delta=f"{delta_pm25:+.3f} tonnes/day",
                delta_color="inverse"
            )
            
            health_impact = delta_pm25 * 1000  # Simplified health impact metric
            st.caption(f"Estimated health benefit: {health_impact:.0f} points")
        
        # NOx Metric
        with col3:
            delta_nox = scenario_data['net_nox_tonnes_day'] - baseline_data['net_nox_tonnes_day']
            
            st.metric(
                label="Net NOₓ Impact",
                value=f"{scenario_data['net_nox_tonnes_day']:.3f} tonnes/day",
                delta=f"{delta_nox:+.3f} tonnes/day",
                delta_color="inverse"
            )
            
            air_quality_impact = delta_nox * 500  # Simplified AQI impact
            st.caption(f"Estimated AQI improvement: {air_quality_impact:.0f} points")
    
    def create_policy_impact_chart(self, baseline_data, scenario_data):
        """Create a visualization of policy impact."""
        pollutants = ['CO₂', 'PM₂.₅', 'NOₓ']
        baseline_values = [
            baseline_data['net_co2_tonnes_day'],
            baseline_data['net_pm25_tonnes_day'] * 1000,  # Scale for visibility
            baseline_data['net_nox_tonnes_day'] * 1000    # Scale for visibility
        ]
        scenario_values = [
            scenario_data['net_co2_tonnes_day'],
            scenario_data['net_pm25_tonnes_day'] * 1000,
            scenario_data['net_nox_tonnes_day'] * 1000
        ]
        
        fig = go.Figure(data=[
            go.Bar(name='Baseline', x=pollutants, y=baseline_values, marker_color='#636efa'),
            go.Bar(name='With Policy', x=pollutants, y=scenario_values, marker_color='#ef553b')
        ])
        
        fig.update_layout(
            title="Policy Impact on Net Pollution",
            xaxis_title="Pollutant",
            yaxis_title="Net Pollution (tonnes/day)",
            barmode='group',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def create_city_comparison(self):
        """Create city comparison chart."""
        st.subheader("🏆 City Performance Leaderboard")
        
        # Mock data for city comparison
        city_data = []
        for city in self.cities[:5]:  # Show top 5 for demo
            efficiency = np.random.uniform(100, 400)
            net_co2 = np.random.uniform(-5000, 30000)
            status = "Carbon Negative" if net_co2 < 0 else "Carbon Positive"
            
            city_data.append({
                'City': city,
                'Net CO₂ Status (tonnes/day)': f"{net_co2:,.0f} ({status})",
                'Sequestration Efficiency (kg CO₂/sq km)': f"{efficiency:.1f}",
                'Primary Driver': np.random.choice(['High Forest Cover', 'Low Traffic', 'High NDVI'])
            })
        
        df = pd.DataFrame(city_data)
        df = df.sort_values('Sequestration Efficiency (kg CO₂/sq km)', ascending=False)
        
        st.dataframe(df, use_container_width=True)
    
    def display_policy_recommendations(self, scenario_params, results):
        """Display AI-powered policy recommendations."""
        st.subheader("🤖 AI Policy Recommendations")
        
        recommendations = []
        
        # Traffic reduction analysis
        if scenario_params['traffic_reduction'] > 0:
            co2_reduction = results.get('policy_impact_co2', 0)
            if co2_reduction < 0:
                recommendations.append({
                    'policy': 'Traffic Reduction',
                    'impact': 'High',
                    'message': f'{scenario_params["traffic_reduction"]}% traffic reduction shows strong emissions reduction potential. Consider implementing congestion pricing.',
                    'priority': 'High'
                })
        
        # Afforestation analysis
        if scenario_params['afforestation_increase'] > 0:
            efficiency = abs(results.get('policy_impact_co2', 0)) / scenario_params['afforestation_increase']
            if efficiency > 100:
                recommendations.append({
                    'policy': 'Afforestation',
                    'impact': 'Medium',
                    'message': f'New green spaces show good sequestration efficiency ({efficiency:.1f} tonnes CO₂/sq km). Focus on native species.',
                    'priority': 'Medium'
                })
        
        # Fleet upgrade analysis
        if scenario_params['bs_upgrade'] > 0:
            nox_reduction = results.get('policy_impact_nox', 0)
            if nox_reduction < 0:
                recommendations.append({
                    'policy': 'Fleet Modernization',
                    'impact': 'High',
                    'message': f'BS-VI upgrade shows significant NOx reduction. Consider vehicle scrappage policy.',
                    'priority': 'High'
                })
        
        # Display recommendations
        if recommendations:
            for rec in recommendations:
                priority_color = {
                    'High': '🔴',
                    'Medium': '🟡',
                    'Low': '🟢'
                }
                
                with st.expander(f"{priority_color[rec['priority']]} {rec['policy']} - {rec['impact']} Impact"):
                    st.write(rec['message'])
        else:
            st.info("No strong policy recommendations based on current scenario. Try adjusting policy parameters.")
    
    def run(self):
        """Main method to run the dashboard."""
        # Setup sidebar and get parameters
        params = self.setup_sidebar()
        
        # Run simulation button
        if st.sidebar.button("🚀 Run Policy Simulation", type="primary"):
            with st.spinner("Running policy simulation..."):
                # Prepare API payload
                payload = {
                    "city_id": params['city'],
                    "ward_id": params['ward'],
                    "traffic_index_0_100": params['traffic_index'],
                    "avg_speed_kph": max(10, 60 - params['traffic_index'] * 0.4),
                    "median_ndvi": params['ndvi'],
                    "forest_area_sqkm": 35.2,  # Example base forest area
                    "max_temp_c": params['temperature'],
                    "humidity_pct": params['humidity'],
                    "wind_speed_ms": 3.0,
                    "pm25_ambient_ug_m3": 120.0,
                    "nox_ambient_ug_m3": 80.0,
                    "traffic_reduction_pct": float(params['traffic_reduction']),
                    "afforestation_increase_sqkm": params['afforestation_increase'],
                    "bs_norm_upgrade_pct": float(params['bs_upgrade'])
                }
                
                # Get baseline (no policy) prediction
                baseline_payload = payload.copy()
                baseline_payload.update({
                    "traffic_reduction_pct": 0.0,
                    "afforestation_increase_sqkm": 0.0,
                    "bs_norm_upgrade_pct": 0.0
                })
                
                baseline_response = self.call_prediction_api(baseline_payload)
                scenario_response = self.call_prediction_api(payload)
                
                if baseline_response and scenario_response:
                    # Store results in session state
                    st.session_state['baseline'] = baseline_response
                    st.session_state['scenario'] = scenario_response
                    st.session_state['params'] = params
                    st.session_state['simulation_run'] = True
        
        # Display results if simulation was run
        if st.session_state.get('simulation_run', False):
            baseline = st.session_state['baseline']
            scenario = st.session_state['scenario']
            params = st.session_state['params']
            
            # Display metrics
            self.display_metrics(baseline, scenario)
            
            # Create layout columns
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Policy impact chart
                self.create_policy_impact_chart(baseline, scenario)
                
                # Policy recommendations
                self.display_policy_recommendations(params, scenario)
            
            with col2:
                # City comparison
                self.create_city_comparison()
                
                # Key insights
                st.subheader("📊 Key Insights")
                
                total_reduction = (
                    (baseline['net_co2_tonnes_day'] - scenario['net_co2_tonnes_day']) +
                    (baseline['net_pm25_tonnes_day'] - scenario['net_pm25_tonnes_day']) * 1000 +
                    (baseline['net_nox_tonnes_day'] - scenario['net_nox_tonnes_day']) * 1000
                )
                
                st.info(f"""
                **Combined Policy Impact:** 
                - **{total_reduction:,.0f}** total pollution reduction score
                - **{(total_reduction/1000):.1f}%** overall improvement
                - Best performing: **CO₂ reduction**
                """)
        
        else:
            # Welcome message and instructions
            st.markdown('<div class="main-header">🌏 Urban Net Pollution Policy Simulator</div>', 
                       unsafe_allow_html=True)
            
            st.markdown("""
            ### Welcome to the Policy Simulation Dashboard
            
            This tool helps urban planners and policymakers understand the impact of various interventions 
            on net pollution levels (emissions minus natural removal).
            
            **How to use:**
            1. Select a city and ward from the sidebar
            2. Adjust policy parameters (traffic reduction, afforestation, fleet upgrades)
            3. Set current environmental conditions
            4. Click "Run Policy Simulation" to see the impact
            
            **Key Metrics:**
            - **Net CO₂**: Total CO₂ emissions minus sequestration by urban forests
            - **Net PM₂.₅**: Particulate matter emissions minus deposition on vegetation
            - **Net NOₓ**: Nitrogen oxides emissions minus removal by green spaces
            
            Start by configuring your policy scenario in the sidebar! 🚀
            """)
            
            # Display sample city data
            st.subheader("📈 Sample City Performance")
            self.create_city_comparison()

# Initialize and run the dashboard
if __name__ == "__main__":
    dashboard = Dashboard()
    dashboard.run()