import os
import subprocess
import sys

VENV_DIR = ".venv"
REQUIREMENTS_FILE = "requirements.txt"
MAIN_SCRIPT = "main.py"

def create_venv():
    if not os.path.exists(VENV_DIR):
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", VENV_DIR], check=True)
    else:
        print("Virtual environment already exists.")

def install_requirements():
    if os.path.exists(REQUIREMENTS_FILE):
        print(f"Installing dependencies from {REQUIREMENTS_FILE}...")
        with open(REQUIREMENTS_FILE, 'r') as f:
            requirements = f.readlines()
            for requirement in requirements:
                requirement = requirement.strip()
                if requirement and not requirement.startswith("#"):
                    try:
                        subprocess.run([os.path.join(VENV_DIR, "Scripts" if os.name == "nt" else "bin", "python"), "-m", "pip", "install", requirement], check=True)
                        print(f"Installed {requirement}")
                    except subprocess.CalledProcessError as e:
                        print(f"Failed to install {requirement}: {e}")
                        print("Continuing with next requirement...")
    else:
        print("No requirements.txt found. Skipping dependency installation.")

def run_main():
    venv_python = os.path.join(VENV_DIR, "Scripts" if os.name == "nt" else "bin", "python")
    print(f"Running {MAIN_SCRIPT} inside the virtual environment...")
    try:
        subprocess.run([venv_python, MAIN_SCRIPT], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to run {MAIN_SCRIPT}: {e}")

def main():
    print(f"Using Python: {sys.executable}")
    create_venv()
    install_requirements()
    
    print(f"Python executable: {sys.executable}")
    print(f"Virtual environment path: {os.path.join(VENV_DIR, 'Scripts' if os.name == 'nt' else 'bin')}")

    run_main()

if __name__ == "__main__":
    main()