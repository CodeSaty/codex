import os

with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Extract the header and footer layout
start_marker = "<!-- DASHBOARD SCROLLABLE AREA -->"
end_marker = "  <script>"

pre = html.split(start_marker)[0]
post = "  <script>\n" + html.split(end_marker)[1]

# We need to replace the active nav class in the sidebar
pre = pre.replace(
    '<a href="/" class="flex items-center gap-3 p-3 rounded-xl bg-rose-50 text-fest-rose">',
    '<a href="/" class="flex items-center gap-3 p-3 rounded-xl text-stone-500 hover:bg-stone-100 hover:text-fest-dark transition-colors">'
).replace(
    '<a href="/attendees.html" class="flex items-center gap-3 p-3 rounded-xl text-stone-500 hover:bg-stone-100 hover:text-fest-dark transition-colors">',
    '<a href="/attendees.html" class="flex items-center gap-3 p-3 rounded-xl bg-rose-50 text-fest-rose">'
)

content = """
    <!-- ATTENDEES SCROLLABLE AREA -->
    <div class="flex-1 overflow-y-auto p-8 no-scrollbar relative">
      <div class="flex items-center justify-between mb-8">
        <div>
          <h2 class="text-2xl font-serif font-bold text-fest-dark">Guest Directory</h2>
          <p class="text-stone-500 text-sm mt-1">Manage festival attendees and staff access.</p>
        </div>
        <button id="open-add-modal" class="flex items-center gap-2 px-5 py-2.5 bg-rose-600 hover:bg-rose-500 text-white rounded-xl font-bold shadow-sm transition-colors text-sm">
          <i data-lucide="plus" class="w-4 h-4"></i> Register Guest
        </button>
      </div>

      <div class="glass-card rounded-2xl border border-stone-200 overflow-hidden">
        <table class="w-full text-left text-sm text-stone-600">
          <thead class="bg-stone-50 border-b border-stone-200 text-xs uppercase text-stone-500 font-bold">
            <tr>
              <th class="px-6 py-4">Name</th>
              <th class="px-6 py-4">Role</th>
              <th class="px-6 py-4">Ticket Type</th>
              <th class="px-6 py-4">Engagement</th>
              <th class="px-6 py-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody id="attendees-table-body" class="divide-y divide-stone-100">
             <!-- Populated by JS -->
             <tr><td colspan="5" class="px-6 py-8 text-center text-stone-400">Loading guests...</td></tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- ADD ATTENDEE MODAL -->
    <div id="add-modal" class="hidden fixed inset-0 z-50 flex items-center justify-center p-4 bg-stone-900/40 backdrop-blur-sm transition-opacity duration-300">
      <div class="glass-card w-full max-w-md p-6 rounded-3xl border border-stone-200 relative shadow-2xl">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-bold text-fest-dark font-serif">Register New Guest</h2>
          <button id="close-add-modal" class="p-2 text-stone-400 hover:text-stone-600 rounded-full hover:bg-stone-100"><i data-lucide="x" class="w-5 h-5"></i></button>
        </div>
        <form id="add-attendee-form" class="space-y-4 font-medium text-sm">
          <div>
            <label class="block text-stone-600 mb-1">Full Name</label>
            <input type="text" id="att-name" class="w-full border border-stone-200 rounded-xl px-4 py-2.5 focus:ring-2 focus:ring-rose-500 focus:outline-none" required>
          </div>
          <div>
            <label class="block text-stone-600 mb-1">Role</label>
            <select id="att-role" class="w-full border border-stone-200 rounded-xl px-4 py-2.5 focus:ring-2 focus:ring-rose-500 focus:outline-none bg-white">
              <option value="Hacker">Attendee</option>
              <option value="VIP">VIP</option>
              <option value="Organizer">Staff</option>
              <option value="Sponsor">Sponsor</option>
            </select>
          </div>
          <div>
            <label class="block text-stone-600 mb-1">Ticket Type</label>
            <input type="text" id="att-ticket" class="w-full border border-stone-200 rounded-xl px-4 py-2.5 focus:ring-2 focus:ring-rose-500 focus:outline-none" placeholder="e.g. GA, 3-Day Pass" required>
          </div>
          <button type="submit" class="w-full py-3 mt-2 bg-fest-dark hover:bg-stone-800 text-white rounded-xl font-bold transition-colors">Complete Registration</button>
        </form>
      </div>
    </div>
  </main>
"""

custom_js = """
  <script>
    document.addEventListener('DOMContentLoaded', () => {
      lucide.createIcons();
      fetchAttendees();
      
      const modal = document.getElementById('add-modal');
      document.getElementById('open-add-modal').addEventListener('click', () => {
        modal.classList.remove('hidden');
      });
      document.getElementById('close-add-modal').addEventListener('click', () => {
        modal.classList.add('hidden');
      });
      
      document.getElementById('add-attendee-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button[type="submit"]');
        btn.textContent = "Registering...";
        btn.disabled = true;
        
        try {
            const res = await fetch('/register_attendee', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: document.getElementById('att-name').value,
                    role: document.getElementById('att-role').value,
                    ticket_type: document.getElementById('att-ticket').value
                })
            });
            if (res.ok) {
                e.target.reset();
                modal.classList.add('hidden');
                fetchAttendees();
            }
        } catch(err) {
            console.error(err);
            alert("Error registering guest.");
        }
        btn.textContent = "Complete Registration";
        btn.disabled = false;
      });
    });

    async function fetchAttendees() {
      const tbody = document.getElementById('attendees-table-body');
      try {
        const res = await fetch('/api/admin/attendees', {
            headers: { 'X-Admin-Key': 'OMNI-SYS-770' }
        });
        if (res.ok) {
          const data = await res.json();
          tbody.innerHTML = '';
          if (data.attendees.length === 0) {
             tbody.innerHTML = '<tr><td colspan="5" class="px-6 py-8 text-center text-stone-400">No guests found.</td></tr>';
             return;
          }
          data.attendees.forEach(a => {
            const roleCol = a.role === 'VIP' ? 'text-rose-600 bg-rose-50 border-rose-200' : 'text-stone-600 bg-stone-100 border-stone-200';
            const tr = document.createElement('tr');
            tr.innerHTML = `
              <td class="px-6 py-4 font-bold text-fest-dark flex items-center gap-3">
                 <div class="w-8 h-8 rounded-full bg-stone-200 flex items-center justify-center text-xs text-stone-500">${a.name.substring(0,2).toUpperCase()}</div>
                 ${a.name}
              </td>
              <td class="px-6 py-4"><span class="px-2.5 py-1 rounded-lg border text-xs font-bold ${roleCol}">${a.role}</span></td>
              <td class="px-6 py-4">${a.ticket_type}</td>
              <td class="px-6 py-4"><div class="flex items-center gap-1 text-emerald-600 font-bold"><i data-lucide="star" class="w-3.5 h-3.5"></i> ${a.engagement_score}</div></td>
              <td class="px-6 py-4 text-right">
                 <button onclick="deleteAttendee('${a._id}')" class="p-2 text-rose-500 hover:bg-rose-50 rounded-lg transition-colors"><i data-lucide="trash-2" class="w-4 h-4"></i></button>
              </td>
            `;
            tbody.appendChild(tr);
          });
          lucide.createIcons();
        }
      } catch (err) {
        tbody.innerHTML = '<tr><td colspan="5" class="px-6 py-8 text-center text-rose-500">Error loading data</td></tr>';
      }
    }
    
    window.deleteAttendee = async function(id) {
        if(!confirm("Are you sure you want to remove this guest?")) return;
        try {
            await fetch('/api/admin/delete_attendee/' + id, {
                method: 'DELETE',
                headers: { 'X-Admin-Key': 'OMNI-SYS-770' }
            });
            fetchAttendees();
        } catch(err) {
            console.error(err);
        }
    }
  </script>
</body>
</html>
"""

with open("static/attendees.html", "w", encoding="utf-8") as f:
    f.write(pre + content + custom_js)

print("done")
