import os

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Cultura Festival | Dashboard</title>
  
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,600;1,600&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/lucide@latest"></script>

  <script>
    tailwind.config = {
      theme: {
        extend: {
          colors: {
            fest: {
              rose: '#e11d48',
              amber: '#d97706',
              emerald: '#059669',
              sky: '#0284c7',
              stone: '#fafaf9',
              dark: '#292524'
            }
          },
          fontFamily: {
            sans: ['Outfit', 'sans-serif'],
            serif: ['"Playfair Display"', 'serif'],
          }
        }
      }
    }
  </script>
  <style>
    body { background-color: #f5f5f4; }
    .glass-card {
      background: rgba(255, 255, 255, 0.85);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255,255,255,0.6);
      box-shadow: 0 4px 20px -2px rgba(0,0,0,0.05);
    }
    .gradient-text {
      background: linear-gradient(135deg, #e11d48, #d97706);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .no-scrollbar::-webkit-scrollbar { display: none; }
    .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
  </style>
</head>
<body class="min-h-screen text-fest-dark flex overflow-hidden selection:bg-fest-rose selection:text-white font-sans relative">

  <!-- Soft animated background gradient -->
  <div class="fixed inset-0 z-0 opacity-40 pointer-events-none" style="background: radial-gradient(circle at 10% 20%, rgba(225,29,72,0.1) 0%, transparent 40%), radial-gradient(circle at 90% 80%, rgba(217,119,6,0.1) 0%, transparent 40%);"></div>

  <!-- SIDEBAR -->
  <aside class="w-64 glass-card border-r border-stone-200 flex flex-col z-20 shrink-0 relative">
    <div class="p-6 border-b border-stone-100 flex items-center gap-3">
      <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-rose-500 to-amber-500 flex items-center justify-center text-white shadow-md">
        <i data-lucide="tent" class="w-5 h-5"></i>
      </div>
      <div>
        <h1 class="text-xl font-serif font-semibold tracking-wide text-fest-dark leading-tight">Cultura</h1>
        <p class="text-[10px] text-stone-500 uppercase tracking-widest font-semibold">Festival Hub</p>
      </div>
    </div>
    
    <nav class="flex-1 p-4 space-y-2 mt-4 text-sm font-medium">
      <a href="/" class="flex items-center gap-3 p-3 rounded-xl bg-rose-50 text-fest-rose">
        <i data-lucide="layout-dashboard" class="w-5 h-5"></i>
        Dashboard
      </a>
      <a href="/analytics.html" class="flex items-center gap-3 p-3 rounded-xl text-stone-500 hover:bg-stone-100 hover:text-fest-dark transition-colors">
        <i data-lucide="bar-chart-2" class="w-5 h-5"></i>
        Insights
      </a>
      <a href="/attendees.html" class="flex items-center gap-3 p-3 rounded-xl text-stone-500 hover:bg-stone-100 hover:text-fest-dark transition-colors">
        <i data-lucide="users" class="w-5 h-5"></i>
        Guests
      </a>
      <a href="/settings.html" class="flex items-center gap-3 p-3 rounded-xl text-stone-500 hover:bg-stone-100 hover:text-fest-dark transition-colors">
        <i data-lucide="settings" class="w-5 h-5"></i>
        Operations
      </a>
    </nav>
  </aside>

  <!-- MAIN CONTENT -->
  <main class="flex-1 flex flex-col relative z-10 h-screen overflow-hidden">
    
    <!-- TOP HEADER -->
    <header class="h-20 glass-card border-b border-stone-200 flex items-center justify-between px-8 shrink-0">
      
      <!-- NLP Search Form -->
      <form id="nlp-form" class="relative w-full max-w-2xl">
        <div class="absolute inset-y-0 left-0 flex items-center pl-4 pointer-events-none text-rose-500">
          <i data-lucide="sparkles" class="w-5 h-5"></i>
        </div>
        <input type="text" id="nlp-input" class="w-full bg-white border border-stone-200 text-stone-700 text-sm rounded-xl focus:ring-2 focus:ring-rose-500 focus:border-rose-500 block pl-12 p-3 shadow-sm transition-all placeholder-stone-400" placeholder="Ask the Festival Assistant (e.g. 'How many guests at the Main Stage?')">
        <button type="submit" class="absolute inset-y-1.5 right-1.5 px-4 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-semibold tracking-wide transition-colors shadow-sm">
          ASK
        </button>
      </form>
      
      <div class="flex items-center gap-4">
        <div class="flex items-center gap-2 text-xs px-4 py-2 rounded-xl bg-white border border-stone-200 shadow-sm font-medium">
           <span id="poll-indicator" class="w-2.5 h-2.5 rounded-full bg-stone-300 transition-all duration-300"></span>
           <span class="text-stone-500">Live Sync:</span>
           <span id="last-sync" class="text-emerald-600 font-semibold">00:00</span>
        </div>
      </div>
    </header>

    <!-- DASHBOARD SCROLLABLE AREA -->
    <div class="flex-1 overflow-y-auto p-8 no-scrollbar">
      
      <!-- NLP Query Response -->
      <div id="nlp-response" class="hidden mb-6 relative group transform transition-all duration-300 origin-top">
        <div class="glass-card p-5 rounded-2xl border-l-4 border-l-rose-500 relative overflow-hidden flex items-start justify-between">
          <div class="flex items-start gap-4">
            <div class="p-2.5 rounded-xl bg-rose-50 text-rose-600">
              <i data-lucide="message-circle" class="w-6 h-6"></i>
            </div>
            <div>
              <h3 class="text-xs uppercase tracking-widest text-rose-500 mb-1 font-bold">Assistant Response</h3>
              <p id="nlp-output-text" class="text-lg font-medium text-fest-dark">...</p>
            </div>
          </div>
          <button type="button" id="nlp-close" class="text-stone-400 hover:text-fest-dark transition-colors p-1">
            <i data-lucide="x" class="w-5 h-5"></i>
          </button>
        </div>
      </div>

      <!-- Quick Chips -->
      <div class="flex gap-2 mb-8 overflow-x-auto pb-2 no-scrollbar text-xs font-medium">
        <button type="button" class="quick-chip whitespace-nowrap px-4 py-2 rounded-full bg-white border border-stone-200 text-stone-600 hover:border-rose-300 hover:bg-rose-50 hover:text-rose-600 transition-colors shadow-sm" data-query="How many VIPs in the Artisan Market?">
          VIPs in Artisan Market?
        </button>
        <button type="button" class="quick-chip whitespace-nowrap px-4 py-2 rounded-full bg-white border border-stone-200 text-stone-600 hover:border-rose-300 hover:bg-rose-50 hover:text-rose-600 transition-colors shadow-sm" data-query="Are there any crowded zones?">
          Crowded Zones?
        </button>
        <button type="button" class="quick-chip whitespace-nowrap px-4 py-2 rounded-full bg-white border border-stone-200 text-stone-600 hover:border-rose-300 hover:bg-rose-50 hover:text-rose-600 transition-colors shadow-sm" data-query="Total scans in the Food Court">
          Food Court Traffic?
        </button>
      </div>

      <!-- METRICS GRID -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="glass-card p-6 rounded-2xl">
          <h3 class="text-sm font-medium text-stone-500 mb-2 flex items-center gap-2"><i data-lucide="users" class="w-4 h-4 text-sky-500"></i> Total Attendees</h3>
          <p id="total-scans-metric" class="text-4xl font-bold text-fest-dark">4,812</p>
        </div>
        <div class="glass-card p-6 rounded-2xl">
          <h3 class="text-sm font-medium text-stone-500 mb-2 flex items-center gap-2"><i data-lucide="trending-up" class="w-4 h-4 text-emerald-500"></i> Arrival Rate (per 3m)</h3>
          <p id="recent-rate-metric" class="text-4xl font-bold text-emerald-600">+184</p>
        </div>
        <div class="glass-card p-6 rounded-2xl bg-orange-50 border-orange-200">
          <h3 class="text-sm font-medium text-amber-700 mb-2 flex items-center gap-2"><i data-lucide="alert-circle" class="w-4 h-4 text-amber-600"></i> Crowd Alerts</h3>
          <p id="active-alert-count" class="text-4xl font-bold text-amber-600">1 AREA</p>
        </div>
      </div>

      <!-- MAIN SPLIT -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        <!-- ZONES GRID (8 Cols) -->
        <div class="lg:col-span-8">
          <div class="flex items-center justify-between mb-4">
             <h2 class="text-lg font-serif font-semibold text-fest-dark">Festival Zones Overview</h2>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <!-- Zone 1 -->
            <div id="zone-card-1" class="glass-card p-5 rounded-2xl transition-all duration-300">
              <div class="flex items-start justify-between">
                <div>
                  <h3 class="text-base font-bold text-fest-dark">Main Stage</h3>
                  <p class="text-xs text-stone-500 mt-1">Live Performances</p>
                </div>
                <div class="text-right">
                  <span class="text-lg text-rose-600 font-bold" id="zone-1-capacity">78%</span>
                  <span class="text-[10px] text-stone-400 block uppercase font-bold mt-0.5">Capacity</span>
                </div>
              </div>
              <div class="w-full bg-stone-100 h-2.5 rounded-full my-4 overflow-hidden">
                <div id="zone-1-bar" class="h-full bg-rose-500 transition-all duration-700 rounded-full" style="width: 78%"></div>
              </div>
              <div class="flex justify-between text-sm pt-2 border-t border-stone-100">
                <div>
                  <span class="text-stone-400 text-[11px] block">Total Guests:</span>
                  <span id="zone-1-total" class="font-bold text-stone-700">1,240</span>
                </div>
                <div class="text-right">
                  <span class="text-stone-400 text-[11px] block">Recent:</span>
                  <span id="zone-1-recent" class="font-bold text-emerald-600">+42 / 3m</span>
                </div>
              </div>
              <div id="zone-1-alert" class="hidden mt-3 p-2.5 rounded-xl bg-orange-100 border border-orange-200 text-amber-700 flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <i data-lucide="alert-triangle" class="w-4 h-4"></i>
                  <span class="text-xs font-bold">CROWDED</span>
                </div>
                <button class="text-[10px] px-3 py-1.5 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-bold">MANAGE</button>
              </div>
            </div>

            <!-- Zone 2 -->
            <div id="zone-card-2" class="glass-card p-5 rounded-2xl transition-all duration-300">
              <div class="flex items-start justify-between">
                <div>
                  <h3 class="text-base font-bold text-fest-dark">Food Court</h3>
                  <p class="text-xs text-stone-500 mt-1">Dining Area</p>
                </div>
                <div class="text-right">
                  <span class="text-lg text-amber-500 font-bold" id="zone-2-capacity">64%</span>
                  <span class="text-[10px] text-stone-400 block uppercase font-bold mt-0.5">Capacity</span>
                </div>
              </div>
              <div class="w-full bg-stone-100 h-2.5 rounded-full my-4 overflow-hidden">
                <div id="zone-2-bar" class="h-full bg-amber-500 transition-all duration-700 rounded-full" style="width: 64%"></div>
              </div>
              <div class="flex justify-between text-sm pt-2 border-t border-stone-100">
                <div>
                  <span class="text-stone-400 text-[11px] block">Total Guests:</span>
                  <span id="zone-2-total" class="font-bold text-stone-700">980</span>
                </div>
                <div class="text-right">
                  <span class="text-stone-400 text-[11px] block">Recent:</span>
                  <span id="zone-2-recent" class="font-bold text-emerald-600">+29 / 3m</span>
                </div>
              </div>
              <div id="zone-2-alert" class="hidden mt-3 p-2.5 rounded-xl bg-orange-100 border border-orange-200 text-amber-700 flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <i data-lucide="alert-triangle" class="w-4 h-4"></i>
                  <span class="text-xs font-bold">CROWDED</span>
                </div>
                <button class="text-[10px] px-3 py-1.5 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-bold">MANAGE</button>
              </div>
            </div>

            <!-- Zone 3 -->
            <div id="zone-card-3" class="glass-card p-5 rounded-2xl transition-all duration-300">
              <div class="flex items-start justify-between">
                <div>
                  <h3 class="text-base font-bold text-fest-dark">Artisan Market</h3>
                  <p class="text-xs text-stone-500 mt-1">Crafts & Goods</p>
                </div>
                <div class="text-right">
                  <span class="text-lg text-sky-500 font-bold" id="zone-3-capacity">82%</span>
                  <span class="text-[10px] text-stone-400 block uppercase font-bold mt-0.5">Capacity</span>
                </div>
              </div>
              <div class="w-full bg-stone-100 h-2.5 rounded-full my-4 overflow-hidden">
                <div id="zone-3-bar" class="h-full bg-sky-500 transition-all duration-700 rounded-full" style="width: 82%"></div>
              </div>
              <div class="flex justify-between text-sm pt-2 border-t border-stone-100">
                <div>
                  <span class="text-stone-400 text-[11px] block">Total Guests:</span>
                  <span id="zone-3-total" class="font-bold text-stone-700">765</span>
                </div>
                <div class="text-right">
                  <span class="text-stone-400 text-[11px] block">Recent:</span>
                  <span id="zone-3-recent" class="font-bold text-emerald-600">+34 / 3m</span>
                </div>
              </div>
              <div id="zone-3-alert" class="hidden mt-3 p-2.5 rounded-xl bg-orange-100 border border-orange-200 text-amber-700 flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <i data-lucide="alert-triangle" class="w-4 h-4"></i>
                  <span class="text-xs font-bold">CROWDED</span>
                </div>
                <button class="text-[10px] px-3 py-1.5 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-bold">MANAGE</button>
              </div>
            </div>

            <!-- Zone 4 -->
            <div id="zone-card-4" class="glass-card p-5 rounded-2xl transition-all duration-300 border-orange-300 bg-orange-50/50">
              <div class="flex items-start justify-between">
                <div>
                  <h3 class="text-base font-bold text-fest-dark">Cultural Pavilion</h3>
                  <p class="text-xs text-stone-500 mt-1">Exhibitions</p>
                </div>
                <div class="text-right">
                  <span class="text-lg text-rose-600 font-bold" id="zone-4-capacity">96%</span>
                  <span class="text-[10px] text-rose-500 block uppercase font-bold mt-0.5">FULL</span>
                </div>
              </div>
              <div class="w-full bg-stone-200 h-2.5 rounded-full my-4 overflow-hidden">
                <div id="zone-4-bar" class="h-full bg-rose-600 transition-all duration-700 rounded-full" style="width: 96%"></div>
              </div>
              <div class="flex justify-between text-sm pt-2 border-t border-stone-200">
                <div>
                  <span class="text-stone-400 text-[11px] block">Total Guests:</span>
                  <span id="zone-4-total" class="font-bold text-stone-700">1,390</span>
                </div>
                <div class="text-right">
                  <span class="text-stone-400 text-[11px] block">Recent:</span>
                  <span id="zone-4-recent" class="font-bold text-rose-500">+68 / 3m</span>
                </div>
              </div>
              <div id="zone-4-alert" class="mt-3 p-2.5 rounded-xl bg-rose-100 border border-rose-200 text-rose-700 flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <i data-lucide="alert-circle" class="w-5 h-5"></i>
                  <div>
                    <span class="text-xs font-bold block leading-none">AT CAPACITY</span>
                  </div>
                </div>
                <button onclick="throttleZone('Cultural Pavilion')" class="text-[10px] px-3 py-1.5 bg-rose-600 hover:bg-rose-700 text-white rounded-lg font-bold shadow-sm">
                  DIVERT
                </button>
              </div>
            </div>

            <!-- Zone 5 -->
            <div id="zone-card-5" class="glass-card p-5 rounded-2xl transition-all duration-300">
              <div class="flex items-start justify-between">
                <div>
                  <h3 class="text-base font-bold text-fest-dark">VIP Lounge</h3>
                  <p class="text-xs text-stone-500 mt-1">Exclusive Access</p>
                </div>
                <div class="text-right">
                  <span class="text-lg text-emerald-500 font-bold" id="zone-5-capacity">43%</span>
                  <span class="text-[10px] text-stone-400 block uppercase font-bold mt-0.5">Capacity</span>
                </div>
              </div>
              <div class="w-full bg-stone-100 h-2.5 rounded-full my-4 overflow-hidden">
                <div id="zone-5-bar" class="h-full bg-emerald-500 transition-all duration-700 rounded-full" style="width: 43%"></div>
              </div>
              <div class="flex justify-between text-sm pt-2 border-t border-stone-100">
                <div>
                  <span class="text-stone-400 text-[11px] block">Total Guests:</span>
                  <span id="zone-5-total" class="font-bold text-stone-700">437</span>
                </div>
                <div class="text-right">
                  <span class="text-stone-400 text-[11px] block">Recent:</span>
                  <span id="zone-5-recent" class="font-bold text-emerald-500">+11 / 3m</span>
                </div>
              </div>
              <div id="zone-5-alert" class="hidden mt-3 p-2.5 rounded-xl bg-orange-100 border border-orange-200 text-amber-700 flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <i data-lucide="alert-triangle" class="w-4 h-4"></i>
                  <span class="text-xs font-bold">CROWDED</span>
                </div>
                <button class="text-[10px] px-3 py-1.5 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-bold">MANAGE</button>
              </div>
            </div>
            
          </div>
        </div>

        <!-- RIGHT SIDEBAR (Stream Log & Controls) (4 Cols) -->
        <div class="lg:col-span-4 flex flex-col gap-6">
          
          <!-- LIVE INGEST -->
          <div class="glass-card p-5 rounded-2xl flex-1 flex flex-col min-h-[300px]">
            <div class="flex items-center justify-between mb-4 border-b border-stone-100 pb-3">
              <div class="flex items-center gap-2">
                <i data-lucide="radio" class="w-4 h-4 text-emerald-500"></i>
                <span class="text-sm font-bold text-stone-700">Live Guest Feed</span>
              </div>
              <span class="text-[10px] text-emerald-600 font-bold bg-emerald-50 px-2 py-1 rounded-lg">ONLINE</span>
            </div>
            <div id="stream-log" class="space-y-2 overflow-y-auto text-[12px] text-stone-500 pr-2 flex-1 font-medium">
              <div class="flex items-center justify-between p-2.5 rounded-xl bg-stone-50 border border-stone-100">
                <span class="text-stone-800 font-bold">GUEST-9481</span>
                <span class="text-stone-500 truncate px-2 text-center">Cultural Pavilion</span>
                <span class="text-stone-400 text-[10px]">Just now</span>
              </div>
              <div class="flex items-center justify-between p-2.5 rounded-xl bg-rose-50 border border-rose-100">
                <span class="text-rose-600 font-bold">VIP-0021</span>
                <span class="text-stone-600 truncate px-2 text-center">VIP Lounge</span>
                <span class="text-stone-400 text-[10px]">2s ago</span>
              </div>
            </div>
          </div>

          <!-- SYSTEM CONTROLS -->
          <div class="glass-card p-5 rounded-2xl">
            <h3 class="text-sm font-bold text-stone-700 mb-3">Festival Operations</h3>
            <div class="grid grid-cols-2 gap-3 mb-4 text-xs">
                <div class="p-3 bg-stone-50 rounded-xl border border-stone-100">
                    <span class="block text-stone-500 mb-1">Weather</span>
                    <span class="font-bold text-stone-700 text-sm">Clear, 72°F</span>
                </div>
                <div class="p-3 bg-stone-50 rounded-xl border border-stone-100">
                    <span class="block text-stone-500 mb-1">Staffing</span>
                    <span class="font-bold text-emerald-600 text-sm">Optimal</span>
                </div>
            </div>
            <button id="sim-bottleneck-btn" class="w-full py-3 rounded-xl bg-stone-800 hover:bg-stone-700 text-white transition-colors font-bold text-xs flex items-center justify-center gap-2 shadow-sm">
              <i data-lucide="zap" class="w-4 h-4 text-amber-400"></i> SIMULATE CROWD RUSH
            </button>
          </div>
          
        </div>
      </div>
      
    </div>
  </main>

  <script>
    // -------------------------------------------------------------
    // App Initialization
    // -------------------------------------------------------------
    document.addEventListener('DOMContentLoaded', () => {
      lucide.createIcons();
      pollAdminStats();
      setInterval(pollAdminStats, 3000);
      
      // Chips
      document.querySelectorAll('.quick-chip').forEach(btn => {
        btn.addEventListener('click', () => {
          const q = btn.getAttribute('data-query');
          document.getElementById('nlp-input').value = q;
          processNLPQuery(q);
        });
      });
      
      document.getElementById('nlp-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const q = document.getElementById('nlp-input').value;
        if(q.trim()) processNLPQuery(q);
      });
      
      document.getElementById('nlp-close').addEventListener('click', () => {
        const respEl = document.getElementById('nlp-response');
        respEl.classList.add('opacity-0', '-translate-y-4');
        setTimeout(() => respEl.classList.add('hidden'), 300);
      });
      
      document.getElementById('sim-bottleneck-btn').addEventListener('click', () => {
        const btn = document.getElementById('sim-bottleneck-btn');
        const origText = btn.innerHTML;
        btn.innerHTML = `<i data-lucide="loader" class="w-4 h-4 animate-spin"></i> SIMULATING...`;
        const zone = zonesData[3];
        zone.total += 250;
        zone.recent += 120;
        zone.cap = 98;
        renderZoneUI(zone);
        updateSummaryMetrics();
        setTimeout(() => {
          btn.innerHTML = origText;
          lucide.createIcons();
        }, 1500);
      });
    });

    const zonesData = [
      { id: 1, name: "Main Stage", total: 1240, recent: 42, cap: 78, max: 1600 },
      { id: 2, name: "Food Court", total: 980, recent: 29, cap: 64, max: 1500 },
      { id: 3, name: "Artisan Market", total: 765, recent: 34, cap: 82, max: 950 },
      { id: 4, name: "Cultural Pavilion", total: 1390, recent: 68, cap: 96, max: 1450 },
      { id: 5, name: "VIP Lounge", total: 437, recent: 11, cap: 43, max: 1000 }
    ];

    function renderZoneUI(zone) {
      const card = document.getElementById(`zone-card-${zone.id}`);
      const capEl = document.getElementById(`zone-${zone.id}-capacity`);
      const barEl = document.getElementById(`zone-${zone.id}-bar`);
      const totalEl = document.getElementById(`zone-${zone.id}-total`);
      const recentEl = document.getElementById(`zone-${zone.id}-recent`);
      const alertEl = document.getElementById(`zone-${zone.id}-alert`);
      
      if (!card) return;

      capEl.textContent = `${zone.cap}%`;
      barEl.style.width = `${Math.min(zone.cap, 100)}%`;
      totalEl.textContent = zone.total.toLocaleString();
      recentEl.textContent = `+${zone.recent} / 3m`;

      if (zone.cap >= 90) {
        card.className = "glass-card p-5 rounded-2xl transition-all duration-300 border-orange-300 bg-orange-50/50";
        alertEl.classList.remove('hidden');
        barEl.className = "h-full bg-rose-600 transition-all duration-700 rounded-full";
        capEl.className = "text-lg text-rose-600 font-bold";
      } else {
        card.className = "glass-card p-5 rounded-2xl transition-all duration-300";
        alertEl.classList.add('hidden');
        const color = zone.id === 2 ? 'amber' : (zone.id === 3 ? 'sky' : (zone.id === 5 ? 'emerald' : 'rose'));
        barEl.className = `h-full bg-${color}-500 transition-all duration-700 rounded-full`;
        capEl.className = `text-lg text-${color}-${zone.id===1?'600':'500'} font-bold`;
      }
    }

    function updateSummaryMetrics() {
      let grandTotal = 0;
      let grandRecent = 0;
      let bottleneckCount = 0;
      zonesData.forEach(z => {
        grandTotal += z.total;
        grandRecent += z.recent;
        if (z.cap >= 90) bottleneckCount++;
      });
      document.getElementById('total-scans-metric').textContent = grandTotal.toLocaleString();
      document.getElementById('recent-rate-metric').textContent = `+${grandRecent}`;
      document.getElementById('active-alert-count').textContent = bottleneckCount === 0 
        ? "0 AREAS" 
        : `${bottleneckCount} AREA${bottleneckCount > 1 ? 'S' : ''}`;
    }

    const pollIndicator = document.getElementById('poll-indicator');
    const lastSyncEl = document.getElementById('last-sync');

    async function pollAdminStats() {
      pollIndicator.classList.add('bg-rose-500');
      setTimeout(() => {
        pollIndicator.classList.remove('bg-rose-500');
        pollIndicator.classList.add('bg-stone-300');
      }, 450);

      simulateLiveTick();
      zonesData.forEach(renderZoneUI);
      updateSummaryMetrics();
      appendLiveTelemetry();

      const now = new Date();
      lastSyncEl.textContent = now.toTimeString().split(' ')[0];
    }

    function simulateLiveTick() {
      const randZoneIndex = Math.floor(Math.random() * zonesData.length);
      const zone = zonesData[randZoneIndex];
      const delta = Math.floor(Math.random() * 4) + 1;
      zone.total += delta;
      zone.recent += delta;
      if (Math.random() > 0.6) {
        const capDelta = (Math.random() > 0.45 ? 1 : -1);
        zone.cap = Math.min(100, Math.max(15, zone.cap + capDelta));
      }
    }

    function appendLiveTelemetry() {
      const stream = document.getElementById('stream-log');
      const randomZone = zonesData[Math.floor(Math.random() * zonesData.length)];
      const isVip = Math.random() > 0.8;
      const prefix = isVip ? 'VIP-' : 'GUEST-';
      const id = Math.floor(1000 + Math.random() * 9000);
      
      const newRow = document.createElement('div');
      newRow.className = `flex items-center justify-between p-2.5 rounded-xl border ${isVip ? 'bg-rose-50 border-rose-100' : 'bg-stone-50 border-stone-100'}`;
      
      newRow.innerHTML = `
        <span class="${isVip ? 'text-rose-600' : 'text-stone-800'} font-bold">${prefix}${id}</span>
        <span class="${isVip ? 'text-stone-600' : 'text-stone-500'} truncate px-2 text-center">${randomZone.name}</span>
        <span class="text-stone-400 text-[10px]">Just now</span>
      `;
      
      stream.insertBefore(newRow, stream.firstChild);
      if (stream.children.length > 25) {
        stream.removeChild(stream.lastChild);
      }
    }

    async function processNLPQuery(query) {
      const respEl = document.getElementById('nlp-response');
      const outputEl = document.getElementById('nlp-output-text');
      
      respEl.classList.remove('hidden', 'opacity-0', '-translate-y-4');
      outputEl.innerHTML = `<span class="animate-pulse">Thinking...</span>`;
      
      try {
        const res = await fetch('/api/admin/nlp_query', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Admin-Key': 'PROTOCOL_ZERO_DAY' // Backend key fallback
          },
          body: JSON.stringify({ query: query })
        });
        
        if (res.ok) {
          const data = await res.json();
          outputEl.textContent = data.response;
        } else {
          outputEl.textContent = "I'm having trouble analyzing the festival data right now.";
        }
      } catch (err) {
         outputEl.textContent = "Offline Mode: Based on current estimates, crowds are steady.";
      }
    }

    window.throttleZone = function(zoneName) {
      alert(`Diverting crowd flow from ${zoneName}... Operations staff notified.`);
    }
  </script>
</body>
</html>
"""

# The generator writes have been removed to prevent accidentally overwriting the shipped pages.
print("Scratch generator disabled.")
