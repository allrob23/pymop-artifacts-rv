from pythonmop.monitor.formalismhandler.base import Base
from typing import List


class Fsm(Base):
    """A class used to store the information of the FSM finite state machine and track the state transactions.
    """

    def __init__(self, formula: str, parameter_event_map: dict, coenable_mode: bool = False,
                 unit_test: bool = False):
        """Initialize the FSM finite state machine with a configuration string.

        Args:
            formula: The FSM finite state machine string generated by the Java logic plugins.
        """

        # Initialize the parent class (base).
        super().__init__(formula, 'fsm', parameter_event_map, coenable_mode)

    def _is_matched(self) -> List[str]:
        """Check if the current state is safe based on the spec defined by the user.

        Returns:
            One list of string containing all the matched categories.
        """

        # Check if the handler is in CFG mode
        if self.formalism == 'cfg':
            raise Exception('ERROR: the _input_parser method should not be called with CFG formalism.')

        # Declare the variable for storing the matched categories.
        matched_categories = []

        # Test all the possible categories apart from the special 'fail' category.
        for key in self.alias_sections.keys():
            if self.current_state in self.alias_sections[key]:
                matched_categories.append(key)

        # Return the list containing all the matched categories.
        return matched_categories
