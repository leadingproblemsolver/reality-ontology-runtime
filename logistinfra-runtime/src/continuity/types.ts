export type WorkstreamStatus = "active" | "waiting" | "blocked" | "done";
export type TransitionStatus = "pending" | "prepared" | "executed" | "settled" | "blocked" | "waiting";

export interface ChatRegistryEntry {
  id: string;
  title: string;
  purpose: string;
  operator: string;
  workstreamId: string;
  invokeWhen: string[];
  artifacts: string[];
  latestState: string;
  sourceRefs: string[];
}

export interface WorkstreamCapsule {
  id: string;
  objective: string;
  status: WorkstreamStatus;
  currentState: string;
  priority: number;
  operator: string;
  chatId?: string | null;
  artifactRefs: string[];
  blocker?: string | null;
  waitingUntil?: string | null;
  lastVerifiedTransitionId?: string | null;
}

export interface Transition {
  id: string;
  workstreamId: string;
  mission: string;
  fromState: string;
  toState: string;
  action: string;
  operator: string;
  owner: string;
  status: TransitionStatus;
  priority: number;
  receiptRequired: string;
  doneWhen: string;
  interruptionWakeCondition: string;
  chatId?: string | null;
  artifactRefs: string[];
  evidenceRefs: string[];
  dependsOn: string[];
  createdAt: string;
  settledAt?: string | null;
}

export interface Receipt {
  id: string;
  transitionId: string;
  source: string;
  observation: Record<string, unknown>;
  proves: string;
  doesNotProve?: string | null;
  verified: boolean;
  verifiedAt: string;
}

export interface GlobalState {
  version: 1;
  updatedAt: string;
  goals: string[];
  frozenDecisions: string[];
  chats: ChatRegistryEntry[];
  workstreams: WorkstreamCapsule[];
  transitions: Transition[];
  receipts: Receipt[];
}

export interface ContextPacket {
  mission: string;
  workstreamId: string;
  currentTruth: string[];
  frozenDecisions: string[];
  evidenceRefs: string[];
  operator: string;
  chatReference: string | null;
  artifactRefs: string[];
  nextAction: string;
  doneWhen: string;
  requiredReceipt: string;
  interruptionWakeCondition: string;
  transitionId: string;
}

export interface SyncResult {
  active: WorkstreamCapsule[];
  waiting: WorkstreamCapsule[];
  blocked: WorkstreamCapsule[];
  done: WorkstreamCapsule[];
  unsettledTransitions: Transition[];
  updatedAt: string;
}
