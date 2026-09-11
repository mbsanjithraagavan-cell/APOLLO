import argparse,json
from uuid import UUID
from app.config import Settings

def main():
 p=argparse.ArgumentParser(description='APOLLO booking demo'); p.add_argument('--demo',choices=['booking','safety','rag']); p.add_argument('--reset-demo',action='store_true'); a=p.parse_args()
 if a.demo=='safety':
  from app.safety import early_safety; print(json.dumps(early_safety('I have chest pain').model_dump())); return
 if a.demo=='booking':
  from app.runtime import ApolloRuntime
  rt=ApolloRuntime()
  if a.reset_demo: print('Demo state reset') ; rt.reset_fictional_demo()
  treatments=['General Consultation','Heart Consultation','Skin Consultation']; print('Treatments:\n'+'\n'.join(f'{i+1}. {x}' for i,x in enumerate(treatments))); treatment='Heart Consultation'; print(f'\nSelected treatment: {treatment}')
  specialty='cardiology'; doctors=rt.discover_doctors(specialty); print('Available doctors:'); [print(f"1. {d['doctor_name']} — {d['specialty'].title()} — {d['available_slot_count']} slots available") for d in doctors]
  if not doctors: print(json.dumps({'status':'no_available_doctors'})); return
  doctor=doctors[0]; slots=rt.discover_slots(doctor['doctor_id']); print('Available slots:'); [print(f"{i+1}. {x['date']} {x['start_time']} - {x['end_time']}") for i,x in enumerate(slots)]
  if not slots: print(json.dumps({'status':'no_available_slots'})); return
  print('Selected slot: 1\nBilling calculated\nConfirm booking? yes'); result=rt.book(UUID('00000000-0000-0000-0000-000000000011'),specialty,True,UUID(str(slots[0]['slot_id']))); print(json.dumps(result,default=str,indent=2)); print('PATIENT: SIMULATED_SENT\nDOCTOR: SIMULATED_SENT'); print('Availability after booking:',len(rt.discover_slots(doctor['doctor_id']))); return
 s=Settings.from_environment(); print(json.dumps({'project':'APOLLO','booking_enabled':True,'model_dir':str(s.model_dir)},indent=2))
if __name__=='__main__': main()

