document.addEventListener('DOMContentLoaded', () => {
    const metricsContainer = document.getElementById('metricsContainer');
    const dashboardMessage = document.getElementById('dashboardMessage');
    const advanceWeekButton = document.getElementById('advanceWeekButton');
    const simulationMessage = document.getElementById('simulationMessage');
    const fetchDashboardButton = document.getElementById('fetchDashboard');
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');


    const API_BASE_URL = '/api';

    const displayMessage = (element, message, isError = false) => {
        element.textContent = message;
        element.className = isError ? 'message error' : 'message success';
        element.style.display = 'block';
    };

    const fetchDashboardMetrics = async () => {
        const token = localStorage.getItem('accessToken');
        if (!token) {
            displayMessage(dashboardMessage, 'You must be logged in to view the dashboard.', true);
            // window.location.href = '/static/auth.html'; // Redirect to login
            return;
        }

        let url = `${API_BASE_URL}/dashboard/`;
        const params = new URLSearchParams();
        if (startDateInput.value) {
            params.append('start_date', startDateInput.value);
        }
        if (endDateInput.value) {
            params.append('end_date', endDateInput.value);
        }
        const query = params.toString();
        if (query) {
            url += `?${query}`;
        }


        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
            });

            if (response.status === 401) {
                displayMessage(dashboardMessage, 'Unauthorized. Please login again.', true);
                localStorage.removeItem('accessToken');
                return;
            }
            if (!response.ok) {
                const errData = await response.json();
                displayMessage(dashboardMessage, `Error fetching dashboard: ${errData.detail || response.statusText}`, true);
                return;
            }

            const data = await response.json();
            metricsContainer.innerHTML = ''; // Clear previous metrics

            const metricsToShow = {
                'Period': data.period_description,
                'Total Sales': `$${parseFloat(data.total_sales).toFixed(2)}`,
                'Total Spend': `$${parseFloat(data.total_spend).toFixed(2)}`,
                'ACoS': `${parseFloat(data.acos).toFixed(2)}%`,
                'ROAS': parseFloat(data.roas).toFixed(2),
                'Impressions': data.impressions,
                'Clicks': data.clicks,
                'Orders': data.orders
            };

            for (const [key, value] of Object.entries(metricsToShow)) {
                const card = document.createElement('div');
                card.className = 'metric-card';
                card.innerHTML = `<h3>${key}</h3><p>${value}</p>`;
                metricsContainer.appendChild(card);
            }
            dashboardMessage.style.display = 'none';

        } catch (error) {
            displayMessage(dashboardMessage, `Network Error: ${error.message}`, true);
        }
    };

    fetchDashboardButton.addEventListener('click', fetchDashboardMetrics);
    fetchDashboardMetrics(); // Load on page load with default (overall)

    advanceWeekButton.addEventListener('click', async () => {
        const token = localStorage.getItem('accessToken');
        if (!token) {
            displayMessage(simulationMessage, 'You must be logged in to advance simulation.', true);
            return;
        }

        try {
            simulationMessage.textContent = 'Advancing simulation...';
            simulationMessage.className = 'message';
            simulationMessage.style.display = 'block';

            const response = await fetch(`${API_BASE_URL}/simulate/advance-week`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
            });

            if (response.status === 401) {
                displayMessage(simulationMessage, 'Unauthorized. Please login again.', true);
                localStorage.removeItem('accessToken');
                return;
            }

            const data = await response.json();
            if (response.ok) {
                displayMessage(simulationMessage, data.message || 'Simulation advanced successfully!', false);
                fetchDashboardMetrics(); // Refresh dashboard after simulation
            } else {
                displayMessage(simulationMessage, `Error advancing simulation: ${data.detail || response.statusText}`, true);
            }
        } catch (error) {
            displayMessage(simulationMessage, `Network Error: ${error.message}`, true);
        }
    });
});
