"""
PyQt5 Desktop GUI for Portfolio Optimization
=============================================

Professional desktop application for Black-Litterman portfolio optimization.
"""

import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List
import numpy as np
import pandas as pd
from io import BytesIO
import matplotlib.pyplot as plt
plt.style.use('dark_background')  # Sleek dark plots
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QMessageBox, QStatusBar,
    QProgressDialog, QFileDialog, QFrame, QCheckBox, QSlider, QScrollArea,
    QHeaderView
)
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
    from reportlab.lib.units import inch
    from reportlab.lib import colors
except ImportError:
    pass

# Add portfolio_optimization to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from portfolio_optimization.models import (
    BlackLittermanOptimizer, RiskMetricsCalculator, PortfolioVisualizer
)
from portfolio_optimization.config import config


class OptimizationWorker(QThread):
    """Background worker for optimization calculations."""
    
    finished = pyqtSignal()
    error = pyqtSignal(str)
    results_ready = pyqtSignal(dict)
    
    def __init__(self, tickers, start_date, end_date, views, confidence):
        super().__init__()
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.views = views
        self.confidence = confidence
        self.results = None
    
    def run(self):
        """Run optimization in background thread."""
        try:
            print(f"\n{'='*60}")
            print("Starting Optimization...")
            print(f"{'='*60}")
            print(f"Tickers: {self.tickers}")
            print(f"Date range: {self.start_date} to {self.end_date}")
            print(f"Views: {self.views}")
            print(f"Confidence: {self.confidence}")
            
            # Initialize optimizer
            print("\nInitializing optimizer...")
            optimizer = BlackLittermanOptimizer(
                ticker_list=self.tickers,
                start_date=self.start_date,
                end_date=self.end_date,
                risk_free_rate=0.03
            )
            
            # Run comparison
            print("Running optimization...")
            results = optimizer.compare_models(self.views, self.confidence if self.confidence else None)
            
            print(f"\n✓ Optimization completed successfully")
            self.results = results
            self.results_ready.emit(results)
            self.finished.emit()
        except Exception as e:
            import traceback
            error_msg = f"Optimization Error: {str(e)}\n\nDetails:\n{traceback.format_exc()}"
            print(f"\n✗ Optimization failed:")
            print(error_msg)
            self.error.emit(f"Optimization Error: {str(e)}")
            self.finished.emit()


class PortfolioGUI(QMainWindow):
    """Main GUI window for portfolio optimization."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Portfolio Optimization System - Black-Litterman Model")
        self.setGeometry(100, 100, 1400, 900)
        
        # Style setup
        self.setup_styles()
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Create tabs
        self.config_tab = self.create_config_tab()
        self.views_tab = self.create_views_tab()
        self.results_tab = self.create_results_tab()
        self.analysis_tab = self.create_analysis_tab()
        
        # Add tabs to tab widget
        self.tabs.addTab(self.config_tab, "Portfolio Configuration")
        self.tabs.addTab(self.views_tab, "Investor Views")
        self.tabs.addTab(self.results_tab, "Optimization Results")
        self.tabs.addTab(self.analysis_tab, "Risk Analysis")
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
        
        # Optimization worker
        self.optimizer_worker = None
        self.last_results = None
        
    def setup_styles(self):
        """Set up application styling."""
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1E1E2E;
                color: #CDD6F4;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTabWidget::pane {
                border: 1px solid #313244;
                border-radius: 8px;
                background-color: #181825;
            }
            QTabBar::tab {
                background-color: #11111B;
                color: #A6ADC8;
                padding: 10px 20px;
                min-width: 220px;
                margin-right: 2px;
                border: 1px solid #313244;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 11pt;
            }
            QTabBar::tab:selected {
                background-color: #1E1E2E;
                color: #89B4FA;
                border-top: 3px solid #89B4FA;
                font-weight: bold;
            }
            QTabBar::tab:hover:!selected {
                background-color: #313244;
            }
            QLabel {
                color: #CDD6F4;
            }
            QPushButton {
                background-color: #89B4FA;
                color: #11111B;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #B4BEFE;
            }
            QPushButton:pressed {
                background-color: #74C7EC;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {
                padding: 8px;
                border: 1px solid #45475A;
                border-radius: 6px;
                background-color: #11111B;
                color: #CDD6F4;
                font-size: 10pt;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {
                border: 1px solid #89B4FA;
            }
            QTableWidget {
                border: 1px solid #45475A;
                border-radius: 6px;
                background-color: #181825;
                color: #CDD6F4;
                gridline-color: #313244;
                selection-background-color: #45475A;
                selection-color: #89B4FA;
            }
            QHeaderView::section {
                background-color: #11111B;
                color: #89B4FA;
                padding: 8px;
                border: none;
                border-right: 1px solid #313244;
                border-bottom: 1px solid #313244;
                font-weight: bold;
                font-size: 10pt;
            }
            QScrollBar:vertical {
                border: none;
                background: #11111B;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #45475A;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #585B70;
            }
        """)
    
    def create_config_tab(self):
        """Create portfolio configuration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Title
        title = QLabel("Portfolio Configuration")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Configuration form
        form_layout = QHBoxLayout()
        
        # Tickers input
        form_layout.addWidget(QLabel("Assets (comma-separated):"))
        self.tickers_input = QLineEdit()
        self.tickers_input.setText("AAPL,MSFT,GOOGL,AMZN,NVDA")
        self.tickers_input.setMinimumWidth(350)
        form_layout.addWidget(self.tickers_input)
        
        # Start date
        form_layout.addWidget(QLabel("Start Date:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addYears(-5))
        self.start_date.setMinimumWidth(160)
        form_layout.addWidget(self.start_date)
        
        # End date
        form_layout.addWidget(QLabel("End Date:"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setMinimumWidth(160)
        form_layout.addWidget(self.end_date)
        
        # Optimize button
        self.optimize_btn = QPushButton("Run Optimization")
        self.optimize_btn.setMinimumWidth(180)
        self.optimize_btn.clicked.connect(self.run_optimization)
        form_layout.addWidget(self.optimize_btn)
        
        form_layout.addStretch()
        layout.addLayout(form_layout)
        
        # Info section
        layout.addWidget(QLabel("\n📊 Portfolio Configuration Guide:"))
        info_text = (
            "• Assets: List of stock tickers to include in the portfolio\n"
            "• Date Range: Historical period for data download\n"
            "• Next: Go to 'Investor Views' tab to specify your views\n"
            "• Click 'Run Optimization' to start the analysis"
        )
        info_label = QLabel(info_text)
        info_label.setStyleSheet("color: #A6ADC8; font-size: 10pt;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        return widget
    
    def create_views_tab(self):
        """Create investor views tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Title
        title = QLabel("Investor Views Specification")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Info
        info = QLabel(
            "Specify your bullish/bearish views on assets and confidence levels.\n"
            "Higher confidence (closer to 1.0) means stronger conviction."
        )
        info.setStyleSheet("color: #A6ADC8; margin-bottom: 10px;")
        layout.addWidget(info)
        
        # Views table
        self.views_table = QTableWidget()
        self.views_table.setColumnCount(4)
        self.views_table.setHorizontalHeaderLabels([
            "Asset", "Expected Return (%)", "Confidence (0-1)", "Action"
        ])
        self.views_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.views_table.setMaximumHeight(300)
        layout.addWidget(self.views_table)
        
        # Button layout
        btn_layout = QHBoxLayout()
        
        add_view_btn = QPushButton("Add View")
        add_view_btn.clicked.connect(lambda: self.add_view_row())
        btn_layout.addWidget(add_view_btn)
        
        clear_views_btn = QPushButton("Clear All")
        clear_views_btn.clicked.connect(self.clear_views)
        btn_layout.addWidget(clear_views_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Default views suggestion
        layout.addWidget(QLabel("\n💡 Example Views:"))
        suggestions = QLabel(
            "Asset: AAPL | Return: 12% | Confidence: 0.60\n"
            "Asset: MSFT | Return: 10% | Confidence: 0.50\n"
            "Asset: GOOGL | Return: 11% | Confidence: 0.55\n"
            "Asset: AMZN | Return: 14% | Confidence: 0.60\n"
            "Asset: NVDA | Return: 15% | Confidence: 0.65"
        )
        suggestions.setStyleSheet("color: #A6ADC8; font-size: 9pt;")
        layout.addWidget(suggestions)
        
        layout.addStretch()
        
        # Pre-populate with example
        self.add_view_row("AAPL", 12.0, 0.60)
        self.add_view_row("MSFT", 10.0, 0.50)
        self.add_view_row("GOOGL", 11.0, 0.55)
        self.add_view_row("AMZN", 14.0, 0.60)
        self.add_view_row("NVDA", 15.0, 0.65)
        
        return widget
    
    def add_view_row(self, asset="", ret_val=0.0, conf=0.5):
        """Add a row to the views table."""
        row = self.views_table.rowCount()
        self.views_table.insertRow(row)
        
        # Asset
        asset_input = QLineEdit(asset)
        self.views_table.setCellWidget(row, 0, asset_input)
        
        # Return
        ret_input = QDoubleSpinBox()
        ret_input.setRange(-50, 50)
        ret_input.setValue(ret_val)
        ret_input.setSuffix("%")
        self.views_table.setCellWidget(row, 1, ret_input)
        
        # Confidence
        conf_input = QDoubleSpinBox()
        conf_input.setRange(0, 1)
        conf_input.setValue(conf)
        conf_input.setSingleStep(0.05)
        self.views_table.setCellWidget(row, 2, conf_input)
        
        # Remove button
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(lambda: self.views_table.removeRow(row))
        self.views_table.setCellWidget(row, 3, remove_btn)
    
    def clear_views(self):
        """Clear all views from table."""
        self.views_table.setRowCount(0)
    
    def create_results_tab(self):
        """Create results display tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Title
        title = QLabel("Optimization Results")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Add tabs for Results: Weights, Metrics, Visualizations
        self.results_tabs = QTabWidget()
        
        # Tab 1: Weights And Metrics
        self.weights_widget = QWidget()
        weights_layout = QVBoxLayout(self.weights_widget)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels([
            "Asset", "Weight (%)", "Expected Return (%)"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        weights_layout.addWidget(QLabel("🎯 Recommended Portfolio (Black-Litterman):"))
        weights_layout.addWidget(self.results_table)
        
        # Metrics section
        weights_layout.addWidget(QLabel("\n📈 Portfolio Metrics:"))
        
        metrics_layout = QHBoxLayout()
        
        # Metric cards
        self.metric_labels = {}
        metrics = {
            'Expected Return': '0.00%',
            'Volatility': '0.00%',
            'Sharpe Ratio': '0.00',
            'VaR (95%)': '0.00%'
        }
        
        for metric_name, default_val in metrics.items():
            metric_frame = QFrame()
            metric_frame.setStyleSheet(
                "border: 1px solid #313244; border-radius: 8px; padding: 10px; background-color: #11111B;"
            )
            metric_layout = QVBoxLayout(metric_frame)
            
            metric_label = QLabel(metric_name)
            metric_label.setStyleSheet("font-weight: bold; color: #89B4FA;")
            metric_value = QLabel(default_val)
            metric_value_font = QFont()
            metric_value_font.setPointSize(12)
            metric_value_font.setBold(True)
            metric_value.setFont(metric_value_font)
            
            metric_layout.addWidget(metric_label)
            metric_layout.addWidget(metric_value)
            
            metrics_layout.addWidget(metric_frame)
            self.metric_labels[metric_name] = metric_value
        
        weights_layout.addLayout(metrics_layout)
        
        self.results_tabs.addTab(self.weights_widget, "Weights & Metrics")
        
        # Tab 2: Visualizations
        self.viz_widget = QWidget()
        viz_layout = QVBoxLayout(self.viz_widget)
        
        # Pie chart for allocation
        self.pie_canvas = FigureCanvas(Figure(figsize=(6, 4), dpi=100))
        viz_layout.addWidget(QLabel("📊 Asset Allocation:"))
        viz_layout.addWidget(self.pie_canvas)
        
        # Cumulative returns chart
        self.returns_canvas = FigureCanvas(Figure(figsize=(6, 4), dpi=100))
        viz_layout.addWidget(QLabel("\n📈 Cumulative Returns:"))
        viz_layout.addWidget(self.returns_canvas)
        
        self.results_tabs.addTab(self.viz_widget, "Visualizations")
        
        layout.addWidget(self.results_tabs)
        
        # Export button
        export_layout = QHBoxLayout()
        export_csv_btn = QPushButton("Export to CSV")
        export_csv_btn.clicked.connect(self.export_results_csv)
        export_layout.addWidget(export_csv_btn)
        
        export_pdf_btn = QPushButton("Export to PDF")
        export_pdf_btn.clicked.connect(self.export_results_pdf)
        export_layout.addWidget(export_pdf_btn)
        
        export_layout.addStretch()
        layout.addLayout(export_layout)
        
        return widget
    
    def create_analysis_tab(self):
        """Create analysis and visualization tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Title
        title = QLabel("Risk Analysis & Comparison")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Analysis table
        self.analysis_table = QTableWidget()
        self.analysis_table.setColumnCount(4)
        self.analysis_table.setHorizontalHeaderLabels([
            "Metric", "Black-Litterman", "Markowitz", "Difference"
        ])
        self.analysis_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(QLabel("\n📊 Model Comparison:"))
        layout.addWidget(self.analysis_table)
        
        # Risk metrics details
        self.risk_metrics_table = QTableWidget()
        self.risk_metrics_table.setColumnCount(2)
        self.risk_metrics_table.setHorizontalHeaderLabels(["Risk Metric", "Value"])
        self.risk_metrics_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(QLabel("\n⚠️ Detailed Risk Metrics (20+):"))
        layout.addWidget(self.risk_metrics_table)
        
        # Info
        info = QLabel(
            "Black-Litterman advantages:\n"
            "• More stable portfolio weights\n"
            "• Incorporates investor views through Bayesian framework\n"
            "• Reduces estimation error vs pure mean-variance\n"
            "• Better risk-adjusted returns in most market conditions"
        )
        info.setStyleSheet("color: #A6ADC8; margin-top: 10px; font-size: 9pt;")
        layout.addWidget(info)
    
    def run_optimization(self):
        """Run the optimization in a background thread."""
        try:
            # Parse inputs
            tickers_str = self.tickers_input.text().strip()
            tickers = [t.strip().upper() for t in tickers_str.split(',')]
            
            if not tickers or all(not t for t in tickers):
                QMessageBox.warning(self, "Input Error", "Please enter at least one ticker.")
                return
            
            start_date = self.start_date.date().toPyDate().strftime('%Y-%m-%d')
            end_date = self.end_date.date().toPyDate().strftime('%Y-%m-%d')
            
            # Extract views from table
            views = {}
            confidence = {}
            
            for row in range(self.views_table.rowCount()):
                asset_widget = self.views_table.cellWidget(row, 0)
                return_widget = self.views_table.cellWidget(row, 1)
                conf_widget = self.views_table.cellWidget(row, 2)
                
                if asset_widget and return_widget and conf_widget:
                    asset = asset_widget.text().strip().upper()
                    ret = return_widget.value() / 100.0  # Convert to decimal
                    conf = conf_widget.value()
                    
                    if asset and asset in tickers:
                        views[asset] = ret
                        confidence[asset] = conf
            
            # Show progress dialog
            progress = QProgressDialog("Running optimization...", None, 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            # Create and start worker
            self.optimizer_worker = OptimizationWorker(tickers, start_date, end_date, views, confidence)
            self.optimizer_worker.finished.connect(progress.close)
            self.optimizer_worker.error.connect(lambda msg: self.handle_optimization_error(msg))
            self.optimizer_worker.results_ready.connect(self.display_results)
            self.optimizer_worker.start()
            
            self.statusBar.showMessage("Optimization in progress...")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def handle_optimization_error(self, error_msg):
        """Handle optimization errors."""
        QMessageBox.critical(self, "Optimization Error", error_msg)
        self.statusBar.showMessage("Error during optimization")
    
    def display_results(self, results):
        """Display optimization results."""
        try:
            # Verify results are valid
            if not results or not isinstance(results, dict):
                raise ValueError("Invalid results format")
            
            self.last_results = results
            
            # Get Black-Litterman results
            bl_data = results.get('black_litterman', {})
            bl_weights = bl_data.get('weights', [])
            bl_metrics = bl_data.get('metrics', {})
            
            if not isinstance(bl_weights, (list, tuple, np.ndarray)) or len(bl_weights) == 0:
                raise ValueError("Invalid weights data")
            
            tickers = self.tickers_input.text().strip().split(',')
            tickers = [t.strip().upper() for t in tickers]
            
            if len(tickers) != len(bl_weights):
                raise ValueError(f"Mismatch: {len(tickers)} tickers but {len(bl_weights)} weights")
            
            # Display portfolio weights - with widget existence check
            if hasattr(self, 'results_table') and self.results_table:
                self.results_table.setRowCount(len(tickers))
                for idx, (ticker, weight) in enumerate(zip(tickers, bl_weights)):
                    try:
                        self.results_table.setItem(idx, 0, QTableWidgetItem(ticker))
                        self.results_table.setItem(idx, 1, QTableWidgetItem(f"{weight*100:.2f}%"))
                        
                        # Expected return for this asset
                        total_weight = sum(bl_weights)
                        expected_ret = bl_metrics.get('Expected Return', 0) * (weight / total_weight if total_weight > 0 else 0)
                        self.results_table.setItem(idx, 2, QTableWidgetItem(f"{expected_ret*100:.2f}%"))
                    except Exception as e:
                        print(f"Warning: Could not set table item {idx}: {e}")
            
            # Display metrics with safe access
            if hasattr(self, 'metric_labels') and self.metric_labels:
                try:
                    if 'Expected Return' in self.metric_labels and self.metric_labels['Expected Return']:
                        self.metric_labels['Expected Return'].setText(
                            f"{bl_metrics.get('Expected Return', 0)*100:.2f}%"
                        )
                    if 'Volatility' in self.metric_labels and self.metric_labels['Volatility']:
                        self.metric_labels['Volatility'].setText(
                            f"{bl_metrics.get('Volatility', 0)*100:.2f}%"
                        )
                    if 'Sharpe Ratio' in self.metric_labels and self.metric_labels['Sharpe Ratio']:
                        self.metric_labels['Sharpe Ratio'].setText(
                            f"{bl_metrics.get('Sharpe Ratio', 0):.4f}"
                        )
                    if 'VaR (95%)' in self.metric_labels and self.metric_labels['VaR (95%)']:
                        self.metric_labels['VaR (95%)'].setText(
                            f"{bl_metrics.get('VaR (95%)', 0)*100:.2f}%"
                        )
                except Exception as e:
                    print(f"Warning: Could not update metric labels: {e}")
            
            # Create visualizations
            try:
                self.create_pie_chart(tickers, bl_weights)
                self.create_returns_chart(results)
            except Exception as e:
                print(f"Warning: Could not create visualizations: {e}")
            
            # Display model comparison
            try:
                self.display_model_comparison(results)
            except Exception as e:
                print(f"Warning: Could not display model comparison: {e}")
            
            # Display risk metrics
            try:
                self.display_risk_metrics(results)
            except Exception as e:
                print(f"Warning: Could not display risk metrics: {e}")
            
            # Switch to results tab safely
            if hasattr(self, 'tabs') and self.tabs:
                self.tabs.setCurrentIndex(2)
            
            self.statusBar.showMessage("✓ Optimization complete!")
        
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error in display_results:\n{error_details}")
            QMessageBox.critical(self, "Display Error", f"Error displaying results:\n{str(e)}")
    
    def display_model_comparison(self, results):
        """Display comparison between models."""
        try:
            if not hasattr(self, 'analysis_table') or not self.analysis_table:
                print("Warning: analysis_table not available")
                return
            
            self.analysis_table.setRowCount(0)
            
            metrics_to_compare = ['Expected Return', 'Volatility', 'Sharpe Ratio', 'Max Drawdown']
            
            for metric in metrics_to_compare:
                try:
                    row = self.analysis_table.rowCount()
                    self.analysis_table.insertRow(row)
                    
                    bl_val = results.get('black_litterman', {}).get('metrics', {}).get(metric, 0)
                    mw_val = results.get('markowitz', {}).get('metrics', {}).get(metric, 0)
                    
                    # Format values
                    if metric == 'Sharpe Ratio':
                        bl_str = f"{bl_val:.4f}"
                        mw_str = f"{mw_val:.4f}"
                        diff_str = f"{abs(bl_val - mw_val):.4f}"
                    else:
                        bl_str = f"{bl_val*100:.2f}%"
                        mw_str = f"{mw_val*100:.2f}%"
                        diff_str = f"{abs(bl_val - mw_val)*100:.2f}%"
                    
                    self.analysis_table.setItem(row, 0, QTableWidgetItem(metric))
                    self.analysis_table.setItem(row, 1, QTableWidgetItem(bl_str))
                    self.analysis_table.setItem(row, 2, QTableWidgetItem(mw_str))
                    self.analysis_table.setItem(row, 3, QTableWidgetItem(diff_str))
                except Exception as inner_e:
                    print(f"Warning: Could not add row for {metric}: {inner_e}")
        except Exception as e:
            print(f"Warning in display_model_comparison: {e}")
    
    def display_risk_metrics(self, results):
        """Display detailed risk metrics."""
        try:
            if not hasattr(self, 'risk_metrics_table') or not self.risk_metrics_table:
                print("Warning: risk_metrics_table not available")
                return
            
            self.risk_metrics_table.setRowCount(0)
            
            bl_metrics = results.get('black_litterman', {}).get('metrics', {})
            
            if not bl_metrics:
                print("Warning: No metrics to display")
                return
            
            for metric_name, metric_value in sorted(bl_metrics.items()):
                try:
                    row = self.risk_metrics_table.rowCount()
                    self.risk_metrics_table.insertRow(row)
                    
                    # Format metric value
                    if isinstance(metric_value, float):
                        if 'Return' in metric_name or 'Volatility' in metric_name or '%' in metric_name:
                            value_str = f"{metric_value*100:.2f}%"
                        else:
                            value_str = f"{metric_value:.4f}"
                    else:
                        value_str = str(metric_value)
                    
                    self.risk_metrics_table.setItem(row, 0, QTableWidgetItem(metric_name))
                    self.risk_metrics_table.setItem(row, 1, QTableWidgetItem(value_str))
                except Exception as inner_e:
                    print(f"Warning: Could not add metric {metric_name}: {inner_e}")
        except Exception as e:
            print(f"Warning in display_risk_metrics: {e}")
    
    def create_pie_chart(self, tickers, weights):
        """Create pie chart for asset allocation."""
        try:
            self.pie_canvas.figure.clear()
            ax = self.pie_canvas.figure.add_subplot(111)
            
            # Filter out very small weights
            colors_list = plt.cm.Set3(np.linspace(0, 1, len(tickers)))
            wedges, texts, autotexts = ax.pie(
                weights, 
                labels=tickers, 
                autopct='%1.1f%%',
                colors=colors_list,
                startangle=90
            )
            
            # Make percentage text bold
            for autotext in autotexts:
                autotext.set_color('#11111B')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(9)
            
            ax.set_title('Asset Allocation', fontweight='bold', fontsize=12)
            self.pie_canvas.figure.tight_layout()
            self.pie_canvas.draw()
        except Exception as e:
            print(f"Error creating pie chart: {e}")
    
    def create_returns_chart(self, results):
        """Create cumulative returns chart."""
        try:
            self.returns_canvas.figure.clear()
            ax = self.returns_canvas.figure.add_subplot(111)
            
            # Create sample returns data
            bl_metrics = results['black_litterman']['metrics']
            mw_metrics = results['markowitz']['metrics']
            
            # Simple comparison chart
            models = ['Black-Litterman', 'Markowitz']
            returns = [
                bl_metrics.get('Expected Return', 0) * 100,
                mw_metrics.get('Expected Return', 0) * 100
            ]
            risks = [
                bl_metrics.get('Volatility', 0) * 100,
                mw_metrics.get('Volatility', 0) * 100
            ]
            
            x = np.arange(len(models))
            width = 0.35
            
            ax.bar(x - width/2, returns, width, label='Expected Return (%)', color='#89B4FA')
            ax.bar(x + width/2, risks, width, label='Volatility (%)', color='#F38BA8')
            
            ax.set_ylabel('(%)', fontweight='bold')
            ax.set_title('Model Comparison', fontweight='bold', fontsize=12)
            ax.set_xticks(x)
            ax.set_xticklabels(models)
            ax.legend()
            ax.grid(axis='y', alpha=0.3)
            
            self.returns_canvas.figure.tight_layout()
            self.returns_canvas.draw()
        except Exception as e:
            print(f"Error creating returns chart: {e}")
    
    def export_results_csv(self):
        """Export results to CSV file."""
        if not self.last_results:
            QMessageBox.warning(self, "No Results", "Please run optimization first.")
            return
        
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export to CSV", "", "CSV Files (*.csv)"
            )
            
            if file_path:
                tickers = self.tickers_input.text().strip().split(',')
                tickers = [t.strip().upper() for t in tickers]
                bl_weights = self.last_results['black_litterman']['weights']
                
                # Create DataFrame
                data = {
                    'Asset': tickers,
                    'Weight': [f"{w*100:.2f}%" for w in bl_weights]
                }
                df = pd.DataFrame(data)
                df.to_csv(file_path, index=False)
                
                QMessageBox.information(self, "Success", f"Results exported to:\n{file_path}")
                self.statusBar.showMessage(f"Results exported to {file_path}")
        
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Error exporting results: {str(e)}")
    
    def export_results_pdf(self):
        """Export results to PDF file with charts."""
        if not self.last_results:
            QMessageBox.warning(self, "No Results", "Please run optimization first.")
            return
        
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export to PDF", "", "PDF Files (*.pdf)"
            )
            
            if file_path:
                # Create PDF document
                doc = SimpleDocTemplate(file_path, pagesize=letter)
                elements = []
                styles = getSampleStyleSheet()
                
                # Title
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=24,
                    textColor=colors.HexColor('#0066cc'),
                    spaceAfter=30,
                    alignment=1
                )
                elements.append(Paragraph("Portfolio Optimization Report", title_style))
                elements.append(Spacer(1, 0.3*inch))
                
                # Portfolio Summary
                elements.append(Paragraph("Portfolio Configuration", styles['Heading2']))
                tickers_str = self.tickers_input.text().strip()
                config_data = [
                    ['Assets:', tickers_str],
                    ['Period:', f"{self.start_date.date().toString('yyyy-MM-dd')} to {self.end_date.date().toString('yyyy-MM-dd')}"],
                    ['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
                ]
                config_table = Table(config_data, colWidths=[1.5*inch, 4*inch])
                config_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(config_table)
                elements.append(Spacer(1, 0.3*inch))
                
                # Metrics
                elements.append(Paragraph("Key Metrics (Black-Litterman Model)", styles['Heading2']))
                bl_metrics = self.last_results['black_litterman']['metrics']
                metrics_data = [
                    ['Metric', 'Value'],
                    ['Expected Return', f"{bl_metrics.get('Expected Return', 0)*100:.2f}%"],
                    ['Volatility', f"{bl_metrics.get('Volatility', 0)*100:.2f}%"],
                    ['Sharpe Ratio', f"{bl_metrics.get('Sharpe Ratio', 0):.4f}"],
                    ['VaR (95%)', f"{bl_metrics.get('VaR (95%)', 0)*100:.2f}%"],
                    ['Max Drawdown', f"{bl_metrics.get('Max Drawdown', 0)*100:.2f}%"]
                ]
                metrics_table = Table(metrics_data, colWidths=[2.5*inch, 2.5*inch])
                metrics_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
                ]))
                elements.append(metrics_table)
                elements.append(Spacer(1, 0.3*inch))
                
                # Portfolio Allocation
                elements.append(Paragraph("Portfolio Allocation", styles['Heading2']))
                tickers = self.tickers_input.text().strip().split(',')
                tickers = [t.strip().upper() for t in tickers]
                bl_weights = self.last_results['black_litterman']['weights']
                
                allocation_data = [['Asset', 'Weight']]
                for ticker, weight in zip(tickers, bl_weights):
                    allocation_data.append([ticker, f"{weight*100:.2f}%"])
                
                allocation_table = Table(allocation_data, colWidths=[2.5*inch, 2.5*inch])
                allocation_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
                ]))
                elements.append(allocation_table)
                
                # Build PDF
                doc.build(elements)
                
                QMessageBox.information(self, "Success", f"PDF exported to:\n{file_path}")
                self.statusBar.showMessage(f"PDF exported to {file_path}")
        
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Error exporting to PDF: {str(e)}")





def main():
    """Run the desktop GUI application."""
    app = __import__('PyQt5.QtWidgets', fromlist=['QApplication']).QApplication(sys.argv)
    
    # Set application icon and info
    app.setApplicationName("Portfolio Optimizer")
    app.setApplicationVersion("2.0")
    
    # Create and show main window
    window = PortfolioGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
