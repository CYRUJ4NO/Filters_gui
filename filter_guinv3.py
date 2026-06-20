import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QFormLayout, QGroupBox, QLineEdit, 
                             QComboBox, QPushButton, QLabel, QCheckBox)
from PyQt5.QtCore import Qt

class CalculadorFiltrosRC(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculador de Filtros Pasivos RC (Inverso)")
        self.setGeometry(100, 100, 1000, 600)
        
        # Tema oscuro emulando tu interfaz
        self.setStyleSheet("""
            QMainWindow { background-color: #2b2b2b; }
            QWidget { color: #ffffff; font-family: 'Segoe UI', Arial; font-size: 12px; }
            QGroupBox { font-weight: bold; border: 1px solid #555555; margin-top: 10px; padding: 10px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }
            QLineEdit, QComboBox { background-color: #3c3f41; border: 1px solid #646464; padding: 4px; color: white; }
            QCheckBox { spacing: 5px; margin-top: 5px; margin-bottom: 5px; }
            QCheckBox::indicator { width: 13px; height: 13px; }
            QPushButton { background-color: #1e6fa8; border: none; padding: 8px; font-weight: bold; border-radius: 4px; margin-top: 5px; }
            QPushButton:hover { background-color: #2687cc; }
            QLabel { font-size: 13px; }
        """)
        
        # --- Componentes de la Interfaz ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Panel Izquierdo (Controles)
        panel_izquierdo = QVBoxLayout()
        
        group_tipo = QGroupBox("Configuración de Filtro")
        form_tipo = QFormLayout()
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Pasa Banda", "Pasa Alta", "Pasa Baja"])
        self.combo_tipo.currentTextChanged.connect(self.alternar_entradas)
        
        self.chk_fase = QCheckBox("Mostrar Curva de Fase")
        self.chk_fase.setChecked(False)
        self.chk_fase.stateChanged.connect(self.plot)
        
        form_tipo.addRow("Tipo de Filtro:", self.combo_tipo)
        form_tipo.addRow("", self.chk_fase)
        group_tipo.setLayout(form_tipo)
        
        # Grupo de Componentes
        self.group_components = QGroupBox("Componentes")
        self.form_comp = QFormLayout()
        
        # Componentes Etapa 1 / Filtro Único
        self.lbl_r1 = QLabel("Resistencia 1 (R1):")
        self.input_r1 = QLineEdit("1")
        self.combo_unit_r1 = QComboBox(); self.combo_unit_r1.addItems(["kΩ", "Ω", "MΩ"])
        self.widget_r1 = self.create_input_layout(self.input_r1, self.combo_unit_r1)
        
        self.lbl_c1 = QLabel("Capacitancia 1 (C1):")
        self.input_c1 = QLineEdit("10")
        self.combo_unit_c1 = QComboBox(); self.combo_unit_c1.addItems(["nF", "pF", "μF", "mF", "F"])
        self.widget_c1 = self.create_input_layout(self.input_c1, self.combo_unit_c1)
        
        # Componentes Etapa 2 (Solo Pasa Banda)
        self.lbl_r2 = QLabel("Resistencia 2 (R2):")
        self.input_r2 = QLineEdit("795.77")
        self.combo_unit_r2 = QComboBox(); self.combo_unit_r2.addItems(["Ω", "kΩ", "MΩ"])
        self.widget_r2 = self.create_input_layout(self.input_r2, self.combo_unit_r2)
        
        self.lbl_c2 = QLabel("Capacitancia 2 (C2):")
        self.input_c2 = QLineEdit("10")
        self.combo_unit_c2 = QComboBox(); self.combo_unit_c2.addItems(["pF", "nF", "μF", "mF", "F"])
        self.widget_c2 = self.create_input_layout(self.input_c2, self.combo_unit_c2)
        
        self.form_comp.addRow(self.lbl_r1, self.widget_r1)
        self.form_comp.addRow(self.lbl_c1, self.widget_c1)
        self.form_comp.addRow(self.lbl_r2, self.widget_r2)
        self.form_comp.addRow(self.lbl_c2, self.widget_c2)
        self.group_components.setLayout(self.form_comp)
        
        btn_calc = QPushButton("Calcular y Graficar")
        btn_calc.clicked.connect(self.plot)
        
        self.lbl_fc = QLabel("Frecuencia de Corte: --")
        self.lbl_fc.setStyleSheet("font-weight: bold; color: #a9b7c6; font-size: 13px; margin-top: 10px;")
        
        panel_izquierdo.addWidget(group_tipo)
        panel_izquierdo.addWidget(self.group_components)
        panel_izquierdo.addWidget(btn_calc)
        panel_izquierdo.addWidget(self.lbl_fc)
        panel_izquierdo.addStretch()
        main_layout.addLayout(panel_izquierdo, 1)

        # Panel Derecho (Gráfico)
        self.fig, self.ax1 = plt.subplots(facecolor='#2b2b2b')
        self.ax2 = self.ax1.twinx()
        self.canvas = FigureCanvas(self.fig)
        main_layout.addWidget(self.canvas, 3)
        
        self.alternar_entradas()

    def create_input_layout(self, lineedit, combo):
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(lineedit, 2)
        layout.addWidget(combo, 1)
        return w

    def alternar_entradas(self):
        tipo = self.combo_tipo.currentText()
        if tipo == "Pasa Banda":
            self.lbl_r1.setText("Resistencia 1 (R1):")
            self.lbl_c1.setText("Capacitancia 1 (C1):")
            self.lbl_r2.show(); self.widget_r2.show()
            self.lbl_c2.show(); self.widget_c2.show()
        else:
            self.lbl_r1.setText("Resistencia (R):")
            self.lbl_c1.setText("Capacitancia (C):")
            self.lbl_r2.hide(); self.widget_r2.hide()
            self.lbl_c2.hide(); self.widget_c2.hide()
        self.plot()

    def convert_value(self, input_widget, combo_widget, is_resistor):
        try:
            val = float(input_widget.text())
            unit = combo_widget.currentText()
            mult = {"Ω": 1, "kΩ": 1e3, "MΩ": 1e6} if is_resistor else {"pF": 1e-12, "nF": 1e-9, "μF": 1e-6, "mF": 1e-3, "F": 1}
            return val * mult[unit]
        except ValueError:
            return None

    def format_hz(self, val):
        if val >= 1e6: return f"{val/1e6:.2f} MHz"
        if val >= 1e3: return f"{val/1e3:.2f} kHz"
        return f"{val:.2f} Hz"

    def plot(self):
        tipo = self.combo_tipo.currentText()
        R1 = self.convert_value(self.input_r1, self.combo_unit_r1, True)
        C1 = self.convert_value(self.input_c1, self.combo_unit_c1, False)
        
        if R1 is None or C1 is None or R1 == 0 or C1 == 0: return

        self.ax1.clear(); self.ax2.clear()
        self.ax2.yaxis.tick_right()
        self.ax2.yaxis.set_label_position("right")
        self.ax1.set_facecolor('#1e1e1e')
        self.ax1.grid(True, which="both", ls="-", color='#444444')

        # Escala fija definitiva a -40 dB
        self.ax1.set_ylim(-40, 5)

        if tipo == "Pasa Banda":
            R2 = self.convert_value(self.input_r2, self.combo_unit_r2, True)
            C2 = self.convert_value(self.input_c2, self.combo_unit_c2, False)
            if R2 is None or C2 is None or R2 == 0 or C2 == 0: return
            
            fc1 = 1 / (2 * np.pi * R1 * C1)
            fc2 = 1 / (2 * np.pi * R2 * C2)
            
            self.lbl_fc.setText(f"fc1 (Baja): {self.format_hz(fc1)}\nfc2 (Alta): {self.format_hz(fc2)}")
            
            f = np.logspace(np.log10(min(fc1, fc2)) - 2, np.log10(max(fc1, fc2)) + 2, 800)
            w = 2 * np.pi * f
            
            H_pasa_alta = (1j * w * R1 * C1) / (1 + 1j * w * R1 * C1)
            H_pasa_baja = 1 / (1 + 1j * w * R2 * C2)
            H = H_pasa_alta * H_pasa_baja
            
            self.ax1.axvline(fc1, color='#55ff55', linestyle='--', linewidth=1.5)
            self.ax1.axvline(fc2, color='#ff4d4d', linestyle='--', linewidth=1.5)
            self.ax2.set_ylim(-95, 95)
        else:
            fc = 1 / (2 * np.pi * R1 * C1)
            self.lbl_fc.setText(f"fc calculada: {self.format_hz(fc)}")
            f = np.logspace(np.log10(fc) - 3, np.log10(fc) + 3, 600)
            w = 2 * np.pi * f
            H = 1 / (1 + 1j * (w / (2*np.pi*fc))) if tipo == "Pasa Baja" else (1j * (w / (2*np.pi*fc))) / (1 + 1j * (w / (2*np.pi*fc)))
            self.ax1.axvline(fc, color='#ff4d4d', linestyle='--', linewidth=1.5)
            self.ax2.set_ylim(-95, 5) if tipo == "Pasa Baja" else self.ax2.set_ylim(-5, 95)

        magnitud_db = 20 * np.log10(np.abs(H))
        fase_grados = np.angle(H, deg=True)

        self.ax1.semilogx(f, magnitud_db, color='#00cbcb', linewidth=2)
        self.ax1.set_xlabel('Frecuencia (Hz)', color='white')
        self.ax1.set_ylabel('Magnitud (dB)', color='#00cbcb')
        self.ax1.tick_params(colors='white', which='both')

        if self.chk_fase.isChecked():
            self.ax2.semilogx(f, fase_grados, color='#ff9f21', linewidth=2)
            self.ax2.set_ylabel('Fase (Grados °)', color='#ff9f21')
            self.ax2.tick_params(colors='white', which='both')
        else:
            self.ax2.set_ylabel('')
            self.ax2.set_yticks([])

        self.fig.suptitle(f"Respuesta en Frecuencia - Filtro {tipo}", color='white', fontsize=14)
        self.fig.tight_layout()
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = CalculadorFiltrosRC()
    win.show()
    sys.exit(app.exec_())

