import argparse, json
from uuid import UUID, uuid4
from app.config import Settings

def main():
    p=argparse.ArgumentParser(description='APOLLO local demo'); p.add_argument('--demo',choices=['booking','safety','rag']); p.add_argument('--reset-demo',action='store_true'); a=p.parse_args()
    if a.demo=='safety':
        from app.safety import early_safety
        print(json.dumps(early_safety('I have chest pain').model_dump())); return
    if a.demo=='rag':
        try:
            from app.services.policy import PolicyService
            from app.agents import PolicyRAGAgent
            from app.rag import answer_policy
            s=Settings.from_environment()
            if not s.database_url: raise RuntimeError('database_url_not_configured')
            service=PolicyService(s.database_url.get_secret_value(),str(s.embedder_dir),s.embedding_dimension)
            agent=PolicyRAGAgent({'query_clinic_policies': lambda q: service.query(q,s.rag_top_k)})
            print(json.dumps(answer_policy('What preparation is required before this outpatient procedure?',uuid4(),agent),default=str,indent=2)); return
        except Exception as e:
            print(json.dumps({'status':'blocked','error':type(e).__name__,'reason':'RAG demo could not access configured local services'})); return
    if a.demo=='booking':
        from app.runtime import ApolloRuntime
        runtime=ApolloRuntime()
        if a.reset_demo: print(json.dumps({'reset':runtime.reset_fictional_demo()}))
        print(json.dumps(runtime.book(UUID('00000000-0000-0000-0000-000000000011'),'cardiology'),default=str,indent=2)); return
    s=Settings.from_environment(); print(json.dumps({'project':'APOLLO','phase':'E+F','booking_enabled':True,'model_dir':str(s.model_dir),'embedder_dir':str(s.embedder_dir),'embedding_dimension':s.embedding_dimension},indent=2))
if __name__=='__main__': main()
