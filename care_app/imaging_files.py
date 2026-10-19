"""Validate and label a complete imaging upload batch before any API request."""
import base64
import hashlib
import io
from pathlib import PurePosixPath

from pypdf import PdfReader
from pypdf.errors import PdfReadError

MAX_FILES = 10
MAX_FILE_BYTES = 10 * 1024 * 1024
MAX_BATCH_BYTES = 30 * 1024 * 1024
MAX_PDF_PAGES = 30
MAX_BATCH_PAGES = 60


def normalize_files(files):
    if not files or len(files) > MAX_FILES:
        raise ValueError('Choose between 1 and 10 imaging files.')
    if sum(len(f['data']) for f in files) > MAX_BATCH_BYTES:
        raise ValueError('The combined upload must be 30 MB or smaller.')
    names, seen, result = set(), set(), []
    for file in files:
        original = PurePosixPath(file['name'].replace('\\', '/')).name
        data = file['data']
        if not data or len(data) > MAX_FILE_BYTES:
            raise ValueError(original + ': choose a nonempty file of 10 MB or less.')
        suffix = PurePosixPath(original).suffix.lower()
        if suffix not in {'.png', '.jpg', '.jpeg', '.webp', '.pdf'}:
            raise ValueError(original + ': use a PDF, PNG, JPEG or WebP file.')
        digest = hashlib.sha256(data).hexdigest()
        if (original, digest) in seen:
            continue
        seen.add((original, digest))
        name = original
        counter = 2
        while name in names:
            name = f'{PurePosixPath(original).stem} ({counter}){suffix}'
            counter += 1
        names.add(name)
        result.append({'name': name, 'data': data, 'digest': digest})
    return result


def batch_digest(files):
    files = normalize_files(files)
    # A rename changes source labels; changing only selection order does not.
    value = '\n'.join(sorted(f['name'] + ':' + f['digest'] for f in files))
    return hashlib.sha256(value.encode()).hexdigest()


def prepare_documents(files, image_encoder):
    content, metadata, total_pages = [], [], 0
    for source in normalize_files(files):
        name, data = source['name'], source['data']
        content.append({'type': 'input_text', 'text': 'Source filename: ' + name})
        if name.lower().endswith('.pdf'):
            if not data.startswith(b'%PDF-'):
                raise ValueError(name + ': this file is not a valid PDF.')
            try:
                reader = PdfReader(io.BytesIO(data))
                if reader.is_encrypted:
                    raise ValueError(name + ': password-protected PDFs are not supported.')
                pages = len(reader.pages)
                if not 1 <= pages <= MAX_PDF_PAGES:
                    raise ValueError(name + ': use a PDF with 1–30 pages.')
            except (PdfReadError, OSError, KeyError, TypeError) as exc:
                raise ValueError(name + ': the PDF could not be read. Try exporting it again.') from exc
            content.append({'type': 'input_file', 'filename': name,
                            'file_data': 'data:application/pdf;base64,' + base64.b64encode(data).decode()})
        else:
            pages = 1
            content.append({'type': 'input_image', 'image_url': image_encoder(data), 'detail': 'high'})
        total_pages += pages
        if total_pages > MAX_BATCH_PAGES:
            raise ValueError('The combined upload must contain no more than 60 pages/images.')
        metadata.append({'filename': name, 'pages': pages,
                         'format': 'PDF' if name.lower().endswith('.pdf') else 'Image'})
    return content, metadata
