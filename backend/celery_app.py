import csv
import os
from datetime import datetime

from celery import Celery

from app import create_app
from controller.models import (
    db,
    Student,
    Company,
    Application,
    Offer
)

celery = Celery(
    "celery",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery.conf.timezone = "Asia/Kolkata"

celery.conf.beat_schedule = {
    "monthly-placement-report": {
        "task": "celery_app.monthly_report",
        "schedule": {
            "type": "crontab",
            "minute": 0,
            "hour": 9,
            "day_of_month": 1
        }
    }
}


# ----------------------------------------------------
# Student Export
# ----------------------------------------------------

@celery.task(name="celery_app.export_student_history")
def export_student_history(student_roll):

    app, _ = create_app()

    with app.app_context():

        student = Student.query.get(student_roll)

        if not student:
            return None

        filename = (
            f"student_{student.roll_no}_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )

        filepath = os.path.join(
            app.config["EXPORT_FOLDER"],
            filename
        )

        os.makedirs(app.config["EXPORT_FOLDER"], exist_ok=True)

        applications = (
            Application.query
            .filter_by(student_id=student.roll_no)
            .all()
        )

        with open(filepath, "w", newline="", encoding="utf-8") as file:

            writer = csv.writer(file)

            writer.writerow([
                "Application ID",
                "Company",
                "Job Title",
                "Application Date",
                "Application Status",
                "Offer Status",
                "Package",
                "Joining Date"
            ])

            for application in applications:

                offer = application.offer

                writer.writerow([
                    application.id,
                    application.placement_drive.company.name,
                    application.placement_drive.job_title,
                    application.application_date,
                    application.status,
                    offer.status if offer else "",
                    offer.package if offer else "",
                    offer.joining_date if offer else ""
                ])

        return filename


# ----------------------------------------------------
# Company Export
# ----------------------------------------------------

@celery.task(name="celery_app.export_company_history")
def export_company_history(company_id):

    app, _ = create_app()

    with app.app_context():

        company = Company.query.get(company_id)

        if not company:
            return None

        filename = (
            f"company_{company.id}_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )

        filepath = os.path.join(
            app.config["EXPORT_FOLDER"],
            filename
        )

        os.makedirs(app.config["EXPORT_FOLDER"], exist_ok=True)

        applications = (
            Application.query
            .join(Application.placement_drive)
            .filter_by(company_id=company.id)
            .all()
        )

        with open(filepath, "w", newline="", encoding="utf-8") as file:

            writer = csv.writer(file)

            writer.writerow([
                "Application ID",
                "Student",
                "Roll Number",
                "Job Title",
                "Application Status",
                "Offer Status",
                "Package"
            ])

            for application in applications:

                offer = application.offer

                writer.writerow([
                    application.id,
                    application.student.name,
                    application.student.roll_no,
                    application.placement_drive.job_title,
                    application.status,
                    offer.status if offer else "",
                    offer.package if offer else ""
                ])

        return filename