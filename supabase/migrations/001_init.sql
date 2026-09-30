create table demo_sessions (
  id uuid primary key default gen_random_uuid(),
  consent_days int,                         -- 30 | 90 | 365
  connected_at timestamptz,
  created_at timestamptz default now()
);

create table user_labels (                  -- feature 6 answers
  session_id uuid references demo_sessions(id) on delete cascade,
  txn_id text,
  category text not null,
  note text,
  primary key (session_id, txn_id)
);

create table income_notes (                 -- feature 14
  session_id uuid references demo_sessions(id) on delete cascade,
  period_start date,
  note text not null,
  include_on_proof boolean default true,
  primary key (session_id, period_start)
);

create table proofs (                       -- features 16–17
  token text primary key,                   -- e.g. 7KQ4-M2X9
  session_id uuid references demo_sessions(id) on delete cascade,
  statement_no text not null,               -- e.g. ES-7KQ4M2X9
  snapshot jsonb not null,
  signature text not null,
  valid_until date not null,
  revoked boolean default false,
  open_count int default 0,
  last_opened_at timestamptz,
  created_at timestamptz default now()
);

alter table demo_sessions enable row level security;
alter table user_labels  enable row level security;
alter table income_notes enable row level security;
alter table proofs       enable row level security;
-- No public policies: only the backend (service-role key) reads and writes.
