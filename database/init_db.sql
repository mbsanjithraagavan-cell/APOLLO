CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE TABLE IF NOT EXISTS doctors (id uuid PRIMARY KEY, name text NOT NULL, specialty text NOT NULL, clinic text NOT NULL, active boolean NOT NULL DEFAULT true);
CREATE TABLE IF NOT EXISTS patients (id uuid PRIMARY KEY, reference_code text UNIQUE NOT NULL, display_name text NOT NULL);
CREATE TABLE IF NOT EXISTS slots (id uuid PRIMARY KEY, doctor_id uuid NOT NULL REFERENCES doctors(id), starts_at timestamptz NOT NULL, ends_at timestamptz NOT NULL, is_booked boolean NOT NULL DEFAULT false, UNIQUE (doctor_id, starts_at));
CREATE TABLE IF NOT EXISTS tariffs (code text PRIMARY KEY, description text NOT NULL, amount numeric(12,2) NOT NULL CHECK (amount >= 0), currency char(3) NOT NULL DEFAULT 'INR');
CREATE TABLE IF NOT EXISTS clinic_policies (id uuid PRIMARY KEY, policy_id text NOT NULL, revision text NOT NULL, category text NOT NULL DEFAULT 'general', content text NOT NULL, embedding vector(384), UNIQUE(policy_id, revision));
CREATE TABLE IF NOT EXISTS policy_chunks (chunk_id uuid PRIMARY KEY, policy_id text NOT NULL, revision text NOT NULL, category text NOT NULL DEFAULT 'general', content text NOT NULL, embedding vector(384));
CREATE TABLE IF NOT EXISTS appointments (id uuid PRIMARY KEY, patient_id uuid NOT NULL REFERENCES patients(id), slot_id uuid NOT NULL UNIQUE REFERENCES slots(id), tariff_code text NOT NULL REFERENCES tariffs(code), amount numeric(12,2) NOT NULL, currency char(3) NOT NULL, idempotency_key uuid UNIQUE NOT NULL, created_at timestamptz NOT NULL DEFAULT now());
INSERT INTO doctors VALUES ('00000000-0000-0000-0000-000000000001','Dr. Ada Rao','cardiology','Apollo Central',true) ON CONFLICT DO NOTHING;
INSERT INTO doctors VALUES ('00000000-0000-0000-0000-000000000002','Dr. Noor Khan','dermatology','Apollo Central',true) ON CONFLICT DO NOTHING;
INSERT INTO patients VALUES ('00000000-0000-0000-0000-000000000011','PATIENT-001','Fictional Patient One') ON CONFLICT DO NOTHING;
INSERT INTO tariffs VALUES ('CONSULT','Outpatient consultation',350.00,'INR') ON CONFLICT DO NOTHING;
INSERT INTO slots VALUES ('00000000-0000-0000-0000-000000000101','00000000-0000-0000-0000-000000000001',now()+interval '1 day',now()+interval '1 day 30 minutes',false) ON CONFLICT DO NOTHING;
INSERT INTO slots VALUES ('00000000-0000-0000-0000-000000000102','00000000-0000-0000-0000-000000000002',now()+interval '1 day 1 hour',now()+interval '1 day 1 hour 30 minutes',false) ON CONFLICT DO NOTHING;

