"""
Helpers for seeding the MySQL database.

This module is designed to be used from ``mysql_seed.py`` and assumes the
project layout:

    /src
      ...
    /seed
      mysql_seed.py
      mysql_seed_helpers.py
      /data
        customers.csv
        employees.csv
        locations.csv
        movies.csv
        promo_codes.csv
        reviews.txt

The CSV *examples* below show the expected columns and example rows.
You will create the actual files yourself.

customers.csv
-------------
first_name,last_name,email,phone_number,address,city,post_code
Alice,Andersen,alice@example.com,11111111,Testvej 1,Copenhagen,2100
Bob,Berg,bob@example.com,22222222,Testvej 2,Aarhus,8000

employees.csv
-------------
first_name,last_name,email,phone_number
Eva,Eriksen,eva@example.com,55555555
Lars,Larsen,lars@example.com,66666666

locations.csv
-------------
address,city
Main Street 1,Copenhagen
Second Avenue 5,Aarhus

movies.csv
----------
title,release_year,runtime_min,rating,summary,genres
The Matrix,1999,136,8.7,"Hacker discovers reality is a simulation","Sci-Fi;Action"
Toy Story,1995,81,8.3,"Toys are alive when humans aren't looking","Animation;Family"

promo_codes.csv
---------------
code,description,percent_off,amount_off_dkk,starts_at,ends_at
WELCOME10,"Welcome discount",10,,2025-01-01 00:00:00,2025-12-31 23:59:59
BIGSAVE,"Huge discount",,50.00,2025-01-01 00:00:00,2025-06-30 23:59:59

reviews.txt
-----------
One review per line, for example:
Fantastic movie, highly recommended.
Too slow and predictable.
Amazing acting, but the ending was weak.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List

from src.repositories.mysql.orm_models.base import SessionLocal

# Directory where CSV / TXT seed files are stored
DATA_DIR = Path(__file__).resolve().parent / "data"


def get_session():
    """Return a new SQLAlchemy session bound to the MySQL engine."""
    return SessionLocal()


def load_csv(filename: str) -> List[Dict[str, str]]:
    """Load a CSV file from the /seed/data directory.

    :param filename: Name of the CSV file, e.g. "customers.csv"
    :return: List of dicts, one per row.

    The first row of the CSV is treated as headers. All values are strings;
    callers are responsible for converting to int/float/datetime as needed.
    """
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def load_lines(filename: str) -> List[str]:
    """Load a simple text file (e.g. reviews.txt) as a list of lines.

    Empty lines are ignored, leading/trailing whitespace is stripped.
    """
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Text file not found: {path}")

    lines: List[str] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                lines.append(line)
    return lines
