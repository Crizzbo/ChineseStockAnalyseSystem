"""
数据验证工具
用于验证从AKShare获取的股票数据的完整性和准确性
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DataValidator:
    """数据验证器"""

    def __init__(self):
        self.logger = logger

    def validate_stock_data(self, data: pd.DataFrame, data_type: str = 'historical') -> Dict[str, Any]:
        """
        验证股票数据质量

        Args:
            data: 股票数据DataFrame
            data_type: 数据类型 ('historical', 'realtime', 'financial')

        Returns:
            Dict: 验证结果
        """
        try:
            validation_result = {
                'is_valid': True,
                'errors': [],
                'warnings': [],
                'data_info': {
                    'total_rows': len(data) if data is not None else 0,
                    'total_columns': len(data.columns) if data is not None else 0,
                    'date_range': None,
                    'data_type': data_type
                }
            }

            if data is None or data.empty:
                validation_result['is_valid'] = False
                validation_result['errors'].append('数据为空或None')
                return validation_result

            # 根据数据类型执行不同的验证
            if data_type == 'historical':
                self._validate_historical_data(data, validation_result)
            elif data_type == 'realtime':
                self._validate_realtime_data(data, validation_result)
            elif data_type == 'financial':
                self._validate_financial_data(data, validation_result)
            else:
                self._validate_basic_data(data, validation_result)

            # 通用验证
            self._validate_common_issues(data, validation_result)

            # 设置最终验证状态
            validation_result['is_valid'] = len(validation_result['errors']) == 0

            if validation_result['is_valid']:
                self.logger.info(f"{data_type}数据验证通过")
            else:
                self.logger.warning(f"{data_type}数据验证失败: {validation_result['errors']}")

            return validation_result

        except Exception as e:
            self.logger.error(f"数据验证过程中发生错误: {str(e)}")
            return {
                'is_valid': False,
                'errors': [f'验证过程异常: {str(e)}'],
                'warnings': [],
                'data_info': {}
            }

    def _validate_historical_data(self, data: pd.DataFrame, result: Dict):
        """验证历史数据"""
        required_columns = ['开盘', '收盘', '最高', '最低', '成交量']

        # 检查必需列
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            result['errors'].append(f'缺少必需列: {missing_columns}')

        # 检查OHLC数据逻辑
        for col in required_columns[:4]:  # OHLC列
            if col in data.columns:
                if (data[col] <= 0).any():
                    result['errors'].append(f'{col}列存在非正数值')

        # 检查最高最低价逻辑
        if '最高' in data.columns and '最低' in data.columns:
            if (data['最高'] < data['最低']).any():
                result['errors'].append('最高价低于最低价的异常数据')

        # 检查开盘收盘价是否在最高最低价范围内
        if all(col in data.columns for col in ['开盘', '收盘', '最高', '最低']):
            if ((data['开盘'] > data['最高']) | (data['开盘'] < data['最低'])).any():
                result['warnings'].append('开盘价超出最高最低价范围')

            if ((data['收盘'] > data['最高']) | (data['收盘'] < data['最低'])).any():
                result['warnings'].append('收盘价超出最高最低价范围')

        # 检查成交量
        if '成交量' in data.columns:
            if (data['成交量'] < 0).any():
                result['errors'].append('成交量存在负数')

        # 检查日期连续性
        if '日期' in data.columns:
            self._validate_date_continuity(data, result)

    def _validate_realtime_data(self, data: pd.DataFrame, result: Dict):
        """验证实时数据"""
        expected_columns = ['代码', '名称', '最新价', '涨跌幅', '成交量']

        # 检查基本列
        missing_columns = [col for col in expected_columns if col not in data.columns]
        if missing_columns:
            result['warnings'].append(f'缺少常见列: {missing_columns}')

        # 检查价格数据
        if '最新价' in data.columns:
            if (data['最新价'] <= 0).any():
                result['errors'].append('最新价存在非正数值')

        # 检查涨跌幅范围（A股一般在-10%到+10%之间，科创板和创业板除外）
        if '涨跌幅' in data.columns:
            extreme_changes = (data['涨跌幅'] > 20) | (data['涨跌幅'] < -20)
            if extreme_changes.any():
                result['warnings'].append('存在极端涨跌幅数据（>20%或<-20%）')

    def _validate_financial_data(self, data: pd.DataFrame, result: Dict):
        """验证财务数据"""
        # 检查数值列是否为数值类型
        numeric_columns = data.select_dtypes(include=[np.number]).columns

        for col in numeric_columns:
            # 检查无穷大值
            if np.isinf(data[col]).any():
                result['warnings'].append(f'{col}列存在无穷大值')

            # 检查极端异常值
            if data[col].std() > 0:
                z_scores = np.abs((data[col] - data[col].mean()) / data[col].std())
                if (z_scores > 5).any():
                    result['warnings'].append(f'{col}列存在极端异常值（Z-score > 5）')

    def _validate_basic_data(self, data: pd.DataFrame, result: Dict):
        """基本数据验证"""
        # 检查数据框基本信息
        if len(data) == 0:
            result['errors'].append('数据行数为0')

        if len(data.columns) == 0:
            result['errors'].append('数据列数为0')

    def _validate_common_issues(self, data: pd.DataFrame, result: Dict):
        """通用问题验证"""
        # 检查重复行
        duplicate_count = data.duplicated().sum()
        if duplicate_count > 0:
            result['warnings'].append(f'存在{duplicate_count}行重复数据')

        # 检查完全空列
        empty_columns = [col for col in data.columns if data[col].isnull().all()]
        if empty_columns:
            result['warnings'].append(f'存在完全为空的列: {empty_columns}')

        # 检查缺失值比例
        missing_ratio = data.isnull().mean()
        high_missing_columns = missing_ratio[missing_ratio > 0.5].index.tolist()
        if high_missing_columns:
            result['warnings'].append(f'以下列缺失值超过50%: {high_missing_columns}')

        # 更新数据信息
        if '日期' in data.columns:
            try:
                date_col = pd.to_datetime(data['日期'])
                result['data_info']['date_range'] = {
                    'start': date_col.min().strftime('%Y-%m-%d'),
                    'end': date_col.max().strftime('%Y-%m-%d'),
                    'days': (date_col.max() - date_col.min()).days
                }
            except Exception:
                result['warnings'].append('日期列格式异常')

    def _validate_date_continuity(self, data: pd.DataFrame, result: Dict):
        """验证日期连续性"""
        try:
            if '日期' not in data.columns:
                return

            dates = pd.to_datetime(data['日期']).sort_values()
            if len(dates) < 2:
                return

            # 检查日期间隔
            date_diffs = dates.diff().dt.days.dropna()

            # 正常交易日间隔应该是1-7天（考虑周末和节假日）
            unusual_gaps = date_diffs[date_diffs > 10]
            if not unusual_gaps.empty:
                result['warnings'].append(f'存在异常的日期间隔: 最大间隔{unusual_gaps.max()}天')

            # 检查是否有未来日期
            today = datetime.now().date()
            future_dates = dates[dates.dt.date > today]
            if not future_dates.empty:
                result['warnings'].append('存在未来日期的数据')

        except Exception as e:
            result['warnings'].append(f'日期验证异常: {str(e)}')

    def validate_multiple_datasets(self, datasets: Dict[str, pd.DataFrame]) -> Dict[str, Dict]:
        """
        验证多个数据集

        Args:
            datasets: 数据集字典，键为数据集名称，值为DataFrame

        Returns:
            Dict: 各数据集的验证结果
        """
        results = {}

        for name, data in datasets.items():
            try:
                # 根据名称推测数据类型
                if 'historical' in name.lower() or 'hist' in name.lower():
                    data_type = 'historical'
                elif 'realtime' in name.lower() or 'spot' in name.lower():
                    data_type = 'realtime'
                elif 'financial' in name.lower() or 'balance' in name.lower() or 'income' in name.lower():
                    data_type = 'financial'
                else:
                    data_type = 'general'

                results[name] = self.validate_stock_data(data, data_type)

            except Exception as e:
                results[name] = {
                    'is_valid': False,
                    'errors': [f'验证过程异常: {str(e)}'],
                    'warnings': [],
                    'data_info': {}
                }

        return results

    def generate_data_quality_report(self, validation_result: Dict) -> str:
        """
        生成数据质量报告

        Args:
            validation_result: 验证结果

        Returns:
            str: 质量报告文本
        """
        report_lines = []
        report_lines.append("=== 数据质量报告 ===")
        report_lines.append(f"验证状态: {'通过' if validation_result['is_valid'] else '失败'}")

        # 数据基本信息
        data_info = validation_result.get('data_info', {})
        report_lines.append(f"数据行数: {data_info.get('total_rows', 'N/A')}")
        report_lines.append(f"数据列数: {data_info.get('total_columns', 'N/A')}")

        if data_info.get('date_range'):
            date_range = data_info['date_range']
            report_lines.append(f"日期范围: {date_range['start']} 至 {date_range['end']} ({date_range['days']}天)")

        # 错误信息
        errors = validation_result.get('errors', [])
        if errors:
            report_lines.append("\n--- 错误信息 ---")
            for i, error in enumerate(errors, 1):
                report_lines.append(f"{i}. {error}")

        # 警告信息
        warnings = validation_result.get('warnings', [])
        if warnings:
            report_lines.append("\n--- 警告信息 ---")
            for i, warning in enumerate(warnings, 1):
                report_lines.append(f"{i}. {warning}")

        if not errors and not warnings:
            report_lines.append("\n数据质量良好，无错误或警告。")

        return "\n".join(report_lines)

    def suggest_data_fixes(self, validation_result: Dict) -> List[str]:
        """
        基于验证结果提供数据修复建议

        Args:
            validation_result: 验证结果

        Returns:
            List[str]: 修复建议列表
        """
        suggestions = []

        errors = validation_result.get('errors', [])
        warnings = validation_result.get('warnings', [])

        # 基于错误提供建议
        for error in errors:
            if '缺少必需列' in error:
                suggestions.append("建议检查数据源API是否正常，或更新列名映射")
            elif '非正数值' in error:
                suggestions.append("建议过滤掉价格或成交量为非正数的异常记录")
            elif '最高价低于最低价' in error:
                suggestions.append("建议检查并修正OHLC数据的逻辑错误")

        # 基于警告提供建议
        for warning in warnings:
            if '重复数据' in warning:
                suggestions.append("建议使用drop_duplicates()方法去除重复行")
            elif '缺失值超过50%' in warning:
                suggestions.append("建议删除缺失值过多的列，或使用插值方法填补")
            elif '极端异常值' in warning:
                suggestions.append("建议使用3σ法则或IQR方法检测并处理异常值")

        if not suggestions:
            suggestions.append("数据质量良好，暂无修复建议")

        return suggestions