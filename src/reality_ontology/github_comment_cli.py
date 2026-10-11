"""Controlled GitHub comment command: PREPARE, APPROVE, EXECUTE.

Approval requires a local human typing the exact digest after inspecting the
payload. No ChatGPT/Claude conversation is treated as authorization.
"""
from __future__ import annotations
import argparse
import json
import sys

from .github_comment import packet, execute
from .store import RealityStore


def main(argv=None):
    p=argparse.ArgumentParser(description="Explicitly approved GitHub issue comment (never automated approval)")
    p.add_argument("--db", default=".runtime/reality.db")
    p.add_argument("--repo", required=True)
    p.add_argument("--issue", required=True, type=int)
    p.add_argument("--message-file", required=True)
    p.add_argument("operation", choices=["prepare", "approve", "execute"])
    args=p.parse_args(argv)
    try:
        with open(args.message_file, "r", encoding="utf-8") as f:
            body=f.read().rstrip("\r\n")
        spec=packet(args.repo,args.issue,body)
        if args.operation=="prepare":
            print(json.dumps(spec, indent=2))
            return 0
        if args.operation=="approve":
            print(json.dumps(spec,indent=2))
            print("APPROVAL FOR ONE EXACT GITHUB COMMENT. Type the full transition_id to approve:", file=sys.stderr)
            entry=input().strip()
            if entry != spec["transition_id"]:
                raise PermissionError("explicit exact-payload approval not supplied")
            with RealityStore(args.db) as store:
                actor=store.add_actor("local_explicit_human_approver")
                store.approve(spec["transition_id"],actor,decision="APPROVE")
            print(json.dumps({"status":"APPROVED_EXACT_PAYLOAD","transition_id":spec["transition_id"]}))
            return 0
        print(json.dumps(execute(args.db,spec),indent=2))
        return 0
    except (ValueError,PermissionError,OSError,RuntimeError,EOFError) as e:
        print(json.dumps({"status":"BLOCKED","error":str(e)}),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
