# Refusjonsskjema NTNUI

Based on [webkom/kvittering](https://github.com/webkom/kvittering), configured to run as a normal docker container.

Handles refund requests for [NTNUI](https://ntnui.no).

## Development

This is one docker image that serves both the Python API, and the Next.js/React frontend. This is done by building the webapp as a static site, and serving it as static files through flask. Be aware that some of the python imports does not support development in Windows.

To run just the frontend:

- Install all packages with `yarn`
- Start the server with `yarn dev`
- Export the static files with `yarn build && yarn export`

To run the backend/everything:

- Make a virtual env with `python -m venv venv`
- Enter the env with (Unix) `source venv/bin/activate` or (Windows) `source venv/Scripts/activate`
- Make sure you are using latest pip with `python -m pip install --upgrade pip`
- Install packages with `pip install -r kaaf/req.txt`
- Start the server with `python kaaf/server.py`
- If the frontend is exported (`yarn export`), the webapp will be available at `localhost:5000` when running `server.py`

### Generating PDFs

It might be nice to be able to quickly generate PDFs when developing, without having to start up everything. To do this you can run:

```python
python kaaf/generate-example.py signature.png attachment1.png attachment2.pdf ...
```

Where `signature.png` and `attachmentN.XYZ` are paths to image files.

## Environment variables

| Variable        | Function                                     |
| --------------- | -------------------------------------------- |
| `SERVICE_ACCOUNT_STR` | Google service account string          |
| `MAIL_ADDRESS`  | Set the mail address for generated receipts  |
| `MAIL_PASSWORD` | Password for the mail account                |
| `ENVIRONMENT`   | Set to "production" for sentry errors        |
| `SENTRY_DSN`    | Ingest errors to sentry                      |

While developing locally, you can temporarily add environment variables to the Dockerfile, such as `ENV MAIL_ADDRESS="no-reply@ntnui.no"`.
