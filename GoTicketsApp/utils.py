import qrcode
from PIL import Image
import json  # Ensure this line is included

def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    return img

def serialize_ticket_data(ticket):
    data = {
        "ticket_id": ticket.id,
        "event_name": ticket.event.name,
        "date_time": ticket.event.date_time.strftime('%Y-%m-%d %H:%M'),
        "seat_number": ticket.seat_number,
        # Add other fields as necessary
    }
    return json.dumps(data)  # This uses the json module
