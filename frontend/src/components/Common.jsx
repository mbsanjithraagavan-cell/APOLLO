import {Activity, AlertCircle, ArrowRight, HeartPulse} from 'lucide-react';
export function ErrorState({message}) {return message ? <div className="error" role="alert"><AlertCircle size={18}/><span>{message}</span></div> : null;}
export function LoadingState({text='Checking live availability…'}) {return <p className="loading" role="status"><Activity size={18}/>{text}</p>;}
export function TreatmentCard({treatment,onSelect}) {return <button className="treatment-card" onClick={onSelect}><HeartPulse aria-hidden="true"/><strong>{treatment.name}</strong><small>{treatment.specialty}</small><ArrowRight className="card-arrow" aria-hidden="true"/></button>;}
export function DoctorCard({doctor,onSelect}) {return <article className="doctor"><div><h4>{doctor.doctor_name}</h4><p>{doctor.specialty} · {doctor.location || 'Location to be confirmed'}</p></div><span>{doctor.available_slot_count} slots available</span><button onClick={onSelect}>Choose clinician <ArrowRight aria-hidden="true"/></button></article>;}
export function SystemStatus({health}) {return <div className="status" aria-label="Observed system status">{Object.entries(health?.services||{}).map(([key,value])=><span key={key} className={['reachable','loaded'].includes(value)?'on':'off'} title={value.replaceAll('_',' ')}>{key}: {value.replaceAll('_',' ')}</span>)}</div>;}

