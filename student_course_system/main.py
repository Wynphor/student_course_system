# 说明：启用延迟类型注解，提升类型提示在不同 Python 版本下的兼容性。
from __future__ import annotations

# 说明：根据条件选择不同处理分支，控制程序执行路径。
if globals().get("__package__") in {None, ""}:
    # 说明：导入当前模块需要使用的标准库、第三方库或项目内部模块。
    from pathlib import Path
    import sys

    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    # 说明：给 __package__ 赋值，保存当前步骤需要继续使用的数据。
    __package__ = "student_course_system"

# 说明：导入当前模块需要使用的标准库、第三方库或项目内部模块。
from .db import initialize_database
from .ui import ElectiveCourseApp


# 说明：程序入口函数，负责初始化数据库、创建主窗口并启动 Tkinter 事件循环。
def main() -> None:
    # 启动前先检查数据库结构和默认数据，保证第一次运行也能直接进入系统。
    initialize_database()
    # 说明：给 app 赋值，保存当前步骤需要继续使用的数据。
    app = ElectiveCourseApp()
    # 说明：开始异常捕获，避免底层错误直接中断程序。
    try:
        # Tkinter 主循环会一直运行到用户关闭窗口；调试时 Ctrl+C 退出也做一次窗口销毁。
        app.mainloop()
    # 说明：捕获异常并转换为业务提示或测试结果。
    except KeyboardInterrupt:
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        app.destroy()


# 说明：根据条件选择不同处理分支，控制程序执行路径。
if __name__ == "__main__":
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    main()
