from django.conf.urls import patterns, include, url
from django.contrib import admin

courseurlpatterns = patterns('',
    url(r'^lesson/(?P<lessonId>[0-9]+)/step/(?P<stepId>[0-9]+)/record/recording/', 'stepicstudio.views.recording_page'),
    url(r'^lesson/(?P<lessonId>[0-9]+)/step/(?P<stepId>[0-9]+)/stop/', 'stepicstudio.views.stop_recording'),
    url(r'^lesson/(?P<lessonId>[0-9]+)/step/(?P<stepId>[0-9]+)/record/', 'stepicstudio.views.start_new_step_recording'),
    url(r'^lesson/(?P<lessonId>[0-9]+)/step/(?P<stepId>[0-9]+)/delete/', 'stepicstudio.views.delete_step'),
    url(r'^lesson/(?P<lessonId>[0-9]+)/step/(?P<stepId>[0-9]+)/(?P<substepId>[0-9]+)/delete/','stepicstudio.views.remove_substep'),
    url(r'^lesson/(?P<lessonId>[0-9]+)/add_step/', 'stepicstudio.views.add_step'),
    url(r'^lesson/(?P<lessonId>[0-9]+)/delete/', 'stepicstudio.views.delete_lesson'),
    url(r'^lesson/(?P<lessonId>[0-9]+)/step/(?P<stepId>[0-9]+)/', 'stepicstudio.views.show_step'),
    url(r'^lesson/(?P<lessonId>[0-9]+)/', 'stepicstudio.views.show_lesson'),

    url(r'^structure', 'stepicstudio.views.show_course_struct'),
    url(r'^', 'stepicstudio.views.get_course_page'),
)

urlpatterns = patterns('',
    # Examples:
    #url(r'^$', 'STEPIC_STUDIO.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^lol/', 'stepicstudio.views.video_view'),

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
    #


    # url(r'^course/(?P<courseId>[0-9]+)/add/lesson/', 'stepicstudio.views.add_lesson'),
    url(r'^loggedin/$', 'stepicstudio.views.loggedin'),


)
