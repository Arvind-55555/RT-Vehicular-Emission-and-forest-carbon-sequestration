import pytest
import os
import sys
import json
import pandas as pd
from unittest.mock import Mock, patch, mock_open

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from report_generator import generate_report


class TestReportGenerator:
    """Test suite for the report generator."""

    @pytest.fixture
    def mock_data(self):
        """Mock data for the report generator."""
        return pd.DataFrame({"Net_CO2_kg": [100.0, 200.0], "Net_PM25_kg": [10.0, 20.0]})

    @patch("os.makedirs")
    @patch("os.path.exists")
    @patch("pandas.read_csv")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_generate_report_success(
        self,
        mock_json_dump,
        mock_file,
        mock_read_csv,
        mock_exists,
        mock_makedirs,
        mock_data,
    ):
        # Setup mocks
        mock_exists.return_value = True
        mock_read_csv.return_value = mock_data

        # Run generator
        generate_report("reports/test_output")

        # Verify
        mock_read_csv.assert_called_once()
        mock_json_dump.assert_called_once()

        # Check report content passed to json.dump
        args, _ = mock_json_dump.call_args
        report_data = args[0]
        assert report_data["status"] == "success"
        assert report_data["metrics"]["total_net_co2_kg"] == 300.0
        assert report_data["metrics"]["total_net_pm25_kg"] == 30.0
        assert report_data["metrics"]["total_records"] == 2

    @patch("os.makedirs")
    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_generate_report_missing_data(
        self, mock_json_dump, mock_file, mock_exists, mock_makedirs
    ):
        # Setup mocks
        mock_exists.return_value = False

        # Run generator
        generate_report("reports/test_output")

        # Verify
        mock_json_dump.assert_called_once()
        args, _ = mock_json_dump.call_args
        report_data = args[0]
        assert report_data["status"] == "warning"
        assert report_data["message"] == "Data file not found"
