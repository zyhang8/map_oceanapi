# from rest_framework import serializers
# from snippets.models import LANGUAGE_CHOICES, STYLE_CHOICES
#
#
# class SnippetSerializer(serializers.Serializer):
#     para1 = serializers.CharField(required=False, allow_blank=True, max_length=100)
#     para2 = serializers.CharField(required=False, allow_blank=True, max_length=100)
#
#     # 利用字段标志控制序列化器渲染到HTML页面时的的显示模板
#     code = serializers.CharField(style={'base_template': 'textarea.html'})
#     linenos = serializers.BooleanField(required=False)
#     language = serializers.ChoiceField(choices=LANGUAGE_CHOICES, default='python')
#     style = serializers.ChoiceField(choices=STYLE_CHOICES, default='friendly')
#
# = serializers.ChoiceField(choices=STYLE_CHOICES, default='friendly')
