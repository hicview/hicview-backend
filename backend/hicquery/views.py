import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../..')
from hicquery.models import HiCQuery, DATA_STORAGE_ROOT
from hicquery.serializers import HiCQuerySerializer

from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import viewsets, filters, status
from rest_framework.decorators import api_view

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import renderers
from django.http import FileResponse
from rest_framework.decorators import action

from django.conf import settings
import os
from wsgiref.util import FileWrapper
from django.http import HttpResponse

from django.core.files import File

import server
from server.resource_map import MDS
from server.resource_map.domain import Domain_Model3D
from server.resource_map import Loader
import uuid
import requests
import mimetypes


class HiCQueryMixins(object):
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )


class HiCQueryViewSet(HiCQueryMixins, viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`,
    `retrieve`, `update`, `destroy` and `download_file` actions
    """
    queryset = HiCQuery.objects.all()
    serializer_class = HiCQuerySerializer

    def get_serializer_context(self):
        return {'request': self.request}

    @action(
        methods=['get'], detail=True, url_path='files/(?P<file_type>[^/.]+)')
    def download_file(self, *args, **kwargs):
        instance = self.get_object()
        _id = kwargs['pk']
        file_type = kwargs['file_type']
        # If the file type not allowed, throw 400
        if file_type not in HiCQuery._ALLOWED_FILE_TYPES:
            return Response(
                data='unsupported file types',
                status=status.HTTP_400_BAD_REQUEST)

        # If the requested file not uploaded or generated, throw 406
        try:
            suffix_name = getattr(instance, file_type).name.split('/')[-1]
        except AttributeError:
            return Response(
                data='Requested file not uploaded or generated',
                status=status.HTTP_406_NOT_ACCEPTABLE)

        filename = os.path.join(settings.MEDIA_ROOT, DATA_STORAGE_ROOT,
                                'query_' + _id, suffix_name)

        binary_flag = is_binary(filename)
        # If the requested file cannot open, throw 404
        try:
            if binary_flag:
                wrapper = FileWrapper(open(filename, 'rb'))
            else:
                wrapper = FileWrapper(open(filename, 'rt'))
        except FileNotFoundError:
            return Response(
                data='Requested file not existed',
                status=status.HTTP_404_NOT_FOUND)

        # Finally return File Response
        response = HttpResponse(wrapper, content_type=file_type)
        response['Content-Length'] = os.path.getsize(filename)
        response[
            'Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(
                filename)

        return response

    @action(
        methods=['get'],
        detail=True,
        url_path='generate/(?P<file_type>[^/.]+)')
    def generate_file(self, *args, **kwargs):
        instance = self.get_object()
        _id = kwargs['pk']
        file_type = kwargs['file_type']
        # If the file type not allowed, throw 400
        if file_type not in HiCQuery._ALLOWED_GENERATE_TARGET_TYPES:
            return Response(
                data='Requested file type cannot assigned as generate target',
                status=status.HTTP_400_BAD_REQUEST)
        # Get save file path
        instance_file_paths = self.get_instance_file_paths(instance, _id)
        return self.generate_dispatcher(instance, file_type,
                                        instance_file_paths)


#        return Response(
#            data=instance_file_paths, status=status.HTTP_201_CREATED)

    def get_instance_file_paths(self, instance, _id):
        instance_file_paths = {}
        for ft in HiCQuery._ALLOWED_FILE_TYPES:
            if getattr(instance, ft).name == '':
                fn = None
            else:
                try:
                    suffix_name = getattr(instance, ft).name.split('/')[-1]
                    fn = os.path.join(settings.BASE_DIR, DATA_STORAGE_ROOT,
                                      'query_' + _id, suffix_name)
                except AttributeError:
                    fn = None
            instance_file_paths[ft] = fn
        return instance_file_paths

    def generate_dispatcher(self, instance, target_file, instance_file_paths):
        file_field = getattr(instance, target_file)
        file_path_prefix = os.path.join(DATA_STORAGE_ROOT,
                                        'query_' + instance.pk.hex)
        print('file prefix', file_path_prefix)

        file_suffix_name = getattr(
            self, 'generate_' + target_file)(instance_file_paths)
        file_field.name = file_suffix_name
        print(file_field.name)
        instance.save()
        return Response(data='data generated', status=status.HTTP_201_CREATED)

    def generate_model_3d_file(self, instance_file_paths):
        """
        Return the name generated 3D model file
        ----------
        @params
        file paths of source files
        @return
        file name of output file
        """
        try:
            for i in HiCQuery._MODEL_3D_FILE_GENERATE_SOURCE:
                if instance_file_paths[i] == None:
                    raise ValueError
        except ValueError:
            return Response(
                data=
                'Requested file cannot be generated, lack required source file',
                status=status.HTTP_400_BAD_REQUEST)
        source_file = instance_file_paths[HiCQuery.
                                          _MODEL_3D_FILE_GENERATE_SOURCE[0]]
        dm3 = Domain_Model3D()
        dm3.generate_data(source_file, 'matrix_3_columns_loader', MDS)
        save_path = '/'.join(
            source_file.split('/')[:-1] + [
                uuid.uuid4().hex + '_model3d',
            ])
        dm3.loader.write_data(save_path, suffix='.npz')
        return dm3.loader.filepath.split('/')[-1]


def is_binary(filename):
    """ 
    Return true if the given filename appears to be binary.
    File is considered to be binary if it contains a NULL byte.
    FIXME: This approach incorrectly reports UTF-16 as binary.
    """
    with open(filename, 'rb') as f:
        for block in f:
            if b'\0' in block:
                return True
    return False


