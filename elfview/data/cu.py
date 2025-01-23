from dataclasses import dataclass
from elfview.data.function import Function
from elfview.data.variable import Variable


@dataclass
class CompilationUnit:
    name: str
    functions: list[Function]
    variables: list[Variable]
    functions_size: int
    variables_size: int
