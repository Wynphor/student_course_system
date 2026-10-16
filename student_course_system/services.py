# 说明：启用延迟类型注解，提升类型提示在不同 Python 版本下的兼容性。
from __future__ import annotations

# 说明：导入当前模块需要使用的标准库、第三方库或项目内部模块。
import csv
from pathlib import Path
# 说明：导入当前模块需要使用的标准库、第三方库或项目内部模块。
from typing import Any

from .auth_utils import hash_password, verify_password
# 说明：导入当前模块需要使用的标准库、第三方库或项目内部模块。
from .db import DB_PATH, get_connection


# 说明：业务异常类，用于把输入错误和数据库约束错误转换为用户提示。
class ServiceError(Exception):
    # 说明：文档字符串，用于说明当前模块、类或函数的用途。
    """Raised when user input or a database operation is invalid."""


# 说明：统一清理文本输入，并检查必填字段不能为空。
def _clean_text(value: Any, field_name: str) -> str:
    # 说明：计算或保存 text，作为后续业务校验、数据库操作或返回结果使用。
    text = str(value).strip()
    # 说明：根据条件选择不同处理分支，控制程序执行路径。
    if not text:
        # 说明：主动抛出业务异常，交由上层界面或测试处理。
        raise ServiceError(f"{field_name}不能为空")
    # 说明：返回处理结果，供调用方继续使用。
    return text


# 说明：把输入转换为整数，并校验学时等数值不能小于零。
def _to_int(value: Any, field_name: str) -> int:
    # 说明：开始异常捕获，避免底层错误直接中断程序。
    try:
        # 说明：计算或保存 number，作为后续业务校验、数据库操作或返回结果使用。
        number = int(str(value).strip())
    # 说明：捕获异常并转换为业务提示或测试结果。
    except ValueError as exc:
        # 说明：主动抛出业务异常，交由上层界面或测试处理。
        raise ServiceError(f"{field_name}必须是整数") from exc
    # 说明：根据条件选择不同处理分支，控制程序执行路径。
    if number < 0:
        # 说明：主动抛出业务异常，交由上层界面或测试处理。
        raise ServiceError(f"{field_name}不能小于0")
    # 说明：返回处理结果，供调用方继续使用。
    return number


# 说明：把输入转换为正浮点数，用于学分和最低毕业学分等字段。
def _to_positive_float(value: Any, field_name: str) -> float:
    # 说明：开始异常捕获，避免底层错误直接中断程序。
    try:
        # 说明：计算或保存 number，作为后续业务校验、数据库操作或返回结果使用。
        number = float(str(value).strip())
    # 说明：捕获异常并转换为业务提示或测试结果。
    except ValueError as exc:
        # 说明：主动抛出业务异常，交由上层界面或测试处理。
        raise ServiceError(f"{field_name}必须是数字") from exc
    # 说明：根据条件选择不同处理分支，控制程序执行路径。
    if number <= 0:
        # 说明：主动抛出业务异常，交由上层界面或测试处理。
        raise ServiceError(f"{field_name}必须大于0")
    # 说明：返回处理结果，供调用方继续使用。
    return number


# 说明：把字典列表导出为 CSV 文件，供课程信息和选课信息导出功能复用。
def _write_csv(path: str | Path, headers: list[str], rows: list[dict[str, Any]]) -> None:
    # 说明：计算或保存 target，作为后续业务校验、数据库操作或返回结果使用。
    target = Path(path)
    # 说明：创建导出目录，确保保存 CSV 时目标文件夹存在。
    target.parent.mkdir(parents=True, exist_ok=True)
    # utf-8-sig 方便 Windows 版 Excel 直接打开中文 CSV。
    with target.open("w", newline="", encoding="utf-8-sig") as fp:
        # 说明：创建按字段名写入的 CSV 写入器。
        writer = csv.DictWriter(fp, fieldnames=headers)
        # 说明：写入 CSV 表头，便于导出文件查看。
        writer.writeheader()
        # 说明：循环处理多条记录、多个控件或多个动画粒子。
        for row in rows:
            # 说明：写入一行 CSV 数据，没有的字段用空字符串填充。
            writer.writerow({key: row.get(key, "") for key in headers})


# 说明：认证服务类，负责登录、密码修改和学生账号维护。
class AuthService:
    # 说明：文档字符串，用于说明当前模块、类或函数的用途。
    """处理登录、密码修改和学生账号维护。"""

    # 说明：定义 __init__ 函数，封装当前模块的一段处理逻辑。
    def __init__(self, db_path: str | Path = DB_PATH):
        # 说明：计算或保存 self.db_path，作为后续业务校验、数据库操作或返回结果使用。
        self.db_path = db_path

    # 说明：验证账号、密码和启用状态，登录成功后返回当前用户身份信息。
    def login(self, username: Any, password: Any) -> dict[str, Any]:
        # 说明：调用文本清理函数，统一处理必填字段。
        username_text = _clean_text(username, "用户名")
        password_text = _clean_text(password, "密码")
        # 说明：使用上下文管理器自动管理数据库连接、文件或窗口资源。
        with get_connection(self.db_path) as conn:
            # 说明：执行 SQL 语句，并通过参数绑定传入变量。
            row = conn.execute(
                """
                SELECT username, password_hash, role, student_id, display_name, is_active
                FROM users
                WHERE username = ?
                """,
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                (username_text,),
            ).fetchone()
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if row is None or int(row["is_active"]) != 1:
            # 说明：主动抛出业务异常，交由上层界面或测试处理。
            raise ServiceError("用户名或密码错误")
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if not verify_password(password_text, row["password_hash"]):
            # 说明：主动抛出业务异常，交由上层界面或测试处理。
            raise ServiceError("用户名或密码错误")
        # 说明：返回处理结果，供调用方继续使用。
        return {
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            "username": row["username"],
            "role": row["role"],
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            "student_id": row["student_id"],
            "display_name": row["display_name"],
        }

    # 说明：根据用户名查询用户信息，用于测试和账号状态检查。
    def get_user(self, username: str) -> dict[str, Any] | None:
        # 说明：使用上下文管理器自动管理数据库连接、文件或窗口资源。
        with get_connection(self.db_path) as conn:
            # 说明：执行 SQL 语句，并通过参数绑定传入变量。
            row = conn.execute(
                """
                SELECT username, role, student_id, display_name, is_active, created_at
                FROM users
                WHERE username = ?
                """,
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                (username,),
            ).fetchone()
        # 说明：返回处理结果，供调用方继续使用。
        return dict(row) if row else None

    # 说明：管理员把指定学生账号密码重置为学号。
    def reset_student_password(self, student_id: Any) -> None:
        # 说明：调用文本清理函数，统一处理必填字段。
        student_id_text = _clean_text(student_id, "学号")
        # 说明：使用上下文管理器自动管理数据库连接、文件或窗口资源。
        with get_connection(self.db_path) as conn:
            # 说明：执行 SQL 语句，并通过参数绑定传入变量。
            student = conn.execute(
                # 说明：计算或保存 "SELECT student_id, name FROM students WHERE student_id，作为后续业务校验、数据库操作或返回结果使用。
                "SELECT student_id, name FROM students WHERE student_id = ?",
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                (student_id_text,),
            ).fetchone()
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            if student is None:
                # 说明：主动抛出业务异常，交由上层界面或测试处理。
                raise ServiceError("未找到该学生")
            # 说明：执行 SQL 语句，并通过参数绑定传入变量。
            conn.execute(
                """
                INSERT INTO users(username, password_hash, role, student_id, display_name, is_active)
                VALUES (?, ?, 'student', ?, ?, 1)
                ON CONFLICT(username) DO UPDATE SET
                    password_hash = excluded.password_hash,
                    student_id = excluded.student_id,
                    display_name = excluded.display_name,
                    is_active = 1
                """,
                (
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    student_id_text,
                    hash_password(student_id_text),
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    student_id_text,
                    student["name"],
                ),
            )

    # 说明：学生自助修改密码，包含原密码、新密码长度和确认密码校验。
    def change_password(self, username: Any, old_password: Any, new_password: Any, confirm_password: Any) -> None:
        # 说明：调用文本清理函数，统一处理必填字段。
        username_text = _clean_text(username, "用户名")
        old_password_text = _clean_text(old_password, "原密码")
        # 说明：调用文本清理函数，统一处理必填字段。
        new_password_text = _clean_text(new_password, "新密码")
        confirm_password_text = _clean_text(confirm_password, "确认密码")
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if new_password_text != confirm_password_text:
            # 说明：主动抛出业务异常，交由上层界面或测试处理。
            raise ServiceError("两次输入的新密码不一致")
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if len(new_password_text) < 6:
            # 说明：主动抛出业务异常，交由上层界面或测试处理。
            raise ServiceError("新密码长度不能少于6位")
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if old_password_text == new_password_text:
            # 说明：主动抛出业务异常，交由上层界面或测试处理。
            raise ServiceError("新密码不能与原密码相同")

        # 说明：使用上下文管理器自动管理数据库连接、文件或窗口资源。
        with get_connection(self.db_path) as conn:
            # 说明：执行 SQL 语句，并通过参数绑定传入变量。
            row = conn.execute(
                """
                SELECT username, password_hash, is_active
                FROM users
                WHERE username = ?
                """,
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                (username_text,),
            ).fetchone()
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            if row is None or int(row["is_active"]) != 1:
                # 说明：主动抛出业务异常，交由上层界面或测试处理。
                raise ServiceError("账号不存在或已停用")
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            if not verify_password(old_password_text, row["password_hash"]):
                # 说明：主动抛出业务异常，交由上层界面或测试处理。
                raise ServiceError("原密码错误")
            # 说明：执行 SQL 语句，并通过参数绑定传入变量。
            conn.execute(
                # 说明：计算或保存 "UPDATE users SET password_hash，作为后续业务校验、数据库操作或返回结果使用。
                "UPDATE users SET password_hash = ? WHERE username = ?",
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                (hash_password(new_password_text), username_text),
            )

    # 说明：查询系统用户列表，便于调试或扩展账号管理功能。
    def list_users(self) -> list[dict[str, Any]]:
        # 说明：使用上下文管理器自动管理数据库连接、文件或窗口资源。
        with get_connection(self.db_path) as conn:
            # 说明：执行 SQL 语句，并通过参数绑定传入变量。
            rows = conn.execute(
                """
                SELECT username, role, student_id, display_name, is_active, created_at
                FROM users
                ORDER BY role, username
                """
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            ).fetchall()
        # 说明：返回处理结果，供调用方继续使用。
        return [dict(row) for row in rows]


# 说明：系统设置服务类，负责最低毕业学分等规则配置。
class SettingsService:
    # 说明：文档字符串，用于说明当前模块、类或函数的用途。
    """读取和维护系统规则配置。"""

    # 说明：定义 __init__ 函数，封装当前模块的一段处理逻辑。
    def __init__(self, db_path: str | Path = DB_PATH):
        # 说明：计算或保存 self.db_path，作为后续业务校验、数据库操作或返回结果使用。
        self.db_path = db_path

    # 说明：从 settings 表读取最低毕业学分要求。
    def get_min_required_credits(self) -> float:
        # 说明：使用上下文管理器自动管理数据库连接、文件或窗口资源。
        with get_connection(self.db_path) as conn:
            # 说明：执行 SQL 语句，并通过参数绑定传入变量。
            row = conn.execute(
                # 说明：计算或保存 "SELECT value FROM settings WHERE key，作为后续业务校验、数据库操作或返回结果使用。
                "SELECT value FROM settings WHERE key = 'min_required_credits'"
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            ).fetchone()
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if row is None:
            # 说明：主动抛出业务异常，交由上层界面或测试处理。
            raise ServiceError("系统未配置最低毕业学分")
        # 说明：返回处理结果，供调用方继续使用。
        return float(row["value"])

    # 说明：保存管理员设置的最低毕业学分要求。
    def set_min_required_credits(self, value: Any) -> None:
        # 说明：调用正数转换函数，校验学分或最低学分输入。
        credits = _to_positive_float(value, "最低毕业学分")
        # 说明：使用上下文管理器自动管理数据库连接、文件或窗口资源。
        with get_connection(self.db_path) as conn:
            # 说明：执行 SQL 语句，并通过参数绑定传入变量。
            conn.execute(
                """
                INSERT INTO settings(key, name, value, updated_at)
                VALUES('min_required_credits', '最低毕业学分', ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = CURRENT_TIMESTAMP
                """,
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                (str(credits),),
            )


# 说明：课程服务类，负责课程增删改查、查询筛选和导出。
class CourseService:
    # 说明：文档字符串，用于说明当前模块、类或函数的用途。
    """课程信息的增删改查、筛选和导出。"""

    # 说明：定义允许排序的字段白名单，避免非法字段拼接进 SQL。
    allowed_sort_fields = {
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        "course_code",
        "course_name",
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        "course_type",
        "total_hours",
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        "lecture_hours",
        "practice_hours",
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        "credits",
        "semester",
    }

    # 说明：定义 __init__ 函数，封装当前模块的一段处理逻辑。
    def __init__(self, db_path: str | Path = DB_PATH):
        # 说明：计算或保存 self.db_path，作为后续业务校验、数据库操作或返回结果使用。
        self.db_path = db_path

    # 说明：按关键字、课程性质、学期和学分范围查询课程列表。
    def list_courses(
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self,
        # 说明：计算或保存 filters: dict[str, Any] | None，作为后续业务校验、数据库操作或返回结果使用。
        filters: dict[str, Any] | None = None,
        # 说明：计算或保存 sort_by: str，作为后续业务校验、数据库操作或返回结果使用。
        sort_by: str = "course_code",
        # 说明：计算或保存 sort_dir: str，作为后续业务校验、数据库操作或返回结果使用。
        sort_dir: str = "ASC",
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    ) -> list[dict[str, Any]]:
        # 说明：计算或保存 filters，作为后续业务校验、数据库操作或返回结果使用。
        filters = filters or {}
        # 排序字段只允许白名单中的数据库列，避免拼接 SQL 时引入非法字段。
        sort_by = sort_by if sort_by in self.allowed_sort_fields else "course_code"
        # 说明：计算或保存 sort_dir，作为后续业务校验、数据库操作或返回结果使用。
        sort_dir = "DESC" if str(sort_dir).upper() == "DESC" else "ASC"

        # 说明：计算或保存 where: list[str]，作为后续业务校验、数据库操作或返回结果使用。
        where: list[str] = []
        # 说明：计算或保存 params: list[Any]，作为后续业务校验、数据库操作或返回结果使用。
        params: list[Any] = []

        # 说明：计算或保存 keyword，作为后续业务校验、数据库操作或返回结果使用。
        keyword = str(filters.get("keyword", "")).strip()
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if keyword:
            # 说明：根据查询条件追加 SQL WHERE 子句片段。
            where.append("(course_code LIKE ? OR course_name LIKE ?)")
            # 说明：计算或保存 like，作为后续业务校验、数据库操作或返回结果使用。
            like = f"%{keyword}%"
            # 说明：一次性追加多个 SQL 查询参数。
            params.extend([like, like])

        # 说明：计算或保存 course_type，作为后续业务校验、数据库操作或返回结果使用。
        course_type = str(filters.get("course_type", "")).strip()
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if course_type:
            # 说明：根据查询条件追加 SQL WHERE 子句片段。
            where.append("course_type = ?")
            # 说明：保存 SQL 占位符对应的参数值。
            params.append(course_type)

        # 说明：计算或保存 semester，作为后续业务校验、数据库操作或返回结果使用。
        semester = str(filters.get("semester", "")).strip()
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if semester:
            # 说明：根据查询条件追加 SQL WHERE 子句片段。
            where.append("semester = ?")
            # 说明：保存 SQL 占位符对应的参数值。
            params.append(semester)

        # 说明：计算或保存 min_credits，作为后续业务校验、数据库操作或返回结果使用。
        min_credits = str(filters.get("min_credits", "")).strip()
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if min_credits:
            # 说明：根据查询条件追加 SQL WHERE 子句片段。
            where.append("credits >= ?")
            # 说明：调用正数转换函数，校验学分或最低学分输入。
            params.append(_to_positive_float(min_credits, "最低学分"))

        # 说明：计算或保存 max_credits，作为后续业务校验、数据库操作或返回结果使用。
        max_credits = str(filters.get("max_credits", "")).strip()
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if max_credits:
            # 说明：根据查询条件追加 SQL WHERE 子句片段。
            where.append("credits <= ?")
            # 说明：调用正数转换函数，校验学分或最低学分输入。
            params.append(_to_positive_float(max_credits, "最高学分"))

        # 说明：计算或保存 sql，作为后续业务校验、数据库操作或返回结果使用。
        sql = "SELECT * FROM courses"
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if where:
            # 说明：计算或保存 sql +，作为后续业务校验、数据库操作或返回结果使用。
            sql += " WHERE " + " AND ".join(where)
        sql += f" ORDER BY {sort_by} {sort_dir}"

        # 说明：使用上下文管理器自动管理数据库连接、文件或窗口资源。
        with get_connection(self.db_path) as conn:
            # 说明：执行 SQL 语句，并通过参数绑定传入变量。
            return [dict(row) for row in conn.execute(sql, params).fetchall()]

    # 说明：根据课程编号查询单门课程详情。
    def get_course(self, course_code: str) -> dict[str, Any] | None:
        # 说明：使用上下文管理器自动管理数据库连接、文件或窗口资源。
        with get_connection(self.db_path) as conn:
            # 说明：执行 SQL 语句，并通过参数绑定传入变量。
            row = conn.execute(
                # 说明：计算或保存 "SELECT * FROM courses WHERE course_code，作为后续业务校验、数据库操作或返回结果使用。
                "SELECT * FROM courses WHERE course_code = ?",
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                (course_code,),
            ).fetchone()
        # 说明：返回处理结果，供调用方继续使用。
        return dict(row) if row else None

    # 说明：新增课程信息，并处理课程编号重复等错误。
    def create_course(self, data: dict[str, Any]) -> None:
        # 说明：计算或保存 payload，作为后续业务校验、数据库操作或返回结果使用。
        payload = self._validate_course(data)
        # 说明：开始异常捕获，避免底层错误直接中断程序。
        try:
            # 说明：使用上下文管理器自动管理数据库连接、文件或窗口资源。
            with get_connection(self.db_path) as conn:
                # 说明：执行 SQL 语句，并通过参数绑定传入变量。
                conn.execute(
                    """
                    INSERT INTO courses(
                        course_code, course_name, course_type, total_hours,
                        lecture_hours, practice_hours, credits, semester
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                        payload["course_code"],
                        payload["course_name"],
                        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                        payload["course_type"],
                        payload["total_hours"],
                        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                        payload["lecture_hours"],
                        payload["practice_hours"],
                        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                        payload["credits"],
                        payload["semester"],
                    ),
                )
        # 说明：捕获异常并转换为业务提示或测试结果。
        except Exception as exc:
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            if "UNIQUE" in str(exc) or "PRIMARY" in str(exc):
                # 说明：主动抛出业务异常，交由上层界面或测试处理。
                raise ServiceError("课程编号已存在") from exc
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            raise

    # 说明：更新指定课程的信息。
    def update_course(self, course_code: str, data: dict[str, Any]) -> None:
        # 说明：计算或保存 payload，作为后续业务校验、数据库操作或返回结果使用。
        payload = self._validate_course({**data, "course_code": course_code})
        # 说明：使用上下文管理器自动管理数据库连接、文件或窗口资源。
        with get_connection(self.db_path) as conn:
            # 说明：执行 SQL 语句，并通过参数绑定传入变量。
            result = conn.execute(
                """
                UPDATE courses SET
                    course_name = ?,
                    course_type = ?,
                    total_hours = ?,
                    lecture_hours = ?,
                    practice_hours = ?,
                    credits = ?,
                    semester = ?
                WHERE course_code = ?
                """,
                (
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    payload["course_name"],
                    payload["course_type"],
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    payload["total_hours"],
                    payload["lecture_hours"],
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    payload["practice_hours"],
                    payload["credits"],
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    payload["semester"],
                    course_code,
                ),
            )
        # 说明：根据受影响行数判断更新或删除操作是否真正命中数据。
        if result.rowcount == 0:
            # 说明：主动抛出业务异常，交由上层界面或测试处理。
            raise ServiceError("未找到要修改的课程")

    # 说明：删除单门课程，关联选课记录通过外键级联删除。
    def delete_course(self, course_code: str) -> None:
        # 说明：使用上下文管理器自动管理数据库连接、文件或窗口资源。
        with get_connection(self.db_path) as conn:
            # 说明：执行 SQL 语句，并通过参数绑定传入变量。
            result = conn.execute(
                # 说明：计算或保存 "DELETE FROM courses WHERE course_code，作为后续业务校验、数据库操作或返回结果使用。
                "DELETE FROM courses WHERE course_code = ?",
                # 说明：调用文本清理函数，统一处理必填字段。
                (_clean_text(course_code, "课程编号"),),
            )
        # 说明：根据受影响行数判断更新或删除操作是否真正命中数据。
        if result.rowcount == 0:
            # 说明：主动抛出业务异常，交由上层界面或测试处理。
            raise ServiceError("未找到要删除的课程")

    # 说明：批量删除勾选的课程。
    def delete_courses(self, course_codes: list[str]) -> int:
        # 说明：调用文本清理函数，统一处理必填字段。
        cleaned = [_clean_text(code, "课程编号") for code in course_codes]
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if not cleaned:
            # 说明：主动抛出业务异常，交由上层界面或测试处理。
            raise ServiceError("请先选择要处理的课程")
        # 批量删除使用占位符生成 IN 条件，既支持多选，也保留参数化查询。
        placeholders = ",".join("?" for _ in cleaned)
        # 说明：使用上下文管理器自动管理数据库连接、文件或窗口资源。
        with get_connection(self.db_path) as conn:
            # 说明：执行 SQL 语句，并通过参数绑定传入变量。
            result = conn.execute(
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                f"DELETE FROM courses WHERE course_code IN ({placeholders})",
                cleaned,
            )
        # 说明：根据受影响行数判断更新或删除操作是否真正命中数据。
        if result.rowcount == 0:
            # 说明：主动抛出业务异常，交由上层界面或测试处理。
            raise ServiceError("未找到要删除的课程")
        # 说明：根据受影响行数判断更新或删除操作是否真正命中数据。
        return result.rowcount

    # 说明：查询课程性质或学期的去重值，供下拉筛选框使用。
    def distinct_values(self, field: str) -> list[str]:
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if field not in {"course_type", "semester"}:
            # 说明：主动抛出业务异常，交由上层界面或测试处理。
            raise ServiceError("不支持的字段")
        # 说明：使用上下文管理器自动管理数据库连接、文件或窗口资源。
        with get_connection(self.db_path) as conn:
            # 说明：执行 SQL 语句，并通过参数绑定传入变量。
            rows = conn.execute(
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                f"SELECT DISTINCT {field} FROM courses ORDER BY {field}"
            ).fetchall()
        # 说明：返回处理结果，供调用方继续使用。
        return [row[field] for row in rows]

    # 说明：导出全部课程信息到 CSV 文件。
    def export_courses_csv(self, path: str | Path) -> None:
        # 说明：计算或保存 headers，作为后续业务校验、数据库操作或返回结果使用。
        headers = [
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            "course_code",
            "course_name",
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            "course_type",
            "total_hours",
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            "lecture_hours",
            "practice_hours",
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            "credits",
            "semester",
        ]
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        _write_csv(path, headers, self.list_courses())

    # 说明：集中校验课程表单数据，保证学时和学分合法。
    def _validate_course(self, data: dict[str, Any]) -> dict[str, Any]:
        # 说明：调用整数转换函数，校验学时类输入。
        total_hours = _to_int(data.get("total_hours"), "总学时")
        lecture_hours = _to_int(data.get("lecture_hours"), "授课学时")
        # 说明：调用整数转换函数，校验学时类输入。
        practice_hours = _to_int(data.get("practice_hours"), "实验或上机学时")
        # 说明：校验授课学时和实践学时之和不能超过总学时。
        if lecture_hours + practice_hours > total_hours:
            # 说明：主动抛出业务异常，交由上层界面或测试处理。
            raise ServiceError("授课学时与实验或上机学时之和不能大于总学时")
        # 说明：返回处理结果，供调用方继续使用。
        return {
            # 说明：调用文本清理函数，统一处理必填字段。
            "course_code": _clean_text(data.get("course_code"), "课程编号"),
            "course_name": _clean_text(data.get("course_name"), "课程名称"),
            # 说明：调用文本清理函数，统一处理必填字段。
            "course_type": _clean_text(data.get("course_type"), "课程性质"),
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            "total_hours": total_hours,
            "lecture_hours": lecture_hours,
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            "practice_hours": practice_hours,
            # 说明：调用正数转换函数，校验学分或最低学分输入。
            "credits": _to_positive_float(data.get("credits"), "学分"),
            # 说明：调用文本清理函数，统一处理必填字段。
            "semester": _clean_text(data.get("semester"), "开课学期"),
        }


# 说明：学生服务类，负责学生资料维护和学生账号同步。
class StudentService:
    # 说明：文档字符串，用于说明当前模块、类或函数的用途。
    """学生资料维护，并负责学生登录账号的同步。"""

    # 说明：定义 __init__ 函数，封装当前模块的一段处理逻辑。
    def __init__(self, db_path: str | Path = DB_PATH):
        # 说明：计算或保存 self.db_path，作为后续业务校验、数据库操作或返回结果使用。
        self.db_path = db_path

    # 说明：按学号、姓名或班级关键字查询学生列表。
    def list_students(self, keyword: str = "") -> list[dict[str, Any]]:
        # 说明：计算或保存 params: list[Any]，作为后续业务校验、数据库操作或返回结果使用。
        params: list[Any] = []
        # 说明：计算或保存 sql，作为后续业务校验、数据库操作或返回结果使用。
        sql = "SELECT * FROM students"
        # 说明：计算或保存 keyword，作为后续业务校验、数据库操作或返回结果使用。
        keyword = keyword.strip()
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if keyword:
            # 说明：计算或保存 sql +，作为后续业务校验、数据库操作或返回结果使用。
            sql += " WHERE student_id LIKE ? OR name LIKE ? OR class_name LIKE ?"
            # 说明：计算或保存 like，作为后续业务校验、数据库操作或返回结果使用。
            like = f"%{keyword}%"
            # 说明：一次性追加多个 SQL 查询参数。
            params.extend([like, like, like])
        # 说明：计算或保存 sql +，作为后续业务校验、数据库操作或返回结果使用。
        sql += " ORDER BY student_id"
        # 说明：使用上下文管理器自动管理数据库连接、文件或窗口资源。
        with get_connection(self.db_path) as conn:
            # 说明：执行 SQL 语句，并通过参数绑定传入变量。
            return [dict(row) for row in conn.execute(sql, params).fetchall()]

    # 说明：根据学号查询单个学生资料。
    def get_student(self, student_id: str) -> dict[str, Any] | None:
        # 说明：使用上下文管理器自动管理数据库连接、文件或窗口资源。
        with get_connection(self.db_path) as conn:
            # 说明：执行 SQL 语句，并通过参数绑定传入变量。
            row = conn.execute(
                # 说明：计算或保存 "SELECT * FROM students WHERE student_id，作为后续业务校验、数据库操作或返回结果使用。
                "SELECT * FROM students WHERE student_id = ?",
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                (student_id,),
            ).fetchone()
        # 说明：返回处理结果，供调用方继续使用。
        return dict(row) if row else None

    # 说明：新增学生资料，并同步创建学生登录账号。
    def create_student(self, data: dict[str, Any]) -> None:
        # 说明：计算或保存 payload，作为后续业务校验、数据库操作或返回结果使用。
        payload = self._validate_student(data)
        # 说明：开始异常捕获，避免底层错误直接中断程序。
        try:
            # 说明：使用上下文管理器自动管理数据库连接、文件或窗口资源。
            with get_connection(self.db_path) as conn:
                # 新增学生和创建学生账号放在同一事务中，避免出现有学生无账号的情况。
                conn.execute(
                    """
                    INSERT INTO students(student_id, name, class_name, major, phone)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                        payload["student_id"],
                        payload["name"],
                        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                        payload["class_name"],
                        payload["major"],
                        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                        payload["phone"],
                    ),
                )
                # 说明：执行 SQL 语句，并通过参数绑定传入变量。
                conn.execute(
                    """
                    INSERT INTO users(username, password_hash, role, student_id, display_name, is_active)
                    VALUES (?, ?, 'student', ?, ?, 1)
                    """,
                    (
                        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                        payload["student_id"],
                        hash_password(payload["student_id"]),
                        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                        payload["student_id"],
                        payload["name"],
                    ),
                )
        # 说明：捕获异常并转换为业务提示或测试结果。
        except Exception as exc:
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            if "UNIQUE" in str(exc) or "PRIMARY" in str(exc):
                # 说明：主动抛出业务异常，交由上层界面或测试处理。
                raise ServiceError("学号已存在") from exc
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            raise

    # 说明：更新学生资料，并同步更新账号显示名。
    def update_student(self, student_id: str, data: dict[str, Any]) -> None:
        # 说明：计算或保存 payload，作为后续业务校验、数据库操作或返回结果使用。
        payload = self._validate_student({**data, "student_id": student_id})
        # 说明：使用上下文管理器自动管理数据库连接、文件或窗口资源。
        with get_connection(self.db_path) as conn:
            # 说明：执行 SQL 语句，并通过参数绑定传入变量。
            result = conn.execute(
                """
                UPDATE students SET name = ?, class_name = ?, major = ?, phone = ?
                WHERE student_id = ?
                """,
                (
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    payload["name"],
                    payload["class_name"],
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    payload["major"],
                    payload["phone"],
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    student_id,
                ),
            )
            # 学生姓名变更后，同步更新登录界面和状态栏展示名称。
            conn.execute(
                # 说明：学生姓名修改后同步更新账号显示名。
                "UPDATE users SET display_name = ? WHERE role = 'student' AND student_id = ?",
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                (payload["name"], student_id),
            )
        # 说明：根据受影响行数判断更新或删除操作是否真正命中数据。
        if result.rowcount == 0:
            # 说明：主动抛出业务异常，交由上层界面或测试处理。
            raise ServiceError("未找到要修改的学生")

    # 说明：删除单个学生，关联账号和选课记录通过外键级联删除。
    def delete_student(self, student_id: str) -> None:
        # 说明：使用上下文管理器自动管理数据库连接、文件或窗口资源。
        with get_connection(self.db_path) as conn:
            # 说明：执行 SQL 语句，并通过参数绑定传入变量。
            result = conn.execute(
                # 说明：计算或保存 "DELETE FROM students WHERE student_id，作为后续业务校验、数据库操作或返回结果使用。
                "DELETE FROM students WHERE student_id = ?",
                # 说明：调用文本清理函数，统一处理必填字段。
                (_clean_text(student_id, "学号"),),
            )
        # 说明：根据受影响行数判断更新或删除操作是否真正命中数据。
        if result.rowcount == 0:
            # 说明：主动抛出业务异常，交由上层界面或测试处理。
            raise ServiceError("未找到要删除的学生")

    # 说明：批量删除勾选的学生。
    def delete_students(self, student_ids: list[str]) -> int:
        # 说明：调用文本清理函数，统一处理必填字段。
        cleaned = [_clean_text(student_id, "学号") for student_id in student_ids]
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if not cleaned:
            # 说明：主动抛出业务异常，交由上层界面或测试处理。
            raise ServiceError("请先选择要处理的学生")
        # users 和 enrollments 表通过外键级联删除，批量删除学生时账号与选课记录会一起清理。
        placeholders = ",".join("?" for _ in cleaned)
        # 说明：使用上下文管理器自动管理数据库连接、文件或窗口资源。
        with get_connection(self.db_path) as conn:
            # 说明：执行 SQL 语句，并通过参数绑定传入变量。
            result = conn.execute(
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                f"DELETE FROM students WHERE student_id IN ({placeholders})",
                cleaned,
            )
        # 说明：根据受影响行数判断更新或删除操作是否真正命中数据。
        if result.rowcount == 0:
            # 说明：主动抛出业务异常，交由上层界面或测试处理。
            raise ServiceError("未找到要删除的学生")
        # 说明：根据受影响行数判断更新或删除操作是否真正命中数据。
        return result.rowcount

    # 说明：集中校验学生表单数据，保证学号、姓名等必填字段不为空。
    def _validate_student(self, data: dict[str, Any]) -> dict[str, Any]:
        # 说明：返回处理结果，供调用方继续使用。
        return {
            # 说明：调用文本清理函数，统一处理必填字段。
            "student_id": _clean_text(data.get("student_id"), "学号"),
            "name": _clean_text(data.get("name"), "姓名"),
            # 说明：调用文本清理函数，统一处理必填字段。
            "class_name": _clean_text(data.get("class_name"), "班级"),
            "major": _clean_text(data.get("major"), "专业"),
            # 说明：调用文本清理函数，统一处理必填字段。
            "phone": _clean_text(data.get("phone"), "联系电话"),
        }


# 说明：选课服务类，负责选课、退课和学分统计。
class EnrollmentService:
    # 说明：文档字符串，用于说明当前模块、类或函数的用途。
    """选课、退课和学分统计。"""

    # 说明：定义 __init__ 函数，封装当前模块的一段处理逻辑。
    def __init__(self, db_path: str | Path = DB_PATH):
        # 说明：计算或保存 self.db_path，作为后续业务校验、数据库操作或返回结果使用。
        self.db_path = db_path
        # 说明：计算或保存 self.settings，作为后续业务校验、数据库操作或返回结果使用。
        self.settings = SettingsService(db_path)

    # 说明：写入学生选课记录，并依靠数据库唯一约束避免重复选课。
    def enroll(self, student_id: str, course_code: str) -> None:
        # 说明：调用文本清理函数，统一处理必填字段。
        student_id = _clean_text(student_id, "学号")
        course_code = _clean_text(course_code, "课程编号")
        # 说明：开始异常捕获，避免底层错误直接中断程序。
        try:
            # 说明：使用上下文管理器自动管理数据库连接、文件或窗口资源。
            with get_connection(self.db_path) as conn:
                # enrollments 表有唯一约束，同一学生不能重复选择同一门课程。
                conn.execute(
                    # 说明：写入学生选课记录。
                    "INSERT INTO enrollments(student_id, course_code) VALUES (?, ?)",
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    (student_id, course_code),
                )
        # 说明：捕获异常并转换为业务提示或测试结果。
        except Exception as exc:
            # 说明：计算或保存 text，作为后续业务校验、数据库操作或返回结果使用。
            text = str(exc)
            # 说明：识别重复选课等唯一约束错误，并转为业务提示。
            if "UNIQUE" in text:
                # 说明：主动抛出业务异常，交由上层界面或测试处理。
                raise ServiceError("该学生已选过此课程") from exc
            # 说明：识别学生或课程不存在导致的外键错误。
            if "FOREIGN KEY" in text:
                # 说明：主动抛出业务异常，交由上层界面或测试处理。
                raise ServiceError("学生或课程不存在") from exc
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            raise

    # 说明：学生本人选课入口，只允许使用当前登录账号绑定的学号。
    def enroll_for_user(self, current_user: dict[str, Any], course_code: str) -> None:
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if current_user.get("role") != "student" or not current_user.get("student_id"):
            # 说明：主动抛出业务异常，交由上层界面或测试处理。
            raise ServiceError("当前账号不是学生账号")
        # 学生模式只使用当前登录账号关联的学号，不能替其他学生选课。
        self.enroll(current_user["student_id"], course_code)

    # 说明：批量选课，多门课程在同一事务中处理。
    def enroll_many(self, student_id: str, course_codes: list[str]) -> int:
        # 说明：调用文本清理函数，统一处理必填字段。
        student_id = _clean_text(student_id, "学号")
        cleaned = [_clean_text(code, "课程编号") for code in course_codes]
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if not cleaned:
            # 说明：主动抛出业务异常，交由上层界面或测试处理。
            raise ServiceError("请先选择要处理的课程")
        # 说明：开始异常捕获，避免底层错误直接中断程序。
        try:
            # 说明：使用上下文管理器自动管理数据库连接、文件或窗口资源。
            with get_connection(self.db_path) as conn:
                # 批量选课在一个事务中执行，任一课程失败时整体回滚，避免半成功状态。
                for course_code in cleaned:
                    # 说明：执行 SQL 语句，并通过参数绑定传入变量。
                    conn.execute(
                        # 说明：写入学生选课记录。
                        "INSERT INTO enrollments(student_id, course_code) VALUES (?, ?)",
                        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                        (student_id, course_code),
                    )
        # 说明：捕获异常并转换为业务提示或测试结果。
        except Exception as exc:
            # 说明：计算或保存 text，作为后续业务校验、数据库操作或返回结果使用。
            text = str(exc)
            # 说明：识别重复选课等唯一约束错误，并转为业务提示。
            if "UNIQUE" in text:
                # 说明：主动抛出业务异常，交由上层界面或测试处理。
                raise ServiceError("所选课程中包含已选课程，批量选课已取消") from exc
            # 说明：识别学生或课程不存在导致的外键错误。
            if "FOREIGN KEY" in text:
                # 说明：主动抛出业务异常，交由上层界面或测试处理。
                raise ServiceError("学生或课程不存在，批量选课已取消") from exc
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            raise
        # 说明：返回处理结果，供调用方继续使用。
        return len(cleaned)

    # 说明：学生本人批量选课入口，限制只能操作本人数据。
    def enroll_many_for_user(self, current_user: dict[str, Any], course_codes: list[str]) -> int:
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if current_user.get("role") != "student" or not current_user.get("student_id"):
            # 说明：主动抛出业务异常，交由上层界面或测试处理。
            raise ServiceError("当前账号不是学生账号")
        # 说明：返回处理结果，供调用方继续使用。
        return self.enroll_many(current_user["student_id"], course_codes)

    # 说明：退选指定学生的一门课程。
    def withdraw(self, student_id: str, course_code: str) -> None:
        # 说明：使用上下文管理器自动管理数据库连接、文件或窗口资源。
        with get_connection(self.db_path) as conn:
            # 说明：执行 SQL 语句，并通过参数绑定传入变量。
            result = conn.execute(
                # 说明：计算或保存 "DELETE FROM enrollments WHERE student_id，作为后续业务校验、数据库操作或返回结果使用。
                "DELETE FROM enrollments WHERE student_id = ? AND course_code = ?",
                (
                    # 说明：调用文本清理函数，统一处理必填字段。
                    _clean_text(student_id, "学号"),
                    _clean_text(course_code, "课程编号"),
                ),
            )
        # 说明：根据受影响行数判断更新或删除操作是否真正命中数据。
        if result.rowcount == 0:
            # 说明：主动抛出业务异常，交由上层界面或测试处理。
            raise ServiceError("未找到该选课记录")

    # 说明：学生本人退课入口，限制只能操作本人课程。
    def withdraw_for_user(self, current_user: dict[str, Any], course_code: str) -> None:
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if current_user.get("role") != "student" or not current_user.get("student_id"):
            # 说明：主动抛出业务异常，交由上层界面或测试处理。
            raise ServiceError("当前账号不是学生账号")
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self.withdraw(current_user["student_id"], course_code)

    # 说明：批量退课，删除指定学生多门已选课程。
    def withdraw_many(self, student_id: str, course_codes: list[str]) -> int:
        # 说明：调用文本清理函数，统一处理必填字段。
        student_id = _clean_text(student_id, "学号")
        cleaned = [_clean_text(code, "课程编号") for code in course_codes]
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if not cleaned:
            # 说明：主动抛出业务异常，交由上层界面或测试处理。
            raise ServiceError("请先选择要处理的课程")
        # 说明：根据批量选择数量动态生成 IN 子句占位符。
        placeholders = ",".join("?" for _ in cleaned)
        # 说明：使用上下文管理器自动管理数据库连接、文件或窗口资源。
        with get_connection(self.db_path) as conn:
            # 说明：执行 SQL 语句，并通过参数绑定传入变量。
            result = conn.execute(
                # 说明：计算或保存 f"DELETE FROM enrollments WHERE student_id，作为后续业务校验、数据库操作或返回结果使用。
                f"DELETE FROM enrollments WHERE student_id = ? AND course_code IN ({placeholders})",
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                [student_id, *cleaned],
            )
        # 说明：根据受影响行数判断更新或删除操作是否真正命中数据。
        if result.rowcount == 0:
            # 说明：主动抛出业务异常，交由上层界面或测试处理。
            raise ServiceError("未找到要退选的课程记录")
        # 说明：根据受影响行数判断更新或删除操作是否真正命中数据。
        return result.rowcount

    # 说明：学生本人批量退课入口，限制只能操作本人数据。
    def withdraw_many_for_user(self, current_user: dict[str, Any], course_codes: list[str]) -> int:
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if current_user.get("role") != "student" or not current_user.get("student_id"):
            # 说明：主动抛出业务异常，交由上层界面或测试处理。
            raise ServiceError("当前账号不是学生账号")
        # 说明：返回处理结果，供调用方继续使用。
        return self.withdraw_many(current_user["student_id"], course_codes)

    # 说明：查询某个学生已经选择的课程。
    def list_enrolled_courses(self, student_id: str) -> list[dict[str, Any]]:
        # 说明：使用上下文管理器自动管理数据库连接、文件或窗口资源。
        with get_connection(self.db_path) as conn:
            # 说明：执行 SQL 语句，并通过参数绑定传入变量。
            rows = conn.execute(
                """
                SELECT c.*, e.enrolled_at
                FROM enrollments e
                JOIN courses c ON c.course_code = e.course_code
                WHERE e.student_id = ?
                ORDER BY c.semester, c.course_code
                """,
                # 说明：调用文本清理函数，统一处理必填字段。
                (_clean_text(student_id, "学号"),),
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            ).fetchall()
        # 说明：返回处理结果，供调用方继续使用。
        return [dict(row) for row in rows]

    # 说明：查询某个学生尚未选择的课程。
    def list_available_courses(self, student_id: str) -> list[dict[str, Any]]:
        # 说明：使用上下文管理器自动管理数据库连接、文件或窗口资源。
        with get_connection(self.db_path) as conn:
            # 说明：执行 SQL 语句，并通过参数绑定传入变量。
            rows = conn.execute(
                """
                SELECT *
                FROM courses
                WHERE course_code NOT IN (
                    SELECT course_code FROM enrollments WHERE student_id = ?
                )
                ORDER BY semester, course_code
                """,
                # 说明：调用文本清理函数，统一处理必填字段。
                (_clean_text(student_id, "学号"),),
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            ).fetchall()
        # 说明：返回处理结果，供调用方继续使用。
        return [dict(row) for row in rows]

    # 说明：汇总学生已选门数、总学分、达标状态和差额学分。
    def get_credit_summary(self, student_id: str) -> dict[str, Any]:
        # 说明：读取当前学生已经选择的课程。
        courses = self.list_enrolled_courses(student_id)
        # 说明：累加已选课程学分，作为学分统计基础。
        total = sum(float(course["credits"]) for course in courses)
        # 达标判断实时读取 settings 表中的要求，设置页修改后统计结果立即变化。
        required = self.settings.get_min_required_credits()
        # 说明：返回处理结果，供调用方继续使用。
        return {
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            "student_id": student_id,
            "selected_count": len(courses),
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            "total_credits": total,
            "required_credits": required,
            # 说明：计算或保存 "is_qualified": total >，作为后续业务校验、数据库操作或返回结果使用。
            "is_qualified": total >= required,
            # 说明：计算距离最低毕业学分要求还差多少。
            "remaining_credits": max(required - total, 0),
        }

    # 说明：汇总所有学生的选课和学分达标情况，供管理员查看。
    def list_student_summaries(self) -> list[dict[str, Any]]:
        # 说明：计算或保存 required，作为后续业务校验、数据库操作或返回结果使用。
        required = self.settings.get_min_required_credits()
        # 说明：使用上下文管理器自动管理数据库连接、文件或窗口资源。
        with get_connection(self.db_path) as conn:
            # 说明：执行 SQL 语句，并通过参数绑定传入变量。
            rows = conn.execute(
                """
                SELECT
                    s.student_id,
                    s.name,
                    s.class_name,
                    COALESCE(SUM(c.credits), 0) AS total_credits,
                    COUNT(e.id) AS selected_count
                FROM students s
                LEFT JOIN enrollments e ON e.student_id = s.student_id
                LEFT JOIN courses c ON c.course_code = e.course_code
                GROUP BY s.student_id, s.name, s.class_name
                ORDER BY s.student_id
                """
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            ).fetchall()
        # 说明：计算或保存 summaries: list[dict[str, Any]]，作为后续业务校验、数据库操作或返回结果使用。
        summaries: list[dict[str, Any]] = []
        # 说明：循环处理多条记录、多个控件或多个动画粒子。
        for row in rows:
            # 说明：计算或保存 data，作为后续业务校验、数据库操作或返回结果使用。
            data = dict(row)
            # 说明：计算或保存 data["required_credits"]，作为后续业务校验、数据库操作或返回结果使用。
            data["required_credits"] = required
            # 说明：计算或保存 data["is_qualified"]，作为后续业务校验、数据库操作或返回结果使用。
            data["is_qualified"] = float(data["total_credits"]) >= required
            # 说明：计算距离最低毕业学分要求还差多少。
            data["remaining_credits"] = max(required - float(data["total_credits"]), 0)
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            summaries.append(data)
        # 说明：返回处理结果，供调用方继续使用。
        return summaries

    # 说明：导出学生选课明细到 CSV 文件。
    def export_enrollments_csv(self, path: str | Path) -> None:
        # 说明：使用上下文管理器自动管理数据库连接、文件或窗口资源。
        with get_connection(self.db_path) as conn:
            # 说明：计算或保存 rows，作为后续业务校验、数据库操作或返回结果使用。
            rows = [
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                dict(row)
                # 说明：执行 SQL 语句，并通过参数绑定传入变量。
                for row in conn.execute(
                    """
                    SELECT
                        s.student_id,
                        s.name,
                        s.class_name,
                        c.course_code,
                        c.course_name,
                        c.course_type,
                        c.credits,
                        c.semester,
                        e.enrolled_at
                    FROM enrollments e
                    JOIN students s ON s.student_id = e.student_id
                    JOIN courses c ON c.course_code = e.course_code
                    ORDER BY s.student_id, c.semester, c.course_code
                    """
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                ).fetchall()
            ]
        # 说明：计算或保存 headers，作为后续业务校验、数据库操作或返回结果使用。
        headers = [
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            "student_id",
            "name",
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            "class_name",
            "course_code",
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            "course_name",
            "course_type",
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            "credits",
            "semester",
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            "enrolled_at",
        ]
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        _write_csv(path, headers, rows)
