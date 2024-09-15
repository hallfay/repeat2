import os
import hashlib
import shutil
import argparse
from collections import defaultdict
from datetime import datetime

def compute_hash(file_path, block_size=65536):
    """计算文件的MD5哈希值"""
    md5 = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(block_size):
                md5.update(chunk)
    except Exception as e:
        print(f"无法读取文件 {file_path}: {e}")
        return None
    return md5.hexdigest()

def find_duplicates(source_dir):
    """遍历文件夹，找到重复文件"""
    hashes = defaultdict(list)
    file_count = 0
    print(f"开始扫描文件夹: {source_dir}")
    for root, dirs, files in os.walk(source_dir):
        for name in files:
            file_count += 1
            if file_count % 100 == 0:
                print(f"已扫描 {file_count} 个文件...")
            file_path = os.path.join(root, name)
            file_hash = compute_hash(file_path)
            if file_hash:
                hashes[file_hash].append(file_path)
    print(f"扫描完成，共处理 {file_count} 个文件。")
    # 过滤出有重复的文件
    duplicates = {hash: paths for hash, paths in hashes.items() if len(paths) > 1}
    return duplicates

def move_duplicates(duplicates, target_dir):
    """移动重复文件到目标文件夹，并生成日志"""
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    log_entries = []
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(target_dir, f"duplicates_log_{timestamp}.txt")
    
    for file_hash, files in duplicates.items():
        # 保留第一个文件，移动其余文件
        original = files[0]
        duplicates_to_move = files[1:]
        log_entries.append(f"原始文件: {original}\n")
        for duplicate in duplicates_to_move:
            try:
                # 保持目录结构相对源文件夹
                relative_path = os.path.relpath(duplicate, start=source_dir)
                new_path = os.path.join(target_dir, relative_path)
                new_dir = os.path.dirname(new_path)
                if not os.path.exists(new_dir):
                    os.makedirs(new_dir)
                shutil.move(duplicate, new_path)
                log_entries.append(f"  重复文件: {duplicate}\n  移动到: {new_path}\n")
                print(f"已移动: {duplicate} --> {new_path}")
            except Exception as e:
                print(f"无法移动文件 {duplicate}: {e}")
                log_entries.append(f"  无法移动文件: {duplicate}. 错误: {e}\n")
        log_entries.append("\n")  # 在每组重复文件之间添加空行

    # 写入日志文件
    try:
        with open(log_file, 'w', encoding='utf-8') as log:
            log.write("\n".join(log_entries))
        print(f"\n日志已生成: {log_file}")
    except Exception as e:
        print(f"无法写入日志文件: {e}")

def main(source_dir, target_dir):
    print(f"开始处理...")
    print(f"源文件夹: {source_dir}")
    print(f"目标文件夹: {target_dir}")
    
    if not os.path.isdir(source_dir):
        print(f"错误：源文件夹不存在: {source_dir}")
        return
    
    duplicates = find_duplicates(source_dir)
    if not duplicates:
        print("没有找到重复文件。")
        return
    total_duplicates = sum(len(files) - 1 for files in duplicates.values())
    print(f"找到 {total_duplicates} 个重复文件。")
    move_duplicates(duplicates, target_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="查找并移动重复文件")
    parser.add_argument("source", help="要扫描的源文件夹路径")
    parser.add_argument("target", help="重复文件的目标文件夹路径")
    
    args = parser.parse_args()
    
    source_dir = os.path.abspath(args.source)
    target_dir = os.path.abspath(args.target)
    
    main(source_dir, target_dir)
