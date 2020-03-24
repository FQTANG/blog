from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Comment
from article.models import ArticlePost
from .forms import CommentForm

#コメントのクリエイト
@login_required(login_url='/userprofile/login/')
def post_comment(request, article_id):
    article=get_object_or_404(ArticlePost,id=article_id)
    if request.method=="POST":
        comment_form=CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment=comment_form.save(commit=False)
            new_comment.article=article
            new_comment.user=request.user
            new_comment.save()
            return redirect(article)
        else:
            return HttpResponse("错误数据，请重新填写")
    else:
        return HttpResponse("发表评论仅接受POST请求。")
#コメントのディレイト
@login_required(login_url='/userprofile/login/')
def delete_comment(request,id): 
    comment =Comment.objects.get(id=id)
    if request.user==comment.user:
        comment.delete() 
        return HttpResponse("删除已完成")
    else:
        return HttpResponse("非授权行为")