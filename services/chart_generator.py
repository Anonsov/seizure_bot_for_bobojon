import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io
from datetime import datetime
import matplotlib.dates as mdates
from matplotlib.colors import LinearSegmentedColormap


class ChartGenerator:
    def __init__(self, seizure_csv_path):
        """Initialize chart generator with path to seizure data"""
        self.seizure_csv_path = seizure_csv_path

    def _load_data(self):
        """Load and clean the seizure data"""
        df = pd.read_csv(self.seizure_csv_path, skiprows=1)
        if 'Unnamed: 0' in df.columns and '№' not in df.columns:
            df = df.rename(columns={'Unnamed: 0': '№'})

        return df

    def _prepare_interval_data(self, df):
        """Extract dates and intervals from data"""
        dates = []
        intervals = []

        for idx, row in df.iterrows():
            try:
                date_str = row['Дата']
                time_str = row['Время']
                dt = datetime.strptime(f"{date_str} {time_str}", "%m/%d/%Y %H:%M")
                dates.append(dt)

                interval_str = str(row.get('Интервал', ''))
                if interval_str and interval_str.strip():
                    try:
                        intervals.append(float(interval_str))
                    except ValueError:
                        intervals.append(None)
                else:
                    intervals.append(None)
            except Exception as e:
                print(f"Error processing row {idx}: {e}")

        # Filter out None values
        valid_indices = [i for i, val in enumerate(intervals) if val is not None]
        filtered_dates = [dates[i] for i in valid_indices]
        filtered_intervals = [intervals[i] for i in valid_indices]
        normalized_intervals = []
        if filtered_intervals:
            max_interval = max(filtered_intervals)
            normalized_intervals = [i / max_interval for i in filtered_intervals]

        return filtered_dates, filtered_intervals, normalized_intervals

    def _prepare_duration_data(self, df):
        """Extract dates and durations from data"""
        dates = []
        durations = []

        for idx, row in df.iterrows():
            try:
                date_str = row['Дата']
                time_str = row['Время']
                dt = datetime.strptime(f"{date_str} {time_str}", "%m/%d/%Y %H:%M")
                dates.append(dt)

                duration_str = str(row.get('Продолж-сть', ''))
                if 'сек' in duration_str:
                    duration_str = duration_str.replace('сек', '').strip()
                if duration_str and duration_str.strip() and duration_str.strip().replace('.', '', 1).isdigit():
                    durations.append(float(duration_str))
                else:
                    durations.append(None)
            except Exception as e:
                print(f"Error processing row {idx}: {e}")

        valid_indices = [i for i, val in enumerate(durations) if val is not None]
        filtered_dates = [dates[i] for i in valid_indices]
        filtered_durations = [durations[i] for i in valid_indices]

        normalized_durations = []
        if filtered_durations:
            max_duration = max(filtered_durations)
            normalized_durations = [d / max_duration for d in filtered_durations]

        return filtered_dates, filtered_durations, normalized_durations

    def generate_interval_chart(self):
        """
        Generate chart showing intervals between seizures
        Longer intervals (good) are shown in blue, shorter in red
        """
        df = self._load_data()
        dates, intervals, normalized_intervals = self._prepare_interval_data(df)

        if not dates or not intervals:
            plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, "Недостаточно данных для построения графика",
                     horizontalalignment='center', verticalalignment='center',
                     transform=plt.gca().transAxes, fontsize=14)
            plt.title("График интервалов между приступами")

            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plt.close()
            return buf

        cmap = LinearSegmentedColormap.from_list('interval_cmap', ['red', 'yellow', 'blue'])

        plt.figure(figsize=(10, 6))
        scatter = plt.scatter(dates, intervals, c=normalized_intervals, cmap=cmap,
                              s=100, alpha=0.7)
        plt.plot(dates, intervals, '-', color='gray', alpha=0.5)

        cbar = plt.colorbar(scatter)
        cbar.set_label('Относительная длина интервала')

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
        plt.gcf().autofmt_xdate()

        plt.title("Интервалы между приступами")
        plt.xlabel("Дата")
        plt.ylabel("Интервал (дни)")
        plt.grid(True, alpha=0.3)

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()

        return buf

    def generate_duration_chart(self):
        """
        Generate chart showing seizure durations
        Shorter durations (good) are shown in blue, longer in red
        """
        df = self._load_data()
        dates, durations, normalized_durations = self._prepare_duration_data(df)

        if not dates or not durations:
            plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, "Недостаточно данных для построения графика",
                     horizontalalignment='center', verticalalignment='center',
                     transform=plt.gca().transAxes, fontsize=14)
            plt.title("График продолжительности приступов")

            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plt.close()
            return buf

        # Blue for short durations, red for long durations
        cmap = LinearSegmentedColormap.from_list('duration_cmap', ['blue', 'yellow', 'red'])

        plt.figure(figsize=(10, 6))
        scatter = plt.scatter(dates, durations, c=normalized_durations, cmap=cmap,
                              s=100, alpha=0.7)
        plt.plot(dates, durations, '-', color='gray', alpha=0.5)

        cbar = plt.colorbar(scatter)
        cbar.set_label('Относительная продолжительность')

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
        plt.gcf().autofmt_xdate()

        plt.title("Продолжительность приступов")
        plt.xlabel("Дата")
        plt.ylabel("Продолжительность (сек)")
        plt.grid(True, alpha=0.3)

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()

        return buf