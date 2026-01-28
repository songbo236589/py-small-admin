"""
Celery 组件管理脚本

用于管理 Celery Worker、Beat、Flower 的启动、停止、重启等操作

使用示例:
    # 启动 Worker
    python -m commands.celery_manager worker start
    # 指定启动
    python -m commands.celery_manager worker start -q  email_queues
    # 停止 Worker
    python -m commands.celery_manager worker stop

    # 重启 Worker
    python -m commands.celery_manager worker restart

    # 启动 Beat
    python -m commands.celery_manager beat start

    # 启动 Flower
    python -m commands.celery_manager flower start

    # 启动所有组件
    python -m commands.celery_manager start all

    # 停止所有组件
    python -m commands.celery_manager stop all

    # 查看所有组件状态
    python -m commands.celery_manager status
"""

import argparse
import os
import platform
import signal
import subprocess
import sys
import time
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from Modules.common.libs.config import Config
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保在项目根目录下运行此脚本")
    sys.exit(1)


class CeleryManager:
    """Celery 组件管理器"""

    def __init__(self):
        """初始化管理器"""
        self.config = Config.get("celery")
        self.pid_dir = project_root / "pids"
        self.log_dir = project_root / "logs"
        self.celery_app = "Modules.common.libs.celery.app"

        # 创建必要的目录
        self.pid_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)

    def _get_pid_file(self, component: str) -> Path:
        """
        获取组件的 PID 文件路径

        Args:
            component: 组件名称 (worker/beat/flower)

        Returns:
            Path: PID 文件路径
        """
        return self.pid_dir / f"celery_{component}.pid"

    def _get_log_file(self, component: str) -> Path:
        """
        获取组件的日志文件路径

        Args:
            component: 组件名称 (worker/beat/flower)

        Returns:
            Path: 日志文件路径
        """
        return self.log_dir / f"celery_{component}.log"

    def _is_running(self, component: str) -> bool:
        """
        检查组件是否正在运行

        Args:
            component: 组件名称 (worker/beat/flower)

        Returns:
            bool: 是否正在运行
        """
        pid_file = self._get_pid_file(component)

        if not pid_file.exists():
            return False

        try:
            with open(pid_file) as f:
                pid = int(f.read().strip())

            # 检查进程是否存在
            if platform.system() == "Windows":
                # Windows: 使用 tasklist 命令检查
                result = subprocess.run(
                    ["tasklist", "/FI", f"PID eq {pid}"],
                    capture_output=True,
                    text=True,
                )
                return str(pid) in result.stdout
            else:
                # Linux/Mac: 使用 kill -0 检查
                os.kill(pid, 0)
                return True
        except (ValueError, ProcessLookupError, OSError):
            # PID 文件无效或进程不存在，删除 PID 文件
            pid_file.unlink(missing_ok=True)
            return False

    def _start_process(
        self,
        component: str,
        cmd: list[str],
        background: bool = True,
    ) -> bool:
        """
        启动进程

        Args:
            component: 组件名称
            cmd: 启动命令
            background: 是否后台运行

        Returns:
            bool: 是否启动成功
        """
        pid_file = self._get_pid_file(component)
        log_file = self._get_log_file(component)

        # 检查是否已经运行
        if self._is_running(component):
            print(f"❌ {component.upper()} 已经在运行中")
            return False

        print(f"🚀 正在启动 {component.upper()}...")

        try:
            if background:
                # 后台运行
                if platform.system() == "Windows":
                    # Windows: 使用 DETACHED_PROCESS
                    process = subprocess.Popen(
                        cmd,
                        stdout=open(log_file, "a"),
                        stderr=subprocess.STDOUT,
                        creationflags=subprocess.DETACHED_PROCESS,
                    )
                else:
                    # Linux/Mac: 使用 nohup
                    process = subprocess.Popen(
                        cmd,
                        stdout=open(log_file, "a"),
                        stderr=subprocess.STDOUT,
                        start_new_session=True,
                    )

                # 保存 PID
                with open(pid_file, "w") as f:
                    f.write(str(process.pid))

                print(f"✅ {component.upper()} 启动成功 (PID: {process.pid})")
                print(f"📝 日志文件: {log_file}")
                return True
            else:
                # 前台运行
                process = subprocess.Popen(cmd)
                process.wait()
                return True

        except Exception as e:
            print(f"❌ {component.upper()} 启动失败: {e}")
            return False

    def _stop_process(self, component: str) -> bool:
        """
        停止进程

        Args:
            component: 组件名称

        Returns:
            bool: 是否停止成功
        """
        pid_file = self._get_pid_file(component)

        if not pid_file.exists():
            print(f"❌ {component.upper()} 未运行")
            return False

        try:
            with open(pid_file) as f:
                pid = int(f.read().strip())

            print(f"🛑 正在停止 {component.upper()} (PID: {pid})...")

            # 发送 SIGTERM 信号
            if platform.system() == "Windows":
                # Windows: 使用 taskkill
                subprocess.run(["taskkill", "/PID", str(pid), "/F"], check=True)
            else:
                # Linux/Mac: 使用 kill
                os.kill(pid, signal.SIGTERM)

            # 等待进程结束
            max_wait = 10
            for _ in range(max_wait):
                time.sleep(1)
                if not self._is_running(component):
                    break

            # 如果进程仍在运行，强制终止
            if self._is_running(component):
                print(f"⚠️  {component.upper()} 未响应，强制终止...")
                if platform.system() == "Windows":
                    subprocess.run(["taskkill", "/PID", str(pid), "/F"], check=True)
                else:
                    os.kill(pid, signal.SIGKILL)  # type: ignore

            # 删除 PID 文件
            pid_file.unlink(missing_ok=True)

            print(f"✅ {component.upper()} 已停止")
            return True

        except Exception as e:
            print(f"❌ {component.upper()} 停止失败: {e}")
            return False

    def _build_worker_command(self, queues: str | None = None) -> list[str]:
        """
        构建 Worker 启动命令

        Args:
            queues: 队列名称，多个队列用逗号分隔

        Returns:
            list[str]: 启动命令
        """
        print(self.config.worker_pool)
        cmd = [
            sys.executable,
            "-m",
            "celery",
            "-A",
            self.celery_app,
            "worker",
            f"--pool={self.config.worker_pool}",
            f"--loglevel={self.config.beat_loglevel.lower()}",
            f"--concurrency={self.config.worker_concurrency}",
            f"--prefetch-multiplier={self.config.worker_prefetch_multiplier}",
            f"--max-tasks-per-child={self.config.worker_max_tasks_per_child}",
        ]

        # 添加队列参数
        if queues:
            cmd.extend(["-Q", queues])
        else:
            cmd.extend(["-Q", self.config.task_default_queue])

        # 添加日志格式
        cmd.append(f"--logfile={self._get_log_file('worker')}")

        return cmd

    def _build_beat_command(self) -> list[str]:
        """
        构建 Beat 启动命令

        Returns:
            list[str]: 启动命令
        """
        cmd = [
            sys.executable,
            "-m",
            "celery",
            "-A",
            self.celery_app,
            "beat",
            f"--loglevel={self.config.beat_loglevel.lower()}",
            f"--schedule={self.config.beat_schedule_filename}",
            f"--max-interval={self.config.beat_max_loop_interval}",
            f"--logfile={self._get_log_file('beat')}",
        ]

        return cmd

    def _build_flower_command(self) -> list[str]:
        """
        构建 Flower 启动命令

        Returns:
            list[str]: 启动命令
        """
        cmd = [
            sys.executable,
            "-m",
            "celery",
            "-A",
            self.celery_app,
            "flower",
            f"--port={self.config.flower['port']}",
            f"--address={self.config.flower['host']}",
            f"--logfile={self._get_log_file('flower')}",
        ]

        # 添加基本认证
        if self.config.flower.get("basic_auth"):
            cmd.append(f"--basic_auth={self.config.flower['basic_auth']}")

        # 添加 Broker API
        if self.config.flower.get("broker_api"):
            cmd.append(f"--broker_api={self.config.flower['broker_api']}")

        return cmd

    # ========== Worker 操作 ==========

    def start_worker(self, queues: str | None = None) -> bool:
        """
        启动 Worker

        Args:
            queues: 队列名称，多个队列用逗号分隔

        Returns:
            bool: 是否启动成功
        """
        cmd = self._build_worker_command(queues)
        return self._start_process("worker", cmd)

    def stop_worker(self) -> bool:
        """
        停止 Worker

        Returns:
            bool: 是否停止成功
        """
        return self._stop_process("worker")

    def restart_worker(self, queues: str | None = None) -> bool:
        """
        重启 Worker

        Args:
            queues: 队列名称，多个队列用逗号分隔

        Returns:
            bool: 是否重启成功
        """
        print("🔄 正在重启 Worker...")
        self.stop_worker()
        time.sleep(2)
        return self.start_worker(queues)

    # ========== Beat 操作 ==========

    def start_beat(self) -> bool:
        """
        启动 Beat

        Returns:
            bool: 是否启动成功
        """
        cmd = self._build_beat_command()
        return self._start_process("beat", cmd)

    def stop_beat(self) -> bool:
        """
        停止 Beat

        Returns:
            bool: 是否停止成功
        """
        return self._stop_process("beat")

    def restart_beat(self) -> bool:
        """
        重启 Beat

        Returns:
            bool: 是否重启成功
        """
        print("🔄 正在重启 Beat...")
        self.stop_beat()
        time.sleep(2)
        return self.start_beat()

    # ========== Flower 操作 ==========

    def start_flower(self) -> bool:
        """
        启动 Flower

        Returns:
            bool: 是否启动成功
        """
        cmd = self._build_flower_command()
        return self._start_process("flower", cmd)

    def stop_flower(self) -> bool:
        """
        停止 Flower

        Returns:
            bool: 是否停止成功
        """
        return self._stop_process("flower")

    def restart_flower(self) -> bool:
        """
        重启 Flower

        Returns:
            bool: 是否重启成功
        """
        print("🔄 正在重启 Flower...")
        self.stop_flower()
        time.sleep(2)
        return self.start_flower()

    # ========== 批量操作 ==========

    def start_all(self) -> None:
        """启动所有组件"""
        print("\n🚀 启动所有 Celery 组件\n")
        print("=" * 50)

        self.start_worker()
        time.sleep(1)

        self.start_beat()
        time.sleep(1)

        self.start_flower()

        print("=" * 50)
        print("\n✅ 所有组件启动完成！\n")
        self.status()

    def stop_all(self) -> None:
        """停止所有组件"""
        print("\n🛑 停止所有 Celery 组件\n")
        print("=" * 50)

        self.stop_flower()
        time.sleep(1)

        self.stop_beat()
        time.sleep(1)

        self.stop_worker()

        print("=" * 50)
        print("\n✅ 所有组件已停止！\n")

    def restart_all(self) -> None:
        """重启所有组件"""
        print("\n🔄 重启所有 Celery 组件\n")
        self.stop_all()
        time.sleep(3)
        self.start_all()

    # ========== 状态查看 ==========

    def status(self) -> None:
        """查看所有组件状态"""
        print("\n📊 Celery 组件状态\n")
        print("=" * 50)

        components = ["worker", "beat", "flower"]

        for component in components:
            pid_file = self._get_pid_file(component)
            log_file = self._get_log_file(component)

            if self._is_running(component):
                with open(pid_file) as f:
                    pid = f.read().strip()
                print(f"✅ {component.upper():10} - 运行中 (PID: {pid})")
            else:
                print(f"❌ {component.upper():10} - 未运行")

            print(f"   日志: {log_file}")

        print("=" * 50)

        # 显示访问信息
        if self._is_running("flower"):
            print("\n🌸 Flower 监控界面:")
            print(
                f"   地址: http://{self.config.flower['host']}:{self.config.flower['port']}"
            )
            if self.config.flower.get("basic_auth"):
                print(f"   认证: {self.config.flower['basic_auth']}")
            print()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Celery 组件管理脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python -m commands.celery_manager worker start
  python -m commands.celery_manager worker stop
  python -m commands.celery_manager worker restart
  python -m commands.celery_manager beat start
  python -m commands.celery_manager flower start
  python -m commands.celery_manager start all
  python -m commands.celery_manager stop all
  python -m commands.celery_manager status
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="操作命令")

    # Worker 子命令
    worker_parser = subparsers.add_parser("worker", help="Worker 操作")
    worker_subparsers = worker_parser.add_subparsers(dest="action")

    worker_start = worker_subparsers.add_parser("start", help="启动 Worker")
    worker_start.add_argument(
        "-q",
        "--queues",
        help="队列名称，多个队列用逗号分隔",
        default=None,
    )

    worker_subparsers.add_parser("stop", help="停止 Worker")
    worker_restart = worker_subparsers.add_parser("restart", help="重启 Worker")
    worker_restart.add_argument(
        "-q",
        "--queues",
        help="队列名称，多个队列用逗号分隔",
        default=None,
    )

    # Beat 子命令
    beat_parser = subparsers.add_parser("beat", help="Beat 操作")
    beat_subparsers = beat_parser.add_subparsers(dest="action")

    beat_subparsers.add_parser("start", help="启动 Beat")
    beat_subparsers.add_parser("stop", help="停止 Beat")
    beat_subparsers.add_parser("restart", help="重启 Beat")

    # Flower 子命令
    flower_parser = subparsers.add_parser("flower", help="Flower 操作")
    flower_subparsers = flower_parser.add_subparsers(dest="action")

    flower_subparsers.add_parser("start", help="启动 Flower")
    flower_subparsers.add_parser("stop", help="停止 Flower")
    flower_subparsers.add_parser("restart", help="重启 Flower")

    # 批量操作
    start_parser = subparsers.add_parser("start", help="启动组件")
    start_parser.add_argument("component", choices=["all"], help="启动所有组件")

    stop_parser = subparsers.add_parser("stop", help="停止组件")
    stop_parser.add_argument("component", choices=["all"], help="停止所有组件")

    restart_parser = subparsers.add_parser("restart", help="重启组件")
    restart_parser.add_argument("component", choices=["all"], help="重启所有组件")

    # 状态查看
    subparsers.add_parser("status", help="查看组件状态")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    manager = CeleryManager()

    # Worker 操作
    if args.command == "worker":
        if args.action == "start":
            manager.start_worker(args.queues)
        elif args.action == "stop":
            manager.stop_worker()
        elif args.action == "restart":
            manager.restart_worker(args.queues)

    # Beat 操作
    elif args.command == "beat":
        if args.action == "start":
            manager.start_beat()
        elif args.action == "stop":
            manager.stop_beat()
        elif args.action == "restart":
            manager.restart_beat()

    # Flower 操作
    elif args.command == "flower":
        if args.action == "start":
            manager.start_flower()
        elif args.action == "stop":
            manager.stop_flower()
        elif args.action == "restart":
            manager.restart_flower()

    # 批量操作
    elif args.command == "start":
        manager.start_all()
    elif args.command == "stop":
        manager.stop_all()
    elif args.command == "restart":
        manager.restart_all()

    # 状态查看
    elif args.command == "status":
        manager.status()


if __name__ == "__main__":
    main()
