use("movieRental");

// -------------------------------------------------------------
// Clean existing data (optional)
// -------------------------------------------------------------
db.rentals.deleteMany({});
db.locations.deleteMany({});
db.movies.deleteMany({});
db.customers.deleteMany({});
db.promoCodes.deleteMany({});
db.membershipTypes.deleteMany({});
db.feeTypes.deleteMany({});
db.genres.deleteMany({});
db.formats.deleteMany({});

// -------------------------------------------------------------
// 1) Lookup collections
// -------------------------------------------------------------

// membershipTypes (GOLD / SILVER / BRONZE)
db.membershipTypes.insertMany([
  { type: "GOLD",   monthlyCostDkk: NumberDecimal("149.00") },
  { type: "SILVER", monthlyCostDkk: NumberDecimal("99.00") },
  { type: "BRONZE", monthlyCostDkk: NumberDecimal("59.00") }
]);

// feeTypes (LATE / DAMAGED / OTHER)
db.feeTypes.insertMany([
  { type: "LATE",    defaultAmountDkk: NumberDecimal("10.00")  },
  { type: "DAMAGED", defaultAmountDkk: NumberDecimal("200.00") },
  { type: "OTHER",   defaultAmountDkk: null }
]);

// promoCodes
db.promoCodes.insertMany([
  {
    code: "WELCOME10",
    description: "First rental 10 DKK off",
    amountOffDkk: NumberDecimal("10.00"),
    percentOff: null,
    startsAt: new Date(),
    endsAt: null
  },
  {
    code: "NOV25",
    description: "November 25% off",
    percentOff: NumberDecimal("25.00"),
    amountOffDkk: null,
    startsAt: new Date(),
    endsAt: null
  },
  {
    code: "WEEKEND50",
    description: "Weekend 50% off",
    percentOff: NumberDecimal("50.00"),
    amountOffDkk: null,
    startsAt: new Date(),
    endsAt: null
  },
  {
    code: "SUMMER15",
    description: "Summer 15% off",
    percentOff: NumberDecimal("15.00"),
    amountOffDkk: null,
    startsAt: new Date(),
    endsAt: null
  },
  {
    code: "B2G1",
    description: "Buy 2 get 1 free",
    percentOff: null,
    amountOffDkk: null,
    startsAt: new Date(),
    endsAt: null
  }
]);

// genres used in movies
db.genres.insertMany([
  { name: "Sci-Fi" },
  { name: "Thriller" },
  { name: "Action" },
  { name: "Animation" },
  { name: "Fantasy" },
  { name: "Drama" },
  { name: "Crime" }
]);

// formats (physical only; DIGITAL is only for rentals.items.format)
db.formats.insertMany([
  { type: "DVD" },
  { type: "BLU-RAY" },
  { type: "VHS" }
]);

// -------------------------------------------------------------
// 2) Movies
// -------------------------------------------------------------
const movieIds = [ObjectId(), ObjectId(), ObjectId(), ObjectId(), ObjectId()];

db.movies.insertMany([
  {
    _id: movieIds[0],
    title: "Inception",
    releaseYear: 2010,
    runtimeMin: 148,
    rating: 9,
    genres: ["Sci-Fi","Thriller"],
    summary: "Dream heist.",
    reviews: []
  },
  {
    _id: movieIds[1],
    title: "The Matrix",
    releaseYear: 1999,
    runtimeMin: 136,
    rating: 9,
    genres: ["Sci-Fi","Action"],
    summary: "Simulation reality.",
    reviews: []
  },
  {
    _id: movieIds[2],
    title: "Spirited Away",
    releaseYear: 2001,
    runtimeMin: 125,
    rating: 10,
    genres: ["Animation","Fantasy"],
    summary: "Spirit world adventure.",
    reviews: []
  },
  {
    _id: movieIds[3],
    title: "Parasite",
    releaseYear: 2019,
    runtimeMin: 132,
    rating: 9,
    genres: ["Thriller","Drama"],
    summary: "Class tensions mount.",
    reviews: []
  },
  {
    _id: movieIds[4],
    title: "The Dark Knight",
    releaseYear: 2008,
    runtimeMin: 152,
    rating: 9,
    genres: ["Action","Crime"],
    summary: "Batman vs Joker.",
    reviews: []
  }
]);

// -------------------------------------------------------------
// 3) Locations (with employees + inventory)
// -------------------------------------------------------------
const locIds = [ObjectId(), ObjectId(), ObjectId()];
const empIds = [ObjectId(), ObjectId(), ObjectId(), ObjectId(), ObjectId(), ObjectId()];
const inv = Array.from({ length: 15 }, () => ObjectId()); // 15 inventory items

db.locations.insertMany([
  {
    _id: locIds[0],
    address: "Frederiksborggade 1",
    city: "København",
    employees: [
      { _id: empIds[0], firstName: "Sara",  lastName: "Holm",      email: "sara@store.dk",  phoneNumber: "+45 11 11 11 11", isActive: true },
      { _id: empIds[1], firstName: "Jonas", lastName: "Andersen",  email: "jonas@store.dk", phoneNumber: "+45 22 22 22 22", isActive: true }
    ],
    inventory: [
      { _id: inv[0],  movieId: movieIds[0], format: "BLU-RAY", status: "AVAILABLE" },
      { _id: inv[1],  movieId: movieIds[0], format: "DVD",     status: "AVAILABLE" },
      { _id: inv[2],  movieId: movieIds[1], format: "BLU-RAY", status: "AVAILABLE" },
      { _id: inv[3],  movieId: movieIds[2], format: "DVD",     status: "AVAILABLE" },
      { _id: inv[4],  movieId: movieIds[4], format: "DVD",     status: "AVAILABLE" }
    ]
  },
  {
    _id: locIds[1],
    address: "Søndergade 50",
    city: "Aarhus",
    employees: [
      { _id: empIds[2], firstName: "Mette", lastName: "Østergaard", email: "mette@store.dk", phoneNumber: "+45 33 33 33 33", isActive: true },
      { _id: empIds[3], firstName: "Ali",   lastName: "Khan",       email: "ali@store.dk",   phoneNumber: "+45 44 44 44 44", isActive: true }
    ],
    inventory: [
      { _id: inv[5],  movieId: movieIds[1], format: "DVD",     status: "AVAILABLE" },
      { _id: inv[6],  movieId: movieIds[2], format: "BLU-RAY", status: "AVAILABLE" },
      { _id: inv[7],  movieId: movieIds[3], format: "DVD",     status: "AVAILABLE" },
      { _id: inv[8],  movieId: movieIds[3], format: "VHS",     status: "AVAILABLE" },
      { _id: inv[9],  movieId: movieIds[4], format: "BLU-RAY", status: "AVAILABLE" }
    ]
  },
  {
    _id: locIds[2],
    address: "Algade 5",
    city: "Roskilde",
    employees: [
      { _id: empIds[4], firstName: "Pia",    lastName: "Lind",    email: "pia@store.dk",    phoneNumber: "+45 55 55 55 55", isActive: true },
      { _id: empIds[5], firstName: "Henrik", lastName: "Poulsen", email: "henrik@store.dk", phoneNumber: "+45 66 66 66 66", isActive: true }
    ],
    inventory: [
      { _id: inv[10], movieId: movieIds[3], format: "DVD",     status: "AVAILABLE" },
      { _id: inv[11], movieId: movieIds[3], format: "BLU-RAY", status: "AVAILABLE" },
      { _id: inv[12], movieId: movieIds[4], format: "DVD",     status: "AVAILABLE" },
      { _id: inv[13], movieId: movieIds[4], format: "BLU-RAY", status: "AVAILABLE" },
      { _id: inv[14], movieId: movieIds[0], format: "VHS",     status: "AVAILABLE" }
    ]
  }
]);

// -------------------------------------------------------------
// 4) Customers (with membershipPlan + recentRentals placeholder)
// -------------------------------------------------------------
const custIds = [ObjectId(), ObjectId(), ObjectId(), ObjectId(), ObjectId()];

db.customers.insertMany([
  {
    _id: custIds[0],
    firstName: "Ava",
    lastName: "Nguyen",
    email: "ava@example.com",
    phoneNumber: "+45 12 34 56 78",
    createdAt: new Date(),
    address: { address: "Vesterbrogade 10", city: "København", postCode: "1620" },
    membershipPlan: {
      membershipType: "GOLD",
      startsOn: new Date(),
      endsOn: null,
      monthlyCostDkk: NumberDecimal("149.00")
    },
    recentRentals: []
  },
  {
    _id: custIds[1],
    firstName: "Lukas",
    lastName: "Madsen",
    email: "lukas@example.com",
    phoneNumber: "+45 98 76 54 32",
    createdAt: new Date(),
    address: { address: "Søndergade 22", city: "Aarhus", postCode: "8000" },
    membershipPlan: {
      membershipType: "SILVER",
      startsOn: new Date(),
      endsOn: null,
      monthlyCostDkk: NumberDecimal("99.00")
    },
    recentRentals: []
  },
  {
    _id: custIds[2],
    firstName: "Maja",
    lastName: "Hansen",
    email: "maja@example.com",
    phoneNumber: "+45 55 55 55 55",
    createdAt: new Date(),
    address: { address: "Nørregade 7", city: "Aarhus", postCode: "8000" },
    membershipPlan: {
      membershipType: "BRONZE",
      startsOn: new Date(),
      endsOn: null,
      monthlyCostDkk: NumberDecimal("59.00")
    },
    recentRentals: []
  },
  {
    _id: custIds[3],
    firstName: "Noah",
    lastName: "Larsen",
    email: "noah@example.com",
    phoneNumber: "+45 44 44 44 44",
    createdAt: new Date(),
    address: { address: "Østerbrogade 80", city: "København", postCode: "2100" },
    membershipPlan: {
      membershipType: "BRONZE",
      startsOn: new Date(),
      endsOn: null,
      monthlyCostDkk: NumberDecimal("59.00")
    },
    recentRentals: []
  },
  {
    _id: custIds[4],
    firstName: "Emma",
    lastName: "Nielsen",
    email: "emma@example.com",
    phoneNumber: "+45 22 33 44 55",
    createdAt: new Date(),
    address: { address: "Algade 12", city: "Roskilde", postCode: "4000" },
    membershipPlan: {
      membershipType: "SILVER",
      startsOn: new Date(),
      endsOn: null,
      monthlyCostDkk: NumberDecimal("99.00")
    },
    recentRentals: []
  }
]);

// -------------------------------------------------------------
// 5) Add some embedded reviews on movies
// -------------------------------------------------------------
db.movies.updateOne(
  { _id: movieIds[0] },
  {
    $push: {
      reviews: {
        $each: [
          { _id: new ObjectId(), customerId: custIds[0], rating: 9,  body: "Still holds up.", createdAt: new Date() },
          { _id: new ObjectId(), customerId: custIds[1], rating: 8,  body: "Great visuals.",  createdAt: new Date() }
        ]
      }
    }
  }
);

db.movies.updateOne(
  { _id: movieIds[2] },
  {
    $push: {
      reviews: {
        $each: [
          { _id: new ObjectId(), customerId: custIds[3], rating: 10, body: "Masterpiece.", createdAt: new Date() }
        ]
      }
    }
  }
);

// -------------------------------------------------------------
// Helper: push recent rental onto customer (max 5)
// -------------------------------------------------------------
function pushRecentRental(custId, rentalId, status, rentedAt) {
  db.customers.updateOne(
    { _id: custId },
    {
      $push: {
        recentRentals: {
          $each: [{ rentalId, status, rentedAtDatetime: rentedAt }],
          $slice: -5
        }
      }
    }
  );
}

// -------------------------------------------------------------
// 6) Rentals
// -------------------------------------------------------------
const rentalIds = Array.from({ length: 10 }, () => ObjectId());

// 1) Ava @ CPH — Inception BLU-RAY — NOV25
db.rentals.insertOne({
  _id: rentalIds[0],
  customerId: custIds[0],
  locationId: locIds[0],
  employeeId: empIds[0],
  status: "OPEN",
  rentedAtDatetime: new Date(),
  dueAtDatetime: new Date(Date.now() + 5 * 24 * 3600 * 1000),
  items: [
    {
      inventoryItemId: inv[0],
      movieId: movieIds[0],
      format: "BLU-RAY"
    }
  ],
  payments: [
    {
      _id: new ObjectId(),
      amountDkk: NumberDecimal("49.00"),
      createdAt: new Date(),
      method: "card"
    }
  ],
  fees: [],
  promo: {
    code: "NOV25",
    percentOff: NumberDecimal("25.00"),
    amountOffDkk: null,
    startsAt: new Date(),
    endsAt: null
  }
});
pushRecentRental(custIds[0], rentalIds[0], "OPEN", new Date());

// 2) Lukas @ Aarhus — Matrix DVD + Spirited Away BLU-RAY — LATE + fee LATE
db.rentals.insertOne({
  _id: rentalIds[1],
  customerId: custIds[1],
  locationId: locIds[1],
  employeeId: empIds[2],
  status: "LATE",
  rentedAtDatetime: new Date(Date.now() - 10 * 24 * 3600 * 1000),
  dueAtDatetime: new Date(Date.now() - 3 * 24 * 3600 * 1000),
  items: [
    {
      inventoryItemId: inv[5],
      movieId: movieIds[1],
      format: "DVD"
    },
    {
      inventoryItemId: inv[6],
      movieId: movieIds[2],
      format: "BLU-RAY"
    }
  ],
  payments: [
    {
      _id: new ObjectId(),
      amountDkk: NumberDecimal("89.00"),
      createdAt: new Date(Date.now() - 10 * 24 * 3600 * 1000),
      method: "cash"
    }
  ],
  fees: [
    {
      _id: new ObjectId(),
      feeType: "LATE",
      amountDkk: NumberDecimal("30.00"),
      snapshot: {
        defaultAmountDkk: NumberDecimal("10.00")
      }
    }
  ],
  promo: null
});
pushRecentRental(
  custIds[1],
  rentalIds[1],
  "LATE",
  new Date(Date.now() - 10 * 24 * 3600 * 1000)
);

// 3) Maja @ Aarhus — Parasite DVD — RESERVED — WELCOME10
db.rentals.insertOne({
  _id: rentalIds[2],
  customerId: custIds[2],
  locationId: locIds[1],
  employeeId: empIds[3],
  status: "RESERVED",
  rentedAtDatetime: new Date(),
  reservedAtDatetime: new Date(),
  items: [
    {
      inventoryItemId: inv[7],
      movieId: movieIds[3],
      format: "DVD"
    }
  ],
  payments: [],
  fees: [],
  promo: {
    code: "WELCOME10",
    amountOffDkk: NumberDecimal("10.00"),
    percentOff: null,
    startsAt: new Date(),
    endsAt: null
  }
});
pushRecentRental(custIds[2], rentalIds[2], "RESERVED", new Date());

// 4) Noah @ Roskilde — Parasite BLU-RAY — RETURNED — fee OTHER
db.rentals.insertOne({
  _id: rentalIds[3],
  customerId: custIds[3],
  locationId: locIds[2],
  employeeId: empIds[4],
  status: "RETURNED",
  rentedAtDatetime: new Date(Date.now() - 5 * 24 * 3600 * 1000),
  returnedAtDatetime: new Date(Date.now() - 1 * 24 * 3600 * 1000),
  dueAtDatetime: new Date(Date.now() - 2 * 24 * 3600 * 1000),
  items: [
    {
      inventoryItemId: inv[11],
      movieId: movieIds[3],
      format: "BLU-RAY"
    }
  ],
  payments: [
    {
      _id: new ObjectId(),
      amountDkk: NumberDecimal("49.00"),
      createdAt: new Date(Date.now() - 5 * 24 * 3600 * 1000),
      method: "card"
    }
  ],
  fees: [
    {
      _id: new ObjectId(),
      feeType: "OTHER",
      amountDkk: NumberDecimal("25.00"),
      snapshot: {
        defaultAmountDkk: null
      }
    }
  ],
  promo: null
});
pushRecentRental(
  custIds[3],
  rentalIds[3],
  "RETURNED",
  new Date(Date.now() - 5 * 24 * 3600 * 1000)
);

// 5) Emma @ Roskilde — Dark Knight DVD — OPEN — WEEKEND50
db.rentals.insertOne({
  _id: rentalIds[4],
  customerId: custIds[4],
  locationId: locIds[2],
  employeeId: empIds[5],
  status: "OPEN",
  rentedAtDatetime: new Date(),
  dueAtDatetime: new Date(Date.now() + 3 * 24 * 3600 * 1000),
  items: [
    {
      inventoryItemId: inv[12],
      movieId: movieIds[4],
      format: "DVD"
    }
  ],
  payments: [
    {
      _id: new ObjectId(),
      amountDkk: NumberDecimal("39.00"),
      createdAt: new Date(),
      method: "mobilepay"
    }
  ],
  fees: [],
  promo: {
    code: "WEEKEND50",
    percentOff: NumberDecimal("50.00"),
    amountOffDkk: null,
    startsAt: new Date(),
    endsAt: null
  }
});
pushRecentRental(custIds[4], rentalIds[4], "OPEN", new Date());

// 6) Ava @ CPH — Matrix BLU-RAY — RETURNED
db.rentals.insertOne({
  _id: rentalIds[5],
  customerId: custIds[0],
  locationId: locIds[0],
  employeeId: empIds[1],
  status: "RETURNED",
  rentedAtDatetime: new Date(Date.now() - 3 * 24 * 3600 * 1000),
  returnedAtDatetime: new Date(),
  dueAtDatetime: new Date(Date.now() - 1 * 24 * 3600 * 1000),
  items: [
    {
      inventoryItemId: inv[2],
      movieId: movieIds[1],
      format: "BLU-RAY"
    }
  ],
  payments: [
    {
      _id: new ObjectId(),
      amountDkk: NumberDecimal("45.00"),
      createdAt: new Date(Date.now() - 3 * 24 * 3600 * 1000),
      method: "card"
    }
  ],
  fees: [],
  promo: null
});
pushRecentRental(
  custIds[0],
  rentalIds[5],
  "RETURNED",
  new Date(Date.now() - 3 * 24 * 3600 * 1000)
);

// 7) Lukas @ CPH — Inception DVD — OPEN — fee DAMAGED
db.rentals.insertOne({
  _id: rentalIds[6],
  customerId: custIds[1],
  locationId: locIds[0],
  employeeId: empIds[0],
  status: "OPEN",
  rentedAtDatetime: new Date(),
  dueAtDatetime: new Date(Date.now() + 7 * 24 * 3600 * 1000),
  items: [
    {
      inventoryItemId: inv[1],
      movieId: movieIds[0],
      format: "DVD"
    }
  ],
  payments: [
    {
      _id: new ObjectId(),
      amountDkk: NumberDecimal("49.00"),
      createdAt: new Date(),
      method: "cash"
    }
  ],
  fees: [
    {
      _id: new ObjectId(),
      feeType: "DAMAGED",
      amountDkk: NumberDecimal("200.00"),
      snapshot: {
        defaultAmountDkk: NumberDecimal("200.00")
      }
    }
  ],
  promo: null
});
pushRecentRental(custIds[1], rentalIds[6], "OPEN", new Date());

// 8) Emma @ Roskilde — Inception VHS — RESERVED — WELCOME10
db.rentals.insertOne({
  _id: rentalIds[7],
  customerId: custIds[4],
  locationId: locIds[2],
  employeeId: empIds[4],
  status: "RESERVED",
  rentedAtDatetime: new Date(),
  reservedAtDatetime: new Date(),
  items: [
    {
      inventoryItemId: inv[14],
      movieId: movieIds[0],
      format: "VHS"
    }
  ],
  payments: [],
  fees: [],
  promo: {
    code: "WELCOME10",
    amountOffDkk: NumberDecimal("10.00"),
    percentOff: null,
    startsAt: new Date(),
    endsAt: null
  }
});
pushRecentRental(custIds[4], rentalIds[7], "RESERVED", new Date());

// 9) Maja @ Aarhus — Dark Knight BLU-RAY — LATE (+ LATE fee)
db.rentals.insertOne({
  _id: rentalIds[8],
  customerId: custIds[2],
  locationId: locIds[1],
  employeeId: empIds[3],
  status: "LATE",
  rentedAtDatetime: new Date(Date.now() - 8 * 24 * 3600 * 1000),
  dueAtDatetime: new Date(Date.now() - 1 * 24 * 3600 * 1000),
  items: [
    {
      inventoryItemId: inv[9],
      movieId: movieIds[4],
      format: "BLU-RAY"
    }
  ],
  payments: [
    {
      _id: new ObjectId(),
      amountDkk: NumberDecimal("39.00"),
      createdAt: new Date(Date.now() - 8 * 24 * 3600 * 1000),
      method: "mobilepay"
    }
  ],
  fees: [
    {
      _id: new ObjectId(),
      feeType: "LATE",
      amountDkk: NumberDecimal("20.00"),
      snapshot: {
        defaultAmountDkk: NumberDecimal("10.00")
      }
    }
  ],
  promo: null
});
pushRecentRental(
  custIds[2],
  rentalIds[8],
  "LATE",
  new Date(Date.now() - 8 * 24 * 3600 * 1000)
);

// 10) Ava @ CPH — Spirited Away DVD — OPEN
db.rentals.insertOne({
  _id: rentalIds[9],
  customerId: custIds[0],
  locationId: locIds[0],
  employeeId: empIds[1],
  status: "OPEN",
  rentedAtDatetime: new Date(),
  dueAtDatetime: new Date(Date.now() + 6 * 24 * 3600 * 1000),
  items: [
    {
      inventoryItemId: inv[3],
      movieId: movieIds[2],
      format: "DVD"
    }
  ],
  payments: [
    {
      _id: new ObjectId(),
      amountDkk: NumberDecimal("39.00"),
      createdAt: new Date(),
      method: "card"
    }
  ],
  fees: [],
  promo: null
});
pushRecentRental(custIds[0], rentalIds[9], "OPEN", new Date());
// -------------------------------------------------------------