from pydantic import BaseModel, ConfigDict
TREATMENTS={'General Consultation':'general','Heart Consultation':'cardiology','Skin Consultation':'dermatology'}
def specialty_for_treatment(treatment:str)->str:
    key=next((k for k in TREATMENTS if k.lower()==treatment.strip().lower()),None)
    if not key: raise ValueError('unsupported_treatment')
    return TREATMENTS[key]
class TreatmentSelection(BaseModel):
    model_config=ConfigDict(extra='forbid',frozen=True)
    treatment:str
    specialty:str
