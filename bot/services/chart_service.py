import matplotlib
# Set backend to Agg to prevent GUI errors in background threads
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import uuid
from typing import Dict, List, Tuple, Optional

# Ensure temp directory exists
TEMP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "temp_charts")
os.makedirs(TEMP_DIR, exist_ok=True)

class ChartService:
    def __init__(self):
        # Harmonious aesthetic colors
        self.colors = [
            "#58a6ff",  # Soft Blue
            "#ff7b72",  # Soft Coral
            "#7ee787",  # Soft Green
            "#d2a8ff",  # Soft Purple
            "#ffca85",  # Soft Orange
            "#a5d6ff",  # Light Blue
            "#ffadad",  # Light Coral
            "#ffd6a5",  # Light Yellow/Orange
            "#caffbf",  # Light Green
            "#9bf6ff",  # Light Cyan
            "#bdb2ff",  # Light Violet
            "#ffc6ff"   # Light Pink
        ]
        
    def generate_expense_pie_chart(self, user_id: int, data: Dict[str, float]) -> Optional[str]:
        """
        Generates a beautiful expense distribution pie chart.
        Returns the absolute path to the saved image.
        """
        if not data:
            return None
            
        try:
            labels = list(data.keys())
            values = list(data.values())
            
            # Style configuration
            plt.style.use('dark_background')
            fig, ax = plt.subplots(figsize=(6, 5), facecolor='#1e1e2e')
            ax.set_facecolor('#1e1e2e')
            
            # Draw Pie Chart
            wedges, texts, autotexts = ax.pie(
                values, 
                labels=labels, 
                autopct='%1.1f%%',
                startangle=140, 
                colors=self.colors[:len(labels)],
                textprops=dict(color="w", fontsize=10),
                wedgeprops=dict(width=0.4, edgecolor='#1e1e2e', linewidth=2) # Donut style!
            )
            
            # Make percentages stand out
            for autotext in autotexts:
                autotext.set_fontsize(9)
                autotext.set_weight('bold')
                autotext.set_color('#11111b')
                
            ax.set_title("Xarajatlar Taqsimoti", color='w', fontsize=14, pad=20, weight='bold')
            
            # Equal aspect ratio ensures that pie is drawn as a circle.
            ax.axis('equal')  
            plt.tight_layout()
            
            # Save chart
            file_path = os.path.join(TEMP_DIR, f"{user_id}_pie_{uuid.uuid4().hex[:8]}.png")
            
            # Cleanup old user charts
            for f in os.listdir(TEMP_DIR):
                if f.startswith(f"{user_id}_pie_") and f.endswith(".png"):
                    try:
                        os.remove(os.path.join(TEMP_DIR, f))
                    except OSError:
                        pass
                        
            plt.savefig(file_path, facecolor=fig.get_facecolor(), edgecolor='none', dpi=150)
            plt.close(fig)
            return file_path
        except Exception as e:
            import logging
            logging.error(f"Error generating pie chart: {e}")
            return None

    def generate_trend_chart(self, user_id: int, days: List[str], amounts: List[float], title: str = "7 Kunlik Xarajatlar Trendi") -> Optional[str]:
        """
        Generates a line chart representing expenditure trends over time.
        """
        if not days or not amounts:
            return None
            
        try:
            plt.style.use('dark_background')
            fig, ax = plt.subplots(figsize=(7, 4.5), facecolor='#1e1e2e')
            ax.set_facecolor('#1e1e2e')
            
            # Plot line
            ax.plot(days, amounts, marker='o', color='#58a6ff', linewidth=3, markersize=8, label="Xarajat (UZS)")
            ax.fill_between(days, amounts, color='#58a6ff', alpha=0.15)
            
            # Titles and labels
            ax.set_title(title, color='w', fontsize=14, pad=20, weight='bold')
            ax.tick_params(colors='w', labelsize=10)
            
            # Grid
            ax.grid(True, color='#313244', linestyle='--', alpha=0.5)
            
            # Clean up borders
            for spine in ax.spines.values():
                spine.set_color('#313244')
                
            plt.xticks(rotation=30)
            plt.tight_layout()
            
            file_path = os.path.join(TEMP_DIR, f"{user_id}_trend_{uuid.uuid4().hex[:8]}.png")
            
            # Cleanup old user trend charts
            for f in os.listdir(TEMP_DIR):
                if f.startswith(f"{user_id}_trend_") and f.endswith(".png"):
                    try:
                        os.remove(os.path.join(TEMP_DIR, f))
                    except OSError:
                        pass
                        
            plt.savefig(file_path, facecolor=fig.get_facecolor(), edgecolor='none', dpi=150)
            plt.close(fig)
            return file_path
        except Exception as e:
            import logging
            logging.error(f"Error generating trend chart: {e}")
            return None

chart_service = ChartService()
