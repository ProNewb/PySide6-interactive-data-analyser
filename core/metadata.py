TRANSFORM_OPERATIONS = {
    "round": {
        "group": "Numeric",
        "handler": "numeric",
        "mode": "single",
        "dtype": "numeric",
        "inputs": ["decimals"]
    },
    "add": {
        "group": "Numeric",
        "handler": "numeric",
        "mode": "single",
        "dtype": "numeric",
        "inputs": ["constant"]
    },
    "subtract" :{
        "group": "Numeric",
        "handler": "numeric",
        "mode": "single",
        "dtype": "numeric",
        "inputs": ["constant"]
}	,
    "multiply" :{
            "group": "Numeric",
            "handler": "numeric",
            "mode": "single",
            "dtype": "numeric",
            "inputs": ["constant"]
    }	,
    "divide":{
            "group": "Numeric",
            "handler": "numeric",
            "mode": "single",
            "dtype": "numeric",
            "inputs": ["constant"]
    }	,

    "floor_divide" :{
        "group": "Numeric",
        "handler": "numeric",
        "mode": "single",
        "dtype": "numeric",
        "inputs": ["constant"]
}	,
    "modulus" :{
        "group": "Numeric",
        "handler": "numeric",
        "mode": "single",
        "dtype": "numeric",
        "inputs": ["constant"]
}	,
    "power":{
        "group": "Numeric",
        "handler": "numeric",
        "mode": "single",
        "dtype": "numeric",
        "inputs": ["constant"]
}	,
    "round":{
        "group": "Numeric",
        "handler": "numeric",
        "mode": "single",
        "dtype": "numeric",
        "inputs": ["constant"]
}	,
    "round_to_nearest":{
        "group": "Numeric",
        "handler": "numeric",
        "mode": "single",
        "up": "bool",
        "dtype": "numeric",
        "inputs": ["int"]
}	,
    "clip":{
        "group": "Numeric",
        "handler": "numeric",
        "mode": "single",
        "dtype": "numeric",
        "inputs": ["constant min", "constant max"]
}	,


    "exp":{
        "group": "Numeric",
        "handler": "numeric",
        "mode": "single",
        "dtype": "numeric"
}	,
    "reciprocal":{
            "group": "Numeric",
            "handler": "numeric",
            "mode": "single",
            "dtype": "numeric"
    }	,
    "absolute":{
            "group": "Numeric",
            "handler": "numeric",
            "mode": "single",
            "dtype": "numeric"
    }	,
    "floor":{
            "group": "Numeric",
            "handler": "numeric",
            "mode": "single",
            "dtype": "numeric"
    }	,
    "ceil":{
            "group": "Numeric",
            "handler": "numeric",
            "mode": "single",
            "dtype": "numeric"
    }	,
    "normalize":{
            "group": "Numeric",
            "handler": "numeric",
            "mode": "single",
            "dtype": "numeric"
    }	,
    "standardize":{
            "group": "Numeric",
            "handler": "numeric",
            "mode": "single",
            "dtype": "numeric"
    }	,
    "z_score":{
            "group": "Numeric",
            "handler": "numeric",
            "mode": "single",
            "dtype": "numeric"
    }	,
    "rank":{
            "group": "Numeric",
            "handler": "numeric",
            "mode": "single",
            "dtype": "numeric"
    }	,
    "cumulative_sum":{
            "group": "Numeric",
            "handler": "numeric",
            "mode": "single",
            "dtype": "numeric"
    }	,
    "log":{
            "group": "Numeric",
            "handler": "numeric",
            "mode": "single",
            "dtype": "numeric"
    }	,



    "concatenate": {
        "group": "Text",
        "handler": "text",
        "mode": "multi",
        "dtype": "text",
        "min_columns": 2,
        "inputs": ["separator"]
    },

    "days_between": {
            "group": "Datetime",
            "handler": "datetime",
            "mode": "multi",
            "dtype": "datetime",
            "min_columns": 2
    },

    "hours_between": {
            "group": "Datetime",
            "handler": "datetime",
            "mode": "multi",
            "dtype": "datetime",
            "min_columns": 2
    },

    "minutes_between": {
            "group": "Datetime",
            "handler": "datetime",
            "mode": "multi",
            "dtype": "datetime",
            "min_columns": 2
    },

    "weeks_between": {
            "group": "Datetime",
            "handler": "datetime",
            "mode": "multi",
            "dtype": "datetime",
            "min_columns": 2
    },
    }

