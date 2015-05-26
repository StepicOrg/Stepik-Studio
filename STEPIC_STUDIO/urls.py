from django.conf.urls import patterns, include, url
from django.contrib import admin

courseurlpatterns = patterns('',
    url(r'^lesson/(?P<lessonId>[0-9]+)/step/(?P<stepId>[0-9]+)/delete/', 'stepicstudio.views.delete_step'),
    url(r'^lesson/(?P<lessonId>[0-9]+)/step/(?P<stepId>[0-9]+)/(?P<substepId>[0-9]+)/delete/','stepicstudio.views.remove_substep'),
    url(r'^lesson/(?P<lessonId>[0-9]+)/add_step/', 'stepicstudio.views.add_step'),
    url(r'^lesson/(?P<lessonId>[0-9]+)/delete/', 'stepicstudio.views.delete_lesson'),
    url(r'^lesson/(?P<lessonId>[0-9]+)/step/(?P<stepId>[0-9]+)/', 'stepicstudio.views.show_step'),
    url(r'^lesson/(?P<lessonId>[0-9]+)/', 'stepicstudio.views.show_lesson'),

    url(r'^structure', 'stepicstudio.views.show_course_struct'),
    url(r'^stat_info', 'stepicstudio.views.view_stat'),
    url(r'^', 'stepicstudio.views.get_course_page'),
)

urlpatterns = patterns('',

    url(r'^rename_elem/$', 'stepicstudio.views.rename_elem'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^settings/', 'stepicstudio.views.user_profile'),

    url(r'^$', 'stepicstudio.views.index'),
    url(r'^login/$', 'stepicstudio.views.login'),
    url(r'^logout/$', 'stepicstudio.views.logout'),
    url(r'^auth/$', 'stepicstudio.views.auth_view'),

    url(r'^reorder_lists/$', 'stepicstudio.views.reorder_elements'),

    url(r'^stop_recording/$', 'stepicstudio.views.stop_all_recording'),

    url(r'^course/(?P<courseId>[0-9]+)/', include(courseurlpatterns)),

    url(r'^courses/', 'stepicstudio.views.get_user_courses'),

    url(r'^add_lesson/', 'stepicstudio.views.add_lesson'),

    url(r'^showcontent/(?P<substepId>[0-9]+)/', 'stepicstudio.views.video_view'),
    url(r'^showscreencontent/(?P<substepId>[0-9]+)/', 'stepicstudio.views.video_screen_view'),
    #


    # url(r'^course/(?P<courseId>[0-9]+)/add/lesson/', 'stepicstudio.views.add_lesson'),
    url(r'^loggedin/$', 'stepicstudio.views.loggedin'),


)
