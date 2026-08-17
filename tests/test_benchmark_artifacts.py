from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def test_benchmark_documents_exist():
    for name in ["BENCHMARK_PLAN.md","RESEARCH_CLAIMS.md","COMMERCIAL_GAP_ANALYSIS.md"]:
        assert (ROOT/"docs/research"/name).exists()
