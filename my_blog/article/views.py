from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import ArticlePost
from .forms import ArticlePostForm
import markdown
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from comment.models import Comment
from comment.forms import CommentForm
from .models import ArticleColumn

# Create your views here.
def article_list(request):
    search = request.GET.get('search')
    order = request.GET.get('order')
    column = request.GET.get('column')
    tag = request.GET.get('tag')
    article_list = ArticlePost.objects.all()
    if search:
        article_list = article_list.filter(
            Q(title__icontains=search) |
            Q(body__icontains=search)
        )
    else:
        search = ''
    if column is not None and column.isdigit():
        article_list = article_list.filter(column=column)
    if tag and tag != 'None':
        article_list = article_list.filter(tags__name__in=[tag])
    if order == 'total_views':
        article_list = article_list.order_by('-total_views')
    paginator = Paginator(article_list, 3)
    page = request.GET.get('page')
    articles = paginator.get_page(page)
    context = { 'articles': articles, 'order': order, 'search': search,'column': column,'tag': tag,}
    return render(request, 'article/list.html', context)

    
def article_detail(request, id):
    article = ArticlePost.objects.get(id=id)
    comments = Comment.objects.filter(article=id)
    comment_form = CommentForm()
    article.total_views += 1
    article.save(update_fields=['total_views'])
    md = markdown.Markdown(
        extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
        ]
    )
    article.body = md.convert(article.body)
    context = { 'article': article, 'toc': md.toc,'comments': comments,'comment_form': comment_form}
    return render(request, 'article/detail.html', context)
    
@login_required(login_url='/userprofile/login/')
def article_create(request):
    login_user_id = request.user.id
    if request.method == "POST":
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            new_article = article_post_form.save(commit=False)
            new_article.author = User.objects.get(id=login_user_id )
            if request.POST['column'] != 'none':
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])
            new_article.save()
            article_post_form.save_m2m()
            return redirect("article:article_list")
        else:
            return HttpResponse("提交内容不合法，请重新填写。")
    else:
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        context = { 'article_post_form': article_post_form, 'columns': columns }
        return render(request, 'article/create.html', context)
        
@login_required(login_url='/userprofile/login/')
def article_update(request, id):
    login_user_id = request.user.id
    article = ArticlePost.objects.get(id=id)
    if request.method == "POST":
        if article.author!=User.objects.get(id=login_user_id):
            return HttpResponse("不能修改不是你写的文章")
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            article.title = request.POST['title']
            article.body = request.POST['body']
            if request.POST['column'] != 'none':
                article.column = ArticleColumn.objects.get(id=request.POST['column'])
            else:
                article.column = None
            article.tags.set(*request.POST.get('tags').split(','), clear=True)
            article.save()
            return redirect("article:article_detail", id=id)
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    else:
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        context = { 'article': article, 'article_post_form': article_post_form,'columns': columns,}
        return render(request, 'article/update.html', context)

@login_required(login_url='/userprofile/login/')        
def article_safe_delete(request, id):
    login_user_id = request.user.id
    if request.method == 'POST':
        article = ArticlePost.objects.get(id=id)
        if article.author!=User.objects.get(id=login_user_id):
            return HttpResponse("不能删除不是你写的文章")
        article.delete()
        return redirect("article:article_list")
    else:
        return HttpResponse("仅允许post请求")