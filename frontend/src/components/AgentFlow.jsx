import {useEffect,useState} from 'react';
import {api} from '../services/api';
import {ErrorState} from './Common';
export function AgentFlow({requestId}) {
 const [events,setEvents]=useState([]),[error,setError]=useState('');
 useEffect(()=>{setEvents([]);setError('');if(requestId)api('/traces/'+requestId).then(r=>setEvents(r.events)).catch(e=>setError(e.message));},[requestId]);
 return <section className="activity"><h2>Agent activity</h2><p>Completed steps recorded by the backend for the latest request.</p><ErrorState message={error}/>{events.length?<ol className="trace-list">{events.map((e,i)=><li key={i}><strong>{e.node.replaceAll('_',' ')}</strong><time>{new Date(e.occurred_at).toLocaleTimeString()}</time></li>)}</ol>:<p>No execution events yet. Complete a booking or ask a policy question.</p>}<p className="agents">Existing agent roles: Booking / Discovery · Allocator · Policy RAG · Safety Critic</p></section>;
}

