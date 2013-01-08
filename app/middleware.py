class ContentTypeMiddleware(object):

    def process_request(self, request):
        if request.method in ('POST') and not 'boundary=' in request.META['CONTENT_TYPE']:
            request.META['CONTENT_TYPE'] = [c.strip() for c in request.META['CONTENT_TYPE'].split(";") ][0]
        return None