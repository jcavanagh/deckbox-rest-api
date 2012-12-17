/**
 * Node.js based build script for LenderPlus Mobile
 *
 * How it Works:
 * - The build is in-place - the build directory is just temporary storage
 * - 
 */
(function() {
    //Node modules and environment
    var path = require('path')
        ,fs = require('fs')
        ,fsx = require('fs-extra')
        ,util = require('util')
        ,childProcess = require('child_process')
        ,spawn = childProcess.spawn
        ,exec = childProcess.exec
        ,isWindows = !!process.platform.match(/^win/)
        //Reference all files from the directory that this script exists in, not from where the build command was executed
        ,rootPath = path.resolve(__dirname);

    //Paths
    //Phonegap
    var PHONEGAP_VERSION = '2.2.0';

    //Directories
    var SRC_DIR = path.join(rootPath, 'src')
        ,BUILD_DIR = path.join(SRC_DIR, 'build')
        ,VENDOR_DIR = path.join(rootPath, 'vendor')
        ,PHONEGAP_DIR = path.join(rootPath, 'phonegap')
        ,BUILD_ASSETS_DIR = path.join(BUILD_DIR, 'default', 'production')
        ,PHONEGAP_VENDOR_DIR = path.join(VENDOR_DIR, 'phonegap')
        ,PHONEGAP_JS_FILENAME = 'cordova-' + PHONEGAP_VERSION + '.js'
        ,ANDROID_WWW_DIR = path.join(PHONEGAP_DIR, 'android', 'assets', 'www')
        ,ANDROID_PHONEGAP_JS = path.join(PHONEGAP_VENDOR_DIR, 'lib', 'android', PHONEGAP_JS_FILENAME);

    //Sencha tooling
    var SENCHA_CMD_LINUX64 = path.join(rootPath, 'vendor', 'sencha-cmd', 'linux64')
        ,SENCHA_CMD_WIN = path.join(rootPath, 'vendor', 'sencha-cmd', 'win32')
        //Path to Sencha executable is different per platform
        ,SENCHA = isWindows ? path.join(SENCHA_CMD_WIN, 'sencha.exe') : path.join(SENCHA_CMD_LINUX64, 'sencha');

    //Set Sencha environment variables
    process.env['SENCHA_CMD_3_0_0'] = isWindows ? SENCHA_CMD_WIN : SENCHA_CMD_LINUX64;

    //------ BUILD ------
    //Clean
    console.log('------ CLEAN ------');
    fsx.removeSync(BUILD_DIR);
    fs.mkdirSync(BUILD_DIR);
    fsx.removeSync(ANDROID_WWW_DIR);
    fs.mkdirSync(ANDROID_WWW_DIR);

    //Minify and package
    console.log('------ MINIFY ------');

    //Change to app dir
    process.chdir(SRC_DIR);

    var minify = exec(SENCHA + ' app build production', copyBuildArtifacts);

    //Hook into minify process streams and relay to console
    minify.stdout.on('data', function(data) {
        console.log(data.toString('utf8').trim());
    });

    minify.stderr.on('data', function(data) {
        console.log(data.toString('utf8').trim());
    });

    //Copy minified app from build dir to Phonegap dirs
    function copyBuildArtifacts(cb) {
        console.log('------ COPY ------');

        //Create a simple default callback that will log an error if we get one
        var cb = cb || function(err){ if(!!err) { console.log(err); } };

        //Copy Android assets
        fsx.copy(BUILD_ASSETS_DIR, ANDROID_WWW_DIR, function() {
            //Copy platform Phonegap JS after base assets
            fsx.copy(ANDROID_PHONEGAP_JS, path.join(ANDROID_WWW_DIR, PHONEGAP_JS_FILENAME), cb);
        });
    }
})();
