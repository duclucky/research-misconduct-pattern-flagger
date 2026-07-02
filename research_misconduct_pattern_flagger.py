# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *

import json
import typing
from dataclasses import dataclass
# Contract to screen healthcare administration research methods for patterns that warrant further investigation, acting as a preliminary screen before ethics board review.

@allow_storage
@dataclass
class Ruling:
    subject_key: str
    verdict: str
    confidence: bigint
    reason: str
    flags: str
    inputs_json: str

class Contract(gl.Contract):
    rulings: TreeMap[str, Ruling]
    subject_history: TreeMap[str, DynArray[str]]
    next_id: bigint

    def __init__(self):
        self.next_id = bigint(0)

    @gl.public.view
    def get_count(self) -> int:
        return int(self.next_id)

    @gl.public.view
    def get_ruling(self, ruling_id: str) -> str:
        try:
            r = self.rulings[str(ruling_id)]
            return json.dumps({
                "subject_key": r.subject_key,
                "verdict": r.verdict,
                "confidence": int(r.confidence),
                "reason": r.reason,
                "flags": json.loads(r.flags),
                "inputs_json": json.loads(r.inputs_json)
            }, ensure_ascii=False)
        except Exception:
            return "{}"

    @gl.public.write
    def screen(self, study_description_text: str) -> None:
        if not study_description_text or not study_description_text.strip():
            raise gl.vm.UserError("study_description_text must not be empty")

        if len(study_description_text) > 6000:
            val = study_description_text[:6000] + "... (truncated)"
        else:
            val = study_description_text.strip()
            
        def leader_fn():
            prompt = f"""You are a healthcare administration ethics preliminary screener.
Read this study's methods description and flag patterns that warrant further investigation (e.g., impossible timelines, lack of proper consent mentions, statistical impossibilities).
Do NOT conclude misconduct, only flag patterns.
INPUT: {val}
Respond ONLY as JSON: {{"verdict":"FLAGGED"|"CLEAN"|"UNVERIFIABLE","confidence":<0-100>,"reason":"...","flags":["flag1","flag2"]}}"""
            res = gl.nondet.exec_prompt(prompt, response_format="json")
            
            verdict_raw = str(res.get("verdict", "")).upper()
            if verdict_raw.startswith("F"):
                verdict = "FLAGGED"
            elif verdict_raw.startswith("C"):
                verdict = "CLEAN"
            else:
                verdict = "UNVERIFIABLE"
                
            conf = max(0, min(100, int(res.get("confidence", 0))))
            
            flags_raw = res.get("flags", [])
            if isinstance(flags_raw, list):
                flags_list = [str(f) for f in flags_raw]
            else:
                flags_list = []
                
            if verdict == "FLAGGED" and not flags_list:
                verdict = "UNVERIFIABLE"
                conf = 0
                
            return json.dumps({
                "verdict": verdict, 
                "confidence": conf,
                "reason": str(res.get("reason", ""))[:400],
                "flags": flags_list
            }, sort_keys=True)

        def validator_fn(leader_res: typing.Any) -> bool:
            if not isinstance(leader_res, gl.vm.Return):
                return False
            try:
                leader = json.loads(leader_res.calldata)
            except Exception:
                return False
            mine = json.loads(leader_fn())
            
            if leader.get("verdict") != mine.get("verdict"):
                return False
                
            band = lambda c: 0 if c < 35 else (1 if c < 80 else 2)
            if band(leader.get("confidence", 0)) != band(mine.get("confidence", 0)):
                return False
                
            if leader.get("verdict") == "FLAGGED":
                leader_flags = leader.get("flags", [])
                mine_flags = mine.get("flags", [])
                if not leader_flags or not mine_flags:
                    return False
                    
            return True

        raw = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
        payload = json.loads(raw)
        
        subject_key = str(hash(val))[:16]
        
        ruling_id = str(self.next_id)
        
        ruling = Ruling(
            subject_key=subject_key,
            verdict=payload.get("verdict", "UNVERIFIABLE"),
            confidence=bigint(payload.get("confidence", 0)),
            reason=payload.get("reason", ""),
            flags=json.dumps(payload.get("flags", [])),
            inputs_json=json.dumps({"study_description_text": study_description_text})
        )
        
        self.rulings[ruling_id] = ruling
        
        if subject_key not in self.subject_history:
            self.subject_history[subject_key] = [ruling_id]
        else:
            hist = self.subject_history[subject_key]
            hist.append(ruling_id)
            self.subject_history[subject_key] = hist
            
        self.next_id += bigint(1)
