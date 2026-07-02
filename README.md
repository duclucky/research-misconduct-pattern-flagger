# ResearchMisconductPatternFlagger

## 1. Purpose and Problem Solved
Reads a study's methods description and flags patterns that warrant further investigation, without concluding misconduct. Serves as a preliminary screen before an ethics board reviews. In healthcare administration, manually screening thousands of study proposals or published methods for subtle impossibilities (e.g., recruiting timelines that defy physical reality, lacking explicit consent procedures, or standard deviations that indicate fabricated data) is time-consuming and error-prone. This contract automates the first pass.

## 2. How Consensus and the Validator Works
The contract uses Optimistic Democracy via `gl.vm.run_nondet_unsafe(leader_fn, validator_fn)` to ensure the AI's flagging is reliable and repeatable.
The custom validator checks the MEANING of the verdict, not just the formatting:
- It independently evaluates the study description.
- It verifies that both the leader and the validator arrive at the exact same conclusion (`FLAGGED`, `CLEAN`, or `UNVERIFIABLE`).
- It maps the AI's confidence (0-100) into three bands (Low: <35, Medium: 35-79, High: 80+). The validator and leader must land in the same confidence band.
- If the verdict is `FLAGGED`, both the leader and the validator must actually produce at least one specific "flag" (a concrete reason) for the consensus to hold.

## 3. Why It Is Reusable
Reads a study's methods description and flags patterns that warrant further investigation, without concluding misconduct. Serves as a preliminary screen before an ethics board reviews.
This matters beyond a one-off demo because it operates as an objective, auditable primitive that any hospital, journal, or academic institution could integrate into their submission pipeline. It creates an immutable, append-only history of early flags for any given text, enabling ethics boards to have a decentralized, untamperable trail of red flags when formally auditing researchers. 

## 4. Usage Example
```python
from genlayer import *

# Assuming contract is deployed at `contract_address`
contract = gl.get_contract_at(contract_address)

# Submit a methods description for screening
study_text = "We recruited 5,000 subjects over a 2-day period and administered the experimental drug."
contract.screen(study_text)

# The result is saved on-chain. You can read the ruling history:
# (Pseudocode for accessing state)
# count = contract.get_count()
# latest_ruling = contract.rulings[str(count - 1)]
# print(latest_ruling.verdict, latest_ruling.flags)
```

## Deployment
- **Contract Address:** 0x68646676E748A2e6C06B36e6aa3Ef708510f625b
- **Network:** studionet
- **Example Transaction Hash:** 0x707c1fe5fed86decba266941b1882fe4e65c2c46609fd85b70bfa397159df035

**Example Input/Output:**
- **Input (`study_description_text`):** "We recruited 5,000 subjects over a 2-day period and administered the experimental drug."
- **Expected Output (`verdict`):** "FLAGGED" (Consensus achieved that the timeline is impossible/warrants investigation).
