# ============================== Define spec ==============================
from dynapyt.analyses.BaseAnalysis import BaseAnalysis

from typing import Any, Callable, Tuple, Dict, Iterable, List, Optional


"""
    This is a basic instrumentation spec that instruments the pre-call and post-call of a function.
"""


class Basic_Instrumentation(BaseAnalysis):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def pre_call(
        self, dyn_ast: str, iid: int, function: Callable, pos_args: Tuple, kw_args: Dict
    ) -> None:
        pass

    def post_call(
        self, dyn_ast: str, iid: int, result: Any, call: Callable, pos_args: Tuple, kw_args: Dict
    ) -> Any:
        pass

    def _in(self, dyn_ast: str, iid: int, left: Any, right: Any, result: bool) -> bool:
        pass

    def not_in(self, dyn_ast: str, iid: int, left: Any, right: Any, result: bool) -> bool:
        pass

    def end_execution(self) -> None:
        pass

# =========================================================================
