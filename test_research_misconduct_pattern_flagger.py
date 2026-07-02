import json
import pytest

def test_screen_flagged(direct_deploy, direct_owner, gl_client):
    contract = direct_deploy("research_misconduct_pattern_flagger.py")
    
    gl_client.provider.make_request(method="sim_installMocks", params={
        "llm_mocks": {
            ".*": json.dumps({
                "verdict": "FLAGGED", 
                "confidence": 95, 
                "reason": "Missing consent documentation and impossible timeline.",
                "flags": ["No informed consent", "Study duration too short for cohort"]
            })
        },
        "web_mocks": {}
    })
    
    contract.connect(direct_owner).screen(
        study_description_text="We recruited 5000 patients in 1 week and collected all blood work."
    ).transact()
    
    assert contract.get_count().call() == 1

def test_screen_clean(direct_deploy, direct_owner, gl_client):
    contract = direct_deploy("research_misconduct_pattern_flagger.py")
    
    gl_client.provider.make_request(method="sim_installMocks", params={
        "llm_mocks": {
            ".*": json.dumps({
                "verdict": "CLEAN", 
                "confidence": 85, 
                "reason": "Methodology looks standard.",
                "flags": []
            })
        },
        "web_mocks": {}
    })
    
    contract.connect(direct_owner).screen(
        study_description_text="Standard trial over 5 years with proper IRB approval."
    ).transact()
    
    assert contract.get_count().call() == 1

def test_screen_empty_input(direct_deploy, direct_owner, gl_client):
    contract = direct_deploy("research_misconduct_pattern_flagger.py")
    
    with pytest.raises(Exception) as excinfo:
        contract.connect(direct_owner).screen(study_description_text="   ").transact()
    assert "study_description_text must not be empty" in str(excinfo.value)

def test_validator_rejects_disagreement(direct_deploy, direct_owner, gl_client):
    contract = direct_deploy("research_misconduct_pattern_flagger.py")
    
    # Send a response that causes leader and validator to disagree
    # E.g., if we return a JSON with a verdict that causes issues or just rely on random failure?
    # Wait, the reference test does:
    # gl_client.provider.make_request(method="sim_installMocks", params={
    #     "llm_mocks": {".*": json.dumps({"verdict": "INVALID_VERDICT_XYZ", "confidence": 90, "reason": "Match."})},
    #     "web_mocks": {}
    # })
    gl_client.provider.make_request(method="sim_installMocks", params={
        "llm_mocks": {
            ".*": json.dumps({
                "verdict": "UNKNOWN_VERDICT", 
                "confidence": 95, 
                "reason": "Unknown",
                "flags": []
            })
        },
        "web_mocks": {}
    })
    
    try:
        contract.connect(direct_owner).screen(
            study_description_text="Some input to trigger the disagreement"
        ).transact()
        assert False, "Should have failed consensus due to invalid verdict"
    except Exception:
        pass
