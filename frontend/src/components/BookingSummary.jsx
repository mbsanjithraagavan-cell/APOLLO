import {money,time} from '../services/api';
export function BookingSummary({preview}) {
 return <div className="summary"><p><span>Treatment</span>{preview.treatment}</p><p><span>Clinician</span>{preview.doctor.doctor_name}</p><p><span>Specialty</span>{preview.specialty}</p><p><span>Starts</span>{time(preview.slot.starts_at)}</p><p><span>Ends</span>{time(preview.slot.ends_at)}</p><p><span>Location</span>{preview.room}</p><hr/><p><span>Consultation</span>{money(preview.billing.subtotal)}</p><p><span>Tax (5%)</span>{money(preview.billing.tax)}</p><h2><span>Total</span>{money(preview.billing.total)}</h2><small>Calculated by APOLLO from the clinic tariff.</small></div>;
}

