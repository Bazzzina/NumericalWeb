/**
 * Numerical Analysis UI Logic
 */

// Tab Switching
function openTab(tabName, event) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    
    document.getElementById(tabName).classList.add('active');
    if (event) {
        event.currentTarget.classList.add('active');
    }
}

// Button loading state manager
function setLoading(buttonId, isLoading, defaultText) {
    const btn = document.getElementById(buttonId);
    if (isLoading) {
        btn.disabled = true;
        btn.innerText = "Processing...";
    } else {
        btn.disabled = false;
        btn.innerText = defaultText;
    }
}

// --- Chapter 1: Roots API Call ---
async function solveRoots() {
    const btnId = 'solve-root-btn';
    setLoading(btnId, true);

    const payload = {
        equation: document.getElementById('eq').value,
        method: document.getElementById('root-method').value,
        xl: document.getElementById('xl').value,
        xu: document.getElementById('xu').value,
        tol: document.getElementById('tol').value
    };

    const errorDiv = document.getElementById('root-error');
    const tbody = document.querySelector('#roots-table tbody');
    
    errorDiv.innerText = "";
    tbody.innerHTML = "";

    try {
        const response = await fetch('/solve_roots', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const result = await response.json();

        if (result.status === "error") {
            errorDiv.innerText = result.message;
        } else if (result.results && result.results.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="empty-state">No results found. Re-check the bounds or function.</td></tr>';
        } else {
            const rows = result.results.map(row => 
                `<tr>
                    <td>${row.iter}</td>
                    <td>${row.xl}</td>
                    <td>${row.xu}</td>
                    <td style="color: var(--primary); font-weight: 600;">${row.xr}</td>
                    <td>${row.err}</td>
                </tr>`
            );
            tbody.innerHTML = rows.join('');
        }
    } catch (err) {
        console.error(err);
        errorDiv.innerText = "Network error. Make sure the backend server is running.";
    } finally {
        setLoading(btnId, false, "Solve Roots");
    }
}

// --- Chapter 2: Dynamic Matrix Generation ---
function generateGrid() {
    const n = parseInt(document.getElementById('matrix-n').value);
    const containerA = document.getElementById('matrix-a-container');
    const containerB = document.getElementById('vector-b-container');
    
    containerA.style.gridTemplateColumns = `repeat(${n}, 1fr)`;
    containerB.style.gridTemplateColumns = `1fr`;
    
    containerA.innerHTML = '';
    containerB.innerHTML = '';

    for (let i = 0; i < n; i++) {
        // Generate Matrix A inputs
        for (let j = 0; j < n; j++) {
            const input = document.createElement('input');
            input.type = 'number'; 
            // Defaulting to identity-like matrix for a better initial feel
            input.value = (i === j) ? 1 : 0; 
            input.className = 'matrix-input';
            input.dataset.row = i; 
            input.dataset.col = j;
            containerA.appendChild(input);
        }
        
        // Generate Vector B inputs
        const bInput = document.createElement('input');
        bInput.type = 'number'; 
        bInput.value = 0;
        bInput.className = 'vector-input';
        bInput.dataset.row = i;
        containerB.appendChild(bInput);
    }
}

// --- Chapter 2: Linear Solver API Call ---
async function solveLinear() {
    const btnId = 'solve-lin-btn';
    setLoading(btnId, true);

    const n = parseInt(document.getElementById('matrix-n').value);
    const method = document.getElementById('lin-method').value;
    
    // Initialize empty arrays
    let matrixA = Array.from({length: n}, () => Array(n).fill(0));
    let vectorB = Array(n).fill(0);

    // Collect Data
    document.querySelectorAll('.matrix-input').forEach(input => {
        matrixA[input.dataset.row][input.dataset.col] = parseFloat(input.value) || 0;
    });
    document.querySelectorAll('.vector-input').forEach(input => {
        vectorB[input.dataset.row] = parseFloat(input.value) || 0;
    });

    const errorDiv = document.getElementById('linear-error');
    const tbody = document.querySelector('#linear-table tbody');
    
    errorDiv.innerText = "";
    tbody.innerHTML = '<tr><td colspan="3" class="empty-state">Calculating...</td></tr>';

    try {
        const response = await fetch('/solve_linear', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ matrixA, vectorB, method })
        });
        
        const result = await response.json();

        if (result.status === "error") {
            errorDiv.innerText = "Error: " + result.message;
            tbody.innerHTML = '<tr><td colspan="3" class="empty-state">Calculation failed.</td></tr>';
        } else if (result.results && result.results.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" class="empty-state">No solution found.</td></tr>';
        } else {
            const rows = result.results.map(row => 
                `<tr>
                    <td style="font-weight: 600;">${row.variable}</td>
                    <td style="color: var(--success); font-weight: 600;">${row.value}</td>
                    <td style="color: var(--text-muted); font-size: 13px;">${row.details}</td>
                </tr>`
            );
            tbody.innerHTML = rows.join('');
        }
    } catch (err) {
        console.error(err);
        errorDiv.innerText = "Network error. Make sure the backend server is running.";
        tbody.innerHTML = '<tr><td colspan="3" class="empty-state">Network error.</td></tr>';
    } finally {
        setLoading(btnId, false, "Calculate Solution");
    }
}

// Initialize the matrix on initial page load
window.addEventListener('DOMContentLoaded', generateGrid);