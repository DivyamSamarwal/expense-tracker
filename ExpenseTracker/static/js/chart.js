// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Only run on dashboard page if the chart element exists
    const chartElement = document.getElementById('categoryPieChart');
    if (!chartElement) return;
    
    // Fetch chart data from the API
    fetch('/api/chart_data')
        .then(response => response.json())
        .then(data => {
            createCategoryPieChart(data);
        })
        .catch(error => {
            console.error('Error fetching chart data:', error);
        });
    
    // Function to create the category pie chart
    function createCategoryPieChart(data) {
        // Extract categories and amounts
        const categories = data.map(item => item.category);
        const amounts = data.map(item => item.amount);
        
        // Define a color palette for categories
        const backgroundColors = [
            '#4dc9f6', '#f67019', '#f53794', '#537bc4', '#acc236',
            '#166a8f', '#00a950', '#58595b', '#8549ba', '#a4e43f',
            '#df5e88'
        ];

        // Create the pie chart
        const ctx = document.getElementById('categoryPieChart').getContext('2d');
        const categoryPieChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: categories.map(cat => cat.charAt(0).toUpperCase() + cat.slice(1)),
                datasets: [{
                    data: amounts,
                    backgroundColor: backgroundColors.slice(0, categories.length),
                    borderColor: 'rgba(255, 255, 255, 0.5)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: '#fff',
                            padding: 10,
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = Number(context.raw || 0);
                                const total = context.dataset.data.reduce((acc, curr) => acc + Number(curr || 0), 0);
                                const percentage = total > 0 ? Math.round((value / total) * 100) : 0;

                                // Read currency from meta tag injected by server
                                const currencyCode = document.querySelector('meta[name="app-currency"]')?.getAttribute('content') || 'INR';
                                const localeMap = { 'INR': 'en-IN', 'USD': 'en-US', 'EUR': 'de-DE', 'GBP': 'en-GB', 'JPY': 'ja-JP', 'AUD': 'en-AU' };
                                const locale = localeMap[currencyCode] || navigator.language;
                                const formatter = new Intl.NumberFormat(locale, { style: 'currency', currency: currencyCode, maximumFractionDigits: 2 });

                                return `${label}: ${formatter.format(value)} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }
});
