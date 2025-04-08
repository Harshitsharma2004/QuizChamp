from django.contrib import admin
from .models import CustomUser, Category, Question,Interest
from django.contrib.auth.admin import UserAdmin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
import csv
import io

from .forms import QuestionCSVUploadForm


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("mobile_no", "dob", "gender", "hobbies", "qualification", "profile_image", "interests")}),
    )
    filter_horizontal = ("interests",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'question_text', 'category']
    list_filter = ['category']

    # Add URL for CSV upload
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-csv/', self.admin_site.admin_view(self.upload_csv), name='upload-questions-csv'),
        ]
        return custom_urls + urls

    # View to handle CSV upload
    def upload_csv(self, request):
        if request.method == "POST":
            form = QuestionCSVUploadForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = form.cleaned_data['csv_file']
                decoded_file = csv_file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))

                for row in reader:
                    category, _ = Category.objects.get_or_create(name=row['category'])
                    Question.objects.create(
                        category=category,
                        question_text=row['question_text'],
                        option1=row['option1'],
                        option2=row['option2'],
                        option3=row['option3'],
                        option4=row['option4'],
                        correct_answer=row['correct_answer']
                    )
                self.message_user(request, "Questions imported successfully!", level=messages.SUCCESS)
                return redirect("..")
        else:
            form = QuestionCSVUploadForm()

        context = {
            'form': form,
            'title': 'Upload CSV for Questions'
        }
        return render(request, "admin/upload_csv.html", context)


# Register user admin
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Interest)