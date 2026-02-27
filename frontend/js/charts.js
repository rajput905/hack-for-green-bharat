/**
 * GreenFlow AI – Chart Module
 *
 * Manages the Chart.js CO2 trend chart.
 * Requires chart.js to be loaded globally.
 */

const CO2_CHART_MAX_POINTS = 30;

let co2ChartInstance = null;

/**
 * Initialise the CO2 line chart on the given canvas ID.
 * @param {string} canvasId
 */
function initCo2Chart(canvasId) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    co2ChartInstance = new Chart(ctx, {
        type: "line",
        data: {
            labels: [],
            datasets: [
                {
                    label: "CO₂ (ppm)",
                    data: [],
                    borderColor: "#00e676",
                    backgroundColor: "rgba(0, 230, 118, 0.08)",
                    borderWidth: 2,
                    pointRadius: 3,
                    pointBackgroundColor: "#00e676",
                    tension: 0.4,
                    fill: true,
                },
                {
                    label: "Risk Threshold (400 ppm)",
                    data: [],
                    borderColor: "rgba(255, 82, 82, 0.5)",
                    borderWidth: 1,
                    borderDash: [6, 4],
                    pointRadius: 0,
                    fill: false,
                    tension: 0,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 400 },
            interaction: { mode: "index", intersect: false },
            plugins: {
                legend: {
                    labels: { color: "#6b7a8d", font: { family: "Inter", size: 11 } },
                },
                tooltip: {
                    backgroundColor: "#1a2433",
                    borderColor: "rgba(255,255,255,0.07)",
                    borderWidth: 1,
                    titleColor: "#00e676",
                    bodyColor: "#e8edf2",
                },
            },
            scales: {
                x: {
                    ticks: { color: "#6b7a8d", maxTicksLimit: 8, font: { size: 10 } },
                    grid: { color: "rgba(255,255,255,0.04)" },
                },
                y: {
                    min: 0,
                    suggestedMax: 500,
                    beginAtZero: true,
                    ticks: { color: "#6b7a8d", font: { size: 10 } },
                    grid: { color: "rgba(255,255,255,0.04)" },
                    title: { display: true, text: "ppm", color: "#6b7a8d", font: { size: 10 } },
                },
            },
        },
    });
}

/**
 * Push a new CO2 data point to the chart.
 * Automatically trims old data to CO2_CHART_MAX_POINTS.
 *
 * @param {number} co2     CO2 reading in ppm.
 * @param {string} label   Time label for the x-axis (e.g. "14:05:22").
 */
function pushCo2DataPoint(co2, label) {
    if (!co2ChartInstance) return;

    const chart = co2ChartInstance;
    chart.data.labels.push(label);
    chart.data.datasets[0].data.push(co2);
    chart.data.datasets[1].data.push(400); // threshold line

    if (chart.data.labels.length > CO2_CHART_MAX_POINTS) {
        chart.data.labels.shift();
        chart.data.datasets.forEach((ds) => ds.data.shift());
    }

    chart.update();
}
