document.addEventListener('DOMContentLoaded', function () {
    const ctx = document.getElementById('riskChart').getContext('2d');

    // Example data passed from Flask
    const cognitiveScore = {{ cognitive_total_score | safe }};
    const lifestyleScore = {{ lifestyle_genetic_score | safe }};

    // Chart data and configuration
    const data = {
        labels: ['Cognitive Tests', 'Lifestyle & Genetics'],
        datasets: [
            {
                label: 'Risk Contribution',
                data: [cognitiveScore, lifestyleScore],
                backgroundColor: ['rgba(75, 192, 192, 0.6)', 'rgba(255, 99, 132, 0.6)'],
                borderColor: ['rgba(75, 192, 192, 1)', 'rgba(255, 99, 132, 1)'],
                borderWidth: 1,
            },
        ],
    };

    const config = {
        type: 'doughnut', // Can be 'bar', 'line', etc.
        data: data,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                },
            },
        },
    };

    // Render the chart
    new Chart(ctx, config);
});
