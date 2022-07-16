from django.http import JsonResponse
from common.json import ModelEncoder
from .models import Attendee, ConferenceVO, AccountVO
from django.views.decorators.http import require_http_methods
import json


class ConferenceVODetailEncoder(ModelEncoder):
    model = ConferenceVO
    properties = ["name", "import_href"]


class AttendeeListEncoder(ModelEncoder):
    model = Attendee
    properties = ["name"]


class AttendeeDetailEncoder(ModelEncoder):
    model = Attendee
    properties = [
        "email",
        "name",
        "company_name",
        "created",
        "conference",
    ]
    encoders = {"conference": ConferenceVODetailEncoder()}

    def get_extra_data(self, o):
        count = AccountVO.objects.filter(email=o.email).count()
        print(count)
        if count > 0:
            return {"has_account": True, "conference": o.conference.name}
        else:
            return {"has_account": False, "conference": o.conference.name}

        # Get the count of AccountVO objects with email equal to o.email
        # Return a dictionary with "has_account": True if count > 0
        # Otherwise, return a dictionary with "has_account": False


@require_http_methods(["GET", "POST"])
def api_list_attendees(request, conference_vo_id=None):
    if request.method == "GET":
        attendees = Attendee.objects.filter(conference=conference_vo_id)
        return JsonResponse(
            {"attendees": attendees},
            encoder=AttendeeListEncoder,
        )

    else:
        content = json.loads(request.body)

        try:
            # THIS LINE IS ADDED

            # conference = ConferenceVO.objects.get(id=conference_vo_id)
            # conference_href = content["conference"]

            # # THIS LINE CHANGES TO ConferenceVO and import_href
            conference_href = content["conference"]
            conference = ConferenceVO.objects.get(import_href=conference_href)
            content["conference"] = conference
            # updates content dictionary to the conference object (which has name, url)
            # and replaces the conference id

            # another way to do it since the poll is filling the model
            # conference = ConferenceVO.objects.get(id=conference_vo_id)
            # content["conference"] = conference

            ## THIS CHANGES TO ConferenceVO
        except ConferenceVO.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid conference id"},
                status=400,
            )

        attendee = Attendee.objects.create(**content)
        return JsonResponse(
            attendee,
            encoder=AttendeeDetailEncoder,
            safe=False,
        )


# deleted to microserve, look at differences
# # Get the Conference object and put it in the content dict
# try:
#     conference = Conference.objects.get(id=conference_vo_id)
#     content["conference"] = conference
# except Conference.DoesNotExist:
#     return JsonResponse(
#         {"message": "Invalid conference id"},
#         status=400,
#     )


@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_attendee(request, pk):
    if request.method == "GET":
        attendee = Attendee.objects.get(id=pk)
        return JsonResponse(
            attendee,
            encoder=AttendeeDetailEncoder,
            safe=False,
        )
    elif request.method == "DELETE":
        count, _ = Attendee.objects.filter(id=pk).delete()
        return JsonResponse({"deleted": count > 0})

    else:
        content = json.loads(request.body)
        try:
            if "conference" in content:
                conference = ConferenceVO.objects.get(id=content["conference"])
                content["conference"] = conference
        except ConferenceVO.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid conference id"},
                status=400,
            )

        Attendee.objects.filter(id=pk).update(**content)

        # copied from get detail
        attendee = Attendee.objects.get(id=pk)
        return JsonResponse(
            attendee,
            encoder=AttendeeDetailEncoder,
            safe=False,
        )

        # try:
        #     if "conference" in content:
        #         conference = Conference.objects.get(conference=content["name"])
        #         content["id"] = conference
        # except Conference.DoesNotExist:
        #     return JsonResponse(
        #         {"message": "Invalid conference"},
        #         status=400,
        #     )


# def api_list_attendees(request, conference_id):

#     """
#     Lists the attendees names and the link to the attendee
#     for the specified conference id.

#     Returns a dictionary with a single key "attendees" which
#     is a list of attendee names and URLS. Each entry in the list
#     is a dictionary that contains the name of the attendee and
#     the link to the attendee's information.

#     {
#         "attendees": [
#             {
#                 "name": attendee's name,
#                 "href": URL to the attendee,
#             },
#             ...
#         ]
#     }
#     """
#     response = []
#     attendees = Attendee.objects.filter(conference=conference_id)
#     for attendee in attendees:
#         response.append(
#             {
#                 "attendees": [
#                     {
#                         "name": attendee.name,
#                         "href": attendee.get_api_url(),
#                     }
#                 ]
#             }
#         )

#     return JsonResponse({"attendees": response})


# def api_show_attendee(request, pk):
#     """
#     Returns the details for the Attendee model specified
#     by the pk parameter.

#     This should return a dictionary with email, name,
#     company name, created, and conference properties for
#     the specified Attendee instance.

#     {
#         "email": the attendee's email,
#         "name": the attendee's name,
#         "company_name": the attendee's company's name,
#         "created": the date/time when the record was created,
#         "conference": {
#             "name": the name of the conference,
#             "href": the URL to the conference,
#         }
#     }
#     """
#     attendee = Attendee.objects.get(id=pk)
#     return JsonResponse(
#         {
#             "email": attendee.email,
#             "name": attendee.name,
#             "company_name": attendee.company_name,
#             "created": attendee.created,
#             "conference": {
#                 "name": attendee.conference.name,
#                 "href": attendee.conference.get_api_url(),
#             },
#         }
#     )
