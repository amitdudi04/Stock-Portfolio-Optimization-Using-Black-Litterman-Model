"""
Advanced Settings Dialog
========================

Additional configuration options for portfolio optimization.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
    QDoubleSpinBox, QCheckBox, QPushButton, QGroupBox, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class AdvancedSettingsDialog(QDialog):
    """Advanced settings dialog for fine-tuning optimizer parameters."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Advanced Settings")
        self.setGeometry(200, 200, 500, 400)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Advanced Optimization Parameters")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Black-Litterman parameters
        bl_group = QGroupBox("Black-Litterman Parameters")
        bl_layout = QVBoxLayout()
        
        # TAU parameter
        tau_layout = QHBoxLayout()
        tau_layout.addWidget(QLabel("TAU (Uncertainty Scalar):"))
        self.tau_spin = QDoubleSpinBox()
        self.tau_spin.setRange(0.001, 1.0)
        self.tau_spin.setValue(0.05)
        self.tau_spin.setSingleStep(0.01)
        tau_layout.addWidget(self.tau_spin)
        tau_help = QLabel("Controls confidence in market equilibrium. Lower = more confidence in market")
        tau_help.setStyleSheet("color: #666666; font-size: 8pt;")
        bl_layout.addLayout(tau_layout)
        bl_layout.addWidget(tau_help)
        
        # Lambda parameter
        lambda_layout = QHBoxLayout()
        lambda_layout.addWidget(QLabel("Lambda (Risk Aversion):"))
        self.lambda_spin = QDoubleSpinBox()
        self.lambda_spin.setRange(0.1, 10.0)
        self.lambda_spin.setValue(2.5)
        self.lambda_spin.setSingleStep(0.1)
        lambda_layout.addWidget(self.lambda_spin)
        lambda_help = QLabel("Investor risk aversion coefficient. Higher = more conservative")
        lambda_help.setStyleSheet("color: #666666; font-size: 8pt;")
        bl_layout.addLayout(lambda_layout)
        bl_layout.addWidget(lambda_help)
        
        bl_group.setLayout(bl_layout)
        layout.addWidget(bl_group)
        
        # Risk Metrics parameters
        risk_group = QGroupBox("Risk Metrics Parameters")
        risk_layout = QVBoxLayout()
        
        # VaR level
        var_layout = QHBoxLayout()
        var_layout.addWidget(QLabel("Value at Risk (VaR) Confidence Level:"))
        self.var_spin = QDoubleSpinBox()
        self.var_spin.setRange(0.90, 0.99)
        self.var_spin.setValue(0.95)
        self.var_spin.setSingleStep(0.01)
        var_layout.addWidget(self.var_spin)
        risk_layout.addLayout(var_layout)
        
        # Risk-free rate
        rf_layout = QHBoxLayout()
        rf_layout.addWidget(QLabel("Risk-Free Rate (annual):"))
        self.rf_spin = QDoubleSpinBox()
        self.rf_spin.setRange(0.0, 0.1)
        self.rf_spin.setValue(0.03)
        self.rf_spin.setSingleStep(0.001)
        self.rf_spin.setSuffix("%")
        rf_layout.addWidget(self.rf_spin)
        risk_layout.addLayout(rf_layout)
        
        risk_group.setLayout(risk_layout)
        layout.addWidget(risk_group)
        
        # Constraints
        constraint_group = QGroupBox("Portfolio Constraints")
        constraint_layout = QVBoxLayout()
        
        self.short_selling_check = QCheckBox("Allow Short Selling")
        constraint_layout.addWidget(self.short_selling_check)
        
        # Min/Max weights
        weights_layout = QHBoxLayout()
        weights_layout.addWidget(QLabel("Max Weight per Asset:"))
        self.max_weight_spin = QDoubleSpinBox()
        self.max_weight_spin.setRange(0.01, 1.0)
        self.max_weight_spin.setValue(1.0)
        self.max_weight_spin.setSingleStep(0.01)
        self.max_weight_spin.setSuffix("%")
        weights_layout.addWidget(self.max_weight_spin)
        constraint_layout.addLayout(weights_layout)
        
        constraint_group.setLayout(constraint_layout)
        layout.addWidget(constraint_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_to_defaults)
        btn_layout.addWidget(reset_btn)
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def reset_to_defaults(self):
        """Reset all parameters to default values."""
        self.tau_spin.setValue(0.05)
        self.lambda_spin.setValue(2.5)
        self.var_spin.setValue(0.95)
        self.rf_spin.setValue(0.03)
        self.short_selling_check.setChecked(False)
        self.max_weight_spin.setValue(1.0)
        QMessageBox.information(self, "Reset", "Parameters reset to default values.")
    
    def get_settings(self):
        """Get current settings as dictionary."""
        return {
            'tau': self.tau_spin.value(),
            'lambda': self.lambda_spin.value(),
            'var_level': self.var_spin.value(),
            'risk_free_rate': self.rf_spin.value() / 100.0,
            'allow_short_selling': self.short_selling_check.isChecked(),
            'max_weight': self.max_weight_spin.value()
        }
