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

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QMessageBox, QStatusBar,
    QProgressDialog, QFileDialog, QFrame
)
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal
from PyQt5.QtGui import QFont

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
            # Initialize optimizer
            optimizer = BlackLittermanOptimizer(
                ticker_list=self.tickers,
                start_date=self.start_date,
                end_date=self.end_date,
                risk_free_rate=0.03
            )
            
            # Run comparison
            results = optimizer.compare_models(self.views, self.confidence)
            
            self.results = results
            self.results_ready.emit(results)
            self.finished.emit()
        except Exception as e:
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
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                color: #333333;
                padding: 8px 20px;
                margin-right: 2px;
                border: 1px solid #cccccc;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                color: #0066cc;
                font-weight: bold;
            }
            QLabel {
                color: #333333;
            }
            QPushButton {
                background-color: #0066cc;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
            QPushButton:pressed {
                background-color: #003d7a;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {
                padding: 6px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }
            QTableWidget {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #0066cc;
                color: white;
                padding: 6px;
                border: none;
                font-weight: bold;
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
        self.tickers_input.setMaximumWidth(300)
        form_layout.addWidget(self.tickers_input)
        
        # Start date
        form_layout.addWidget(QLabel("Start Date:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate(2021, 1, 1))
        self.start_date.setMaximumWidth(120)
        form_layout.addWidget(self.start_date)
        
        # End date
        form_layout.addWidget(QLabel("End Date:"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setMaximumWidth(120)
        form_layout.addWidget(self.end_date)
        
        # Optimize button
        self.optimize_btn = QPushButton("Run Optimization")
        self.optimize_btn.setMaximumWidth(150)
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
        info_label.setStyleSheet("color: #666666; font-size: 10pt;")
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
        info.setStyleSheet("color: #666666; margin-bottom: 10px;")
        layout.addWidget(info)
        
        # Views table
        self.views_table = QTableWidget()
        self.views_table.setColumnCount(4)
        self.views_table.setHorizontalHeaderLabels([
            "Asset", "Expected Return (%)", "Confidence (0-1)", "Action"
        ])
        self.views_table.setMaximumHeight(300)
        layout.addWidget(self.views_table)
        
        # Button layout
        btn_layout = QHBoxLayout()
        
        add_view_btn = QPushButton("Add View")
        add_view_btn.clicked.connect(self.add_view_row)
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
            "Asset: NVDA | Return: 15% | Confidence: 0.65"
        )
        suggestions.setStyleSheet("color: #666666; font-size: 9pt;")
        layout.addWidget(suggestions)
        
        layout.addStretch()
        
        # Pre-populate with example
        self.add_view_row("AAPL", 12.0, 0.60)
        self.add_view_row("MSFT", 10.0, 0.50)
        
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
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels([
            "Asset", "Weight (%)", "Expected Return (%)"
        ])
        layout.addWidget(QLabel("\n🎯 Recommended Portfolio (Black-Litterman):"))
        layout.addWidget(self.results_table)
        
        # Metrics section
        layout.addWidget(QLabel("\n📈 Portfolio Metrics:"))
        
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
                "border: 1px solid #cccccc; border-radius: 4px; padding: 10px;"
            )
            metric_layout = QVBoxLayout(metric_frame)
            
            metric_label = QLabel(metric_name)
            metric_label.setStyleSheet("font-weight: bold; color: #0066cc;")
            metric_value = QLabel(default_val)
            metric_value_font = QFont()
            metric_value_font.setPointSize(12)
            metric_value_font.setBold(True)
            metric_value.setFont(metric_value_font)
            
            metric_layout.addWidget(metric_label)
            metric_layout.addWidget(metric_value)
            
            metrics_layout.addWidget(metric_frame)
            self.metric_labels[metric_name] = metric_value
        
        layout.addLayout(metrics_layout)
        
        # Export button
        export_layout = QHBoxLayout()
        export_btn = QPushButton("Export Results to CSV")
        export_btn.clicked.connect(self.export_results)
        export_layout.addWidget(export_btn)
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
        layout.addWidget(QLabel("\n📊 Model Comparison:"))
        layout.addWidget(self.analysis_table)
        
        # Risk metrics details
        self.risk_metrics_table = QTableWidget()
        self.risk_metrics_table.setColumnCount(2)
        self.risk_metrics_table.setHorizontalHeaderLabels(["Risk Metric", "Value"])
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
        info.setStyleSheet("color: #666666; margin-top: 10px; font-size: 9pt;")
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
            self.last_results = results
            
            # Get Black-Litterman results
            bl_data = results.get('black_litterman', {})
            bl_weights = bl_data.get('weights', [])
            bl_metrics = bl_data.get('metrics', {})
            
            tickers = self.tickers_input.text().strip().split(',')
            tickers = [t.strip().upper() for t in tickers]
            
            # Display portfolio weights
            self.results_table.setRowCount(len(tickers))
            for idx, (ticker, weight) in enumerate(zip(tickers, bl_weights)):
                self.results_table.setItem(idx, 0, QTableWidgetItem(ticker))
                self.results_table.setItem(idx, 1, QTableWidgetItem(f"{weight*100:.2f}%"))
                
                # Expected return for this asset
                expected_ret = bl_metrics.get('Expected Return', 0) * (weight / sum(bl_weights) if sum(bl_weights) > 0 else 0)
                self.results_table.setItem(idx, 2, QTableWidgetItem(f"{expected_ret*100:.2f}%"))
            
            # Display metrics
            if 'Expected Return' in self.metric_labels:
                self.metric_labels['Expected Return'].setText(
                    f"{bl_metrics.get('Expected Return', 0)*100:.2f}%"
                )
            if 'Volatility' in self.metric_labels:
                self.metric_labels['Volatility'].setText(
                    f"{bl_metrics.get('Volatility', 0)*100:.2f}%"
                )
            if 'Sharpe Ratio' in self.metric_labels:
                self.metric_labels['Sharpe Ratio'].setText(
                    f"{bl_metrics.get('Sharpe Ratio', 0):.4f}"
                )
            if 'VaR (95%)' in self.metric_labels:
                self.metric_labels['VaR (95%)'].setText(
                    f"{bl_metrics.get('VaR (95%)', 0)*100:.2f}%"
                )
            
            # Display model comparison
            self.display_model_comparison(results)
            
            # Display risk metrics
            self.display_risk_metrics(results)
            
            # Switch to results tab
            self.tabs.setCurrentIndex(2)
            
            self.statusBar.showMessage("✓ Optimization complete!")
        
        except Exception as e:
            QMessageBox.critical(self, "Display Error", f"Error displaying results: {str(e)}")
    
    def display_model_comparison(self, results):
        """Display comparison between models."""
        self.analysis_table.setRowCount(0)
        
        metrics_to_compare = ['Expected Return', 'Volatility', 'Sharpe Ratio', 'Max Drawdown']
        
        for metric in metrics_to_compare:
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
    
    def display_risk_metrics(self, results):
        """Display detailed risk metrics."""
        self.risk_metrics_table.setRowCount(0)
        
        bl_metrics = results.get('black_litterman', {}).get('metrics', {})
        
        for metric_name, metric_value in sorted(bl_metrics.items()):
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
    
    def export_results(self):
        """Export results to CSV file."""
        if not self.last_results:
            QMessageBox.warning(self, "No Results", "Please run optimization first.")
            return
        
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Results", "", "CSV Files (*.csv);;Excel Files (*.xlsx)"
            )
            
            if file_path:
                # Prepare data
                tickers = self.tickers_input.text().strip().split(',')
                tickers = [t.strip().upper() for t in tickers]
                bl_weights = self.last_results['black_litterman']['weights']
                
                # Create DataFrame
                data = {
                    'Asset': tickers,
                    'Weight': [f"{w*100:.2f}%" for w in bl_weights]
                }
                df = pd.DataFrame(data)
                
                # Add metrics
                metrics_data = self.last_results['black_litterman']['metrics']
                metrics_df = pd.DataFrame({
                    'Metric': list(metrics_data.keys()),
                    'Value': list(metrics_data.values())
                })
                
                if file_path.endswith('.csv'):
                    df.to_csv(file_path, index=False)
                    metrics_df.to_csv(file_path.replace('.csv', '_metrics.csv'), index=False)
                else:
                    with pd.ExcelWriter(file_path) as writer:
                        df.to_excel(writer, sheet_name='Portfolio', index=False)
                        metrics_df.to_excel(writer, sheet_name='Metrics', index=False)
                
                QMessageBox.information(self, "Success", f"Results exported to:\n{file_path}")
                self.statusBar.showMessage(f"Results exported to {file_path}")
        
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Error exporting results: {str(e)}")


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
