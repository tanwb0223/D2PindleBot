"""
项目启动脚本
提供安全启动和环境检查功能
"""
import sys
import os
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from logger_config import LoggerConfig
from config_validator import ConfigValidator
from performance_monitor import get_global_monitor


def check_python_version() -> bool:
    """检查Python版本"""
    if sys.version_info < (3, 7):
        print("错误: 需要Python 3.7或更高版本")
        return False
    print(f"✓ Python版本: {sys.version}")
    return True


def check_dependencies() -> bool:
    """检查依赖包"""
    required_packages = {
        'cv2': 'opencv-python',
        'numpy': 'numpy',
        'PIL': 'Pillow',
        'win32gui': 'pywin32',
        'psutil': 'psutil'
    }

    missing_packages = []
    for module, package_name in required_packages.items():
        try:
            __import__(module)
            print(f"✓ {package_name} 已安装")
        except ImportError:
            print(f"✗ {package_name} 未安装")
            missing_packages.append(package_name)

    if missing_packages:
        print(f"\n请安装缺失的包:")
        print(f"pip install {' '.join(missing_packages)}")
        return False

    return True


def check_config_file() -> bool:
    """检查配置文件"""
    config_file = "config.json"
    if not os.path.exists(config_file):
        print(f"✗ 配置文件不存在: {config_file}")
        print("正在创建默认配置文件...")

        try:
            validator = ConfigValidator()
            validator.create_default_config(config_file)
            print(f"✓ 默认配置文件已创建: {config_file}")
            print("请编辑配置文件并设置正确的坐标后再运行程序")
            return False
        except Exception as e:
            print(f"✗ 创建配置文件失败: {e}")
            return False
    else:
        print(f"✓ 配置文件存在: {config_file}")

        # 验证配置文件
        try:
            validator = ConfigValidator()
            config = validator.load_and_validate_config(config_file)
            print("✓ 配置文件验证通过")
            return True
        except Exception as e:
            print(f"✗ 配置文件验证失败: {e}")
            return False


def setup_directories() -> bool:
    """创建必要的目录"""
    directories = ['logs', 'screenshots', 'reports']

    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                print(f"✓ 创建目录: {directory}")
            except Exception as e:
                print(f"✗ 创建目录失败 {directory}: {e}")
                return False
        else:
            print(f"✓ 目录已存在: {directory}")

    return True


def cleanup_old_logs() -> None:
    """清理旧日志"""
    try:
        LoggerConfig.cleanup_old_logs("logs", max_files=5)
    except Exception as e:
        print(f"清理日志失败: {e}")


def main() -> int:
    """主启动函数"""
    print("=" * 60)
    print("D2 Pindleskin Bot - 启动检查")
    print("=" * 60)

    # 环境检查
    checks = [
        ("Python版本检查", check_python_version),
        ("依赖包检查", check_dependencies),
        ("配置文件检查", check_config_file),
        ("目录结构检查", setup_directories)
    ]

    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        print("-" * 30)
        if not check_func():
            print(f"{check_name}失败，程序退出")
            return 1

    # 清理旧日志
    print(f"\n清理旧日志:")
    print("-" * 30)
    cleanup_old_logs()

    # 启动成功
    print("\n" + "=" * 60)
    print("✓ 所有检查通过，可以启动主程序")
    print("运行命令: python main.py")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())