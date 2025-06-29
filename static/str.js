document.addEventListener('DOMContentLoaded', () => {
    const strTableBody = document.getElementById('strTableBody');
    const strMessage = document.getElementById('strMessage');
    const fetchStrReportButton = document.getElementById('fetchStrReport');
    const startDateInput = document.getElementById('strStartDate');
    const endDateInput = document.getElementById('strEndDate');
    const campaignIdInput = document.getElementById('strCampaignId');

    const prevPageButton = document.getElementById('prevPage');
    const nextPageButton = document.getElementById('nextPage');
    const pageInfoSpan = document.getElementById('pageInfo');

    const API_BASE_URL = '/api';
    let currentPage = 0; // 0-indexed for skip parameter
    const limit = 50; // Records per page

    const displayMessage = (element, message, isError = false) => {
        element.textContent = message;
        element.className = isError ? 'message error' : 'message success';
        element.style.display = 'block';
    };

    const fetchStrData = async () => {
        const token = localStorage.getItem('accessToken');
        if (!token) {
            displayMessage(strMessage, 'You must be logged in to view reports.', true);
            // window.location.href = '/static/auth.html';
            return;
        }

        let url = `${API_BASE_URL}/reports/search-term`;
        const params = new URLSearchParams();
        if (startDateInput.value) params.append('start_date', startDateInput.value);
        if (endDateInput.value) params.append('end_date', endDateInput.value);
        if (campaignIdInput.value) params.append('campaign_id', campaignIdInput.value);

        params.append('skip', currentPage * limit);
        params.append('limit', limit);

        const query = params.toString();
        if (query) {
            url += `?${query}`;
        }

        try {
            strMessage.style.display = 'none';
            strTableBody.innerHTML = '<tr><td colspan="15">Loading report...</td></tr>';

            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
            });

            if (response.status === 401) {
                displayMessage(strMessage, 'Unauthorized. Please login again.', true);
                localStorage.removeItem('accessToken');
                strTableBody.innerHTML = '<tr><td colspan="15">Unauthorized.</td></tr>';
                return;
            }
            if (!response.ok) {
                const errData = await response.json();
                displayMessage(strMessage, `Error fetching report: ${errData.detail || response.statusText}`, true);
                strTableBody.innerHTML = `<tr><td colspan="15">Error: ${errData.detail || response.statusText}</td></tr>`;
                return;
            }

            const data = await response.json();
            strTableBody.innerHTML = ''; // Clear previous data

            if (data.length === 0) {
                strTableBody.innerHTML = '<tr><td colspan="15">No search term data found for the selected criteria.</td></tr>';
            } else {
                data.forEach(item => {
                    const row = strTableBody.insertRow();
                    row.innerHTML = `
                        <td>${item.report_date}</td>
                        <td>${item.search_term_text}</td>
                        <td>${item.campaign_name || 'N/A'} (ID: ${item.campaign_id})</td>
                        <td>${item.ad_group_name || 'N/A'} (ID: ${item.ad_group_id})</td>
                        <td>${item.matched_keyword_text || 'N/A'} ${item.matched_keyword_id ? '(ID: ' + item.matched_keyword_id + ')' : ''}</td>
                        <td>${item.impressions}</td>
                        <td>${item.clicks}</td>
                        <td>${parseFloat(item.spend).toFixed(2)}</td>
                        <td>${item.orders}</td>
                        <td>${parseFloat(item.sales).toFixed(2)}</td>
                        <td>${parseFloat(item.acos).toFixed(2)}%</td>
                        <td>${parseFloat(item.roas).toFixed(2)}</td>
                        <td>${parseFloat(item.cpc).toFixed(2)}</td>
                        <td>${parseFloat(item.ctr).toFixed(2)}%</td>
                        <td>${parseFloat(item.cvr).toFixed(2)}%</td>
                    `;
                });
            }
            updatePaginationControls(data.length);

        } catch (error) {
            displayMessage(strMessage, `Network Error: ${error.message}`, true);
            strTableBody.innerHTML = `<tr><td colspan="15">Network Error: ${error.message}</td></tr>`;
        }
    };

    const updatePaginationControls = (countOnPage) => {
        pageInfoSpan.textContent = `Page ${currentPage + 1}`;
        prevPageButton.disabled = currentPage === 0;
        nextPageButton.disabled = countOnPage < limit; // Disable if fewer items than limit were returned
    };

    fetchStrReportButton.addEventListener('click', () => {
        currentPage = 0; // Reset to first page on new filter apply
        fetchStrData();
    });

    prevPageButton.addEventListener('click', () => {
        if (currentPage > 0) {
            currentPage--;
            fetchStrData();
        }
    });

    nextPageButton.addEventListener('click', () => {
        currentPage++;
        fetchStrData();
    });


    fetchStrData(); // Initial load
});
