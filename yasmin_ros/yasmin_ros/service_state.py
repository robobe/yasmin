

from yasmin import State
from yasmin.blackboard import Blackboard
from simple_node import Node
from .basic_outcomes import SUCCEED, ABORT


class ServiceState(State):

    def __init__(self,
                 node: Node,
                 srv_type,
                 srv_name: str,
                 create_request_handler,
                 outcomes=None,
                 response_handler=None):

        _outcomes = [SUCCEED, ABORT]

        if outcomes:
            _outcomes = _outcomes + outcomes

        self.__service_client = node.create_client(srv_type, srv_name)

        self.__create_request_handler = create_request_handler
        self.__response_handler = response_handler

        if not self.__create_goal_handler:
            raise Exception("create_request_handler is needed")

        super().__init__(_outcomes)

    def _create_request(self, blackboard: Blackboard):
        return self.__create_request_handler(blackboard)

    def execute(self, blackboard: Blackboard) -> str:

        request = self._create_request(blackboard)
        self.__service_client.wait_for_service()

        try:
            response = self.__service_client.call(request)

            if self.__response_handler:
                outcome = self.__response_handler(blackboard, response)

                if outcome:
                    return outcome

            return SUCCEED
        except:
            return ABORT
