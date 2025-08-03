import pandas as pd
import os
from datetime import datetime
from config import path_to_csv


class CSVManager:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        # Ensure the directory exists
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)

        # Check if file exists, if not create it with headers
        if not os.path.exists(csv_path):
            self._create_empty_csv()

    def _create_empty_csv(self):
        """Create an empty CSV file with appropriate headers"""
        headers = [
            "Судорожные приступы", "", "", "", "", ""
        ]
        subheaders = [
            "№", "Дата", "Время", "Продолж-сть", "Интервал", "Комментарии"
        ]

        # Create DataFrame with headers
        df = pd.DataFrame([headers, subheaders])
        df.to_csv(self.csv_path, index=False, header=False)

    def get_data(self):
        """Read the CSV file and return as DataFrame"""
        try:
            df = pd.read_csv(self.csv_path, skiprows=1)  # Skip the title row
            return df
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return pd.DataFrame()

    def add_seizure_record(self, datetime_str, duration, comment=""):
        """
        Add a new seizure record to the CSV file

        Args:
            datetime_str (str): Date and time in format 'YYYY-MM-DD HH:MM'
            duration (str): Duration of the seizure
            comment (str): Optional comment

        Returns:
            tuple: (Success status, interval in days)
        """
        try:
            # Parse the datetime
            dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")

            # Format date as MM/DD/YYYY for CSV
            date_str = dt.strftime("%m/%d/%Y")
            # Format time as HH:MM for CSV
            time_str = dt.strftime("%H:%M")

            # Read existing data
            df = self.get_data()

            # Calculate the row number for the new entry
            if df.empty or len(df.columns) < 6:
                new_row_num = 1
                interval = ""
            else:
                # Clean up column names if needed
                if '№' not in df.columns and 'Unnamed: 0' in df.columns:
                    df = df.rename(columns={'Unnamed: 0': '№'})

                # Get the last row number
                try:
                    last_row_num = int(df['№'].iloc[-1])
                    new_row_num = last_row_num + 1
                except:
                    new_row_num = 1

                # Calculate interval if possible
                interval_days = None
                try:
                    last_date = df['Дата'].iloc[-1]
                    last_time = df['Время'].iloc[-1]
                    last_dt = datetime.strptime(f"{last_date} {last_time}", "%m/%d/%Y %H:%M")

                    # Calculate days between seizures
                    delta = (dt - last_dt).days
                    interval = str(delta) if delta > 0 else "0"
                    interval_days = delta
                except:
                    interval = ""

            # Create new row
            new_row = {
                '№': new_row_num,
                'Дата': date_str,
                'Время': time_str,
                'Продолж-сть': duration,
                'Интервал': interval,
                'Комментарии': comment
            }

            # Append to DataFrame
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

            # Write back to CSV, preserving the header
            with open(self.csv_path, 'r') as f:
                header = f.readline().strip()

            with open(self.csv_path, 'w') as f:
                f.write(header + '\n')
                df.to_csv(f, index=False)

            return True, interval_days

        except Exception as e:
            print(f"Error adding seizure record: {e}")
            return False, None

    def get_statistics(self):
        """
        Calculate statistics from the seizure data

        Returns:
            dict: Statistics about seizures
        """
        try:
            df = self.get_data()
            stats = {
                "total_seizures": len(df),
                "avg_interval": df["Интервал"].astype(float).mean() if "Интервал" in df else 0,
                "avg_duration": None,  # Would need to parse duration strings
                "last_seizure": None,
            }

            if not df.empty:
                last_row = df.iloc[-1]
                stats["last_seizure"] = {
                    "date": last_row["Дата"],
                    "time": last_row["Время"],
                    "duration": last_row["Продолж-сть"]
                }

            return stats
        except Exception as e:
            print(f"Error calculating statistics: {e}")
            return {}


# Create a singleton instance
csv_manager = CSVManager(path_to_csv)