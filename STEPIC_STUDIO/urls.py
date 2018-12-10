from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import RedirectView

courseurlpatterns = patterns(
    '',
    url(r'^add-lesson/', 'stepicstudio.views.add_lesson'),
    url(r'^lesson/(?P<lesson_id>[0-9]+)/step/(?P<step_id>[0-9]+)/delete/', 'stepicstudio.views.delete_step'),
    url(r'^lesson/(?P<lesson_id>[0-9]+)/step/(?P<step_id>[0-9]+)/(?P<substep_id>[0-9]+)/delete/',
        'stepicstudio.views.delete_substep'),
    url(r'^lesson/(?P<lesson_id>[0-9]+)/add_step/', 'stepicstudio.views.add_step'),
    url(r'^lesson/(?P<lesson_id>[0-9]+)/delete/', 'stepicstudio.views.delete_lesson'),
    url(r'^lesson/(?P<lesson_id>[0-9]+)/step/(?P<step_id>[0-9]+)/stop', 'stepicstudio.views.stop_recording'),
    url(r'^lesson/(?P<lesson_id>[0-9]+)/step/(?P<step_id>[0-9]+)/export-prproj',
        'stepicstudio.views.export_step_to_prproj'),
    url(r'^lesson/(?P<lesson_id>[0-9]+)/step/(?P<step_id>[0-9]+)/', 'stepicstudio.views.show_step'),
    url(r'^lesson/(?P<lesson_id>[0-9]+)/export-prproj', 'stepicstudio.views.export_lesson_to_prproj'),
    url(r'^lesson/(?P<lesson_id>[0-9]+)/', 'stepicstudio.views.show_lesson'),

    url(r'^structure', 'stepicstudio.views.show_course_struct'),
    url(r'^stat_info', 'stepicstudio.views.view_stat'),
    url(r'^export-prproj', 'stepicstudio.views.export_course_to_prproj'),
    url(r'^', 'stepicstudio.views.get_course_page'),
)

urlpatterns = patterns(
    '',
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/icons/favicon.ico', permanent=True)),

    url(r'^rename-elem/$', 'stepicstudio.views.rename_elem'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^settings/update_substep_template/', 'stepicstudio.views.update_substep_tmpl'),
    url(r'^settings/', 'stepicstudio.views.user_profile'),

    url(r'^$', 'stepicstudio.views.index'),
    url(r'^login/$', 'stepicstudio.views.login'),
    url(r'^logout/$', 'stepicstudio.views.logout'),
    url(r'^auth/$', 'stepicstudio.views.auth_view'),

    url(r'^reorder-lists/$', 'stepicstudio.views.reorder_elements'),

    url(r'^stop-recording/', 'stepicstudio.views.stop_all_recording'),

    url(r'^course/(?P<course_id>[0-9]+)/', include(courseurlpatterns)),
    url(r'^courses/', 'stepicstudio.views.get_user_courses'),
    url(r'^unlock-all/', 'stepicstudio.views.clear_all_locked_substeps'),
    url(r'^all-notes/(?P<course_id>[0-9]+)/', 'stepicstudio.views.generate_notes_page'),

    url(r'^showcontent/(?P<substep_id>[0-9]+)/', 'stepicstudio.views.video_view'),
    url(r'^showscreencontent/(?P<substep_id>[0-9]+)/', 'stepicstudio.views.video_screen_view'),

    url(r'^create_montage/(?P<substep_id>[0-9]+)/', 'stepicstudio.views.montage'),
    url(r'^create-step-montage/(?P<step_id>[0-9]+)/', 'stepicstudio.views.step_montage'),
    url(r'^create-lesson-montage/(?P<lesson_id>[0-9]+)/', 'stepicstudio.views.lesson_montage'),
    url(r'^show-montage/(?P<substep_id>[0-9]+)/', 'stepicstudio.views.show_montage'),

    url(r'^loggedin/$', 'stepicstudio.views.loggedin'),
    url(r'^notes/step/(?P<step_id>[0-9]+)/', 'stepicstudio.views.notes'),

    url(r'^substep-statuses/', 'stepicstudio.views.substep_statuses'),
    url(r'^autofocus-camera/', 'stepicstudio.views.autofocus_camera'),
)

handler500 = 'stepicstudio.views.error500_handler'
