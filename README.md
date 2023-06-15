# Mass Transit Billing

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Overview

A billing system for a mass transit system which consists of a network of train
stations, each of which belongs to a pricing zone.

Each time a user enters (IN) or exits (OUT) a station it is recorded. The
system is provided data about the user_id, direction (IN/OUT of the station),
the station, and the time of the entry/exit (in UTC) for all the journeys in a
given period. The data is sorted by timestamp, but not necessarily by users.

### Billing System

There is a £2 base fee for all journeys, and additional costs based on the entry
and exit zones.

| Zone | In / Out Additional Cost |
| ---- | ------------------------ |
| 1    | £0.80                    |
| 2-3  | £0.50                    |
| 4-5  | £0.30                    |
| 6+   | £0.10                    |

#### Example 1

zone 1 -> zone 1 = 2.00 + 0.80 + 0.80 = £3.60

#### Example 2

zone 6 -> zone 4 = 2.00 + 0.10 + 0.30 = £2.40

For any erroneous journeys where an IN or OUT is missing a £5 fee is used as the
total journey price. It should be assumed that all valid journeys are completed
before midnight (i.e. all valid journeys will have an IN and an OUT on the same
day).

There is also a daily cap of £15, and a monthly cap of £100. Caps include all
journey costs and fees, once a given cap is reached the customer pays no extra
for the given day or month.

### Assumptions

- The program and tests are run as explained in the [Usage](#usage) section.
- CSV files are provided for the station zone map and journey data.
- The CSV files are encoded in UTF-8.
- The CSV files contain valid data in the correct format, and there are no
  missing values.
- Zone names will be formatted as integers starting from 1.
- Stations will only be in one zone.
- There are no restrictions on customers tapping in or out of stations outside
  of those stated in the specification.
- Pricing of the zones will remain fixed for the foreseeable future.
- Any future changes to a station's zone will not be backdated, so refunds or
  additional charges will not be required.
- There will be future extensions to the system, so the program is designed to
  be easily extended.

## Usage

This program was written and tested using Python 3.11.3 on macOS Ventura 13.3.1.

### Running the Program

No external libraries are required to run the program.

To run the program, use the following command from the [src](src/) directory:

```bash
python mass_transit_billing.py <zone_map_file_path> <journey_map_file_path> <output_file_path>
```

For example:

```bash
python mass_transit_billing.py ../resources/zone_map.csv ../resources/journey_data.csv ../resources/output.csv
```

### Running the Tests

The tests are written using the [pytest](https://docs.pytest.org/en/stable/)
library. Ensure that you have the correct version installed by running the
following command from the [root](./) directory:

```bash
pip install -r requirements.txt
```

To run the tests, use the following command from the [tests](tests/) directory:

```bash
pytest
```

## Code Conventions

- [Black](https://github.com/psf/black) for code formatting
- [Google's Docstring Format](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)
