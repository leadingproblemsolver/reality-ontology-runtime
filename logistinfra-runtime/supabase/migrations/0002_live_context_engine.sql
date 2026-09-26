create table if not exists chat_registry (
  id text primary key,
  title text not null,
  purpose text not null,
  operator text not null,
  workstream_id text not null,
  invoke_when jsonb not null default '[]'::jsonb,
  artifacts jsonb not null default '[]'::jsonb,
  latest_state text not null default '',
  source_refs jsonb not null default '[]'::jsonb,
  updated_at timestamptz not null default now()
);

create table if not exists workstream_capsules (
  id text primary key,
  objective text not null,
  status text not null check (status in ('active','waiting','blocked','done')),
  current_state text not null,
  priority integer not null default 0,
  operator text not null,
  chat_id text references chat_registry(id) on delete set null,
  artifact_refs jsonb not null default '[]'::jsonb,
  blocker text,
  waiting_until timestamptz,
  last_verified_transition_id text,
  updated_at timestamptz not null default now()
);

create table if not exists continuity_transitions (
  id text primary key,
  workstream_id text not null references workstream_capsules(id) on delete cascade,
  mission text not null,
  from_state text not null,
  to_state text not null,
  action text not null,
  operator text not null,
  owner text not null,
  status text not null check (status in ('pending','prepared','executed','settled','blocked','waiting')),
  priority integer not null default 0,
  receipt_required text not null,
  done_when text not null,
  interruption_wake_condition text not null,
  chat_id text references chat_registry(id) on delete set null,
  artifact_refs jsonb not null default '[]'::jsonb,
  evidence_refs jsonb not null default '[]'::jsonb,
  depends_on jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now(),
  settled_at timestamptz
);

alter table workstream_capsules
  drop constraint if exists workstream_capsules_last_verified_transition_id_fkey;

alter table workstream_capsules
  add constraint workstream_capsules_last_verified_transition_id_fkey
  foreign key (last_verified_transition_id)
  references continuity_transitions(id)
  on delete set null;

create table if not exists continuity_receipts (
  id text primary key,
  transition_id text not null references continuity_transitions(id) on delete cascade,
  source text not null,
  observation jsonb not null,
  proves text not null,
  does_not_prove text,
  verified boolean not null default false,
  verified_at timestamptz not null,
  created_at timestamptz not null default now(),
  unique (transition_id)
);

create table if not exists global_state (
  id text primary key default 'canonical' check (id = 'canonical'),
  goals jsonb not null default '[]'::jsonb,
  frozen_decisions jsonb not null default '[]'::jsonb,
  updated_at timestamptz not null default now()
);

alter table chat_registry enable row level security;
alter table workstream_capsules enable row level security;
alter table continuity_transitions enable row level security;
alter table continuity_receipts enable row level security;
alter table global_state enable row level security;
