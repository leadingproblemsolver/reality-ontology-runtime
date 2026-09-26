create table if not exists goals (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  status text not null default 'active',
  created_at timestamptz not null default now()
);

create table if not exists signals (
  id uuid primary key default gen_random_uuid(),
  source text not null,
  source_id text not null,
  source_url text,
  observed_at timestamptz not null default now(),
  observation jsonb not null,
  created_at timestamptz not null default now(),
  unique (source, source_id)
);

create table if not exists opportunities (
  id uuid primary key default gen_random_uuid(),
  signal_id uuid not null references signals(id) on delete cascade,
  target text,
  problem text,
  score numeric,
  rationale jsonb not null default '{}'::jsonb,
  uncertainty text,
  recommended_action text,
  status text not null default 'proposed',
  created_at timestamptz not null default now(),
  unique (signal_id)
);

create table if not exists executions (
  id uuid primary key default gen_random_uuid(),
  opportunity_id uuid references opportunities(id) on delete set null,
  action text not null,
  expected_transition text,
  status text not null default 'prepared',
  approval_required boolean not null default true,
  started_at timestamptz,
  completed_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists approvals (
  id uuid primary key default gen_random_uuid(),
  execution_id uuid not null references executions(id) on delete cascade,
  decision text not null,
  payload_hash text,
  decided_at timestamptz not null default now()
);

create table if not exists evidence (
  id uuid primary key default gen_random_uuid(),
  execution_id uuid references executions(id) on delete set null,
  signal_id uuid references signals(id) on delete set null,
  source text not null,
  observation jsonb not null,
  proves text,
  does_not_prove text,
  observed_at timestamptz not null default now(),
  created_at timestamptz not null default now()
);

alter table goals enable row level security;
alter table signals enable row level security;
alter table opportunities enable row level security;
alter table executions enable row level security;
alter table approvals enable row level security;
alter table evidence enable row level security;
