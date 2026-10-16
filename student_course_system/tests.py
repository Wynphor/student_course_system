# 说明：启用延迟类型注解，提升类型提示在不同 Python 版本下的兼容性。
from __future__ import annotations

# 说明：导入当前模块需要使用的标准库、第三方库或项目内部模块。
import tempfile
import shutil
# 说明：导入当前模块需要使用的标准库、第三方库或项目内部模块。
import unittest
import importlib
# 说明：导入当前模块需要使用的标准库、第三方库或项目内部模块。
from pathlib import Path

from .db import initialize_database
# 说明：导入当前模块需要使用的标准库、第三方库或项目内部模块。
from .services import AuthService, CourseService, EnrollmentService, ServiceError, SettingsService, StudentService


# 说明：单元测试类，使用独立临时数据库验证核心功能。
class ElectiveSystemTestCase(unittest.TestCase):
    # 说明：定义 setUp 函数，封装当前模块的一段处理逻辑。
    def setUp(self) -> None:
        # 每个测试使用独立临时数据库，避免测试之间的数据互相影响。
        base_tmp = Path(__file__).resolve().parent.parent / "tmp" / "student_course_system_tests"
        # 说明：准备 base_tmp.mkdir(parents，作为当前测试步骤的输入数据或实际结果。
        base_tmp.mkdir(parents=True, exist_ok=True)
        # 说明：创建独立临时目录，避免测试污染正式数据。
        self.tmp_path = Path(tempfile.mkdtemp(prefix="case_", dir=base_tmp))
        # 说明：准备 self.db_path，作为当前测试步骤的输入数据或实际结果。
        self.db_path = self.tmp_path / "test.db"
        # 说明：准备 initialize_database(self.db_path, seed，作为当前测试步骤的输入数据或实际结果。
        initialize_database(self.db_path, seed=True)
        # 说明：准备 self.courses，作为当前测试步骤的输入数据或实际结果。
        self.courses = CourseService(self.db_path)
        # 说明：准备 self.students，作为当前测试步骤的输入数据或实际结果。
        self.students = StudentService(self.db_path)
        # 说明：准备 self.enrollments，作为当前测试步骤的输入数据或实际结果。
        self.enrollments = EnrollmentService(self.db_path)
        # 说明：准备 self.settings，作为当前测试步骤的输入数据或实际结果。
        self.settings = SettingsService(self.db_path)
        # 说明：准备 self.auth，作为当前测试步骤的输入数据或实际结果。
        self.auth = AuthService(self.db_path)

    # 说明：定义 tearDown 函数，封装当前模块的一段处理逻辑。
    def tearDown(self) -> None:
        # 说明：测试结束后删除临时目录。
        shutil.rmtree(self.tmp_path, ignore_errors=True)

    # 说明：定义测试用例 test_database_seed_and_default_setting，验证系统对应功能是否符合预期。
    def test_database_seed_and_default_setting(self) -> None:
        # 说明：断言实际结果是否符合预期。
        self.assertGreaterEqual(len(self.courses.list_courses()), 8)
        self.assertGreaterEqual(len(self.students.list_students()), 3)
        # 说明：断言实际结果是否符合预期。
        self.assertEqual(self.settings.get_min_required_credits(), 60.0)

    # 说明：定义测试用例 test_default_admin_and_student_login，验证系统对应功能是否符合预期。
    def test_default_admin_and_student_login(self) -> None:
        # 说明：准备 admin，作为当前测试步骤的输入数据或实际结果。
        admin = self.auth.login("admin", "123456")
        # 说明：断言实际结果是否符合预期。
        self.assertEqual(admin["role"], "admin")
        self.assertIsNone(admin["student_id"])

        # 说明：准备 student，作为当前测试步骤的输入数据或实际结果。
        student = self.auth.login("2024001", "2024001")
        # 说明：断言实际结果是否符合预期。
        self.assertEqual(student["role"], "student")
        self.assertEqual(student["student_id"], "2024001")

        # 说明：断言实际结果是否符合预期。
        with self.assertRaises(ServiceError):
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            self.auth.login("admin", "wrong")

    # 说明：定义测试用例 test_student_can_change_own_password，验证系统对应功能是否符合预期。
    def test_student_can_change_own_password(self) -> None:
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self.auth.change_password("2024001", "2024001", "abc12345", "abc12345")
        # 说明：准备 user，作为当前测试步骤的输入数据或实际结果。
        user = self.auth.login("2024001", "abc12345")
        # 说明：断言实际结果是否符合预期。
        self.assertEqual(user["student_id"], "2024001")

        with self.assertRaises(ServiceError):
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            self.auth.login("2024001", "2024001")

        # 说明：断言实际结果是否符合预期。
        with self.assertRaises(ServiceError):
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            self.auth.change_password("2024001", "wrong-old", "newpass1", "newpass1")

        # 说明：断言实际结果是否符合预期。
        with self.assertRaises(ServiceError):
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            self.auth.change_password("2024001", "abc12345", "short", "short")

        # 说明：断言实际结果是否符合预期。
        with self.assertRaises(ServiceError):
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            self.auth.change_password("2024001", "abc12345", "newpass1", "newpass2")

    # 说明：定义测试用例 test_course_create_query_update_delete，验证系统对应功能是否符合预期。
    def test_course_create_query_update_delete(self) -> None:
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self.courses.create_course(
            {
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                "course_code": "MATH201",
                "course_name": "离散数学",
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                "course_type": "专业必修",
                "total_hours": "48",
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                "lecture_hours": "40",
                "practice_hours": "8",
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                "credits": "3",
                "semester": "第2学期",
            }
        )
        # 说明：准备 queried，作为当前测试步骤的输入数据或实际结果。
        queried = self.courses.list_courses({"keyword": "离散", "course_type": "专业必修"})
        # 说明：断言实际结果是否符合预期。
        self.assertEqual(len(queried), 1)
        self.assertEqual(queried[0]["course_code"], "MATH201")

        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self.courses.update_course(
            "MATH201",
            {
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                "course_name": "离散数学基础",
                "course_type": "专业必修",
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                "total_hours": "48",
                "lecture_hours": "36",
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                "practice_hours": "12",
                "credits": "3.5",
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                "semester": "第2学期",
            },
        )
        # 说明：断言实际结果是否符合预期。
        self.assertEqual(self.courses.get_course("MATH201")["credits"], 3.5)

        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self.courses.delete_course("MATH201")
        # 说明：断言实际结果是否符合预期。
        self.assertIsNone(self.courses.get_course("MATH201"))

    # 说明：定义测试用例 test_course_credit_and_type_search，验证系统对应功能是否符合预期。
    def test_course_credit_and_type_search(self) -> None:
        # 说明：准备 rows，作为当前测试步骤的输入数据或实际结果。
        rows = self.courses.list_courses({"min_credits": "3", "max_credits": "4", "course_type": "专业必修"})
        # 说明：断言实际结果是否符合预期。
        self.assertTrue(rows)
        self.assertTrue(all(row["course_type"] == "专业必修" for row in rows))
        # 说明：断言实际结果是否符合预期。
        self.assertTrue(all(3 <= float(row["credits"]) <= 4 for row in rows))

    # 说明：定义测试用例 test_enrollment_prevents_duplicate_and_withdraws，验证系统对应功能是否符合预期。
    def test_enrollment_prevents_duplicate_and_withdraws(self) -> None:
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self.enrollments.enroll("2024001", "CS101")
        # 说明：断言实际结果是否符合预期。
        with self.assertRaises(ServiceError):
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            self.enrollments.enroll("2024001", "CS101")

        # 说明：读取并展示当前学生的学分统计结果。
        summary = self.enrollments.get_credit_summary("2024001")
        # 说明：断言实际结果是否符合预期。
        self.assertEqual(summary["selected_count"], 1)
        self.assertEqual(summary["total_credits"], 4.0)

        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self.enrollments.withdraw("2024001", "CS101")
        # 说明：读取并展示当前学生的学分统计结果。
        summary = self.enrollments.get_credit_summary("2024001")
        # 说明：断言实际结果是否符合预期。
        self.assertEqual(summary["selected_count"], 0)
        self.assertEqual(summary["total_credits"], 0)

    # 说明：定义测试用例 test_batch_course_student_and_enrollment_operations，验证系统对应功能是否符合预期。
    def test_batch_course_student_and_enrollment_operations(self) -> None:
        # 说明：准备 count，作为当前测试步骤的输入数据或实际结果。
        count = self.enrollments.enroll_many("2024001", ["CS101", "CS102"])
        # 说明：断言实际结果是否符合预期。
        self.assertEqual(count, 2)
        # 说明：读取并展示当前学生的学分统计结果。
        summary = self.enrollments.get_credit_summary("2024001")
        # 说明：断言实际结果是否符合预期。
        self.assertEqual(summary["selected_count"], 2)
        self.assertEqual(summary["total_credits"], 8.0)

        # 说明：准备 count，作为当前测试步骤的输入数据或实际结果。
        count = self.enrollments.withdraw_many("2024001", ["CS101", "CS102"])
        # 说明：断言实际结果是否符合预期。
        self.assertEqual(count, 2)
        # 说明：读取并展示当前学生的学分统计结果。
        self.assertEqual(self.enrollments.get_credit_summary("2024001")["selected_count"], 0)

        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self.enrollments.enroll("2024002", "AI101")
        # 说明：准备 deleted_courses，作为当前测试步骤的输入数据或实际结果。
        deleted_courses = self.courses.delete_courses(["AI101", "PE101"])
        # 说明：断言实际结果是否符合预期。
        self.assertEqual(deleted_courses, 2)
        self.assertIsNone(self.courses.get_course("AI101"))
        # 说明：读取并展示当前学生的学分统计结果。
        self.assertEqual(self.enrollments.get_credit_summary("2024002")["selected_count"], 0)

        # 说明：准备 deleted_students，作为当前测试步骤的输入数据或实际结果。
        deleted_students = self.students.delete_students(["2024002", "2024003"])
        # 说明：断言实际结果是否符合预期。
        self.assertEqual(deleted_students, 2)
        self.assertIsNone(self.auth.get_user("2024002"))
        # 说明：断言实际结果是否符合预期。
        self.assertIsNone(self.auth.get_user("2024003"))

    # 说明：定义测试用例 test_new_student_account_delete_cascade_and_password_reset，验证系统对应功能是否符合预期。
    def test_new_student_account_delete_cascade_and_password_reset(self) -> None:
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self.students.create_student(
            {
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                "student_id": "2024999",
                "name": "测试学生",
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                "class_name": "计科2499",
                "major": "计算机科学与技术",
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                "phone": "13900009999",
            }
        )
        # 说明：准备 user，作为当前测试步骤的输入数据或实际结果。
        user = self.auth.login("2024999", "2024999")
        # 说明：断言实际结果是否符合预期。
        self.assertEqual(user["student_id"], "2024999")

        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self.auth.reset_student_password("2024999")
        # 说明：断言实际结果是否符合预期。
        self.assertEqual(self.auth.login("2024999", "2024999")["role"], "student")

        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self.students.delete_student("2024999")
        # 说明：断言实际结果是否符合预期。
        self.assertIsNone(self.auth.get_user("2024999"))

    # 说明：定义测试用例 test_student_user_enrollment_is_limited_to_self，验证系统对应功能是否符合预期。
    def test_student_user_enrollment_is_limited_to_self(self) -> None:
        # 说明：准备 user，作为当前测试步骤的输入数据或实际结果。
        user = self.auth.login("2024001", "2024001")
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self.enrollments.enroll_for_user(user, "CS101")
        # 说明：读取并展示当前学生的学分统计结果。
        own_summary = self.enrollments.get_credit_summary("2024001")
        other_summary = self.enrollments.get_credit_summary("2024002")
        # 说明：断言实际结果是否符合预期。
        self.assertEqual(own_summary["selected_count"], 1)
        self.assertEqual(other_summary["selected_count"], 0)

        # 说明：断言实际结果是否符合预期。
        with self.assertRaises(ServiceError):
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            self.enrollments.enroll_for_user({"role": "admin", "student_id": None}, "CS102")

    # 说明：定义测试用例 test_setting_changes_credit_qualification，验证系统对应功能是否符合预期。
    def test_setting_changes_credit_qualification(self) -> None:
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self.enrollments.enroll("2024002", "CS101")
        self.settings.set_min_required_credits("3")
        # 说明：读取并展示当前学生的学分统计结果。
        self.assertTrue(self.enrollments.get_credit_summary("2024002")["is_qualified"])

        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self.settings.set_min_required_credits("5")
        # 说明：读取并展示当前学生的学分统计结果。
        summary = self.enrollments.get_credit_summary("2024002")
        # 说明：断言实际结果是否符合预期。
        self.assertFalse(summary["is_qualified"])
        # 说明：计算距离最低毕业学分要求还差多少。
        self.assertEqual(summary["remaining_credits"], 1.0)

    # 说明：定义测试用例 test_export_csv_files，验证系统对应功能是否符合预期。
    def test_export_csv_files(self) -> None:
        # 说明：准备 course_path，作为当前测试步骤的输入数据或实际结果。
        course_path = self.tmp_path / "courses.csv"
        # 说明：准备 enrollment_path，作为当前测试步骤的输入数据或实际结果。
        enrollment_path = self.tmp_path / "enrollments.csv"
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self.enrollments.enroll("2024003", "CS202")
        self.courses.export_courses_csv(course_path)
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self.enrollments.export_enrollments_csv(enrollment_path)
        # 说明：断言实际结果是否符合预期。
        self.assertTrue(course_path.exists())
        self.assertTrue(enrollment_path.exists())
        # 说明：断言实际结果是否符合预期。
        self.assertIn("course_code", course_path.read_text(encoding="utf-8-sig"))
        self.assertIn("student_id", enrollment_path.read_text(encoding="utf-8-sig"))

    # 说明：定义测试用例 test_pixel_assets_and_ui_import，验证系统对应功能是否符合预期。
    def test_pixel_assets_and_ui_import(self) -> None:
        # 说明：导入当前模块需要使用的标准库、第三方库或项目内部模块。
        from . import ui
        from . import pixel_assets

        # 说明：检查并准备本地素材，素材缺失时自动生成占位图。
        paths = pixel_assets.ensure_assets()
        # 说明：断言实际结果是否符合预期。
        self.assertTrue(paths["login"].exists())
        self.assertTrue(paths["sidebar"].exists())
        # 说明：断言实际结果是否符合预期。
        self.assertTrue(paths["kanban"].exists())
        self.assertIn(paths["login"].read_bytes()[:6], {b"GIF89a", b"GIF87a", b"\x89PNG\r\n"})
        # 说明：断言实际结果是否符合预期。
        self.assertIn(paths["sidebar"].read_bytes()[:6], {b"GIF89a", b"GIF87a", b"\x89PNG\r\n"})
        # 说明：准备 module，作为当前测试步骤的输入数据或实际结果。
        module = importlib.reload(ui)
        # 说明：断言实际结果是否符合预期。
        self.assertTrue(hasattr(module, "ElectiveCourseApp"))
        self.assertTrue(hasattr(module, "AnimatedGif"))
        # 说明：断言实际结果是否符合预期。
        self.assertTrue(hasattr(module, "NyanVirusBackground"))
        self.assertTrue(hasattr(module, "PixelFirework"))
        # 说明：断言实际结果是否符合预期。
        self.assertTrue(hasattr(module, "KanbanMascot"))

    # 说明：定义测试用例 test_pixel_assets_fallback_without_downloaded_source，验证系统对应功能是否符合预期。
    def test_pixel_assets_fallback_without_downloaded_source(self) -> None:
        # 说明：导入当前模块需要使用的标准库、第三方库或项目内部模块。
        from . import pixel_assets

        # 说明：准备 original_values，作为当前测试步骤的输入数据或实际结果。
        original_values = {
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            "ASSET_DIR": pixel_assets.ASSET_DIR,
            "NYAN_SOURCE": pixel_assets.NYAN_SOURCE,
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            "NYAN_LOGIN": pixel_assets.NYAN_LOGIN,
            "NYAN_SIDEBAR": pixel_assets.NYAN_SIDEBAR,
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            "LOGIN_FALLBACK": pixel_assets.LOGIN_FALLBACK,
            "SIDEBAR_FALLBACK": pixel_assets.SIDEBAR_FALLBACK,
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            "KANBAN_SOURCE": pixel_assets.KANBAN_SOURCE,
            "KANBAN_FALLBACK": pixel_assets.KANBAN_FALLBACK,
        }
        # 说明：开始异常捕获，避免底层错误直接中断程序。
        try:
            # 说明：准备 asset_dir，作为当前测试步骤的输入数据或实际结果。
            asset_dir = self.tmp_path / "asset_fallback"
            # 说明：准备 pixel_assets.ASSET_DIR，作为当前测试步骤的输入数据或实际结果。
            pixel_assets.ASSET_DIR = asset_dir
            # 说明：准备 pixel_assets.NYAN_SOURCE，作为当前测试步骤的输入数据或实际结果。
            pixel_assets.NYAN_SOURCE = asset_dir / "nyan_cat_source.gif"
            # 说明：准备 pixel_assets.NYAN_LOGIN，作为当前测试步骤的输入数据或实际结果。
            pixel_assets.NYAN_LOGIN = asset_dir / "nyan_cat_login.gif"
            # 说明：准备 pixel_assets.NYAN_SIDEBAR，作为当前测试步骤的输入数据或实际结果。
            pixel_assets.NYAN_SIDEBAR = asset_dir / "nyan_cat_sidebar.gif"
            # 说明：准备 pixel_assets.LOGIN_FALLBACK，作为当前测试步骤的输入数据或实际结果。
            pixel_assets.LOGIN_FALLBACK = asset_dir / "login_mascot.png"
            # 说明：准备 pixel_assets.SIDEBAR_FALLBACK，作为当前测试步骤的输入数据或实际结果。
            pixel_assets.SIDEBAR_FALLBACK = asset_dir / "sidebar_mascot.png"
            # 说明：准备 pixel_assets.KANBAN_SOURCE，作为当前测试步骤的输入数据或实际结果。
            pixel_assets.KANBAN_SOURCE = asset_dir / "kanban_musume_source.png"
            # 说明：准备 pixel_assets.KANBAN_FALLBACK，作为当前测试步骤的输入数据或实际结果。
            pixel_assets.KANBAN_FALLBACK = asset_dir / "kanban_musume_fallback.png"
            # 说明：检查并准备本地素材，素材缺失时自动生成占位图。
            paths = pixel_assets.ensure_assets()
            # 说明：断言实际结果是否符合预期。
            self.assertEqual(paths["login"].read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
            self.assertEqual(paths["sidebar"].read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
            # 说明：断言实际结果是否符合预期。
            self.assertEqual(paths["kanban"].read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
        # 说明：无论是否发生异常都执行收尾逻辑。
        finally:
            # 说明：循环处理多条记录、多个控件或多个动画粒子。
            for key, value in original_values.items():
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                setattr(pixel_assets, key, value)


# 说明：根据条件选择不同处理分支，控制程序执行路径。
if __name__ == "__main__":
    # 说明：使用 unittest 框架组织自动化测试。
    unittest.main()
