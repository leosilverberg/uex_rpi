module.exports = function(grunt) {
	grunt.initConfig ({
		pkg: grunt.file.readJSON('package.json'),
		sass: {
			dist: {
				files: {
					'scripts/style.css' : 'sass/style.scss'
					}
				}
			},	
		watch: {
			source: {
				files: ['sass/**/*.scss'],
				tasks: ['sass'],
				options:{
					livereload: true,
				}
			}
		}
			
	});
	
			grunt.loadNpmTasks('grunt-sass');
			grunt.loadNpmTasks('grunt-contrib-watch');
			grunt.registerTask('default',['watch']);
}
