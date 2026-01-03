import asyncio
import os
import hashlib
from .base import BaseSensor

class FileSensor(BaseSensor):
    """
    文件变更传感器 (File Watcher Sensor)
    智能监听特定目录的变更，建立“内容级开发意识”。
    """
    def __init__(self, bus, watch_path: str, interval: int = 5):
        super().__init__("FileSensor", bus)
        self.watch_path = watch_path
        self.interval = interval
        self.last_mtimes = {}
        self.last_hashes = {} # 内容级校验 (Content-level check)

    def _compute_hash(self, fpath: str) -> str:
        """计算文件的 SHA256 哈希值 (Compute content hash)"""
        try:
            # 性能优化：大于 5MB 的文件跳过哈希，仅记录时间戳
            if os.path.getsize(fpath) > 5 * 1024 * 1024:
                return "large_file_skip_hash"
                
            hash_sha256 = hashlib.sha256()
            with open(fpath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except:
            return None

    async def _run(self):
        if not os.path.exists(self.watch_path):
            print(f"[感知器] 错误: 路径 {self.watch_path} 不存在，停止监听。")
            return

        initial_scan_done = False
        import sys
        import time
        
        while self.running:
            try:
                # 强制排除项
                exclude_dirs = {
                    'logs', '.git', '__pycache__', '.venv', 'dist', 'build', 
                    'instance', 'memory', 'node_modules', '.idea', '.vscode', 'tmp'
                }
                exclude_files = {'knowledge.json', '.DS_Store', 'uv.lock', '.janus_history'}
                
                current_files = []
                now = time.time()
                
                for root, dirs, files in os.walk(self.watch_path):
                    dirs[:] = [d for d in dirs if d not in exclude_dirs]
                    
                    for f in files:
                        if f in exclude_files: continue
                        if f.endswith(('.py', '.js', '.md', '.json', '.html', '.css', '.sh')):
                            current_files.append(os.path.join(root, f))
                
                for fpath in current_files:
                    try:
                        mtime = os.path.getmtime(fpath)
                    except (OSError, FileNotFoundError): continue
                        
                    rel_path = os.path.relpath(fpath, self.watch_path)
                    
                    # [AI-SAFEGUARD]: 内容感知双检逻辑锁定
                    # 严禁改为纯 mtime 检查。mtime 在某些环境下（如 Git 切换）不可靠。
                    # 必须保持 (mtime 触发 -> 哈希校验 -> 最终确认) 的双重过滤路径。
                    changed_mtime = fpath not in self.last_mtimes or mtime > self.last_mtimes[fpath]
                    
                    if changed_mtime:
                        current_hash = self._compute_hash(fpath)
                        last_hash = self.last_hashes.get(fpath)
                        
                        # 内容确实发生了改变 (Actual content change)
                        if last_hash and current_hash != last_hash:
                            await self.bus.emit(
                                source="visual",
                                data=f"检测到活动文件变更: {rel_path}",
                                importance=0.4
                            )
                        # 新文件创建 (New file creation)
                        elif initial_scan_done and not last_hash:
                            await self.bus.emit(
                                source="visual",
                                data=f"检测到新文件创建: {rel_path}",
                                importance=0.5
                            )
                        # 初始扫描的活跃文件 (Initial scan activity)
                        # 静默启动：初始扫描时不触发感知事件，避免启动时阻塞
                        elif not initial_scan_done and now - mtime < 120:
                            pass  # 静默记录，不触发感知事件
                        
                        # 更新缓存
                        self.last_hashes[fpath] = current_hash
                        self.last_mtimes[fpath] = mtime
                
                initial_scan_done = True
                
            except Exception as e:
                print(f"[感知器] FileSensor 运行时严重异常: {type(e).__name__}: {str(e)}")
                sys.stdout.flush()
            
            await asyncio.sleep(self.interval)

