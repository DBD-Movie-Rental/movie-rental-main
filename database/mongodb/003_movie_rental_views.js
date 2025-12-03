// 003_movie_rental_views.js

// ----------------------------------------
// View of overdue rentals
// ----------------------------------------
db.createView("vw_overdue_rentals", "rentals", [
  {
    $match: {
      status: { $in: ["OPEN", "LATE"] },
      dueAtDatetime: { $lt: new Date() }
    }
  },
  {
    $project: {
      _id: 0,
      rental_id: "$rentalId",
      customer_id: "$customerId",
      due_at_datetime: "$dueAtDatetime",
      status: "$status",
      hours_overdue: {
        $dateDiff: {
          startDate: "$dueAtDatetime",
          endDate: new Date(),
          unit: "hour"
        }
      }
    }
  }
]);

// ----------------------------------------
// View of customers with their addresses
// ----------------------------------------
db.createView("vw_customer_addresses", "customers", [
  {
    $project: {
      _id: 0,
      customer_id: "$customerId",
      first_name: "$firstName",
      last_name: "$lastName",
      email: "$email",
      phone_number: "$phoneNumber",
      address_id: "$address.addressId",
      address: "$address.address",
      city: "$address.city",
      post_code: "$address.postCode"
    }
  }
]);

// ----------------------------------------
// View of customers, their addresses, and rentals
// ----------------------------------------
db.createView("vw_customer_address_rentals", "rentals", [
  {
    $lookup: {
      from: "customers",
      localField: "customerId",
      foreignField: "customerId",
      as: "customer_doc"
    }
  },
  { $unwind: "$customer_doc" },
  {
    $project: {
      _id: 0,
      customer_id: "$customer_doc.customerId",
      first_name: "$customer_doc.firstName",
      last_name: "$customer_doc.lastName",
      email: "$customer_doc.email",
      phone_number: "$customer_doc.phoneNumber",
      address_id: "$customer_doc.address.addressId",
      address: "$customer_doc.address.address",
      city: "$customer_doc.address.city",
      post_code: "$customer_doc.address.postCode",
      rental_id: "$rentalId",
      rental_status: "$status",
      rented_at_datetime: "$rentedAtDatetime",
      due_at_datetime: "$dueAtDatetime",
      returned_at_datetime: "$returnedAtDatetime",
      reserved_at_datetime: "$reservedAtDatetime",
      employee_id: "$employeeId",
      promo_code_id: "$promo.promoCodeId"
    }
  }
]);

// ----------------------------------------
// Aggregated rental summary per customer
// ----------------------------------------
db.createView("vw_customer_rental_summary", "rentals", [
  {
    $group: {
      _id: "$customerId",
      total_rentals: { $count: {} },
      open_rentals: {
        $sum: { $cond: [{ $eq: ["$status", "OPEN"] }, 1, 0] }
      },
      late_rentals: {
        $sum: { $cond: [{ $eq: ["$status", "LATE"] }, 1, 0] }
      },
      reserved_rentals: {
        $sum: { $cond: [{ $eq: ["$status", "RESERVED"] }, 1, 0] }
      },
      returned_rentals: {
        $sum: { $cond: [{ $eq: ["$status", "RETURNED"] }, 1, 0] }
      },
      first_rented_at_datetime: { $min: "$rentedAtDatetime" },
      last_rented_at_datetime: { $max: "$rentedAtDatetime" },
      total_payments_dkk: { $sum: { $sum: "$payments.amountDkk" } },
      total_late_fees_dkk: {
        $sum: {
          $reduce: {
            input: "$fees",
            initialValue: 0,
            in: {
              $add: [
                "$$value",
                {
                  $cond: [
                    { $eq: ["$$this.snapshot.feeType", "LATE"] },
                    "$$this.amountDkk",
                    0
                  ]
                }
              ]
            }
          }
        }
      },
      total_damaged_fees_dkk: {
        $sum: {
          $reduce: {
            input: "$fees",
            initialValue: 0,
            in: {
              $add: [
                "$$value",
                {
                  $cond: [
                    { $eq: ["$$this.snapshot.feeType", "DAMAGED"] },
                    "$$this.amountDkk",
                    0
                  ]
                }
              ]
            }
          }
        }
      },
      total_other_fees_dkk: {
        $sum: {
          $reduce: {
            input: "$fees",
            initialValue: 0,
            in: {
              $add: [
                "$$value",
                {
                  $cond: [
                    { $eq: ["$$this.snapshot.feeType", "OTHER"] },
                    "$$this.amountDkk",
                    0
                  ]
                }
              ]
            }
          }
        }
      },
      total_all_fees_dkk: { $sum: { $sum: "$fees.amountDkk" } }
    }
  },
  {
    $lookup: {
      from: "customers",
      localField: "_id",
      foreignField: "customerId",
      as: "c"
    }
  },
  { $unwind: "$c" },
  {
    $project: {
      _id: 0,
      customer_id: "$_id",
      first_name: "$c.firstName",
      last_name: "$c.lastName",
      email: "$c.email",
      phone_number: "$c.phoneNumber",
      total_rentals: 1,
      open_rentals: 1,
      late_rentals: 1,
      reserved_rentals: 1,
      returned_rentals: 1,
      first_rented_at_datetime: 1,
      last_rented_at_datetime: 1,
      total_payments_dkk: 1,
      total_late_fees_dkk: 1,
      total_damaged_fees_dkk: 1,
      total_other_fees_dkk: 1,
      total_all_fees_dkk: 1
    }
  }
]);

// ----------------------------------------
// View of customers with membership info
// ----------------------------------------
db.createView("vw_customer_membership", "customers", [
  {
    $project: {
      _id: 0,
      customer_id: "$customerId",
      first_name: "$firstName",
      last_name: "$lastName",
      email: "$email",
      phone_number: "$phoneNumber",
      membership_plan_id: "$membershipPlan.membershipPlanId",
      membership_level: "$membershipPlan.membershipType",
      monthly_cost: "$membershipPlan.monthlyCostDkk",
      starts_on: "$membershipPlan.startsOn",
      ends_on: "$membershipPlan.endsOn"
    }
  }
]);
