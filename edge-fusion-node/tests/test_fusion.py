from firmware.fusion import calculate_fusion_score, score_to_level


def test_all_zero_inputs():
    assert calculate_fusion_score(0.0, 0, False) == 0.0


def test_all_max_inputs():
    assert calculate_fusion_score(45.0, 1500, True) == 100.0


def test_temperature_boundaries():
    assert calculate_fusion_score(30.0, 0, False) == 0.0
    assert calculate_fusion_score(45.0, 0, False) == 100.0


def test_gas_boundaries():
    assert calculate_fusion_score(0.0, 500, False) == 0.0
    assert calculate_fusion_score(0.0, 1500, False) == 100.0


def test_score_threshold_boundaries():
    assert score_to_level(39.9) == "NORMAL"
    assert score_to_level(40.0) == "WARNING"
    assert score_to_level(74.9) == "WARNING"
    assert score_to_level(75.0) == "CRITICAL"


def test_exact_threshold_mixture():
    assert calculate_fusion_score(30.0, 500, False) == 0.0
    assert calculate_fusion_score(45.0, 500, False) == 100.0
    assert calculate_fusion_score(30.0, 1500, False) == 100.0
    assert calculate_fusion_score(45.0, 1500, False) == 100.0
