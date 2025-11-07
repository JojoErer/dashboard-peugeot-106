from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
import sys

app = QApplication(sys.argv)
engine = QQmlApplicationEngine()

# Add path to the parent folder of the module
engine.addImportPath(r"C:\Users\jorer\OneDrive\Documenten\test\build\x86_windows_msys_pe_64bit-Debug")  # folder containing 'test' folder

engine.load(r"C:\Users\jorer\OneDrive\Documenten\test\build\x86_windows_msys_pe_64bit-Debug\mainPY.qml")

if not engine.rootObjects():
    sys.exit(-1)

sys.exit(app.exec())