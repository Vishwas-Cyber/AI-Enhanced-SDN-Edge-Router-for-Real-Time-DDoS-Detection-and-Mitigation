from src.runtime_contract import explain, vectorize

def test_runtime_feature_order():
    sample={"duration":5,"byte_count":100,"flow_count":2,"bps":80,"pps":10}
    assert vectorize(sample)==[10.0,80.0,2.0,100.0,5.0]

def test_explanation_decision():
    sample={"pps":10,"bps":80,"flow_count":2,"byte_count":100,"duration":5}
    assert explain(sample,0.95)["decision"]=="attack"
