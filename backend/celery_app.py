import csv
import os
from datetime import datetime,timedelta

from celery import Celery
from celery.schedules import crontab
from app import create_app
from controller.models import (
    db,
    Student,
    Company,
    Application,
    Offer,Placement_Drive,Interview,Eligibility,User
)
from sqlalchemy import func
from flask_mail import Message
from flask import render_template

from app import mail


celery = Celery(
    "celery",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery.conf.timezone = "Asia/Kolkata"

celery.conf.beat_schedule = {

    "daily-student-reminder": {

        "task": "celery_app.daily_student_reminder",

        "schedule": crontab(
            hour=9,
            minute=0
        )

    },

    "monthly-placement-report": {

        "task": "celery_app.monthly_report",

        "schedule": crontab(
            day_of_month=1,
            hour=9,
            minute=0
        )

    }

}
@celery.task(name="celery_app.monthly_report")
def monthly_report():
    from app import create_app
    app, _ = create_app()

    with app.app_context():

        today = datetime.now()
        month_name = today.strftime("%B %Y")

        total_students = Student.query.count()
        placed_students = Student.query.filter_by(placed=True).count()

        placement_percentage = (
            round((placed_students / total_students) * 100, 2)
            if total_students else 0
        )

        total_companies = Company.query.count()

        approved_companies = Company.query.filter_by(
            approval_status="Approved"
        ).count()

        total_drives = Placement_Drive.query.count()

        approved_drives = Placement_Drive.query.filter_by(
            status="Approved"
        ).count()

        pending_drives = Placement_Drive.query.filter_by(
            status="Pending"
        ).count()

        closed_drives = Placement_Drive.query.filter_by(
            status="Closed"
        ).count()

        rejected_drives = Placement_Drive.query.filter_by(
            status="Rejected"
        ).count()

        total_applications = Application.query.count()

        applied = Application.query.filter_by(
            status="Applied"
        ).count()

        shortlisted = Application.query.filter_by(
            status="Shortlisted"
        ).count()

        selected = Application.query.filter_by(
            status="Selected"
        ).count()

        rejected = Application.query.filter_by(
            status="Rejected"
        ).count()

        cancelled = Application.query.filter_by(
            status="Cancelled"
        ).count()

        total_interviews = Interview.query.count()

        scheduled = Interview.query.filter_by(
            status="Scheduled"
        ).count()

        completed = Interview.query.filter_by(
            status="Completed"
        ).count()

        cancelled_interviews = Interview.query.filter_by(
            status="Cancelled"
        ).count()

        interviews_this_month = Interview.query.filter(
            func.extract("month", Interview.interview_datetime) == today.month,
            func.extract("year", Interview.interview_datetime) == today.year
        ).count()

        total_offers = Offer.query.count()

        offered = Offer.query.filter_by(
            status="Offered"
        ).count()

        accepted = Offer.query.filter_by(
            status="Accepted"
        ).count()

        rejected_offers = Offer.query.filter_by(
            status="Rejected"
        ).count()

        top_companies = (
    db.session.query(
        Company.name,
        func.count(Application.id).label("applications")
    )
    .select_from(Company)
    .join(
        Placement_Drive,
        Company.id == Placement_Drive.company_id
    )
    .join(
        Application,
        Placement_Drive.id == Application.drive_id
    )
    .group_by(Company.id, Company.name)
    .order_by(func.count(Application.id).desc())
    .limit(5)
    .all()
)

        admin = User.query.filter_by(
            email="admin@gmail.com"
        ).first()

        if not admin:
            return

        msg = Message(
            subject=f"Monthly Placement Report - {month_name}",
            recipients=[admin.email]
        )

        msg.html = render_template(
            "monthly_report_admin.html",

            month=month_name,

            total_students=total_students,
            placed_students=placed_students,
            placement_percentage=placement_percentage,

            total_companies=total_companies,
            approved_companies=approved_companies,

            total_drives=total_drives,
            approved_drives=approved_drives,
            pending_drives=pending_drives,
            closed_drives=closed_drives,
            rejected_drives=rejected_drives,

            total_applications=total_applications,
            applied=applied,
            shortlisted=shortlisted,
            selected=selected,
            rejected=rejected,
            cancelled=cancelled,

            total_interviews=total_interviews,
            scheduled=scheduled,
            completed=completed,
            cancelled_interviews=cancelled_interviews,
            interviews_this_month=interviews_this_month,

            total_offers=total_offers,
            offered=offered,
            accepted=accepted,
            rejected_offers=rejected_offers,

            top_companies=top_companies
        )

        mail.send(msg)

@celery.task(name="celery_app.daily_student_reminder")
def daily_student_reminder():
    from app import create_app
    app, _ = create_app()

    with app.app_context():

        tomorrow = datetime.now().date() + timedelta(days=1)

        students = Student.query.all()

        for student in students:

            if student.placed:
                continue

            interviews = (
                Interview.query
                .join(Application)
                .filter(
                    Application.student_id == student.roll_no,
                    Interview.status == "Scheduled"
                )
                .all()
            )

            interviews = [
                interview
                for interview in interviews
                if interview.interview_datetime.date() == tomorrow
            ]

            eligible_drives = []

            eligibilities = Eligibility.query.filter_by(
                program_code=student.program_code,
                eligible_year=student.year_in_program
            ).all()

            for eligibility in eligibilities:

                if student.cgpa < eligibility.min_cgpa:
                    continue

                drive = eligibility.placement_drive

                if (
                    drive.status == "Approved"
                    and drive.application_deadline.date() == tomorrow
                ):

                    applied = Application.query.filter_by(
                        student_id=student.roll_no,
                        drive_id=drive.id
                    ).first()

                    if not applied:
                        eligible_drives.append(drive)

            if not interviews and not eligible_drives:
                continue

            msg = Message(
                subject="Placement Portal Daily Reminder",
                recipients=[student.user.email]
            )

            msg.html = render_template(
                "daily_reminder.html",
                student=student,
                interviews=interviews,
                drives=eligible_drives
            )

            mail.send(msg)

@celery.task(name="celery_app.export_student_history")
def export_student_history(student_roll):
    from app import create_app
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

@celery.task(name="celery_app.export_company_history")
def export_company_history(company_id):
    from app import create_app
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