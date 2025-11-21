// Main Application JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    setupEventListeners();
    loadSampleData();
});

function initializeCharts() {
    // Hero Chart - City Comparison
    const heroData = [{
        type: 'bar',
        x: ['Delhi', 'Mumbai', 'Bengaluru', 'Chennai', 'Kolkata'],
        y: [35000, 28000, 32000, 25000, 22000],
        name: 'Emissions',
        marker: { color: '#e74c3c' }
    }, {
        type: 'bar',
        x: ['Delhi', 'Mumbai', 'Bengaluru', 'Chennai', 'Kolkata'],
        y: [12000, 15000, 18000, 14000, 16000],
        name: 'Sequestration',
        marker: { color: '#2E8B57' }
    }];

    const heroLayout = {
        title: 'Emissions vs Sequestration (kg CO₂/day)',
        barmode: 'group',
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: 'white' },
        showlegend: true,
        legend: {
            orientation: 'h',
            x: 0,
            y: 1.1
        }
    };

    Plotly.newPlot('hero-chart', heroData, heroLayout, { responsive: true });

    // Methodology Chart
    const methodologyData = [{
        values: [35, 25, 20, 15, 5],
        labels: ['Traffic Data', 'Satellite Imagery', 'Weather Data', 'Vehicle Registry', 'Other'],
        type: 'pie',
        marker: {
            colors: ['#2E8B57', '#3498db', '#e74c3c', '#f39c12', '#9b59b6']
        }
    }];

    const methodologyLayout = {
        title: 'Data Sources Distribution',
        paper_bgcolor: 'rgba(0,0,0,0)',
        showlegend: true
    };

    Plotly.newPlot('methodology-chart', methodologyData, methodologyLayout);
}

function setupEventListeners() {
    // Slider value updates
    const trafficSlider = document.getElementById('traffic-slider');
    const forestSlider = document.getElementById('forest-slider');
    const upgradeSlider = document.getElementById('upgrade-slider');
    
    const trafficValue = document.getElementById('traffic-value');
    const forestValue = document.getElementById('forest-value');
    const upgradeValue = document.getElementById('upgrade-value');

    trafficSlider.addEventListener('input', function() {
        trafficValue.textContent = this.value + '%';
    });

    forestSlider.addEventListener('input', function() {
        forestValue.textContent = this.value;
    });

    upgradeSlider.addEventListener('input', function() {
        upgradeValue.textContent = this.value + '%';
    });

    // Simulation button
    document.getElementById('run-simulation').addEventListener('click', runSimulation);
}

function loadSampleData() {
    // Load sample city data for mini-charts
    const cities = ['delhi', 'mumbai', 'bengaluru', 'chennai', 'kolkata'];
    
    cities.forEach(city => {
        const data = generateCityData(city);
        createMiniChart(city + '-chart', data);
    });
}

function generateCityData(city) {
    // Generate sample data for each city
    const baseValues = {
        'delhi': { emission: 35000, sequestration: 12000 },
        'mumbai': { emission: 28000, sequestration: 15000 },
        'bengaluru': { emission: 32000, sequestration: 18000 },
        'chennai': { emission: 25000, sequestration: 14000 },
        'kolkata': { emission: 22000, sequestration: 16000 }
    };

    const base = baseValues[city] || baseValues.delhi;
    
    return {
        type: 'scatter',
        x: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
        y: [
            base.emission * 0.9,
            base.emission * 0.95,
            base.emission,
            base.emission * 1.05,
            base.emission * 1.1
        ],
        mode: 'lines+markers',
        line: { color: '#e74c3c', width: 2 },
        marker: { size: 6 }
    };
}

function createMiniChart(elementId, data) {
    const layout = {
        margin: { t: 0, r: 0, b: 0, l: 0 },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        xaxis: { showgrid: false, showticklabels: false },
        yaxis: { showgrid: false, showticklabels: false },
        showlegend: false
    };

    Plotly.newPlot(elementId, [data], layout, { displayModeBar: false });
}

function runSimulation() {
    const city = document.getElementById('city-select').value;
    const trafficReduction = parseInt(document.getElementById('traffic-slider').value);
    const afforestation = parseInt(document.getElementById('forest-slider').value);
    const bsUpgrade = parseInt(document.getElementById('upgrade-slider').value);

    // Simulate API call and update results
    const results = simulatePrediction(city, trafficReduction, afforestation, bsUpgrade);
    
    updateResultsDisplay(results, city, trafficReduction, afforestation, bsUpgrade);
    updateSimulationChart(results);
}

function simulatePrediction(city, trafficReduction, afforestation, bsUpgrade) {
    // Base values for each city (in kg/day)
    const baseValues = {
        'delhi': { co2: 35000, pm25: 150, nox: 280 },
        'mumbai': { co2: 28000, pm25: 120, nox: 220 },
        'bengaluru': { co2: 32000, pm25: 130, nox: 240 },
        'chennai': { co2: 25000, pm25: 110, nox: 200 },
        'kolkata': { co2: 22000, pm25: 100, nox: 180 }
    };

    const base = baseValues[city] || baseValues.delhi;
    
    // Calculate impacts
    const trafficImpact = 1 - (trafficReduction / 100) * 0.6;
    const forestImpact = 1 - (afforestation / 100) * 0.3;
    const upgradeImpact = 1 - (bsUpgrade / 100) * 0.4;

    const netCO2 = base.co2 * trafficImpact * forestImpact;
    const netPM25 = base.pm25 * trafficImpact * upgradeImpact;
    const netNOX = base.nox * trafficImpact * upgradeImpact;

    const co2Reduction = base.co2 - netCO2;
    const pm25Reduction = base.pm25 - netPM25;
    const noxReduction = base.nox - netNOX;

    return {
        netCO2: Math.round(netCO2),
        netPM25: Math.round(netPM25 * 100) / 100,
        netNOX: Math.round(netNOX * 100) / 100,
        co2Reduction: Math.round(co2Reduction),
        pm25Reduction: Math.round(pm25Reduction * 100) / 100,
        noxReduction: Math.round(noxReduction * 100) / 100
    };
}

function updateResultsDisplay(results, city, trafficReduction, afforestation, bsUpgrade) {
    // Update result values
    document.getElementById('co2-result').textContent = results.netCO2.toLocaleString();
    document.getElementById('pm25-result').textContent = results.netPM25;
    document.getElementById('nox-result').textContent = results.netNOX;

    // Update change indicators
    document.getElementById('co2-change').textContent = `-${results.co2Reduction.toLocaleString()} kg/day`;
    document.getElementById('co2-change').className = 'result-change positive';
    
    document.getElementById('pm25-change').textContent = `-${results.pm25Reduction} kg/day`;
    document.getElementById('pm25-change').className = 'result-change positive';
    
    document.getElementById('nox-change').textContent = `-${results.noxReduction} kg/day`;
    document.getElementById('nox-change').className = 'result-change positive';

    // Update metadata
    const metaText = `City: ${city.charAt(0).toUpperCase() + city.slice(1)} | Traffic: -${trafficReduction}% | Afforestation: +${afforestation}km² | BS-VI: +${bsUpgrade}%`;
    document.getElementById('results-meta').textContent = metaText;
}

function updateSimulationChart(results) {
    const data = [{
        type: 'bar',
        x: ['CO₂', 'PM₂.₅', 'NOₓ'],
        y: [results.co2Reduction, results.pm25Reduction * 100, results.noxReduction * 100],
        marker: {
            color: ['#2E8B57', '#3498db', '#e74c3c']
        }
    }];

    const layout = {
        title: 'Pollution Reduction Impact',
        xaxis: { title: 'Pollutant' },
        yaxis: { title: 'Reduction (kg/day)' },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)'
    };

    Plotly.newPlot('simulation-chart', data, layout, { responsive: true });
}

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Navbar scroll effect
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 100) {
        navbar.style.background = 'rgba(255, 255, 255, 0.98)';
        navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.1)';
    } else {
        navbar.style.background = 'rgba(255, 255, 255, 0.95)';
        navbar.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
    }
});