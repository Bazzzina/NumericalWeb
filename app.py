from flask import Flask, render_template, request, jsonify
import numpy as np
import sympy as sp

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/solve_roots', methods=['POST'])
def solve_roots():
    data = request.json
    eq_str = data.get('equation')
    method = data.get('method')
    
    try:
        xl = float(data.get('xl', 1))
        tol = float(data.get('tol', 0.01))
        x = sp.Symbol('x')
        f = sp.sympify(eq_str)
        f_num = sp.lambdify(x, f, 'numpy')
        results = []

        if method == "Bisection":
            xu = float(data.get('xu', 2))
            xr_old = 0
            for i in range(1, 30):
                xr = (xl + xu) / 2
                err = abs((xr - xr_old) / xr) * 100 if i > 1 else 100
                results.append({"iter": i, "xl": round(xl,4), "xu": round(xu,4), "xr": round(xr,4), "err": f"{err:.2f}%"})
                if err < tol: break
                if f_num(xl) * f_num(xr) < 0: xu = xr
                else: xl = xr
                xr_old = xr

        elif method == "Newton":
            df = sp.diff(f, x)
            df_num = sp.lambdify(x, df, 'numpy')
            xi = xl
            for i in range(1, 30):
                f_val = f_num(xi)
                df_val = df_num(xi)
                if df_val == 0:
                    return jsonify({"status": "error", "message": "Derivative is zero."})
                xi_next = xi - (f_val / df_val)
                err = abs((xi_next - xi) / xi_next) * 100
                results.append({"iter": i, "xl": "-", "xu": "-", "xr": round(xi_next,4), "err": f"{err:.2f}%"})
                if err < tol: break
                xi = xi_next

        elif method == "Secant":
            x_prev = float(data.get('xl', 1))
            x_curr = float(data.get('xu', 2))
            for i in range(1, 30):
                f_prev = f_num(x_prev)
                f_curr = f_num(x_curr)
                if f_curr - f_prev == 0:
                    return jsonify({"status": "error", "message": "Division by zero."})
                x_next = x_curr - f_curr * (x_curr - x_prev) / (f_curr - f_prev)
                err = abs((x_next - x_curr) / x_next) * 100
                results.append({"iter": i, "xl": round(x_prev,4), "xu": round(x_curr,4), "xr": round(x_next,4), "err": f"{err:.2f}%"})
                if err < tol: break
                x_prev, x_curr = x_curr, x_next

        elif method == "False Position":
            xu = float(data.get('xu', 2))
            if f_num(xl) * f_num(xu) >= 0:
                return jsonify({"status": "error", "message": "f(xl) and f(xu) must have different signs."})
            xr_old = 0
            for i in range(1, 30):
                f_xl = f_num(xl)
                f_xu = f_num(xu)
                if f_xl - f_xu == 0: break
                xr = xu - (f_xu * (xl - xu)) / (f_xl - f_xu)
                err = abs((xr - xr_old) / xr) * 100 if i > 1 else 100
                results.append({"iter": i, "xl": round(xl,4), "xu": round(xu,4), "xr": round(xr,4), "err": f"{err:.2f}%"})
                if err < tol or f_num(xr) == 0: break
                if f_num(xl) * f_num(xr) < 0: xu = xr
                else: xl = xr
                xr_old = xr

        elif method == "Fixed Point":
            xi = xl
            for i in range(1, 30):
                xi_next = f_num(xi)
                if xi_next != 0: err = abs((xi_next - xi) / xi_next) * 100
                else: err = 100
                results.append({"iter": i, "xl": "-", "xu": "-", "xr": round(xi_next,4), "err": f"{err:.2f}%"})
                if err < tol: break
                xi = xi_next

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
        res_text = ""

        if method == "Cramer's Rule":
            det_A = np.linalg.det(matrix_a)
            res_text += f"Step 1: Calculate Determinant of A\nDet(A) = {det_A:.4f}\n\n"
            if abs(det_A) < 1e-9:
                return jsonify({"status": "error", "message": "Determinant is zero. No unique solution."})
            
            for i in range(n):
                Ai = matrix_a.copy()
                Ai[:, i] = vector_b
                det_Ai = np.linalg.det(Ai)
                xi = det_Ai / det_A
                res_text += f"x{i+1}: Det(A{i+1}) = {det_Ai:.4f}  =>  x{i+1} = {xi:.4f}\n"
        else:
            x = np.linalg.solve(matrix_a, vector_b)
            res_text += f"Solution using {method}:\n" + "="*35 + "\n"
            for i in range(n):
                res_text += f"  x{i+1}  =  {x[i]:.4f}\n"

        return jsonify({"status": "success", "result": res_text})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)