importPackage(java.lang);
importPackage(java.io);
importPackage(javax.script);
importPackage(com.sencha.util);
importPackage(com.sencha.util.filters);
importPackage(com.sencha.logging);
importPackage(com.sencha.exceptions);
importPackage(com.sencha.command);

var _logger = SenchaLogManager.getLogger("app-upgrade");

var JSON = new (function () {
    var useHasOwn = !!{}.hasOwnProperty,
        pad = function (n) {
            return n < 10 ? "0" + n : n;
        },
        doDecode = function (json) {
            return eval("(" + json + ')');
        },
        doEncode = function (o) {
            if (typeof o == 'undefined' || o === null) {
                return "null";
            } else if (Object.prototype.toString.call(o) === '[object Array]') {
                return encodeArray(o);
            } else if (Object.prototype.toString.call(o) === '[object Date]') {
                return JSON.encodeDate(o);
            } else if (typeof o == 'string') {
                return encodeString(o);
            } else if (typeof o == 'number') {
                //don't use isNumber here, since finite checks happen inside isNumber
                return isFinite(o) ? String(o) : "null";
            } else if (typeof o == 'boolean') {
                return String(o);
            } else if (typeof o == 'object') {
                return encodeObject(o);
            } else if (typeof o === "function") {
                return encodeString(o.toString());
            }
            return 'undefined';
        },
        m = {
            "\b":'\\b',
            "\t":'\\t',
            "\n":'\\n',
            "\f":'\\f',
            "\r":'\\r',
            '"':'\\"',
            "\\":'\\\\',
            '\x0b':'\\u000b' //ie doesn't handle \v
        },
        charToReplace = /[\\\"\x00-\x1f\x7f-\uffff]/g,
        encodeString = function (s) {
            return '"' + s.replace(charToReplace, function (a) {
                var c = m[a];
                return (typeof c === 'string') ? c : ('\\u' + ('0000' + a.charCodeAt(0).toString(16)).slice(-4));
            }) + '"';
        },
        encodeArray = function (o) {
            var a = ["[", ""],
            // Note empty string in case there are no serializable members.
                len = o.length,
                i;
            for (i = 0; i < len; i += 1) {
                a.push(doEncode(o[i]), ',');
            }
            // Overwrite trailing comma (or empty string)
            a[a.length - 1] = ']';
            return a.join("");
        },
        encodeObject = function (o) {
            var a = ["{", ""],
            // Note empty string in case there are no serializable members.
                i;
            for (i in o) {
                if (typeof o[i] != 'function' && (!useHasOwn ||( o.hasOwnProperty && o.hasOwnProperty(i)))) {
                    a.push(doEncode(i), ":", doEncode(o[i]), ',');
                }
            }
            // Overwrite trailing comma (or empty string)
            a[a.length - 1] = '}';
            return a.join("");
        };

    this.encodeDate = function (o) {
        return '"' + o.getFullYear() + "-"
            + pad(o.getMonth() + 1) + "-"
            + pad(o.getDate()) + "T"
            + pad(o.getHours()) + ":"
            + pad(o.getMinutes()) + ":"
            + pad(o.getSeconds()) + '"';
    };

    this.encode = doEncode;
    this.decode = doDecode;

})();

function readConfig(configFile) {
    _logger.trace("reading config data from {}", configFile);
    // ensure the data is a javascript string
    var configData = '' + readFileContent(configFile);
    return jsonDecode(configData);
}

function jsonDecode(data) {
    _logger.trace("decoding json data");
    return JSON.decode(data);
}

function jsonEncode(obj) {
    _logger.debug("encoding json data");
    return JSON.encode(obj);
}

function resolvePath() {
    return new File(joinPath.apply(this, arguments)).getAbsolutePath();
}

function joinPath() {
    var len = arguments.length, i, paths = [];
    for (i = 0; i < len; i++) {
        if (_logger.isTraceEnabled()) {
            _logger.trace("adding path arg : {}", arguments[i]);
        }
        paths.push(arguments[i]);
    }
    return PathUtil.getAbsolutePath(paths.join(File.separator));
}

function copyFiles(proj, dir, todir, includes, excludes) {
    var task = proj.createTask("copy"),
        fileset = proj.createDataType('fileset');

    fileset.setDir(new File(dir));
    if(includes) {
        fileset.setIncludes(includes);
    }

    if(excludes) {
        fileset.setExcludes(excludes);
    }

    task.setTodir(new File(todir));
    task.addFileset(fileset);
    task.execute();
}

function moveFiles(proj, from, to, includes, excludes) {
    var task = proj.createTask("move"),
        fileset = proj.createDataType('fileset');

    fileset.setDir(new File(from));
    if(includes) {
        fileset.setIncludes(includes);
    }

    if(excludes) {
        fileset.setExcludes(excludes);
    }

    task.setTodir(new File(to));
    task.addFileset(fileset);
    task.execute();
}

function moveFile(proj, from, to) {
    var task = proj.createTask("move");
    task.setTofile(new File(to));
    task.setFile(new File(from));
    task.execute();
}

function readFileContent(file) {
    return FileUtil.readUnicodeFile(file);
}

function writeFileContent(file, content) {
    FileUtil.writeFile(file, content);
}

function deleteFile(file) {
    FileUtil['delete'](file);
}


function each(list, func) {
    var len = list.length,
        i;
    for (i = 0; i < len; i++) {
        func(list[i]);
    }
    return list;
}

function endsWith(input, substr) {
    // ensure js strings, not java strings
    input = input + '';
    substr = substr + '';
    return input.indexOf(substr, input.length - substr.length) !== -1;
}

function isChildPath(parent, child) {
    var parentPath = PathUtil.getCanonicalPath(parent) + '',
        childPath = PathUtil.getCanonicalPath(child) + '';

    return childPath.indexOf(parentPath) === 0;
}

function exists(path) {
    return new File(path).exists();
}

function runAppUpgrade(proj) {
    var basedir = proj.getProperty("basedir"),
        newSdkPath = proj.getProperty("args.path"),
        appPath = resolvePath("."),
        hasSenchaSdkFile = new File(appPath, ".senchasdk").exists(),
        hasSenchaDir = new File(appPath, ".sencha").exists();

    // v2 app
    if(hasSenchaSdkFile && !hasSenchaDir) {

        // backup packager.json
        // backup app.json
        // backup .senchasdk target directory
        // generate app locally from new framework
        // update app.json paths to .senchasdk stuff to framework.dir
        // delete .senchasdk

        var appSdkFile = resolvePath(appPath, '.senchasdk'),
            appSdkPtr =  FileUtil.readFile(appSdkFile).trim(),
            appSdkPath = resolvePath(appPath, appSdkPtr),
            appConfigFile = resolvePath(appPath, "app.json"),
            appConfig = readConfig(appConfigFile),
            oldSdkVersion = FileUtil.readFile(resolvePath(appSdkPath, "version.txt")).trim(),
            appBackupPath = resolvePath(appPath, ".sencha_backup", appName, oldSdkVersion),
            sdkBackupPath = resolvePath(appBackupPath, appSdkPtr),
            appName = appConfig.name,
            generateCmd = [
                "--sdk-path=" + newSdkPath,
                "generate",
                "app",
                "-upgrade",
                appName,
                appPath
            ],
            sencha = new Sencha(),
            newAppConfig,
            frameworkPath,
            relativePath,
            appFiles = [
                ".senchasdk",
                "app.js",
                "app.json",
                "packager.json",
                "index.html"
            ];

        _logger.debug("Backing up application sdk from {} to {}",
            appSdkPath,
            sdkBackupPath);

        moveFiles(proj, appSdkPath, sdkBackupPath);

        _logger.info("Renamed {} to {} for backup", appSdkPath, sdkBackupPath);

        _logger.debug("Backing up application specific files");

        copyFiles(proj, appPath, appBackupPath, "**/*", ".sencha_backup/**/*");

        _logger.info("Creating new application structure");

        _logger.debug(generateCmd.join(" "));
        sencha.dispatch(generateCmd);

        _logger.info("Updating references to framework files");

        newAppConfig = new SenchaConfigManager(appPath).getConfig();
        frameworkPath = newAppConfig.get("framework.dir");
        relativePath =
            (PathUtil.getRelativePath(appPath, frameworkPath) + '').replace("\\", "/");

        if(endsWith(relativePath, "/")) {
            relativePath = relativePath.substring(0, relativePath.length - 1);
        }

        _logger.debug("Updating file references from path '{}' to path '{}'",
            appSdkPtr,
            relativePath)

        each(appFiles, function(file){
            var fileData = readFileContent(file);

            // prop: "sdk/...
            fileData = StringUtil.replace(
                fileData,
                "\"" + appSdkPtr,
                "\"" + relativePath);

            // prop: 'sdk/...
            fileData = StringUtil.replace(
                fileData,
                "'" + appSdkPtr,
                "'" + relativePath);

            writeFileContent(file, fileData);
        });

        deleteFile(appSdkFile);

        // set the app config path for sencha.cfg update downstream
        proj.setProperty("app.ir", appPath);
        proj.setProperty("app.config.dir", [appPath, '.sencha', 'app'].join(File.separator));

    }
    // v3 app
    else if(hasSenchaDir) {

        var frameworkName = proj.getProperty("framework.name"),
            appName = proj.getProperty("app.name"),
            workspacePath = proj.getProperty("workspace.dir"),
            appSdkPath = resolvePath(proj.getProperty(frameworkName + ".dir")),
            oldSdkVersion = proj.getProperty("framework.version"),
            appBackupPath = resolvePath(appPath, ".sencha_backup", appName, oldSdkVersion),
            sdkBackupPath = resolvePath(workspacePath, ".sencha_backup", frameworkName, oldSdkVersion),
            generateCmd = [
                "--sdk-path=" + newSdkPath,
                "generate",
                "app",
                "-upgrade",
                appName,
                appPath
            ],
            appBackupExcludes = [
                ".sencha_backup/**/*"
            ],
            sencha = new Sencha();

        if(!exists(sdkBackupPath)) {
            _logger.info("Backing up framework files from {} to {}",
                appSdkPath,
                sdkBackupPath);

            moveFiles(proj, appSdkPath, sdkBackupPath);
        }

        _logger.info("Backing up application files from {} to {}",
            appPath,
            appBackupPath);

        if(isChildPath(appPath, appSdkPath)) {
            _logger.debug("excluding framework files from app backup");
            appBackupExcludes.push(PathUtil.getRelativePath(appPath, appSdkPath) + "/**/*");
        }

        copyFiles(proj, appPath, appBackupPath, ["**/*"].join(','), appBackupExcludes.join(','));

        _logger.info("Updating application and workspace files");
        _logger.debug("running command : sencha " + generateCmd.join(" "));

        sencha.dispatch(generateCmd);

        _logger.info("A backup of pre-upgrade application files is available at {}", 
            appBackupPath);

    } else if(!hasSenchaSdkFile) {

        _logger.error("Unable to locate .senchasdk file or .sencha folder");
        _logger.error("Please ensure this folder is a valid v2 or v3 Sencha Touch application");
        throw new ExState("No .senchasdk file or .sencha directory found");

    }

}

(function (proj) {
    _logger.info("building application");
    runAppUpgrade(proj);
})(project);