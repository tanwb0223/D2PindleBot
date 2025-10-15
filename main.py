from game_bot import D2PindleBot
import sys
import traceback
from logger_config import LoggerConfig


def print_startup_info():
    """打印启动信息"""
    print("=" * 60)
    print("🎮 暗黑破坏神2 自动刷Pindleskin程序 - 优化版本")
    print("=" * 60)
    print("\n📋 使用说明:")
    print("1. 确保游戏已经启动")
    print("2. 角色必须完成安亚救援任务（开启红门）")
    print("3. 角色需要在哈洛加斯城镇")
    print("4. 修改 config.json 配置文件中的坐标和按键设置")
    print("5. 按 Ctrl+C 可以随时停止程序")
    print("\n⚠️  警告: 使用自动化程序可能违反游戏服务条款，有封号风险!")
    print("💡 建议: 仅在单机模式使用")
    print("=" * 60)


def confirm_start() -> bool:
    """确认是否开始运行"""
    try:
        response = input("\n🚀 是否继续? (y/n): ").strip().lower()
        return response in ['y', 'yes', '是', '开始']
    except KeyboardInterrupt:
        print("\n\n👋 程序已取消")
        return False


def main():
    """主函数"""
    # 设置基础日志
    logger = LoggerConfig.setup_logger("MainApp", level=logging.INFO)

    try:
        print_startup_info()

        if not confirm_start():
            sys.exit(0)

        # 获取配置文件路径
        config_file = 'config.json'
        if len(sys.argv) > 1:
            config_file = sys.argv[1]
            logger.info(f"使用指定配置文件: {config_file}")

        # 创建并启动机器人
        logger.info("正在创建机器人实例...")
        bot = D2PindleBot(config_file)

        logger.info("正在启动机器人...")
        bot.start()

    except KeyboardInterrupt:
        print("\n\n⚡ 用户中断程序")
        logger.info("程序被用户中断")
        sys.exit(0)
    except Exception as e:
        error_msg = f"程序运行出错: {e}"
        print(f"\n❌ {error_msg}")
        logger.error(error_msg)
        logger.error(f"详细错误信息:\n{traceback.format_exc()}")

        # 显示性能报告（如果可用）
        try:
            from performance_monitor import get_global_monitor
            monitor = get_global_monitor()
            print("\n📊 性能报告:")
            print(monitor.get_performance_report())
        except Exception:
            pass

        sys.exit(1)


if __name__ == '__main__':
    main()
