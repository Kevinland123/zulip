# Webhooks for external integrations.
from typing import Any, Dict

from django.http import HttpRequest, HttpResponse

from zerver.actions.message_send import check_send_private_message
from zerver.decorator import webhook_view
from zerver.lib.request import REQ, RequestNotes, has_request_variables
from zerver.lib.response import json_success
from zerver.models import UserProfile, get_user


@webhook_view("Dialogflow")
@has_request_variables
def api_dialogflow_webhook(
    request: HttpRequest,
    user_profile: UserProfile,
    payload: Dict[str, Any] = REQ(argument_type="body"),
    email: str = REQ(),
) -> HttpResponse:
    status = payload["status"]["code"]

    if status == 200:
        result = payload["result"]["fulfillment"]["speech"]
        if not result:
            alternate_result = payload["alternateResult"]["fulfillment"]["speech"]
            if not alternate_result:
                body = "Dialogflow couldn't process your query."
            else:
                body = alternate_result
        else:
            body = result
    else:
        error_status = payload["status"]["errorDetails"]
        body = f"{status} - {error_status}"

    receiving_user = get_user(email, user_profile.realm)
    client = RequestNotes.get_notes(request).client
    assert client is not None
    check_send_private_message(user_profile, client, receiving_user, body)
    return json_success(request)
