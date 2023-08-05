from blog.forms import CommentForm, PostForm, UserForm
from blog.models import Category, Comment, Post
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from blogicum.settings import MAX_POSTS_ON_PAGE


class AuthorCheckMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', pk=self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)


class IndexListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = MAX_POSTS_ON_PAGE
    ordering = ['-pub_date', 'title']

    def get_queryset(self):
        now = timezone.now()
        queryset = super().get_queryset().select_related(
            'location', 'author', 'category'
        ).filter(
            pub_date__lte=now,
            is_published=True,
            category__is_published=True
        ).annotate(comment_count=Count('comments'))
        return queryset


class UserListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = MAX_POSTS_ON_PAGE
    ordering = ['-pub_date', 'title']

    def get_queryset(self):
        username = self.kwargs['username']
        profile = get_object_or_404(User, username=username)

        if profile == self.request.user:
            # all posts for the current user's profile
            queryset = super().get_queryset().select_related(
                'location', 'author', 'category'
            ).filter(
                author=profile
            ).annotate(
                comment_count=Count('comments')
            )
            return queryset
        else:
            # published posts for other users
            now = timezone.now()
            return super().get_queryset().select_related(
                'location', 'author', 'category'
            ).filter(
                author=profile,
                pub_date__lte=now,
                is_published=True,
                category__is_published=True
            ).annotate(comment_count=Count('comments'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs['username']
        profile = get_object_or_404(User, username=username)
        context['profile'] = profile
        return context


class CategoryListView(ListView):
    model = Category
    template_name = 'blog/category.html'
    paginate_by = MAX_POSTS_ON_PAGE

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )

        now = timezone.now()

        return self.category.posts.filter(
            is_published=True,
            pub_date__lte=now
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        post = self.object

        # check is_published and author
        if not post.is_published or (
            post.category and not post.category.is_published
        ):
            if request.user.is_authenticated and request.user == post.author:
                return super().dispatch(request, *args, **kwargs)
            raise Http404('Page not found')

        # check pub_time and author
        now = timezone.now()

        if post.pub_date > now and request.user != post.author:
            raise Http404('Page not found')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.all().order_by(
            'created_at'
        )
        return context


class PostUpdateView(AuthorCheckMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'pk': self.kwargs['pk']}
        )


class PostDeleteView(AuthorCheckMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.request.user}
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.commented_post = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.commented_post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'pk': self.commented_post.pk}
        )


class CommentUpdateView(AuthorCheckMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_pk'

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'pk': self.kwargs['pk']}
        )


class CommentDeleteView(AuthorCheckMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_pk'

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'pk': self.kwargs['pk']}
        )


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.object.username}
        )
