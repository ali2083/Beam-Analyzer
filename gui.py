from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QMessageBox)
from PyQt5.QtGui import QDoubleValidator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from plots_data import getting_plots_data

class BeamAnalysisApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Beam Analysis')

        # Layouts
        main_layout = QHBoxLayout()
        input_layout = QVBoxLayout()
        plot_layout = QVBoxLayout()

        # Input widgets
        labels = ["Length of Beam (meters):", "Modulus of Elasticity (Pascal):", "Moment of Inertia (m^4):"]
        self.entries = []

        for label in labels:
            input_label = QLabel(label)
            input_entry = QLineEdit()
            input_entry.setValidator(QDoubleValidator(0.0, float('inf'),3))
            input_layout.addWidget(input_label)
            input_layout.addWidget(input_entry)
            self.entries.append(input_entry)

        input_layout.addWidget(QLabel("Supports (Type and Position):"))
        self.supports_layout = QVBoxLayout()
        self.add_support_button = QPushButton("Add Support")
        self.add_support_button.clicked.connect(self.add_support)
        input_layout.addLayout(self.supports_layout)
        input_layout.addWidget(self.add_support_button)

        input_layout.addWidget(QLabel("Point Loads (Position and Value):"))
        self.point_loads_layout = QVBoxLayout()
        self.add_point_load_button = QPushButton("Add Point Load")
        self.add_point_load_button.clicked.connect(self.add_point_load)
        input_layout.addLayout(self.point_loads_layout)
        input_layout.addWidget(self.add_point_load_button)

        input_layout.addWidget(QLabel("Distributed Loads (Load Function and Interval):"))
        self.distributed_loads_layout = QVBoxLayout()
        self.add_distributed_load_button = QPushButton("Add Distributed Load")
        self.add_distributed_load_button.clicked.connect(self.add_distributed_load)
        input_layout.addLayout(self.distributed_loads_layout)
        input_layout.addWidget(self.add_distributed_load_button)

        input_layout.addWidget(QLabel("Moment (Position and Value):"))
        self.moments_layout = QVBoxLayout()
        self.add_moment_button = QPushButton("Add Moment")
        self.add_moment_button.clicked.connect(self.add_moment)
        input_layout.addLayout(self.moments_layout)
        input_layout.addWidget(self.add_moment_button)

        analyze_button = QPushButton("Analyze")
        analyze_button.clicked.connect(self.perform_analysis_wrapper)
        input_layout.addWidget(analyze_button)

        # Plot placeholders
        self.shear_force_canvas = self.create_plot_canvas("Shear Force Diagram", plot_layout)
        self.bending_moment_canvas = self.create_plot_canvas("Bending Moment Diagram", plot_layout)
        self.deflection_canvas = self.create_plot_canvas("Deflection Diagram", plot_layout)

        # Add layouts to main layout
        main_layout.addLayout(input_layout, 1)
        main_layout.addLayout(plot_layout, 2)

        self.setLayout(main_layout)

    def add_support(self):
        support_input_layout = QHBoxLayout()
        support_type = QComboBox()
        support_type.addItems(["Roller", "Pin", "Fixed"])
        support_position = QLineEdit()
        support_position.setValidator(QDoubleValidator())
        support_position.setPlaceholderText("Position")
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda: self.delete_widget(support_input_layout))
        support_input_layout.addWidget(support_type)
        support_input_layout.addWidget(support_position)
        support_input_layout.addWidget(delete_button)
        self.supports_layout.addLayout(support_input_layout)

    def add_point_load(self):
        point_load_input_layout = QHBoxLayout()
        point_load_value = QLineEdit()
        point_load_value.setValidator(QDoubleValidator())
        point_load_value.setPlaceholderText("Value")
        point_load_position = QLineEdit()
        point_load_position.setValidator(QDoubleValidator())
        point_load_position.setPlaceholderText("Position")
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda: self.delete_widget(point_load_input_layout))
        point_load_input_layout.addWidget(point_load_value)
        point_load_input_layout.addWidget(point_load_position)
        point_load_input_layout.addWidget(delete_button)
        self.point_loads_layout.addLayout(point_load_input_layout)

    def add_distributed_load(self):
        distributed_load_input_layout = QHBoxLayout()
        load_function = QLineEdit()
        load_function.setPlaceholderText("Load Function")
        interval_start = QLineEdit()
        interval_start.setValidator(QDoubleValidator())
        interval_start.setPlaceholderText("Start Position")
        interval_end = QLineEdit()
        interval_end.setValidator(QDoubleValidator())
        interval_end.setPlaceholderText("End Position")
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda: self.delete_widget(distributed_load_input_layout))
        distributed_load_input_layout.addWidget(load_function)
        distributed_load_input_layout.addWidget(interval_start)
        distributed_load_input_layout.addWidget(interval_end)
        distributed_load_input_layout.addWidget(delete_button)
        self.distributed_loads_layout.addLayout(distributed_load_input_layout)

    def add_moment(self):
        moment_input_layout = QHBoxLayout()
        moment_value = QLineEdit()
        moment_value.setValidator(QDoubleValidator())
        moment_value.setPlaceholderText("Value")
        moment_position = QLineEdit()
        moment_position.setValidator(QDoubleValidator())
        moment_position.setPlaceholderText("Position")
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda: self.delete_widget(moment_input_layout))
        moment_input_layout.addWidget(moment_value)
        moment_input_layout.addWidget(moment_position)
        moment_input_layout.addWidget(delete_button)
        self.moments_layout.addLayout(moment_input_layout)

    def delete_widget(self, layout):
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        layout.deleteLater()

    def create_plot_canvas(self, title, layout):
        label = QLabel(title)
        layout.addWidget(label)
        fig = Figure()
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
        return canvas
    
    def check_required_supports(self):
        for i in range(self.supports_layout.count()):
            layout = self.supports_layout.itemAt(i).layout()
            if layout:
                for j in range(layout.count()):
                    widget = layout.itemAt(j).widget()
                    if isinstance(widget, QLineEdit) and not widget.text():
                        return False
        return True

    def check_required_point_loads(self):
        for i in range(self.point_loads_layout.count()):
            layout = self.point_loads_layout.itemAt(i).layout()
            if layout:
                for j in range(layout.count()):
                    widget = layout.itemAt(j).widget()
                    if isinstance(widget, QLineEdit) and not widget.text():
                        return False
        return True

    def check_required_distributed_loads(self):
        for i in range(self.distributed_loads_layout.count()):
            layout = self.distributed_loads_layout.itemAt(i).layout()
            if layout:
                for j in range(layout.count()):
                    widget = layout.itemAt(j).widget()
                    if isinstance(widget, QLineEdit) and not widget.text():
                        return False
        return True
    
    def validate_inputs(self):
        for entry in self.entries:
            try:
                float(entry.text())
            except ValueError:
                return False
        return True
    
    def perform_analysis_wrapper(self):
        # Collect inputs and call perform_analysis from calc.py
        if not self.validate_inputs():
            QMessageBox.warning(self, "Warning", "Please fill in all required fields and ensure correct support setup.")
            return

        length = float(self.entries[0].text())
        elasticity = float(self.entries[1].text())
        inertia = float(self.entries[2].text())

        ## support_type: 1 - Roller, 2 - Pin, 3 - Fixed ##
        supports = []
        for layout in (self.supports_layout.itemAt(i).layout() for i in range(self.supports_layout.count())):
            support_type = layout.itemAt(0).widget().currentText()
            position = float(layout.itemAt(1).widget().text())
            if support_type == "Roller":
                support_code = 1
            elif support_type == "Pin":
                support_code = 2
            elif support_type == "Fixed":
                support_code = 3
            supports.append((support_code, position))

        point_loads = [(float(layout.itemAt(0).widget().text()), float(layout.itemAt(1).widget().text())) 
                       for layout in (self.point_loads_layout.itemAt(i).layout() for i in range(self.point_loads_layout.count()))]

        distributed_loads = [(layout.itemAt(0).widget().text(), float(layout.itemAt(1).widget().text()), float(layout.itemAt(2).widget().text())) 
                             for layout in (self.distributed_loads_layout.itemAt(i).layout() for i in range(self.distributed_loads_layout.count()))]
        
        moments = [(float(layout.itemAt(0).widget().text()), float(layout.itemAt(1).widget().text()))
                  for layout in (self.moments_layout.itemAt(i).layout() for i in range(self.moments_layout.count()))]
        
        shear, moment, deflection = getting_plots_data(length, elasticity, inertia, supports, point_loads, distributed_loads, moments)

        # Draw shear force diagram
        self.shear_force_canvas.figure.clear()
        ax = self.shear_force_canvas.figure.add_subplot(111)
        ax.plot(shear)
        ax.set_title("Shear Force Diagram")
        ax.set_xlabel("Position (m)")
        ax.set_ylabel("Shear Force (N)")
        self.shear_force_canvas.draw()

        # Draw bending moment diagram
        self.bending_moment_canvas.figure.clear()
        ax = self.bending_moment_canvas.figure.add_subplot(111)
        ax.plot(moment)
        ax.set_title("Bending Moment Diagram")
        ax.set_xlabel("Position (m)")
        ax.set_ylabel("Bending Moment (Nm)")
        self.bending_moment_canvas.draw()

        # Draw deflection diagram
        self.deflection_canvas.figure.clear()
        ax = self.deflection_canvas.figure.add_subplot(111)
        ax.plot(deflection)
        ax.set_title("Deflection Diagram")
        ax.set_xlabel("Position (m)")
        ax.set_ylabel("Deflection (m)")
        self.deflection_canvas.draw()
