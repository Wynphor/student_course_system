# 说明：启用延迟类型注解，提升类型提示在不同 Python 版本下的兼容性。
from __future__ import annotations

# 说明：导入当前模块需要使用的标准库、第三方库或项目内部模块。
from contextlib import contextmanager
import sqlite3
# 说明：导入当前模块需要使用的标准库、第三方库或项目内部模块。
from pathlib import Path
from typing import Iterator

# 说明：导入当前模块需要使用的标准库、第三方库或项目内部模块。
from .auth_utils import hash_password


# 说明：设置 BASE_DIR，用于数据库路径、默认数据或 SQL 参数。
BASE_DIR = Path(__file__).resolve().parent
# 说明：设置 DATA_DIR，用于数据库路径、默认数据或 SQL 参数。
DATA_DIR = BASE_DIR / "data"
# 说明：设置 DB_PATH，用于数据库路径、默认数据或 SQL 参数。
DB_PATH = DATA_DIR / "elective_system.db"


# 说明：装饰器用于给下一行函数或属性添加额外行为。
@contextmanager
def get_connection(db_path: str | Path = DB_PATH) -> Iterator[sqlite3.Connection]:
    # 说明：设置 path，用于数据库路径、默认数据或 SQL 参数。
    path = Path(db_path)
    # 说明：设置 path.parent.mkdir(parents，用于数据库路径、默认数据或 SQL 参数。
    path.parent.mkdir(parents=True, exist_ok=True)
    # 说明：创建 SQLite 数据库连接，后续通过该连接读写本地数据库。
    conn = sqlite3.connect(path)
    # 说明：让查询结果支持按字段名读取，减少下标访问带来的歧义。
    conn.row_factory = sqlite3.Row
    # SQLite 默认不强制外键，这里显式开启，学生或课程删除时选课记录才能自动级联清理。
    conn.execute("PRAGMA foreign_keys = ON")
    # 说明：开始异常捕获，避免底层错误直接中断程序。
    try:
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        yield conn
        conn.commit()
    # 说明：捕获异常并转换为业务提示或测试结果。
    except Exception:
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        conn.rollback()
        raise
    # 说明：无论是否发生异常都执行收尾逻辑。
    finally:
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        conn.close()


# 说明：初始化数据库结构，首次运行时自动建表并写入默认数据。
def initialize_database(db_path: str | Path = DB_PATH, seed: bool = True) -> None:
    # 说明：使用上下文管理器自动管理数据库连接、文件或窗口资源。
    with get_connection(db_path) as conn:
        # 所有表都采用 IF NOT EXISTS，便于重复启动程序而不破坏已有数据。
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS courses (
                course_code TEXT PRIMARY KEY,
                course_name TEXT NOT NULL,
                course_type TEXT NOT NULL,
                total_hours INTEGER NOT NULL CHECK(total_hours >= 0),
                lecture_hours INTEGER NOT NULL CHECK(lecture_hours >= 0),
                practice_hours INTEGER NOT NULL CHECK(practice_hours >= 0),
                credits REAL NOT NULL CHECK(credits > 0),
                semester TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                class_name TEXT NOT NULL,
                major TEXT NOT NULL,
                phone TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                course_code TEXT NOT NULL,
                enrolled_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(student_id, course_code),
                FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                FOREIGN KEY(course_code) REFERENCES courses(course_code) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'student')),
                student_id TEXT,
                display_name TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE
            );
            """
        )
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if seed:
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            seed_default_data(conn)


# 说明：写入默认系统设置、示例课程和示例学生，方便首次运行和演示。
def seed_default_data(conn: sqlite3.Connection) -> None:
    # 课程规则放在 settings 表，后续可由界面修改，不在业务代码中写死毕业要求。
    conn.execute(
        """
        INSERT OR IGNORE INTO settings(key, name, value)
        VALUES('min_required_credits', '毕业最低学分要求', '60')
        """
    )
    # 说明：执行 SQL 语句，并通过参数绑定传入变量。
    conn.execute(
        """
        UPDATE settings
        SET name = '毕业最低学分要求'
        WHERE key = 'min_required_credits'
        """
    )

    # 说明：定义默认课程数据，便于系统首次运行后直接演示。
    default_courses = [
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        ("CS101", "Python摸鱼自动化入门", "专业必修", 64, 40, 24, 4.0, "第1学期"),
        ("CS102", "数据结构吧务管理实战", "专业必修", 64, 48, 16, 4.0, "第2学期"),
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        ("CS201", "SQLite楼中楼数据库原理", "专业必修", 56, 40, 16, 3.5, "第3学期"),
        ("CS202", "Web前端炫彩签名档制作", "专业选修", 48, 24, 24, 3.0, "第4学期"),
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        ("AI101", "人工智能复读机导论", "专业选修", 40, 32, 8, 2.5, "第5学期"),
        ("SE101", "软件工程：从挖坑到填坑", "专业必修", 48, 40, 8, 3.0, "第5学期"),
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        ("GE101", "互联网黑话与大学英语", "公共必修", 64, 64, 0, 4.0, "第1学期"),
        ("PE101", "键盘侠体能恢复训练", "公共必修", 32, 8, 24, 1.0, "第2学期"),
    ]
    # 说明：执行 SQL 语句，并通过参数绑定传入变量。
    course_count = conn.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
    # 说明：根据条件选择不同处理分支，控制程序执行路径。
    if course_count == 0:
        # 空库首次运行时写入演示课程，便于直接展示查询和选课流程。
        conn.executemany(
            """
            INSERT INTO courses(
                course_code, course_name, course_type, total_hours,
                lecture_hours, practice_hours, credits, semester
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            default_courses,
        )
    # 说明：根据条件选择不同处理分支，控制程序执行路径。
    else:
        # 说明：执行 SQL 语句，并通过参数绑定传入变量。
        conn.executemany(
            """
            UPDATE courses
            SET course_name = ?,
                course_type = ?,
                total_hours = ?,
                lecture_hours = ?,
                practice_hours = ?,
                credits = ?,
                semester = ?
            WHERE course_code = ?
            """,
            [
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                (name, course_type, total_hours, lecture_hours, practice_hours, credits, semester, code)
                # 说明：循环处理多条记录、多个控件或多个动画粒子。
                for code, name, course_type, total_hours, lecture_hours, practice_hours, credits, semester in default_courses
            ],
        )

    # 说明：定义默认学生数据，用于登录和选课演示。
    default_students = [
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        ("2024001", "小吧主阿明", "贴吧考古2401", "计算机科学与技术", "13800000001"),
        ("2024002", "楼主别跑", "表情包工程2401", "计算机科学与技术", "13800000002"),
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        ("2024003", "潜水员小王", "复读机软件2401", "软件工程", "13800000003"),
    ]
    # 说明：执行 SQL 语句，并通过参数绑定传入变量。
    student_count = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    # 说明：根据条件选择不同处理分支，控制程序执行路径。
    if student_count == 0:
        # 示例学生会同步生成登录账号，学生账号规则为“学号/学号”。
        conn.executemany(
            """
            INSERT INTO students(student_id, name, class_name, major, phone)
            VALUES (?, ?, ?, ?, ?)
            """,
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            default_students,
        )
    # 说明：根据条件选择不同处理分支，控制程序执行路径。
    else:
        # 说明：执行 SQL 语句，并通过参数绑定传入变量。
        conn.executemany(
            """
            UPDATE students
            SET name = ?,
                class_name = ?,
                major = ?,
                phone = ?
            WHERE student_id = ?
            """,
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            [(name, class_name, major, phone, student_id) for student_id, name, class_name, major, phone in default_students],
        )

    # 说明：根据默认学生和管理员规则补齐登录账号。
    seed_default_users(conn)


# 说明：创建默认管理员账号，并为学生表中的每个学生补齐登录账号。
def seed_default_users(conn: sqlite3.Connection) -> None:
    # 默认管理员只在不存在时创建，避免覆盖用户后续修改过的密码。
    conn.execute(
        """
        INSERT OR IGNORE INTO users(username, password_hash, role, student_id, display_name, is_active)
        VALUES (?, ?, 'admin', NULL, ?, 1)
        """,
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        ("admin", hash_password("123456"), "吧务管理员"),
    )
    # 说明：执行 SQL 语句，并通过参数绑定传入变量。
    conn.execute(
        """
        UPDATE users
        SET display_name = '吧务管理员'
        WHERE username = 'admin'
        """
    )

    # 说明：执行 SQL 语句，并通过参数绑定传入变量。
    students = conn.execute("SELECT student_id, name FROM students ORDER BY student_id").fetchall()
    # 说明：循环处理多条记录、多个控件或多个动画粒子。
    for student in students:
        # 说明：设置 student_id，用于数据库路径、默认数据或 SQL 参数。
        student_id = student["student_id"]
        # 为每个学生补齐登录账号；已有账号只同步显示名，不重置密码。
        conn.execute(
            """
            INSERT OR IGNORE INTO users(username, password_hash, role, student_id, display_name, is_active)
            VALUES (?, ?, 'student', ?, ?, 1)
            """,
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            (student_id, hash_password(student_id), student_id, student["name"]),
        )
        # 说明：执行 SQL 语句，并通过参数绑定传入变量。
        conn.execute(
            """
            UPDATE users
            SET display_name = ?
            WHERE username = ? AND role = 'student'
            """,
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            (student["name"], student_id),
        )
