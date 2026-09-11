from pathlib import Path
from html import escape
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from app.schemas import BillingBreakdown
class NotificationDispatcher:
    def __init__(self, output_dir="output"): self.output=Path(output_dir); self.output.mkdir(parents=True,exist_ok=True)
    def render(self, appointment_id, patient_reference, doctor, specialty, starts_at, room, billing: BillingBreakdown, citations=()):
        refs=", ".join(citations) or "none"
        html=f"""<!doctype html><html><body><h1>APOLLO Appointment Confirmation</h1><p>SIMULATED notification</p><p>Appointment: {escape(str(appointment_id))}</p><p>Patient reference: {escape(str(patient_reference))}</p><p>Doctor: {escape(doctor)} ({escape(specialty)})</p><p>When: {escape(str(starts_at))}<br>Room: {escape(room)}</p><p>Subtotal: {billing.subtotal} {billing.currency}<br>Tax: {billing.tax} {billing.currency}<br>Total: {billing.total} {billing.currency}</p><p>Policy references: {escape(refs)}</p></body></html>"""
        hp=self.output/f"appointment-{appointment_id}.html"; hp.write_text(html,encoding="utf-8")
        pp=self.output/f"appointment-{appointment_id}.pdf"; c=canvas.Canvas(str(pp),pagesize=A4); y=800
        for line in [f"APOLLO APPOINTMENT CONFIRMATION (SIMULATED)",f"Appointment: {appointment_id}",f"Patient reference: {patient_reference}",f"Doctor: {doctor} ({specialty})",f"When: {starts_at}",f"Room: {room}",f"Subtotal: {billing.subtotal} {billing.currency}",f"Tax: {billing.tax} {billing.currency}",f"Total: {billing.total} {billing.currency}",f"Policy references: {refs}"]:
            c.drawString(50,y,line[:110]); y-=18
        c.save()
        return {"html":str(hp),"pdf":str(pp),"email":"SIMULATED","calendar":"SIMULATED","appointment_id":str(appointment_id)}
    def render_dual(self, appointment_id, patient_reference, patient_name, treatment, doctor, specialty, starts_at, room, billing, citations=()):
        base=self.render(appointment_id,patient_reference,doctor,specialty,starts_at,room,billing,citations)
        doctor_record={"doctor_name":doctor,"appointment_id":str(appointment_id),"patient_reference":str(patient_reference),"patient_name":patient_name,"treatment":treatment,"date":starts_at.date().isoformat(),"time":starts_at.time().isoformat(),"room":room,"doctor_email_status":"SIMULATED_SENT"}
        base.update({"patient_name":patient_name,"treatment":treatment,"patient_email_status":"SIMULATED_SENT","doctor_notification":doctor_record})
        return base


