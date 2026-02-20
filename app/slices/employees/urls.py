from fastapi import APIRouter
from app.slices.employees.create_employee.ui.route import router as create_employee_router
from app.slices.employees.get_employee.ui.route import router as get_employee_router
from app.slices.employees.list_employees.ui.route import router as list_employees_router
from app.slices.employees.update_employee.ui.route import router as update_employee_router
from app.slices.employees.delete_employee.ui.route import router as delete_employee_router
from app.slices.employees.create_salary_advance.ui.route import router as create_salary_advance_router
from app.slices.employees.list_salary_advances.ui.route import router as list_salary_advances_router
from app.slices.employees.get_salary_summary.ui.route import router as get_salary_summary_router

router = APIRouter(prefix="/employees", tags=["employees"])
# Register fixed-prefix routes first to avoid conflicts with /{employee_id}
router.include_router(create_employee_router)
router.include_router(list_employees_router)
router.include_router(update_employee_router)
router.include_router(delete_employee_router)
router.include_router(get_salary_summary_router)
router.include_router(create_salary_advance_router)
router.include_router(list_salary_advances_router)
# Register the dynamic route last so it doesn't capture fixed paths like /salary-advances
router.include_router(get_employee_router)
