use("movieRental");

// -----------------------------------------------------------------------------
// customers - embedded address, recentRentals, membership
// -----------------------------------------------------------------------------
db.createCollection("customers", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["firstName", "lastName", "email", "createdAt", "address","membershipPlan"],
      properties: {
        firstName:   { bsonType: "string" },
        lastName:    { bsonType: "string" },
        email:       { bsonType: "string" },
        phoneNumber: { bsonType: ["string","null"] },
        createdAt:   { bsonType: "date" },

        address: {
          bsonType: "object",
          required: ["address", "city", "postCode"],
          properties: {
            address:  { bsonType: "string" },
            city:     { bsonType: "string" },
            postCode: { bsonType: "string" }
          }
        },

        membershipPlan: {
          bsonType: "object",
          required: ["membershipType","startsOn","monthlyCostDkk"],
          properties: {
            membershipType: {
              enum: ["GOLD","SILVER","BRONZE"] // ref membershipTypes.type
            },
            startsOn: { bsonType: "date" },
            endsOn:   { bsonType: ["date","null"] },
            monthlyCostDkk: { bsonType: "decimal" }
          }
        },

        recentRentals: {
          bsonType: "array",
          maxItems: 5,
          items: {
            bsonType: "object",
            required: ["rentalId", "status", "rentedAtDatetime"],
            properties: {
              rentalId:         { bsonType: "objectId" },
              status:           { enum: ["RESERVED","OPEN","RETURNED","LATE","CANCELLED"] },
              rentedAtDatetime: { bsonType: "date" }
            }
          }
        }
      }
    }
  }
});

// Case-insensitive unique email index
db.customers.createIndex(
  { email: 1 },
  { unique: true, collation: { locale: "en", strength: 2 } }
);

// -----------------------------------------------------------------------------
// promoCodes (lookup)
// -----------------------------------------------------------------------------
db.createCollection("promoCodes", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["code"],
      properties: {
        code:        { bsonType: "string" },
        description: { bsonType: ["string","null"] },
        percentOff:  {
          bsonType: ["decimal","null"],
          minimum: NumberDecimal("0"),
          maximum: NumberDecimal("100")
        },
        amountOffDkk: { bsonType: ["decimal","null"] },
        startsAt:     { bsonType: ["date","null"] },
        endsAt:       { bsonType: ["date","null"] }
      }
    }
  }
});

db.promoCodes.createIndex({ code: 1 }, { unique: true });

// -----------------------------------------------------------------------------
// membershipTypes (lookup)
// -----------------------------------------------------------------------------
db.createCollection("membershipTypes", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["type","monthlyCostDkk"],
      properties: {
        type: {
          enum: ["GOLD","SILVER","BRONZE"] // same as SQL membership enum
        },
        monthlyCostDkk: { bsonType: "decimal" }
      }
    }
  }
});

db.membershipTypes.createIndex({ type: 1 }, { unique: true });

// -----------------------------------------------------------------------------
// feeTypes (lookup)
// -----------------------------------------------------------------------------
db.createCollection("feeTypes", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["type","defaultAmountDkk"],
      properties: {
        type: {
          enum: ["LATE","DAMAGED","OTHER"] // same as SQL fee_type enum
        },
        defaultAmountDkk: { bsonType: ["decimal","null"] }
      }
    }
  }
});

db.feeTypes.createIndex({ type: 1 }, { unique: true });

// -----------------------------------------------------------------------------
// genres (lookup)
// -----------------------------------------------------------------------------
db.createCollection("genres", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name"],
      properties: {
        name: { bsonType: "string" }
      }
    }
  }
});

db.genres.createIndex({ name: 1 }, { unique: true });

// -----------------------------------------------------------------------------
// formats (lookup) – SQL formats only; Mongo inventory also supports DIGITAL
// -----------------------------------------------------------------------------
db.createCollection("formats", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["type"],
      properties: {
        type: { enum: ["DVD","BLU-RAY","VHS"] }
      }
    }
  }
});

db.formats.createIndex({ type: 1 }, { unique: true });

// -----------------------------------------------------------------------------
// movies - reviews embedded
// -----------------------------------------------------------------------------
db.createCollection("movies", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["title"],
      properties: {
        title:      { bsonType: "string" },
        releaseYear:{ bsonType: ["int","null"] },
        runtimeMin: { bsonType: ["int","null"] },
        // SQL rating is DECIMAL(3,1); here we keep an int 1–10 (design choice)
        rating:     { bsonType: ["int","null"], minimum: 1, maximum: 10 },
        summary:    { bsonType: ["string","null"] },

        // genre names as strings, backed by genres collection
        genres: {
          bsonType: "array",
          items: { bsonType: "string" }
        },

        reviews: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["rating","createdAt"],
            properties: {
              _id:        { bsonType: "objectId" },
              customerId: { bsonType: ["objectId","null"] },
              rating:     { bsonType: "int", minimum: 1, maximum: 10 },
              body:       { bsonType: ["string","null"] },
              createdAt:  { bsonType: "date" }
            }
          }
        }
      }
    }
  }
});

db.movies.createIndex({ title: 1 });
db.movies.createIndex({ genres: 1, releaseYear: -1 });

// -----------------------------------------------------------------------------
// locations - employees and inventory embedded
// -----------------------------------------------------------------------------
db.createCollection("locations", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["address","city"],
      properties: {
        address: { bsonType: "string" },
        city:    { bsonType: "string" },

        employees: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["_id","firstName","lastName","email","isActive"],
            properties: {
              _id:         { bsonType: "objectId" },
              firstName:   { bsonType: "string" },
              lastName:    { bsonType: "string" },
              phoneNumber: { bsonType: ["string","null"] },
              email:       { bsonType: "string" },
              isActive:    { bsonType: "bool" }
            }
          }
        },

        inventory: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["_id","movieId","format","status"],
            properties: {
              _id:     { bsonType: "objectId" },
              movieId: { bsonType: "objectId" }, // ref movies._id
              format:  { enum: ["DVD","BLU-RAY","VHS"] },
              status:  { enum: ["AVAILABLE","RENTED","DAMAGED","RETIRED"] }
            }
          }
        }
      }
    }
  }
});

db.locations.createIndex({ "inventory.movieId": 1, "inventory.status": 1 });
db.locations.createIndex({ "employees.email": 1 });

// -----------------------------------------------------------------------------
// rentals - embedded items, payments, fees, promo snapshot, locationId
// -----------------------------------------------------------------------------
db.createCollection("rentals", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["customerId","locationId","status","items"],
      properties: {
        customerId: { bsonType: "objectId" }, // ref customers._id
        locationId: { bsonType: "objectId" }, // ref locations._id
        employeeId: { bsonType: ["objectId","null"] }, // ref locations.employees._id

        status: {
          enum: ["RESERVED","OPEN","RETURNED","LATE", "CANCELLED"]
        },

        // reserved rentals may omit rentedAtDatetime entirely
        rentedAtDatetime:   { bsonType: "date" },
        returnedAtDatetime: { bsonType: ["date","null"] },
        dueAtDatetime:      { bsonType: ["date","null"] },
        reservedAtDatetime: { bsonType: ["date","null"] },

        // Items: snapshot of which copy, which movie, and which format
        items: {
          bsonType: "array",
          minItems: 1,
          items: {
            bsonType: "object",
            required: ["inventoryItemId","movieId","format"],
            properties: {
              inventoryItemId: {
                bsonType: "objectId" // locations.inventory._id
              },
              movieId: {
                bsonType: "objectId" // movies._id
              },
              format: {
                enum: ["DVD","BLU-RAY","VHS","DIGITAL"] // snapshot at rental time
              }
            }
          }
        },

        payments: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["_id","amountDkk","createdAt"],
            properties: {
              _id:       { bsonType: "objectId" },
              amountDkk: { bsonType: "decimal" },
              createdAt: { bsonType: "date" },
              // extra fields (method, etc.) are allowed but not validated here
            }
          }
        },

        fees: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["_id","feeType","amountDkk"],
            properties: {
              _id:       { bsonType: "objectId" },
              feeType:   { bsonType: "string" },  // ref feeTypes.type ("LATE", ...)
              amountDkk: { bsonType: "decimal" },
              snapshot: {
                bsonType: ["object","null"],
                properties: {
                  // default amount at the time fee was applied
                  defaultAmountDkk: { bsonType: ["decimal","null"] }
                }
              }
            }
          }
        },

        promo: {
          bsonType: ["object","null"],
          properties: {
            code:         { bsonType: "string" }, // ref promoCodes.code
            percentOff:   { bsonType: ["decimal","null"] },
            amountOffDkk: { bsonType: ["decimal","null"] },
            startsAt:     { bsonType: ["date","null"] },
            endsAt:       { bsonType: ["date","null"] }
          }
        }
      }
    }
  }
});

// indexes (including store-scoped recent rentals)
db.rentals.createIndex({ customerId: 1, status: 1, rentedAtDatetime: -1 });
db.rentals.createIndex({ status: 1 });
db.rentals.createIndex({ "items.inventoryItemId": 1 });
db.rentals.createIndex({ locationId: 1, status: 1, rentedAtDatetime: -1 });
// -----------------------------------------------------------------------------