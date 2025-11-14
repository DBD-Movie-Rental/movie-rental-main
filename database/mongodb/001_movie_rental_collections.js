use("movieRental");

// -----------------------------------------------------------------------------
// customers - embedded address, recentRentals, membership
// customer        -> customers
// address         -> customers.address
// membership_plan -> customers.membershipPlan
// membership      -> membershipTypes (lookup)
// rental          -> customers.recentRentals (summary)
// -----------------------------------------------------------------------------
db.createCollection("customers", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["customerId","firstName","lastName","email","createdAt","address","membershipPlan"],
      properties: {
        // MySQL customer.customer_id
        customerId: { bsonType: "int" },

        firstName:   { bsonType: "string" },
        lastName:    { bsonType: "string" },
        email:       { bsonType: "string" },
        phoneNumber: { bsonType: ["string","null"] },
        createdAt:   { bsonType: "date" },

        // MySQL address (address_id, address, city, post_code, customer_id)
        address: {
          bsonType: "object",
          required: ["addressId","address","city","postCode"],
          properties: {
            addressId: { bsonType: "int" },   // address.address_id
            address:   { bsonType: "string" },
            city:      { bsonType: "string" },
            postCode:  { bsonType: "string" }
          }
        },

        // MySQL membership_plan + membership
        membershipPlan: {
          bsonType: "object",
          required: ["membershipPlanId","membershipType","startsOn","monthlyCostDkk"],
          properties: {
            membershipPlanId: { bsonType: "int" }, // membership_plan.membership_plan_id
            membershipType: {
              enum: ["GOLD","SILVER","BRONZE"]     // membership.membership
            },
            startsOn:       { bsonType: "date" },  // membership_plan.starts_on
            endsOn:         { bsonType: ["date","null"] }, // membership_plan.ends_on
            monthlyCostDkk: { bsonType: "decimal" },       // membership_plan.monthly_cost
            membershipId:   { bsonType: "int" }   // membership.membership_id
          }
        },

        // Summary of recent rentals for this customer
        recentRentals: {
          bsonType: "array",
          maxItems: 5,
          items: {
            bsonType: "object",
            required: ["rentalId","status","rentedAtDatetime"],
            properties: {
              rentalId:         { bsonType: "int" }, // rental.rental_id
              status:           { enum: ["RESERVED","OPEN","RETURNED","LATE","CANCELLED"] },
              rentedAtDatetime: { bsonType: "date" }
            }
          }
        }
      }
    }
  }
});

// -----------------------------------------------------------------------------
// promoCodes (lookup)  <-> promo_code
// -----------------------------------------------------------------------------
db.createCollection("promoCodes", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["promoCodeId","code","startsAt","endsAt"],
      properties: {
        promoCodeId: { bsonType: "int" }, // promo_code.promo_code_id
        code:        { bsonType: "string" },
        description: { bsonType: ["string","null"] },
        percentOff:  {
          bsonType: ["decimal","null"],
          minimum: NumberDecimal("0"),
          maximum: NumberDecimal("100")
        },
        amountOffDkk: { bsonType: ["decimal","null"] },
        startsAt:     { bsonType: "date" }, // promo_code.starts_at
        endsAt:       { bsonType: "date" }  // promo_code.ends_at
      }
    }
  }
});

// -----------------------------------------------------------------------------
// membershipTypes (lookup)  <-> membership
// -----------------------------------------------------------------------------
db.createCollection("membershipTypes", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["membershipId","type"],
      properties: {
        membershipId: { bsonType: "int" }, // membership.membership_id
        type: {
          enum: ["GOLD","SILVER","BRONZE"] // membership.membership
        }
      }
    }
  }
});

// -----------------------------------------------------------------------------
// feeTypes (lookup)  <-> fee
// -----------------------------------------------------------------------------
db.createCollection("feeTypes", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["feeId","feeType","defaultAmountDkk"],
      properties: {
        feeId:   { bsonType: "int" }, // fee.fee_id
        feeType: {
          enum: ["LATE","DAMAGED","OTHER"] // fee.fee_type
        },
        defaultAmountDkk: { bsonType: "decimal" } // fee.amount_dkk
      }
    }
  }
});

// -----------------------------------------------------------------------------
// genres (lookup)  <-> genre
// -----------------------------------------------------------------------------
db.createCollection("genres", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["genreId","name"],
      properties: {
        genreId: { bsonType: "int" }, // genre.genre_id
        name:    { bsonType: "string" }
      }
    }
  }
});

// -----------------------------------------------------------------------------
// formats (lookup) <-> format
// -----------------------------------------------------------------------------
db.createCollection("formats", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["formatId","type"],
      properties: {
        formatId: { bsonType: "int" }, // format.format_id
        type:     { enum: ["DVD","BLU-RAY","VHS"] } // format.format
      }
    }
  }
});

// -----------------------------------------------------------------------------
// movies - reviews embedded  <-> movie, review, movie_genre
// -----------------------------------------------------------------------------
db.createCollection("movies", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["movieId","title"],
      properties: {
        movieId:    { bsonType: "int" }, // movie.movie_id
        title:      { bsonType: "string" },
        releaseYear:{ bsonType: ["int","null"] },
        runtimeMin: { bsonType: ["int","null"] },
        // SQL rating is DECIMAL(3,1); here we keep 1–10 int
        rating:     { bsonType: ["int","null"], minimum: 1, maximum: 10 },
        summary:    { bsonType: ["string","null"] },

        // genre names, backed by genres.name (movie_genre join table collapsed)
        genres: {
          bsonType: "array",
          items: { bsonType: "string" }
        },

        // review table embedded
        reviews: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["reviewId","rating","createdAt","movieId"],
            properties: {
              reviewId:  { bsonType: "int" }, // review.review_id
              movieId:   { bsonType: "int" }, // review.movie_id
              rating:    { bsonType: "int", minimum: 1, maximum: 10 },
              body:      { bsonType: ["string","null"] },
              createdAt: { bsonType: "date" },
              // optional: link to a customer (non-SQL extension)
              customerId: { bsonType: ["int","null"] } // customer.customer_id (if used)
            }
          }
        }
      }
    }
  }
});

// -----------------------------------------------------------------------------
// locations - employees and inventory embedded
// location       -> locations
// employee       -> locations.employees
// inventory_item -> locations.inventory
// -----------------------------------------------------------------------------
db.createCollection("locations", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["locationId","address","city"],
      properties: {
        locationId: { bsonType: "int" }, // location.location_id
        address:    { bsonType: "string" },
        city:       { bsonType: "string" },

        employees: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["employeeId","firstName","lastName","email","isActive"],
            properties: {
              employeeId:  { bsonType: "int" }, // employee.employee_id
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
            required: ["inventoryItemId","movieId","formatId","status"],
            properties: {
              inventoryItemId: { bsonType: "int" }, // inventory_item.inventory_item_id
              movieId:         { bsonType: "int" }, // inventory_item.movie_id
              formatId:        { bsonType: "int" }, // inventory_item.format_id
              status:          { enum: ["AVAILABLE","RENTED","DAMAGED","RETIRED"] }
            }
          }
        }
      }
    }
  }
});

// -----------------------------------------------------------------------------
// rentals - embedded items, payments, fees, promo snapshot
// rental       -> rentals
// rental_item  -> rentals.items[]
// payment      -> rentals.payments[]
// rental_fee   -> rentals.fees[]
// -----------------------------------------------------------------------------
db.createCollection("rentals", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["rentalId","customerId","locationId","status","items"],
      properties: {
        rentalId:   { bsonType: "int" },          // rental.rental_id
        customerId:{ bsonType: "int" },           // rental.customer_id
        locationId:{ bsonType: "int" },           // derived from inventory_item.location_id
        employeeId:{ bsonType: ["int","null"] },  // rental.employee_id

        status: {
          enum: ["RESERVED","OPEN","RETURNED","LATE","CANCELLED"]
        },

        rentedAtDatetime:   { bsonType: ["date","null"] }, // rental.rented_at_datetime
        returnedAtDatetime: { bsonType: ["date","null"] }, // rental.returned_at_datetime
        dueAtDatetime:      { bsonType: ["date","null"] }, // rental.due_at_datetime
        reservedAtDatetime: { bsonType: ["date","null"] }, // rental.reserved_at_datetime

        // rental_item embedded
        items: {
          bsonType: "array",
          minItems: 1,
          items: {
            bsonType: "object",
            required: ["rentalItemId","inventoryItemId","movieId","formatId"],
            properties: {
              rentalItemId:    { bsonType: "int" }, // rental_item.rental_item_id
              inventoryItemId: { bsonType: "int" }, // rental_item.inventory_item_id
              movieId:         { bsonType: "int" }, // inventory_item.movie_id
              formatId:        { bsonType: "int" }  // inventory_item.format_id
            }
          }
        },

        // payment embedded
        payments: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["paymentId","amountDkk","createdAt"],
            properties: {
              paymentId: { bsonType: "int" },      // payment.payment_id
              amountDkk: { bsonType: "decimal" },  // payment.amount_dkk
              createdAt: { bsonType: "date" }      // payment.created_at
            }
          }
        },

        // rental_fee embedded
        fees: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["rentalFeeId","feeId","amountDkk"],
            properties: {
              rentalFeeId: { bsonType: "int" },    // rental_fee.rental_fee_id
              feeId:       { bsonType: "int" },    // rental_fee.fee_id
              amountDkk:   { bsonType: "decimal" },
              snapshot: {
                bsonType: ["object","null"],
                properties: {
                  feeType:         { bsonType: ["string","null"] },  // fee.fee_type
                  defaultAmountDkk:{ bsonType: ["decimal","null"] }  // fee.amount_dkk at time
                }
              }
            }
          }
        },

        // promo snapshot
        promo: {
          bsonType: ["object","null"],
          properties: {
            promoCodeId:  { bsonType: ["int","null"] },     // rental.promo_code_id
            code:         { bsonType: ["string","null"] },  // promo_code.code snapshot
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
// -----------------------------------------------------------------------------