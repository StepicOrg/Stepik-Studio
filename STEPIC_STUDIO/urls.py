from django.conf.urls import patterns, include, url
from django.contrib import admin

courseurlpatterns = patterns(
    '',
    url(r'^lesson/(?P<lesson_id>[0-9]+)/step/(?P<step_id>[0-9]+)/delete/', 'stepicstudio.views.delete_step'),
    url(r'^lesson/(?P<lesson_id>[0-9]+)/step/(?P<step_id>[0-9]+)/(?P<substep_id>[0-9]+)/delete/',
        'stepicstudio.views.remove_substep'),
    url(r'^lesson/(?P<lesson_id>[0-9]+)/add_step/', 'stepicstudio.views.add_step'),
    url(r'^lesson/(?P<lesson_id>[0-9]+)/delete/', 'stepicstudio.views.delete_lesson'),
    url(r'^lesson/(?P<lesson_id>[0-9]+)/step/(?P<step_id>[0-9]+)/', 'stepicstudio.views.show_step'),
    url(r'^lesson/(?P<lesson_id>[0-9]+)/', 'stepicstudio.views.show_lesson'),

    url(r'^structure', 'stepicstudio.views.show_course_struct'),
    url(r'^stat_info', 'stepicstudio.views.view_stat'),
    url(r'^', 'stepicstudio.views.get_course_page'),
)

urlpatterns = patterns(
    '',
    url(r'^rename_elem/$', 'stepicstudio.views.rename_elem'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^settings/update_substep_template/', 'stepicstudio.views.update_substep_tmpl'),
    url(r'^settings/', 'stepicstudio.views.user_profile'),

    url(r'^$', 'stepicstudio.views.index'),
    url(r'^login/$', 'stepicstudio.views.login'),
    url(r'^logout/$', 'stepicstudio.views.logout'),
    url(r'^auth/$', 'stepicstudio.views.auth_view'),

    url(r'^reorder_lists/$', 'stepicstudio.views.reorder_elements'),

    url(r'^stop_recording/', 'stepicstudio.views.stop_all_recording'),

    url(r'^course/(?P<course_id>[0-9]+)/', include(courseurlpatterns)),

    url(r'^courses/', 'stepicstudio.views.get_user_courses'),
    url(r'^unlock_all/', 'stepicstudio.views.clear_all_locked_substeps'),

    url(r'^add_lesson/', 'stepicstudio.views.add_lesson'),

    url(r'^all_notes/(?P<course_id>[0-9]+)/', 'stepicstudio.views.generate_notes_page'),

    url(r'^showcontent/(?P<substep_id>[0-9]+)/', 'stepicstudio.views.video_view'),
    url(r'^showscreencontent/(?P<substep_id>[0-9]+)/', 'stepicstudio.views.video_screen_view'),

    url(r'^create_montage/(?P<substep_id>[0-9]+)/', 'stepicstudio.views.montage'),
    url(r'^create_step_montage/(?P<step_id>[0-9]+)/', 'stepicstudio.views.step_montage'),
    url(r'^show_montage/(?P<substep_id>[0-9]+)/', 'stepicstudio.views.show_montage'),

    url(r'^substep_status/(?P<substep_id>[0-9]+)/', 'stepicstudio.views.substep_status'),

    url(r'^loggedin/$', 'stepicstudio.views.loggedin'),
    url(r'^notes/step/(?P<step_id>[0-9]+)/', 'stepicstudio.views.notes'),
)

handler500 = 'stepicstudio.views.error500_handler'
