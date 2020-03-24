from django.urls import path
from . import views

app_name = 'comment'

urlpatterns = [
    # コメントを提出
    path('post-comment/<int:article_id>/', views.post_comment, name='post_comment'),
    # コメントを削減
    path('delete_comment/<int:id>/',views.delete_comment,name='delete_comment'),
]