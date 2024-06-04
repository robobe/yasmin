# Copyright (C) 2023  Miguel Ángel González Santamarta

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from enum import IntEnum
from threading import Event, Lock
from typing import Dict, List, Union

from yasmin.blackboard import Blackboard
from yasmin.state import State


class SMMode(IntEnum):
    EXECUTE = 1
    TICK = 2


class StateMachine(State):
    def __init__(self, outcomes: List[str]) -> None:

        super().__init__(outcomes)

        self._states = {}
        self._start_state = None
        self.__current_state_name = None
        self.__current_state_lock = Lock()
        self.__trigger = Event()
        self.__wait_time = 0

    def add_state(
        self, name: str, state: State, transitions: Dict[str, str] = None
    ) -> None:

        if not transitions:
            transitions = {}

        self._states[name] = {"state": state, "transitions": transitions}

        if not self._start_state:
            self._start_state = name

    def set_tick_freq(self, freq: int):
        if int(freq) <= 0:
            return

        self.__wait_time = 1 / int(freq)

    def set_start_state(self, name: str) -> None:
        self._start_state = name
        with self.__current_state_lock:
            self.__current_state_name = self._start_state
            print(self.__current_state_name)

    def get_start_state(self) -> str:
        return self._start_state

    def cancel_state(self) -> None:
        super().cancel_state()
        with self.__current_state_lock:
            if self.__current_state_name:
                self._states[self.__current_state_name]["state"].cancel_state()

    def tick_tok(self, blackboard: Blackboard) -> str:

        

        with self.__current_state_lock:
            state: Dict = self._states[self.__current_state_name]
        
        state_: State = state["state"]
        outcome = state_.tick(blackboard)
        if outcome != self.__current_state_name:
            new_state_: State = self._states[outcome]["state"]
            new_state_.timer_reset()
            # check outcome belongs to state
            if outcome not in state_.get_outcomes():
                raise Exception(
                    f"Outcome ({outcome}) is not register in state {self.__current_state_name}"
                )

            # translate outcome using transitions
            if outcome in state["transitions"]:
                outcome = state["transitions"][outcome]

            # outcome is an outcome of the sm
            if outcome in self.get_outcomes():
                with self.__current_state_lock:
                    self.__current_state_name = None
                return outcome

            # outcome is a state
            elif outcome in self._states:
                with self.__current_state_lock:
                    self.__current_state_name = outcome

            # outcome is not in the sm
            else:
                raise Exception(f"Outcome ({outcome}) without transition")
            

        return outcome

    def execute(self, blackboard: Blackboard) -> str:

        with self.__current_state_lock:
            self.__current_state_name = self._start_state

        while True:

            with self.__current_state_lock:
                state = self._states[self.__current_state_name]

            outcome = state["state"](blackboard)
            if outcome != self.__current_state_name:
                # check outcome belongs to state
                if outcome not in state["state"].get_outcomes():
                    raise Exception(
                        f"Outcome ({outcome}) is not register in state {self.__current_state_name}"
                    )

                # translate outcome using transitions
                if outcome in state["transitions"]:
                    outcome = state["transitions"][outcome]

                # outcome is an outcome of the sm
                if outcome in self.get_outcomes():
                    with self.__current_state_lock:
                        self.__current_state_name = None
                    return outcome

                # outcome is a state
                elif outcome in self._states:
                    with self.__current_state_lock:
                        self.__current_state_name = outcome

                # outcome is not in the sm
                else:
                    raise Exception(f"Outcome ({outcome}) without transition")

    def get_states(self) -> Dict[str, Union[State, Dict[str, str]]]:
        return self._states

    def get_current_state(self) -> str:
        with self.__current_state_lock:
            if self.__current_state_name:
                return self.__current_state_name

        return ""

    def __str__(self) -> str:
        return f"StateMachine: {self._states}"
