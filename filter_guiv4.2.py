#!/usr/bin/env python3

import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QCheckBox)

plt.style.use('dark_background')

DARK_STYLE = """
QMainWindow { background-color: #2b2b2b; }
QWidget { background-color: #2b2b2b; color: #e0e0e0; font-family: sans-serif; font-size: 13px; }
QLineEdit { background-color: #3c3f41; border: 1px solid #555555; border-radius: 4px; padding: 4px; color: #ffffff; }
QComboBox { background-color: #3c3f41; border: 1px solid #555555; border-radius: 4px; padding: 4px; color: #ffffff; }
QPushButton { background-color: #4a90e2; color: white; border: none; border-radius: 4px; padding: 8px; font-weight: bold; }
QPushButton:hover { background-color: #357abd; }
"""

class FiltroApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculador de Filtros Pasivos RC")
        self.setGeometry(100, 100, 950, 600)
        self.setStyleSheet(DARK_STYLE)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        control_panel.setFixedWidth(320)
        
        control_layout.addWidget(QLabel("<b>Tipo de Filtro:</b>"))
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Pasa Alta", "Pasa Baja", "Pasa Banda"])
        self.combo_tipo.currentIndexChanged.connect(self.toggle_inputs)
        control_layout.addWidget(self.combo_tipo)
        
        self.lbl_fc1 = QLabel("Frecuencia de Corte (fc):")
        control_layout.addWidget(self.lbl_fc1)
        
        layout_fc1 = QHBoxLayout()
        self.txt_fc1 = QLineEdit("20")
        self.unit_fc1 = QComboBox()
        self.unit_fc1.addItems(["Hz", "kHz"])
        layout_fc1.addWidget(self.txt_fc1)
        layout_fc1.addWidget(self.unit_fc1)
        control_layout.addLayout(layout_fc1)
        
        self.lbl_fc2 = QLabel("Frecuencia de Corte Alta (fc2):")
        self.lbl_fc2_widget = QWidget()
        layout_fc2_container = QVBoxLayout(self.lbl_fc2_widget)
        layout_fc2_container.setContentsMargins(0, 0, 0, 0)
        
        layout_fc2_inputs = QHBoxLayout()
        self.txt_fc2 = QLineEdit("20")
        self.unit_fc2 = QComboBox()
        self.unit_fc2.addItems(["kHz", "Hz"])
        layout_fc2_inputs.addWidget(self.txt_fc2)
        layout_fc2_inputs.addWidget(self.unit_fc2)
        
        layout_fc2_container.addWidget(self.lbl_fc2)
        layout_fc2_container.addLayout(layout_fc2_inputs)
        control_layout.addWidget(self.lbl_fc2_widget)
        
        self.chk_fase = QCheckBox("Mostrar Curva de Fase")
        self.chk_fase.setChecked(True)
        self.chk_fase.stateChanged.connect(self.calcular_y_graficar)
        control_layout.addWidget(self.chk_fase)
        
        self.btn_calcular = QPushButton("Calcular y Graficar")
        self.btn_calcular.clicked.connect(self.calcular_y_graficar)
        control_layout.addWidget(self.btn_calcular)
        
        control_layout.addWidget(QLabel("<br><b>Componentes Calculados:</b>"))
        self.lbl_resultados = QLabel("Introduce los valores y haz clic en calcular.")
        self.lbl_resultados.setWordWrap(True)
        control_layout.addWidget(self.lbl_resultados)
        control_layout.addStretch()
        
        # Cuadro/plot principal único
        self.figure, self.ax_mag = plt.subplots(figsize=(6, 5), facecolor='#2b2b2b')
        self.ax_phase = self.ax_mag.twinx()
        self.canvas = FigureCanvas(self.figure)
        
        main_layout.addWidget(control_panel)
        main_layout.addWidget(self.canvas)
        
        self.toggle_inputs()
        self.calcular_y_graficar()

    def toggle_inputs(self):
        es_pasabanda = self.combo_tipo.currentText() == "Pasa Banda"
        self.lbl_fc1.setText("Frecuencia Baja (fc1):" if es_pasabanda else "Frecuencia de Corte (fc):")
        self.lbl_fc2_widget.setVisible(es_pasabanda)

    def sugerir_capacitor(self, fc):
        if fc < 100: return 1e-6, "1 µF"
        elif fc < 1000: return 100e-9, "100 nF"
        return 1e-8, "10 nF"

    def obtener_frecuencia(self, campo_texto, campo_unidad):
        val = float(campo_texto.text().replace(',', '.'))
        return val * 1000 if campo_unidad.currentText() == "kHz" else val

    def calcular_y_graficar(self):
        try:
            tipo = self.combo_tipo.currentText()
            fc1 = self.obtener_frecuencia(self.txt_fc1, self.unit_fc1)
            f = np.logspace(0, 6, 1000)
            w = 2 * np.pi * f
            
            self.ax_mag.clear()
            self.ax_phase.clear()
            
            self.ax_mag.set_facecolor('#2b2b2b')
            
            if tipo == "Pasa Alta":
                C, C_str = self.sugerir_capacitor(fc1)
                R = 1 / (2 * np.pi * fc1 * C)
                texto_res = f"<b>Etapa Pasa Alta (fc):</b><br>C = {C_str}<br>R = {R:.2f} Ω"
                H = (1j * w * R * C) / (1 + 1j * w * R * C)
                self.ax_mag.axvline(fc1, color='#ff6b6b', linestyle='--', label=f'fc = {fc1:.1f} Hz')

            elif tipo == "Pasa Baja":
                C, C_str = self.sugerir_capacitor(fc1)
                R = 1 / (2 * np.pi * fc1 * C)
                texto_res = f"<b>Etapa Pasa Baja (fc):</b><br>C = {C_str}<br>R = {R:.2f} Ω"
                H = 1 / (1 + 1j * w * R * C)
                self.ax_mag.axvline(fc1, color='#ff6b6b', linestyle='--', label=f'fc = {fc1:.1f} Hz')

            elif tipo == "Pasa Banda":
                fc2 = self.obtener_frecuencia(self.txt_fc2, self.unit_fc2)
                if fc1 >= fc2:
                    self.lbl_resultados.setText("<font color='#ff6b6b'><b>Error:</b> fc1 debe ser menor que fc2.</font>")
                    return
                C1, C1_str = self.sugerir_capacitor(fc1)
                R1 = 1 / (2 * np.pi * fc1 * C1)
                C2, C2_str = self.sugerir_capacitor(fc2)
                R2 = 1 / (2 * np.pi * fc2 * C2)
                
                texto_res = f"<b>Etapa Pasa Alta (fc1):</b><br>C1 = {C1_str}<br>R1 = {R1:.2f} Ω<br><br>" \
                            f"<b>Etapa Pasa Baja (fc2):</b><br>C2 = {C2_str}<br>R2 = {R2:.2f} Ω"
                H = ((1j * w * R1 * C1) / (1 + 1j * w * R1 * C1)) * (1 / (1 + 1j * w * R2 * C2))
                self.ax_mag.axvline(fc1, color='#51cf66', linestyle='--', label=f'fc1 = {fc1:.1f} Hz')
                self.ax_mag.axvline(fc2, color='#ff6b6b', linestyle='--', label=f'fc2 = {fc2:.1f} Hz')

            # Dibujar la curva de Magnitud
            magnitud_db = 20 * np.log10(np.abs(H))
            trazos = self.ax_mag.semilogx(f, magnitud_db, linewidth=2, color='#00adb5', label="Magnitud (dB)")
            self.ax_mag.set_title(f"Respuesta en Frecuencia - Filtro {tipo}", color='#ffffff')
            self.ax_mag.set_xlabel("Frecuencia (Hz)", color='#e0e0e0')
            self.ax_mag.set_ylabel("Magnitud (dB)", color='#00adb5')
            self.ax_mag.set_ylim(-20, 2)
            self.ax_mag.grid(True, which="both", linestyle=":", alpha=0.3, color='#888888')

            # Control dinámico de la visibilidad de la curva de Fase
            if self.chk_fase.isChecked():
                self.ax_phase.get_yaxis().set_visible(True)
                fase_grados = np.angle(H, deg=True)
                linea_fase = self.ax_phase.semilogx(f, fase_grados, linewidth=2, color='#ff9f43', label="Fase (°)")
                
                # Forzar que los textos y marcas se queden estrictamente a la derecha del cuadro
                self.ax_phase.set_ylabel("Fase (Grados °)", color='#ff9f43')
                self.ax_phase.yaxis.set_label_position("right")
                self.ax_phase.yaxis.tick_right()
                
                self.ax_phase.set_ylim(-100, 100)
                self.ax_phase.set_yticks([-90, -45, 0, 45, 90])
                trazos = trazos + linea_fase
            else:
                # Si el checkbox se desmarca, apaga por completo las marcas y textos del eje derecho
                self.ax_phase.get_yaxis().set_visible(False)

            # Actualizar la leyenda unificada en base a las curvas visibles
            labs = [t.get_label() for t in trazos]
            self.ax_mag.legend(trazos, labs, facecolor='#3c3f41', edgecolor='#555555', loc='lower left')

            self.figure.tight_layout()
            self.canvas.draw()
            self.lbl_resultados.setText(texto_res)

        except ValueError:
            self.lbl_resultados.setText("<font color='#ff6b6b'><b>Error:</b> Valores inválidos.</font>")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = FiltroApp()
    ventana.show()
    sys.exit(app.exec_())

