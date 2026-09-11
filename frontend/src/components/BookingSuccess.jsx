import {CheckCircle} from 'lucide-react';
import {BookingSummary} from './BookingSummary';
export function BookingSuccess({result,removed}) {
 if (!result) return <section className="empty"><CheckCircle/><h2>Your confirmation will appear here</h2><p>Choose a treatment and confirm an appointment to get started.</p></section>;
 const notification=result.notification;
 return <section className="success"><CheckCircle aria-hidden="true"/><h2>Appointment confirmed</h2><p className="appointment-id">Reference: {result.appointment_id}</p><BookingSummary preview={result}/><div className="notify"><span>Patient notification <b>{notification.patient_email_status || 'Not available'}</b></span><span>Doctor notification <b>{notification.doctor_notification?.doctor_email_status || 'Not available'}</b></span></div><p>Email delivery is simulated for this fictional demo.</p>{removed===true&&<p className="verified">Live availability refreshed: your booked slot is no longer listed.</p>}{removed===false&&<p role="alert">Booking succeeded, but availability needs review.</p>}{removed===null&&<p>Booking succeeded. Availability refresh has not been verified.</p>}<div className="file-actions">{notification.html&&<a href={notification.html} target="_blank" rel="noreferrer">View confirmation</a>}{notification.pdf&&<a href={notification.pdf} target="_blank" rel="noreferrer">View PDF</a>}</div></section>;
}

