// Tab Switching Logic
function openTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(tabName).classList.add('active');
    event.currentTarget.classList.add('active');
}

// Chapter 1: Roots API Call
async function solveRoots() {
    const data = {
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
            body: JSON.stringify(data)
        });
        const result = await response.json();

        if (result.status === "error") {
            errorDiv.innerText = result.message;
            return;
        }

        result.results.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${row.iter}</td><td>${row.xl}</td><td>${row.xu}</td><td>${row.xr}</td><td>${row.err}</td>`;
            tbody.appendChild(tr);
        });
    } catch (err) {
        errorDiv.innerText = "Network error. Make sure Flask is running.";
    }
}

// Chapter 2: Dynamic Matrix Generation
function generateGrid() {
    const n = parseInt(document.getElementById('matrix-n').value);
    const containerA = document.getElementById('matrix-a-container');
    const containerB = document.getElementById('vector-b-container');
    
    containerA.style.gridTemplateColumns = `repeat(${n}, 1fr)`;
    containerB.style.gridTemplateColumns = `1fr`;
    
    containerA.innerHTML = '';
    containerB.innerHTML = '';

    for (let i = 0; i < n; i++) {
        for (let j = 0; j < n; j++) {
            const input = document.createElement('input');
            input.type = 'number'; input.value = 0;
            input.className = 'matrix-input';
            input.dataset.row = i; input.dataset.col = j;
            containerA.appendChild(input);
        }
        const bInput = document.createElement('input');
        bInput.type = 'number'; bInput.value = 0;
        bInput.className = 'vector-input';
        bInput.dataset.row = i;
        containerB.appendChild(bInput);
    }
}

// Chapter 2: Linear Solver API Call
async function solveLinear() {
    const n = parseInt(document.getElementById('matrix-n').value);
    const method = document.getElementById('lin-method').value;
    const resultBox = document.getElementById('linear-result');
    
    let matrixA = Array.from({length: n}, () => Array(n).fill(0));
    let vectorB = Array(n).fill(0);

    document.querySelectorAll('.matrix-input').forEach(input => {
        matrixA[input.dataset.row][input.dataset.col] = parseFloat(input.value);
    });
    document.querySelectorAll('.vector-input').forEach(input => {
        vectorB[input.dataset.row] = parseFloat(input.value);
    });

    try {
        const response = await fetch('/solve_linear', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ matrixA, vectorB, method })
        });
        const result = await response.json();

        if (result.status === "error") {
            resultBox.value = "Error: " + result.message;
        } else {
            resultBox.value = result.result;
        }
    } catch (err) {
        resultBox.value = "Network error. Make sure Flask is running.";
    }
}

// Initialize the matrix on page load
window.onload = generateGrid;