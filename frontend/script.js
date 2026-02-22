/*
 * Black-Litterman Portfolio Intelligence UI Controller
 * Integrates Chart.js visual structures with FastAPI math backend
 */

// -------------------------------------------------------------
// UI INTERACTIVITY & THEMES
// -------------------------------------------------------------

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Dark/Light Mode Toggle
    const themeBtn = document.getElementById('theme-btn');
    const moonIcon = document.getElementById('moon-icon');
    const sunIcon = document.getElementById('sun-icon');
    const htmlElement = document.documentElement;

    // Smooth scroll for landing page button
    document.querySelector('a[href="#dashboard"]').addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });

    themeBtn.addEventListener('click', () => {
        const currentTheme = htmlElement.getAttribute('data-theme');
        if (currentTheme === 'dark') {
            htmlElement.setAttribute('data-theme', 'light');
            moonIcon.style.display = 'none';
            sunIcon.style.display = 'block';
            updateChartsTheme('light');
        } else {
            htmlElement.setAttribute('data-theme', 'dark');
            sunIcon.style.display = 'none';
            moonIcon.style.display = 'block';
            updateChartsTheme('dark');
        }
    });

    // 2. Initialize Views Table Logic
    const viewsBody = document.getElementById('views-body');
    const addViewBtn = document.getElementById('add-view-btn');
    const clearViewsBtn = document.getElementById('clear-views-btn');

    // Default Configuration
    const presets = [
        { asset: 'AAPL', return: 12, conf: 0.60 },
        { asset: 'MSFT', return: 10, conf: 0.50 },
        { asset: 'GOOGL', return: 11, conf: 0.55 },
        { asset: 'AMZN', return: 14, conf: 0.60 },
        { asset: 'NVDA', return: 15, conf: 0.65 }
    ];

    function createRow(ticker = '', ret = '', conf = '') {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><input type="text" class="view-ticker" placeholder="e.g. AAPL" value="${ticker}" style="width: 100px;"></td>
            <td><div style="display: flex; align-items: center; gap: 6px;"><input type="number" step="0.1" class="view-return" placeholder="12.5" value="${ret}" style="width: 80px;"><span>%</span></div></td>
            <td><input type="number" step="0.05" min="0" max="1" class="view-conf" placeholder="0.5" value="${conf}" style="width: 100px;"></td>
            <td><button type="button" class="danger-btn remove-row">Remove</button></td>
        `;
        viewsBody.appendChild(tr);

        tr.querySelector('.remove-row').addEventListener('click', () => {
            tr.remove();
        });
    }

    // Populate presets natively
    presets.forEach(p => createRow(p.asset, p.return, p.conf));

    addViewBtn.addEventListener('click', () => createRow());
    clearViewsBtn.addEventListener('click', () => {
        viewsBody.innerHTML = '';
        createRow(); // Leave one empty
    });

    // 3. API Invocation Logic
    const runBtn = document.getElementById('run-optimization-btn');
    const btnText = runBtn.querySelector('span');
    const spinner = document.getElementById('loading-spinner');
    const emptyState = document.getElementById('empty-state');
    const dataViews = document.getElementById('data-views');
    const errorBox = document.getElementById('error-box');

    runBtn.addEventListener('click', async () => {
        // Collect UI Payload
        errorBox.style.display = 'none';

        const tickersRaw = document.getElementById('tickers').value;
        const tickers = tickersRaw.split(',').map(t => t.trim().toUpperCase()).filter(t => t);

        const start_date = document.getElementById('start_date').value;
        const end_date = document.getElementById('end_date').value;

        // Parse views table into dicts
        const views = {};
        const confs = {};

        const rows = document.querySelectorAll('#views-body tr');
        rows.forEach(row => {
            const rawTicker = row.querySelector('.view-ticker').value.trim().toUpperCase();
            const rawRet = row.querySelector('.view-return').value;
            const rawConf = row.querySelector('.view-conf').value;

            if (rawTicker && rawRet && rawConf && tickers.includes(rawTicker)) {
                // Return must be divided by 100 to map UI percentages (12%) to Math logic (0.12)
                views[rawTicker] = parseFloat(rawRet) / 100.0;
                confs[rawTicker] = parseFloat(rawConf);
            }
        });

        // Validation limits
        if (tickers.length < 2) {
            showError("System requires >= 2 assets to optimize correlations.");
            return;
        }

        const payload = {
            tickers: tickers,
            start_date: start_date,
            end_date: end_date,
            views: views,
            confidence: confs
        };

        // UI Loading Transition
        btnText.style.display = 'none';
        spinner.style.display = 'block';
        runBtn.disabled = true;

        try {
            const response = await fetch('/api/optimize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || "Optimization matrix failed.");
            }

            // Display Results
            emptyState.style.display = 'none';
            dataViews.style.display = 'block';

            renderDashboard(result.data, tickers);

        } catch (err) {
            showError(err.message);
        } finally {
            btnText.style.display = 'inline';
            spinner.style.display = 'none';
            runBtn.disabled = false;
        }
    });

    function showError(msg) {
        errorBox.textContent = "Engine Error: " + msg;
        errorBox.style.display = 'block';
    }

});

// -------------------------------------------------------------
// INTELLIGENCE CHARTING LOGIC (Chart.js)
// -------------------------------------------------------------

let allocationChartInstance = null;
let comparisonChartInstance = null;

function renderDashboard(data, tickers) {

    const bl = data.black_litterman;
    const mw = data.markowitz;

    // 1. Core Top Metrics
    const metrics = bl.metrics;
    document.getElementById('bl-sharpe').textContent = metrics['Sharpe Ratio'].toFixed(4);
    document.getElementById('bl-vol').textContent = (metrics['Volatility'] * 100).toFixed(2) + "%";
    document.getElementById('bl-ret').textContent = (metrics['Expected Return'] * 100).toFixed(2) + "%";

    // 2. Absolute Weights Results Table
    const tbody = document.getElementById('results-body');
    tbody.innerHTML = '';

    tickers.forEach((ticker, i) => {
        const blWeight = bl.weights[i];
        const mwWeight = mw.weights[i];
        const diff = blWeight - mwWeight;

        let diffHtml = '';
        if (diff > 0.01) {
            diffHtml = `<span style="color: var(--success); font-weight: bold;">+${(diff * 100).toFixed(2)}% Over-weight</span>`;
        } else if (diff < -0.01) {
            diffHtml = `<span style="color: var(--danger); font-weight: bold;">${(diff * 100).toFixed(2)}% Under-weight</span>`;
        } else {
            diffHtml = `<span style="color: var(--text-muted)">Matched</span>`;
        }

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td style="font-weight: bold;">${ticker}</td>
            <td><div style="width: 100%; background: var(--bg-main); border-radius: 4px; height: 16px; overflow: hidden;"><div style="width: ${(blWeight * 100).toFixed(2)}%; background: var(--accent-primary); height: 100%;"></div></div> <span style="font-size: 0.8rem; margin-top:2px; display:inline-block">${(blWeight * 100).toFixed(2)}%</span></td>
            <td>${diffHtml}</td>
        `;
        tbody.appendChild(tr);
    });

    // 3. Graphic Chart Instances
    const themeStr = document.documentElement.getAttribute('data-theme');
    const textColor = themeStr === 'dark' ? '#f8fafc' : '#0f172a';
    Chart.defaults.color = textColor;
    Chart.defaults.font.family = "'Inter', sans-serif";

    // Chart #1: Doughnut Distribution
    const ctxPie = document.getElementById('allocation-chart').getContext('2d');
    if (allocationChartInstance) allocationChartInstance.destroy();

    // Beautiful pastel color palette
    const bgColors = [
        'rgba(59, 130, 246, 0.8)',
        'rgba(139, 92, 246, 0.8)',
        'rgba(16, 185, 129, 0.8)',
        'rgba(245, 158, 11, 0.8)',
        'rgba(239, 68, 68, 0.8)',
        'rgba(14, 165, 233, 0.8)'
    ];

    allocationChartInstance = new Chart(ctxPie, {
        type: 'doughnut',
        data: {
            labels: tickers,
            datasets: [{
                data: bl.weights.map(w => w * 100),
                backgroundColor: bgColors.slice(0, tickers.length),
                borderWidth: 0,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: { position: 'right' }
            }
        }
    });

    // Chart #2: Model Bar Comparison
    const ctxBar = document.getElementById('comparison-chart').getContext('2d');
    if (comparisonChartInstance) comparisonChartInstance.destroy();

    comparisonChartInstance = new Chart(ctxBar, {
        type: 'bar',
        data: {
            labels: ['Black-Litterman', 'Markowitz'],
            datasets: [
                {
                    label: 'Expected Return (%)',
                    data: [bl.metrics['Expected Return'] * 100, mw.metrics['Expected Return'] * 100],
                    backgroundColor: 'rgba(59, 130, 246, 0.8)',
                    borderRadius: 4
                },
                {
                    label: 'Volatility (%)',
                    data: [bl.metrics['Volatility'] * 100, mw.metrics['Volatility'] * 100],
                    backgroundColor: 'rgba(239, 68, 68, 0.8)',
                    borderRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(148, 163, 184, 0.1)' }
                },
                x: {
                    grid: { display: false }
                }
            }
        }
    });
}

function updateChartsTheme(theme) {
    const textColor = theme === 'dark' ? '#f8fafc' : '#0f172a';
    Chart.defaults.color = textColor;

    if (allocationChartInstance) allocationChartInstance.update();
    if (comparisonChartInstance) comparisonChartInstance.update();
}
