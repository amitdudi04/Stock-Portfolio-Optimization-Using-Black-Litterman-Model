"""
Visualization Module for Black-Litterman Portfolio Optimization
================================================================

Generates comprehensive visualizations including efficient frontier,
portfolio comparisons, cumulative returns, and risk analysis plots.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import seaborn as sns
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')


class PortfolioVisualizer:
    """Generate professional visualizations for portfolio optimization."""
    
    def __init__(self, optimizer, results):
        """
        Initialize visualizer.
        
        Parameters:
        -----------
        optimizer : BlackLittermanOptimizer
            The optimizer object with data and calculations
        results : dict
            Results from compare_models()
        """
        self.optimizer = optimizer
        self.results = results
        self.style = 'seaborn-v0_8-darkgrid'
        plt.style.use(self.style)
        sns.set_palette("husl")
    
    def plot_efficient_frontier(self, n_portfolios=500, figsize=(12, 8)):
        """
        Plot the efficient frontier comparing Markowitz and Black-Litterman.
        
        Parameters:
        -----------
        n_portfolios : int
            Number of random portfolios to generate for comparison
        figsize : tuple
            Figure size (width, height)
        """
        # Generate random portfolios for context
        np.random.seed(42)
        returns_list = []
        volatility_list = []
        sharpe_list = []
        
        for _ in range(n_portfolios):
            weights = np.random.random(len(self.optimizer.ticker_list))
            weights /= np.sum(weights)
            
            # Use BL returns for random portfolios
            portfolio_return = np.sum(weights * self.optimizer.bl_returns)
            portfolio_vol = np.sqrt(weights @ self.optimizer.cov_matrix @ weights)
            sharpe = (portfolio_return - self.optimizer.risk_free_rate) / portfolio_vol
            
            returns_list.append(portfolio_return)
            volatility_list.append(portfolio_vol)
            sharpe_list.append(sharpe)
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot random portfolios
        scatter = ax.scatter(volatility_list, returns_list, c=sharpe_list, 
                            cmap='viridis', alpha=0.5, s=30, label='Random Portfolios')
        
        # Plot optimized portfolios
        markowitz = self.results['markowitz']
        bl = self.results['black_litterman']
        equal = self.results['equal_weight']
        
        markowitz_vol = np.sqrt(markowitz['weights'] @ self.optimizer.cov_matrix @ 
                               markowitz['weights'])
        bl_vol = np.sqrt(bl['weights'] @ self.optimizer.cov_matrix @ bl['weights'])
        equal_vol = np.sqrt(equal['weights'] @ self.optimizer.cov_matrix @ equal['weights'])
        
        markowitz_ret = markowitz['metrics']['Expected Return']
        bl_ret = bl['metrics']['Expected Return']
        equal_ret = equal['metrics']['Expected Return']
        
        # Plot optimal portfolios
        ax.scatter(markowitz_vol, markowitz_ret, s=300, marker='*', 
                  color='red', edgecolors='darkred', linewidth=2, 
                  label='Markowitz Maximum Sharpe', zorder=5)
        
        ax.scatter(bl_vol, bl_ret, s=300, marker='*', 
                  color='green', edgecolors='darkgreen', linewidth=2,
                  label='Black-Litterman Maximum Sharpe', zorder=5)
        
        ax.scatter(equal_vol, equal_ret, s=300, marker='s', 
                  color='blue', edgecolors='darkblue', linewidth=2,
                  label='Equal-Weight Benchmark', zorder=5)
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Sharpe Ratio', fontsize=11, fontweight='bold')
        
        # Labels and formatting
        ax.set_xlabel('Volatility (Annual)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Expected Return (Annual)', fontsize=12, fontweight='bold')
        ax.set_title('Efficient Frontier: Markowitz vs Black-Litterman Model', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='best', fontsize=10, framealpha=0.95)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('efficient_frontier.png', dpi=300, bbox_inches='tight')
        print("✓ Saved: efficient_frontier.png")
        plt.show()
    
    def plot_weight_comparison(self, figsize=(14, 6)):
        """Plot portfolio weights comparison across models."""
        
        models_data = {
            'Markowitz': self.results['markowitz']['weights'],
            'Black-Litterman': self.results['black_litterman']['weights'],
            'Equal-Weight': self.results['equal_weight']['weights']
        }
        
        fig, axes = plt.subplots(1, 3, figsize=figsize, sharey=True)
        colors = sns.color_palette("Set2", len(self.optimizer.ticker_list))
        
        for idx, (model_name, weights) in enumerate(models_data.items()):
            ax = axes[idx]
            
            # Create bar chart
            bars = ax.bar(self.optimizer.ticker_list, weights, color=colors, 
                         edgecolor='black', linewidth=1.5)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1%}', ha='center', va='bottom', fontsize=9)
            
            ax.set_title(model_name, fontsize=12, fontweight='bold')
            ax.set_ylabel('Weight' if idx == 0 else '', fontsize=11, fontweight='bold')
            ax.set_ylim(0, max(weights) * 1.15)
            ax.grid(axis='y', alpha=0.3)
        
        fig.suptitle('Portfolio Weights Comparison', fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        plt.savefig('weight_comparison.png', dpi=300, bbox_inches='tight')
        print("✓ Saved: weight_comparison.png")
        plt.show()
    
    def plot_cumulative_returns(self, figsize=(12, 7)):
        """Plot cumulative returns for optimized portfolios."""
        
        # Calculate cumulative returns
        daily_returns = self.optimizer.returns
        
        # Markowitz portfolio
        markowitz_weights = self.results['markowitz']['weights']
        markowitz_daily_ret = (daily_returns @ markowitz_weights).values
        markowitz_cumulative = (1 + markowitz_daily_ret).cumprod()
        
        # Black-Litterman portfolio
        bl_weights = self.results['black_litterman']['weights']
        bl_daily_ret = (daily_returns @ bl_weights).values
        bl_cumulative = (1 + bl_daily_ret).cumprod()
        
        # Equal-weight portfolio
        equal_weights = self.results['equal_weight']['weights']
        equal_daily_ret = (daily_returns @ equal_weights).values
        equal_cumulative = (1 + equal_daily_ret).cumprod()
        
        # Create plot
        fig, ax = plt.subplots(figsize=figsize)
        
        ax.plot(daily_returns.index, markowitz_cumulative, linewidth=2, 
               label='Markowitz', alpha=0.8, color='red')
        ax.plot(daily_returns.index, bl_cumulative, linewidth=2.5, 
               label='Black-Litterman', alpha=0.8, color='green')
        ax.plot(daily_returns.index, equal_cumulative, linewidth=2, 
               label='Equal-Weight', alpha=0.8, color='blue')
        
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Cumulative Return', fontsize=12, fontweight='bold')
        ax.set_title('Portfolio Cumulative Returns (Out-of-Sample)', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='best', fontsize=11, framealpha=0.95)
        ax.grid(True, alpha=0.3)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.0%}'.format(y-1)))
        
        plt.tight_layout()
        plt.savefig('cumulative_returns.png', dpi=300, bbox_inches='tight')
        print("✓ Saved: cumulative_returns.png")
        plt.show()
    
    def plot_drawdown(self, figsize=(12, 7)):
        """Plot maximum drawdown analysis."""
        
        daily_returns = self.optimizer.returns
        
        # Calculate drawdowns for each portfolio
        portfolios = {
            'Markowitz': self.results['markowitz']['weights'],
            'Black-Litterman': self.results['black_litterman']['weights'],
            'Equal-Weight': self.results['equal_weight']['weights']
        }
        
        fig, ax = plt.subplots(figsize=figsize)
        colors = ['red', 'green', 'blue']
        
        for (name, weights), color in zip(portfolios.items(), colors):
            # Calculate cumulative returns
            portfolio_ret = (daily_returns @ weights).values
            cumulative = (1 + portfolio_ret).cumprod()
            
            # Calculate running maximum and drawdown
            running_max = np.maximum.accumulate(cumulative)
            drawdown = (cumulative - running_max) / running_max
            
            ax.fill_between(daily_returns.index, drawdown, 0, alpha=0.3, 
                           color=color, label=name)
        
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Drawdown', fontsize=12, fontweight='bold')
        ax.set_title('Portfolio Drawdown Over Time', fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='best', fontsize=11, framealpha=0.95)
        ax.grid(True, alpha=0.3)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.0%}'.format(y)))
        
        plt.tight_layout()
        plt.savefig('drawdown.png', dpi=300, bbox_inches='tight')
        print("✓ Saved: drawdown.png")
        plt.show()
    
    def plot_risk_metrics_comparison(self, figsize=(14, 8)):
        """Plot comprehensive risk metrics comparison."""
        
        metrics_to_plot = ['Expected Return', 'Volatility', 'Sharpe Ratio', 'Max Drawdown']
        
        # Prepare data
        data_dict = {}
        for model_name, model_data in self.results.items():
            data_dict[model_name.replace('_', ' ').title()] = model_data['metrics']
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        axes = axes.flatten()
        
        colors = sns.color_palette("Set2", len(data_dict))
        
        for idx, metric in enumerate(metrics_to_plot):
            ax = axes[idx]
            
            values = [data_dict[model][metric] for model in data_dict.keys()]
            bars = ax.bar(data_dict.keys(), values, color=colors, 
                         edgecolor='black', linewidth=1.5)
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                if metric in ['Expected Return', 'Volatility', 'Max Drawdown']:
                    label = f'{height:.2%}'
                else:
                    label = f'{height:.3f}'
                
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       label, ha='center', va='bottom', fontsize=10, fontweight='bold')
            
            ax.set_title(metric, fontsize=12, fontweight='bold')
            ax.set_ylabel('Value', fontsize=10, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
            ax.set_ylim(0, max(values) * 1.2 if metric != 'Max Drawdown' else None)
        
        fig.suptitle('Risk Metrics Comparison', fontsize=14, fontweight='bold', y=0.995)
        plt.tight_layout()
        plt.savefig('risk_metrics.png', dpi=300, bbox_inches='tight')
        print("✓ Saved: risk_metrics.png")
        plt.show()
    
    def plot_correlation_heatmap(self, figsize=(10, 8)):
        """Plot correlation matrix heatmap."""
        
        fig, ax = plt.subplots(figsize=figsize)
        
        corr_matrix = self.optimizer.returns.corr()
        
        sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
                   center=0, square=True, linewidths=1, cbar_kws={"shrink": 0.8},
                   ax=ax, vmin=-1, vmax=1)
        
        ax.set_title('Asset Correlation Matrix', fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig('correlation_matrix.png', dpi=300, bbox_inches='tight')
        print("✓ Saved: correlation_matrix.png")
        plt.show()
    
    def generate_all_visualizations(self):
        """Generate all visualizations."""
        
        print("\n" + "="*60)
        print("GENERATING VISUALIZATIONS")
        print("="*60)
        
        self.plot_correlation_heatmap()
        self.plot_efficient_frontier()
        self.plot_weight_comparison()
        self.plot_cumulative_returns()
        self.plot_drawdown()
        self.plot_risk_metrics_comparison()
        
        print("\n✓ All visualizations generated successfully!")


def create_visualizations(optimizer, results):
    """Convenience function to create all visualizations."""
    visualizer = PortfolioVisualizer(optimizer, results)
    visualizer.generate_all_visualizations()
