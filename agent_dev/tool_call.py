import json
from typing import Literal


class Parameter:
    def __init__(self, name, type: Literal["string", "number", "boolean", "array", "object"], description, required):
        self.name = name
        self.type = type
        self.description = description
        self.required = required


class Tool:
    def __init__(self, name, description, parameters: list[Parameter], func):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.func = func

    def call(self, args: str):
        args_dict = json.loads(args)

        # First check all required parameters
        for parameter in self.parameters:
            if parameter.required and parameter.name not in args_dict:
                raise ValueError(
                    f"Parameter {parameter.name} is required but not provided")

        # Then do type conversion for provided parameters
        for parameter in self.parameters:
            if parameter.name in args_dict:
                if parameter.type == "string":
                    args_dict[parameter.name] = str(args_dict[parameter.name])
                elif parameter.type == "number":
                    args_dict[parameter.name] = float(
                        args_dict[parameter.name])
                elif parameter.type == "boolean":
                    args_dict[parameter.name] = bool(args_dict[parameter.name])
                elif parameter.type == "array":
                    args_dict[parameter.name] = list(args_dict[parameter.name])
                elif parameter.type == "object":
                    args_dict[parameter.name] = dict(args_dict[parameter.name])

        result = self.func(**args_dict)
        if isinstance(result, str):
            return result
        else:
            return json.dumps(result)

    def to_json(self):
        parameters_dict = {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        }

        for param in self.parameters:
            parameters_dict["properties"][param.name] = {
                "type": param.type,
                "description": param.description
            }
            if param.required:
                parameters_dict["required"].append(param.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": parameters_dict,
                "strict": True
            }
        }
