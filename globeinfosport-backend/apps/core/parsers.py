"""Multipart forms with a JSON payload retain lists, booleans and nulls."""
import json

from rest_framework.exceptions import ParseError
from rest_framework.parsers import DataAndFiles, MultiPartParser


class EditorialMultiPartParser(MultiPartParser):
    def parse(self, stream, media_type=None, parser_context=None):
        result = super().parse(stream, media_type, parser_context)
        if "payload" not in result.data:
            return result
        try:
            payload = json.loads(result.data["payload"])
        except (TypeError, ValueError) as exc:
            raise ParseError("Le formulaire contient un JSON invalide.") from exc
        if not isinstance(payload, dict):
            raise ParseError("Le formulaire doit contenir un objet JSON.")
        # A plain dict deliberately avoids QueryDict's HTML list semantics.
        return DataAndFiles(payload, {key: result.files[key] for key in result.files})
