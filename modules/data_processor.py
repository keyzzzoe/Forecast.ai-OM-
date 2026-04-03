import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class DataProcessor:
    def __init__(self):
        self.data = None
        self.date_column = None
        self.target_column = None
        self.frequency = None
        self.train_data = None
        self.test_data = None

    def load_data(self, file):
        """Load CSV or Excel file or path string"""
        try:
            if isinstance(file, str):
                if file.endswith('.csv'):
                    self.data = pd.read_csv(file)
                else:
                    self.data = pd.read_excel(file)
            else:
                name = file.name if hasattr(file, 'name') else ''
                if name.endswith('.csv') or name == '':
                    self.data = pd.read_csv(file)
                elif name.endswith(('.xlsx', '.xls')):
                    self.data = pd.read_excel(file)
                else:
                    raise ValueError("不支持的文件格式")
            return self.data
        except Exception as e:
            raise ValueError(f"数据加载失败: {str(e)}")

    def validate_data(self, df, date_col, target_col):
        """Validate data quality"""
        self.data = df
        issues = []

        if date_col not in self.data.columns:
            issues.append(f"日期列 '{date_col}' 不存在")
        if target_col not in self.data.columns:
            issues.append(f"目标列 '{target_col}' 不存在")

        if issues:
            return {'valid': False, 'message': '; '.join(issues)}

        self.date_column = date_col
        self.target_column = target_col

        try:
            self.data[date_col] = pd.to_datetime(self.data[date_col])
        except:
            issues.append(f"日期列格式无法解析")

        try:
            self.data[target_col] = pd.to_numeric(self.data[target_col])
        except:
            issues.append(f"目标列不是数值类型")

        if len(self.data) < 30:
            issues.append(f"数据量不足（需要至少30行）")

        missing_dates = self.data[date_col].isna().sum()
        missing_target = self.data[target_col].isna().sum()
        if missing_dates > 0:
            issues.append(f"日期列有{missing_dates}个缺失值")
        if missing_target > 0:
            issues.append(f"目标列有{missing_target}个缺失值")

        duplicates = self.data[date_col].duplicated().sum()
        if duplicates > 0:
            issues.append(f"发现{duplicates}个重复日期")

        if issues:
            return {'valid': False, 'message': '; '.join(issues)}

        self.data = self.data.sort_values(date_col).reset_index(drop=True)
        self.frequency = self._detect_frequency()

        return {'valid': True, 'message': '数据验证通过'}

    def _detect_frequency(self):
        """Detect time series frequency"""
        dates = pd.to_datetime(self.data[self.date_column])
        diffs = dates.diff().dropna()
        median_diff = diffs.median()

        if median_diff <= timedelta(days=1):
            return "daily"
        elif median_diff <= timedelta(days=7):
            return "weekly"
        elif median_diff <= timedelta(days=31):
            return "monthly"
        else:
            return "other"

    def get_data_summary(self):
        """Get data quality summary"""
        if self.data is None:
            return {}

        target_data = self.data[self.target_column]

        return {
            "total_rows": len(self.data),
            "date_range": (
                str(self.data[self.date_column].min().date()),
                str(self.data[self.date_column].max().date())
            ),
            "frequency": self.frequency,
            "target_mean": round(float(target_data.mean()), 2),
            "target_std": round(float(target_data.std()), 2),
            "target_min": round(float(target_data.min()), 2),
            "target_max": round(float(target_data.max()), 2),
            "missing_values": int(target_data.isna().sum()),
            "outliers": int(self._count_outliers(target_data))
        }

    def _count_outliers(self, series):
        """Count outliers using IQR method"""
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        return ((series < lower) | (series > upper)).sum()

    def prepare_time_series(self, df, date_col, target_col):
        """Prepare clean time series DataFrame"""
        self.date_column = date_col
        self.target_column = target_col
        self.data = df.copy()
        self.data[date_col] = pd.to_datetime(self.data[date_col])
        self.data[target_col] = pd.to_numeric(self.data[target_col])
        self.data = self.data.sort_values(date_col).reset_index(drop=True)
        return self.data[[date_col, target_col]]

    def split_train_test(self, df=None, test_size=0.2):
        """Split data into train and test sets"""
        data = df if df is not None else self.data
        split_idx = int(len(data) * (1 - test_size))
        self.train_data = data.iloc[:split_idx].copy()
        self.test_data = data.iloc[split_idx:].copy()
        return self.train_data, self.test_data

    def create_features(self, df):
        """Create time series features"""
        df = df.copy()

        # Lag features
        for lag in [1, 7, 30]:
            df[f'lag_{lag}'] = df[self.target_column].shift(lag)

        # Rolling statistics
        for window in [7, 30]:
            df[f'rolling_mean_{window}'] = df[self.target_column].rolling(window).mean()
            df[f'rolling_std_{window}'] = df[self.target_column].rolling(window).std()

        # Time-based features
        df['day_of_week'] = pd.to_datetime(df[self.date_column]).dt.dayofweek
        df['day_of_month'] = pd.to_datetime(df[self.date_column]).dt.day
        df['month'] = pd.to_datetime(df[self.date_column]).dt.month
        df['quarter'] = pd.to_datetime(df[self.date_column]).dt.quarter

        return df

    def get_clean_series(self, dataset='train'):
        """Get clean time series for modeling"""
        data = self.train_data if dataset == 'train' else self.test_data
        return data[[self.date_column, self.target_column]].copy()
