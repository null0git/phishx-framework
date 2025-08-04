/**
 * PhishX Analytics Dashboard
 * Handles chart initialization, data loading, and visualization
 */

class AnalyticsDashboard {
    constructor() {
        this.charts = {};
        this.refreshInterval = null;
        this.currentTimeRange = '7';
        this.isLoading = false;
        
        // Chart color schemes
        this.colors = {
            primary: '#0d6efd',
            success: '#198754',
            danger: '#dc3545',
            warning: '#ffc107',
            info: '#0dcaf0',
            secondary: '#6c757d'
        };
        
        this.chartColors = [
            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
            '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
        ];
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.initializeCharts();
        this.loadData();
        this.startAutoRefresh();
    }
    
    setupEventListeners() {
        // Time range selection
        document.querySelectorAll('input[name="timeRange"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.currentTimeRange = e.target.value;
                this.loadData();
            });
        });
        
        // Refresh button
        const refreshBtn = document.querySelector('[data-action="refresh"]');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshData());
        }
        
        // Export button
        const exportBtn = document.querySelector('[data-action="export"]');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportReport());
        }
    }
    
    initializeCharts() {
        this.initCaptureTimelineChart();
        this.initLocationCharts();
        this.initBrowserCharts();
        this.initHourlyActivityChart();
        this.initCampaignPerformanceChart();
    }
    
    initCaptureTimelineChart() {
        const ctx = document.getElementById('captureTimelineChart');
        if (!ctx) return;
        
        this.charts.timeline = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Captured Credentials',
                    data: [],
                    borderColor: this.colors.primary,
                    backgroundColor: this.colors.primary + '20',
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: this.colors.primary,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: 'white' }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: 'white',
                        bodyColor: 'white',
                        borderColor: this.colors.primary,
                        borderWidth: 1
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { 
                            color: 'white',
                            callback: function(value) {
                                return Number.isInteger(value) ? value : '';
                            }
                        },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    },
                    x: {
                        ticks: { color: 'white' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });
    }
    
    initLocationCharts() {
        // Countries doughnut chart
        const countriesCtx = document.getElementById('countriesChart');
        if (countriesCtx) {
            this.charts.countries = new Chart(countriesCtx, {
                type: 'doughnut',
                data: {
                    labels: [],
                    datasets: [{
                        data: [],
                        backgroundColor: this.chartColors,
                        borderWidth: 2,
                        borderColor: '#2d3748'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { 
                                color: 'white',
                                padding: 20,
                                usePointStyle: true
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: 'white',
                            bodyColor: 'white'
                        }
                    }
                }
            });
        }
        
        // Initialize world map
        this.initWorldMap();
    }
    
    initWorldMap() {
        const mapElement = document.getElementById('worldMap');
        if (!mapElement) return;
        
        try {
            this.worldMap = L.map('worldMap', {
                zoomControl: false,
                attributionControl: false
            }).setView([20, 0], 2);
            
            // Dark tile layer
            L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                attribution: '',
                subdomains: 'abcd',
                maxZoom: 19
            }).addTo(this.worldMap);
            
            // Add zoom control to top right
            L.control.zoom({
                position: 'topright'
            }).addTo(this.worldMap);
            
        } catch (error) {
            console.warn('Could not initialize world map:', error);
        }
    }
    
    initBrowserCharts() {
        // Browsers bar chart
        const browsersCtx = document.getElementById('browsersChart');
        if (browsersCtx) {
            this.charts.browsers = new Chart(browsersCtx, {
                type: 'bar',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Users',
                        data: [],
                        backgroundColor: this.colors.info + '80',
                        borderColor: this.colors.info,
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: 'white' }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { 
                                color: 'white',
                                callback: function(value) {
                                    return Number.isInteger(value) ? value : '';
                                }
                            },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' }
                        },
                        x: {
                            ticks: { color: 'white' },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' }
                        }
                    }
                }
            });
        }
        
        // OS pie chart
        const osCtx = document.getElementById('osChart');
        if (osCtx) {
            this.charts.os = new Chart(osCtx, {
                type: 'pie',
                data: {
                    labels: [],
                    datasets: [{
                        data: [],
                        backgroundColor: this.chartColors,
                        borderWidth: 2,
                        borderColor: '#2d3748'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { 
                                color: 'white',
                                padding: 20,
                                usePointStyle: true
                            }
                        }
                    }
                }
            });
        }
    }
    
    initHourlyActivityChart() {
        const ctx = document.getElementById('hourlyActivityChart');
        if (!ctx) return;
        
        this.charts.hourly = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Array.from({length: 24}, (_, i) => `${i.toString().padStart(2, '0')}:00`),
                datasets: [{
                    label: 'Activity',
                    data: new Array(24).fill(0),
                    backgroundColor: this.colors.warning + '80',
                    borderColor: this.colors.warning,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: 'white' }
                    },
                    tooltip: {
                        callbacks: {
                            title: function(context) {
                                return `Hour: ${context[0].label}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { 
                            color: 'white',
                            callback: function(value) {
                                return Number.isInteger(value) ? value : '';
                            }
                        },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    },
                    x: {
                        ticks: { color: 'white' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    }
                }
            }
        });
    }
    
    initCampaignPerformanceChart() {
        // This would be a separate chart for campaign comparison
        // Implementation depends on specific requirements
    }
    
    async loadData() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoading(true);
        
        try {
            await Promise.all([
                this.loadTimelineData(),
                this.loadLocationData(),
                this.loadBrowserData(),
                this.loadHourlyActivity(),
                this.loadSummaryStats(),
                this.loadCampaignPerformance()
            ]);
        } catch (error) {
            console.error('Failed to load analytics data:', error);
            this.showError('Failed to load analytics data');
        } finally {
            this.isLoading = false;
            this.showLoading(false);
        }
    }
    
    async loadTimelineData() {
        try {
            const response = await fetch(`/api/analytics/timeline?range=${this.currentTimeRange}`);
            const data = await response.json();
            
            if (this.charts.timeline) {
                this.charts.timeline.data.labels = data.map(item => {
                    const date = new Date(item.date);
                    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                });
                this.charts.timeline.data.datasets[0].data = data.map(item => item.captures);
                this.charts.timeline.update('none');
            }
        } catch (error) {
            console.error('Failed to load timeline data:', error);
        }
    }
    
    async loadLocationData() {
        try {
            const response = await fetch(`/api/analytics/locations?range=${this.currentTimeRange}`);
            const data = await response.json();
            
            // Update countries chart
            if (this.charts.countries && data.countries) {
                const countries = Object.keys(data.countries).slice(0, 8);
                const counts = Object.values(data.countries).slice(0, 8);
                
                this.charts.countries.data.labels = countries;
                this.charts.countries.data.datasets[0].data = counts;
                this.charts.countries.update('none');
            }
            
            // Update world map
            this.updateWorldMap(data);
            
        } catch (error) {
            console.error('Failed to load location data:', error);
        }
    }
    
    async loadBrowserData() {
        try {
            const response = await fetch(`/api/analytics/browsers?range=${this.currentTimeRange}`);
            const data = await response.json();
            
            // Update browsers chart
            if (this.charts.browsers && data.browsers) {
                const browsers = Object.keys(data.browsers);
                const counts = Object.values(data.browsers);
                
                this.charts.browsers.data.labels = browsers;
                this.charts.browsers.data.datasets[0].data = counts;
                this.charts.browsers.update('none');
            }
            
            // Update OS chart
            if (this.charts.os && data.operating_systems) {
                const os = Object.keys(data.operating_systems);
                const counts = Object.values(data.operating_systems);
                
                this.charts.os.data.labels = os;
                this.charts.os.data.datasets[0].data = counts;
                this.charts.os.update('none');
            }
            
        } catch (error) {
            console.error('Failed to load browser data:', error);
        }
    }
    
    async loadHourlyActivity() {
        try {
            const response = await fetch(`/api/analytics/hourly?range=${this.currentTimeRange}`);
            const data = await response.json();
            
            if (this.charts.hourly) {
                const hourlyData = new Array(24).fill(0);
                data.forEach(item => {
                    hourlyData[item.hour] = item.captures;
                });
                
                this.charts.hourly.data.datasets[0].data = hourlyData;
                this.charts.hourly.update('none');
            }
        } catch (error) {
            console.error('Failed to load hourly activity:', error);
        }
    }
    
    async loadSummaryStats() {
        try {
            const response = await fetch(`/api/analytics/summary?range=${this.currentTimeRange}`);
            const data = await response.json();
            
            this.updateStatCards(data);
        } catch (error) {
            console.error('Failed to load summary stats:', error);
        }
    }
    
    async loadCampaignPerformance() {
        try {
            const response = await fetch('/api/analytics/campaigns');
            const data = await response.json();
            
            this.updateCampaignTable(data);
        } catch (error) {
            console.error('Failed to load campaign performance:', error);
        }
    }
    
    updateStatCards(data) {
        const stats = {
            'totalCaptures': data.total_captures || 0,
            'successRate': (data.success_rate || 0).toFixed(1) + '%',
            'uniqueVictims': data.unique_victims || 0,
            'avgTime': data.avg_time || 'N/A'
        };
        
        Object.entries(stats).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }
    
    updateCampaignTable(data) {
        const tbody = document.getElementById('campaignPerformanceBody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        data.forEach(campaign => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>
                    <strong>${this.escapeHtml(campaign.campaign_name)}</strong>
                    <br><small class="text-muted">ID: ${campaign.campaign_id}</small>
                </td>
                <td>${campaign.total_visits}</td>
                <td>${campaign.credentials_captured}</td>
                <td>${campaign.unique_visitors}</td>
                <td>
                    <span class="badge ${this.getConversionRateBadgeClass(campaign.conversion_rate)}">
                        ${campaign.conversion_rate}%
                    </span>
                </td>
                <td>
                    <span class="badge ${campaign.is_active ? 'bg-success' : 'bg-secondary'}">
                        ${campaign.is_active ? 'Active' : 'Inactive'}
                    </span>
                </td>
            `;
            tbody.appendChild(row);
        });
    }
    
    updateWorldMap(data) {
        if (!this.worldMap) return;
        
        // Clear existing markers
        this.worldMap.eachLayer(layer => {
            if (layer instanceof L.Marker) {
                this.worldMap.removeLayer(layer);
            }
        });
        
        // Add new markers (simplified implementation)
        // In production, you'd use actual country coordinates
        const countryCoords = {
            'United States': [39.8283, -98.5795],
            'United Kingdom': [55.3781, -3.4360],
            'Germany': [51.1657, 10.4515],
            'France': [46.2276, 2.2137],
            'Canada': [56.1304, -106.3468],
            'Australia': [-25.2744, 133.7751],
            'Japan': [36.2048, 138.2529],
            'Brazil': [-14.2350, -51.9253]
        };
        
        if (data.countries) {
            Object.entries(data.countries).forEach(([country, count]) => {
                const coords = countryCoords[country];
                if (coords) {
                    const marker = L.circleMarker(coords, {
                        radius: Math.min(Math.max(count * 2, 5), 20),
                        fillColor: this.colors.danger,
                        color: '#fff',
                        weight: 2,
                        opacity: 1,
                        fillOpacity: 0.7
                    }).addTo(this.worldMap);
                    
                    marker.bindPopup(`${country}: ${count} captures`);
                }
            });
        }
    }
    
    getConversionRateBadgeClass(rate) {
        if (rate >= 5) return 'bg-success';
        if (rate >= 2) return 'bg-warning';
        return 'bg-danger';
    }
    
    showLoading(show) {
        const loadingElements = document.querySelectorAll('.analytics-loading');
        loadingElements.forEach(element => {
            element.style.display = show ? 'block' : 'none';
        });
    }
    
    showError(message) {
        console.error(message);
        // You could show a toast notification here
        if (window.showNotification) {
            window.showNotification(message, 'error');
        }
    }
    
    refreshData() {
        this.loadData();
        if (window.showNotification) {
            window.showNotification('Analytics refreshed', 'success');
        }
    }
    
    exportReport() {
        const timeRange = this.currentTimeRange;
        window.open(`/admin/analytics/export?range=${timeRange}`, '_blank');
    }
    
    startAutoRefresh() {
        // Refresh every 5 minutes
        this.refreshInterval = setInterval(() => {
            if (document.visibilityState === 'visible') {
                this.loadData();
            }
        }, 300000);
    }
    
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
    
    destroy() {
        this.stopAutoRefresh();
        
        // Destroy all charts
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        
        // Remove map
        if (this.worldMap) {
            this.worldMap.remove();
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize analytics dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('captureTimelineChart')) {
        window.analyticsDashboard = new AnalyticsDashboard();
    }
});

// Clean up when leaving the page
window.addEventListener('beforeunload', function() {
    if (window.analyticsDashboard) {
        window.analyticsDashboard.destroy();
    }
});
