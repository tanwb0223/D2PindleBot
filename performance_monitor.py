"""
性能监控模块
提供性能指标收集和分析功能
"""
import time
import psutil
import threading
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import logging


@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    execution_time: Optional[float] = None
    operation_name: Optional[str] = None


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self, max_samples: int = 1000):
        self.max_samples = max_samples
        self.metrics: List[PerformanceMetrics] = []
        self.logger = logging.getLogger("Performance")
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # 定时器相关
        self._timers: Dict[str, float] = {}
        self._operation_times: List[tuple] = []  # (operation, duration, timestamp)

    def start_monitoring(self, interval: float = 1.0) -> None:
        """开始性能监控

        Args:
            interval: 监控间隔（秒）
        """
        if self._monitoring:
            return

        self._monitoring = True
        self._stop_event.clear()
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self._monitor_thread.start()
        self.logger.info("性能监控已启动")

    def stop_monitoring(self) -> None:
        """停止性能监控"""
        if not self._monitoring:
            return

        self._monitoring = False
        self._stop_event.set()

        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)

        self.logger.info("性能监控已停止")

    def _monitor_loop(self, interval: float) -> None:
        """监控循环"""
        while self._monitoring and not self._stop_event.is_set():
            try:
                # 收集系统性能指标
                cpu_percent = psutil.cpu_percent()
                memory_info = psutil.virtual_memory()
                memory_mb = memory_info.used / 1024 / 1024

                metrics = PerformanceMetrics(
                    timestamp=time.time(),
                    cpu_percent=cpu_percent,
                    memory_percent=memory_info.percent,
                    memory_mb=memory_mb
                )

                # 添加到指标列表（限制大小）
                if len(self.metrics) >= self.max_samples:
                    self.metrics.pop(0)
                self.metrics.append(metrics)

            except Exception as e:
                self.logger.error(f"收集性能指标失败: {e}")

            # 等待下一次监控
            self._stop_event.wait(interval)

    def start_timer(self, operation_name: str) -> None:
        """开始计时

        Args:
            operation_name: 操作名称
        """
        self._timers[operation_name] = time.time()

    def end_timer(self, operation_name: str) -> float:
        """结束计时

        Args:
            operation_name: 操作名称

        Returns:
            操作耗时（秒）
        """
        if operation_name not in self._timers:
            self.logger.warning(f"未找到计时器: {operation_name}")
            return 0.0

        start_time = self._timers.pop(operation_name)
        duration = time.time() - start_time

        # 记录操作时间
        self._operation_times.append((operation_name, duration, time.time()))

        # 限制历史记录大小
        if len(self._operation_times) > self.max_samples:
            self._operation_times.pop(0)

        return duration

    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """获取当前性能指标"""
        if not self.metrics:
            return None
        return self.metrics[-1]

    def get_average_metrics(self, sample_count: int = 10) -> Optional[Dict[str, float]]:
        """获取平均性能指标

        Args:
            sample_count: 采样数量

        Returns:
            平均性能指标
        """
        if not self.metrics:
            return None

        recent_metrics = self.metrics[-sample_count:]
        if not recent_metrics:
            return None

        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory_mb = sum(m.memory_mb for m in recent_metrics) / len(recent_metrics)

        return {
            'cpu_percent': avg_cpu,
            'memory_percent': avg_memory,
            'memory_mb': avg_memory_mb
        }

    def get_operation_stats(self, operation_name: str) -> Optional[Dict[str, float]]:
        """获取操作统计信息

        Args:
            operation_name: 操作名称

        Returns:
            操作统计信息
        """
        operation_times = [
            duration for op, duration, _ in self._operation_times
            if op == operation_name
        ]

        if not operation_times:
            return None

        return {
            'count': len(operation_times),
            'total_time': sum(operation_times),
            'avg_time': sum(operation_times) / len(operation_times),
            'min_time': min(operation_times),
            'max_time': max(operation_times)
        }

    def get_performance_report(self) -> str:
        """生成性能报告"""
        report = ["性能监控报告", "=" * 50]

        # 系统性能指标
        current = self.get_current_metrics()
        if current:
            report.append(f"当前系统状态:")
            report.append(f"  CPU使用率: {current.cpu_percent:.1f}%")
            report.append(f"  内存使用率: {current.memory_percent:.1f}%")
            report.append(f"  内存使用量: {current.memory_mb:.1f} MB")

        # 平均性能指标
        avg_metrics = self.get_average_metrics()
        if avg_metrics:
            report.append(f"\n平均性能指标:")
            report.append(f"  平均CPU使用率: {avg_metrics['cpu_percent']:.1f}%")
            report.append(f"  平均内存使用率: {avg_metrics['memory_percent']:.1f}%")
            report.append(f"  平均内存使用量: {avg_metrics['memory_mb']:.1f} MB")

        # 操作统计
        if self._operation_times:
            report.append(f"\n操作统计:")
            operations = set(op for op, _, _ in self._operation_times)
            for op in sorted(operations):
                stats = self.get_operation_stats(op)
                if stats:
                    report.append(f"  {op}:")
                    report.append(f"    执行次数: {stats['count']}")
                    report.append(f"    总耗时: {stats['total_time']:.3f}s")
                    report.append(f"    平均耗时: {stats['avg_time']:.3f}s")
                    report.append(f"    最短耗时: {stats['min_time']:.3f}s")
                    report.append(f"    最长耗时: {stats['max_time']:.3f}s")

        return "\n".join(report)

    def save_metrics_to_file(self, filename: str = "performance_metrics.txt") -> None:
        """保存性能指标到文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"性能指标保存时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(self.get_performance_report())

            self.logger.info(f"性能指标已保存到: {filename}")
        except Exception as e:
            self.logger.error(f"保存性能指标失败: {e}")

    def clear_metrics(self) -> None:
        """清空性能指标"""
        self.metrics.clear()
        self._operation_times.clear()
        self.logger.info("性能指标已清空")


# 装饰器版本的性能监控
def monitor_performance(operation_name: Optional[str] = None):
    """性能监控装饰器"""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            monitor = PerformanceMonitor()
            name = operation_name or func.__name__

            monitor.start_timer(name)
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = monitor.end_timer(name)
                if duration > 1.0:  # 只记录超过1秒的操作
                    monitor.logger.info(f"{name} 执行时间: {duration:.3f}s")

        return wrapper
    return decorator


# 全局性能监控实例
_global_monitor = PerformanceMonitor()


def get_global_monitor() -> PerformanceMonitor:
    """获取全局性能监控实例"""
    return _global_monitor