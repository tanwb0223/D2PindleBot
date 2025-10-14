from game_bot import D2PindleBot
import sys


def main():
    print("=" * 50)
    print("暗黑破坏神2 自动刷Pindleskin程序")
    print("=" * 50)
    print("\n使用说明:")
    print("1. 确保游戏已经启动")
    print("2. 角色必须完成安亚救援任务（开启红门）")
    print("3. 角色需要在哈洛加斯城镇")
    print("4. 修改 config.json 配置文件中的坐标和按键设置")
    print("5. 按 Ctrl+C 可以随时停止程序")
    print("\n警告: 使用自动化程序可能违反游戏服务条款，有封号风险!")
    print("=" * 50)
    
    response = input("\n是否继续? (y/n): ")
    if response.lower() != 'y':
        print("已取消")
        sys.exit(0)
    
    config_file = 'config.json'
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    
    bot = D2PindleBot(config_file)
    bot.start()


if __name__ == '__main__':
    main()
