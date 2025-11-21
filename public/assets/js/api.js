// Main Application JavaScript
const API_BASE = '/api';

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

async function initializeApp() {
    initializeCharts();
    setupEventListeners();
    await checkAPIStatus();
}

function initializeCharts() {
    // Hero Chart
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
        showlegend: true
    };

    Plotly.newPlot('hero-chart', heroData, heroLayout, { responsive: true });
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

async function checkAPIStatus() {
    try {
        const response = await fetch(`${API_BASE}/cities`);
        const statusElement = document.getElementById('api-status');
        
        if (response.ok) {
            statusElement.className = 'status-indicator active';
            statusElement.innerHTML = '<i class="fas fa-circle"></i><span>API Status: Connected</span>';
        } else {
            throw new Error('API not available');
        }
    } catch (error) {
        const statusElement = document.getElementById('api-status');
        statusElement.className = 'status-indicator inactive';
        statusElement.innerHTML = '<i class="fas fa-circle"></i><span>API Status: Offline (Using Demo)</span>';
    }
}

async function runSimulation() {
    const city = document.getElementById('city-select').value;
    const trafficReduction = parseInt(document.getElementById('traffic-slider').value);
    const afforestation = parseInt(document.getElementById('forest-slider').value);
    const bsUpgrade = parseInt(document.getElementById('upgrade-slider').value);

    const runButton = document.getElementById('run-simulation');
    const originalText = runButton.innerHTML;
    
    // Show loading state
    runButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Running...';
    runButton.disabled = true;

    try {
        const results = await runPrediction(city, trafficReduction, afforestation, bsUpgrade);
        updateResultsDisplay(results);
        updateSimulationChart(results);
    } catch (error) {
        // Fallback to demo data
        const demoResults = generateDemoResults(city, trafficReduction, afforestation, bsUpgrade);
        updateResultsDisplay(demoResults);
        updateSimulationChart(demoResults);
    } finally {
        runButton.innerHTML = originalText;
        runButton.disabled = false;
    }
}

async function runPrediction(city, trafficReduction, afforestation, bsUpgrade) {
    const response = await fetch(`${API_BASE}/predict`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            city: city,
            traffic_reduction: trafficReduction,
            afforestation: afforestation,
            bs_upgrade: bsUpgrade
        })
    });

    if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
    }

    return await response.json();
}

function generateDemoResults(city, trafficReduction, afforestation, bsUpgrade) {
    const baseValues = {
        'delhi': { co2: 35000, pm25: 150, nox: 280 },
        'mumbai': { co2: 28000, pm25: 120, nox: 220 },
        'bengaluru': { co2: 32000, pm25: 130, nox: 240 },
        'chennai': { co2: 25000, pm25: 110, nox: 200 },
        'kolkata': { co2: 22000, pm25: 100, nox: 180 }
    };
    
    const base = baseValues[city] || baseValues.delhi;
    
    const trafficImpact = 1 - (trafficReduction / 100) * 0.6;
    const forestImpact = 1 - (afforestation / 100) * 0.3;
    const upgradeImpact = 1 - (bsUpgrade / 100) * 0.4;

    const netCO2 = base.co2 * trafficImpact * forestImpact;
    const netPM25 = base.pm25 * trafficImpact * upgradeImpact;
    const netNOX = base.nox * trafficImpact * upgradeImpact;

    return {
        success: true,
        city: city,
        parameters: {
            traffic_reduction: trafficReduction,
            afforestation: afforestation,
            bs_upgrade: bsUpgrade
        },
        results: {
            net_co2: Math.round(netCO2),
            net_pm25: Math.round(netPM25 * 100) / 100,
            net_nox: Math.round(netNOX * 100) / 100,
            co2_reduction: Math.round(base.co2 - netCO2),
            pm25_reduction: Math.round((base.pm25 - netPM25) * 100) / 100,
            nox_reduction: Math.round((base.nox - netNOX) * 100) / 100
        }
    };
}

function updateResultsDisplay(results) {
    document.getElementById('co2-result').textContent = results.results.net_co2.toLocaleString();
    document.getElementById('pm25-result').textContent = results.results.net_pm25.toFixed(2);
    document.getElementById('nox-result').textContent = results.results.net_nox.toFixed(2);

    document.getElementById('co2-change').textContent = `-${results.results.co2_reduction.toLocaleString()} kg/day`;
    document.getElementById('co2-change').className = 'result-change positive';
    
    document.getElementById('pm25-change').textContent = `-${results.results.pm25_reduction.toFixed(2)} kg/day`;
    document.getElementById('pm25-change').className = 'result-change positive';
    
    document.getElementById('nox-change').textContent = `-${results.results.nox_reduction.toFixed(2)} kg/day`;
    document.getElementById('nox-change').className = 'result-change positive';

    const metaText = `City: ${results.city} | Traffic: -${results.parameters.traffic_reduction}% | Afforestation: +${results.parameters.afforestation}km² | BS-VI: +${results.parameters.bs_upgrade}%`;
    document.getElementById('results-meta').textContent = metaText;
}

function updateSimulationChart(results) {
    const data = [{
        type: 'bar',
        x: ['CO₂', 'PM₂.₅', 'NOₓ'],
        y: [
            results.results.co2_reduction / 1000, 
            results.results.pm25_reduction * 10, 
            results.results.nox_reduction * 10
        ],
        marker: {
            color: ['#2E8B57', '#3498db', '#e74c3c']
        }
    }];

    const layout = {
        title: 'Pollution Reduction Impact',
        xaxis: { title: 'Pollutant' },
        yaxis: { title: 'Reduction Impact Score' },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)'
    };

    Plotly.newPlot('simulation-chart', data, layout, { responsive: true });
}

// Smooth scrolling
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