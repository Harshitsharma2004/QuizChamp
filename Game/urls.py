from django.urls import path
from .views import (
    register, verify_email, user_login, activate, home, 
    profile, edit_profile, change_password, delete_account, user_logout,
    dashboard, forgot_password, verify_otp, reset_password,
    select_category, start_quiz, quiz_question, submit_answer, quiz_result,general_facts,upload_csv
)

urlpatterns = [
    path("", home, name="home"),
    path("register/", register, name="register"),
    path("verify_email/<int:user_id>/", verify_email, name="verify_email"),
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
    path("activate/<uidb64>/<token>/", activate, name="activate"),
    path("profile/", profile, name="profile"),
    path("edit_profile/", edit_profile, name="edit_profile"),
    path("change_password/", change_password, name="change_password"),
    path("delete_account/", delete_account, name="delete_account"),
    path("dashboard/", dashboard, name="dashboard"),
    path("forgot-password/", forgot_password, name="forgot_password"),
    path("verify-otp/", verify_otp, name="verify_otp"),
    path("reset-password/", reset_password, name="reset_password"),

    # 🎯 Quiz-related
    path("select-category/", select_category, name="select_category"),
    path("start-quiz/", start_quiz, name="start_quiz"),
    path("quiz-question/", quiz_question, name="quiz_question"),
    path("submit-answer/", submit_answer, name="submit_answer"),
    path("result/", quiz_result, name="quiz_result"),

    #facts
    path('facts/', general_facts, name='general_facts'),

    #upload csv
    path('upload-csv/', upload_csv, name='upload_csv'),
]
