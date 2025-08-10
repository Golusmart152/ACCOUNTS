# FastFin Accounting Software

This is a desktop accounting application built with Python and CustomTkinter.

## How to Run on Windows

To run this application on your Windows PC, please follow the steps below.

### 1. Install Python

If you don't have Python installed, download and install it from the official website.

- **[Download Python](https://www.python.org/downloads/)**
- When installing, make sure to check the box that says **"Add Python to PATH"**.

You can verify that Python is installed by opening a Command Prompt and typing:
```
python --version
```

### 2. Set Up the Project

1.  **Download or clone this repository.**
2.  **Open a Command Prompt** in the project's root directory (the one containing this `README.md` file).

### 3. Create a Virtual Environment (Recommended)

Using a virtual environment keeps your project's dependencies separate from your system's Python installation.

```bash
python -m venv venv
```

Activate the virtual environment:
```bash
venv\Scripts\activate
```
Your command prompt should now have `(venv)` at the beginning of the line.

### 4. Install Dependencies

Install the required Python packages using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 5. Run the Application

Once the dependencies are installed, you can run the application. Run the following command from the project's root directory:

```bash
python -m src.main
```

(Note: We use `python -m src.main` instead of `python src/main.py` to ensure that Python handles the project's internal imports correctly.)

The application window should now open.

## Code Polishing Notes

- A `requirements.txt` file has been added to the project to make dependency management straightforward.
- This `README.md` file has been updated to provide clear setup and execution instructions.
