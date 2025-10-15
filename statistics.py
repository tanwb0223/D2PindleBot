"""
统计系统 - 追踪刷怪效率和物品掉落
"""
import time
from typing import Dict, List, Optional
from datetime import datetime
import logging


class Statistics:
    """刷怪统计"""

    def __init__(self, max_history: int = 1000):
        self.start_time = time.time()
        self.total_runs = 0
        self.successful_runs = 0
        self.failed_runs = 0
        self.run_times: List[float] = []
        self.items_picked: Dict[str, int] = {
            "unique": 0,
            "rune": 0,
            "set": 0,
            "rare": 0
        }
        self.last_report_time = time.time()
        self.logger = logging.getLogger(__name__)

        # 性能优化：限制历史记录大小
        self.max_history = max_history
    
    def start_run(self) -> None:
        """开始一次刷怪"""
        self.run_start_time = time.time()

    def end_run(self, success: bool = True, items: Optional[Dict[str, int]] = None) -> None:
        """结束一次刷怪"""
        try:
            duration = time.time() - self.run_start_time

            # 性能优化：限制历史记录大小
            if len(self.run_times) >= self.max_history:
                self.run_times.pop(0)  # 移除最旧的记录

            self.run_times.append(duration)
            self.total_runs += 1

            if success:
                self.successful_runs += 1
            else:
                self.failed_runs += 1

            # 更新拾取物品统计
            if items:
                for item_type, count in items.items():
                    if item_type in self.items_picked:
                        self.items_picked[item_type] += count

        except Exception as e:
            self.logger.error(f"统计记录失败: {e}")
    
    def get_elapsed_time(self) -> float:
        """获取总运行时间（秒）"""
        return time.time() - self.start_time
    
    def get_average_run_time(self) -> float:
        """获取平均单局时间"""
        if not self.run_times:
            return 0.0
        return sum(self.run_times) / len(self.run_times)
    
    def get_runs_per_hour(self) -> float:
        """获取每小时刷怪次数"""
        elapsed = self.get_elapsed_time()
        if elapsed == 0:
            return 0.0
        return (self.total_runs / elapsed) * 3600
    
    def get_success_rate(self) -> float:
        """获取成功率"""
        if self.total_runs == 0:
            return 0.0
        return (self.successful_runs / self.total_runs) * 100
    
    def get_report(self, detailed: bool = False) -> str:
        """生成统计报告"""
        elapsed = self.get_elapsed_time()
        avg_time = self.get_average_run_time()
        runs_per_hour = self.get_runs_per_hour()
        success_rate = self.get_success_rate()
        
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        
        report = f"""
╔══════════════════════════════════════════╗
║          📊 刷怪统计报告                  ║
╠══════════════════════════════════════════╣
║ 运行时长: {hours:02d}:{minutes:02d}:{seconds:02d}
║ 总次数:   {self.total_runs}
║ 成功:     {self.successful_runs}
║ 失败:     {self.failed_runs}
║ 成功率:   {success_rate:.1f}%
║ 
║ 效率指标:
║ - 平均单局时间: {avg_time:.2f} 秒
║ - 每小时次数:   {runs_per_hour:.1f}
║ 
║ 拾取物品:
║ - 💎 暗金: {self.items_picked['unique']}
║ - 🔮 符文: {self.items_picked['rune']}
║ - 🌟 绿装: {self.items_picked['set']}
║ - ⚡ 亮黄: {self.items_picked['rare']}
╚══════════════════════════════════════════╝
"""
        
        if detailed and self.run_times:
            # 添加详细时间分析
            min_time = min(self.run_times)
            max_time = max(self.run_times)
            recent_avg = sum(self.run_times[-10:]) / min(10, len(self.run_times))
            
            report += f"""
详细分析:
- 最快单局: {min_time:.2f} 秒
- 最慢单局: {max_time:.2f} 秒
- 最近10局平均: {recent_avg:.2f} 秒
"""
        
        return report
    
    def get_short_status(self) -> str:
        """获取简短状态（用于日志）"""
        return (f"进度: {self.total_runs} 次 | "
                f"成功率: {self.get_success_rate():.1f}% | "
                f"效率: {self.get_runs_per_hour():.1f} 次/小时 | "
                f"暗金: {self.items_picked['unique']} | "
                f"符文: {self.items_picked['rune']}")
    
    def should_report(self, interval: int = 300) -> bool:
        """判断是否应该生成报告（默认每5分钟）"""
        now = time.time()
        if now - self.last_report_time >= interval:
            self.last_report_time = now
            return True
        return False
    
    def save_to_file(self, filename: str = "statistics.txt"):
        """保存统计到文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"统计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(self.get_report(detailed=True))
                f.write("\n\n运行时间记录:\n")
                for i, run_time in enumerate(self.run_times, 1):
                    f.write(f"第{i}局: {run_time:.2f}秒\n")
        except Exception as e:
            print(f"保存统计失败: {e}")
