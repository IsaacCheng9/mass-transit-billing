"""
To run the program, use the following command from the src/ directory:

python mass_transit_billing.py <zone_map_file> <journey_map_file> <output_file>
"""
import csv
import sys
from collections import defaultdict
from datetime import datetime


class MassTransitBillingSystem:
    """
    A billing system for a mass transit system which consists of a network of
    train stations, each of which belongs to a pricing zone.

    Each time a user enters (IN) or exits (OUT) a station it is recorded. The
    system is provided data about the user_id, direction (IN/OUT of the
    station), the station, and the time of the entry/exit (in UTC) for all the
    journeys in a given period. The data is sorted by timestamp, but not
    necessarily by users.
    """

    def __init__(
        self, zone_map_file: str, journey_data_file: str, output_file: str
    ) -> None:
        self.zone_map_file = zone_map_file
        self.journey_data_file = journey_data_file
        self.output_file = output_file
        # station_name: zone
        self.station_to_zone = {}
        # user_id: [(zone, direction, timestamp), ...]
        self.journeys_per_user = defaultdict(list)
        # user_id: total_billing_amount
        self.user_bills = defaultdict(float)

    @staticmethod
    def get_additional_zone_cost(zone: int) -> float:
        """
        Get the additional cost of travelling to/from a given zone.

        Args:
            zone: The zone to travel to/from.
        """
        if not isinstance(zone, int):
            raise TypeError("Zone must be an integer.")
        if zone <= 0:
            raise ValueError("Zone must be greater than or equal to 1.")

        if zone == 1:
            return 0.80
        if 2 <= zone <= 3:
            return 0.50
        if 4 <= zone <= 5:
            return 0.30
        if zone >= 6:
            return 0.10

    def read_zone_map(self) -> None:
        """
        Read the CSV file that maps each station to its pricing zone and
        translate this into a dictionary.
        """
        with open(self.zone_map_file, encoding="utf-8") as file:
            reader = csv.reader(file)
            # Skip the header row.
            next(reader, None)
            for station, zone in reader:
                self.station_to_zone[station] = int(zone)

    def read_journey_data(self) -> None:
        """
        Read the CSV file containing the journey data and translate this into a
        dictionary mapping each user to a list of their journeys.
        """
        with open(self.journey_data_file, encoding="utf-8") as file:
            reader = csv.reader(file)
            # Skip the header row.
            next(reader, None)
            for user_id, station, direction, timestamp in reader:
                # Convert the timestamp to a datetime object for ease of
                # processing.
                timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
                self.journeys_per_user[user_id].append(
                    (self.station_to_zone[station], direction, timestamp)
                )

    def calculate_billing_amounts_per_user(self) -> None:
        """
        Calculate the total amount each user owes by aggregating the cost of
        their journeys.
        """
        for user_id, journeys in self.journeys_per_user.items():
            # Store the daily journeys in a stack so that we can find the
            # matching IN journey for each OUT journey.
            daily_journeys = []
            # Keep track of daily and monthly totals, as these are capped at
            # £15 and £100 respectively.
            daily_total = 0.00
            monthly_total = 0.00
            # Track the current day to determine when to reset the daily total.
            cur_day = journeys[0][2].date()

            for zone, direction, timestamp in journeys:
                if direction == "IN":
                    daily_journeys.append(zone)
                # If the user does not have a matching IN journey, then they
                # must be charged a missing fee of £5.
                elif direction == "OUT" and not daily_journeys:
                    daily_total += 5.00
                # Otherwise, calculate the cost of the journey based on the
                # last IN journey and the current OUT journey.
                elif direction == "OUT":
                    entry_zone = daily_journeys.pop()
                    # £2 base fee for all journeys, plus additional costs based
                    # on the entry and exit zones.
                    journey_cost = (
                        2.0
                        + self.get_additional_zone_cost(entry_zone)
                        + self.get_additional_zone_cost(zone)
                    )
                    daily_total += round(journey_cost, 2)

                # If a new day has started, update it, update the running total
                # for the month, and reset the daily total.
                if timestamp.date() > cur_day:
                    cur_day = timestamp.date()
                    monthly_total += min(15.00, daily_total)
                    daily_total = 0.00

            # The user has not exited all stations they entered, so charge them
            # a missing fee of £5 per day.
            if daily_journeys:
                daily_total += round(5.00 * len(daily_journeys), 2)
            monthly_total += round(min(15.00, daily_total), 2)

            # There's a monthly cap of £100.
            self.user_bills[user_id] = min(100.00, monthly_total)

    def write_billing_output(self) -> None:
        """
        Write the billing output to a CSV file, with each line containing the
        user ID and their billing amount (£).
        """
        with open(self.output_file, "w", encoding="utf-8") as file:
            writer = csv.writer(file)
            # Write the billing output in ascending order of user ID.
            for user_id, bill_amount in sorted(self.user_bills.items()):
                # Format the billing amount to two decimal places, as we store
                # the amount in £.
                formatted_amount = format(bill_amount, ".2f")
                writer.writerow([user_id, formatted_amount])

        print(
            f"Successfully wrote billing output to {self.output_file} at "
            f"{datetime.now()}"
        )

    def process_billing(self) -> None:
        """
        Process the billing for the transactions in the transit system.
        """
        self.read_zone_map()
        self.read_journey_data()
        self.calculate_billing_amounts_per_user()
        self.write_billing_output()


if __name__ == "__main__":
    zone_map, journey_data, output = sys.argv[1:]
    billing_system = MassTransitBillingSystem(zone_map, journey_data, output)
    billing_system.process_billing()
