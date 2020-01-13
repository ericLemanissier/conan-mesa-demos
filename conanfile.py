from conans import ConanFile, tools, AutoToolsBuildEnvironment
import shutil
import os


class LibnameConan(ConanFile):
    name = "mesa-demos"
    version = "8.4.0"
    description = "Keep it short"
    topics = ("conan", "libname", "logging")
    url = "https://github.com/bincrafters/conan-libname"
    homepage = "https://cgit.freedesktop.org/mesa/demos"
    license = "MIT"  # Indicates license type of the packaged library; please use SPDX Identifiers https://spdx.org/licenses/
    _autotools = None
    generators = "pkg_config"

    # Options may need to change depending on the packaged library
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    requires = [
        "mesa/19.3.1@bincrafters/stable",
        "glew/2.1.0@bincrafters/stable",
        "mesa-glu/9.0.1@bincrafters/stable"
    ]

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self, include_rpath_flags=True)
            self._autotools.configure(pkg_config_paths=self.build_folder)
        return self._autotools

    def build(self):
        for package in self.deps_cpp_info.deps:
            lib_path = self.deps_cpp_info[package].rootpath
            for dirpath, _, filenames in os.walk(lib_path):
                for filename in filenames:
                    if filename.endswith('.pc'):
                        shutil.copyfile(os.path.join(dirpath, filename), filename)
                        tools.replace_prefix_in_pc_file(filename, lib_path)
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.install(args=["-j1"])

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
