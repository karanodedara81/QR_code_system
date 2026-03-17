 HEAD
## Django QR Code Payment Demo

This project is a small Django web application that demonstrates a QR based payment flow for a petrol pump.
It lets you generate QR codes bound to a customer's mobile number, scan and validate them, and inspect a
history of generated QR codes.

### Features

- Generate QR codes from free text combined with a 10 digit mobile number.
- Store QR metadata in the database with a timestamp.
- Upload and scan QR code images to validate against stored records.
- Simple QR history page with optional filtering by mobile number.
- Clean, responsive UI using custom CSS.

### Tech stack

- Python / Django
- SQLite (default Django database)
- `qrcode`, `Pillow`, `pyzbar` for QR code generation and scanning
- HTML templates with Django template language

### Running the project locally

1. Create and activate a virtual environment (optional but recommended).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Apply database migrations:

```bash
python manage.py migrate
```

4. Start the development server:

```bash
python manage.py runserver
```

5. Open `http://127.0.0.1:8000/` in your browser.

### Useful URLs

- Home: `/`
- Generate QR: `/qr/generate/`
- Scan QR: `/qr/scan/`
- QR History: `/qr/history/`

=======
# QR_code_system
>>>>>>> f7f932f049c78995d519032addfff8fce853d136
