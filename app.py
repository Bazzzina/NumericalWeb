from flask import Flask, render_template, request, jsonify
import numpy as np
import sympy as sp

app = Flask(__name__)

# --- Helper Functions for Numerical Root Finding ---

def bisection(f_num, xl, xu, tol, max_iter=30):
    results = []
    xr_old = 0
    for i in range(1, max_iter + 1):
        xr = (xl + xu) / 2.0
        err = abs((xr - xr_old) / xr) * 100 if i > 1 else 100
        results.append({"iter": i, "xl": round(xl, 4), "xu": round(xu, 4), "xr": round(xr, 4), "err": f"{err:.2f}%"})
        
        if err < tol: 
            break
            
        if f_num(xl) * f_num(xr) < 0: 
            xu = xr
        else: 
            xl = xr
        xr_old = xr
    return results

def newton(f, x, f_num, xi, tol, max_iter=30):
    results = []
    df = sp.diff(f, x)
    df_num = sp.lambdify(x, df, 'numpy')
    
    for i in range(1, max_iter + 1):
        f_val, df_val = f_num(xi), df_num(xi)
        if df_val == 0:
            raise ValueError("Derivative is zero. Cannot proceed with Newton's method.")
            
        xi_next = xi - (f_val / df_val)
        err = abs((xi_next - xi) / xi_next) * 100 if xi_next != 0 else 100
        results.append({"iter": i, "xl": "-", "xu": "-", "xr": round(xi_next, 4), "err": f"{err:.2f}%"})
        
        if err < tol: 
            break
        xi = xi_next
    return results

def secant(f_num, x_prev, x_curr, tol, max_iter=30):
    results = []
    for i in range(1, max_iter + 1):
        f_prev, f_curr = f_num(x_prev), f_num(x_curr)
        if f_curr - f_prev == 0:
            raise ValueError("Division by zero. Difference between function evaluations is zero.")
            
        x_next = x_curr - f_curr * (x_curr - x_prev) / (f_curr - f_prev)
        err = abs((x_next - x_curr) / x_next) * 100 if x_next != 0 else 100
        results.append({"iter": i, "xl": round(x_prev, 4), "xu": round(x_curr, 4), "xr": round(x_next, 4), "err": f"{err:.2f}%"})
        
        if err < tol: 
            break
        x_prev, x_curr = x_curr, x_next
    return results

def false_position(f_num, xl, xu, tol, max_iter=30):
    if f_num(xl) * f_num(xu) >= 0:
        raise ValueError("f(xl) and f(xu) must have different signs to bracket the root.")
        
    results = []
    xr_old = 0
    for i in range(1, max_iter + 1):
        f_xl, f_xu = f_num(xl), f_num(xu)
        if f_xl - f_xu == 0: 
            break
            
        xr = xu - (f_xu * (xl - xu)) / (f_xl - f_xu)
        err = abs((xr - xr_old) / xr) * 100 if i > 1 else 100
        results.append({"iter": i, "xl": round(xl, 4), "xu": round(xu, 4), "xr": round(xr, 4), "err": f"{err:.2f}%"})
        
        if err < tol or f_num(xr) == 0: 
            break
            
        if f_num(xl) * f_num(xr) < 0: 
            xu = xr
        else: 
            xl = xr
        xr_old = xr
    return results

def fixed_point(f_num, xi, tol, max_iter=30):
    results = []
    for i in range(1, max_iter + 1):
        xi_next = f_num(xi)
        err = abs((xi_next - xi) / xi_next) * 100 if xi_next != 0 else 100
        results.append({"iter": i, "xl": "-", "xu": "-", "xr": round(xi_next, 4), "err": f"{err:.2f}%"})
        
        if err < tol: 
            break
        xi = xi_next
    return results

# --- Application Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/solve_roots', methods=['POST'])
def solve_roots():
    data = request.json
    try:
        method = data.get('method')
        eq_str = data.get('equation')
        xl = float(data.get('xl', 1))
        xu = float(data.get('xu', 2))
        tol = float(data.get('tol', 0.01))
        
        x = sp.Symbol('x')
        f = sp.sympify(eq_str)
        f_num = sp.lambdify(x, f, 'numpy')

        # Dispatch table for methods
        if method == "Bisection":
            results = bisection(f_num, xl, xu, tol)
        elif method == "Newton":
            results = newton(f, x, f_num, xl, tol)
        elif method == "Secant":
            results = secant(f_num, xl, xu, tol)
        elif method == "False Position":
            results = false_position(f_num, xl, xu, tol)
        elif method == "Fixed Point":
            results = fixed_point(f_num, xl, tol)
        else:
            raise ValueError(f"Unknown root finding method: {method}")

        return jsonify({"status": "success", "results": results})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/solve_linear', methods=['POST'])
def solve_linear():
    data = request.json
    try:
        matrix_a = np.array(data.get('matrixA'), dtype=float)
        vector_b = np.array(data.get('vectorB'), dtype=float)
        method = data.get('method')
        n = len(vector_b)
        results = []

        if method == "Cramer's Rule":
            det_A = np.linalg.det(matrix_a)
            if abs(det_A) < 1e-9:
                raise ValueError("Determinant is near zero. No unique solution exists.")
            
            for i in range(n):
                Ai = matrix_a.copy()
                Ai[:, i] = vector_b
                det_Ai = np.linalg.det(Ai)
                xi = det_Ai / det_A
                results.append({
                    "variable": f"x{i+1}", 
                    "value": round(xi, 4),
                    "details": f"Det(A{i+1}) = {det_Ai:.4f}, Det(A) = {det_A:.4f}"
                })
        else:
            # General solution (Gauss Elimination equivalent via numpy)
            x = np.linalg.solve(matrix_a, vector_b)
            for i in range(n):
                results.append({
                    "variable": f"x{i+1}", 
                    "value": round(x[i], 4),
                    "details": "-"
                })

        return jsonify({"status": "success", "results": results})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
