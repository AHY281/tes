import pyautogui
import time
import os
import sys
import ctypes
import pyperclip
import threading
import keyboard

w, h = pyautogui.size()
region_w = w // 3
region_h = h // 2

regions = {
    "top_left": (region_w * 0, 0, region_w, region_h),
    "top_center": (region_w * 1, 0, region_w, region_h),
    "top_right": (region_w * 2, 0, region_w, region_h),
    "bottom_left": (region_w * 0, region_h, region_w, region_h),
    "bottom_center": (region_w * 1, region_h, region_w, region_h),
    "bottom_right": (region_w * 2, region_h, region_w, region_h),
    "scrollbar": (w - 20, 0, 20, h),
}

IMAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
MAX_PAGE_CLICKS = 200
should_exit = False

def on_exit_key(event):
    global should_exit
    if event.name == 'esc':
        should_exit = True
        print("\n\n【中断】检测到 ESC 键，正在退出...")

keyboard.on_press(on_exit_key)

def check_exit():
    global should_exit
    return should_exit

def get_center(location):
    if location is None:
        return None
    return (location[0] + location[2] // 2, location[1] + location[3] // 2)

def show_alert(title, message):
    return ctypes.windll.user32.MessageBoxW(0, message, title, 1)

def find_image(image_name, regions_list, y_start=0, confidence=0.7, grayscale=False):
    image_path = os.path.join(IMAGE_DIR, image_name)
    if not os.path.exists(image_path):
        print(f"【错误】图片不存在: {image_path}")
        return None
    
    print(f"【找图】正在搜索 {image_name} (y_start={y_start}, confidence={confidence})...")
    
    for region_name in regions_list:
        region = regions.get(region_name)
        if region is None:
            continue
        
        region_x, region_y, region_w, region_h = region
        
        if y_start > region_y + region_h:
            continue
        
        adjusted_region = (region_x, max(region_y, y_start), region_w, region_h)
        
        print(f"       → 在 {region_name} 区域搜索...")
        
        try:
            location = pyautogui.locateOnScreen(
                image=image_path,
                grayscale=grayscale,
                region=adjusted_region,
                confidence=confidence
            )
            if location is not None:
                center = get_center(location)
                print(f"【成功】在{region_name}找到 {image_name}! 位置: {center}")
                return center
        except pyautogui.ImageNotFoundException:
            print(f"       → {region_name} 未找到")
        except Exception as e:
            print(f"       → {region_name} 出错: {e}")
    
    print(f"【失败】未找到 {image_name}")
    return None

def drag_scroll_up(distance=100):
    print(f"【操作】鼠标滚轮下滚 {distance} 像素")
    pyautogui.scroll(-distance)
    time.sleep(0.5)
    return False

def scroll_down(pixels=300):
    print(f"【操作】鼠标滚轮下滚 {pixels} 像素")
    pyautogui.scroll(-pixels)
    time.sleep(0.5)

def main():
    print("=" * 60)
    print("       自动评教脚本 v2.3 (图像识别版)")
    print("=" * 60)
    print(f"【配置】屏幕分辨率: {w}x{h}")
    print(f"【配置】图片目录: {IMAGE_DIR}")
    print(f"【配置】预设最大翻页次数: {MAX_PAGE_CLICKS}")
    print("【提示】按 ESC 键可强制停止脚本")
    print("=" * 60)
    
    input("【提示】按回车键开始...")
    
    print("\n【倒计时】3秒后开始自动评价...")
    for i in range(3, 0, -1):
        print(f"\r【倒计时】{i}秒", end="")
        time.sleep(1)
    print("\n【开始】自动评价启动!")
    
    total_evaluated = 0
    page_clicks = 0
    
    try:
        while page_clicks < MAX_PAGE_CLICKS:
            if check_exit():
                print("\n【退出】用户中断，脚本终止")
                sys.exit(0)
                
            print(f"\n{'='*60}")
            print(f"【阶段1/5】寻找未评项目")
            print(f"{'='*60}")
            
            wp_pos = find_image("wp.png", ["top_right", "bottom_right"], confidence=0.8, grayscale=True)
            n_pos = None
            
            if wp_pos is None:
                print("\n【提示】未找到wp.png，开始下滑侦查...")
                
                while True:
                    if check_exit():
                        print("\n【退出】用户中断，脚本终止")
                        sys.exit(0)
                        
                    print(f"\n--- 执行一次深度下滑 (800像素) ---")
                    scroll_down(800)
                    
                    print("【侦查】下滑后，重新寻找 wp.png 和 n.png...")
                    wp_pos = find_image("wp.png", ["top_right", "bottom_right"], confidence=0.8, grayscale=True)
                    n_pos = find_image("n.png", ["bottom_center"], confidence=0.8, grayscale=True)
                    
                    if wp_pos is not None:
                        print("【侦查结果】找到 wp.png！停止下滑。")
                        break
                        
                    if n_pos is not None:
                        print("【侦查结果】找到 n.png！准备翻页。")
                        break
                    
                    print("【侦查结果】两图皆未发现，继续下滑...")
            
            if wp_pos is not None:
                click_x = wp_pos[0] + 190
                click_y = wp_pos[1]
                print(f"\n【操作】点击评价按钮 (wp右移190px): ({click_x}, {click_y})")
                pyautogui.click(click_x, click_y)
                time.sleep(0.5)
                pyautogui.click(click_x, click_y)
                print("【等待】等待评价页面加载...")
                time.sleep(1.5)
                
            elif n_pos is not None:
                page_clicks += 1
                print(f"\n【操作】点击n.png中心 ({page_clicks}/{MAX_PAGE_CLICKS})")
                pyautogui.click(n_pos[0], n_pos[1])
                
                print("【等待】等待3秒...")
                time.sleep(3)     # 改成了 3 秒
                
                print("【操作】上滚1000像素 (第1次)")
                pyautogui.scroll(1000)
                time.sleep(0.5)
                
                print("【操作】上滚1000像素 (第2次)")
                pyautogui.scroll(1000)
                time.sleep(0.5)
                
                print("【翻页完成】返回顶部，重新寻找 wp.png...")
                continue
            
            else:
                print("\n【提示】经过多次下滑，wp.png 和 n.png 均未找到，可能已全部评完")
                break
            
            print(f"\n{'='*60}")
            print(f"【阶段2/5】填写评分 (共5个)")
            print(f"{'='*60}")
            score_count = 0
            
            print(f"【操作】先额外上滑 (拖动滚动条)")
            drag_scroll_up(100)
            
            while score_count < 5:
                if check_exit():
                    print("\n【退出】用户中断，脚本终止")
                    sys.exit(0)
                    
                print(f"\n--- 评分 {score_count+1}/5 ---")
                pos_20 = find_image("20.png", ["top_left"], confidence=0.95, grayscale=True)
                
                if pos_20 is None:
                    print(f"【提示】第{score_count+1}个20.png未找到，尝试上滑...")
                    drag_scroll_up(100)
                    
                    pos_20 = find_image("20.png", ["top_left"], confidence=0.95, grayscale=True)
                    if pos_20 is None:
                        print(f"【错误】第{score_count+1}个20.png仍未找到")
                        print(f"【测试】开始五次测试滚动（间隔2秒）...")
                        for i in range(5):
                            pixels = (i + 1) * 50
                            print(f"【测试】第{i+1}/5次滚动: 拖动滚动条上移 {pixels} 像素")
                            drag_scroll_up(pixels)
                            time.sleep(1.5)
                        result = show_alert("评教失败", f"找不到第{score_count+1}个评分框!\n\n已进行五次测试滚动:\n50px → 100px → 150px → 200px → 250px\n\n选择:\n确定 - 重新开始当前评价\n取消 - 结束脚本")
                        if result == 1:
                            print("【用户选择】重新开始当前评价")
                            pyautogui.hotkey('alt', 'left')
                            time.sleep(2)
                            break
                        else:
                            print("【用户选择】结束脚本")
                            sys.exit(0)
                
                print(f"【操作】点击评分框: {pos_20}")
                pyautogui.click(pos_20[0], pos_20[1])
                time.sleep(0.3)
                pyautogui.click(pos_20[0], pos_20[1])
                print("【输入】输入20")
                pyautogui.typewrite("20")
                time.sleep(0.5)
                
                score_count += 1
                print(f"【完成】第{score_count}个评分完成")
                
                if score_count < 5:
                    print(f"【操作】上滑找下一个")
                    drag_scroll_up(100)
            
            if score_count < 5:
                continue
            
            print(f"\n{'='*60}")
            print(f"【阶段3/5】填写评价内容")
            print(f"{'='*60}")
            k_pos = find_image("k.png", ["top_left"], confidence=0.8, grayscale=True)
            
            if k_pos is not None:
                input_x = k_pos[0]
                input_y = k_pos[1] + 350
                print(f"【操作】点击评价输入框 (k下方350px): ({input_x}, {input_y})")
                pyautogui.click(input_x, input_y)
                time.sleep(0.3)
                pyautogui.click(input_x, input_y)
                time.sleep(0.5)
                print("【输入】粘贴'无'")
                pyperclip.copy("无")
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.5)
            else:
                result = show_alert("评教失败", "找不到评价内容(k.png)!\n\n选择:\n确定 - 跳过继续提交\n取消 - 结束脚本")
                if result != 1:
                    print("【用户选择】结束脚本")
                    sys.exit(0)
                print("【用户选择】跳过评价内容")
            
            print(f"\n{'='*60}")
            print(f"【阶段4/5】查找提交按钮(t.png)")
            print(f"{'='*60}")
            t_pos = find_image("t.png", ["bottom_center"], confidence=0.8, grayscale=True)
            
            if t_pos is not None:
                print(f"【操作】点击t.png: {t_pos}")
                pyautogui.click(t_pos[0], t_pos[1])
                
                print("【等待】等待1秒...")
                time.sleep(1)
                
                print(f"【找图】查找d.png...")
                d_pos = find_image("d.png", ["bottom_center"], confidence=0.8, grayscale=True)
                
                if d_pos is None:
                    print("【提示】第一次未找到d.png，等待2秒后重试...")
                    time.sleep(2)
                    
                    d_pos = find_image("d.png", ["bottom_center"], confidence=0.8, grayscale=True)
                    
                    if d_pos is None:
                        result = show_alert("评教失败", "找不到d.png!\n\n等待2秒后仍未找到。\n\n选择:\n确定 - 手动提交后继续\n取消 - 结束脚本")
                        if result != 1:
                            print("【用户选择】结束脚本")
                            sys.exit(0)
                        input("【提示】请手动点击确定按钮，完成后按回车键继续...")

                if d_pos is not None:
                    print(f"【操作】点击d.png: {d_pos}")
                    pyautogui.click(d_pos[0], d_pos[1])
                    
                print("【等待】等待2秒...")
                time.sleep(2)
            else:
                result = show_alert("评教失败", "找不到t.png!\n\n选择:\n确定 - 手动提交后继续\n取消 - 结束脚本")
                if result != 1:
                    print("【用户选择】结束脚本")
                    sys.exit(0)
                input("【提示】请手动点击提交按钮，完成后按回车键继续...")
            
            total_evaluated += 1
            print(f"\n{'='*60}")
            print(f"【完成】第{total_evaluated}个评价完成!")
            print(f"{'='*60}")
            time.sleep(2)
    
    except KeyboardInterrupt:
        print("\n\n【中断】用户按 Ctrl+C 强制停止脚本")
        sys.exit(0)
    
    print(f"\n{'='*60}")
    print(f"       评价完成!")
    print(f"       共评价 {total_evaluated} 个项目")
    print(f"       翻页次数: {page_clicks}/{MAX_PAGE_CLICKS}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
