# SHARED CONTEXT - GenLayer Intelligent Contract (paste ONCE at the top of the Antigravity session, as system/project instructions)

You are an AI coding agent tasked with building **GenLayer Intelligent Contracts**
in Python for submission to the **"Intelligent Contracts"** category (Builder
track, 0-300 points) of the GenLayer Builder Points Program
(portal.genlayer.foundation). Read this whole context carefully; the 100 tasks
that follow all depend on it and will NOT repeat this material.

## What the reviewers reward (official category description)
"Submit standalone GenLayer Intelligent Contracts that are strong enough to be
useful, reusable, or educational for other builders. We're looking for
high-quality contract primitives and meaningful use cases: contracts with real
GenLayer consensus logic, clear state design, thoughtful validators or
equivalence checks, and a use case that would still matter beyond a one-off
demo. This category is NOT for basic examples, hello-world contracts, simple
storage, thin LLM wrappers, format-only validators, boilerplate forks, or
generic 'AI decides X' demos. A strong submission should include readable
source, a clear explanation of the contract's purpose, how consensus is used,
and enough documentation or tests for reviewers and builders to understand the
primitive."

Every contract you produce MUST clear that bar. Treat the reference
"WebComplianceOracle" (below) as the minimum quality floor, not the ceiling:
deep state design with an append-only ruling history, a real custom validator
that checks the MEANING of the verdict (not JSON shape), and full edge-case
handling.

## 1. What GenLayer is (required background)
GenLayer is a Layer-1 blockchain that places AI at the consensus layer. Every
validator runs its own LLM; the validator network acts as a decentralized "AI
jury" that votes and converges on a shared result even for **subjective**
decisions. The consensus mechanism is called **Optimistic Democracy**: one
validator acts as the leader and proposes a result; the other validators
independently re-run the work and vote to agree or disagree. An Intelligent
Contract is a smart contract written in **Python** (not Solidity), a class that
inherits `gl.Contract`, able to call an LLM and read the live web from inside
contract logic - things traditional smart contracts cannot do.

## 2. Equivalence Principle - the consensus mechanism your contract MUST truly use
This is the single most important axis. There are four ways for validators to
"agree":
- `gl.eq_principle.strict_eq(fn)` - agree only if results are byte-identical.
  Use for a bool / normalized number.
- `gl.eq_principle.prompt_comparative(fn, principle)` - validators use NLP to
  check whether two outputs are equivalent under `principle`.
- `gl.eq_principle.prompt_non_comparative(fn, *, task, criteria)` - validators
  do NOT re-run the task; they only check the leader's output meets `criteria`.
- **`gl.vm.run_nondet_unsafe(leader_fn, validator_fn)`** - YOU write
  `validator_fn(leader_result) -> bool`. This is the most powerful option and is
  the REQUIRED mechanism for all 100 tasks below (unless a task explicitly says
  to use strict_eq for a pure bool).

**The validator MUST check MEANING (the verdict plus a confidence band), NEVER
just JSON shape / key presence / schema.** If two validators can reach different
verdicts and both still pass, that is a CRITICAL DEFECT and the number-one
reason submissions get rejected. A "format-only validator" is an automatic fail.

## 3. What gets a contract REJECTED (avoid absolutely)
- Hello-world, plain simple storage.
- **Thin LLM wrapper**: just wraps one LLM call and returns it, with no state
  design and no real validator.
- **Format-only validator**: only checks the JSON is valid / has the right keys,
  not the content / conclusion.
- Boilerplate fork (e.g. Wizard of Coin) with names changed.
- Generic "AI decides X" demo with no reusable primitive and no consensus depth.
- A full app with a frontend (that belongs to a different category).

## 4. What earns a HIGH score
- **Standalone**: valuable without any UI.
- Non-determinism is the CORE: remove the LLM/web part and the primitive becomes
  meaningless.
- **Custom validator** that checks the meaning of the result, explained clearly
  in the docs under "how consensus is used".
- **Deep state design**: `@allow_storage @dataclass` structs, `bigint` for
  numbers, `TreeMap[str, ...]` for maps, an explicit state lifecycle, and an
  append-only history so past rulings are auditable.
- **Edge cases branch explicitly and raise UserError** where appropriate (see
  section 7).
- **Generalized** into a reusable primitive (parameterized inputs, nothing
  hardcoded to one situation).
- **README + tests**: purpose, public API, how consensus works, usage example,
  happy-path + edge-case tests.

## 5. MANDATORY skeleton for EVERY contract file (.py)
```python
# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *

import json
import typing
from dataclasses import dataclass
# Describe the contract's purpose HERE (AFTER the import), ASCII only.


@allow_storage
@dataclass
class Ruling:                 # custom storage struct - one immutable ruling record
    subject_key: str          # what this ruling is about (echoed inputs / a stable key)
    verdict: str
    confidence: bigint        # persisted numbers are ALWAYS bigint, never int/u256
    reason: str
    inputs_json: str          # echo of all inputs for a full audit trail


class Contract(gl.Contract):  # MUST be named "Contract", inherits gl.Contract
    rulings: TreeMap[str, Ruling]        # ruling_id (str) -> Ruling
    subject_history: TreeMap[str, DynArray[str]]  # subject_key -> list of ruling_ids (append-only)
    next_id: bigint

    def __init__(self):
        self.next_id = bigint(0)         # do NOT reassign TreeMap()/DynArray() here

    @gl.public.view
    def get_count(self) -> int:
        return int(self.next_id)

    @gl.public.write
    def adjudicate(self, some_input: str) -> None:
        if not some_input or not some_input.strip():
            raise gl.vm.UserError("some_input must not be empty")

        val = some_input.strip()

        def leader_fn():
            # web reads / LLM calls only inside this inner fn (captured by closure)
            prompt = f\"\"\"You are an impartial adjudicator.
INPUT: {val}
Respond ONLY as JSON: {{"verdict":"PASS"|"FAIL","confidence":<0-100>,"reason":"..."}}\"\"\"
            res = gl.nondet.exec_prompt(prompt, response_format="json")
            verdict = "PASS" if str(res.get("verdict", "")).upper().startswith("P") else "FAIL"
            conf = max(0, min(100, int(res.get("confidence", 0))))
            return json.dumps({"verdict": verdict, "confidence": conf,
                               "reason": str(res.get("reason", ""))[:400]}, sort_keys=True)

        def validator_fn(leader_res: typing.Any) -> bool:
            if not isinstance(leader_res, gl.vm.Return):
                return False
            try:
                leader = json.loads(leader_res.calldata)
            except Exception:
                return False
            mine = json.loads(leader_fn())          # independent re-run
            if leader.get("verdict") != mine.get("verdict"):
                return False                         # different CONCLUSION -> no consensus
            band = lambda c: 0 if c < 35 else (1 if c < 80 else 2)
            return band(leader.get("confidence", 0)) == band(mine.get("confidence", 0))

        raw = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
        payload = json.loads(raw)
        # deterministically write state from payload, append to history, bump next_id
```

## 6. 27 TECHNICAL RULES (violating any is a broken deploy or broken consensus)
1. Line 1 of the file MUST be `# v0.2.16`; line 2 is the `Depends` comment.
   Missing -> `Contract Queues not found`.
2. Do NOT reassign `TreeMap()`/`DynArray()` in `__init__` (GenVM auto-inits them
   empty). Reassigning -> `AssertionError: TreeMap <- TreeMap`. Furthermore, you
   CANNOT instantiate `DynArray()` directly anywhere in your code (raises
   `TypeError: this class can't be instantiated by user`). To initialize a nested
   array inside a `TreeMap`, assign a standard Python list (e.g.
   `my_map[key] = [val]`); GenVM will automatically cast it to a `DynArray`.
3. NO `float` in a public method signature - use `int` (multiply by 100 for
   cents).
4. Valid public-method types ONLY: `str, bool, bytes, int`, sized ints
   (`u8..u256`, `i8..i256`), `Address`, `DynArray[T]`, `TreeMap[K,V]`. Forbidden:
   `float, list[T], dict[K,V]`, un-wrapped custom classes.
5. Storage uses `TreeMap`/`DynArray`, NOT `dict`/`list`. Only fully instantiated
   generics (`TreeMap[str,u256]` ok, bare `TreeMap` not).
6. The class MUST be named `Contract` and inherit `gl.Contract`. One Contract
   subclass per module.
7. Every `gl.nondet.*` call MUST be inside an inner function, invoked via
   `gl.eq_principle.*` or `gl.vm.run_nondet_unsafe(leader_fn, validator_fn)`.
   Calling it directly in the method body crashes.
8. Only `from genlayer import *`. NEVER `import genlayer as gl` (shadows the
   sandbox).
9. Persisted numeric fields MUST be `bigint`, never `u256`/`int`.
10. Send GEN via `gl.get_contract_at(addr).emit_transfer(value=u256(amount))`
    (there is no `gl.eth.send_value`).
11. Custom storage structs MUST use `@allow_storage @dataclass`.
12. `TreeMap` keys MUST be `str` (convert `str(id)` / hex at the boundary).
13. Convert `Address` to `str` defensively: `try: a.as_hex except: str(a)`.
14. **The contract file MUST be pure ASCII - NOT a single non-ASCII character
    anywhere, including comments.** Forbidden: em dash, en dash, curly quotes,
    unicode arrows (use `->`), accented characters, emoji, non-breaking space.
    Violation -> `Could not load contract schema` (a schema error, NOT a runtime
    error - easy to misdiagnose). Put any non-English notes in the README, never
    in the .py. Scan before considering it done:
    ```bash
    python3 -c 'import sys
    for i,l in enumerate(open(sys.argv[1],encoding="utf-8"),1):
        bad=[c for c in l if ord(c)>127]
        if bad: print(f"Line {i}: {bad!r}  {l.strip()}")' contracts/your_contract.py
    ```
    No output = clean.
15. `from genlayer import *` SHOULD be on line 3 (right under the two
    version/depends lines). Do NOT insert a long comment block between the header
    and the import; put long descriptions AFTER the import.
16. LLM prompts must state the role + criteria + output format, and demand JSON
    ONLY, no markdown fences. With `response_format="json"` GenLayer returns a
    dict already; with `response_format="text"` strip fences defensively.
17. In a custom validator, put ONLY the decision (verdict + confidence band) into
    what gets compared; keep free-form prose OUT of the comparison to avoid false
    consensus failures caused by wording differences.
18. When returning JSON strings from public view methods, use `ensure_ascii=False` in `json.dumps()` (e.g., `json.dumps(data, ensure_ascii=False)`). This prevents Unicode characters (like Vietnamese) from being escaped into `\uXXXX`, ensuring readable output in GenLayer Studio while keeping the `.py` source file itself pure ASCII.

## 7. Edge-case principles that apply to EVERY contract (do not repeat per task, but always implement)
- Empty / structurally invalid input (e.g. a URL not starting with http/https,
  an empty string) -> `raise gl.vm.UserError("...")` IMMEDIATELY, before entering
  the nondet block.
- Failures at RUNTIME (web page fails to load, LLM returns broken JSON, empty
  content) -> do NOT crash - return the lowest / most neutral verdict band
  available (e.g. "PARTIAL"/"NEEDS_REVIEW"/"UNVERIFIABLE") with low confidence
  and a reason explaining why, then still store the record normally.
- Oversized input -> truncate to a safe limit (e.g. 6000 chars) before putting it
  in the prompt, to avoid blowing the token budget.
- Every write call creates a NEW ruling record (never silently overwrites an old
  one), unless the task explicitly defines a separate "recheck"/status-update
  method.
- Every ruling appends to a per-subject history so callers can audit how a
  subject's verdict evolved over time.

## 8. Safety constraints
- Cybersecurity contracts (tasks 81-90): the contract may ONLY classify / rate
  based on the provided text description. It must NEVER ask the LLM to generate
  exploit code, attack payloads, concrete attack instructions, or real phishing
  content. The prompt must explicitly bound the LLM to "classify/rate only, do
  not produce attack content".
- Task 95 (ArtStyleInfringementJudge): compare only textual descriptions of
  style; never ask the LLM to reproduce or verbatim-describe copyrighted artwork.

## 9. Recommended deploy & verification (do this before reporting "done")
1. Run the ASCII scan (section 6, rule 14) on the .py file - must be clean.
2. Open `https://studio.genlayer.com/run-debug`.
3. Settings -> Reset Storage -> Confirm -> hard refresh.
4. Deploy, click the transaction in the sidebar, confirm `Result: SUCCESS` (not
   just `Status: FINALIZED`).
5. On `Result: ERROR`, read the traceback and map it to one of the 26 rules.

## 10. MANDATORY deliverables for EVERY task (identical structure)
1. `<contract_snake_case>.py` - the skeleton in section 5, all 26 rules, pure
   ASCII.
2. `test_<contract_snake_case>.py` - using `gltest`. Mock LLM/web via
   `sim_installMocks` with a FLAT DICT params (do NOT wrap in a list):
   ```python
   client.provider.make_request(method="sim_installMocks", params={
       "llm_mocks": {".*": json.dumps({"verdict": "PASS", "confidence": 85, "reason": "..."})},
       "web_mocks": {".*": {"status": 200, "body": "Mock page content"}},
   })
   ```
   Writes use the fluent API:
   `contract.connect(acct).method(args=[...]).transact()`. Reads:
   `contract.method(args=[...]).call()`. Minimum tests: one happy-path per
   possible verdict + one edge-case test specific to the task + one test proving
   the validator REJECTS a leader result whose verdict differs from an
   independent re-run (mock two different LLM responses to force disagreement).
3. `README.md` - four required sections: (1) what the primitive does and the
   problem it solves, (2) how consensus / the validator works - stressing that it
   checks MEANING, not FORMAT, and naming the exact confidence bands, (3) why it
   is reusable across many problems (with concrete examples), (4) a usage example
   (code snippet).

