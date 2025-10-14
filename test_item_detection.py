"""
测试物品检测功能
用于调试和查看检测到的物品位置
"""
import cv2
import numpy as np
from item_detector import ItemDetector
import time

def main():
    print("=" * 60)
    print("暗黑2物品检测测试工具")
    print("=" * 60)
    print("\n功能说明:")
    print("1. 截取指定区域屏幕")
    print("2. 检测暗金、绿装、符文等物品")
    print("3. 在图像上标记检测到的物品")
    print("4. 保存结果图像到 detected_items.png")
    print("\n使用步骤:")
    print("1. 启动游戏，击杀Pindleskin，等待物品掉落")
    print("2. 运行此脚本")
    print("3. 查看控制台输出和生成的图像")
    print("=" * 60)
    
    # 配置检测区域（D2R 1920x1080分辨率）
    scan_area = (400, 250, 1520, 800)  # (x1, y1, x2, y2)
    item_types = ['unique', 'set', 'rune', 'rare']
    
    print("\n注意: 此工具针对D2R重置版优化")
    print("如果使用其他分辨率，请调整 scan_area 参数")
    
    print(f"\n扫描区域: {scan_area}")
    print(f"物品类型: {', '.join(item_types)}")
    print("\n3秒后开始检测...")
    time.sleep(3)
    
    # 创建检测器
    detector = ItemDetector()
    
    # 截取屏幕
    print("正在截取屏幕...")
    img = detector.capture_screen(scan_area)
    
    # 检测物品
    print("正在检测物品...")
    items = detector.detect_items_by_color(img, item_types)
    
    # 输出结果
    print(f"\n检测到 {len(items)} 个物品:")
    for idx, (x, y, item_type) in enumerate(items):
        abs_x = scan_area[0] + x
        abs_y = scan_area[1] + y
        print(f"  物品 {idx+1} [{item_type}]: 相对坐标({x}, {y}), 绝对坐标({abs_x}, {abs_y})")
    
    # 在图像上标记物品
    result_img = img.copy()
    
    # 不同类型用不同颜色
    type_colors = {
        'unique': (0, 165, 255),  # 橙色
        'set': (0, 255, 0),       # 绿色
        'rune': (0, 140, 255),    # 橙红色
        'rare': (0, 255, 255),    # 黄色
        'magic': (255, 0, 0)      # 蓝色
    }
    
    for x, y, item_type in items:
        color = type_colors.get(item_type, (255, 255, 255))
        cv2.circle(result_img, (x, y), 15, color, 3)
        cv2.putText(result_img, f"{item_type}", (x+20, y-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.putText(result_img, f"({x},{y})", (x+20, y+10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
    
    # 保存结果
    output_file = 'detected_items.png'
    cv2.imwrite(output_file, result_img)
    print(f"\n结果已保存到: {output_file}")
    
    # 显示图像（可选）
    try:
        cv2.imshow('Detected Items', result_img)
        print("\n按任意键关闭图像窗口...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except:
        print("无法显示图像窗口，但已保存到文件")
    
    print("\n测试完成！")
    print("\n提示: 如果检测不准确，可以调整 item_detector.py 中的颜色范围")


if __name__ == '__main__':
    main()
