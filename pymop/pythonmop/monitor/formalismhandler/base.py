from typing import List


class Base:
    """A base class used to store the information of the formalism handler and track the current state
    """

    save_event_history = False

    def __init__(self, formula: str, formalism: str, parameter_event_map: dict, coenable_mode: bool):
        """Initialize the formalism handler with a configuration string.

        Args:
            formula: The formalism string generated by the users (CFG)/ Java logic plugins (ERE / FSM / LTL).
            formalism: The specific type of the finite state machine (Only allows: ere, fsm, ltl and cfg).
            parameter_event_map: The map between the parameter types and their event name.
            coenable_mode: Whether the formalism handler is configured with the coenable mode or not.
        """
        # Check if the formalism typeis valid
        if formalism not in ['ere', 'fsm', 'ltl', 'cfg']:
            raise Exception(f'ERROR: The formalism {formalism} is not valid for PyMOP.')

        # Store the formalism type for future usages
        self.formalism = formalism

        # Initialize the status indicating if the handler has failed (not possible to match)
        self.fail_status = False

        # Used for testing purposes
        self.event_list = []

        # If the formalism handler is not configured with the CFG string
        if self.formalism != 'cfg':
            # Declare the variables used for the FSM.
            self.current_state = None  # The current state of the FSM.
            self.transitions = {}  # All possible transitions of the FSM.
            self.alias_sections = {}  # The alias section(s) of the FSM.
            self.all_events = set(parameter_event_map.keys())  # All possible events of the FSM.
            self.coenable_mode = coenable_mode

            # Initialize the FSM using the configuration string.
            self._input_parser(formula)

            # If the formalism is LTL, then add the violation category to the alias sections as it is not produced by the Java logic plugins.
            if self.formalism == 'ltl':
                self.alias_sections['violation'] = ['violation']

            # If the parameter_event_map is not None, then compute the all_events set and the coenable sets.
            if coenable_mode:
                # Compute the coenable sets for the FSM.
                self.coenable_set = {}
                for alias_section in self.alias_sections.keys():
                    self.coenable_set[alias_section] = self.compute_coenable_sets(self.transitions.keys(), self.all_events, self.transitions, self.alias_sections[alias_section])
        else:
            pass  # Nothing to do, functionality in CFG class

    def _input_parser(self, formula: str) -> None:
        """Parse the configuration string to set up the base FSM.
           Notes: ONLY WORKS WITH ERE / FSM / LTL (CFG not using it).

        Args:
            formula: The finite state machine string generated by the Java logic plugins.
        """

        # Check if the handler is in CFG mode
        if self.formalism == 'cfg':
            raise Exception('ERROR: the _input_parser method should not be called with CFG formalism.')

        # Declare a boolean for the default transition usage status
        default_used = False

        # Handler the special case of LTL as the output format is slightly different
        if self.formalism == 'ltl':
            formula = formula[:-1]

        # Split the input string and initialize the base FSM.
        sections = formula.split(']\n')

        # Iterator each section to find all the possible transitions
        for section in sections:

            # For the transitions part:
            if 'alias' not in section:
                state, transitions = section.split('[')
                state = state.strip()

                # Initialize the current state to the start state which is assumed to be the first listed state.
                if self.current_state is None:
                    self.current_state = state

                # Initialize the transitions variable by adding the state and possible transitions.
                self.transitions[state] = {}
                default_status = False
                default_state = None
                added_events = set()

                # Add the possible transitions to the variable.
                for transition in transitions.strip().split('\n'):

                    # Special case for adding the default transition to the variable.
                    if 'default' in transition:
                        default_status = True
                        default_used = True
                        default_state = transition.strip().split(' ')[1]
                        continue

                    # Add the possible transition to the variable.
                    if '->' in transition:
                        action, result_state = transition.split(' -> ')
                        self.transitions[state][action.strip()] = result_state.strip()
                        added_events.add(action.strip())

                # Add the default transition to the variable.
                if default_status:
                    unadded_events = self.all_events - added_events
                    for unadded_event in unadded_events:
                        self.transitions[state][unadded_event] = default_state

            # For alias expressions part:
            else:
                alias_sections = section.strip().split('\n')

                # Add each alias expression into the alias_sections variable.
                for alias_section in alias_sections:
                    alias, states = alias_section.strip().split(' = ')

                    # Extract the category from the alias string.
                    category = alias.strip().split(' ')[1]

                    # Extract the category from the alias string.
                    states = states.split(', ')

                    # Add the category and states map into the variable
                    self.alias_sections[category] = states

        if not default_used:
            self.all_events.remove('default')

    def compute_coenable_sets(self, states, events, transitions, goal_states):
        """
        Compute the coenable sets for a given FSM. A coenable set for an event e contains all sets of events
        that can lead to a goal state after e occurs.

        Args:
            states: Set of states in the FSM.
            events: Set of events in the FSM.
            transitions: Transition function as a dictionary
                        where transitions[s][e] = next_state.
            goal_states: List of goal states where the match condition is met.

        Returns:
            The calculated coenable sets for each event. For each event e, returns a set of frozensets,
            where each frozenset contains events that can reach a goal state after e.
        """

        # Initialize SEEABLE sets for each state
        # SEEABLE(s) contains sets of events that can reach a goal state from state s
        seeable = {state: set() for state in states}
        for g in goal_states:
            # Goal states can reach themselves with no additional events, therefore a frozenset with an empty set. is added.
            seeable[g] = {frozenset()}  

        # Work backwards from goal states to compute all possible event sequences
        # Use a while loop to iterate until no more changes are made
        changed = True
        while changed:
            changed = False
            for state in states:
                # For each transition from current state
                for event, next_state in transitions.get(state, {}).items():
                    # For each known sequence that reaches goal from next_state
                    # We use list() to create a copy to avoid modifying while iterating
                    for seq in list(seeable[next_state]):  
                        # Add current event to sequence and create new frozen set
                        new_seq = frozenset({event}) | seq
                        # If this is a new sequence for current state, add it
                        if new_seq not in seeable[state]:
                            seeable[state].add(new_seq)
                            changed = True

        # Compute COENABLE sets for each event
        # COENABLE(e) contains all event sequences that can reach goal after e occurs
        coenable_sets = {event: set() for event in events}
        for state in states:
            for event, next_state in transitions.get(state, {}).items():
                # Add all seeable sequences from next_state to this event's coenable set
                coenable_sets[event].update(seeable[next_state])

        # Remove empty sets from coenable sets
        for event in coenable_sets:
            coenable_sets[event] = {s for s in coenable_sets[event] if s}

        # Return the coenable sets for each event
        return coenable_sets

    def transition(self, event: str) -> List[str]:
        """Transit the FSM to a new state when an event is performed.
           Notes: ONLY WORKS WITH ERE / FSM / LTL (CFG not using it).

        Args:
            event: The event performed by the monitored program.
        """

        if Base.save_event_history:
            self.event_list.append(event)

        # Check if the handler is in CFG mode
        if self.formalism == 'cfg':
            raise Exception('ERROR: the _input_parser method should not be called with CFG formalism.')

        # Declare the list variable for storing the matched categories
        matched_categories = []

        # Check if the fail state is True
        if self.fail_status:
            # Add the 'fail' category to the matched categories
            matched_categories.append('fail')
            return matched_categories

        # Check if the transition of the event is specifically defined for the current state.
        if event in self.transitions[self.current_state].keys():
            # Transit the FSM to the new state
            self.current_state = self.transitions[self.current_state][event]

            # Check if the transition is safe and return the result.
            matched_categories = self._is_matched()

        # Return the 'fail' state when the transition is undefined.
        else:
            # Add the 'fail' category to the matched categories
            matched_categories.append('fail')

            # Set the fail state to True
            self.fail_status = True

        # Return the matched categories
        return matched_categories

    def _is_matched(self) -> List[str]:
        """Check if the current state is a safe state.
           Notes: ONLY WORKS WITH ERE / FSM / LTL (CFG not using it).

        Returns:
            One boolean expression indicated if the transition is allowed.
        """

        # This function should always be overwritten by the child class
        raise Exception('ERROR: the _is_matched is not overwritten by the child class')

    def get_current_state(self):
        """Get the current state of the fsm.
           Notes: ONLY WORKS WITH ERE / FSM / LTL (CFG not using it).

        Returns:
            The current state of the fsm.
        """

        # Check if the handler is in CFG mode
        if self.formalism == 'cfg':
            raise Exception('ERROR: the get_current_state method should not be called with CFG formalism.')

        return self.current_state

    def get_transitions(self):
        """Get all the possible transitions of the fsm.
           Notes: ONLY WORKS WITH ERE / FSM / LTL (CFG not using it).

        Returns:
            All the possible transitions of the fsm.
        """

        # Check if the handler is in CFG mode
        if self.formalism == 'cfg':
            raise Exception('ERROR: the get_transitions method should not be called with CFG formalism.')

        return self.transitions
    
    def get_coenable_set(self):
        """Get the coenable sets for the fsm.

        Returns:
            The coenable set for the given event.
        """
        # Check if the handler is in CFG mode
        if not self.coenable_mode:
            raise Exception('ERROR: the get_coenable_set method should not be called without coenable mode.')
        else:
            return self.coenable_set
    
    def __repr__(self):
        if Base.save_event_history:
            return f'{self.event_list}'
        else:
            return super().__repr__()
