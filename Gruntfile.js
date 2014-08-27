module.exports = function(grunt) {

    // Project configuration.
    grunt.initConfig({
        pkg : grunt.file.readJSON('package.json'),
        config : {
            destination : 'public/static/js/lib',
        },
        bower : {
            dev : {
                dest : '<%= config.destination %>',
                options : {
                    stripAffix : false,
                    packageSpecific : {
                        'headroom.js' : {
                            files : [ "dist/headroom.js" ]
                        }
                    }
                }
            }
        },
        clean : [ '<%= config.destination %>' ]
    });

    grunt.loadNpmTasks('grunt-bower');
    grunt.loadNpmTasks('grunt-contrib-clean');

    // Default task(s).
    grunt.registerTask('default', [ 'clean', 'bower' ]);
};