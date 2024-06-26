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


from typing import List
from abc import ABC, abstractmethod
from yasmin.blackboard import Blackboard
from time import time

NO_PREVIOUS_STATE = None

class State(ABC):

    def __init__(self, outcomes: List[str]) -> None:
        self._outcomes = []
        self._canceled = False
        self.__start_time = 0
        self.__previous_state_name = NO_PREVIOUS_STATE
        self.timer_reset()

        if outcomes:
            self._outcomes = outcomes
        else:
            raise Exception("There must be at least one outcome")

    def __call__(self, blackboard: Blackboard = None) -> str:
        self._canceled = False

        if blackboard is None:
            blackboard = Blackboard()

        outcome = self.execute(blackboard)

        if outcome not in self._outcomes:
            raise Exception(
                f"Outcome '{outcome}' does not belong to the outcomes of the state '{self}'. The possible outcomes are: {self._outcomes}")

        return outcome

    # @abstractmethod
    def execute(self, blackboard: Blackboard) -> str:
        pass
        # raise NotImplementedError(
        #     "Subclasses must implement the execute method")
    def tick(self, blackboard: Blackboard) -> str:
        pass

    @property
    def previous_state_name(self):
        return self.__previous_state_name
    
    @previous_state_name.setter
    def previous_state_name(self, state_name):
        self.__previous_state_name = state_name

    def timer_reset(self):
        self.__start_time = time()

    def timer_elapsed(self):
        return time() - self.__start_time

    def __str__(self) -> str:
        return self.__class__.__name__

    def cancel_state(self) -> None:
        self._canceled = True

    def is_canceled(self) -> bool:
        return self._canceled

    def get_outcomes(self) -> List[str]:
        return self._outcomes
