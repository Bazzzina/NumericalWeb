# Numerical Analysis Solver

A web-based application for solving numerical analysis problems. This tool was built using a Python Flask backend to handle the mathematics, and an HTML/CSS/JavaScript frontend for a fast, interactive user interface.

## Features

* **Chapter 1: Roots Finding**
  * Solves equations using Bisection, Newton-Raphson, False Position, Secant, and Fixed Point methods.
  * Calculates and displays the error percentage for each iteration.
* **Chapter 2: Linear Equations**
  * Solves systems of linear equations using Gauss Elimination, Cramer's Rule, and Gauss-Jordan.
  * Supports dynamic matrix sizes (from 2x2 up to 6x6).

## Project Structure

* `app.py`: The Python Flask server that handles all mathematical logic (NumPy and SymPy).
* `requirements.txt`: The list of Python libraries needed to run the project.
* `templates/index.html`: The main web page structure.
* `static/style.css`: The dark-mode styling and layout.
* `static/script.js`: The logic that sends data between the web page and the Python server without reloading the page.

## How to Run the Project

**1. Install the required libraries**  
Open your terminal in the project folder and run:
`pip install -r requirements.txt`

**2. Start the server**  
Run the Flask application using Python:
`python app.py`

**3. Open the website**  
Open your web browser and go to the local address provided by Flask:
`http://127.0.0.1:5000/`

*Note: Because this project uses a Python backend, it must be run using the terminal command above. It will not work properly if opened using the VS Code "Live Server" extension.*

