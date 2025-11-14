use("movieRental");

// -----------------------------------------------------------------------------
// customers
// -----------------------------------------------------------------------------
db.customers.createIndex(
  { customerId: 1 },
  { unique: true }
);

db.customers.createIndex(
  { email: 1 },
  {
    unique: true,
    collation: { locale: "en", strength: 2 } // case-insensitive uniqueness
  }
);

// -----------------------------------------------------------------------------
// promoCodes
// -----------------------------------------------------------------------------
db.promoCodes.createIndex(
  { promoCodeId: 1 },
  { unique: true }
);

db.promoCodes.createIndex(
  { code: 1 },
  { unique: true }
);

// -----------------------------------------------------------------------------
// membershipTypes
// -----------------------------------------------------------------------------
db.membershipTypes.createIndex(
  { membershipId: 1 },
  { unique: true }
);

db.membershipTypes.createIndex(
  { type: 1 },
  { unique: true }
);

// -----------------------------------------------------------------------------
// feeTypes
// -----------------------------------------------------------------------------
db.feeTypes.createIndex(
  { feeId: 1 },
  { unique: true }
);

db.feeTypes.createIndex(
  { feeType: 1 },
  { unique: true }
);

// -----------------------------------------------------------------------------
// genres
// -----------------------------------------------------------------------------
db.genres.createIndex(
  { genreId: 1 },
  { unique: true }
);

db.genres.createIndex(
  { name: 1 },
  { unique: true }
);

// -----------------------------------------------------------------------------
// formats
// -----------------------------------------------------------------------------
db.formats.createIndex(
  { formatId: 1 },
  { unique: true }
);

db.formats.createIndex(
  { type: 1 },
  { unique: true }
);

// -----------------------------------------------------------------------------
// movies
// -----------------------------------------------------------------------------
db.movies.createIndex(
  { movieId: 1 },
  { unique: true }
);

db.movies.createIndex(
  { title: 1 }
);

db.movies.createIndex(
  { genres: 1, releaseYear: -1 }
);

// -----------------------------------------------------------------------------
// locations
// -----------------------------------------------------------------------------
db.locations.createIndex(
  { locationId: 1 },
  { unique: true }
);

db.locations.createIndex(
  { "inventory.movieId": 1, "inventory.status": 1 }
);

db.locations.createIndex(
  { "employees.email": 1 }
);

// -----------------------------------------------------------------------------
// rentals
// -----------------------------------------------------------------------------
db.rentals.createIndex(
  { rentalId: 1 },
  { unique: true }
);

db.rentals.createIndex(
  { customerId: 1, status: 1, rentedAtDatetime: -1 }
);

db.rentals.createIndex(
  { status: 1 }
);

db.rentals.createIndex(
  { "items.inventoryItemId": 1 }
);

db.rentals.createIndex(
  { locationId: 1, status: 1, rentedAtDatetime: -1 }
);
// -----------------------------------------------------------------------------