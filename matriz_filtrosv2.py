#!/usr/bin/env python3

import sys
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView)

DARK_STYLE = """
QMainWindow { background-color: #2b2b2b; }
QWidget { background-color: #2b2b2b; color: #e0e0e0; font-family: sans-serif; font-size: 13px; }
QLineEdit { background-color: #3c3f41; border: 1px solid #555555; border-radius: 4px; padding: 4px; color: #ffffff; }
QComboBox { background-color: #3c3f41; border: 1px solid #555555; border-radius: 4px; padding: 4px; color: #ffffff; }
QPushButton { background-color: #28a745; color: white; border: none; border-radius: 4px; padding: 8px; font-weight: bold; }
QPushButton:hover { background-color: #218838; }
QTableWidget { background-color: #1e1e1e; color: #ffffff; border: 1px solid #555555; gridline-color: #333333; }
QHeaderView::section { background-color: #3c3f41; color: white; padding: 4px; border: 1px solid #555555; font-weight: bold; }
"""

# Valores base de la serie comercial de resistencias E24 (tolerancia típica del 5%)
VALORES_E24 = [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0, 
               3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1]

def buscar_resistencia_comercial(r_exacta):
    """Encuentra el valor comercial E24 más cercano para cualquier valor de resistencia."""
    if r_exacta <= 0: return 0
    # Determinar el exponente (década) de la resistencia
    exponente = int(np.floor(np.log10(r_exacta)))
    mantisa = r_exacta / (10 ** exponente)
    
    # Buscar el valor más cercano en la lista base E24
    mejor_base = min(VALORES_E24, key=lambda x: abs(x - mantisa))
    r_comercial = mejor_base * (10 ** exponente)
    return r_comercial

class MatrizFiltrosApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Matriz de Combinaciones RC Comerciales")
        self.setGeometry(100, 100, 950, 600)
        self.setStyleSheet(DARK_STYLE)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # Panel Izquierdo
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        control_panel.setFixedWidth(280)
        
        control_layout.addWidget(QLabel("<b>Frecuencia Objetivo (fc):</b>"))
        layout_fc = QHBoxLayout()
        self.txt_fc = QLineEdit("1000")
        self.unit_fc = QComboBox()
        self.unit_fc.addItems(["Hz", "kHz"])
        layout_fc.addWidget(self.txt_fc)
        layout_fc.addWidget(self.unit_fc)
        control_layout.addLayout(layout_fc)
        
        self.btn_calcular = QPushButton("Generar Combinaciones")
        self.btn_calcular.clicked.connect(self.generar_matriz)
        control_layout.addWidget(self.btn_calcular)
        
        lbl_nota = QLabel("<br>💡 <b>Nota:</b> La relación matemática fc = 1 / (2πRC) es idéntica tanto para configuraciones Pasa Alta como Pasa Baja de primer orden.")
        lbl_nota.setWordWrap(True)
        control_layout.addWidget(lbl_nota)
        control_layout.addStretch()
        
        # Panel Derecho: Tabla expandida a 5 columnas
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Capacitor", "Código", "R. Exacta", "R. Comercial (E24)", "fc Real (Error %)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        main_layout.addWidget(control_panel)
        main_layout.addWidget(self.table)
        
        self.lista_capacitores = [
            (1e-9, "102"), (1.5e-9, "152"), (2.2e-9, "222"), (3.3e-9, "332"), (4.7e-9, "472"), (6.8e-9, "682"),
            (10e-9, "103"), (15e-9, "153"), (22e-9, "223"), (33e-9, "333"), (47e-9, "473"), (68e-9, "683"),
            (100e-9, "104"), (220e-9, "224"), (330e-9, "334"), (470e-9, "474"), (680e-9, "684"),
            (1e-6, "105"), (2.2e-6, "225"), (4.7e-6, "475"), (10e-6, "106")
        ]
        
        self.generar_matriz()

    def formato_resistencia(self, r_val):
        """Convierte un valor numérico de resistencia a un formato legible con prefijos."""
        if r_val >= 1e6: return f"{r_val/1e6:.2f} MΩ"
        elif r_val >= 1000: return f"{r_val/1000:.2f} kΩ"
        return f"{r_val:.2f} Ω"

    def generar_matriz(self):
        try:
            raw_fc = float(self.txt_fc.text().replace(',', '.'))
            fc_objetivo = raw_fc * 1000 if self.unit_fc.currentText() == "kHz" else raw_fc
            if fc_objetivo <= 0: return
            
            self.table.setRowCount(0)
            
            for f_row, (C_val, C_code) in enumerate(self.lista_capacitores):
                # R exacta requerida
                R_exacta = 1 / (2 * np.pi * fc_objetivo * C_val)
                
                # R comercial más cercana
                R_comercial = buscar_resistencia_comercial(R_exacta)
                
                # Frecuencia real resultante y cálculo del error porcentual
                fc_real = 1 / (2 * np.pi * R_comercial * C_val)
                error_porcentual = ((fc_real - fc_objetivo) / fc_objetivo) * 100
                
                # CORRECCIÓN CUADRO ROJO: Formatear limpiando los decimales flotantes indeseados (ej: 15.0 nF en vez de 14.999...)
                if C_val >= 1e-6:
                    desc_cap = f"{round(C_val*1e6, 2)} µF"
                else:
                    desc_cap = f"{round(C_val*1e9, 2)} nF"
                
                # Formatear frecuencias para la última columna
                if fc_real >= 1000:
                    desc_f_real = f"{fc_real/1000:.2f} kHz"
                else:
                    desc_f_real = f"{fc_real:.1f} Hz"
                
                desc_error = f" ({'+' if error_porcentual >= 0 else ''}{error_porcentual:.1f}%)"
                
                # Llenar la fila
                self.table.insertRow(f_row)
                self.table.setItem(f_row, 0, QTableWidgetItem(desc_cap))
                self.table.setItem(f_row, 1, QTableWidgetItem(C_code))
                self.table.setItem(f_row, 2, QTableWidgetItem(self.formato_resistencia(R_exacta)))
                self.table.setItem(f_row, 3, QTableWidgetItem(self.formato_resistencia(R_comercial)))
                
                # Resaltar la última columna
                item_analisis = QTableWidgetItem(desc_f_real + desc_error)
                if abs(error_porcentual) > 7.0:
                    item_analisis.setForeground(np.array([255, 107, 107])) # Rojo suave si desvía mucho
                self.table.setItem(f_row, 4, item_analisis)
                
        except ValueError:
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MatrizFiltrosApp()
    ventana.show()
    sys.exit(app.exec_())

