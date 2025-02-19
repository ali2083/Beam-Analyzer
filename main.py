# main.py
from gui import BeamAnalysisApp
from PyQt5.QtWidgets import QApplication
import sys

def main():
    app = QApplication(sys.argv)
    ex = BeamAnalysisApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
