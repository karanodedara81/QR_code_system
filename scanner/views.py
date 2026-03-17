from django.shortcuts import render
from .models import QRCode
import qrcode
from django.core.files.storage import FileSystemStorage
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from pathlib import Path
from pyzbar.pyzbar import decode
from PIL import Image


# Update these with your real UPI details
UPI_ID = "karanodedara81@oksbi"
PAYEE_NAME = "Odedara's Petrol Pump"


def generate_qr(request):
    qr_image_url = None
    error = None
    if request.method == 'POST':
        mobile_number = request.POST.get('mobile_number')
        data = request.POST.get('qr_data')  # used as payment note / description
        amount = request.POST.get('amount')

        if not mobile_number or len(mobile_number) != 10 or not mobile_number.isdigit():
            error = 'Invalid mobile number. Please enter a 10-digit number.'
        else:
            # Build a UPI payment URL that UPI apps (GPay, PhonePe, etc.) understand
            upi_params = {
                "pa": UPI_ID,
                "pn": PAYEE_NAME,
                "cu": "INR",
            }

            if amount:
                upi_params["am"] = amount
            if data:
                upi_params["tn"] = data

            query_string = "&".join(
                f"{key}={value}" for key, value in upi_params.items() if value
            )
            upi_url = f"upi://pay?{query_string}"

            qr = qrcode.make(upi_url)
            qr_image_io = BytesIO()
            qr.save(qr_image_io, format='PNG')
            qr_image_io.seek(0)

            qr_storage_path = settings.MEDIA_ROOT / 'qr_codes'
            fs = FileSystemStorage(location=qr_storage_path, base_url='/media/qr_codes/')
            filename = f"upi_{mobile_number}.png"
            qr_image_content = ContentFile(qr_image_io.read(), name=filename)
            fs.save(filename, qr_image_content)
            qr_image_url = fs.url(filename)

            # Store the UPI URL and mobile for history
            QRCode.objects.create(data=upi_url, mobile_number=mobile_number)

    return render(
        request,
        'scanner/generate.html',
        {'qr_image_url': qr_image_url, 'error': error},
    )


def scan_qr(request):
    result = None
    result_lines = None
    error = None
    if request.method == 'POST' and request.FILES.get('qr_image'):
        mobile_number = request.POST.get('mobile_number')
        qr_image = request.FILES['qr_image']

        if not mobile_number or len(mobile_number) != 10 or not mobile_number.isdigit():
            error = 'Invalid mobile number. Please enter a 10-digit number.'
        else:
            fs = FileSystemStorage()
            filename = fs.save(qr_image.name, qr_image)
            image_path = Path(fs.location) / filename
            try:
                image = Image.open(image_path)
                decoded_objects = decode(image)

                if decoded_objects:
                    qr_content = decoded_objects[0].data.decode('utf-8').strip()

                    # Support old "data|mobile" codes and handle other QR types gracefully
                    if '|' in qr_content:
                        qr_data, qr_mobile_number = qr_content.split('|', 1)

                        qr_entry = QRCode.objects.filter(
                            data=qr_data, mobile_number=qr_mobile_number
                        ).first()

                        if qr_entry and qr_mobile_number == mobile_number:
                            result = "Scan Success: Valid QR Code for the provided mobile number"

                            qr_entry.delete()

                            qr_image_path = settings.MEDIA_ROOT / 'qr_codes' / f"{qr_data}_{qr_mobile_number}.png"
                            if qr_image_path.exists():
                                qr_image_path.unlink()

                            if image_path.exists():
                                image_path.unlink()
                        else:
                            result = "Scan Failed: Invalid QR Code or mobile number mismatch"
                    elif qr_content.startswith("upi://pay?"):
                        # Nicely format UPI content lines
                        from urllib.parse import urlparse, parse_qs

                        parsed = urlparse(qr_content)
                        params = parse_qs(parsed.query)
                        pa = params.get("pa", [""])[0]
                        am = params.get("am", [""])[0]
                        cu = params.get("cu", [""])[0]

                        result_lines = []
                        if pa:
                            result_lines.append(f"UPI ID = {pa}")
                        if am:
                            result_lines.append(f"Amount = {am}")
                        if cu:
                            result_lines.append(f"Currency = {cu}")

                        if not result_lines:
                            result = f"Scanned content: {qr_content}"
                        else:
                            result = "Scanned UPI Payment Details"
                    else:
                        # For other QR content, just show the raw text to the user
                        result = f"Scanned content: {qr_content}"
                else:
                    result = "No QR Code detected in the image."
            except Exception as e:
                error = f"Error processing the image: {str(e)}"
            finally:
                if image_path.exists():
                    image_path.unlink()

    return render(
        request,
        'scanner/scan.html',
        {'result': result, 'result_lines': result_lines, 'error': error},
    )


def qr_history(request):
    mobile_number = request.GET.get('mobile_number')
    if mobile_number:
        qrs = QRCode.objects.filter(mobile_number=mobile_number).order_by('-created_at')
    else:
        qrs = QRCode.objects.all().order_by('-created_at')

    context = {
        'qrs': qrs,
        'mobile_number': mobile_number or '',
    }
    return render(request, 'scanner/history.html', context)
