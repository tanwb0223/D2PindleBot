"""
日志配置模块
提供统一的日志配置和管理
"""
import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional


class LoggerConfig:
    """日志配置管理器"""

    @staticmethod
    def setup_logger(name: str = "D2PindleBot",
                    level: int = logging.INFO,
                    log_file: Optional[str] = None,
                    max_bytes: int = 10 * 1024 * 1024,  # 10MB
                    backup_count: int = 5) -> logging.Logger:
        """设置日志记录器

        Args:
            name: 日志记录器名称
            level: 日志级别
            log_file: 日志文件路径，None表示不写入文件
            max_bytes: 单个日志文件最大字节数
            backup_count: 保留的日志文件数量

        Returns:
            配置好的日志记录器
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # 避免重复添加处理器
        if logger.handlers:
            return logger

        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 文件处理器（如果指定了日志文件）
        if log_file:
            try:
                # 确保日志目录存在
                log_dir = os.path.dirname(log_file)
                if log_dir and not os.path.exists(log_dir):
                    os.makedirs(log_dir)

                # 使用RotatingFileHandler实现日志轮转
                file_handler = logging.handlers.RotatingFileHandler(
                    log_file,
                    maxBytes=max_bytes,
                    backupCount=backup_count,
                    encoding='utf-8'
                )
                file_handler.setLevel(level)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)

            except Exception as e:
                # 如果文件处理器设置失败，只使用控制台输出
                logger.error(f"设置日志文件处理器失败: {e}")

        return logger

    @staticmethod
    def get_session_logger(log_dir: str = "logs") -> logging.Logger:
        """获取会话日志记录器

        Args:
            log_dir: 日志目录

        Returns:
            会话日志记录器
        """
        # 创建会话特定的日志文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"bot_session_{timestamp}.log")

        return LoggerConfig.setup_logger(
            name="D2PindleBot",
            level=logging.INFO,
            log_file=log_file
        )

    @staticmethod
    def get_debug_logger() -> logging.Logger:
        """获取调试日志记录器

        Returns:
            调试日志记录器
        """
        return LoggerConfig.setup_logger(
            name="D2PindleBot_Debug",
            level=logging.DEBUG,
            log_file="logs/debug.log"
        )

    @staticmethod
    def setup_performance_monitoring() -> logging.Logger:
        """设置性能监控日志

        Returns:
            性能监控日志记录器
        """
        return LoggerConfig.setup_logger(
            name="Performance",
            level=logging.INFO,
            log_file="logs/performance.log"
        )

    @staticmethod
    def cleanup_old_logs(log_dir: str = "logs", max_files: int = 10) -> None:
        """清理旧的日志文件

        Args:
            log_dir: 日志目录
            max_files: 保留的最大文件数
        """
        try:
            if not os.path.exists(log_dir):
                return

            # 获取所有日志文件并按修改时间排序
            log_files = []
            for filename in os.listdir(log_dir):
                if filename.startswith("bot_session_") and filename.endswith(".log"):
                    file_path = os.path.join(log_dir, filename)
                    mtime = os.path.getmtime(file_path)
                    log_files.append((file_path, mtime))

            # 按修改时间排序（最新的在前）
            log_files.sort(key=lambda x: x[1], reverse=True)

            # 删除超出数量限制的文件
            for file_path, _ in log_files[max_files:]:
                try:
                    os.remove(file_path)
                    print(f"已删除旧日志文件: {file_path}")
                except Exception as e:
                    print(f"删除日志文件失败 {file_path}: {e}")

        except Exception as e:
            print(f"清理日志文件失败: {e}")


# 预定义的日志配置
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/bot.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'detailed',
            'encoding': 'utf-8'
        }
    },
    'loggers': {
        'D2PindleBot': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False
        },
        'Performance': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING'
    }
}