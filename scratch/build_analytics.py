import os

with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Extract the header and footer layout
start_marker = "<!-- DASHBOARD SCROLLABLE AREA -->"
end_marker = "  <script>"

pre = html.split(start_marker)[0]
# Also need to inject Chart.js into head
pre = pre.replace('</head>', '  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>\n</head>')

# Replace active nav
pre = pre.replace(
    '<a href="/" class="flex items-center gap-3 p-3 rounded-xl bg-rose-50 text-fest-rose">',
    '<a href="/" class="flex items-center gap-3 p-3 rounded-xl text-stone-500 hover:bg-stone-100 hover:text-fest-dark transition-colors">'
).replace(
    '<a href="/analytics.html" class="flex items-center gap-3 p-3 rounded-xl text-stone-500 hover:bg-stone-100 hover:text-fest-dark transition-colors">',
    '<a href="/analytics.html" class="flex items-center gap-3 p-3 rounded-xl bg-rose-50 text-fest-rose">'
)

content = """
    <!-- ANALYTICS SCROLLABLE AREA -->
    <div class="flex-1 overflow-y-auto p-8 no-scrollbar relative">
      <div class="flex items-center justify-between mb-8">
        <div>
          <h2 class="text-2xl font-serif font-bold text-fest-dark">Festival Insights</h2>
          <p class="text-stone-500 text-sm mt-1">Real-time attendance metrics and crowd distribution.</p>
        </div>
        <div class="flex items-center gap-3">
          <button class="px-4 py-2 bg-white border border-stone-200 text-stone-600 hover:bg-stone-50 rounded-xl font-bold text-sm shadow-sm transition-colors flex items-center gap-2">
            <i data-lucide="download" class="w-4 h-4"></i> Export CSV
          </button>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        
        <!-- BAR CHART -->
        <div class="glass-card p-6 rounded-3xl border border-stone-200">
          <h3 class="text-lg font-bold text-fest-dark mb-4">Live Area Capacity</h3>
          <div class="relative h-72 w-full">
            <canvas id="capacityChart"></canvas>
          </div>
        </div>

        <!-- RECENT ACTIVITY LOG -->
        <div class="glass-card p-6 rounded-3xl border border-stone-200 flex flex-col h-full max-h-96">
          <h3 class="text-lg font-bold text-fest-dark mb-4">Latest Guest Movements</h3>
          <div id="activity-log" class="space-y-3 overflow-y-auto pr-2 flex-1">
             <div class="text-stone-400 text-center py-10">Loading insights...</div>
          </div>
        </div>
        
      </div>
      
    </div>
  </main>
"""

custom_js = """
  <script>
    let capacityChartInstance = null;

    document.addEventListener('DOMContentLoaded', () => {
      lucide.createIcons();
      fetchAnalyticsData();
      setInterval(fetchAnalyticsData, 5000); // refresh every 5s
    });

    async function fetchAnalyticsData() {
      try {
        const res = await fetch('/api/admin/stats', {
            headers: { 'X-Admin-Key': 'OMNI-SYS-770' }
        });
        if (res.ok) {
          const data = await res.json();
          updateChart(data.zones);
          updateLog(data.recent_logs);
        }
      } catch (err) {
        console.error("Error loading analytics", err);
      }
    }
    
    function updateChart(zones) {
      const labels = zones.map(z => z.zone_name);
      const dataPoints = zones.map(z => z.total_scans);
      
      const ctx = document.getElementById('capacityChart').getContext('2d');
      if (capacityChartInstance) {
          capacityChartInstance.data.labels = labels;
          capacityChartInstance.data.datasets[0].data = dataPoints;
          capacityChartInstance.update();
      } else {
          capacityChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
              labels: labels,
              datasets: [{
                label: 'Total Guests Checked In',
                data: dataPoints,
                backgroundColor: 'rgba(225, 29, 72, 0.8)',
                borderRadius: 8,
              }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: { legend: { display: false } },
              scales: {
                y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.05)' } },
                x: { grid: { display: false } }
              }
            }
          });
      }
    }
    
    function updateLog(logs) {
       const container = document.getElementById('activity-log');
       if(!logs || logs.length === 0) return;
       container.innerHTML = '';
       logs.forEach(log => {
          const isVip = log.role === 'VIP';
          const div = document.createElement('div');
          div.className = "flex items-center gap-4 p-3 rounded-xl bg-stone-50 border border-stone-100";
          div.innerHTML = `
            <div class="w-10 h-10 rounded-full flex items-center justify-center ${isVip ? 'bg-rose-100 text-rose-600' : 'bg-emerald-100 text-emerald-600'}">
              <i data-lucide="${isVip ? 'star' : 'user'}" class="w-5 h-5"></i>
            </div>
            <div class="flex-1">
              <p class="text-sm font-bold text-fest-dark">${log.attendee_name} <span class="text-xs font-normal text-stone-500 ml-1">(${log.role})</span></p>
              <p class="text-xs text-stone-500">Entered <span class="font-bold">${log.zone_name}</span></p>
            </div>
            <div class="text-xs text-stone-400">Just now</div>
          `;
          container.appendChild(div);
       });
       lucide.createIcons();
    }
  </script>
</body>
</html>
"""

with open("static/analytics.html", "w", encoding="utf-8") as f:
    f.write(pre + content + custom_js)

print("done")
