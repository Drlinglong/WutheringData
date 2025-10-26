#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil

# 设置输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def cleanup_files():
    """清理不必要的文件，只保留最终输出"""
    
    print("=== 文件清理开始 ===")
    
    # 1. 保留的最终输出文件
    keep_files = {
        "WutheringDialog/data/dialogs_zh-Hans.complete_final.jsonl": "dialogs_zh-Hans_complete.jsonl",
        "WutheringDialog/data/items.jsonl": "items.jsonl",
        "WutheringDialog/data/weapons.jsonl": "weapons.jsonl",
        "WutheringDialog/data/characters.jsonl": "characters.jsonl",
        "WutheringDialog/data/enemies.jsonl": "enemies.jsonl",
        "WutheringDialog/data/achievements.jsonl": "achievements.jsonl"
    }
    
    # 2. 保留的脚本文件
    keep_scripts = [
        "complete_dialogue_processor.py",
        "auto_scan_categories.py",
        "generate_split_data.py",
        "analyze_final_quality.py",
        "extract_characters.py",
        "extract_items.py",
        "extract_weapons.py",
        "extract_enemies.py",
        "extract_achievements.py",
        "extract_dialog.py"
    ]
    
    # 3. 创建输出目录
    output_dir = "final_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print(f"✅ 创建输出目录: {output_dir}")
    
    # 4. 复制最终文件
    copied_files = []
    for src, dst in keep_files.items():
        if os.path.exists(src):
            dest_path = os.path.join(output_dir, dst)
            shutil.copy2(src, dest_path)
            copied_files.append(dest_path)
            print(f"✅ 复制: {src} -> {dest_path}")
        else:
            print(f"⚠️  文件不存在: {src}")
    
    # 5. 复制脚本文件
    scripts_dir = os.path.join(output_dir, "scripts")
    if not os.path.exists(scripts_dir):
        os.makedirs(scripts_dir)
    
    copied_scripts = []
    for script in keep_scripts:
        if os.path.exists(script):
            dest_path = os.path.join(scripts_dir, script)
            shutil.copy2(script, dest_path)
            copied_scripts.append(dest_path)
            print(f"✅ 复制脚本: {script} -> {dest_path}")
        else:
            print(f"⚠️  脚本不存在: {script}")
    
    # 6. 复制必要的配置文件
    config_dirs = ["ConfigDB", "TextMap"]
    for config_dir in config_dirs:
        if os.path.exists(config_dir):
            dest_dir = os.path.join(output_dir, config_dir)
            if os.path.exists(dest_dir):
                shutil.rmtree(dest_dir)
            shutil.copytree(config_dir, dest_dir)
            print(f"✅ 复制配置: {config_dir}")
    
    print(f"\n=== 清理完成 ===")
    print(f"输出目录: {output_dir}")
    print(f"复制的文件: {len(copied_files)}")
    print(f"复制的脚本: {len(copied_scripts)}")
    
    print("\n保留的文件:")
    for file in copied_files:
        print(f"  - {file}")
    
    print("\n保留的脚本:")
    for script in copied_scripts:
        print(f"  - {script}")

if __name__ == "__main__":
    cleanup_files()
