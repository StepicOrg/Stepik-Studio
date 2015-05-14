module.exports = function(grunt) {

  // Project configuration.
  grunt.initConfig({
      dirs: {
      handlebars: 'static/extra/hb_templates/'
    },
    watch: {
      handlebars: {
        files: ['<%= handlebars.compile.src %>'],
        tasks: ['handlebars:compile']
      }
    },
    handlebars: {
        compile: {
            src: '<%= dirs.handlebars %>/*.handlebars',
            dest: '<%= dirs.handlebars %>/templates.js'
        }
    },
    uglify: {
      options: {
        banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n'
      },
      build: {
        src: 'src/<%= pkg.name %>.js',
        dest: 'build/<%= pkg.name %>.min.js'
      }
    },

          pkg: grunt.file.readJSON('package.json')
  });

  // Load the plugin that provides the "uglify" task.
  grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-handlebars');

  // Default task(s).
  grunt.registerTask('default', ['watch']);

};