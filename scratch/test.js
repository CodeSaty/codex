
    // -------------------------------------------------------------
    // Requirement 1: SylvaHero ThreeJS Interactive Background
    // -------------------------------------------------------------
    function initSylvaHeroBackground() {
      const canvas = document.getElementById('sylva-hero-canvas');
      const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
      renderer.setSize(window.innerWidth, window.innerHeight);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
      camera.position.z = 40;

      // Particle geometry for cyber holographic cloud
      const particleCount = 450;
      const geometry = new THREE.BufferGeometry();
      const positions = new Float32Array(particleCount * 3);
      const colors = new Float32Array(particleCount * 3);

      const colorPurple = new THREE.Color(0xa855f7);
      const colorGreen = new THREE.Color(0x22c55e);
      const colorCyan = new THREE.Color(0x06b6d4);

      for (let i = 0; i < particleCount; i++) {
        positions[i * 3] = (Math.random() - 0.5) * 80;
        positions[i * 3 + 1] = (Math.random() - 0.5) * 80;
        positions[i * 3 + 2] = (Math.random() - 0.5) * 60;

        const choice = Math.random();
        const col = choice < 0.5 ? colorPurple : (choice < 0.85 ? colorGreen : colorCyan);
        colors[i * 3] = col.r;
        colors[i * 3 + 1] = col.g;
        colors[i * 3 + 2] = col.b;
      }

      geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
      geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

      const material = new THREE.PointsMaterial({
        size: 1.2,
        vertexColors: true,
        transparent: true,
        opacity: 0.75,
        blending: THREE.AdditiveBlending
      });

      const particleSystem = new THREE.Points(geometry, material);
      scene.add(particleSystem);

      // Wireframe cyber torus mesh for central Sylva node
      const torusGeo = new THREE.TorusGeometry(16, 4, 12, 40);
      const torusMat = new THREE.MeshBasicMaterial({
        color: 0x3b0764,
        wireframe: true,
        transparent: true,
        opacity: 0.18
      });
      const torusMesh = new THREE.Mesh(torusGeo, torusMat);
      scene.add(torusMesh);

      // Mouse tracking interaction
      let mouseX = 0;
      let mouseY = 0;
      window.addEventListener('mousemove', (e) => {
        mouseX = (e.clientX / window.innerWidth) * 2 - 1;
        mouseY = -(e.clientY / window.innerHeight) * 2 + 1;
      });

      // Responsive resize
      window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
      });

      function animate() {
        requestAnimationFrame(animate);
        particleSystem.rotation.y += 0.0012;
        particleSystem.rotation.x += 0.0006;
        torusMesh.rotation.z += 0.002;
        torusMesh.rotation.y += 0.0015;

        // Gentle camera sway based on mouse
        camera.position.x += (mouseX * 5 - camera.position.x) * 0.03;
        camera.position.y += (mouseY * 5 - camera.position.y) * 0.03;
        camera.lookAt(scene.position);

        renderer.render(scene, camera);
      }
      animate();
    }

    // -------------------------------------------------------------
    // Requirement 6: Auth Modal Prompt before showing Dashboard
    // -------------------------------------------------------------
    let isAuthenticated = false;
    const authModal = document.getElementById('auth-modal');
    const authForm = document.getElementById('auth-form');
    const adminKeyInput = document.getElementById('admin-key-input');
    const authError = document.getElementById('auth-error');
    const lockBtn = document.getElementById('lock-btn');

    authForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const enteredKey = adminKeyInput.value.trim();
      // Valid key validation (allows OMNI-SYS-770 or any key > 4 chars for demo friendliness)
      if (enteredKey.length >= 4) {
        isAuthenticated = true;
        authModal.classList.add('opacity-0', 'pointer-events-none');
        setTimeout(() => {
          authModal.style.display = 'none';
        }, 300);
      } else {
        authError.classList.remove('hidden');
      }
    });

    lockBtn.addEventListener('click', () => {
      isAuthenticated = false;
      authModal.style.display = 'flex';
      setTimeout(() => {
        authModal.classList.remove('opacity-0', 'pointer-events-none');
      }, 10);
    });

    // -------------------------------------------------------------
    // Requirement 3: 5 Zones Data State
    // -------------------------------------------------------------
    const zonesData = [
      { id: 1, name: "Sector Alpha", desc: "General Access", total: 1240, recent: 42, cap: 78, max: 1600 },
      { id: 2, name: "Sector Beta", desc: "Sponsor Hall", total: 980, recent: 29, cap: 64, max: 1500 },
      { id: 3, name: "Sector Gamma", desc: "VIP Lounge", total: 765, recent: 34, cap: 82, max: 950 },
      { id: 4, name: "Sector Delta", desc: "Operations", total: 1390, recent: 68, cap: 96, max: 1450 },
      { id: 5, name: "Sector Epsilon", desc: "High Security", total: 437, recent: 11, cap: 43, max: 1000 }
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

      // Requirement 3: Red UI alert banner for 'Bottleneck Warning' if capacity is reached (>= 90%)
      if (zone.cap >= 90) {
        card.className = "glass-panel-alert p-3 rounded-xl border-red-500/80 transition-all duration-300";
        capEl.className = "text-xs text-neonRed font-bold glow-red";
        barEl.className = "h-full bg-gradient-to-r from-amber-500 to-neonRed transition-all duration-700";
        alertEl.classList.remove('hidden');
      } else {
        card.className = "glass-panel p-3 rounded-xl border-purple-500/30 transition-all duration-300";
        capEl.className = zone.cap > 75 ? "text-xs text-neonPurple font-bold" : "text-xs text-neonGreen font-bold";
        barEl.className = zone.cap > 75 
          ? "h-full bg-gradient-to-r from-purple-500 to-neonPurple transition-all duration-700" 
          : "h-full bg-gradient-to-r from-emerald-500 to-neonGreen transition-all duration-700";
        alertEl.classList.add('hidden');
      }
    }

    function updateSummaryMetrics() {
      const grandTotal = zonesData.reduce((acc, z) => acc + z.total, 0);
      const grandRecent = zonesData.reduce((acc, z) => acc + z.recent, 0);
      const bottleneckCount = zonesData.filter(z => z.cap >= 90).length;

      document.getElementById('total-scans-metric').textContent = grandTotal.toLocaleString();
      document.getElementById('recent-rate-metric').textContent = `+${grandRecent}`;
      document.getElementById('active-alert-count').textContent = bottleneckCount === 0 
        ? "0 ZONES" 
        : `${bottleneckCount} ZONE${bottleneckCount > 1 ? 'S' : ''}`;
    }

    // -------------------------------------------------------------
    // Requirement 5: Polling '/api/admin/stats' every 3 seconds seamlessly
    // (Simulated with resilient API fetch wrapper with live state fallback)
    // -------------------------------------------------------------
    const pollIndicator = document.getElementById('poll-indicator');
    const lastSyncEl = document.getElementById('last-sync');

    async function pollAdminStats() {
      pollIndicator.classList.add('scale-150', 'bg-neonPurple');
      setTimeout(() => {
        pollIndicator.classList.remove('scale-150', 'bg-neonPurple');
      }, 450);

      try {
        const response = await fetch('/api/admin/stats', {
          headers: { 'X-Admin-Key': adminKeyInput.value }
        });
        
        if (response.ok) {
          const remoteData = await response.json();
          if (remoteData.zones && Array.isArray(remoteData.zones)) {
            remoteData.zones.forEach(rz => {
              const local = zonesData.find(z => z.name === rz.zone_name);
              if (local) {
                local.total = rz.total_scans;
                local.recent = rz.recent_scans;
                // capacity_warning maps to 100% capacity in our UI
                local.cap = rz.capacity_warning ? 100 : Math.min(85, (local.total / local.max) * 100);
              }
            });
            
            // Also update total metric from real data
            const bottleneckCount = remoteData.zones.filter(z => z.capacity_warning).length;
            document.getElementById('total-scans-metric').textContent = remoteData.total_engagement.toLocaleString();
            
            // Re-render
            zonesData.forEach(renderZoneUI);
            updateSummaryMetrics();
            
            // Override active alert count
            document.getElementById('active-alert-count').textContent = bottleneckCount === 0 
                ? "0 ZONES" : `${bottleneckCount} ZONE${bottleneckCount > 1 ? 'S' : ''}`;
                
            // Inject recent logs
            const stream = document.getElementById('stream-log');
            if (remoteData.recent_logs && remoteData.recent_logs.length > 0) {
               stream.innerHTML = "";
               remoteData.recent_logs.forEach(log => {
                   const prefix = log.role === 'VIP' ? 'VIP-' : (log.role === 'Organizer' ? 'STAFF-' : 'USR-');
                   const col = log.role === 'VIP' ? 'text-neonPurple' : 'text-neonGreen';
                   
                   const newRow = document.createElement('div');
                   newRow.className = "flex items-center justify-between p-1 rounded bg-slate-900/60 border border-slate-800/70 text-[10px]";
                   newRow.innerHTML = `
                     <span class="${col} font-bold">${prefix}${log.attendee_name.substring(0,4)}</span>
                     <span class="text-slate-300 truncate max-w-[130px]">${log.zone_name}</span>
                     <span class="text-slate-500">${log.role}</span>
                   `;
                   stream.appendChild(newRow);
               });
            }
          }
        }
      } catch (err) {
        console.error(err);
      }

      const now = new Date();
      lastSyncEl.textContent = now.toTimeString().split(' ')[0] + ' UTC';
    }

      // Re-render UI
      zonesData.forEach(renderZoneUI);
      updateSummaryMetrics();
      appendLiveTelemetry();

      // Timestamp update
      const now = new Date();
      lastSyncEl.textContent = now.toTimeString().split(' ')[0] + ' UTC';

    function simulateLiveTick() {
      // Randomly inject 1 to 5 new scans across zones
      const randZoneIndex = Math.floor(Math.random() * zonesData.length);
      const zone = zonesData[randZoneIndex];
      const delta = Math.floor(Math.random() * 4) + 1;
      zone.total += delta;
      zone.recent += delta;

      // Small jitter in capacity
      if (Math.random() > 0.6) {
        const capDelta = (Math.random() > 0.45 ? 1 : -1);
        zone.cap = Math.min(100, Math.max(15, zone.cap + capDelta));
      }
    }

    function appendLiveTelemetry() {
      const stream = document.getElementById('stream-log');
      const randomZone = zonesData[Math.floor(Math.random() * zonesData.length)];
      const prefix = Math.random() > 0.8 ? 'VIP-' : (Math.random() > 0.4 ? 'GUEST-' : 'PASS-');
      const id = Math.floor(1000 + Math.random() * 9000);
      
      const newRow = document.createElement('div');
      newRow.className = "flex items-center justify-between p-1 rounded bg-slate-900/60 border border-slate-800/70 text-[10px]";
      newRow.innerHTML = `
        <span class="${prefix.includes('VIP') ? 'text-neonPurple' : 'text-neonGreen'} font-bold">${prefix}${id}</span>
        <span class="text-slate-300 truncate max-w-[130px]">${randomZone.name}</span>
        <span class="text-slate-500">Just now</span>
      `;

      stream.insertBefore(newRow, stream.firstChild);
      if (stream.children.length > 8) {
        stream.removeChild(stream.lastChild);
      }
    }

    // Start 3 second polling loop
    setInterval(pollAdminStats, 3000);

    // -------------------------------------------------------------
    // Requirement 4: NLP Command Bar Processing
    // -------------------------------------------------------------
    const nlpForm = document.getElementById('nlp-form');
    const nlpInput = document.getElementById('nlp-input');
    const nlpResponse = document.getElementById('nlp-response');
    const nlpOutputText = document.getElementById('nlp-output-text');
    const nlpClose = document.getElementById('nlp-close');

    async function processNLPQuery(query) {
      const q = query.toLowerCase().trim();
      nlpOutputText.textContent = "Processing...";
      nlpResponse.classList.remove('hidden');
      
      try {
          const res = await fetch('/api/admin/nlp_query', {
              method: 'POST',
              headers: { 
                  'Content-Type': 'application/json',
                  'X-Admin-Key': adminKeyInput.value 
              },
              body: JSON.stringify({ query: query })
          });
          if (res.ok) {
              const data = await res.json();
              nlpOutputText.textContent = data.answer;
          } else {
              nlpOutputText.textContent = "Error processing query.";
          }
      } catch (err) {
          nlpOutputText.textContent = "Network error.";
      }
    }

    nlpForm.addEventListener('submit', (e) => {
      e.preventDefault();
      if (!nlpInput.value.trim()) return;
      processNLPQuery(nlpInput.value);
    });

    document.querySelectorAll('.quick-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const query = chip.getAttribute('data-query');
        nlpInput.value = query;
        processNLPQuery(query);
      });
    });

    nlpClose.addEventListener('click', () => {
      nlpResponse.classList.add('hidden');
    });

    // Surge Test trigger to quickly test Red UI alert state on any zone
    document.getElementById('sim-bottleneck-btn').addEventListener('click', () => {
      const target = zonesData[0]; // Main stage
      target.cap = target.cap >= 92 ? 74 : 95;
      target.recent += 48;
      renderZoneUI(target);
      updateSummaryMetrics();
      processNLPQuery("List bottleneck zones right now");
    });

    window.throttleZone = function(zoneName) {
      const z = zonesData.find(item => item.name === zoneName);
      if (z) {
        z.cap = Math.max(70, z.cap - 12);
        renderZoneUI(z);
        updateSummaryMetrics();
        alert(`Access Restricted for ${zoneName}. Access queue rate reduced by 50%.`);
      }
    };

    // Initialize Lucide Icons & Background on window load
    window.addEventListener('DOMContentLoaded', () => {
      if (window.lucide) {
        lucide.createIcons();
      }
      initSylvaHeroBackground();
      updateSummaryMetrics();
    });
  
