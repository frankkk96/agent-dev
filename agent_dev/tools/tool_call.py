import json
from typing import Literal, Callable, Any, Union, Dict, List


class Parameter:
    def __init__(self, name: str, type: Literal["string", "number", "boolean", "array", "object"], description: str, required: bool):
        self.name = name
        self.type = type
        self.description = description
        self.required = required


class Tool:
    def __init__(self, name: str, description: str, parameters: list[Parameter], func: Callable):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.func = func

    def _convert_type(self, value: Any, param: Parameter) -> Any:
        """Safely convert value to the specified parameter type."""
        try:
            if param.type == "string":
                if not isinstance(value, (str, int, float, bool)):
                    raise ValueError(f"Cannot convert {type(value)} to string")
                return str(value)

            elif param.type == "number":
                if isinstance(value, bool):
                    raise ValueError("Boolean cannot be converted to number")
                if isinstance(value, (int, float)):
                    return value
                if isinstance(value, str):
                    # Try to convert string to int first, then float if that fails
                    try:
                        return int(value)
                    except ValueError:
                        return float(value)
                raise ValueError(f"Cannot convert {type(value)} to number")

            elif param.type == "boolean":
                if isinstance(value, bool):
                    return value
                if isinstance(value, str):
                    value = value.lower()
                    if value in ('true', '1', 'yes'):
                        return True
                    if value in ('false', '0', 'no'):
                        return False
                    raise ValueError(
                        f"Cannot convert string '{value}' to boolean")
                if isinstance(value, (int, float)):
                    return bool(value)
                raise ValueError(f"Cannot convert {type(value)} to boolean")

            elif param.type == "array":
                if not isinstance(value, (list, tuple)):
                    raise ValueError(
                        f"Expected list or tuple, got {type(value)}")
                return list(value)

            elif param.type == "object":
                if not isinstance(value, dict):
                    raise ValueError(f"Expected dict, got {type(value)}")
                return dict(value)

            else:
                raise ValueError(f"Unknown parameter type: {param.type}")

        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Error converting parameter '{param.name}': {str(e)}")

    def call(self, args: str) -> Union[str, Dict, List]:
        try:
            args_dict = json.loads(args)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON arguments: {str(e)}")

        if not isinstance(args_dict, dict):
            raise ValueError("Arguments must be a JSON object")

        # Check required parameters
        for parameter in self.parameters:
            if parameter.required and parameter.name not in args_dict:
                raise ValueError(
                    f"Parameter '{parameter.name}' is required but not provided")

        # Convert types for all provided parameters
        converted_args = {}
        for parameter in self.parameters:
            if parameter.name in args_dict:
                value = args_dict[parameter.name]
                converted_args[parameter.name] = self._convert_type(
                    value, parameter)

        try:
            result = self.func(**converted_args)
            print("called tool: ", self.name, "result: ", result)

            if result is None:
                raise ValueError(
                    f"Tool '{self.name}' returned None. This might indicate an unhandled case in the function. Args: {converted_args}")

            if isinstance(result, str):
                return result
            return json.dumps(result)
        except Exception as e:
            raise RuntimeError(f"Error executing tool '{self.name}': {str(e)}")

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
