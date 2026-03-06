import sys
import csv
import matplotlib
matplotlib.use('QtAgg')

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QLabel, QComboBox, QDoubleSpinBox, QSpinBox, 
    QPushButton, QGroupBox, QTableWidget, QTableWidgetItem, 
    QHeaderView, QDateEdit, QFormLayout, QSplitter, QFileDialog, QMessageBox, QAbstractSpinBox
)
from PyQt6.QtCore import Qt, QDate
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Core Engine
from pipelines.dual_market import evaluate_dual_market, MARKET_CONFIG, TICKER_NAME_MAP
from ui.plot_utils import COLORS, apply_modern_theme, apply_figure_theme

class DateSelector(QWidget):
    """Custom built date selector bypassing native Calendar bugs"""
    def __init__(self, default_date: QDate, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        self.year_cb = QComboBox()
        self.month_cb = QComboBox()
        self.day_cb = QComboBox()
        
        # Style to fit the theme explicitly
        cb_style = f"background-color: {COLORS['panel']}; color: {COLORS['text']}; border: 1px solid {COLORS['border']}; border-radius: 3px; padding: 2px;"
        self.year_cb.setStyleSheet(cb_style)
        self.month_cb.setStyleSheet(cb_style)
        self.day_cb.setStyleSheet(cb_style)
        
        # Populate only valid empirical years
        current_year = QDate.currentDate().year()
        self.year_cb.addItems([str(y) for y in range(2005, current_year + 1)])
        self.month_cb.addItems([f"{m:02d}" for m in range(1, 13)])
        self.day_cb.addItems([f"{d:02d}" for d in range(1, 32)])
        
        # Layout Order: Year-Month-Day
        layout.addWidget(self.year_cb, 2)
        layout.addWidget(QLabel("-"))
        layout.addWidget(self.month_cb, 1)
        layout.addWidget(QLabel("-"))
        layout.addWidget(self.day_cb, 1)
        
        self.year_cb.currentIndexChanged.connect(self.update_days)
        self.month_cb.currentIndexChanged.connect(self.update_days)
        
        self.setDate(default_date)
        
    def update_days(self):
        y = int(self.year_cb.currentText())
        m = int(self.month_cb.currentText())
        d = int(self.day_cb.currentText())
        days_in_month = QDate(y, m, 1).daysInMonth()
        
        self.day_cb.blockSignals(True)
        self.day_cb.clear()
        self.day_cb.addItems([f"{i:02d}" for i in range(1, days_in_month + 1)])
        if d <= days_in_month:
            self.day_cb.setCurrentText(f"{d:02d}")
        else:
            self.day_cb.setCurrentText(f"{days_in_month:02d}")
        self.day_cb.blockSignals(False)
        
    def setDate(self, qdate: QDate):
        self.year_cb.setCurrentText(str(qdate.year()))
        self.month_cb.setCurrentText(f"{qdate.month():02d}")
        self.update_days()
        self.day_cb.setCurrentText(f"{qdate.day():02d}")
        
    def date(self) -> QDate:
        y = int(self.year_cb.currentText())
        m = int(self.month_cb.currentText())
        d = int(self.day_cb.currentText())
        return QDate(y, m, d)


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        plt.style.use('dark_background')
        self.fig = plt.Figure(figsize=(width, height), dpi=dpi)
        apply_figure_theme(self.fig)
        super(MplCanvas, self).__init__(self.fig)

class ModernDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        # Title tuned to the current empirical engine naming (include India)
        self.setWindowTitle("Empirical Evaluation Engine — US Developed, China Emerging, India Emerging")
        self.resize(1400, 900)
        self.apply_dark_theme()
        
        self.results = None
        self.current_market = "US"
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        left_panel = self.create_control_panel()
        splitter.addWidget(left_panel)
        
        right_panel = self.create_display_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([300, 1100])
        
    def apply_dark_theme(self):
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {COLORS['bg']};
                color: {COLORS['text']};
                font-family: 'Inter', 'Segoe UI', Arial;
            }}
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: {COLORS['secondary']};
            }}
            QPushButton {{
                background-color: {COLORS['primary']};
                color: {COLORS['bg']};
                font-weight: bold;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
            }}
            QPushButton:hover {{
                background-color: #f5a0b9;
            }}
            QTabWidget::pane {{
                border: 1px solid {COLORS['border']};
            }}
            QTabBar::tab {{
                background-color: {COLORS['panel']};
                color: {COLORS['text']};
                padding: 8px 15px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['secondary']};
                color: {COLORS['bg']};
                font-weight: bold;
            }}
            QTableWidget {{
                background-color: {COLORS['panel']};
                alternate-background-color: {COLORS['bg']};
                gridline-color: {COLORS['border']};
                border: 1px solid {COLORS['border']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['panel']};
                color: {COLORS['secondary']};
                font-weight: bold;
                border: 1px solid {COLORS['border']};
                padding: 4px;
            }}
            QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {{
                background-color: {COLORS['panel']};
                border: 1px solid {COLORS['border']};
                border-radius: 3px;
                padding: 4px;
                color: {COLORS['text']};
            }}

            QCalendarWidget QWidget {{
                alternate-background-color: {COLORS['panel']};
                color: {COLORS['text']};
            }}
        """)
        
    def wrap_with_buttons(self, spinbox):
        spinbox.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        spinbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        btn_minus = QPushButton("-")
        btn_plus = QPushButton("+")
        btn_minus.setFixedSize(28, 28)
        btn_plus.setFixedSize(28, 28)
        
        btn_style = f"""
            QPushButton {{
                background-color: {COLORS['panel']}; 
                color: {COLORS['primary']}; 
                border: 1px solid {COLORS['border']}; 
                border-radius: 4px; 
                font-weight: bold; 
                font-size: 18px;
                padding: 0px;
                margin: 0px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['border']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['primary']};
                color: {COLORS['bg']};
            }}
        """
        btn_minus.setStyleSheet(btn_style)
        btn_plus.setStyleSheet(btn_style)
        
        # Connect clicking to stepping the value up or down
        btn_minus.clicked.connect(spinbox.stepDown)
        btn_plus.clicked.connect(spinbox.stepUp)
        
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addWidget(btn_minus)
        layout.addWidget(spinbox)
        layout.addWidget(btn_plus)
        return container
        
    def create_control_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 10, 0)
        
        group_market = QGroupBox("Market Context")
        form_market = QFormLayout()
        self.market_selector = QComboBox()
        self.market_selector.addItems(["US", "CHINA", "INDIA", "TRI-MARKET"])
        form_market.addRow("Select Market:", self.market_selector)
        group_market.setLayout(form_market)
        layout.addWidget(group_market)
        
        group_date = QGroupBox("Horizon")
        form_date = QFormLayout()
        self.start_date = DateSelector(QDate(2010, 1, 1))
        self.end_date = DateSelector(QDate(2025, 1, 1))
        
        form_date.addRow("Start Date:", self.start_date)
        form_date.addRow("End Date:", self.end_date)
        group_date.setLayout(form_date)
        layout.addWidget(group_date)
        
        group_params = QGroupBox("Black-Litterman Parameters")
        form_params = QFormLayout()
        self.tau_slider = QDoubleSpinBox()
        self.tau_slider.setRange(0.01, 1.0)
        self.tau_slider.setSingleStep(0.01)
        self.tau_slider.setValue(0.05)
        self.lambda_slider = QDoubleSpinBox()
        self.lambda_slider.setRange(1.0, 10.0)
        self.lambda_slider.setSingleStep(0.1)
        self.lambda_slider.setValue(2.5)
        form_params.addRow("Tau (τ):", self.wrap_with_buttons(self.tau_slider))
        form_params.addRow("Risk Aversion (λ):", self.wrap_with_buttons(self.lambda_slider))
        group_params.setLayout(form_params)
        layout.addWidget(group_params)
        
        group_fric = QGroupBox("Market Friction")
        form_fric = QFormLayout()
        self.trans_cost = QDoubleSpinBox()
        self.trans_cost.setRange(0.0, 0.05)
        self.trans_cost.setSingleStep(0.001)
        self.trans_cost.setDecimals(4)
        self.trans_cost.setValue(0.001)
        self.rebal_freq = QSpinBox()
        self.rebal_freq.setRange(5, 252)
        self.rebal_freq.setValue(63)
        form_fric.addRow("Trade Cost (rate):", self.wrap_with_buttons(self.trans_cost))
        form_fric.addRow("Rebalance (days):", self.wrap_with_buttons(self.rebal_freq))
        group_fric.setLayout(form_fric)
        layout.addWidget(group_fric)
        
        layout.addStretch()
        self.btn_run = QPushButton("RUN EMPIRICAL ANALYSIS")
        self.btn_run.setFixedHeight(45)
        self.btn_run.clicked.connect(self.run_analysis)
        layout.addWidget(self.btn_run)
        
        return panel

    def build_export_button(self, table, default_name):
        btn = QPushButton("Export to CSV")
        btn.clicked.connect(lambda: self.export_table_to_csv(table, default_name))
        return btn

    def export_table_to_csv(self, table, default_name):
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", default_name, "CSV Files (*.csv)")
        if path:
            try:
                with open(path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    # Write Headers
                    headers = []
                    if table.verticalHeader().isVisible():
                        headers.append("RowName")
                    for c in range(table.columnCount()):
                        item = table.horizontalHeaderItem(c)
                        headers.append(item.text() if item else str(c))
                    writer.writerow(headers)
                    
                    # Write Data
                    for r in range(table.rowCount()):
                        row_data = []
                        if table.verticalHeader().isVisible():
                            vitem = table.verticalHeaderItem(r)
                            row_data.append(vitem.text() if vitem else str(r))
                        
                        for c in range(table.columnCount()):
                            item = table.item(r, c)
                            row_data.append(item.text() if item else "")
                        writer.writerow(row_data)
                QMessageBox.information(self, "Export Successful", f"Data exported to {path}")
            except Exception as e:
                QMessageBox.warning(self, "Export Failed", str(e))

    def create_display_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = QTabWidget()
        
        self.tab_us = QWidget()
        self.tab_cn = QWidget()
        self.tab_in = QWidget()
        self.tab_comp = QWidget()
        self.tab_robust = QWidget()
        self.tab_stress = QWidget()
        self.tab_soe = QWidget()
        self.tab_stats = QWidget()
        
        self.setup_market_tab(self.tab_us, "US")
        self.setup_market_tab(self.tab_cn, "CHINA")
        self.setup_market_tab(self.tab_in, "INDIA")
        self.setup_comparison_tab(self.tab_comp)
        self.setup_robustness_tab(self.tab_robust)
        self.setup_stress_tab(self.tab_stress)
        self.setup_soe_tab(self.tab_soe)
        self.setup_stats_tab(self.tab_stats)
        
        self.tabs.addTab(self.tab_us, "US Market")
        self.tabs.addTab(self.tab_cn, "China Market")
        self.tabs.addTab(self.tab_in, "India Market")
        self.tabs.addTab(self.tab_comp, "Tri-Market Structural Analysis")
        self.tabs.addTab(self.tab_robust, "Robustness Analysis")
        self.tabs.addTab(self.tab_stress, "Crisis Stress Tests")
        self.tabs.addTab(self.tab_soe, "China SOE vs Private Study")
        self.tabs.addTab(self.tab_stats, "Formal Statistical Validation")
        
        layout.addWidget(self.tabs)
        return panel

    def setup_market_tab(self, tab, market_name):
        layout = QVBoxLayout(tab)
        
        canvas = MplCanvas(self, width=8, height=4, dpi=100)
        layout.addWidget(canvas, stretch=2)
        
        if market_name == "US":
            self.canvas_us = canvas
        elif market_name == "CHINA":
            self.canvas_cn = canvas
        else:
            self.canvas_in = canvas
            
        bottom_layout = QHBoxLayout()
        
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Annual Return", "Volatility", "Sharpe Ratio", 
            "Information Ratio", "Max Drawdown", "Avg Turnover"
        ])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.setFixedHeight(140)
        
        weights_table = QTableWidget()
        weights_table.setColumnCount(4)
        weights_table.setHorizontalHeaderLabels([
            "Ticker", "Company", "Weight (BL)", "Expected Return"
        ])
        weights_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        weights_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        weights_table.setAlternatingRowColors(True)
        weights_table.setFixedHeight(140)
        
        bottom_layout.addWidget(table, stretch=1)
        bottom_layout.addWidget(weights_table, stretch=1)
        
        layout.addLayout(bottom_layout)
        
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(self.build_export_button(table, f"{market_name}_metrics.csv"))
        h_layout.addWidget(self.build_export_button(weights_table, f"{market_name}_allocation.csv"))
        
        layout.addLayout(h_layout)
        
        if market_name == "US":
            self.table_us = table
            self.weights_us = weights_table
        elif market_name == "CHINA":
            self.table_cn = table
            self.weights_cn = weights_table
        else:
            self.table_in = table
            self.weights_in = weights_table

    def setup_comparison_tab(self, tab):
        layout = QVBoxLayout(tab)
        self.canvas_comp = MplCanvas(self, width=10, height=8, dpi=100)
        layout.addWidget(self.canvas_comp, stretch=3)
        
        self.table_comp = QTableWidget()
        self.table_comp.setColumnCount(8)
        self.table_comp.setHorizontalHeaderLabels([
            "Market", "Model", "Annual Return", "Volatility", 
            "Sharpe", "IR", "Max Drawdown", "Turnover"
        ])
        self.table_comp.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_comp.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_comp.setAlternatingRowColors(True)
        layout.addWidget(self.table_comp, stretch=1)
        
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(self.build_export_button(self.table_comp, "cross_market_comparison.csv"))
        layout.addLayout(h_layout)

    def setup_robustness_tab(self, tab):
        layout = QVBoxLayout(tab)
        self.canvas_robust = MplCanvas(self, width=8, height=6, dpi=100)
        layout.addWidget(self.canvas_robust, stretch=2)
        
        self.table_robust = QTableWidget()
        self.table_robust.setColumnCount(4) # Market, Tau, ER, Sharpe
        self.table_robust.setHorizontalHeaderLabels(["Market", "Tau (τ)", "Expected Return", "Sharpe Ratio"])
        self.table_robust.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_robust.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_robust.setAlternatingRowColors(True)
        layout.addWidget(self.table_robust, stretch=1)
        
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(self.build_export_button(self.table_robust, "robustness_analysis.csv"))
        layout.addLayout(h_layout)

    def setup_stress_tab(self, tab):
        layout = QVBoxLayout(tab)
        self.canvas_stress = MplCanvas(self, width=8, height=6, dpi=100)
        layout.addWidget(self.canvas_stress, stretch=2)
        
        self.table_stress = QTableWidget()
        self.table_stress.setColumnCount(4)
        self.table_stress.setHorizontalHeaderLabels([
            "Structural Metric", "US Market", "China Market", "India Market"
        ])
        self.table_stress.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_stress.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_stress.setAlternatingRowColors(True)
        layout.addWidget(self.table_stress, stretch=1)
        
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(self.build_export_button(self.table_stress, "stress_test_analysis.csv"))
        layout.addLayout(h_layout)

    def setup_soe_tab(self, tab):
        layout = QVBoxLayout(tab)
        self.canvas_soe = MplCanvas(self, width=8, height=4, dpi=100)
        layout.addWidget(self.canvas_soe, stretch=2)
        
        self.table_soe = QTableWidget()
        self.table_soe.setColumnCount(6)
        self.table_soe.setHorizontalHeaderLabels([
            "Cohort", "Ann. Return", "Volatility", "Sharpe", "Max Drawdown", "ASI (Drift)"
        ])
        self.table_soe.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_soe.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_soe.setAlternatingRowColors(True)
        self.table_soe.setFixedHeight(120)
        
        layout.addWidget(self.table_soe, stretch=1)
        
        self.label_soe_tests = QLabel("Structural Validation: Run Tri-Market or China to populate SOE Hypothesis Tests")
        self.label_soe_tests.setStyleSheet(f"color: {COLORS['secondary']}; font-weight: bold; font-size: 14px;")
        layout.addWidget(self.label_soe_tests)
        
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(self.build_export_button(self.table_soe, "china_soe_private_study.csv"))
        layout.addLayout(h_layout)

    def setup_stats_tab(self, tab):
        layout = QVBoxLayout(tab)
        
        desc = QLabel("Formal Non-Stationary Bootstrap and Analytical P-Values for Black-Litterman Outperformance")
        desc.setStyleSheet(f"color: {COLORS['text']}; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        self.table_stats = QTableWidget()
        self.table_stats.setColumnCount(3)
        self.table_stats.setHorizontalHeaderLabels([
            "Market (BL vs Markowitz)", "Circular Block Bootstrap (p-value)", "Jobson-Korkie (p-value)"
        ])
        self.table_stats.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_stats.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_stats.setAlternatingRowColors(True)
        
        layout.addWidget(self.table_stats, stretch=3)
        
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(self.build_export_button(self.table_stats, "statistical_validation.csv"))
        layout.addLayout(h_layout)

    def run_analysis(self):
        self.btn_run.setText("COMPUTING...")
        self.btn_run.setEnabled(False)
        self.btn_run.setStyleSheet(f"background-color: {COLORS['border']}; color: gray;")
        QApplication.processEvents()
        
        try:
            import copy
            config = copy.deepcopy(MARKET_CONFIG)
            
            # Extract values from GUI 
            # Note: We use .date().toString() on the custom DateSelector
            start_date_str = self.start_date.date().toString("yyyy-MM-dd")
            end_date_str = self.end_date.date().toString("yyyy-MM-dd")
            tau_val = self.tau_slider.value()
            lam_val = self.lambda_slider.value()
            tc_val = self.trans_cost.value()
            rebal_val = self.rebal_freq.value()
            
            selected_market = self.market_selector.currentText()
            markets_to_run = ["US", "CHINA", "INDIA"] if selected_market == "TRI-MARKET" else [selected_market]
            
            # Sub-select config
            eval_config = {k: config[k] for k in markets_to_run if k in config}
            
            # Inject dynamic UI updates into relevant market configs
            for mk in eval_config.keys():
                eval_config[mk]["start"] = start_date_str
                eval_config[mk]["end"] = end_date_str
                eval_config[mk]["tau_override"] = tau_val
                eval_config[mk]["lambda_override"] = lam_val
                eval_config[mk]["trade_cost_override"] = tc_val
                eval_config[mk]["rebalance_days_override"] = rebal_val

            self.results = evaluate_dual_market(eval_config)
            
            if "US" in eval_config:
                self.update_market_tab("US", self.canvas_us, self.table_us, self.weights_us)
            if "CHINA" in eval_config:
                self.update_market_tab("CHINA", self.canvas_cn, self.table_cn, self.weights_cn)
            if "INDIA" in eval_config:
                self.update_market_tab("INDIA", self.canvas_in, self.table_in, self.weights_in)
                
            self.update_comparison_tab()
            self.update_robustness_tab()
            self.update_stress_tab()
            self.update_soe_tab()
            self.update_stats_tab()
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Error during analysis: {e}")
            
        finally:
            self.btn_run.setText("RUN EMPIRICAL ANALYSIS")
            self.btn_run.setEnabled(True)
            self.btn_run.setStyleSheet(f"background-color: {COLORS['primary']}; color: {COLORS['bg']};")

    def update_market_tab(self, market, canvas, table, weights_table):
        if not self.results: return
        res = self.results["raw_results"][market]
        
        fig = canvas.fig
        fig.clf()
        ax = fig.add_subplot(111)
        
        cum = res["backtest_series"]
        ax.plot(cum["bl_cum"], label='Black-Litterman Net', color=COLORS['primary'], linewidth=2)
        ax.plot(cum["mw_cum"], label='Markowitz Net', color=COLORS['secondary'], linewidth=1.5, linestyle='--')
        ax.plot(cum["bench_cum"], label='Benchmark', color=COLORS['benchmark'], linewidth=1.5, alpha=0.8)
        
        apply_modern_theme(ax, f"{market} Market Cumulative Returns")
        ax.legend(frameon=False, labelcolor=COLORS['text'])
        fig.tight_layout(pad=2.0)
        canvas.draw()
        
        table.setRowCount(3)
        table.setVerticalHeaderLabels(["Black-Litterman", "Markowitz", "Benchmark"])
        
        p = res["performance"]
        bl_data = [f"{p['bl_ret']*100:.2f}%", f"{p['bl_vol']*100:.2f}%", f"{p['bl_sharpe']:.3f}", f"{p['bl_ir']:.3f}", f"{p['bl_dd']*100:.2f}%", f"{p['bl_turn']*100:.2f}%"]
        mw_data = [f"{p['mw_ret']*100:.2f}%", f"{p['mw_vol']*100:.2f}%", f"{p['mw_sharpe']:.3f}", f"{p['mw_ir']:.3f}", f"{p['mw_dd']*100:.2f}%", f"{p['mw_turn']*100:.2f}%"]
        bh_data = [f"{p['bench_ret']*100:.2f}%", f"{p['bench_vol']*100:.2f}%", f"{p['bench_sharpe']:.3f}", "N/A", f"{p['bench_dd']*100:.2f}%", "N/A"]
        
        for r, row_data in enumerate([bl_data, mw_data, bh_data]):
            for c, val in enumerate(row_data):
                table.setItem(r, c, QTableWidgetItem(val))
                
        # Populate Weights Table
        baseline_dict = res["baseline"]
        bl_weights = baseline_dict['black_litterman']['weights']
        # The ordering of weights from the optimizer matches the original tickers order initialized
        tickers = MARKET_CONFIG[market]["tickers"]
        views = MARKET_CONFIG[market]["views"]
        
        weights_table.setRowCount(len(tickers))
        for r, ticker in enumerate(tickers):
            company_name = TICKER_NAME_MAP.get(ticker, ticker)
            
            er = views.get(ticker, None)
            er_text = f"{er*100:.2f}%" if er is not None else "N/A"
            
            weights_table.setItem(r, 0, QTableWidgetItem(str(ticker)))
            weights_table.setItem(r, 1, QTableWidgetItem(company_name))
            weights_table.setItem(r, 2, QTableWidgetItem(f"{bl_weights[r]*100:.2f}%"))
            weights_table.setItem(r, 3, QTableWidgetItem(er_text))

    def update_comparison_tab(self):
        if not self.results: return
        res_map = self.results["raw_results"]
        if "US" not in res_map or "CHINA" not in res_map or "INDIA" not in res_map:
            return  # Need all 3 for Tri-Market comp
            
        us_res = res_map["US"]
        cn_res = res_map["CHINA"]
        in_res = res_map["INDIA"]
        
        fig = self.canvas_comp.fig
        fig.clf()
        axs = fig.subplots(2, 2)
        
        # 1. Cumulative Return Comparison (US BL vs CN BL vs IN BL)
        axs[0,0].plot(us_res["backtest_series"]["bl_cum"], color=COLORS['primary'], label='US (BL)')
        axs[0,0].plot(cn_res["backtest_series"]["bl_cum"], color=COLORS['secondary'], label='China (BL)')
        axs[0,0].plot(in_res["backtest_series"]["bl_cum"], color=COLORS['accent'], label='India (BL)')
        apply_modern_theme(axs[0,0], "Tri-Market Cum. Returns (BL Net)")
        axs[0,0].legend(frameon=False, labelcolor=COLORS['text'])
        
        # 2. Sharpe Ratio Bar Chart
        labels = ['US', 'CHINA', 'INDIA']
        bl_sharpes = [us_res["performance"]["bl_sharpe"], cn_res["performance"]["bl_sharpe"], in_res["performance"]["bl_sharpe"]]
        mw_sharpes = [us_res["performance"]["mw_sharpe"], cn_res["performance"]["mw_sharpe"], in_res["performance"]["mw_sharpe"]]
        x = np.arange(len(labels))
        width = 0.35
        
        axs[0,1].bar(x - width/2, bl_sharpes, width, label='Black-Litterman', color=COLORS['primary'])
        axs[0,1].bar(x + width/2, mw_sharpes, width, label='Markowitz', color=COLORS['secondary'])
        axs[0,1].set_xticks(x)
        axs[0,1].set_xticklabels(labels)
        apply_modern_theme(axs[0,1], "Out-of-Sample Sharpe Ratios")
        axs[0,1].legend(frameon=False, labelcolor=COLORS['text'])
        
        # 3. Max Drawdown Comparison
        bl_dd = [us_res["performance"]["bl_dd"]*100, cn_res["performance"]["bl_dd"]*100, in_res["performance"]["bl_dd"]*100]
        mw_dd = [us_res["performance"]["mw_dd"]*100, cn_res["performance"]["mw_dd"]*100, in_res["performance"]["mw_dd"]*100]
        axs[1,0].bar(x - width/2, bl_dd, width, label='Black-Litterman', color=COLORS['primary'])
        axs[1,0].bar(x + width/2, mw_dd, width, label='Markowitz', color=COLORS['secondary'])
        axs[1,0].set_xticks(x)
        axs[1,0].set_xticklabels(labels)
        axs[1,0].invert_yaxis()
        apply_modern_theme(axs[1,0], "Maximum Drawdown (%)")
        axs[1,0].legend(frameon=False, labelcolor=COLORS['text'])
        
        # 4. Crisis Volatility Spike Comparison
        bl_spike = [us_res["stress"]["black_litterman"]["Volatility Spike (x)"],
                    cn_res["stress"]["black_litterman"]["Volatility Spike (x)"],
                    in_res["stress"]["black_litterman"]["Volatility Spike (x)"]]
        mw_spike = [us_res["stress"]["markowitz"]["Volatility Spike (x)"],
                    cn_res["stress"]["markowitz"]["Volatility Spike (x)"],
                    in_res["stress"]["markowitz"]["Volatility Spike (x)"]]
        axs[1,1].bar(x - width/2, bl_spike, width, label='Black-Litterman', color=COLORS['primary'])
        axs[1,1].bar(x + width/2, mw_spike, width, label='Markowitz', color=COLORS['secondary'])
        axs[1,1].set_xticks(x)
        axs[1,1].set_xticklabels(labels)
        apply_modern_theme(axs[1,1], "Vol Spikes (x) vs Pre-Crisis Base")
        axs[1,1].legend(frameon=False, labelcolor=COLORS['text'])
        
        fig.tight_layout(pad=3.5)
        fig.subplots_adjust(hspace=0.5, wspace=0.3)
        self.canvas_comp.draw()
        
        df = self.results["summary_df"]
        self.table_comp.setRowCount(len(df))
        for r, row in df.iterrows():
            for c, val in enumerate(row):
                self.table_comp.setItem(r, c, QTableWidgetItem(str(val)))

    def update_robustness_tab(self):
        if not self.results: return
        
        fig = self.canvas_robust.fig
        fig.clf()
        ax = fig.add_subplot(111)
        
        res_map = self.results["raw_results"]
        
        colors_map = {
            "US": COLORS['primary'],
            "CHINA": COLORS['secondary'],
            "INDIA": COLORS['accent']
        }
        
        table_rows = []
        for market in ["US", "CHINA", "INDIA"]:
            if market in res_map:
                tau_df = res_map[market]["tau"]
                ax.plot(tau_df.index, tau_df["Sharpe Ratio"], color=colors_map[market], marker='o', linewidth=2, label=f'{market} Sharpe')
                
                for idx, row in tau_df.iterrows():
                    table_rows.append({
                        "Market": market,
                        "Tau": f"{idx:.3f}",
                        "ER": f"{row['Expected Return']*100:.2f}%",
                        "Sharpe": f"{row['Sharpe Ratio']:.3f}"
                    })
        
        apply_modern_theme(ax, "Cross-Market Tau Sensitivity (Sharpe Ratio)")
        ax.set_ylabel("Sharpe Ratio")
        ax.set_xlabel("Tau (τ)")
        ax.legend(frameon=False, labelcolor=COLORS['text'])
        
        fig.tight_layout(pad=2.0)
        self.canvas_robust.draw()
        
        self.table_robust.setRowCount(len(table_rows))
        for r, row_data in enumerate(table_rows):
            self.table_robust.setItem(r, 0, QTableWidgetItem(row_data["Market"]))
            self.table_robust.setItem(r, 1, QTableWidgetItem(row_data["Tau"]))
            self.table_robust.setItem(r, 2, QTableWidgetItem(row_data["ER"]))
            self.table_robust.setItem(r, 3, QTableWidgetItem(row_data["Sharpe"]))

    def update_stress_tab(self):
        if not self.results: return
        
        df = self.results["structural_df"]
        
        fig = self.canvas_stress.fig
        fig.clf()
        ax = fig.add_subplot(111)
        
        res_map = self.results["raw_results"]
        if "US" in res_map and "CHINA" in res_map and "INDIA" in res_map:
            # Simple bar comparison of drawdowns 
            labels = ["US 2008", "China 2015", "India 2008"]
            us_dd = res_map["US"]["stress"]["black_litterman"]["Max Drawdown"] * 100
            cn_dd = res_map["CHINA"]["stress"]["black_litterman"]["Max Drawdown"] * 100
            in_dd = res_map["INDIA"]["stress"]["black_litterman"]["Max Drawdown"] * 100
            
            ax.bar(labels, [us_dd, cn_dd, in_dd], color=[COLORS['primary'], COLORS['secondary'], COLORS['accent']])
            apply_modern_theme(ax, "Maximum Crisis Drawdown (BL Model)")
            ax.set_ylabel("Drawdown (%)")
        
        fig.tight_layout(pad=2.0)
        self.canvas_stress.draw()
        
        self.table_stress.setRowCount(len(df))
        for r, (idx, row) in enumerate(df.iterrows()):
            self.table_stress.setItem(r, 0, QTableWidgetItem(str(row["Structural Metric"])))
            
            has_us = "US Market" in row
            has_cn = "China Market" in row
            has_in = "India Market" in row
            
            if has_us: self.table_stress.setItem(r, 1, QTableWidgetItem(str(row["US Market"])))
            if has_cn: self.table_stress.setItem(r, 2, QTableWidgetItem(str(row["China Market"])))
            if has_in: self.table_stress.setItem(r, 3, QTableWidgetItem(str(row["India Market"])))

    def update_soe_tab(self):
        if not self.results: return
        soe_study = self.results.get("soe_study")
        if not soe_study:
            self.label_soe_tests.setText("China market not executed. Select China or Tri-Market to run the SOE structural sub-study.")
            return
            
        fig = self.canvas_soe.fig
        fig.clf()
        ax = fig.add_subplot(111)
        
        s_res = soe_study["soe"]
        p_res = soe_study["private"]
        
        if s_res.get("net_returns") is None or p_res.get("net_returns") is None:
            raise ValueError("Missing 'net_returns' in SOE or Private analysis results.")
        if len(s_res["net_returns"]) == 0 or len(p_res["net_returns"]) == 0:
            raise ValueError("Empty DataFrame assigned to table model for SOE/Private study.")
        
        s_cum = (1 + s_res["net_returns"]).cumprod()
        p_cum = (1 + p_res["net_returns"]).cumprod()
        
        ax.plot(s_cum, label='State-Owned Enterprises (BL)', color=COLORS['secondary'], linewidth=2)
        ax.plot(p_cum, label='Private Enterprises (BL)', color=COLORS['accent'], linewidth=2, linestyle='--')
        
        apply_modern_theme(ax, "Structural Ownership: Cumulative Returns")
        ax.legend(frameon=False, labelcolor=COLORS['text'])
        fig.tight_layout(pad=2.0)
        self.canvas_soe.draw()
        
        self.table_soe.setRowCount(2)
        
        sm = s_res["metrics"]
        pm = p_res["metrics"]
        
        self.table_soe.setItem(0, 0, QTableWidgetItem("State-Owned Enterprises"))
        self.table_soe.setItem(0, 1, QTableWidgetItem(f"{sm['annualized_net_return']*100:.2f}%"))
        self.table_soe.setItem(0, 2, QTableWidgetItem(f"{sm['annualized_volatility']*100:.2f}%"))
        self.table_soe.setItem(0, 3, QTableWidgetItem(f"{sm['sharpe']:.3f}"))
        self.table_soe.setItem(0, 4, QTableWidgetItem(f"{sm['max_drawdown']*100:.2f}%"))
        self.table_soe.setItem(0, 5, QTableWidgetItem(f"{sm['asi']:.4f}"))

        self.table_soe.setItem(1, 0, QTableWidgetItem("Private Enterprises"))
        self.table_soe.setItem(1, 1, QTableWidgetItem(f"{pm['annualized_net_return']*100:.2f}%"))
        self.table_soe.setItem(1, 2, QTableWidgetItem(f"{pm['annualized_volatility']*100:.2f}%"))
        self.table_soe.setItem(1, 3, QTableWidgetItem(f"{pm['sharpe']:.3f}"))
        self.table_soe.setItem(1, 4, QTableWidgetItem(f"{pm['max_drawdown']*100:.2f}%"))
        self.table_soe.setItem(1, 5, QTableWidgetItem(f"{pm['asi']:.4f}"))
        
        t = soe_study["tests"]
        txt = (f"Null Hypothesis Validations:\n"
               f"H0 (Equal Volatility): p-value = {t['vol_p_value']:.4f}\n"
               f"H0 (Equal Allocation Drift ASI): p-value = {t['asi_p_value']:.4f}")
        self.label_soe_tests.setText(txt)

    def update_stats_tab(self):
        if not self.results: return
        stats = self.results.get("statistical_tests", {})
        
        self.table_stats.setRowCount(len(stats))
        for r, (market, res) in enumerate(stats.items()):
            self.table_stats.setItem(r, 0, QTableWidgetItem(market))
            
            p_boot = res.get("bootstrap_p", float('nan'))
            p_jk = res.get("jobson_korkie_p", float('nan'))
            
            b_text = f"{p_boot:.4f} {'(Significant ★)' if p_boot < 0.05 else ''}" if not np.isnan(p_boot) else "N/A"
            j_text = f"{p_jk:.4f} {'(Significant ★)' if p_jk < 0.05 else ''}" if not np.isnan(p_jk) else "N/A"
            
            self.table_stats.setItem(r, 1, QTableWidgetItem(b_text))
            self.table_stats.setItem(r, 2, QTableWidgetItem(j_text))

def launch_desktop_gui():
    app = QApplication(sys.argv)
    window = ModernDashboard()
    window.show()
    sys.exit(app.exec())
