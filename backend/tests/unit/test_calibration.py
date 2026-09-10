from __future__ import annotations

from src.models.calibration import CalibrationService


def test_calibration_bounds():
    service = CalibrationService()
    calibrated = service.calibrate(0.5)
    assert 0.0 <= calibrated <= 1.0


def test_calibration_low():
    service = CalibrationService()
    calibrated = service.calibrate(0.1)
    assert calibrated < 0.5


def test_calibration_high():
    service = CalibrationService()
    calibrated = service.calibrate(0.9)
    assert calibrated > 0.5
