The get_sheets is failing and understanding how its hard. so i decided to change the get_sheets() to return a dictrionary instead of an array. so instead of a lot of [] I get:

when good:

{ result: "success", sheets: [ previous_array] }

when bad:

{ result: "error", error_message: "meaningful message", sheets: [probably empty] }

Can you refactor the code for me?
