from src.data_loader import load_dataset
from src.metric_engine import MetricEngine


def test_summary_stats_have_expected_keys():
    df = load_dataset("data/sales_data.csv")
    engine = MetricEngine(df)
    stats = engine.summary_stats()
    assert "total_sales" in stats
    assert "median_sales" in stats
    assert "std_sales" in stats


def test_product_performance_not_empty():
    df = load_dataset("data/sales_data.csv")
    engine = MetricEngine(df)
    frame = engine.product_performance()
    assert not frame.empty
