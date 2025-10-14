from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import Http404
from django.views import generic

# pip install django-braces
from braces.views import SelectRelatedMixin

from . import forms, models
from django.contrib.auth import get_user_model

User = get_user_model()


class PostList(SelectRelatedMixin, generic.ListView):
    model = models.Post
    select_related = ("user", "group")


class UserPosts(generic.ListView):
    model = models.Post
    template_name = "post/user_post_list.html"

    def get_queryset(self):
        username = self.kwargs.get("username")
        try:
            self.post_user = User.objects.prefetch_related("posts").get(
                username__iexact=username
            )
        except User.DoesNotExist:
            raise Http404
        else:
            return self.post_user.posts.all()  # Use the correct related_name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post_user"] = self.post_user
        return context


class PostDetail(SelectRelatedMixin, generic.DetailView):
    model = models.Post
    select_related = ("user", "group")

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(
            user__username__iexact=self.kwargs.get("username")
        )


class CreatePost(LoginRequiredMixin, SelectRelatedMixin, generic.CreateView):
    model = models.Post
    fields = ("message", "group")

    def form_valid(self, form):
        form.instance.user = self.request.user

        # Prevent duplicate posts by the same user
        if models.Post.objects.filter(user=self.request.user, message=form.instance.message).exists():
            form.add_error("message", "You have already posted this message.")
            return self.form_invalid(form)

        return super().form_valid(form)


class DeletePost(LoginRequiredMixin, SelectRelatedMixin, generic.DeleteView):
    model = models.Post
    select_related = ("user", "group")
    success_url = reverse_lazy("post:all")

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user_id=self.request.user.id)

    def delete(self, *args, **kwargs):
        messages.success(self.request, "Post Deleted")
        return super().delete(*args, **kwargs)
