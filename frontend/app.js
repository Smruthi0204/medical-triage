const API = 'http://localhost:8081/api';

// ── Current note being viewed ─────────────────────────────────
let currentNoteId = null;

// ── Page Navigation ───────────────────────────────────────────
function showPage(page) {
    document.getElementById('analyzePage').classList.add('hidden');
    document.getElementById('dashboardPage').classList.add('hidden');

    if (page === 'analyze') {
        document.getElementById('analyzePage').classList.remove('hidden');
    } else {
        document.getElementById('dashboardPage').classList.remove('hidden');
        loadDashboard();
    }
}

// ── Analyze Note ──────────────────────────────────────────────
async function analyzeNote() {
    const note      = document.getElementById('noteInput').value.trim();
    const resultDiv = document.getElementById('result');
    const errorDiv  = document.getElementById('error');

    resultDiv.classList.add('hidden');
    errorDiv.classList.add('hidden');

    if (!note) {
        errorDiv.textContent = 'Please enter a clinical note.';
        errorDiv.classList.remove('hidden');
        return;
    }

    try {
        const response = await fetch(`${API}/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ note })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.message || 'Server error: ' + response.status);
        }

        const data = await response.json();

        // Fill result table
        document.getElementById('resId').textContent         = data.id;
        document.getElementById('resSpecialty').textContent  = data.specialty;
        document.getElementById('resConfidence').textContent = (data.confidence * 100).toFixed(1) + '%';
        document.getElementById('resStatus').textContent     = data.status;
        document.getElementById('resCleanText').textContent  = data.cleanText || 'N/A';

        // Fill probabilities table
        const probTable = document.getElementById('probTable');
        probTable.innerHTML = '<tr><th>Specialty</th><th>Probability</th></tr>';
        data.allProbabilities.forEach(p => {
            probTable.innerHTML += `
                <tr>
                    <td>${p.specialty}</td>
                    <td>${(p.probability * 100).toFixed(1)}%</td>
                </tr>`;
        });

        resultDiv.classList.remove('hidden');

    } catch (err) {
        errorDiv.textContent = 'Error: ' + err.message;
        errorDiv.classList.remove('hidden');
    }
}

// ── Load Dashboard ────────────────────────────────────────────
async function loadDashboard() {
    loadStats();
    loadNotes();
}

async function loadStats() {
    try {
        const response = await fetch(`${API}/stats`);
        const data     = await response.json();

        const statsTable = document.getElementById('statsTable');
        statsTable.innerHTML = '<tr><th>Specialty</th><th>Count</th></tr>';
        data.forEach(row => {
            statsTable.innerHTML += `
                <tr>
                    <td>${row[0]}</td>
                    <td>${row[1]}</td>
                </tr>`;
        });
    } catch (err) {
        console.error('Failed to load stats:', err);
    }
}

async function loadNotes() {
    try {
        const response = await fetch(`${API}/notes`);
        const data     = await response.json();

        const notesTable = document.getElementById('notesTable');
        notesTable.innerHTML = `
            <tr>
                <th>ID</th>
                <th>Specialty</th>
                <th>Confidence</th>
                <th>Status</th>
                <th>Created At</th>
                <th>Actions</th>
            </tr>`;

        data.forEach(note => {
            // Store note data on the row using data attributes
            // This avoids issues with special characters breaking onclick
            const rowId = `row-${note.id}`;
            notesTable.innerHTML += `
                <tr id="${rowId}"
                    data-id="${note.id}"
                    data-specialty="${note.specialty}"
                    data-confidence="${note.confidence}"
                    data-status="${note.status}"
                    data-created="${note.createdAt}"
                    data-raw="${encodeURIComponent(note.rawNote || '')}"
                    data-clean="${encodeURIComponent(note.cleanText || '')}">
                    <td>${note.id}</td>
                    <td>${note.specialty}</td>
                    <td>${(note.confidence * 100).toFixed(1)}%</td>
                    <td>${note.status}</td>
                    <td>${new Date(note.createdAt).toLocaleString()}</td>
                    <td>
                        <button onclick="viewNote('${rowId}')">View</button>
                    </td>
                </tr>`;
        });
    } catch (err) {
        console.error('Failed to load notes:', err);
    }
}

// ── Open Modal ────────────────────────────────────────────────
function viewNote(rowId) {
    const row = document.getElementById(rowId);

    currentNoteId = row.dataset.id;

    document.getElementById('mId').textContent        = row.dataset.id;
    document.getElementById('mSpecialty').textContent = row.dataset.specialty;
    document.getElementById('mConfidence').textContent = (parseFloat(row.dataset.confidence) * 100).toFixed(1) + '%';
    document.getElementById('mStatus').textContent    = row.dataset.status;
    document.getElementById('mCreatedAt').textContent = new Date(row.dataset.created).toLocaleString();
    document.getElementById('mRawNote').textContent   = decodeURIComponent(row.dataset.raw);
    document.getElementById('mCleanNote').textContent = decodeURIComponent(row.dataset.clean) || 'N/A';

    document.getElementById('modal').classList.remove('hidden');
}

// ── Close Modal ───────────────────────────────────────────────
function closeModal() {
    document.getElementById('modal').classList.add('hidden');
    currentNoteId = null;
}

// ── Mark Reviewed from Modal ──────────────────────────────────
async function markReviewed() {
    if (!currentNoteId) return;

    await updateStatus(currentNoteId, 'Reviewed');

    // Update status inside modal immediately
    document.getElementById('mStatus').textContent = 'Reviewed';

    // Refresh notes table in background
    loadNotes();
}

// ── Update Status ─────────────────────────────────────────────
async function updateStatus(id, status) {
    try {
        await fetch(`${API}/notes/${id}/status?status=${status}`, {
            method: 'PATCH'
        });
        loadNotes();
    } catch (err) {
        console.error('Failed to update status:', err);
    }
}