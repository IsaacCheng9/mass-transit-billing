"""
To run the program, use the following command from the tests/ directory:

pytest
"""

import tempfile
from datetime import datetime

import pytest

from src.mass_transit_billing import MassTransitBillingSystem


class TestMassTransitBillingSystem:
    """
    A test class for the MassTransitBillingSystem class.
    """

    @pytest.fixture
    def sample_billing_system(self) -> MassTransitBillingSystem:
        """
        Create a sample billing system for testing.

        Returns:
            A sample billing system object.
        """
        zone_map_file = "sample_zone_map.csv"
        journey_data_file = "sample_journey_data.csv"
        with tempfile.NamedTemporaryFile("w", encoding="utf-8") as temp_output_file:
            output_file = temp_output_file.name

        return MassTransitBillingSystem(zone_map_file, journey_data_file, output_file)

    def test_get_additional_zone_cost_amounts(
        self, sample_billing_system: MassTransitBillingSystem
    ):
        """
        Ensure that the cost of additional zones is read correctly.

        Args:
            sample_billing_system: A sample billing system object.
        """
        # Zone 1 costs £0.80, zones 2-3 costs £0.50, zones 4-5 costs £0.30, and
        # zones 6+ cost £0.10.
        assert sample_billing_system.get_additional_zone_cost(1) == 0.80
        assert sample_billing_system.get_additional_zone_cost(2) == 0.50
        assert sample_billing_system.get_additional_zone_cost(3) == 0.50
        assert sample_billing_system.get_additional_zone_cost(5) == 0.30
        assert sample_billing_system.get_additional_zone_cost(6) == 0.10
        assert sample_billing_system.get_additional_zone_cost(100) == 0.10

    def test_get_additional_zone_cost_errors(
        self, sample_billing_system: MassTransitBillingSystem
    ):
        """
        Ensure that invalid zone numbers raise the correct errors.

        Args:
            sample_billing_system: A sample billing system object.
        """
        # Zones should always be positive integers.
        with pytest.raises(ValueError):
            sample_billing_system.get_additional_zone_cost(-1)
        with pytest.raises(ValueError):
            sample_billing_system.get_additional_zone_cost(0)
        with pytest.raises(TypeError):
            sample_billing_system.get_additional_zone_cost("")
        with pytest.raises(TypeError):
            sample_billing_system.get_additional_zone_cost("a")
        with pytest.raises(TypeError):
            sample_billing_system.get_additional_zone_cost([])
        with pytest.raises(TypeError):
            sample_billing_system.get_additional_zone_cost({})

    def test_read_zone_map(self, sample_billing_system: MassTransitBillingSystem):
        """
        Ensure that the map of station to zone number is read correctly.

        Args:
            sample_billing_system: A sample billing system object.
        """
        sample_billing_system.read_zone_map()
        assert sample_billing_system.station_to_zone == {
            "station1": 1,
            "station2": 2,
            "station3": 3,
            "station4": 4,
        }

    def test_read_journey_data(self, sample_billing_system: MassTransitBillingSystem):
        """
        Ensure that journey data is read correctly.

        Args:
            sample_billing_system: A sample billing system object.
        """
        sample_billing_system.read_zone_map()
        sample_billing_system.read_journey_data()
        assert dict(sample_billing_system.journeys_per_user) == {
            "user1": [
                (1, "IN", datetime(2022, 4, 4, 9, 40)),
                (3, "OUT", datetime(2022, 4, 4, 13, 55)),
                (1, "IN", datetime(2022, 4, 7, 9, 40)),
                (1, "OUT", datetime(2022, 4, 7, 9, 45)),
            ],
            "user2": [
                (3, "IN", datetime(2022, 4, 4, 9, 50)),
                (1, "OUT", datetime(2022, 4, 4, 10, 50)),
            ],
            "user3": [
                (4, "IN", datetime(2022, 4, 6, 5, 10)),
                (2, "OUT", datetime(2022, 4, 6, 7, 40)),
                # As they tapped out but not in, this journey should cause
                # a £5 missing tap charge.
                (2, "OUT", datetime(2022, 4, 10, 7, 40)),
            ],
        }

    def test_calculate_billing_amounts_per_user(
        self, sample_billing_system: MassTransitBillingSystem
    ):
        """
        Ensure that the billing amounts per user are calculated correctly.

        Args:
            sample_billing_system: A sample billing system object.
        """
        sample_billing_system.read_zone_map()
        sample_billing_system.read_journey_data()
        sample_billing_system.calculate_billing_amounts_per_user()
        assert dict(sample_billing_system.user_bills) == {
            "user1": 6.90,
            "user2": 3.30,
            "user3": 7.80,
        }

    def test_write_billing_output(
        self, sample_billing_system: MassTransitBillingSystem
    ):
        """
        Ensure that the output CSV file is written correctly.

        Args:
            sample_billing_system: A sample billing system object.
        """
        sample_billing_system.read_zone_map()
        sample_billing_system.read_journey_data()
        sample_billing_system.calculate_billing_amounts_per_user()
        sample_billing_system.write_billing_output()
        with open(
            sample_billing_system.output_file, "r", encoding="utf-8"
        ) as output_file:
            output = output_file.read()
        assert output == (
            "user1,6.90\n" "user2,3.30\n" "user3,7.80\n"
        )

    def test_process_billing(self, sample_billing_system: MassTransitBillingSystem):
        """
        Ensure that the entire billing process is executed correctly.

        Args:
            sample_billing_system: A sample billing system object.
        """
        sample_billing_system.process_billing()
        with open(
            sample_billing_system.output_file, "r", encoding="utf-8"
        ) as output_file:
            output = output_file.read()
        assert output == (
            "user1,6.90\n" "user2,3.30\n" "user3,7.80\n"
        )
