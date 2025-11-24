import matplotlib.pyplot as plt
import os
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class EmissionVisualizer:
    """Comprehensive visualization class for emissions and sequestration data"""
    
    def __init__(self, style: str = 'seaborn'):
        self.style = style
        self.set_plot_style()
        
    def set_plot_style(self):
        """Set consistent plotting style"""
        if self.style == 'seaborn':
            sns.set_theme(style="whitegrid")
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 12
        
    def create_emissions_trend(self, data: pd.DataFrame, 
                             save_path: Optional[str] = None) -> go.Figure:
        """Create interactive emissions trend visualization"""
        try:
            fig = px.line(data, x='date', y='emissions', 
                         color='vehicle_type', 
                         title='Vehicle Emissions Trends Over Time',
                         labels={'emissions': 'Emissions (kg CO2)', 'date': 'Date'},
                         template='plotly_white')
            
            fig.update_layout(
                xaxis=dict(tickangle=45),
                hovermode='x unified'
            )
            
            if save_path:
                fig.write_html(save_path)
                base_path, _ = os.path.splitext(save_path)
                fig.write_image(f"{base_path}.png")
                
            return fig
            
        except Exception as e:
            logger.error(f"Error creating emissions trend: {str(e)}")
            raise
    
    def create_emissions_comparison(self, data: pd.DataFrame,
                                  save_path: Optional[str] = None) -> plt.Figure:
        """Create emissions comparison by vehicle type"""
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
            
            # Emissions by vehicle type
            vehicle_emissions = data.groupby('vehicle_type')['emissions'].sum().sort_values()
            ax1.barh(vehicle_emissions.index, vehicle_emissions.values)
            ax1.set_title('Total Emissions by Vehicle Type')
            ax1.set_xlabel('Total Emissions (kg CO2)')
            
            # Emissions by fuel type
            fuel_emissions = data.groupby('fuel_type')['emissions'].mean()
            colors = plt.cm.Set3(np.linspace(0, 1, len(fuel_emissions)))
            ax2.pie(fuel_emissions.values, labels=fuel_emissions.index, 
                   autopct='%1.1f%%', colors=colors)
            ax2.set_title('Emissions Distribution by Fuel Type')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                base_path, _ = os.path.splitext(save_path)
                plt.savefig(f"{base_path}.pdf", bbox_inches='tight')
                
            return fig
            
        except Exception as e:
            logger.error(f"Error creating emissions comparison: {str(e)}")
            raise
    
    def create_carbon_balance_dashboard(self, emissions_data: pd.DataFrame,
                                      sequestration_data: pd.DataFrame,
                                      save_path: Optional[str] = None) -> go.Figure:
        """Create comprehensive carbon balance dashboard"""
        try:
            # Calculate totals
            total_emissions = emissions_data['emissions'].sum()
            total_sequestration = sequestration_data['carbon_sequestered'].sum()
            net_balance = total_sequestration - total_emissions
            
            # Create subplots
            fig = go.Figure()
            
            # Add bars for emissions and sequestration
            fig.add_trace(go.Bar(
                name='Vehicle Emissions',
                x=['Carbon Balance'],
                y=[total_emissions],
                marker_color='red',
                hovertemplate='Emissions: %{y:.2f} kg CO2<extra></extra>'
            ))
            
            fig.add_trace(go.Bar(
                name='Forest Sequestration',
                x=['Carbon Balance'],
                y=[total_sequestration],
                marker_color='green',
                hovertemplate='Sequestration: %{y:.2f} kg CO2<extra></extra>'
            ))
            
            fig.update_layout(
                title='Carbon Emissions vs Sequestration Balance',
                barmode='group',
                showlegend=True,
                template='plotly_white'
            )
            
            if save_path:
                fig.write_html(save_path)
                
            return fig
            
        except Exception as e:
            logger.error(f"Error creating carbon balance dashboard: {str(e)}")
            raise

    def create_geospatial_visualization(self, data: pd.DataFrame,
                                      location_field: str = 'location',
                                      save_path: Optional[str] = None) -> go.Figure:
        """Create geospatial visualization of emissions"""
        try:
            if 'latitude' not in data.columns or 'longitude' not in data.columns:
                logger.warning("Geospatial visualization skipped - missing coordinates")
                return None

            fig = px.scatter_geo(data, 
                                lat='latitude', 
                                lon='longitude',
                                size='emissions',
                                color='vehicle_type',
                                hover_name=location_field,
                                title='Geospatial Distribution of Vehicle Emissions',
                                projection='natural earth')
            
            if save_path:
                fig.write_html(save_path)
                
            return fig
            
        except Exception as e:
            logger.warning("Geospatial visualization skipped - missing coordinates")
            return None