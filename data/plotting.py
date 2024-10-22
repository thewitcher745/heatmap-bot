import pandas as pd
from matplotlib import pyplot as plt
import mplfinance as mpf
import seaborn as sns
from mpl_toolkits.axes_grid1.inset_locator import inset_axes


class PlottingTool:
    def __init__(self, title: str):
        self.fig, self.ax = plt.subplots(figsize=(12, 10))

        self.ax.set_facecolor('#131722')  # Set background color directly on ax
        self.fig.patch.set_facecolor('#131722')  # Set background color directly on ax

        # Set tick colors and font sizes
        self.ax.tick_params(axis='x', colors='white', labelsize=14)
        self.ax.tick_params(axis='y', colors='white', labelsize=18)

        # Set axes lines (spines) colors
        self.ax.spines['top'].set_color('#131722')
        self.ax.spines['bottom'].set_color('#131722')
        self.ax.spines['left'].set_color('#131722')
        self.ax.spines['right'].set_color('#131722')

        # Add title
        self.ax.set_title('Candlestick Chart', color='white', fontsize=25)

    def draw_candlesticks(self, candlesticks_df: pd.DataFrame):
        # Define custom style
        custom_style = mpf.make_mpf_style(
            marketcolors=mpf.make_marketcolors(
                up='#00B3C4', down='#DB4352',
                edge='i', wick='i',
            ),
        )

        mpf.plot(candlesticks_df, type='candle', ylabel='', style=custom_style, ax=self.ax)

    def draw_heatmap(self, orderbook):
        bids = orderbook['bids']
        asks = orderbook['asks']

        # Format the bids/asks for heatmap plotting
        bid_prices = [float(bid[0]) for bid in bids]
        bid_volumes = [float(bid[1]) for bid in bids]
        ask_prices = [float(ask[0]) for ask in asks]
        ask_volumes = [float(ask[1]) for ask in asks]

        # Create a heatmap with price on one axis and volume as intensity
        plt.figure(figsize=(10, 6))
        sns.heatmap([bid_volumes, ask_volumes], cmap='coolwarm', ax=self.ax)

    def save(self):
        self.fig.savefig("candlesticks.png")

    @staticmethod
    def show():
        plt.show()
