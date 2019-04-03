from hicquery.models import HiCQuery
from rest_framework import serializers
from rest_framework.reverse import reverse
# from django.http import request
class HiCQuerySerializer(serializers.ModelSerializer):
    download_links = serializers.SerializerMethodField()
    links = serializers.SerializerMethodField()
    generate_links = serializers.SerializerMethodField()
    
    class Meta:
        model = HiCQuery
        fields = ('id', 'title', 'create_date', 'bed_file', 'matrix_file',
                  'model_3d_file', 'linker_file', 'links','download_links',
                  'generate_links')
        extra_kwargs = {
            'create_date': {
                'required': False
            },
            'bed_file': {
                'required': False
            },
            'matrix_file': {
                'required': False
            },
            'model_3d_file': {
                'required': False
            },
            'linker_file': {
                'required': False
            }
        }

    def get_links(self, obj):
        request = self.context['request']
        _id = getattr(obj, 'id')
        return request.build_absolute_uri(reverse('hicquery-detail', args=[_id]))
    
    def get_download_links(self, obj):
        request = self.context['request']
        _id = getattr(obj, 'id')
        links = {}
        for i in HiCQuery._ALLOWED_FILE_TYPES:
#            links[i] = HttpRequest.build_absolute_uri(reverse('queryfile-details',
#                               args=[_id,i]))
            links[i] = request.build_absolute_uri(reverse('hicquery-download-file',
                               args=[_id,i]))

        return links

    def get_generate_links(self, obj):
        request = self.context['request']
        _id = getattr(obj, 'id')
        links = {}
        for i in HiCQuery._ALLOWED_GENERATE_TARGET_TYPES:
            links[i] = request.build_absolute_uri(reverse('hicquery-generate-file',
                               args=[_id,i]))
        return links
