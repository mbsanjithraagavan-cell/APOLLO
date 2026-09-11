import {useEffect,useState} from 'react';
import {HeartPulse} from 'lucide-react';
import {api} from './services/api';
import {SystemStatus,ErrorState} from './components/Common';
import {BookingWizard} from './components/BookingWizard';
import {BookingSuccess} from './components/BookingSuccess';
import {PolicyAssistant} from './components/PolicyAssistant';
import {AgentFlow} from './components/AgentFlow';
import {AgentBooking} from './components/AgentBooking';
export default function App(){
 const [tab,setTab]=useState('agent'),[health,setHealth]=useState(null),[error,setError]=useState(''),[confirmation,setConfirmation]=useState(null),[removed,setRemoved]=useState(null),[requestId,setRequestId]=useState(null);
 useEffect(()=>{api('/health').then(setHealth).catch(e=>setError(e.message));},[]);
 function booked(result,gone){setConfirmation(result);setRemoved(gone);}
 useEffect(()=>{if(requestId)api('/health').then(setHealth).catch(()=>{});},[requestId]);
 return <main><header><div className="brand"><span><HeartPulse aria-hidden="true"/></span><div><h1>APOLLO</h1><p>Agentic Patient & Outpatient Logistics Orchestrator</p></div></div><SystemStatus health={health}/></header><nav aria-label="Main navigation">{[['agent','Book with APOLLO'],['book','Browse Manually'],['ask','Ask APOLLO'],['confirmation','My Confirmation'],['activity','Agent Activity']].map(([id,label])=><button key={id} className={tab===id?'active':''} aria-current={tab===id?'page':undefined} onClick={()=>setTab(id)}>{label}</button>)}</nav><ErrorState message={error}/>{tab==='agent'&&<AgentBooking onBooked={booked} onRequest={setRequestId}/>}<div hidden={tab!=='book'}><BookingWizard onBooked={booked} onRequest={setRequestId}/></div>{tab==='ask'&&<PolicyAssistant onRequest={setRequestId}/>} {tab==='confirmation'&&<BookingSuccess result={confirmation} removed={removed}/>} {tab==='activity'&&<AgentFlow requestId={requestId}/>}<footer>APOLLO · Fictional outpatient demonstration · Local model resources</footer></main>;
}
