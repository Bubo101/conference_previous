from django.http import JsonResponse

from events.models import Conference

from .models import Presentation, Status
from common.json import ModelEncoder
from events.api_views import ConferenceListEncoder
from django.views.decorators.http import require_http_methods
import json
import pika


class PresentationListEncoder(ModelEncoder):
    model = Presentation
    properties = [
        "title",
        # "status",
    ]

    def get_extra_data(self, o):
        return {"status": o.status.name}


class PresentationDetailEncoder(ModelEncoder):
    model = Presentation
    properties = [
        "presenter_name",
        "company_name",
        "presenter_email",
        "title",
        "synopsis",
        "created",
        "status",
        "conference",
    ]

    def get_extra_data(self, o):
        return {"status": o.status.name}

    encoders = {
        "conference": ConferenceListEncoder(),
    }


@require_http_methods(["PUT"])
def api_approve_presentation(request, pk):
    presentation = Presentation.objects.get(id=pk)
    presentation.approve()

    jsondict = json.dumps(
        {
            "presenter_name": presentation.presenter_name,
            "presenter_email": presentation.presenter_email,
            "title": presentation.title,
        }
    )
    parameters = pika.ConnectionParameters(host="rabbitmq")
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue="presentation_approvals")
    channel.basic_publish(
        exchange="",
        routing_key="presentation_approvals",
        body=jsondict,
    )
    connection.close()

    return JsonResponse(
        presentation,
        encoder=PresentationDetailEncoder,
        safe=False,
    )


@require_http_methods(["PUT"])
def api_reject_presentation(request, pk):
    presentation = Presentation.objects.get(id=pk)
    presentation.reject()

    jsondict = json.dumps(
        {
            "presenter_name": presentation.presenter_name,
            "presenter_email": presentation.presenter_email,
            "title": presentation.title,
        }
    )
    parameters = pika.ConnectionParameters(host="rabbitmq")
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue="presentation_rejections")
    channel.basic_publish(
        exchange="",
        routing_key="presentation_rejections",
        body=jsondict,
    )
    connection.close()
    return JsonResponse(
        presentation,
        encoder=PresentationDetailEncoder,
        safe=False,
    )


@require_http_methods(["GET", "POST"])
def api_list_presentations(request, conference_id):
    if request.method == "GET":
        presentations = Presentation.objects.filter(conference=conference_id)
        return JsonResponse(
            {"presentations": presentations},
            encoder=PresentationListEncoder,
        )
    else:
        content = json.loads(request.body)
        try:
            conference = Conference.objects.get(id=conference_id)
            content["conference"] = conference
        except Conference.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid conference"},
                status=400,
            )
        presentation = Presentation.create(**content)

        return JsonResponse(
            presentation,
            encoder=PresentationDetailEncoder,
            safe=False,
        )


@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_presentation(request, pk):
    if request.method == "GET":
        presentation = Presentation.objects.get(id=pk)
        return JsonResponse(
            presentation,
            encoder=PresentationDetailEncoder,
            safe=False,
        )
    elif request.method == "DELETE":
        count, _ = Presentation.objects.filter(id=pk).delete()
        return JsonResponse({"deleted": count > 0})

    else:
        content = json.loads(request.body)
        try:
            if "conference" in content:
                conference = Conference.objects.get(id=content["conference"])
                content["conference"] = conference
        except Conference.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid conference"},
                status=400,
            )
        try:
            if "status" in content:
                status = Status.objects.get(name=content["status"])
                content["status"] = status
        except Status.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid status"},
                status=400,
            )
        Presentation.objects.filter(id=pk).update(**content)
        presentation = Presentation.objects.get(id=pk)

        return JsonResponse(
            presentation,
            encoder=PresentationDetailEncoder,
            safe=False,
        )


# def api_list_presentations(request, conference_id):
#     """
#     Lists the presentation titles and the link to the
#     presentation for the specified conference id.

#     Returns a dictionary with a single key "presentations"
#     which is a list of presentation titles and URLS. Each
#     entry in the list is a dictionary that contains the
#     title of the presentation, the name of its status, and
#     the link to the presentation's information.

#     {
#         "presentations": [
#             {
#                 "title": presentation's title,
#                 "status": presentation's status name
#                 "href": URL to the presentation,
#             },
#             ...
#         ]
#     }
#     """
#     presentations = [
#         {
#             "title": p.title,
#             "status": p.status.name,
#             "href": p.get_api_url(),
#         }
#         for p in Presentation.objects.filter(conference=conference_id)
#     ]
#     return JsonResponse({"presentations": presentations})


# def api_show_presentation(request, pk):
#     """
#     Returns the details for the Presentation model specified
#     by the pk parameter.

#     This should return a dictionary with the presenter's name,
#     their company name, the presenter's email, the title of
#     the presentation, the synopsis of the presentation, when
#     the presentation record was created, its status name, and
#     a dictionary that has the conference name and its URL

#     {
#         "presenter_name": the name of the presenter,
#         "company_name": the name of the presenter's company,
#         "presenter_email": the email address of the presenter,
#         "title": the title of the presentation,
#         "synopsis": the synopsis for the presentation,
#         "created": the date/time when the record was created,
#         "status": the name of the status for the presentation,
#         "conference": {
#             "name": the name of the conference,
#             "href": the URL to the conference,
#         }
#     }
#     """
#     presentation = Presentation.objects.get(id=pk)
#     return JsonResponse(
#         {
#             "presenter_name": presentation.presenter_name,
#             "company_name": presentation.company_name,
#             "presenter_email": presentation.presenter_email,
#             "title": presentation.title,
#             "synopsis": presentation.synopsis,
#             "created": presentation.created,
#             "status": presentation.status.name,
#             "conference": {
#                 "name": presentation.conference.name,
#                 "href": presentation.conference.get_api_url(),
#             },
#         }
#     )
