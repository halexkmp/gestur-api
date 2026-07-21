from fastapi import APIRouter
from app.slices.employees.create_employee.ui.route import router as create_employee_router
from app.slices.employees.get_employee.ui.route import router as get_employee_router
from app.slices.employees.list_employees.ui.route import router as list_employees_router
from app.slices.employees.update_employee.ui.route import router as update_employee_router
from app.slices.employees.delete_employee.ui.route import router as delete_employee_router
from app.slices.employees.create_salary_advance.ui.route import router as create_salary_advance_router
from app.slices.employees.list_salary_advances.ui.route import router as list_salary_advances_router
from app.slices.employees.delete_salary_advance.ui.route import router as delete_salary_advance_router
from app.slices.employees.get_salary_summary.ui.route import router as get_salary_summary_router
from app.slices.employees.get_lateness_config.ui.route import router as get_lateness_config_router
from app.slices.employees.update_lateness_config.ui.route import router as update_lateness_config_router
from app.slices.employees.get_my_salary_summary.ui.route import router as get_my_salary_summary_router
from app.slices.employees.list_my_salary_advances.ui.route import router as list_my_salary_advances_router
from app.slices.employees.get_employee_schedule.ui.route import router as get_employee_schedule_router
from app.slices.employees.set_employee_schedule.ui.route import router as set_employee_schedule_router
from app.slices.employees.get_my_employee_schedule.ui.route import router as get_my_employee_schedule_router
from app.slices.employees.create_justified_absence.ui.route import router as create_justified_absence_router
from app.slices.employees.list_justified_absences.ui.route import router as list_justified_absences_router
from app.slices.employees.delete_justified_absence.ui.route import router as delete_justified_absence_router
from app.slices.employees.get_attendance_verification.ui.route import router as get_attendance_verification_router
from app.slices.employees.get_employees_schedule_overview.ui.route import router as get_employees_schedule_overview_router

router = APIRouter(prefix="/employees", tags=["employees"])
# Register fixed-prefix routes first to avoid conflicts with /{employee_id}
router.include_router(create_employee_router)
router.include_router(list_employees_router)
router.include_router(get_salary_summary_router)
router.include_router(create_salary_advance_router)
router.include_router(list_salary_advances_router)
router.include_router(delete_salary_advance_router)
router.include_router(get_lateness_config_router)
router.include_router(update_lateness_config_router)
router.include_router(get_my_salary_summary_router)
router.include_router(list_my_salary_advances_router)
router.include_router(get_employee_schedule_router)
router.include_router(set_employee_schedule_router)
router.include_router(get_my_employee_schedule_router)
router.include_router(create_justified_absence_router)
router.include_router(list_justified_absences_router)
router.include_router(delete_justified_absence_router)
router.include_router(get_attendance_verification_router)
router.include_router(get_employees_schedule_overview_router)
# Register dynamic routes last so they don't capture fixed paths like /salary-advances
# or /lateness-config (both PUT /{employee_id} and PUT /lateness-config would otherwise collide)
router.include_router(update_employee_router)
router.include_router(delete_employee_router)
router.include_router(get_employee_router)
