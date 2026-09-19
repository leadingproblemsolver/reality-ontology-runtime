import type { ContinuityStore } from "./store.js";
import type {
  ContextPacket,
  GlobalState,
  Receipt,
  SyncResult,
  Transition,
  WorkstreamCapsule,
} from "./types.js";

function nowIso(): string {
  return new Date().toISOString();
}

function transitionSettled(state: GlobalState, id: string): boolean {
  return state.transitions.some((transition) => transition.id === id && transition.status === "settled");
}

function transitionEligible(state: GlobalState, transition: Transition): boolean {
  if (transition.status !== "pending") return false;
  if (!transition.dependsOn.every((id) => transitionSettled(state, id))) return false;
  const workstream = state.workstreams.find((entry) => entry.id === transition.workstreamId);
  if (!workstream || workstream.status !== "active") return false;
  return true;
}

function missionScore(transition: Transition, mission: string): number {
  const target = mission.trim().toLowerCase();
  if (!target) return transition.priority;
  const candidate = transition.mission.toLowerCase();
  const exact = candidate === target ? 1000 : 0;
  const contains = candidate.includes(target) || target.includes(candidate) ? 100 : 0;
  return exact + contains + transition.priority;
}

function currentTruthFor(workstream: WorkstreamCapsule, state: GlobalState): string[] {
  const truth = [`workstream_status=${workstream.status}`, `current_state=${workstream.currentState}`];
  if (workstream.lastVerifiedTransitionId) {
    const receipt = state.receipts.find((entry) => entry.transitionId === workstream.lastVerifiedTransitionId);
    truth.push(`last_verified_transition=${workstream.lastVerifiedTransitionId}`);
    if (receipt) truth.push(`last_receipt_proves=${receipt.proves}`);
  }
  if (workstream.blocker) truth.push(`blocker=${workstream.blocker}`);
  if (workstream.waitingUntil) truth.push(`waiting_until=${workstream.waitingUntil}`);
  return truth;
}

export async function sync(store: ContinuityStore): Promise<SyncResult> {
  const state = await store.load();
  return {
    active: state.workstreams.filter((entry) => entry.status === "active"),
    waiting: state.workstreams.filter((entry) => entry.status === "waiting"),
    blocked: state.workstreams.filter((entry) => entry.status === "blocked"),
    done: state.workstreams.filter((entry) => entry.status === "done"),
    unsettledTransitions: state.transitions.filter((entry) => entry.status !== "settled"),
    updatedAt: state.updatedAt,
  };
}

export async function route(store: ContinuityStore, mission: string): Promise<ContextPacket | null> {
  const state = await store.load();
  const eligible = state.transitions
    .filter((entry) => transitionEligible(state, entry))
    .sort((a, b) => missionScore(b, mission) - missionScore(a, mission));

  const transition = eligible[0];
  if (!transition) return null;

  const workstream = state.workstreams.find((entry) => entry.id === transition.workstreamId);
  if (!workstream) throw new Error(`transition ${transition.id} references missing workstream`);

  const chat = transition.chatId
    ? state.chats.find((entry) => entry.id === transition.chatId)
    : state.chats.find((entry) => entry.workstreamId === workstream.id && entry.operator === transition.operator);

  const evidenceRefs = [...new Set([
    ...transition.evidenceRefs,
    ...state.receipts
      .filter((entry) => state.transitions.some((t) => t.workstreamId === workstream.id && t.id === entry.transitionId))
      .map((entry) => `receipt:${entry.id}`),
  ])];

  return {
    mission,
    workstreamId: workstream.id,
    currentTruth: currentTruthFor(workstream, state),
    frozenDecisions: state.frozenDecisions,
    evidenceRefs,
    operator: transition.operator,
    chatReference: chat ? `${chat.title} [${chat.id}]` : null,
    toolRefs: transition.toolRefs ?? [],\n    artifactRefs: [...new Set([...workstream.artifactRefs, ...transition.artifactRefs])],
    nextAction: transition.action,
    doneWhen: transition.doneWhen,
    requiredReceipt: transition.receiptRequired,
    interruptionWakeCondition: transition.interruptionWakeCondition,
    transitionId: transition.id,
  };
}

export async function settle(store: ContinuityStore, receipt: Receipt): Promise<GlobalState> {
  if (!receipt.verified) throw new Error("receipt is not independently verified");
  if (!receipt.proves.trim()) throw new Error("receipt.proves is required");
  if (!receipt.source.trim()) throw new Error("receipt.source is required");

  const state = await store.load();
  const transition = state.transitions.find((entry) => entry.id === receipt.transitionId);
  if (!transition) throw new Error(`unknown transition ${receipt.transitionId}`);
  if (transition.status === "settled") {
    const duplicate = state.receipts.find((entry) => entry.transitionId === receipt.transitionId);
    if (duplicate) return state;
    throw new Error(`transition ${receipt.transitionId} already settled without receipt`);
  }
  if (!transitionEligible(state, transition) && transition.status !== "executed" && transition.status !== "prepared") {
    throw new Error(`transition ${receipt.transitionId} is not admissible for settlement from status=${transition.status}`);
  }

  transition.status = "settled";
  transition.settledAt = receipt.verifiedAt || nowIso();

  if (!state.receipts.some((entry) => entry.id === receipt.id)) state.receipts.push(receipt);

  const workstream = state.workstreams.find((entry) => entry.id === transition.workstreamId);
  if (!workstream) throw new Error(`transition ${transition.id} references missing workstream`);
  workstream.currentState = transition.toState;
  workstream.lastVerifiedTransitionId = transition.id;

  const remaining = state.transitions
    .filter((entry) => entry.workstreamId === workstream.id && entry.status === "pending")
    .filter((entry) => entry.dependsOn.every((id) => id === transition.id || transitionSettled(state, id)));

  if (remaining.length === 0) workstream.status = "done";

  state.updatedAt = nowIso();
  await store.save(state);
  return state;
}
