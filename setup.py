import os
import subprocess
import sys

VENV_DIR = ".venv"
REQUIREMENTS_FILE = "requirements.txt"

def get_venv_python():
    return os.path.join(
        VENV_DIR,
        "Scripts" if os.name == "nt" else "bin",
        "python"
    )

def get_venv_pip():
    return os.path.join(
        VENV_DIR,
        "Scripts" if os.name == "nt" else "bin",
        "pip"
    )

def create_venv():
    if not os.path.exists(VENV_DIR):
        print("🔧 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", VENV_DIR], check=True)
    else:
        print("✅ Virtual environment already exists.")

def install_requirements():
    pip_path = get_venv_pip()
    print("📦 Upgrading pip...")
    subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)

    if os.path.exists(REQUIREMENTS_FILE):
        print(f"📂 Installing dependencies from {REQUIREMENTS_FILE}...")
        try:
            subprocess.run([pip_path, "install", "-r", REQUIREMENTS_FILE], check=True)
        except subprocess.CalledProcessError:
            print("⚠️ Some packages failed to install — retrying individually.")
            with open(REQUIREMENTS_FILE) as reqs:
                for line in reqs:
                    package = line.strip()
                    if package and not package.startswith("#"):
                        try:
                            subprocess.run([pip_path, "install", package], check=True)
                        except subprocess.CalledProcessError:
                            print(f"❌ Failed to install {package}, skipping.")
    else:
        print("⚠️ No requirements.txt found. Skipping dependency installation.")

def rerun_in_venv():
    """Re-run this script inside the virtual environment, but only once."""
    if os.environ.get("INSIDE_VENV") == "1":
        return  # Already inside the venv

    venv_python = os.path.abspath(get_venv_python())
    current_python = os.path.abspath(sys.executable)

    if venv_python != current_python:
        print(f"🔁 Re-running inside virtual environment ({venv_python})...")
        new_env = os.environ.copy()
        new_env["INSIDE_VENV"] = "1"
        subprocess.run([venv_python, __file__] + sys.argv[1:], check=True, env=new_env)
        sys.exit(0)

def main():
    print(f"🐍 Using Python: {sys.executable}")
    create_venv()
    rerun_in_venv()
    install_requirements()
    
    print(f"🐍 Python executable: {sys.executable}")
    print(f"📦 Virtual environment path: {sys.prefix}")

    print("\n🎉 Environment is ready and active!")

if __name__ == "__main__":
    main()
