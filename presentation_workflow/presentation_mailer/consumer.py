import json
import pika
from pika.exceptions import AMQPConnectionError
import django
import os
import sys
import time
from django.core.mail import send_mail


sys.path.append("")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "presentation_mailer.settings")
django.setup()

while True:
    try:

        def process_approval(ch, method, properties, body):
            info = json.loads(body)
            print(info, "-")
            name = info["presenter_name"]
            title = info["title"]
            presenter_email = info["presenter_email"]
            subject = "Presentation Accepted!"
            message = f"{name}, we're happy to tell you your presentation {title} has been accepted."
            from_email = "admin@conference.go"

            send_mail(
                subject,
                message,
                from_email,
                [presenter_email],
                fail_silently=False,
            )

        def process_rejected(ch, method, properties, body):
            info = json.loads(body)
            name = info["presenter_name"]
            title = info["title"]
            presenter_email = info["presenter_email"]
            subject = "Presentation Rejected"
            message = f"{name}, we're sorry to tell you your presentation {title} has been rejected."
            from_email = "admin@conference.go"

            send_mail(
                subject,
                message,
                from_email,
                [presenter_email],
                fail_silently=False,
            )

        parameters = pika.ConnectionParameters(host="rabbitmq")
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        channel.queue_declare(queue="presentation_approvals")
        channel.basic_consume(
            queue="presentation_approvals",
            on_message_callback=process_approval,
            auto_ack=True,
        )
        channel.queue_declare(queue="presentation_rejections")
        channel.basic_consume(
            queue="presentation_rejections",
            on_message_callback=process_rejected,
            auto_ack=True,
        )
        channel.start_consuming()

    except AMQPConnectionError:
        print("Could not connect to RabbitMQ")
        time.sleep(2.0)
