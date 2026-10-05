import os

file_path = "static/index.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

# The JS logic strictly begins at: "  // -------------------------------------------------------------\n    // Requirement 1:"
js_start_idx = html.find("// Requirement 1: SylvaHero") - 65
if js_start_idx < 0:
    print("Could not find JS start")
    exit(1)

js_code = html[js_start_idx:]
# The end of js_code will include the old </body> and </html> which we want to replace or keep.
# Actually, the file ends with </script>\n</body>\n</html>.
js_code = js_code[:js_code.rfind("</script>")]

# Remove toggle-sound-btn listener from JS to prevent null errors, or just let it fail silently
js_code = js_code.replace(
    "document.getElementById('toggle-sound-btn').addEventListener('click', () => {",
    "const sndBtn = document.getElementById('toggle-sound-btn'); if(sndBtn) sndBtn.addEventListener('click', () => {"
)

# Extract just the <head> exactly (it is clean in the current file because it was at the top)
head_code = html[:html.find("</head>") + 7]

new_body = """
<body class="min-h-screen bg-[#0f172a] text-slate-100 flex overflow-hidden selection:bg-purple-500 selection:text-white">

  <!-- ThreeJS Canvas -->
  <canvas id="sylva-hero-canvas" class="fixed inset-0 pointer-events-none z-0 opacity-45"></canvas>
  <div class="fixed inset-0 grid-bg-line pointer-events-none z-0"></div>

  <!-- AUTH MODAL -->
  <div id="auth-modal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md transition-opacity duration-300">
    <div class="glass-panel w-full max-w-sm p-6 rounded-2xl border border-purple-500/40 relative shadow-2xl overflow-hidden">
      <div class="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-neonGreen via-neonPurple to-neonCyan"></div>
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-2">
          <span class="inline-block w-2.5 h-2.5 rounded-full bg-neonGreen animate-ping"></span>
          <span class="text-xs tracking-widest text-slate-400 uppercase font-sans">SYS_SEC // AUTH GATE</span>
        </div>
        <span class="text-[10px] text-purple-400 bg-purple-950/60 px-2 py-0.5 rounded border border-purple-800">OMNI_v1.0</span>
      </div>
      <div class="text-center mb-6">
        <div class="w-14 h-14 mx-auto rounded-xl bg-purple-900/40 border border-purple-500/40 flex items-center justify-center mb-3 text-neonPurple shadow-[0_0_15px_rgba(168,85,247,0.3)]">
          <i data-lucide="shield-alert" class="w-7 h-7"></i>
        </div>
        <h2 class="text-xl font-bold tracking-wider text-white">ACCESS COMMAND DECK</h2>
      </div>
      <form id="auth-form" class="space-y-4">
        <div>
          <label class="block text-xs uppercase tracking-wider text-slate-400 mb-1">Passkey / Admin Token</label>
          <div class="relative">
            <input type="password" id="admin-key-input" placeholder="ENTER KEY" value="OMNI-SYS-770" class="w-full bg-slate-900/90 border border-purple-500/50 rounded-lg px-3.5 py-2.5 text-sm text-neonGreen font-mono focus:outline-none focus:border-neonGreen" required>
          </div>
          <p id="auth-error" class="hidden text-xs text-neonRed mt-1.5 flex items-center gap-1"><i data-lucide="alert-circle" class="w-3.5 h-3.5"></i> Invalid Credentials.</p>
        </div>
        <button type="submit" class="w-full py-3 px-4 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-semibold text-sm uppercase transition-all shadow-[0_0_20px_rgba(168,85,247,0.4)] flex items-center justify-center gap-2 hover:scale-95">
          <span>Authenticate Session</span>
          <i data-lucide="arrow-right" class="w-4 h-4"></i>
        </button>
      </form>
    </div>
  </div>

  <!-- SIDEBAR -->
  <aside class="w-64 glass-panel border-r border-purple-500/30 flex flex-col z-20 shrink-0 shadow-2xl relative backdrop-blur-2xl">
    <div class="p-6 border-b border-purple-500/30 flex items-center gap-3">
      <div class="w-10 h-10 rounded-xl bg-purple-600/20 flex items-center justify-center text-neonPurple border border-purple-500/50 shadow-[0_0_10px_rgba(168,85,247,0.5)]">
        <i data-lucide="hexagon" class="w-6 h-6"></i>
      </div>
      <div>
        <h1 class="text-base font-bold tracking-wider text-white leading-tight">OMNIEVENT</h1>
        <p class="text-[10px] text-slate-400 uppercase tracking-widest font-sans">Command Center</p>
      </div>
    </div>
    
    <nav class="flex-1 p-4 space-y-2 mt-4 font-sans text-sm">
      <a href="/" class="flex items-center gap-3 p-3 rounded-lg bg-gradient-to-r from-purple-600/40 to-transparent border-l-2 border-neonPurple text-white">
        <i data-lucide="layout-dashboard" class="w-5 h-5 text-neonPurple"></i>
        Dashboard
      </a>
      <a href="/analytics.html" class="flex items-center gap-3 p-3 rounded-lg text-slate-400 hover:bg-slate-800/60 hover:text-white transition-colors">
        <i data-lucide="bar-chart-2" class="w-5 h-5"></i>
        Analytics
      </a>
      <a href="/attendees.html" class="flex items-center gap-3 p-3 rounded-lg text-slate-400 hover:bg-slate-800/60 hover:text-white transition-colors">
        <i data-lucide="users" class="w-5 h-5"></i>
        Database
      </a>
      <a href="/settings.html" class="flex items-center gap-3 p-3 rounded-lg text-slate-400 hover:bg-slate-800/60 hover:text-white transition-colors">
        <i data-lucide="settings" class="w-5 h-5"></i>
        System Settings
      </a>
    </nav>
    
    <div class="p-4 border-t border-purple-500/30">
      <button id="lock-btn" class="w-full flex items-center justify-center gap-2 py-2.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-400 hover:text-white hover:border-purple-500 transition-colors font-sans text-sm">
        <i data-lucide="lock" class="w-4 h-4"></i> Lock System
      </button>
    </div>
  </aside>

  <!-- MAIN CONTENT -->
  <main class="flex-1 flex flex-col relative z-10 h-screen overflow-hidden">
    
    <!-- TOP HEADER -->
    <header class="h-20 glass-panel border-b border-purple-500/30 flex items-center justify-between px-8 shrink-0 backdrop-blur-md">
      
      <!-- NLP Search Form -->
      <form id="nlp-form" class="relative w-full max-w-2xl">
        <div class="absolute inset-y-0 left-0 flex items-center pl-4 pointer-events-none text-neonPurple">
          <i data-lucide="terminal" class="w-5 h-5"></i>
        </div>
        <input type="text" id="nlp-input" class="w-full bg-slate-950/80 border border-purple-500/40 text-slate-200 text-sm rounded-xl focus:ring-1 focus:ring-neonPurple focus:border-neonPurple block pl-12 p-3 font-mono shadow-[inset_0_2px_10px_rgba(0,0,0,0.5)] placeholder-slate-600 transition-all" placeholder="Query Omni Intelligence (e.g. 'How many VIPs are in Sector Beta?')">
        <button type="submit" class="absolute inset-y-1.5 right-1.5 px-4 bg-purple-600 hover:bg-purple-500 text-white rounded-lg text-xs font-bold uppercase tracking-wider transition-colors shadow-sm">
          EXECUTE
        </button>
      </form>
      
      <div class="flex items-center gap-4 font-mono">
        <div class="flex items-center gap-2 text-[11px] px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800">
           <span id="poll-indicator" class="w-2 h-2 rounded-full bg-slate-600 transition-all duration-300"></span>
           <span class="text-slate-400">LAST SYNC:</span>
           <span id="last-sync" class="text-neonGreen">00:00:00 UTC</span>
        </div>
      </div>
    </header>

    <!-- DASHBOARD SCROLLABLE AREA -->
    <div class="flex-1 overflow-y-auto p-8 no-scrollbar">
      
      <!-- NLP Query Response -->
      <div id="nlp-response" class="hidden mb-6 relative group transform transition-all duration-300 origin-top">
        <div class="absolute inset-0 bg-gradient-to-r from-neonPurple to-neonCyan blur-md opacity-30 group-hover:opacity-50 transition-opacity"></div>
        <div class="glass-panel p-5 rounded-xl border border-neonCyan/50 relative overflow-hidden flex items-start justify-between">
          <div class="flex items-start gap-4">
            <div class="p-2 rounded bg-cyan-950/80 border border-cyan-800 text-neonCyan">
              <i data-lucide="bot" class="w-6 h-6"></i>
            </div>
            <div>
              <h3 class="text-xs uppercase tracking-widest text-cyan-400 mb-1 font-bold">Omni Intelligence Response</h3>
              <p id="nlp-output-text" class="text-lg font-mono text-white glow-cyan drop-shadow-md">...</p>
            </div>
          </div>
          <button type="button" id="nlp-close" class="text-slate-400 hover:text-white transition-colors">
            <i data-lucide="x" class="w-5 h-5"></i>
          </button>
        </div>
      </div>

      <!-- Quick Chips -->
      <div class="flex gap-2 mb-8 overflow-x-auto pb-2 no-scrollbar text-xs font-sans">
        <button type="button" class="quick-chip whitespace-nowrap px-4 py-2 rounded-lg bg-slate-800/70 border border-slate-700/80 text-slate-300 hover:border-purple-400 hover:bg-purple-900/30 hover:text-white transition-colors" data-query="How many VIPs in Sector Delta?">
          VIPs in Sector Delta?
        </button>
        <button type="button" class="quick-chip whitespace-nowrap px-4 py-2 rounded-lg bg-slate-800/70 border border-slate-700/80 text-slate-300 hover:border-purple-400 hover:bg-purple-900/30 hover:text-white transition-colors" data-query="List bottleneck zones right now">
          Active Bottlenecks?
        </button>
        <button type="button" class="quick-chip whitespace-nowrap px-4 py-2 rounded-lg bg-slate-800/70 border border-slate-700/80 text-slate-300 hover:border-purple-400 hover:bg-purple-900/30 hover:text-white transition-colors" data-query="Total scans in Sector Beta">
          Sector Beta Scans?
        </button>
      </div>

      <!-- METRICS GRID -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="glass-panel p-5 rounded-xl border border-purple-500/20">
          <h3 class="text-xs uppercase tracking-widest text-slate-400 mb-2 font-sans flex items-center gap-2"><i data-lucide="activity" class="w-4 h-4 text-neonPurple"></i> Global Attendance</h3>
          <p id="total-scans-metric" class="text-4xl font-bold text-white font-mono">4,812</p>
        </div>
        <div class="glass-panel p-5 rounded-xl border border-purple-500/20">
          <h3 class="text-xs uppercase tracking-widest text-slate-400 mb-2 font-sans flex items-center gap-2"><i data-lucide="zap" class="w-4 h-4 text-neonGreen"></i> Flow Rate (per 3m)</h3>
          <p id="recent-rate-metric" class="text-4xl font-bold text-neonGreen font-mono">+184</p>
        </div>
        <div class="glass-panel p-5 rounded-xl border border-red-500/40 shadow-[0_0_15px_rgba(239,68,68,0.1)]">
          <h3 class="text-xs uppercase tracking-widest text-red-300 mb-2 font-sans flex items-center gap-2"><i data-lucide="alert-triangle" class="w-4 h-4 text-neonRed"></i> Alert Status</h3>
          <p id="active-alert-count" class="text-4xl font-bold text-neonRed font-mono">1 ZONE</p>
        </div>
      </div>

      <!-- MAIN SPLIT -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        <!-- ZONES GRID (8 Cols) -->
        <div class="lg:col-span-8">
          <div class="flex items-center justify-between mb-4">
             <h2 class="text-sm uppercase tracking-widest font-bold text-slate-300"><i data-lucide="map" class="inline w-4 h-4 mr-2 text-neonPurple"></i>Sector Telemetry</h2>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <!-- Zone 1 -->
            <div id="zone-card-1" class="glass-panel p-4 rounded-xl border-purple-500/30 transition-all duration-300">
              <div class="flex items-start justify-between">
                <div>
                  <div class="flex items-center gap-2">
                    <span class="w-2.5 h-2.5 rounded-full bg-neonPurple shadow-[0_0_8px_rgba(168,85,247,0.8)]"></span>
                    <h3 class="text-base font-bold text-white tracking-wide">Sector Alpha</h3>
                  </div>
                  <p class="text-xs text-slate-400 font-sans mt-1">General Access</p>
                </div>
                <div class="text-right">
                  <span class="text-lg text-neonPurple font-bold" id="zone-1-capacity">78%</span>
                  <span class="text-[10px] text-slate-500 block uppercase tracking-wider mt-0.5">Capacity</span>
                </div>
              </div>
              <div class="w-full bg-slate-900/80 h-2 rounded-full my-4 overflow-hidden border border-slate-700">
                <div id="zone-1-bar" class="h-full bg-gradient-to-r from-indigo-500 to-neonPurple transition-all duration-700" style="width: 78%"></div>
              </div>
              <div class="grid grid-cols-2 gap-3 text-sm pt-2 border-t border-slate-700/60">
                <div>
                  <span class="text-slate-400 text-[10px] block mb-0.5">TOTAL SCANS:</span>
                  <span id="zone-1-total" class="font-bold text-slate-200">1,240</span>
                </div>
                <div>
                  <span class="text-slate-400 text-[10px] block mb-0.5">RECENT SCANS:</span>
                  <span id="zone-1-recent" class="font-bold text-neonGreen">+42 / 3m</span>
                </div>
              </div>
              <div id="zone-1-alert" class="hidden mt-3 p-2 rounded-lg bg-red-950/70 border border-red-500 text-neonRed flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <i data-lucide="triangle-alert" class="w-4 h-4 text-neonRed animate-bounce"></i>
                  <span class="text-xs font-bold tracking-wider">BOTTLENECK WARNING</span>
                </div>
                <button class="text-[10px] px-3 py-1 bg-red-800/80 hover:bg-red-700 text-white rounded font-sans uppercase font-bold">REROUTE</button>
              </div>
            </div>

            <!-- Zone 2 -->
            <div id="zone-card-2" class="glass-panel p-4 rounded-xl border-purple-500/30 transition-all duration-300">
              <div class="flex items-start justify-between">
                <div>
                  <div class="flex items-center gap-2">
                    <span class="w-2.5 h-2.5 rounded-full bg-neonGreen shadow-[0_0_8px_rgba(34,197,94,0.8)]"></span>
                    <h3 class="text-base font-bold text-white tracking-wide">Sector Beta</h3>
                  </div>
                  <p class="text-xs text-slate-400 font-sans mt-1">Sponsor Hall</p>
                </div>
                <div class="text-right">
                  <span class="text-lg text-neonGreen font-bold" id="zone-2-capacity">64%</span>
                  <span class="text-[10px] text-slate-500 block uppercase tracking-wider mt-0.5">Capacity</span>
                </div>
              </div>
              <div class="w-full bg-slate-900/80 h-2 rounded-full my-4 overflow-hidden border border-slate-700">
                <div id="zone-2-bar" class="h-full bg-gradient-to-r from-emerald-500 to-neonGreen transition-all duration-700" style="width: 64%"></div>
              </div>
              <div class="grid grid-cols-2 gap-3 text-sm pt-2 border-t border-slate-700/60">
                <div>
                  <span class="text-slate-400 text-[10px] block mb-0.5">TOTAL SCANS:</span>
                  <span id="zone-2-total" class="font-bold text-slate-200">980</span>
                </div>
                <div>
                  <span class="text-slate-400 text-[10px] block mb-0.5">RECENT SCANS:</span>
                  <span id="zone-2-recent" class="font-bold text-neonGreen">+29 / 3m</span>
                </div>
              </div>
              <div id="zone-2-alert" class="hidden mt-3 p-2 rounded-lg bg-red-950/70 border border-red-500 text-neonRed flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <i data-lucide="triangle-alert" class="w-4 h-4 text-neonRed animate-bounce"></i>
                  <span class="text-xs font-bold tracking-wider">BOTTLENECK WARNING</span>
                </div>
                <button class="text-[10px] px-3 py-1 bg-red-800/80 hover:bg-red-700 text-white rounded font-sans uppercase font-bold">REROUTE</button>
              </div>
            </div>

            <!-- Zone 3 -->
            <div id="zone-card-3" class="glass-panel p-4 rounded-xl border-purple-500/30 transition-all duration-300">
              <div class="flex items-start justify-between">
                <div>
                  <div class="flex items-center gap-2">
                    <span class="w-2.5 h-2.5 rounded-full bg-neonCyan shadow-[0_0_8px_rgba(6,182,212,0.8)]"></span>
                    <h3 class="text-base font-bold text-white tracking-wide">Sector Gamma</h3>
                  </div>
                  <p class="text-xs text-slate-400 font-sans mt-1">VIP Lounge</p>
                </div>
                <div class="text-right">
                  <span class="text-lg text-neonCyan font-bold" id="zone-3-capacity">82%</span>
                  <span class="text-[10px] text-slate-500 block uppercase tracking-wider mt-0.5">Capacity</span>
                </div>
              </div>
              <div class="w-full bg-slate-900/80 h-2 rounded-full my-4 overflow-hidden border border-slate-700">
                <div id="zone-3-bar" class="h-full bg-gradient-to-r from-blue-500 to-neonCyan transition-all duration-700" style="width: 82%"></div>
              </div>
              <div class="grid grid-cols-2 gap-3 text-sm pt-2 border-t border-slate-700/60">
                <div>
                  <span class="text-slate-400 text-[10px] block mb-0.5">TOTAL SCANS:</span>
                  <span id="zone-3-total" class="font-bold text-slate-200">765</span>
                </div>
                <div>
                  <span class="text-slate-400 text-[10px] block mb-0.5">RECENT SCANS:</span>
                  <span id="zone-3-recent" class="font-bold text-neonCyan">+34 / 3m</span>
                </div>
              </div>
              <div id="zone-3-alert" class="hidden mt-3 p-2 rounded-lg bg-red-950/70 border border-red-500 text-neonRed flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <i data-lucide="triangle-alert" class="w-4 h-4 text-neonRed animate-bounce"></i>
                  <span class="text-xs font-bold tracking-wider">BOTTLENECK WARNING</span>
                </div>
                <button class="text-[10px] px-3 py-1 bg-red-800/80 hover:bg-red-700 text-white rounded font-sans uppercase font-bold">REROUTE</button>
              </div>
            </div>

            <!-- Zone 4 -->
            <div id="zone-card-4" class="glass-panel-alert p-4 rounded-xl border-red-500/80 transition-all duration-300 relative overflow-hidden">
              <div class="absolute inset-0 bg-red-600/10 animate-pulse pointer-events-none"></div>
              <div class="flex items-start justify-between relative z-10">
                <div>
                  <div class="flex items-center gap-2">
                    <span class="w-2.5 h-2.5 rounded-full bg-neonRed shadow-[0_0_10px_rgba(239,68,68,1)] animate-ping"></span>
                    <h3 class="text-base font-bold text-white tracking-wide">Sector Delta</h3>
                  </div>
                  <p class="text-xs text-slate-400 font-sans mt-1">Operations</p>
                </div>
                <div class="text-right">
                  <span class="text-lg text-neonRed font-bold glow-red" id="zone-4-capacity">96%</span>
                  <span class="text-[10px] text-red-400 block uppercase tracking-wider font-bold mt-0.5">OVERFLOW</span>
                </div>
              </div>
              <div class="w-full bg-slate-900/80 h-2 rounded-full my-4 overflow-hidden border border-red-900/60 relative z-10">
                <div id="zone-4-bar" class="h-full bg-gradient-to-r from-orange-500 to-neonRed transition-all duration-700" style="width: 96%"></div>
              </div>
              <div class="grid grid-cols-2 gap-3 text-sm pt-2 border-t border-red-900/40 relative z-10">
                <div>
                  <span class="text-slate-400 text-[10px] block mb-0.5">TOTAL SCANS:</span>
                  <span id="zone-4-total" class="font-bold text-slate-200">1,390</span>
                </div>
                <div>
                  <span class="text-slate-400 text-[10px] block mb-0.5">RECENT SCANS:</span>
                  <span id="zone-4-recent" class="font-bold text-neonRed">+68 / 3m</span>
                </div>
              </div>
              <div id="zone-4-alert" class="mt-3 p-2.5 rounded-lg bg-red-950/90 border border-red-500 text-neonRed flex items-center justify-between relative z-10">
                <div class="flex items-center gap-2">
                  <i data-lucide="triangle-alert" class="w-5 h-5 text-neonRed flex-shrink-0"></i>
                  <div>
                    <span class="text-[11px] font-bold tracking-wider block leading-none">BOTTLENECK WARNING</span>
                    <span class="text-[9px] text-red-300 font-sans mt-0.5 block">Capacity threshold exceeded</span>
                  </div>
                </div>
                <button onclick="throttleZone('Sector Delta')" class="text-[10px] px-3 py-1.5 bg-red-600 hover:bg-red-500 text-white rounded font-sans font-bold uppercase shadow-sm">
                  SLOW ADMIT
                </button>
              </div>
            </div>

            <!-- Zone 5 -->
            <div id="zone-card-5" class="glass-panel p-4 rounded-xl border-purple-500/30 transition-all duration-300">
              <div class="flex items-start justify-between">
                <div>
                  <div class="flex items-center gap-2">
                    <span class="w-2.5 h-2.5 rounded-full bg-neonPurple shadow-[0_0_8px_rgba(168,85,247,0.8)]"></span>
                    <h3 class="text-base font-bold text-white tracking-wide">Sector Epsilon</h3>
                  </div>
                  <p class="text-xs text-slate-400 font-sans mt-1">High Security</p>
                </div>
                <div class="text-right">
                  <span class="text-lg text-neonPurple font-bold" id="zone-5-capacity">43%</span>
                  <span class="text-[10px] text-slate-500 block uppercase tracking-wider mt-0.5">Capacity</span>
                </div>
              </div>
              <div class="w-full bg-slate-900/80 h-2 rounded-full my-4 overflow-hidden border border-slate-700">
                <div id="zone-5-bar" class="h-full bg-gradient-to-r from-purple-500 to-indigo-500 transition-all duration-700" style="width: 43%"></div>
              </div>
              <div class="grid grid-cols-2 gap-3 text-sm pt-2 border-t border-slate-700/60">
                <div>
                  <span class="text-slate-400 text-[10px] block mb-0.5">TOTAL SCANS:</span>
                  <span id="zone-5-total" class="font-bold text-slate-200">437</span>
                </div>
                <div>
                  <span class="text-slate-400 text-[10px] block mb-0.5">RECENT SCANS:</span>
                  <span id="zone-5-recent" class="font-bold text-neonPurple">+11 / 3m</span>
                </div>
              </div>
              <div id="zone-5-alert" class="hidden mt-3 p-2 rounded-lg bg-red-950/70 border border-red-500 text-neonRed flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <i data-lucide="triangle-alert" class="w-4 h-4 text-neonRed animate-bounce"></i>
                  <span class="text-xs font-bold tracking-wider">BOTTLENECK WARNING</span>
                </div>
                <button class="text-[10px] px-3 py-1 bg-red-800/80 hover:bg-red-700 text-white rounded font-sans uppercase font-bold">REROUTE</button>
              </div>
            </div>
            
          </div>
        </div>

        <!-- RIGHT SIDEBAR (Stream Log & Controls) (4 Cols) -->
        <div class="lg:col-span-4 flex flex-col gap-6">
          
          <!-- LIVE INGEST -->
          <div class="glass-panel p-5 rounded-xl border border-purple-500/20 flex-1 flex flex-col min-h-[300px]">
            <div class="flex items-center justify-between mb-4 border-b border-purple-500/20 pb-3">
              <div class="flex items-center gap-2">
                <i data-lucide="radio" class="w-4 h-4 text-neonPurple"></i>
                <span class="text-xs font-bold uppercase tracking-wider text-slate-200">LIVE TELEMETRY INGEST</span>
              </div>
              <span class="text-[10px] text-neonGreen animate-pulse font-mono tracking-widest bg-green-900/30 px-2 py-0.5 rounded">ONLINE</span>
            </div>
            <div id="stream-log" class="space-y-2 overflow-y-auto font-mono text-[11px] text-slate-400 pr-2 flex-1">
              <div class="flex items-center justify-between p-2 rounded bg-slate-900/60 border border-slate-700/50">
                <span class="text-neonGreen font-bold">USR-9481</span>
                <span class="text-slate-300 truncate px-2 text-center">Sector Delta</span>
                <span class="text-slate-500">Just now</span>
              </div>
              <div class="flex items-center justify-between p-2 rounded bg-slate-900/60 border border-slate-700/50">
                <span class="text-neonPurple font-bold">VIP-0021</span>
                <span class="text-slate-300 truncate px-2 text-center">Sector Epsilon</span>
                <span class="text-slate-500">2s ago</span>
              </div>
            </div>
          </div>

          <!-- SYSTEM CONTROLS -->
          <div class="glass-panel p-5 rounded-xl border border-purple-500/20">
            <h3 class="text-xs font-bold uppercase tracking-widest text-slate-400 mb-3 font-sans">System Diagnostics</h3>
            <div class="grid grid-cols-2 gap-3 mb-4 text-xs font-sans">
                <div class="p-3 bg-slate-900 rounded-lg border border-slate-700/50">
                    <span class="block text-slate-500 mb-1">Latency</span>
                    <span class="font-mono text-neonGreen text-sm">18ms</span>
                </div>
                <div class="p-3 bg-slate-900 rounded-lg border border-slate-700/50">
                    <span class="block text-slate-500 mb-1">Db Sync</span>
                    <span class="font-mono text-neonCyan text-sm">OK</span>
                </div>
            </div>
            <button id="sim-bottleneck-btn" class="w-full py-2.5 rounded-lg bg-indigo-900/40 border border-indigo-500/50 hover:bg-indigo-800/60 text-indigo-300 hover:text-white transition-colors font-bold text-xs tracking-wider flex items-center justify-center gap-2">
              <i data-lucide="zap" class="w-4 h-4"></i> EXECUTE SURGE TEST
            </button>
            <!-- Add a hidden toggle sound button to avoid breaking JS -->
            <button id="toggle-sound-btn" class="hidden"></button>
          </div>
          
        </div>
      </div>
      
    </div>
  </main>

  <script>
"""

new_html = head_code + new_body + js_code + "\n</script>\n</body>\n</html>"

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_html)

print("Done")
